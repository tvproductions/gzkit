"""Chores command implementations."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import cast

from rich.table import Table

from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root

CHORES_REGISTRY_PATH = Path("config/gzkit.chores.json")
CHORE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_LANES = {"lite", "heavy"}
DEFAULT_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class ChoreStep:
    """Single executable step in a chore definition."""

    name: str
    argv: tuple[str, ...]
    timeout_seconds: int


@dataclass(frozen=True)
class ChoreDefinition:
    """Validated chore definition loaded from registry."""

    slug: str
    title: str
    lane: str
    description: str
    steps: tuple[ChoreStep, ...]
    evidence_commands: tuple[str, ...]
    acceptance_checks: tuple[str, ...]


@dataclass(frozen=True)
class StepExecution:
    """Execution result for one chore step."""

    step: ChoreStep
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str


def _raise_blockers(blockers: list[str]) -> None:
    """Raise a user-facing BLOCKERS error."""
    if not blockers:
        return
    raise GzCliError("BLOCKERS:\n" + "\n".join(f"- {item}" for item in blockers))


def _normalize_string_list(
    value: object,
    field_name: str,
    blockers: list[str],
    *,
    minimum: int = 1,
) -> tuple[str, ...]:
    """Parse and validate a string list field."""
    if not isinstance(value, list):
        blockers.append(f"{field_name} must be a JSON array of strings.")
        return ()
    parsed: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            blockers.append(f"{field_name} entries must be non-empty strings.")
            return ()
        parsed.append(item.strip())
    if len(parsed) < minimum:
        blockers.append(f"{field_name} must contain at least {minimum} item(s).")
    return tuple(parsed)


def _parse_step(
    raw_step: object,
    chore_slug: str,
    index: int,
    blockers: list[str],
) -> ChoreStep | None:
    """Parse one chore step definition."""
    step_path = f"chores[{chore_slug}].steps[{index}]"
    if not isinstance(raw_step, dict):
        blockers.append(f"{step_path} must be an object.")
        return None
    step_data = cast("dict[str, object]", raw_step)

    name = step_data.get("name")
    if not isinstance(name, str) or not name.strip():
        blockers.append(f"{step_path}.name must be a non-empty string.")
        return None

    if "command" in step_data:
        blockers.append(
            f"{step_path}.command is not allowed. Use argv arrays only for deterministic execution."
        )
        return None

    argv_raw = step_data.get("argv")
    argv = _normalize_string_list(argv_raw, f"{step_path}.argv", blockers)
    if not argv:
        return None

    timeout_raw = step_data.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    if not isinstance(timeout_raw, int) or timeout_raw <= 0:
        blockers.append(f"{step_path}.timeout_seconds must be a positive integer.")
        return None

    return ChoreStep(name=name.strip(), argv=argv, timeout_seconds=timeout_raw)


def _parse_chore(raw_chore: object, index: int, blockers: list[str]) -> ChoreDefinition | None:
    """Parse one chore definition."""
    if not isinstance(raw_chore, dict):
        blockers.append(f"chores[{index}] must be an object.")
        return None
    chore_data = cast("dict[str, object]", raw_chore)

    slug_raw = chore_data.get("slug")
    if not isinstance(slug_raw, str) or not CHORE_SLUG_RE.match(slug_raw):
        blockers.append(f"chores[{index}].slug must be kebab-case (for example: quality-check).")
        return None
    slug = slug_raw.strip()

    title_raw = chore_data.get("title")
    if not isinstance(title_raw, str) or not title_raw.strip():
        blockers.append(f"chores[{slug}].title must be a non-empty string.")
        return None
    title = title_raw.strip()

    lane_raw = chore_data.get("lane")
    if not isinstance(lane_raw, str) or lane_raw.strip().lower() not in ALLOWED_LANES:
        blockers.append(f"chores[{slug}].lane must be one of: {', '.join(sorted(ALLOWED_LANES))}.")
        return None
    lane = lane_raw.strip().lower()

    description_raw = chore_data.get("description", "")
    description = description_raw.strip() if isinstance(description_raw, str) else ""

    steps_raw = chore_data.get("steps")
    if not isinstance(steps_raw, list) or not steps_raw:
        blockers.append(f"chores[{slug}].steps must be a non-empty array.")
        return None

    parsed_steps: list[ChoreStep] = []
    for step_index, raw_step in enumerate(steps_raw):
        parsed_step = _parse_step(raw_step, slug, step_index, blockers)
        if parsed_step is not None:
            parsed_steps.append(parsed_step)

    evidence_raw = chore_data.get("evidence")
    if not isinstance(evidence_raw, dict):
        blockers.append(f"chores[{slug}].evidence must be an object.")
        return None
    evidence_data = cast("dict[str, object]", evidence_raw)
    evidence_commands = _normalize_string_list(
        evidence_data.get("commands"),
        f"chores[{slug}].evidence.commands",
        blockers,
    )

    acceptance_raw = chore_data.get("acceptance")
    if not isinstance(acceptance_raw, dict):
        blockers.append(f"chores[{slug}].acceptance must be an object.")
        return None
    acceptance_data = cast("dict[str, object]", acceptance_raw)
    acceptance_checks = _normalize_string_list(
        acceptance_data.get("checks"),
        f"chores[{slug}].acceptance.checks",
        blockers,
    )

    if not parsed_steps or not evidence_commands or not acceptance_checks:
        return None

    return ChoreDefinition(
        slug=slug,
        title=title,
        lane=lane,
        description=description,
        steps=tuple(parsed_steps),
        evidence_commands=evidence_commands,
        acceptance_checks=acceptance_checks,
    )


def _load_chores_registry() -> tuple[Path, dict[str, ChoreDefinition]]:
    """Load and validate the chores registry."""
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

    if payload.get("schema") != "gzkit.chores.v1":
        blockers.append("Registry schema must be 'gzkit.chores.v1'.")

    chores_raw = payload.get("chores")
    if not isinstance(chores_raw, list) or not chores_raw:
        blockers.append("Registry field 'chores' must be a non-empty array.")
        _raise_blockers(blockers)
        return registry_path, {}

    registry: dict[str, ChoreDefinition] = {}
    for index, raw_chore in enumerate(chores_raw):
        chore = _parse_chore(raw_chore, index, blockers)
        if chore is None:
            continue
        if chore.slug in registry:
            blockers.append(f"Duplicate chore slug in registry: {chore.slug}")
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


def _log_path(project_root: Path, slug: str) -> Path:
    """Compute deterministic log path for a chore slug."""
    config = ensure_initialized()
    return (
        project_root
        / config.paths.design_root
        / "briefs"
        / "chores"
        / f"CHORE-{slug}"
        / "logs"
        / "CHORE-LOG.md"
    )


def _write_chore_log(
    project_root: Path,
    registry_path: Path,
    chore: ChoreDefinition,
    status: str,
    step_results: list[StepExecution],
) -> Path:
    """Append one dated run entry to chore log."""
    log_path = _log_path(project_root, chore.slug)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(f"# CHORE-LOG: {chore.slug}\n\n", encoding="utf-8")

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    lines: list[str] = [
        f"## {timestamp}",
        f"- Status: {status}",
        f"- Chore: {chore.slug}",
        f"- Title: {chore.title}",
        f"- Lane: {chore.lane}",
        f"- Registry: {registry_path.relative_to(project_root).as_posix()}",
        "- Steps:",
    ]
    for result in step_results:
        cmd = " ".join(result.step.argv)
        lines.append(
            f"  - {result.step.name}: `{cmd}` => rc={result.returncode} "
            f"({result.duration_seconds:.2f}s)"
        )

    lines.append("- Evidence Commands:")
    for command in chore.evidence_commands:
        lines.append(f"  - {command}")

    lines.append("- Acceptance Checks:")
    for check in chore.acceptance_checks:
        lines.append(f"  - {check}")

    lines.extend(["", "```text"])
    for result in step_results:
        if result.stdout.strip():
            lines.append(f"[{result.step.name}] stdout:")
            lines.append(result.stdout.strip())
        if result.stderr.strip():
            lines.append(f"[{result.step.name}] stderr:")
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
    table.add_column("Steps", justify="right")
    table.add_column("Title")

    for chore in sorted(registry.values(), key=lambda item: item.slug):
        table.add_row(chore.slug, chore.lane, str(len(chore.steps)), chore.title)

    console.print(table)


def chores_plan(slug: str) -> None:
    """Render deterministic plan details for one chore."""
    project_root = get_project_root()
    registry_path, chore = _resolve_chore(slug)
    log_path = _log_path(project_root, chore.slug)

    console.print(f"[bold]Chore Plan: {chore.slug}[/bold]")
    console.print(f"  Title: {chore.title}")
    console.print(f"  Lane: {chore.lane}")
    console.print(f"  Registry: {registry_path.relative_to(project_root).as_posix()}")
    console.print(f"  Log path: {log_path.relative_to(project_root).as_posix()}")
    if chore.description:
        console.print(f"  Description: {chore.description}")

    console.print("  Steps:")
    for index, step in enumerate(chore.steps, start=1):
        console.print(
            f"    {index}. {step.name} (timeout: {step.timeout_seconds}s) -> {' '.join(step.argv)}"
        )

    console.print("  Evidence commands:")
    for command in chore.evidence_commands:
        console.print(f"    - {command}")

    console.print("  Acceptance checks:")
    for check in chore.acceptance_checks:
        console.print(f"    - {check}")


def chores_run(slug: str) -> None:
    """Execute one chore and append dated log output."""
    project_root = get_project_root()
    registry_path, chore = _resolve_chore(slug)
    executions: list[StepExecution] = []

    try:
        for step in chore.steps:
            started = perf_counter()
            completed = subprocess.run(
                list(step.argv),
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=step.timeout_seconds,
                check=False,
            )
            duration = perf_counter() - started
            step_result = StepExecution(
                step=step,
                returncode=completed.returncode,
                duration_seconds=duration,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
            executions.append(step_result)

            if completed.returncode != 0:
                log_path = _write_chore_log(
                    project_root,
                    registry_path,
                    chore,
                    status="FAIL",
                    step_results=executions,
                )
                raise GzCliError(
                    "Chore step failed:\n"
                    f"- chore: {chore.slug}\n"
                    f"- step: {step.name}\n"
                    f"- returncode: {completed.returncode}\n"
                    f"- log: {log_path.relative_to(project_root).as_posix()}"
                )
    except subprocess.TimeoutExpired as exc:
        duration = float(exc.timeout or 0)
        timeout_stdout = (
            exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        )
        timeout_stderr = (
            exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        )
        timeout_result = StepExecution(
            step=step,
            returncode=124,
            duration_seconds=duration,
            stdout=timeout_stdout,
            stderr=timeout_stderr,
        )
        executions.append(timeout_result)
        log_path = _write_chore_log(
            project_root,
            registry_path,
            chore,
            status="FAIL",
            step_results=executions,
        )
        raise GzCliError(
            "Chore step timed out:\n"
            f"- chore: {chore.slug}\n"
            f"- step: {step.name}\n"
            f"- timeout_seconds: {step.timeout_seconds}\n"
            f"- log: {log_path.relative_to(project_root).as_posix()}"
        ) from None
    except FileNotFoundError as exc:
        log_path = _write_chore_log(
            project_root,
            registry_path,
            chore,
            status="FAIL",
            step_results=executions,
        )
        raise GzCliError(
            "Chore step command not found:\n"
            f"- chore: {chore.slug}\n"
            f"- missing executable: {exc.filename}\n"
            f"- log: {log_path.relative_to(project_root).as_posix()}"
        ) from None

    log_path = _write_chore_log(
        project_root,
        registry_path,
        chore,
        status="PASS",
        step_results=executions,
    )
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
        log_path = _log_path(project_root, chore.slug)
        has_log = "yes" if log_path.exists() else "no"
        rel_path = log_path.relative_to(project_root).as_posix()
        table.add_row(chore.slug, chore.lane, has_log, rel_path)

    console.print(table)
