"""Chores command implementations (v2.0 registry format).

v2.0 uses a pointer-style registry where each chore has its own directory
containing CHORE.md (human workflow) and acceptance.json (machine criteria).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from rich.table import Table

from gzkit.commands.common import GzCliError, console, get_project_root

CHORES_REGISTRY_PATH = Path("config/gzkit.chores.json")
CHORE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_LANES = {"lite", "medium", "heavy"}
SHELL_OPERATORS_RE = re.compile(r"&&|\|\||[|<>]")
LANE_TIMEOUTS: dict[str, int] = {"lite": 120, "medium": 300, "heavy": 900}


class AcceptanceCriterion(BaseModel):
    """Single acceptance criterion from a chore's acceptance.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    criterion_type: str
    command: str
    argv: tuple[str, ...]
    expected: int | None = None
    not_contains: str | None = None
    contains: str | None = None
    description: str | None = None


class ChoreDefinition(BaseModel):
    """Validated chore definition loaded from v2.0 registry + acceptance.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str
    title: str
    lane: str
    version: str
    path: str
    criteria: tuple[AcceptanceCriterion, ...]
    timeout_seconds: int
    vendor: str | None = None


class CriterionResult(BaseModel):
    """Execution result for one acceptance criterion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    criterion: AcceptanceCriterion
    passed: bool
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    detail: str


def _raise_blockers(blockers: list[str]) -> None:
    """Raise a user-facing BLOCKERS error."""
    if not blockers:
        return
    raise GzCliError("BLOCKERS:\n" + "\n".join(f"- {item}" for item in blockers))


_CRITERION_TYPES = frozenset(
    {
        "exitCodeEquals",
        "outputNotContains",
        "outputContains",
        "fileExists",
    }
)

# ---------------------------------------------------------------------------
# Extracted helpers live in chores_exec.py.  Import after models/constants
# are defined to avoid circular-import issues.
# ---------------------------------------------------------------------------
from gzkit.commands.chores_exec import (  # noqa: E402
    _evaluate_criterion,
    _log_path,
    _parse_chore_pointer,
    _write_chore_log,
)


def _detect_active_harness() -> str | None:
    """Detect the active agent harness from project markers."""
    project_root = get_project_root()
    if (project_root / ".claude").is_dir():
        return "claude"
    return None


def _chore_matches_harness(chore: ChoreDefinition, active_harness: str | None) -> bool:
    """Return True if chore is applicable to the active harness."""
    if chore.vendor is None:
        return True
    if active_harness is None:
        return False
    return chore.vendor == active_harness


def _filter_registry(
    registry: dict[str, ChoreDefinition],
) -> dict[str, ChoreDefinition]:
    """Filter registry to chores matching the active harness."""
    harness = _detect_active_harness()
    return {slug: c for slug, c in registry.items() if _chore_matches_harness(c, harness)}


def _load_chores_registry() -> tuple[Path, dict[str, ChoreDefinition]]:
    """Load and validate the v2.0 chores registry."""
    project_root = get_project_root()
    registry_path = project_root / CHORES_REGISTRY_PATH
    blockers: list[str] = []

    if not registry_path.exists():
        blockers.append(f"Missing chores registry: {CHORES_REGISTRY_PATH.as_posix()}")
        _raise_blockers(blockers)

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        blockers.append(f"Invalid JSON in {CHORES_REGISTRY_PATH.as_posix()}: {exc.msg}")
        _raise_blockers(blockers)
        return registry_path, {}

    if not isinstance(payload, dict):
        blockers.append("Registry root must be a JSON object.")
        _raise_blockers(blockers)
        return registry_path, {}

    spec_version = payload.get("specVersion")
    if spec_version != "2.0":
        blockers.append("Registry specVersion must be '2.0'.")

    # Parse lane timeouts from registry, falling back to built-in defaults.
    lane_timeouts: dict[str, int] = dict(LANE_TIMEOUTS)
    lanes_raw = payload.get("lanes")
    if isinstance(lanes_raw, dict):
        for lane_name, lane_cfg in lanes_raw.items():
            if isinstance(lane_cfg, dict):
                ts = lane_cfg.get("timeoutSeconds")
                if isinstance(ts, int) and ts > 0:
                    lane_timeouts[lane_name.lower()] = ts

    chores_raw = payload.get("chores")
    if not isinstance(chores_raw, list) or not chores_raw:
        blockers.append("Registry field 'chores' must be a non-empty array.")
        _raise_blockers(blockers)
        return registry_path, {}

    registry: dict[str, ChoreDefinition] = {}
    for idx, raw_chore in enumerate(chores_raw):
        chore = _parse_chore_pointer(
            raw_chore,
            idx,
            project_root,
            lane_timeouts,
            blockers,
        )
        if chore is None:
            continue
        if chore.slug in registry:
            blockers.append(f"Duplicate chore slug: {chore.slug}")
            continue
        registry[chore.slug] = chore

    _raise_blockers(blockers)
    return registry_path, registry


def _resolve_chore(slug: str) -> tuple[Path, ChoreDefinition]:
    """Resolve one chore by slug from the validated registry."""
    registry_path, registry = _load_chores_registry()
    chore = registry.get(slug)
    if chore is None:
        msg = f"BLOCKERS:\n- Unknown chore slug: {slug}"
        raise GzCliError(msg)  # noqa: TRY003
    harness = _detect_active_harness()
    if not _chore_matches_harness(chore, harness):
        msg = (
            f"BLOCKERS:\n- Chore '{slug}' is vendor-scoped to '{chore.vendor}' "
            f"but active harness is '{harness or 'none'}'"
        )
        raise GzCliError(msg)  # noqa: TRY003
    return registry_path, chore


