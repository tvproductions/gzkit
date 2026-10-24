"""Complexity ceiling scope: xenon's C/C/C contract over Lizard (RO-9 tranche 4, GHI #1183).

`docs/governance/harbor-ro9-astral-toolchain.md` § Ruled for tranche 4. Xenon and
Radon are retired; the three-part ceiling they enforced is re-derived over
Lizard's native function scores, held by gzkit rather than a wrapper:

- ``function``: no function's cyclomatic complexity exceeds the ceiling;
- ``module-mean``: no module's arithmetic mean over its functions exceeds it;
- ``overall-mean``: the function-weighted mean over the population does not.

Values compare unrounded, and a value equal to the ceiling passes. A module with
no functions has no mean and adds no denominator.

The ceiling is the one Ruff reads, ``[tool.ruff.lint.mccabe] max-complexity``,
so C901 and this gate cannot disagree about the number. A project that ships
code and declares no ceiling is refused: the contract needs the number stated
once, and Ruff's unstated default is not a statement. The population is the
Python the wheel ships, read from the same predictor ``--distribution`` reads;
a project not built by uv_build ships nothing this scope can model and is
clean.

A partial measurement cannot pass. Every function the parser finds must carry a
Lizard score (``unmeasured`` otherwise: an inline suite, which can also hide the
functions after it), and a module that does not parse is ``unparseable``. A body
that is nothing but ``...`` carries no decision and is the one exemption.

Cognitive complexity is the second leg, scored by gzkit's own
:mod:`gzkit.complexity.cognitive` over CPython's ``ast`` (the operator ruled
complexipy a poor replacement, 2026-10-22). A project opts in by declaring
``complexity.cognitive_ceiling`` in ``.gzkit.json``. No shipped function may score
above it unless ``data/cognitive_complexity_baseline.json`` holds it, keyed by
POSIX path and qualified name, at no less than its score. The baseline is a
shrink-ratchet that must stay exact: a row above its function's score, a row whose
function is gone, and a row at or under the ceiling are each findings, so the
baseline can only shrink, by hand, with the refactor that earns it.

Registered as ``gz validate --complexity-ceiling``; runs in ``gz check`` as the
"Complexity ceiling" step.
"""

import ast
import tomllib
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from gzkit.complexity.cognitive import score_cognitive
from gzkit.complexity.functions import is_ellipsis_stub
from gzkit.complexity.lizard_adapter import FunctionScore, score_functions
from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.distribution import wheel_shipped_files
from gzkit.registries import RegistryError, load_registry

__all__ = [
    "CeilingFinding",
    "audit_complexity_ceiling",
    "cyclomatic_ceiling",
    "measure_ceiling",
]

_COGNITIVE_BASELINE_NAME = "cognitive_complexity_baseline.json"
_COGNITIVE_BASELINE = f"data/{_COGNITIVE_BASELINE_NAME}"

Scorer = Callable[[str, str], list[FunctionScore]]
FindingKind = Literal[
    "function",
    "module-mean",
    "overall-mean",
    "unmeasured",
    "unparseable",
    "cognitive",
    "cognitive-held",
    "cognitive-baseline",
]
Baseline = Mapping[tuple[str, str], int]


class CeilingFinding(BaseModel):
    """One breach of the ceiling, or one refused partial measurement."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: FindingKind
    file: str
    message: str


def cyclomatic_ceiling(pyproject: Mapping[str, Any]) -> float | None:
    """Return the cyclomatic ceiling Ruff reads from *pyproject*, or None when undeclared."""
    mccabe = pyproject.get("tool", {}).get("ruff", {}).get("lint", {}).get("mccabe", {})
    ceiling = mccabe.get("max-complexity")
    return None if ceiling is None else float(ceiling)


def _measure_module(
    file: str, source: str, ceiling: float, scorer: Scorer
) -> tuple[list[CeilingFinding], list[int]]:
    """Measure one module; return its findings and its functions' scores."""
    try:
        tree = ast.parse(source, filename=file)
    except SyntaxError as exc:
        return [CeilingFinding(kind="unparseable", file=file, message=f"{file}: {exc.msg}")], []
    scores = scorer(source, file)
    measured = {score.line for score in scores}
    findings = [
        CeilingFinding(
            kind="unmeasured",
            file=file,
            message=(
                f"{file}:{node.lineno} {node.name}: Lizard did not measure this function "
                "(an inline suite); a partial measurement cannot pass"
            ),
        )
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.lineno not in measured
        and not is_ellipsis_stub(node)
    ]
    findings.extend(
        CeilingFinding(
            kind="function",
            file=file,
            message=(
                f"{file}:{score.line} {score.name}: cyclomatic {score.cyclomatic} > {ceiling:g}"
            ),
        )
        for score in scores
        if score.cyclomatic > ceiling
    )
    values = [score.cyclomatic for score in scores]
    if values and (mean := sum(values) / len(values)) > ceiling:
        findings.append(
            CeilingFinding(
                kind="module-mean",
                file=file,
                message=(
                    f"{file}: module mean {mean:.4f} > {ceiling:g} over {len(values)} functions"
                ),
            )
        )
    return findings, values


