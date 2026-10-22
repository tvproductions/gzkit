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

Registered as ``gz validate --complexity-ceiling``; runs in ``gz check`` as the
"Complexity ceiling" step.
"""

from __future__ import annotations

import ast
import tomllib
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from gzkit.complexity.lizard_adapter import FunctionScore, score_functions
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.distribution import wheel_shipped_files

__all__ = [
    "CeilingFinding",
    "audit_complexity_ceiling",
    "cyclomatic_ceiling",
    "measure_ceiling",
]

Scorer = Callable[[str, str], list[FunctionScore]]
FindingKind = Literal["function", "module-mean", "overall-mean", "unmeasured", "unparseable"]


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


def _is_ellipsis_stub(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True when the body is ``...`` alone, after an optional docstring."""
    body = node.body
    if len(body) == 2 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    return (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and body[0].value.value is Ellipsis
    )


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
        and not _is_ellipsis_stub(node)
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
    return [
        ValidationError(
            type="complexity_ceiling",
            artifact=finding.file or "pyproject.toml",
            message=f"{finding.message}. {_RECOVERY[finding.kind]}",
        )
        for finding in measure_ceiling(files, ceiling)
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
}
