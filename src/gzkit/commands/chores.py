"""Chores command implementations (v2.0 registry format).

v2.0 uses a pointer-style registry where each chore has its own directory
containing CHORE.md (human workflow) and acceptance.json (machine criteria).
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import cast

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


def _parse_command_to_argv(
    command: str,
    context: str,
    blockers: list[str],
) -> tuple[str, ...]:
    """Parse a shell command string into an argv tuple, rejecting shell operators."""
    if SHELL_OPERATORS_RE.search(command):
        blockers.append(
            f"{context}: command contains shell operators. Split into separate criteria instead."
        )
        return ()
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        blockers.append(f"{context}: invalid command syntax: {exc}")
        return ()
    if not parts:
        blockers.append(f"{context}: command is empty after parsing.")
        return ()
    return tuple(parts)


_CRITERION_TYPES = frozenset(
    {
        "exitCodeEquals",
        "outputNotContains",
        "outputContains",
        "fileExists",
    }
)


def _parse_criterion(
    raw: object,
    index: int,
    chore_slug: str,
    blockers: list[str],
) -> AcceptanceCriterion | None:
    """Parse one acceptance criterion from acceptance.json."""
    context = f"chores[{chore_slug}].criteria[{index}]"
    if not isinstance(raw, dict):
        blockers.append(f"{context} must be an object.")
        return None
    data = cast("dict[str, object]", raw)

    criterion_type = data.get("type")
    if not isinstance(criterion_type, str) or criterion_type not in _CRITERION_TYPES:
        blockers.append(f"{context}.type must be one of: {', '.join(sorted(_CRITERION_TYPES))}.")
        return None

    command = data.get("command")
    if not isinstance(command, str) or not command.strip():
        blockers.append(f"{context}.command must be a non-empty string.")
        return None
    command = command.strip()

    argv = _parse_command_to_argv(command, context, blockers)
    if not argv:
        return None

    expected: int | None = None
    not_contains: str | None = None
    contains: str | None = None
    desc_raw = data.get("description")
    description = desc_raw.strip() if isinstance(desc_raw, str) else None

    if criterion_type == "exitCodeEquals":
        expected_raw = data.get("expected")
        if not isinstance(expected_raw, int):
            blockers.append(f"{context}.expected must be an integer for exitCodeEquals.")
            return None
        expected = expected_raw

    elif criterion_type == "outputNotContains":
        nc_raw = data.get("notContains")
        if not isinstance(nc_raw, str) or not nc_raw:
            blockers.append(f"{context}.notContains must be a non-empty string.")
            return None
        not_contains = nc_raw

    elif criterion_type == "outputContains":
        c_raw = data.get("contains")
        if not isinstance(c_raw, str) or not c_raw:
            blockers.append(f"{context}.contains must be a non-empty string.")
            return None
        contains = c_raw

    return AcceptanceCriterion(
        criterion_type=criterion_type,
        command=command,
        argv=argv,
        expected=expected,
        not_contains=not_contains,
        contains=contains,
        description=description,
    )


def _load_acceptance(
    project_root: Path,
    chore_path: str,
    chore_slug: str,
    blockers: list[str],
) -> tuple[AcceptanceCriterion, ...]:
    """Load and validate acceptance.json from a chore directory."""
    acceptance_file = project_root / chore_path / "acceptance.json"
    if not acceptance_file.exists():
        blockers.append(
            f"Missing acceptance.json for chore '{chore_slug}': {chore_path}/acceptance.json"
        )
        return ()

    try:
        payload = json.loads(acceptance_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        blockers.append(f"Invalid JSON in {chore_path}/acceptance.json: {exc.msg}")
        return ()

    if not isinstance(payload, dict):
        blockers.append(f"{chore_path}/acceptance.json root must be a JSON object.")
        return ()

    criteria_raw = payload.get("criteria")
    if not isinstance(criteria_raw, list) or not criteria_raw:
        blockers.append(f"{chore_path}/acceptance.json must have a non-empty 'criteria' array.")
        return ()

    parsed: list[AcceptanceCriterion] = []
    for idx, raw_criterion in enumerate(criteria_raw):
        criterion = _parse_criterion(raw_criterion, idx, chore_slug, blockers)
        if criterion is not None:
            parsed.append(criterion)

    return tuple(parsed)


def _parse_chore_pointer(
    raw_chore: object,
    index: int,
    project_root: Path,
    lane_timeouts: dict[str, int],
    blockers: list[str],
) -> ChoreDefinition | None:
    """Parse one v2.0 chore pointer from the registry."""
    if not isinstance(raw_chore, dict):
        blockers.append(f"chores[{index}] must be an object.")
        return None
    data = cast("dict[str, object]", raw_chore)

    slug_raw = data.get("slug")
    if not isinstance(slug_raw, str) or not CHORE_SLUG_RE.match(slug_raw):
        blockers.append(f"chores[{index}].slug must be kebab-case (for example: quality-check).")
        return None
    slug = slug_raw.strip()

    title_raw = data.get("title")
    if not isinstance(title_raw, str) or not title_raw.strip():
        blockers.append(f"chores[{slug}].title must be a non-empty string.")
        return None
    title = title_raw.strip()

    lane_raw = data.get("lane")
    if not isinstance(lane_raw, str):
        blockers.append(f"chores[{slug}].lane must be one of: {', '.join(sorted(ALLOWED_LANES))}.")
        return None
    lane = lane_raw.strip().lower()
    if lane not in ALLOWED_LANES:
        blockers.append(f"chores[{slug}].lane must be one of: {', '.join(sorted(ALLOWED_LANES))}.")
        return None

    version_raw = data.get("version", "1.0.0")
    version = version_raw.strip() if isinstance(version_raw, str) else "1.0.0"

    path_raw = data.get("path")
    if not isinstance(path_raw, str) or not path_raw.strip():
        blockers.append(f"chores[{slug}].path must be a non-empty string.")
        return None
    chore_path = path_raw.strip()

    chore_dir = project_root / chore_path
    if not chore_dir.is_dir():
        blockers.append(f"Chore directory not found: {chore_path}")
        return None

    criteria = _load_acceptance(
        project_root,
        chore_path,
        slug,
        blockers,
    )
    if not criteria:
        return None

    timeout = lane_timeouts.get(lane, LANE_TIMEOUTS.get(lane, 900))

    return ChoreDefinition(
        slug=slug,
        title=title,
        lane=lane,
        version=version,
        path=chore_path,
        criteria=criteria,
        timeout_seconds=timeout,
    )


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
        raise GzCliError(f"BLOCKERS:\n- Unknown chore slug: {slug}")
    return registry_path, chore


def _log_path(project_root: Path, chore: ChoreDefinition) -> Path:
    """Compute log path inside chore's proofs directory."""
    return project_root / chore.path / "proofs" / "CHORE-LOG.md"


