"""gz task CLI — lifecycle management for TASK entities (ADR-0.22.0 / OBPI-0.22.0-04).

Subcommands: list, start, complete, block, escalate.
"""

import json
import re
from pathlib import Path
from typing import TypedDict

from rich.markup import escape

from gzkit.commands.closeout_form import _append_frontmatter_list_value
from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root
from gzkit.events import (
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
)
from gzkit.ledger import LEDGER_SCHEMA, Ledger, LedgerEvent
from gzkit.ledger_corrections import live_events
from gzkit.tasks import TaskId, TaskStatus, derive_req_task_id, get_task_registry, next_seq_for_req
from gzkit.triangle import extract_reqs_from_brief

_REQ_PARTS_RE = re.compile(r"^REQ-(\d+\.\d+\.\d+)-(\d+)-(\d+)$")
_OBPI_LINEAGE_RE = re.compile(r"^(OBPI-\d+\.\d+\.\d+-\d+)")


def _obpi_lineage_id(obpi_id: str) -> str:
    """Return the slug-independent OBPI identity used by TASK ids."""
    match = _OBPI_LINEAGE_RE.match(obpi_id)
    return match.group(1) if match else obpi_id


def _load_tasks_for_obpi(ledger: Ledger, obpi_id: str) -> dict[str, dict[str, str]]:
    """Build current TASK state from ledger events for an OBPI.

    Returns a dict keyed by task_id with ``status`` and ``description`` fields.
    """
    tasks: dict[str, dict[str, str]] = {}
    for event in live_events(ledger.read_all()):
        extra = event.extra
        ev_type = event.event
        ev_obpi = extra.get("obpi_id", "")
        task_id = extra.get("task_id", "")
        if _obpi_lineage_id(ev_obpi) != _obpi_lineage_id(obpi_id) or not task_id:
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


def _ledger_obpi_for_task(ledger: Ledger, task_id_str: str) -> str:
    """Return the OBPI id recorded on the task's ``task_started`` event.

    ``gz obpi pipeline`` records the *full* OBPI slug (e.g.
    ``OBPI-0.0.37-17-agents-md-density-classification``); the short
    ``OBPI-<semver>-<item>`` form derived from the TASK id alone does not equal
    it, so status resolution must read the slug the ledger actually carries.
    Returns ``""`` when no ``task_started`` event names the task.
    """
    obpi_id = ""
    for event in live_events(ledger.read_all()):
        extra = event.extra
        if extra.get("task_id") == task_id_str and event.event == "task_started":
            recorded = extra.get("obpi_id", "")
            if recorded:
                obpi_id = recorded
    return obpi_id