def chores_list() -> None:
    """List chore definitions from registry."""
    _registry_path, registry = _load_chores_registry()
    registry = _filter_registry(registry)
    table = Table(title="Chores Registry")
    table.add_column("Slug", style="cyan")
    table.add_column("Lane", style="green")
    table.add_column("Version")
    table.add_column("Vendor")
    table.add_column("Criteria", justify="right")
    table.add_column("Title")

    for chore in sorted(registry.values(), key=lambda item: item.slug):
        table.add_row(
            chore.slug,
            chore.lane,
            chore.version,
            chore.vendor or "",
            str(len(chore.criteria)),
            chore.title,
        )

    console.print(table)


def chores_plan(slug: str) -> None:
    """Render deterministic plan details for one chore."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    log_path = _log_path(project_root, chore)

    console.print(f"[bold]Chore Plan: {chore.slug}[/bold]")
    console.print(f"  Title: {chore.title}")
    console.print(f"  Lane: {chore.lane}")
    console.print(f"  Version: {chore.version}")
    console.print(f"  Path: {chore.path}")
    console.print(f"  Log: {log_path.relative_to(project_root).as_posix()}")
    console.print("  Acceptance Criteria:")
    for idx, c in enumerate(chore.criteria, start=1):
        desc = f" -- {c.description}" if c.description else ""
        if c.criterion_type == "exitCodeEquals":
            console.print(f"    {idx}. [{c.criterion_type}] `{c.command}` == {c.expected}{desc}")
        elif c.criterion_type == "outputNotContains":
            console.print(
                f"    {idx}. [{c.criterion_type}] "
                f"`{c.command}` must not contain "
                f"'{c.not_contains}'{desc}"
            )
        elif c.criterion_type == "outputContains":
            console.print(
                f"    {idx}. [{c.criterion_type}] `{c.command}` must contain '{c.contains}'{desc}"
            )
        else:
            console.print(f"    {idx}. [{c.criterion_type}] `{c.command}`{desc}")


def chores_show(slug: str) -> None:
    """Display the CHORE.md content for one chore."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    chore_md = project_root / chore.path / "CHORE.md"
    if not chore_md.exists():
        msg = f"BLOCKERS:\n- Missing CHORE.md: {chore.path}/CHORE.md"
        raise GzCliError(msg)  # noqa: TRY003
    console.print(chore_md.read_text(encoding="utf-8"))


def chores_advise(slug: str) -> None:
    """Dry-run acceptance criteria and report actionable status."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)

    console.print(f"[bold]Chore Advice: {chore.slug}[/bold]")
    console.print(f"  Lane: {chore.lane}  |  Version: {chore.version}")
    console.print()

    all_pass = True
    for idx, criterion in enumerate(chore.criteria, start=1):
        result = _evaluate_criterion(
            criterion,
            project_root,
            chore.timeout_seconds,
        )
        mark = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        console.print(
            f"  {idx}. {mark}  `{criterion.command}` "
            f"({result.duration_seconds:.1f}s) -- {result.detail}"
        )
        if not result.passed:
            all_pass = False

    console.print()
    if all_pass:
        console.print(
            "[green]All criteria pass.[/green] Run `gz chores run " + slug + "` to log the result."
        )
    else:
        console.print(
            "[yellow]Some criteria failed.[/yellow] "
            "Read the CHORE.md workflow for remediation steps:"
        )
        chore_md = project_root / chore.path / "CHORE.md"
        console.print(f"  {chore_md.relative_to(project_root).as_posix()}")


def chores_run(slug: str) -> None:
    """Execute one chore's acceptance criteria and log results."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    results: list[CriterionResult] = []

    for criterion in chore.criteria:
        result = _evaluate_criterion(
            criterion,
            project_root,
            chore.timeout_seconds,
        )
        results.append(result)

        if not result.passed:
            log_path = _write_chore_log(
                project_root,
                chore,
                "FAIL",
                results,
            )
            msg = (
                "Chore criterion failed:\n"
                f"- chore: {chore.slug}\n"
                f"- criterion: {result.criterion.command}\n"
                f"- detail: {result.detail}\n"
                f"- log: "
                f"{log_path.relative_to(project_root).as_posix()}"
            )
            raise GzCliError(msg)  # noqa: TRY003

    log_path = _write_chore_log(project_root, chore, "PASS", results)
    console.print(
        f"[green]Chore completed.[/green] log: {log_path.relative_to(project_root).as_posix()}"
    )


def chores_audit(*, all_chores: bool, slug: str | None) -> None:
    """Audit chores for log presence."""
    project_root = get_project_root()
    _registry_path, registry = _load_chores_registry()
    registry = _filter_registry(registry)

    if all_chores:
        chores = sorted(registry.values(), key=lambda item: item.slug)
    else:
        if not slug:
            msg = "BLOCKERS:\n- Provide --all or --slug <slug>."
            raise GzCliError(msg)  # noqa: TRY003
        chore = registry.get(slug)
        if chore is None:
            msg = f"BLOCKERS:\n- Unknown chore slug: {slug}"
            raise GzCliError(msg)  # noqa: TRY003
        chores = [chore]

    table = Table(title="Chores Audit")
    table.add_column("Slug", style="cyan")
    table.add_column("Lane", style="green")
    table.add_column("Has Log")
    table.add_column("Log Path")

    for chore in chores:
        log = _log_path(project_root, chore)
        has_log = "yes" if log.exists() else "no"
        rel_path = log.relative_to(project_root).as_posix()
        table.add_row(chore.slug, chore.lane, has_log, rel_path)

    console.print(table)