def _evaluate_criterion(
    criterion: AcceptanceCriterion,
    project_root: Path,
    timeout: int,
) -> CriterionResult:
    """Execute one criterion and evaluate the result."""
    started = perf_counter()
    try:
        completed = subprocess.run(
            list(criterion.argv),
            cwd=project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = perf_counter() - started
        stdout = (
            exc.stdout.decode("utf-8", errors="replace")
            if isinstance(exc.stdout, bytes)
            else (exc.stdout or "")
        )
        stderr = (
            exc.stderr.decode("utf-8", errors="replace")
            if isinstance(exc.stderr, bytes)
            else (exc.stderr or "")
        )
        return CriterionResult(
            criterion=criterion,
            passed=False,
            returncode=124,
            duration_seconds=duration,
            stdout=stdout,
            stderr=stderr,
            detail=f"Timed out after {timeout}s",
        )
    except FileNotFoundError:
        duration = perf_counter() - started
        return CriterionResult(
            criterion=criterion,
            passed=False,
            returncode=127,
            duration_seconds=duration,
            stdout="",
            stderr=f"Command not found: {criterion.argv[0]}",
            detail=f"Missing executable: {criterion.argv[0]}",
        )

    duration = perf_counter() - started

    if criterion.criterion_type == "exitCodeEquals":
        passed = completed.returncode == criterion.expected
        detail = (
            f"exit {completed.returncode} == {criterion.expected}"
            if passed
            else f"exit {completed.returncode} != {criterion.expected}"
        )
    elif criterion.criterion_type == "outputNotContains":
        found = criterion.not_contains is not None and criterion.not_contains in completed.stdout
        passed = not found
        detail = (
            f"output clean of '{criterion.not_contains}'"
            if passed
            else f"output contains '{criterion.not_contains}'"
        )
    elif criterion.criterion_type == "outputContains":
        passed = criterion.contains is not None and criterion.contains in completed.stdout
        detail = (
            f"output contains '{criterion.contains}'"
            if passed
            else f"output missing '{criterion.contains}'"
        )
    elif criterion.criterion_type == "fileExists":
        target = Path(str(criterion.expected)) if criterion.expected else None
        passed = target is not None and (project_root / target).exists()
        detail = f"file {'exists' if passed else 'not found'}: {target}"
    else:
        passed = False
        detail = f"Unknown criterion type: {criterion.criterion_type}"

    return CriterionResult(
        criterion=criterion,
        passed=passed,
        returncode=completed.returncode,
        duration_seconds=duration,
        stdout=completed.stdout,
        stderr=completed.stderr,
        detail=detail,
    )


def _write_chore_log(
    project_root: Path,
    chore: ChoreDefinition,
    status: str,
    results: list[CriterionResult],
) -> Path:
    """Append one dated run entry to chore log."""
    log_path = _log_path(project_root, chore)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(
            f"# CHORE-LOG: {chore.slug}\n\n",
            encoding="utf-8",
        )

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines: list[str] = [
        f"## {timestamp}",
        f"- Status: {status}",
        f"- Chore: {chore.slug}",
        f"- Title: {chore.title}",
        f"- Lane: {chore.lane}",
        f"- Version: {chore.version}",
        "- Criteria Results:",
    ]
    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        lines.append(
            f"  - [{mark}] `{result.criterion.command}` "
            f"=> rc={result.returncode} "
            f"({result.duration_seconds:.2f}s) — {result.detail}"
        )

    lines.extend(["", "```text"])
    for result in results:
        if result.stdout.strip():
            lines.append(f"[{result.criterion.command}] stdout:")
            lines.append(result.stdout.strip())
        if result.stderr.strip():
            lines.append(f"[{result.criterion.command}] stderr:")
            lines.append(result.stderr.strip())
    lines.extend(["```", ""])

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return log_path


def chores_list() -> None:
    """List chore definitions from registry."""
    _registry_path, registry = _load_chores_registry()
    table = Table(title="Chores Registry")
    table.add_column("Slug", style="cyan")
    table.add_column("Lane", style="green")
    table.add_column("Version")
    table.add_column("Criteria", justify="right")
    table.add_column("Title")

    for chore in sorted(registry.values(), key=lambda item: item.slug):
        table.add_row(
            chore.slug,
            chore.lane,
            chore.version,
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
        desc = f" — {c.description}" if c.description else ""
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
        raise GzCliError(f"BLOCKERS:\n- Missing CHORE.md: {chore.path}/CHORE.md")
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
            f"({result.duration_seconds:.1f}s) — {result.detail}"
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
            raise GzCliError(
                "Chore criterion failed:\n"
                f"- chore: {chore.slug}\n"
                f"- criterion: {result.criterion.command}\n"
                f"- detail: {result.detail}\n"
                f"- log: "
                f"{log_path.relative_to(project_root).as_posix()}"
            )

    log_path = _write_chore_log(project_root, chore, "PASS", results)
    console.print(
        f"[green]Chore completed.[/green] log: {log_path.relative_to(project_root).as_posix()}"
    )


def chores_audit(*, all_chores: bool, slug: str | None) -> None:
    """Audit chores for log presence."""
    project_root = get_project_root()
    _registry_path, registry = _load_chores_registry()

    if all_chores:
        chores = sorted(registry.values(), key=lambda item: item.slug)
    else:
        if not slug:
            raise GzCliError("BLOCKERS:\n- Provide --all or --slug <slug>.")
        chore = registry.get(slug)
        if chore is None:
            raise GzCliError(f"BLOCKERS:\n- Unknown chore slug: {slug}")
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