def measure_ceiling(
    files: Mapping[str, str], ceiling: float, *, scorer: Scorer = score_functions
) -> list[CeilingFinding]:
    """Measure *files* (path to source) against the three-part *ceiling*."""
    findings: list[CeilingFinding] = []
    population: list[int] = []
    for file in sorted(files):
        module_findings, values = _measure_module(file, files[file], ceiling, scorer)
        findings.extend(module_findings)
        population.extend(values)
    if population and (mean := sum(population) / len(population)) > ceiling:
        findings.append(
            CeilingFinding(
                kind="overall-mean",
                file="",
                message=(f"overall mean {mean:.4f} > {ceiling:g} over {len(population)} functions"),
            )
        )
    return findings


def _cognitive_scores(files: Mapping[str, str]) -> dict[tuple[str, str], tuple[int, int]]:
    """Score each parseable module; a qualified name defined twice keeps its higher score."""
    scores: dict[tuple[str, str], tuple[int, int]] = {}
    for file in sorted(files):
        try:
            module_scores = score_cognitive(files[file], file)
        except SyntaxError:
            continue  # the cyclomatic leg reports the module as unparseable
        for score in module_scores:
            key = (file, score.name)
            if key not in scores or score.score > scores[key][0]:
                scores[key] = (score.score, score.line)
    return scores


def _over_ceiling(
    scores: Mapping[tuple[str, str], tuple[int, int]], ceiling: int, baseline: Baseline
) -> list[CeilingFinding]:
    """Each function above the ceiling that no row holds, or above the row that holds it."""
    findings: list[CeilingFinding] = []
    for (file, name), (score, line) in sorted(scores.items()):
        held = baseline.get((file, name))
        limit = ceiling if held is None else max(held, ceiling)
        if score <= limit:
            continue
        source = "the ceiling" if held is None else f"its baseline row ({_COGNITIVE_BASELINE})"
        message = f"{file}:{line} {name}: cognitive {score} > {limit}, {source}"
        findings.append(CeilingFinding(kind="cognitive", file=file, message=message))
    return findings


def _inexact_rows(
    scores: Mapping[tuple[str, str], tuple[int, int]], ceiling: int, baseline: Baseline
) -> list[CeilingFinding]:
    """Each row that holds more than its function scores, a gone function, or nothing."""
    findings: list[CeilingFinding] = []
    for (file, name), held in sorted(baseline.items()):
        current = scores.get((file, name))
        if current is not None and current[0] >= held > ceiling:
            continue
        now = "is gone" if current is None else f"now scores {current[0]}"
        message = (
            f"{_COGNITIVE_BASELINE} holds {file} {name} at {held} and it {now} (ceiling {ceiling})"
        )
        findings.append(CeilingFinding(kind="cognitive-held", file=file, message=message))
    return findings


def measure_cognitive(
    files: Mapping[str, str], ceiling: int, baseline: Baseline
) -> list[CeilingFinding]:
    """Hold *files* to the cognitive *ceiling*, less the functions *baseline* holds."""
    scores = _cognitive_scores(files)
    return _over_ceiling(scores, ceiling, baseline) + _inexact_rows(scores, ceiling, baseline)


