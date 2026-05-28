"""gz task CLI — lifecycle management for TASK entities (ADR-0.22.0 / OBPI-0.22.0-04).

Subcommands: list, start, complete, block, escalate.
"""

import json
import re
from pathlib import Path

from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root
from gzkit.events import (
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
)
from gzkit.ledger import LEDGER_SCHEMA, Ledger, LedgerEvent
from gzkit.tasks import TaskId, TaskStatus, derive_req_task_id, next_seq_for_req
from gzkit.triangle import extract_reqs_from_brief

_REQ_PARTS_RE = re.compile(r"^REQ-(\d+\.\d+\.\d+)-(\d+)-(\d+)$")


def _load_tasks_for_obpi(ledger: Ledger, obpi_id: str) -> dict[str, dict[str, str]]:
    """Build current TASK state from ledger events for an OBPI.

    Returns a dict keyed by task_id with ``status`` and ``description`` fields.
    """
    tasks: dict[str, dict[str, str]] = {}
    for event in ledger.read_all():
        extra = event.extra
        ev_type = event.event
        ev_obpi = extra.get("obpi_id", "")
        task_id = extra.get("task_id", "")
        if ev_obpi != obpi_id or not task_id:
            continue
        if ev_type == "task_started":
            tasks.setdefault(task_id, {"status": "pending", "description": ""})
            tasks[task_id]["status"] = TaskStatus.IN_PROGRESS.value
        elif ev_type == "task_completed":
            tasks.setdefault(task_id, {"status": "pending", "description": ""})
            tasks[task_id]["status"] = TaskStatus.COMPLETED.value
        elif ev_type == "task_blocked":
            tasks.setdefault(task_id, {"status": "pending", "description": ""})
            tasks[task_id]["status"] = TaskStatus.BLOCKED.value
            tasks[task_id]["reason"] = extra.get("reason", "")
        elif ev_type == "task_escalated":
            tasks.setdefault(task_id, {"status": "pending", "description": ""})
            tasks[task_id]["status"] = TaskStatus.ESCALATED.value
            tasks[task_id]["reason"] = extra.get("reason", "")
    return tasks


def _resolve_task_context(ledger: Ledger, task_id_str: str) -> tuple[TaskId, str, str]:
    """Parse a TASK ID and derive parent OBPI and ADR identifiers."""
    task_id = TaskId.parse(task_id_str)
    obpi_id = f"OBPI-{task_id.semver}-{task_id.obpi_item}"
    adr_id = f"ADR-{task_id.semver}"
    return task_id, obpi_id, adr_id


def _current_task_status(ledger: Ledger, task_id_str: str, obpi_id: str) -> TaskStatus:
    """Determine the current status of a task from ledger events."""
    status = TaskStatus.PENDING
    for event in ledger.read_all():
        extra = event.extra
        if extra.get("task_id") != task_id_str or extra.get("obpi_id") != obpi_id:
            continue
        if event.event == "task_started":
            status = TaskStatus.IN_PROGRESS
        elif event.event == "task_completed":
            status = TaskStatus.COMPLETED
        elif event.event == "task_blocked":
            status = TaskStatus.BLOCKED
        elif event.event == "task_escalated":
            status = TaskStatus.ESCALATED
    return status


def _emit_task_event(
    ledger: Ledger,
    event_model: TaskStartedEvent | TaskCompletedEvent | TaskBlockedEvent | TaskEscalatedEvent,
) -> None:
    """Serialize a typed task event and append to the ledger."""
    data = json.loads(event_model.model_dump_json())
    ledger.append(LedgerEvent.model_validate(data))


def auto_start_obpi_tasks(
    ledger: Ledger,
    *,
    obpi_id: str,
    parent_adr: str,
    brief_content: str,
    agent: str = "gz-obpi-pipeline",
) -> list[str]:
    """Auto-start one TASK (seq=01) per REQ declared in an OBPI brief.

    Called by ``gz obpi pipeline`` at full-launch entry (GHI #552 layer 4 —
    pipeline TASK auto-coordination). Idempotent: TASKs already started in the
    ledger are skipped silently. Returns the list of newly-started TASK IDs.

    Eliminates the manual-coordination friction that drove silent TASK
    abandonment (3 Task: vs. 305+ Ceremony: trailers in 30-day audit).
    """
    req_entities = extract_reqs_from_brief(brief_content, parent_obpi=obpi_id)
    existing = _load_tasks_for_obpi(ledger, obpi_id)
    started: list[str] = []
    for req in req_entities:
        try:
            task_id = derive_req_task_id(str(req.id))
        except ValueError:
            continue
        if task_id in existing:
            continue
        event = TaskStartedEvent(
            event="task_started",
            id=task_id,
            schema_=LEDGER_SCHEMA,
            task_id=task_id,
            obpi_id=obpi_id,
            adr_id=parent_adr,
            agent=agent,
        )
        _emit_task_event(ledger, event)
        started.append(task_id)
    return started