def _resolve_obpi_id(ledger: Ledger, short_obpi: str, *, project_root: Path | None = None) -> str:
    """Resolve a short OBPI id (``OBPI-<semver>-<item>``) to its full slug.

    Mirrors ``Ledger.resolve_artifact_id``'s short->long ADR logic for the OBPI
    namespace: when exactly one artifact-graph key extends the short id with a
    ``-<slug>`` suffix, return that full slug; an absent or ambiguous prefix
    returns the short id unchanged. ``gz obpi pipeline`` records the full slug,
    so canonicalizing here keeps a manually-started TASK's ``obpi_id`` identical
    to the pipeline's instead of writing a divergent short form (GHI #653).
    """
    graph = ledger.get_artifact_graph()
    prefix = f"{short_obpi}-"
    matches = [key for key in graph if key.startswith(prefix)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1 and project_root is not None:
        # Layer-2 may name OBPIs Layer-1 cannot show — orphaned `obpi_created`
        # records accumulate (that is why `audit_obpi_lifecycle_coherence`
        # exists), and one phantom sharing the short prefix is enough to make a
        # genuinely-unambiguous id look ambiguous and force the divergent short
        # form. Disambiguate by on-disk brief: canon decides. Two REAL briefs
        # stay ambiguous — guessing would write a confidently wrong obpi_id.
        on_disk = [key for key in matches if _find_brief_path(project_root, key) is not None]
        if len(on_disk) == 1:
            return on_disk[0]
    return short_obpi


def _all_started_task_ids(ledger: Ledger) -> set[str]:
    """Return every ``task_id`` with a ``task_started`` event, ignoring ``obpi_id``.

    Start-dedup must key on ``task_id`` alone: a TASK already started under a
    different ``obpi_id`` spelling (e.g. the short form a manual ``gz task
    start`` wrote before the pipeline ran) must not be double-started under the
    full slug (GHI #653).
    """
    started: set[str] = set()
    for event in live_events(ledger.read_all()):
        if event.event == "task_started":
            task_id = event.extra.get("task_id", "")
            if task_id:
                started.add(task_id)
    return started


def _resolve_task_context(ledger: Ledger, task_id_str: str) -> tuple[TaskId, str, str]:
    """Parse a TASK ID and derive parent OBPI and ADR identifiers.

    The OBPI id is taken from the task's ``task_started`` ledger event when
    present (authoritative — the pipeline records the full OBPI slug). When no
    such event exists yet (the first ``gz task start``), the short
    ``OBPI-<semver>-<item>`` form derived from the TASK id is canonicalized to
    its full slug via ``_resolve_obpi_id`` so the short form is never written —
    keeping ``_current_task_status`` (which filters on ``obpi_id``) and the
    emitted transition event consistent with the slug the pipeline records
    (GHI #653).
    """
    task_id = TaskId.parse(task_id_str)
    adr_id = f"ADR-{task_id.semver}"
    derived = f"OBPI-{task_id.semver}-{task_id.obpi_item}"
    obpi_id = _ledger_obpi_for_task(ledger, task_id_str) or _resolve_obpi_id(ledger, derived)
    return task_id, obpi_id, adr_id


def _current_task_status(ledger: Ledger, task_id_str: str, obpi_id: str) -> TaskStatus:
    """Determine the current status of a task from ledger events."""
    status = TaskStatus.PENDING
    for event in live_events(ledger.read_all()):
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
    project_root: Path | None = None,
) -> list[str]:
    """Auto-start one TASK (seq=01) per REQ declared in an OBPI brief.

    Called by ``gz obpi pipeline`` at full-launch entry (GHI #552 layer 4 —
    pipeline TASK auto-coordination). Idempotent: TASKs already started in the
    ledger are skipped silently. Returns the list of newly-started TASK IDs.

    Eliminates the manual-coordination friction that drove silent TASK
    abandonment (3 Task: vs. 305+ Ceremony: trailers in 30-day audit).

    ``project_root`` stamps each minted TASK into the brief's ``tasks:``
    discovery channel, exactly as both manual ``gz task start`` paths do
    (GHI #752, reopened 2026-08-17). This is the third and highest-traffic
    producer of ``task_started``; leaving it unstamped kept the frontmatter
    channel empty precisely where the pipeline does the minting. Optional
    because the ledger write is the governance record and the declaration is
    best-effort — attribution must never block the pipeline.
    """
    req_entities = extract_reqs_from_brief(brief_content, parent_obpi=obpi_id)
    existing = _all_started_task_ids(ledger)
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
        if project_root is not None:
            _stamp_brief_task_declaration(project_root, obpi_id, task_id)
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
        console.print(f"{tid:<30} {status:<15} {escape(reason)}")


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
    _stamp_brief_task_declaration(project_root, obpi_id, str(task_id))

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
        console.print(f"[yellow]Blocked[/yellow] {task_id}: {escape(reason)}")


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
        console.print(f"[red]Escalated[/red] {task_id}: {escape(reason)}")