def _load_cognitive_baseline(project_root: Path) -> tuple[dict[tuple[str, str], int], list[str]]:
    """Return the baseline rows by (file, function), and any defects in the file itself."""
    try:
        rows = load_registry(project_root, _COGNITIVE_BASELINE_NAME)["functions"]
    except RegistryError:
        return {}, []
    except (KeyError, TypeError) as exc:
        return {}, [f"{_COGNITIVE_BASELINE} is malformed ({exc})"]
    baseline: dict[tuple[str, str], int] = {}
    defects: list[str] = []
    for row in rows:
        key = (str(row["file"]), str(row["function"]))
        if key in baseline:
            defects.append(f"{_COGNITIVE_BASELINE} holds {key[0]} {key[1]} twice")
        baseline[key] = int(row["score"])
    return baseline, defects


def _cognitive_findings(project_root: Path, files: Mapping[str, str]) -> list[CeilingFinding]:
    """Run the cognitive leg when `.gzkit.json` declares its ceiling."""
    ceiling = GzkitConfig.load(project_root / ".gzkit.json").complexity.cognitive_ceiling
    if ceiling is None:
        return []
    baseline, defects = _load_cognitive_baseline(project_root)
    findings = [
        CeilingFinding(kind="cognitive-baseline", file=_COGNITIVE_BASELINE, message=defect)
        for defect in defects
    ]
    return findings + measure_cognitive(files, ceiling, baseline)


def audit_complexity_ceiling(project_root: Path) -> list[ValidationError]:
    """Hold the Python the wheel ships to the C/C/C ceiling Ruff reads."""
    shipped = sorted(
        p for p in wheel_shipped_files(project_root, missing_ok=True) if p.endswith(".py")
    )
    if not shipped:
        return []
    with (project_root / "pyproject.toml").open("rb") as handle:
        ceiling = cyclomatic_ceiling(tomllib.load(handle))
    if ceiling is None:
        return [
            ValidationError(
                type="complexity_ceiling",
                artifact="pyproject.toml",
                message=(
                    "no cyclomatic ceiling is declared for the shipped code. The C/C/C "
                    "contract reads one number, the one Ruff enforces as C901 (RO-9 tranche "
                    "4, GHI #1183): set `[tool.ruff.lint.mccabe] max-complexity`, then "
                    "re-run `uv run gz validate --complexity-ceiling`"
                ),
            )
        ]
    files = {rel: (project_root / rel).read_text(encoding="utf-8") for rel in shipped}
    findings = measure_ceiling(files, ceiling) + _cognitive_findings(project_root, files)
    return [
        ValidationError(
            type="complexity_ceiling",
            artifact=finding.file or "pyproject.toml",
            message=f"{finding.message}. {_RECOVERY[finding.kind]}",
        )
        for finding in findings
    ]


_WHY = "gzkit holds shipped code to the C/C/C ceiling Ruff reads (RO-9 tranche 4, GHI #1183)"
_RERUN = "then re-run `uv run gz validate --complexity-ceiling`"
_RECOVERY: dict[FindingKind, str] = {
    "function": f"{_WHY}: split the function's decisions into named helpers, {_RERUN}",
    "module-mean": f"{_WHY}: split the module by responsibility, {_RERUN}",
    "overall-mean": f"{_WHY}: reduce the highest-scoring functions first, {_RERUN}",
    "unmeasured": (
        "a partial measurement cannot pass (RO-9 tranche 4): move the function body "
        f"below its `def` line, {_RERUN}"
    ),
    "unparseable": f"a module that does not parse cannot be measured: fix the syntax, {_RERUN}",
    "cognitive": (
        "gzkit holds shipped code to the cognitive ceiling `.gzkit.json` declares, and a "
        "baseline row only shrinks (RO-9 tranche 4): flatten the nesting or split the "
        f"function into named helpers, {_RERUN}"
    ),
    "cognitive-held": (
        f"{_COGNITIVE_BASELINE} is a shrink-ratchet that stays exact (RO-9 tranche 4): lower "
        "the row to the function's score, or delete it when the function is gone or at the "
        "ceiling, set baseline_count in data/waiver_ratchet_registry.json to the row count, "
        f"{_RERUN}"
    ),
    "cognitive-baseline": (
        f"{_COGNITIVE_BASELINE} is keyed by file and function, one row each (RO-9 tranche "
        f"4): restore it from git or merge the rows, {_RERUN}"
    ),
}