def auto_complete_obpi_tasks(
    ledger: Ledger,
    *,
    obpi_id: str,
    parent_adr: str,
    agent: str = "gz-obpi-pipeline",
) -> list[str]:
    """Auto-complete every in_progress TASK tied to an OBPI on receipt emission.

    Called by ``gz obpi complete`` after the ``obpi_receipt_emitted`` event
    lands (GHI #552 layer 4). Transitions in_progress TASKs to completed;
    skips terminal states (completed/blocked/escalated). Idempotent: already-
    completed TASKs are not re-emitted.
    """
    tasks = _load_tasks_for_obpi(ledger, obpi_id)
    completed: list[str] = []
    for task_id, info in tasks.items():
        if info["status"] != TaskStatus.IN_PROGRESS.value:
            continue
        event = TaskCompletedEvent(
            event="task_completed",
            id=task_id,
            schema_=LEDGER_SCHEMA,
            task_id=task_id,
            obpi_id=obpi_id,
            adr_id=parent_adr,
            agent=agent,
        )
        _emit_task_event(ledger, event)
        completed.append(task_id)
    return completed


def task_list_cmd(obpi: str, *, as_json: bool = False) -> None:
    """List all tasks for an OBPI with their current status."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    canonical = ledger.canonicalize_id(obpi)
    tasks = _load_tasks_for_obpi(ledger, canonical)

    if not tasks:
        if as_json:
            console.print(json.dumps({"obpi": canonical, "tasks": []}, indent=2))
        else:
            console.print(f"No tasks found for {canonical}.")
        return

    if as_json:
        rows = [{"task_id": tid, **info} for tid, info in sorted(tasks.items())]
        console.print(json.dumps({"obpi": canonical, "tasks": rows}, indent=2))
        return

    console.print(f"[bold]Tasks for {canonical}[/bold]\n")
    console.print(f"{'TASK ID':<30} {'STATUS':<15} {'REASON'}")
    console.print("-" * 70)
    for tid, info in sorted(tasks.items()):
        status = info["status"]
        reason = info.get("reason", "")
        console.print(f"{tid:<30} {status:<15} {reason}")


def task_start_cmd(task_id_str: str, *, as_json: bool = False) -> None:
    """Start or resume a task (pending/blocked -> in_progress)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    task_id, obpi_id, adr_id = _resolve_task_context(ledger, task_id_str)
    current = _current_task_status(ledger, str(task_id), obpi_id)

    if current not in (TaskStatus.PENDING, TaskStatus.BLOCKED):
        msg = f"Invalid TASK transition: {current.value} -> in_progress"
        raise GzCliError(msg)  # noqa: TRY003

    event = TaskStartedEvent(
        event="task_started",
        id=str(task_id),
        schema_=LEDGER_SCHEMA,
        task_id=str(task_id),
        obpi_id=obpi_id,
        adr_id=adr_id,
        agent="claude-code",
    )
    _emit_task_event(ledger, event)

    if as_json:
        console.print(
            json.dumps(
                {
                    "task_id": str(task_id),
                    "event": "task_started",
                    "from_status": current.value,
                    "to_status": "in_progress",
                },
                indent=2,
            )
        )
    else:
        label = "Resumed" if current == TaskStatus.BLOCKED else "Started"
        console.print(f"[green]{label}[/green] {task_id}")


