"""gz task CLI — lifecycle management for TASK entities (ADR-0.22.0 / OBPI-0.22.0-04).

Subcommands: list, start, complete, block, escalate.
"""

import json

from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root
from gzkit.events import (
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
)
from gzkit.ledger import LEDGER_SCHEMA, Ledger, LedgerEvent
from gzkit.tasks import TaskId, TaskStatus, derive_req_task_id
from gzkit.triangle import extract_reqs_from_brief


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
