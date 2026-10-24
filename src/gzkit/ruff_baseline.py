"""Every Ruff rule under a counted shrink-ratchet baseline (RO-9 tranche 4).

`docs/governance/harbor-ro9-astral-toolchain.md` § Ruled for tranche 4. Ruff
selects ``ALL`` with preview, less the standing exceptions recorded in
``pyproject.toml``; Ruff ships no baseline of its own, so the findings the tree
carried when the selection widened are held in ``data/ruff_baseline.json``,
one row per (POSIX path, rule) with its count, never by line. The operator
ruled the shape by selection: a keyed shrink-ratchet baseline (*"b"*), counted
and run by gzkit (*"Counted, gz-run (Rec.)"*), in its own file (*"Own file
(Rec.)"*).

The verdict is exact, as the cognitive and astral-discipline baselines are:

- ``unheld``: a (file, rule) carries more findings than its row holds, or has no
  row. A tree with no baseline file holds nothing, so every finding fails, which
  is plain ``ruff check``.
- ``lower``: a row holds more findings than remain, so its slack could hide a new
  one. ``gz lint --ratchet`` lowers it.
- ``dead``: a row whose findings are all gone. ``gz lint --ratchet`` removes it.

Ruff is reached through one runner, injected so the comparison is testable
without it (hexagonal § Operative rule 6).
"""

import functools
import json
import subprocess  # noqa: S404 — Ruff is an external tool, reached only by argv
import sys
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from gzkit.registries import RegistryError, load_registry, registry_path

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "BASELINE_NAME",
    "BASELINE_RELPATH",
    "BaselineError",
    "Breach",
    "LintReport",
    "RuffFinding",
    "RuffRunError",
    "Runner",
    "Walker",
    "compare",
    "lint_against_baseline",
    "load_baseline",
    "lowered_rows",
    "parse_ruff_json",
    "ratchet_baseline",
    "render_report",
    "run_ruff_json",
    "run_ruff_walk",
]

BASELINE_NAME = "ruff_baseline.json"
BASELINE_RELPATH = f"data/{BASELINE_NAME}"
_ROWS = "rows"
_SPEC = "docs/governance/harbor-ro9-astral-toolchain.md"
_SYNTAX_RULE = "invalid-syntax"

BreachKind = Literal["unheld", "lower", "dead"]
Key = tuple[str, str]


class RuffFinding(BaseModel):
    """One Ruff diagnostic, keyed by the POSIX path relative to the project root."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str = Field(..., description="POSIX path relative to the project root")
    rule: str = Field(..., description="Ruff code, or invalid-syntax")
    line: int = Field(..., description="1-based row of the finding")
    column: int = Field(..., description="1-based column of the finding")
    message: str = Field(..., description="Ruff's message")


class Breach(BaseModel):
    """One (file, rule) whose findings disagree with its baseline row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: BreachKind = Field(..., description="unheld, lower or dead")
    file: str = Field(..., description="POSIX path relative to the project root")
    rule: str = Field(..., description="Ruff code")
    found: int = Field(..., description="Findings Ruff reports for this file and rule")
    held: int = Field(..., description="Findings the baseline row holds (0 when none)")
    findings: tuple[RuffFinding, ...] = Field((), description="The findings, for an unheld key")


class LintReport(BaseModel):
    """The baseline verdict over one Ruff run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    findings: tuple[RuffFinding, ...] = Field(..., description="Every finding Ruff reported")
    breaches: tuple[Breach, ...] = Field(..., description="Keys that disagree with the baseline")
    has_baseline: bool = Field(..., description="Whether data/ruff_baseline.json exists")

    @property
    def ok(self) -> bool:
        """Report whether every finding is held and every row is exact."""
        return not self.breaches


class RuffRunError(RuntimeError):
    """Ruff could not run, or printed something that is not its JSON report."""


class BaselineError(RuntimeError):
    """``data/ruff_baseline.json`` exists but is not a valid baseline."""


class Runner(Protocol):
    """Runs Ruff over targets and returns its JSON report."""

    def __call__(self, project_root: Path, targets: Sequence[str], *, fix: bool) -> str:
        """Return Ruff's ``--output-format json`` report for *targets*."""
        ...