def task_complete_cmd(task_id_str: str, *, as_json: bool = False) -> None:
    """Complete a task (in_progress -> completed)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    task_id, obpi_id, adr_id = _resolve_task_context(ledger, task_id_str)
    current = _current_task_status(ledger, str(task_id), obpi_id)

    if current != TaskStatus.IN_PROGRESS:
        msg = f"Invalid TASK transition: {current.value} -> completed"
        raise GzCliError(msg)  # noqa: TRY003

    event = TaskCompletedEvent(
        event="task_completed",
        id=str(task_id),
        schema_=LEDGER_SCHEMA,
        task_id=str(task_id),
        obpi_id=obpi_id,
        adr_id=adr_id,
        agent="claude-code",
    )
    _emit_task_event(ledger, event)

    if as_json:
        console.print(
            json.dumps(
                {
                    "task_id": str(task_id),
                    "event": "task_completed",
                    "from_status": current.value,
                    "to_status": "completed",
                },
                indent=2,
            )
        )
    else:
        console.print(f"[green]Completed[/green] {task_id}")


def task_block_cmd(task_id_str: str, reason: str, *, as_json: bool = False) -> None:
    """Block a task (in_progress -> blocked)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    task_id, obpi_id, adr_id = _resolve_task_context(ledger, task_id_str)
    current = _current_task_status(ledger, str(task_id), obpi_id)

    if current != TaskStatus.IN_PROGRESS:
        msg = f"Invalid TASK transition: {current.value} -> blocked"
        raise GzCliError(msg)  # noqa: TRY003

    event = TaskBlockedEvent(
        event="task_blocked",
        id=str(task_id),
        schema_=LEDGER_SCHEMA,
        task_id=str(task_id),
        obpi_id=obpi_id,
        adr_id=adr_id,
        agent="claude-code",
        reason=reason,
    )
    _emit_task_event(ledger, event)

    if as_json:
        console.print(
            json.dumps(
                {
                    "task_id": str(task_id),
                    "event": "task_blocked",
                    "from_status": current.value,
                    "to_status": "blocked",
                    "reason": reason,
                },
                indent=2,
            )
        )
    else:
        console.print(f"[yellow]Blocked[/yellow] {task_id}: {reason}")


def task_escalate_cmd(task_id_str: str, reason: str, *, as_json: bool = False) -> None:
    """Escalate a task (in_progress -> escalated)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    task_id, obpi_id, adr_id = _resolve_task_context(ledger, task_id_str)
    current = _current_task_status(ledger, str(task_id), obpi_id)

    if current != TaskStatus.IN_PROGRESS:
        msg = f"Invalid TASK transition: {current.value} -> escalated"
        raise GzCliError(msg)  # noqa: TRY003

    event = TaskEscalatedEvent(
        event="task_escalated",
        id=str(task_id),
        schema_=LEDGER_SCHEMA,
        task_id=str(task_id),
        obpi_id=obpi_id,
        adr_id=adr_id,
        agent="claude-code",
        reason=reason,
    )
    _emit_task_event(ledger, event)

    if as_json:
        console.print(
            json.dumps(
                {
                    "task_id": str(task_id),
                    "event": "task_escalated",
                    "from_status": current.value,
                    "to_status": "escalated",
                    "reason": reason,
                },
                indent=2,
            )
        )
    else:
        console.print(f"[red]Escalated[/red] {task_id}: {reason}")


def task_start_by_req_cmd(req_id: str, seq_arg: str, *, as_json: bool = False) -> None:
    """Start a new TASK for a REQ using --seq next|N (OBPI-0.0.64-03)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    m = _REQ_PARTS_RE.match(req_id)
    if not m:
        raise GzCliError(f"Invalid REQ identifier: {req_id!r}")  # noqa: TRY003
    semver, obpi_item, _ = m.groups()
    obpi_id = f"OBPI-{semver}-{obpi_item}"
    adr_id = f"ADR-{semver}"

    existing_tasks = _load_tasks_for_obpi(ledger, obpi_id)
    existing_ids = list(existing_tasks.keys())

    if seq_arg == "next":
        seq_num = next_seq_for_req(req_id, existing_task_ids=existing_ids)
    else:
        try:
            seq_num = int(seq_arg)
            if seq_num < 1:
                raise ValueError  # noqa: TRY301
        except ValueError:
            raise GzCliError(  # noqa: TRY003
                f"--seq must be 'next' or a positive integer, got {seq_arg!r}"
            ) from None
        candidate = derive_req_task_id(req_id, seq=seq_num)
        if candidate in existing_tasks:
            raise GzCliError(  # noqa: TRY003
                f"TASK {candidate} already exists; use --seq next or a different N"
            )

    task_id_str = derive_req_task_id(req_id, seq=seq_num)
    task_id = TaskId.parse(task_id_str)
    current = _current_task_status(ledger, task_id_str, obpi_id)
    if current not in (TaskStatus.PENDING, TaskStatus.BLOCKED):
        raise GzCliError(f"Invalid TASK transition: {current.value} -> in_progress")  # noqa: TRY003

    event = TaskStartedEvent(
        event="task_started",
        id=task_id_str,
        schema_=LEDGER_SCHEMA,
        task_id=task_id_str,
        obpi_id=obpi_id,
        adr_id=adr_id,
        agent="claude-code",
    )
    _emit_task_event(ledger, event)

    if as_json:
        console.print(
            json.dumps(
                {
                    "task_id": task_id_str,
                    "event": "task_started",
                    "from_status": current.value,
                    "to_status": "in_progress",
                },
                indent=2,
            )
        )
    else:
        console.print(f"[green]Started[/green] {task_id}")