def task_start_by_req_cmd(req_id: str, seq_arg: str, *, as_json: bool = False) -> None:
    """Start a new TASK for a REQ using --seq next|N (OBPI-0.0.64-03)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    m = _REQ_PARTS_RE.match(req_id)
    if not m:
        raise GzCliError(f"Invalid REQ identifier: {req_id!r}")  # noqa: TRY003
    semver, obpi_item, _ = m.groups()
    short_obpi_id = f"OBPI-{semver}-{obpi_item}"
    obpi_id = _resolve_obpi_id(ledger, short_obpi_id, project_root=project_root)
    # Same canonicalization for the ADR: `gz obpi complete` records the full
    # slug, so emitting the bare `ADR-<semver>` here writes the same class of
    # spelling divergence this producer was repaired for (GHI #653).
    adr_id = ledger.resolve_artifact_id(f"ADR-{semver}")

    existing_ids = _all_started_task_ids(ledger)

    if seq_arg == "next":
        seq_num = next_seq_for_req(req_id, existing_task_ids=list(existing_ids))
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
        if candidate in existing_ids:
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
    _stamp_brief_task_declaration(project_root, obpi_id, task_id_str)

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
    """Resolve an OBPI id to its brief under canon, never to a same-named file elsewhere.

    Anchored twice, because the lookup was unanchored twice over (GHI #824).

    The SEARCH ROOT is the ADR tree, via the canonical brief-discovery helper
    rather than a second copy of the walk. A project-root ``rglob`` treats every
    ``OBPI-*.md`` in the working tree as a candidate brief, and ``gz obpi
    pipeline`` names its own plan files ``OBPI-<id>-<slug>.md`` — so the
    collision fires for every OBPI that ever passed the plan-audit gate, and
    ``.claude/`` sorts before ``docs/``. Measured at filing: 164 of this repo's
    542 short ids resolved to a plan file.

    The MATCH is stem-anchored. ``needle in candidate.name`` is a substring test,
    so a slug that merely MENTIONS another id (``migrate-0.1.0-01-artifacts``)
    reads as that id.

    Ambiguity returns None rather than taking a lexical tiebreak — the stance
    ``_canonical_obpi_id`` already takes one function up: guessing between two
    real briefs writes a confidently wrong answer. Silence is recoverable;
    a stamp in the wrong artifact is not, because the caller cannot tell the two
    apart (`_stamp_brief_task_declaration` is best-effort by contract).
    """
    from gzkit.commands.validate_briefs import _find_obpi_briefs  # noqa: PLC0415

    briefs = _find_obpi_briefs(project_root)
    exact = [path for path in briefs if path.stem == obpi_id]
    if len(exact) == 1:
        return exact[0]
    prefixed = [path for path in briefs if path.stem.startswith(f"{obpi_id}-")]
    return prefixed[0] if len(prefixed) == 1 else None


def _stamp_brief_task_declaration(project_root: Path, obpi_id: str, task_id: str) -> Path | None:
    """Declare ``task_id`` in its OBPI brief's ``tasks:`` discovery channel.

    Fixes the producer rather than the gate — the same move the commit-trailer
    channel needed (GHI #731). ``task_start`` already resolves the OBPI id at the
    moment the TASK is minted, so the declaration is runtime-known; asking an
    author to restate it is the convention that decayed to ~15% on the trailer
    channel and to zero here (GHI #752).

    Best-effort by design: minting the TASK is the operator's work and the
    declaration is the governance record of it. An unfindable or unwritable brief
    returns None rather than raising, so attribution can never block the pipeline.
    """
    brief = _find_brief_path(project_root, obpi_id)
    if brief is None:
        return None
    try:
        content = brief.read_text(encoding="utf-8")
        updated = _append_frontmatter_list_value(content, "tasks", task_id)
        if updated != content:
            brief.write_text(updated, encoding="utf-8")
    except OSError:
        return None
    return brief


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

    from gzkit.commands.validate_task_envelope import (  # noqa: PLC0415
        _channel_declarations_for_obpi,
        _crossing_channels,
    )
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

    # Collect ALL FOUR discovery channels — the diagnose surface is the ADR-0.0.64
    # named layer-drift recovery view, so it MUST read the same @advances (ch1) and
    # commit-trailer (ch3) channels the validator's signature (c) evaluates, not just
    # frontmatter + ledger. Routes through the validator's own four-channel collector
    # (single source of truth) rather than re-deriving a 2-channel subset.
    # ``_obpi_lineage_id`` rather than a fourth inline spelling of the same regex:
    # the local one truncated on ``\d{2}`` where every other normalizer reads ``\d+``
    # (GHI #946).
    decls = _channel_declarations_for_obpi(project_root, _obpi_lineage_id(brief.id))

    channels: dict[str, list[str]] = {
        "@advances (ch1)": sorted(decls["advances"]),
        "frontmatter tasks: (ch2)": sorted(decls["frontmatter"]),
        "commit trailers (ch3)": sorted(decls["commit_trailer"]),
        "ledger task_id (ch4)": sorted(decls["ledger"]),
    }
    # ONE drift predicate for both consumers. Computing it locally re-stated
    # `tids != all_tasks` under another spelling — any inequality read as drift —
    # which GHI #820 overturned: a channel merely BEHIND is not contradicting, and
    # reporting it as drift invites the falsified attribution #820 forbids. The
    # validator's own failure text sends the operator straight to this view, so the
    # two must not answer differently (GHI #820, reopened).
    non_empty = {name: tids for name, tids in decls.items() if tids}
    drift = bool(_crossing_channels(non_empty))

    if as_json:
        print(_json.dumps({"obpi_id": brief.id, "channels": channels, "drift": drift}, indent=2))
        return

    _render_envelope_diagnose_table(brief.id, channels, drift)


class FanoutRow(TypedDict):
    """One per-TASK fan-out row as rendered by ``gz task fanout``.

    A ``TypedDict`` rather than a model: these rows are a JSON transport shape
    serialised verbatim by ``--json``, and the heterogeneous value types
    (``str`` vs ``int``) are what make ``seq`` sortable.
    """

    task_id: str
    seq: int
    status: str
    files_touched: int
    edits: int
    attribution_check: str


def _build_fanout_rows(ledger: Ledger, req_id: str) -> list[FanoutRow]:
    """Build per-TASK fan-out rows for a REQ-ID from ledger events.

    Returns a list of :class:`FanoutRow` sorted by seq, each with:
    task_id, seq, status, files_touched, edits, attribution_check.
    """
    m = _REQ_PARTS_RE.match(req_id)
    if not m:
        raise GzCliError(f"Invalid REQ identifier: {req_id!r}")  # noqa: TRY003
    semver, obpi_item, req_index = m.groups()
    obpi_id = f"OBPI-{semver}-{obpi_item}"
    task_prefix = f"TASK-{semver}-{obpi_item}-{req_index}-"

    # Scan ledger events once and accumulate per-task data.
    task_status: dict[str, str] = {}
    task_files: dict[str, set[str]] = {}
    task_edits: dict[str, int] = {}

    for event in live_events(ledger.read_all()):
        extra = event.extra
        ev_type = event.event
        ev_obpi = extra.get("obpi_id", "")
        tid = extra.get("task_id", "")

        # Lifecycle events — must match obpi_id and task_prefix.
        if ev_obpi == obpi_id and tid and tid.startswith(task_prefix):
            task_edits[tid] = task_edits.get(tid, 0) + 1
            if ev_type == "task_started":
                task_status[tid] = TaskStatus.IN_PROGRESS.value
            elif ev_type == "task_completed":
                task_status[tid] = TaskStatus.COMPLETED.value
            elif ev_type == "task_blocked":
                task_status[tid] = TaskStatus.BLOCKED.value
            elif ev_type == "task_escalated":
                task_status[tid] = TaskStatus.ESCALATED.value

        # artifact_edited events attributed to a matching task.
        if ev_type == "artifact_edited" and tid and tid.startswith(task_prefix):
            path = extra.get("path", "")
            if path:
                task_files.setdefault(tid, set()).add(path)
            task_edits[tid] = task_edits.get(tid, 0) + 1

    rows: list[FanoutRow] = []
    for tid in sorted(task_status):
        seq_str = tid.rsplit("-", 1)[-1]
        try:
            seq_num = int(seq_str)
        except ValueError:
            seq_num = 0
        rows.append(
            {
                "task_id": tid,
                "seq": seq_num,
                "status": task_status[tid],
                "files_touched": len(task_files.get(tid, set())),
                "edits": task_edits.get(tid, 0),
                "attribution_check": "pass",
            }
        )
    rows.sort(key=lambda r: r["seq"])
    return rows


def task_fanout_cmd(req_id: str, *, detail: bool = False, as_json: bool = False) -> None:
    """Show TASK fan-out for a REQ-ID (ADR-0.0.64/OBPI-05)."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    m = _REQ_PARTS_RE.match(req_id)
    if not m:
        raise GzCliError(f"Invalid REQ identifier: {req_id!r}")  # noqa: TRY003

    rows = _build_fanout_rows(ledger, req_id)

    if not rows:
        console.print(f"No tasks found for {req_id}.")
        return

    if as_json:
        console.print(json.dumps(rows, indent=2))
        return

    if detail:
        registry = get_task_registry()
        for row in rows:
            tid = str(row["task_id"])
            console.print(f"{escape(tid)}  \\[{row['status']}]")
            matches = [r for r in registry if r.task_id == tid]
            if matches:
                for rec in matches:
                    if rec.source_file and rec.source_line:
                        console.print(f"  └─ {rec.source_file}:{rec.source_line}")
                    else:
                        console.print("  └─ (no @advances decorators)")
            else:
                console.print("  └─ (no @advances decorators)")
        return

    # Default: table output.
    header = f"{'TASK':<35} {'seq':>4}  {'status':<12} {'files':>6}  {'edits':>6}  {'check':<8}"
    console.print(header)
    console.print("-" * len(header))
    for row in rows:
        console.print(
            f"{str(row['task_id']):<35} {row['seq']:>4}  "
            f"{str(row['status']):<12} {row['files_touched']:>6}  "
            f"{row['edits']:>6}  {str(row['attribution_check']):<8}"
        )