def _run_ruff(argv: list[str], project_root: Path, stage: str) -> str:
    """Run Ruff with *argv* in *project_root*.

    Returns:
        Ruff's stdout.

    Raises:
        RuffRunError: Ruff could not start, or exited non-zero (*stage* names when).

    """
    try:
        result = subprocess.run(  # noqa: S603 — fixed argv; targets are paths, never a shell
            argv,
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        msg = f"Ruff could not start ({exc}); install the dev group with `uv sync --locked`"
        raise RuffRunError(msg) from exc
    if result.returncode != 0:
        detail = "\n".join((result.stderr or result.stdout).strip().splitlines()[:20])
        msg = f"Ruff exited {result.returncode} {stage}:\n{detail}"
        raise RuffRunError(msg)
    return result.stdout


def run_ruff_json(project_root: Path, targets: Sequence[str], *, fix: bool) -> str:
    """Run Ruff over *targets* and return its JSON report.

    ``--exit-zero`` makes findings exit 0, so any other status is Ruff itself
    failing (a bad configuration, an unreadable path), which raises
    :class:`RuffRunError`.

    Returns:
        Ruff's JSON report on stdout.

    """
    argv = ["uv", "run", "ruff", "check", "--output-format", "json", "--exit-zero"]
    if fix:
        argv.append("--fix")
    return _run_ruff([*argv, *targets], project_root, "before reporting")


class Walker(Protocol):
    """Lists the files Ruff reads when it walks the whole tree."""

    def __call__(self, project_root: Path) -> list[str]:
        """Return the POSIX paths, relative to *project_root*, Ruff's walk of ``.`` reads."""
        ...


def run_ruff_walk(project_root: Path) -> list[str]:
    """List the files Ruff reads when it walks the whole tree.

    Ruff lints any path it is named, a gitignored or extensionless one included,
    so a named-file run must be held to this list to judge what the whole-tree
    run judges. Ruff failing to start or to list raises :class:`RuffRunError`.

    Returns:
        The walked files as POSIX paths relative to *project_root*.

    """
    argv = ["uv", "run", "ruff", "check", "--show-files", "."]
    stdout = _run_ruff(argv, project_root, "listing its files")
    return [_relative(line, project_root) for line in stdout.splitlines() if line.strip()]


@functools.cache
def ruff_rule_codes() -> dict[str, str]:
    """Map each Ruff rule name to its code, from the installed Ruff's own table.

    RUF201 writes configuration entries as rule names, so a reader comparing
    them with codes translates through Ruff rather than a copied table.

    Returns:
        Every rule's code, keyed by its name.

    Raises:
        RuffRunError: Ruff could not start, exited non-zero, or printed no table.

    """
    argv = [sys.executable, "-m", "ruff", "rule", "--all", "--output-format", "json"]
    try:
        result = subprocess.run(  # noqa: S603 — fixed argv, never a shell
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        msg = f"Ruff could not start ({exc}); install the dev group with `uv sync --locked`"
        raise RuffRunError(msg) from exc
    if result.returncode != 0:
        msg = f"`ruff rule --all` exited {result.returncode}: {result.stderr.strip()[:200]}"
        raise RuffRunError(msg)
    try:
        table = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        msg = f"`ruff rule --all` printed no JSON rule table: {exc}"
        raise RuffRunError(msg) from exc
    return {rule["name"]: rule["code"] for rule in table}


def _relative(filename: str, project_root: Path) -> str:
    path = Path(filename)
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def parse_ruff_json(stdout: str, project_root: Path) -> list[RuffFinding]:
    """Parse Ruff's ``--output-format json`` report into findings.

    Returns:
        One finding per diagnostic, its path relative to *project_root*.

    Raises:
        RuffRunError: The report is not a JSON list.

    """
    try:
        items = json.loads(stdout or "[]")
    except json.JSONDecodeError as exc:
        msg = f"Ruff's report is not JSON ({exc})"
        raise RuffRunError(msg) from exc
    if not isinstance(items, list):
        msg = "Ruff's report is not a list of diagnostics"
        raise RuffRunError(msg)
    try:
        return [_finding(item, project_root) for item in items]
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        msg = f"Ruff's report carries a diagnostic gzkit cannot read ({exc!r})"
        raise RuffRunError(msg) from exc


def _finding(item: dict[str, object], project_root: Path) -> RuffFinding:
    location = item.get("location") or {}
    if not isinstance(location, dict):
        location = {}
    return RuffFinding(
        file=_relative(str(item["filename"]), project_root),
        rule=str(item.get("code") or _SYNTAX_RULE),
        line=int(location.get("row", 0)),
        column=int(location.get("column", 0)),
        message=str(item.get("message", "")),
    )


#: Rules Ruff evaluates from the executable bit, which only Unix-like systems
#: carry (`ruff rule EXE001`). A row for one cannot be exact on Windows, where
#: Ruff does not run it and the row reads as dead.
PLATFORM_DEPENDENT_RULES = frozenset({"EXE001", "EXE002"})


def load_baseline(project_root: Path, *, platform_rows: bool = False) -> dict[Key, int] | None:
    """Read ``data/ruff_baseline.json``.

    *platform_rows* admits a row for a rule in :data:`PLATFORM_DEPENDENT_RULES`,
    for the ratchet alone, which deletes it.

    Returns:
        The rows' counts by (file, rule), or None when the tree has no baseline.

    Raises:
        BaselineError: The file is malformed, holds a key twice, a count below 1,
            or a rule Ruff runs on some platforms only.

    """
    if not registry_path(project_root, BASELINE_NAME).is_file():
        return None
    try:
        rows = load_registry(project_root, BASELINE_NAME)[_ROWS]
    except (RegistryError, KeyError, TypeError) as exc:
        msg = f"{BASELINE_RELPATH} is malformed ({exc})"
        raise BaselineError(msg) from exc
    baseline: dict[Key, int] = {}
    for row in rows:
        key = (str(row["file"]), str(row["rule"]))
        count = row["count"]
        if key in baseline:
            msg = f"{BASELINE_RELPATH} holds {key[0]} {key[1]} twice"
            raise BaselineError(msg)
        if key[1] in PLATFORM_DEPENDENT_RULES and not platform_rows:
            msg = (
                f"{BASELINE_RELPATH} holds {key[0]} {key[1]}, a rule Ruff runs only where "
                "files carry an executable bit, so the row cannot be exact on Windows: "
                "fix the finding (drop the shebang, or set the bit) and delete the row"
            )
            raise BaselineError(msg)
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            msg = f"{BASELINE_RELPATH} holds {key[0]} {key[1]} at {count!r}, not a count"
            raise BaselineError(msg)
        baseline[key] = count
    return baseline


def _in_scope(file: str, scope: Sequence[str] | None) -> bool:
    if scope is None:
        return True
    return any(file == entry or file.startswith(f"{entry}/") for entry in scope)


def compare(
    findings: Sequence[RuffFinding],
    baseline: dict[Key, int],
    scope: Sequence[str] | None = None,
) -> list[Breach]:
    """Return every (file, rule) whose findings disagree with *baseline*.

    *scope* limits the row checks to the files a partial run read (POSIX paths
    relative to the root, a directory covering what lies under it); None is the
    whole tree.

    Returns:
        The breaches, sorted by (file, rule).

    """
    by_key: dict[Key, list[RuffFinding]] = {}
    for finding in findings:
        by_key.setdefault((finding.file, finding.rule), []).append(finding)
    breaches = []
    for key in sorted(by_key.keys() | {k for k in baseline if _in_scope(k[0], scope)}):
        found, held = len(by_key.get(key, [])), baseline.get(key, 0)
        if found > held:
            kind: BreachKind = "unheld"
        elif found == held:
            continue
        else:
            kind = "lower" if found else "dead"
        breaches.append(
            Breach(
                kind=kind,
                file=key[0],
                rule=key[1],
                found=found,
                held=held,
                findings=tuple(by_key.get(key, [])) if kind == "unheld" else (),
            )
        )
    return breaches


def _scope(targets: Sequence[str], project_root: Path) -> list[str] | None:
    entries = [_relative(str(project_root / target), project_root) for target in targets]
    return None if not entries or "." in entries else entries


def lint_against_baseline(
    project_root: Path,
    targets: Sequence[str] = (),
    *,
    fix: bool = False,
    runner: Runner = run_ruff_json,
    walker: Walker = run_ruff_walk,
) -> LintReport:
    """Run Ruff over *targets* (the whole tree when empty) and judge it against the baseline.

    A named file outside Ruff's walk of the whole tree is not judged: the gate is
    the whole-tree run, and a named-file run (the pre-commit hook) judges no file
    that run never reads. A named directory is walked by Ruff itself.

    Returns:
        The findings and the breaches of the baseline.

    """
    if _scope(targets, project_root) is not None:
        walked = set(walker(project_root))
        targets = [
            target
            for target in targets
            if (project_root / target).is_dir()
            or _relative(str(project_root / target), project_root) in walked
        ]
        if not targets:
            return LintReport(
                findings=(), breaches=(), has_baseline=load_baseline(project_root) is not None
            )
    findings = parse_ruff_json(runner(project_root, list(targets) or ["."], fix=fix), project_root)
    baseline = load_baseline(project_root)
    breaches = compare(findings, baseline or {}, _scope(targets, project_root))
    return LintReport(
        findings=tuple(findings), breaches=tuple(breaches), has_baseline=baseline is not None
    )


def lowered_rows(findings: Sequence[RuffFinding], baseline: dict[Key, int]) -> dict[Key, int]:
    """Lower *baseline* to *findings*.

    Returns:
        Each row at the lesser of its count and its findings; a row with none left dropped.

    """
    found = Counter((finding.file, finding.rule) for finding in findings)
    return {key: min(held, found[key]) for key, held in baseline.items() if found[key]}


def ratchet_baseline(project_root: Path, *, runner: Runner = run_ruff_json) -> int:
    """Lower every row of the baseline to the tree's findings; return the rows removed.

    Shrink-only by construction: a row is never raised and no row is added, so an
    unheld finding still fails the next `gz lint`. A row for a rule Ruff runs on
    some platforms only is deleted whatever the tree holds, since no baseline may
    keep one.

    Returns:
        The number of rows removed.

    Raises:
        BaselineError: The tree has no baseline to lower.

    """
    baseline = load_baseline(project_root, platform_rows=True)
    if baseline is None:
        msg = f"no {BASELINE_RELPATH} to ratchet"
        raise BaselineError(msg)
    findings = parse_ruff_json(runner(project_root, ["."], fix=False), project_root)
    rows = {
        key: count
        for key, count in lowered_rows(findings, baseline).items()
        if key[1] not in PLATFORM_DEPENDENT_RULES
    }
    path = registry_path(project_root, BASELINE_NAME)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[_ROWS] = [
        {"file": file, "rule": rule, "count": count} for (file, rule), count in sorted(rows.items())
    ]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(baseline) - len(rows)


_WHY = (
    "gzkit runs every Ruff rule, and holds the findings the tree carried when the "
    f"selection widened in {BASELINE_RELPATH}, a shrink-only baseline ({_SPEC} § Ruled "
    "for tranche 4)"
)
_RECOVERY: dict[BreachKind, str] = {
    "unheld": f"{_WHY}: fix the new findings, then re-run `uv run gz lint`",
    "lower": (
        f"{_WHY}: a fixed finding lowers its row, or the slack hides the next one; run "
        "`uv run gz lint --ratchet` (it lowers rows, never raises them), then re-run "
        "`uv run gz lint`"
    ),
    "dead": (
        f"{_WHY}: a row whose findings are gone is removed; run `uv run gz lint --ratchet`, "
        "then re-run `uv run gz lint`"
    ),
}


def render_report(report: LintReport, *, max_lines: int = 20) -> str:
    """Render the breaches as three-part recovery prose, one block per kind.

    Returns:
        The blocks, each naming the findings, the rule and the next step.

    """
    blocks = []
    for kind in ("unheld", "lower", "dead"):
        breaches = [b for b in report.breaches if b.kind == kind]
        if not breaches:
            continue
        lines = []
        for breach in breaches:
            lines.append(f"{breach.file}: {breach.rule} {breach.found} found, {breach.held} held")
            lines.extend(
                f"  {f.file}:{f.line}:{f.column} {f.rule} {f.message}" for f in breach.findings
            )
        shown = lines[:max_lines]
        if len(lines) > max_lines:
            shown.append(f"... {len(lines) - max_lines} more lines; re-run `uv run gz lint`")
        blocks.append("\n".join([*shown, _RECOVERY[kind]]))
    return "\n\n".join(blocks)