def _find_brief_path(project_root: Path, obpi_id: str) -> Path | None:
    needle = obpi_id.removeprefix("OBPI-")
    for candidate in sorted(project_root.rglob("OBPI-*.md")):
        if needle in candidate.name:
            return candidate
    return None


def _collect_ledger_task_ids_for_obpi_prefix(ledger_path: Path, obpi_prefix: str) -> set[str]:
    import json as _json  # noqa: PLC0415

    result: set[str] = set()
    if not (ledger_path.exists() and obpi_prefix):
        return result
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        tid = ev.get("task_id")
        if tid and isinstance(tid, str):
            tm = re.match(r"^TASK-([\d.]+?-\d{2})-\d{2}-\d{2}$", tid)
            if tm and tm.group(1) == obpi_prefix:
                result.add(tid)
    return result


def _render_envelope_diagnose_table(
    brief_id: str, channels: dict[str, list[str]], drift: bool
) -> None:
    col = 44
    print(f"\nTask envelope diagnosis: {brief_id}")
    print("=" * (32 + col))
    print(f"{'Channel':<32}{'Task IDs':<{col}}")
    print("-" * (32 + col))
    for ch_name, tasks in channels.items():
        task_str = ", ".join(tasks) if tasks else "—"
        print(f"{ch_name:<32}{task_str:<{col}}")
    print("-" * (32 + col))
    print("⚠  Layer-drift detected" if drift else "✓  No layer-drift")
    print()


def task_envelope_diagnose_cmd(obpi_id: str, *, as_json: bool = False) -> None:
    """Render per-channel TASK declarations side-by-side for an OBPI (ADR-0.0.64/OBPI-04)."""
    import json as _json  # noqa: PLC0415
    import sys  # noqa: PLC0415

    from gzkit.governance.brief_structure import LegacyBriefShape, parse_brief  # noqa: PLC0415

    project_root = get_project_root()
    brief_path = _find_brief_path(project_root, obpi_id)
    if brief_path is None:
        print(f"Brief not found for: {obpi_id}", file=sys.stderr)
        raise SystemExit(1)

    brief = parse_brief(brief_path)
    if isinstance(brief, LegacyBriefShape):
        print("Brief is legacy shape; structured frontmatter required.", file=sys.stderr)
        raise SystemExit(1)

    ch2: set[str] = set(brief.tasks)
    m = re.match(r"^OBPI-([\d.]+?-\d{2})", brief.id)
    obpi_prefix = m.group(1) if m else ""
    ch4 = _collect_ledger_task_ids_for_obpi_prefix(
        project_root / ".gzkit" / "ledger.jsonl", obpi_prefix
    )

    channels: dict[str, list[str]] = {
        "@advances (ch1)": [],
        "frontmatter tasks: (ch2)": sorted(ch2),
        "commit trailers (ch3)": [],
        "ledger task_id (ch4)": sorted(ch4),
    }
    populated = [s for s in [ch2, ch4] if s]
    drift = len(populated) > 1 and len({frozenset(s) for s in populated}) > 1

    if as_json:
        print(_json.dumps({"obpi_id": brief.id, "channels": channels, "drift": drift}, indent=2))
        return

    _render_envelope_diagnose_table(brief.id, channels, drift)
