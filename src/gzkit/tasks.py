"""TASK entity model for fourth-tier governance (ADR-0.22.0).

Defines the TASK entity: identifier parsing, lifecycle states, valid
transitions, plan-derived creation, and git commit linkage (trailer
parsing, formatting, and four-tier chain resolution).

Follows the ReqId/ReqEntity pattern in ``triangle.py``.
"""

from __future__ import annotations

import enum
import json
import pathlib
import re
import types
from collections.abc import Callable, Iterable
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

from gzkit.ledger_corrections import live_events

# ---------------------------------------------------------------------------
# TASK identifier
# ---------------------------------------------------------------------------

_TASK_PATTERN = re.compile(
    r"^TASK-(?P<semver>\d+\.\d+\.\d+)-(?P<obpi_item>\d+)-(?P<req_index>\d+)-(?P<seq>\d+)$"
)


class TaskId(BaseModel):
    """Parsed TASK identifier with structured fields.

    Identifier scheme: ``TASK-<semver>-<obpi_item>-<req_index>-<seq>``
    Example: ``TASK-0.20.0-01-01-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    semver: str = Field(..., description="SemVer portion (e.g. '0.20.0')")
    obpi_item: str = Field(..., description="OBPI item number (e.g. '01')")
    req_index: str = Field(..., description="REQ criterion index (e.g. '01')")
    seq: str = Field(..., description="Sequence number within the REQ (e.g. '01')")

    @classmethod
    def parse(cls, raw: str) -> TaskId:
        """Parse a TASK identifier string into a ``TaskId``.

        Raises ``ValueError`` when *raw* does not match the canonical pattern.
        """
        m = _TASK_PATTERN.match(raw.strip())
        if m is None:
            msg = f"Invalid TASK identifier: {raw!r}"
            raise ValueError(msg)
        return cls(
            semver=m.group("semver"),
            obpi_item=m.group("obpi_item"),
            req_index=m.group("req_index"),
            seq=m.group("seq"),
        )

    def __str__(self) -> str:
        """Return the canonical TASK identifier string."""
        return f"TASK-{self.semver}-{self.obpi_item}-{self.req_index}-{self.seq}"


# ---------------------------------------------------------------------------
# TASK lifecycle
# ---------------------------------------------------------------------------


class TaskStatus(enum.StrEnum):
    """TASK lifecycle states (exactly five)."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


_VALID_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.PENDING: frozenset({TaskStatus.IN_PROGRESS}),
    TaskStatus.IN_PROGRESS: frozenset(
        {TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.ESCALATED}
    ),
    TaskStatus.BLOCKED: frozenset({TaskStatus.IN_PROGRESS}),
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.ESCALATED: frozenset(),
}


# ---------------------------------------------------------------------------
# TASK entity
# ---------------------------------------------------------------------------


class TaskEntity(BaseModel):
    """A single execution-level task linked to a parent REQ and OBPI."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: TaskId = Field(..., description="Parsed TASK identifier")
    description: str = Field(..., description="Human-readable task description")
    status: TaskStatus = Field(..., description="Current lifecycle state")
    parent_req: str = Field(..., description="Parent REQ reference (e.g. 'REQ-0.20.0-01-01')")
    parent_obpi: str = Field(..., description="Parent OBPI reference (e.g. 'OBPI-0.20.0-01')")

    def transition(self, target: TaskStatus) -> TaskEntity:
        """Return a new ``TaskEntity`` with *target* status.

        Raises ``ValueError`` if the transition is not valid.
        """
        allowed = _VALID_TRANSITIONS.get(self.status, frozenset())
        if target not in allowed:
            msg = f"Invalid TASK transition: {self.status.value} -> {target.value}"
            raise ValueError(msg)
        return self.model_copy(update={"status": target})


_REQ_TO_TASK_RE = re.compile(r"^REQ-(\d+\.\d+\.\d+)-(\d+)-(\d+)$")


def next_seq_for_req(req_id: str, *, existing_task_ids: list[str]) -> int:
    """Return the next available seq for req_id given already-started TASK IDs.

    Scans existing_task_ids for TASK IDs whose prefix matches req_id (same
    semver, obpi_item, req_index) and returns max(seq) + 1. Returns 1 when
    no matching IDs exist.

    Raises:
        ValueError: If req_id does not match the expected REQ ID format.

    """
    m = _REQ_TO_TASK_RE.match(req_id)
    if not m:
        msg = f"Invalid REQ ID format: {req_id!r} (expected REQ-X.Y.Z-NN-MM)"
        raise ValueError(msg)
    semver, obpi_item, req_index = m.groups()
    prefix = f"TASK-{semver}-{obpi_item}-{req_index}-"
    max_seq = 0
    for task_id_str in existing_task_ids:
        if task_id_str.startswith(prefix):
            try:
                tid = TaskId.parse(task_id_str)
                max_seq = max(max_seq, int(tid.seq))
            except ValueError:
                pass
    return max_seq + 1


def derive_req_task_id(req_id: str, *, seq: int = 1) -> str:
    """Derive the canonical TASK ID for a given REQ ID.

    REQ-X.Y.Z-NN-MM → TASK-X.Y.Z-NN-MM-{seq:02d}

    The default ``seq=1`` is the auto-coordinated TASK that the OBPI pipeline
    creates on launch (one per REQ). Manual multi-cycle work increments seq
    via subsequent `gz task start TASK-X.Y.Z-NN-MM-PP` invocations.
    """
    match = _REQ_TO_TASK_RE.match(req_id)
    if not match:
        msg = f"Invalid REQ ID format: {req_id!r} (expected REQ-X.Y.Z-NN-MM)"
        raise ValueError(msg)
    semver, obpi_item, req_index = match.groups()
    return f"TASK-{semver}-{obpi_item}-{req_index}-{seq:02d}"


# ---------------------------------------------------------------------------
# Plan-derived factory
# ---------------------------------------------------------------------------


def create_task_from_plan_step(
    *,
    plan_text: str,
    parent_obpi: str,
    parent_req: str,
    semver: str,
    obpi_item: str,
    req_index: str,
    seq: int,
) -> TaskEntity:
    """Create a TASK entity from a plan-file step and parent context.

    *seq* is an integer that gets zero-padded to two digits in the identifier.
    """
    task_id = TaskId(
        semver=semver,
        obpi_item=obpi_item,
        req_index=req_index,
        seq=f"{seq:02d}",
    )
    return TaskEntity(
        id=task_id,
        description=plan_text,
        status=TaskStatus.PENDING,
        parent_req=parent_req,
        parent_obpi=parent_obpi,
    )


# ---------------------------------------------------------------------------
# Git commit linkage (OBPI-0.22.0-03)
# ---------------------------------------------------------------------------

_TRAILER_LINE_RE = re.compile(r"^Task:\s+(TASK-\d+\.\d+\.\d+-\d+-\d+-\d+)\s*$")

# Accepts the formal four-tier TASK ID `TASK-X.Y.Z-NN-MM-PP` (under an OBPI/REQ)
# OR the kebab slug-form `TASK-<kebab-slug>` with an OPTIONAL `-#<ghi>` anchor.
# The `#<ghi>` was made optional by operator mandate (2026-06-01): requiring a
# GHI number to commit any direct fix was the friction that turned the
# direct-fix path into a tarpit, and — paired with the producer never stamping
# a trailer — left the OBPI pipeline's git-sync emitting commit-trailer-failing
# commits. A GHI-less descriptive slug (e.g. `TASK-gz-git-sync`, the named
# git-sync ceremony attribution) is now a valid src/tests attribution; the
# `-#<ghi>` anchor remains accepted when present. The slug form cannot be
# parsed by `TaskId.parse`, so this regex is used only for trailer-presence
# detection (`has_task_trailer`); `parse_task_trailers` keeps the strict form.
_ANY_TASK_TRAILER_RE = re.compile(
    r"^Task:\s+TASK-(?:\d+\.\d+\.\d+-\d+-\d+-\d+|[a-z][a-z0-9-]*(?:-#\d+)?)\s*$"
)


def format_commit_trailer(task: TaskEntity | TaskId) -> str:
    """Produce a git commit trailer line from a TASK entity or identifier.

    Returns a string like ``Task: TASK-0.20.0-01-01-01``.
    """
    tid = task.id if isinstance(task, TaskEntity) else task
    return f"Task: {tid}"


_TRAILER_REQUIRED_ROOTS: tuple[str, ...] = ("src/", "tests/")

_TASK_CLOSING_EVENTS: frozenset[str] = frozenset(
    {"task_completed", "task_blocked", "task_escalated"}
)


def active_task_trailers(ledger_path: pathlib.Path, staged_paths: Iterable[str]) -> list[str]:
    """Return ``Task:`` trailer lines for every in-progress TASK.

    The pipeline mints one TASK per REQ and then relies on an author to recall
    each of them in a commit trailer. Measured 2026-07-29: 87 post-epoch OBPIs
    minted 467 TASKs that appear in no trailer at all, so the commit-trailer
    discovery channel is empty for 96 of 102 OBPIs and Signature (c) skips them
    — total under-declaration read as "nothing to compare" (GHI #731). Stamping
    the attribution the runtime already holds is the producer-side fix, the same
    move GHI #653 needed twice.

    Scoped, not blanket: `.gzkit/rules/tests.md` § TASK-Driven Workflow makes
    ``Task:`` mandatory on ``src/**`` and ``tests/**`` only, so a docs-only
    commit stamps nothing rather than manufacturing attribution the rule never
    asked for. Returns ``[]`` for an absent ledger and skips malformed lines —
    this runs inside a commit hook, where an exception blocks all work.
    """
    if not any(
        path.replace("\\", "/").startswith(_TRAILER_REQUIRED_ROOTS) for path in staged_paths
    ):
        return []
    try:
        raw = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return []

    rows: list[dict] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            rows.append(event)

    # This reader parses the JSONL itself rather than going through
    # ``Ledger.read_all`` (it runs inside a commit hook, where an exception
    # blocks all work), so it must apply the corrections explicitly or it
    # disagrees with `gz task list` about the same TASK — a discharged blocker
    # reads in_progress there and closed here (GHI #611).
    started: list[str] = []
    closed: set[str] = set()
    for event in live_events(rows):
        task_id = event.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            continue
        kind = event.get("event")
        if kind == "task_started":
            started.append(task_id)
        elif kind in _TASK_CLOSING_EVENTS:
            closed.add(task_id)

    seen: set[str] = set()
    return [
        f"Task: {task_id}"
        for task_id in started
        if task_id not in closed and not (task_id in seen or seen.add(task_id))
    ]


def parse_task_trailers(commit_message: str) -> list[TaskId]:
    """Extract TASK IDs from the trailer section of a commit message.

    The trailer section is the final paragraph — a contiguous block of
    ``Key: Value`` lines at the end of the message, separated from the
    body by a blank line.  Only ``Task:`` trailers with valid TASK IDs
    are returned; other trailers and body text are ignored.
    """
    lines = commit_message.rstrip("\n").split("\n")

    # Walk backwards to find the trailer block: contiguous key-value
    # lines at the end, preceded by a blank line.
    trailer_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if not line.strip():
            break
        if re.match(r"^[\w-]+:\s", line):
            trailer_start = i
        else:
            # Non-trailer, non-blank line — no trailer block here
            trailer_start = len(lines)
            break

    results: list[TaskId] = []
    for line in lines[trailer_start:]:
        m = _TRAILER_LINE_RE.match(line)
        if m:
            results.append(TaskId.parse(m.group(1)))
    return results


def has_task_trailer(commit_message: str) -> bool:
    """Return True if the commit's trailer block contains any ``Task:`` line.

    Accepts BOTH the formal four-tier ID `TASK-X.Y.Z-NN-MM-PP` and the slug-form
    `TASK-<slug>-#<ghi>` (direct-fix work outside OBPI scope). Used by
    `gz validate --commit-trailers` to enforce TASK discipline on src/tests
    commits without restricting direct-fix authors to formal IDs they have no
    OBPI to mint against.
    """
    lines = commit_message.rstrip("\n").split("\n")
    trailer_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if not line.strip():
            break
        if re.match(r"^[\w-]+:\s", line):
            trailer_start = i
        else:
            trailer_start = len(lines)
            break
    return any(_ANY_TASK_TRAILER_RE.match(line) for line in lines[trailer_start:])


_CEREMONY_TRAILER_RE = re.compile(r"^Ceremony:\s*(?P<value>\S+)\s*$")


def parse_ceremony_trailers(commit_message: str) -> list[str]:
    """Extract ``Ceremony: <value>`` markers from a commit's trailer block.

    Ceremony trailers satisfy the ``--commit-trailers`` governance-intent
    check for chore/sync commits that are not scoped to a single TASK
    (e.g. ``gz git-sync`` auto-commits bundling multi-OBPI reconcile work).
    The value names the governing ceremony (``gz-git-sync``,
    ``adr-closeout``, ``obpi-reconcile``) so audits can still trace the
    code change back to governance intent even without a TASK id.
    """
    lines = commit_message.rstrip("\n").split("\n")
    trailer_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if not line.strip():
            break
        if re.match(r"^[\w-]+:\s", line):
            trailer_start = i
        else:
            trailer_start = len(lines)
            break
    return [
        m.group("value")
        for line in lines[trailer_start:]
        if (m := _CEREMONY_TRAILER_RE.match(line))
    ]


_EVAL_FEEDBACK_SOURCE_TRAILER_RE = re.compile(r"^Eval-feedback-source:\s*(?P<value>\S+)\s*$")


def parse_eval_feedback_source_trailers(commit_message: str) -> list[str]:
    """Extract Eval-feedback-source: values from a commit's trailer block.

    Repeatable trailer. Format: Eval-feedback-source: <event-id-or-artifact-path>.
    Used to trace rule edits back to the evaluation feedback loop source artifacts.
    """
    lines = commit_message.rstrip("\n").split("\n")
    trailer_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if not line.strip():
            break
        if re.match(r"^[\w-]+:\s", line):
            trailer_start = i
        else:
            trailer_start = len(lines)
            break
    return [
        m.group("value")
        for line in lines[trailer_start:]
        if (m := _EVAL_FEEDBACK_SOURCE_TRAILER_RE.match(line))
    ]


def resolve_task_chain(task_id: TaskId) -> dict[str, str]:
    """Resolve the four-tier traceability chain from a TASK identifier.

    Returns a dict with keys ``task``, ``req``, ``obpi``, ``adr``
    derived purely from the identifier components.
    """
    return {
        "task": str(task_id),
        "req": f"REQ-{task_id.semver}-{task_id.obpi_item}-{task_id.req_index}",
        "obpi": f"OBPI-{task_id.semver}-{task_id.obpi_item}",
        "adr": f"ADR-{task_id.semver}",
    }


# ---------------------------------------------------------------------------
# @advances decorator and TASK attribution registry (OBPI-0.0.64-02)
# ---------------------------------------------------------------------------

_AF = TypeVar("_AF")


class TaskAttributionRecord(BaseModel):
    """A registered ``@advances`` decoration linking a function to a TASK.

    Captured at decoration time. Mirrors the precedent set by
    ``@covers``'s ``LinkageRecord`` but scoped to TASK-tier attribution
    on source functions (as opposed to REQ-tier attribution on tests).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = Field(..., description="TASK identifier (e.g. 'TASK-0.0.64-02-01-01')")
    source_fn: str = Field(..., description="Fully qualified function name")
    source_file: str | None = Field(
        None, description="Source file path rendered via .as_posix() (cross-platform rule)"
    )
    source_line: int | None = Field(None, description="1-indexed first source line of fn")


_ADVANCES_REGISTRY: list[TaskAttributionRecord] = []
_KNOWN_TASK_REQS: frozenset[str] | None = None


def _find_project_root_for_advances() -> pathlib.Path | None:
    """Walk up from CWD to find the project root (directory containing .gzkit/)."""
    current = pathlib.Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".gzkit").is_dir():
            return parent
    return None


def _load_known_task_reqs() -> frozenset[str]:
    """Scan briefs and cache the set of known parent REQ identifiers for TASKs.

    Follows ``@covers``'s ``_load_known_reqs`` lazy pattern. TASKs are validated
    by checking that their derived parent REQ (``REQ-<semver>-<obpi_item>-<req_index>``)
    exists in a discovered brief — TASK IDs themselves are not pre-registered.
    """
    global _KNOWN_TASK_REQS
    if _KNOWN_TASK_REQS is not None:
        return _KNOWN_TASK_REQS

    root = _find_project_root_for_advances()
    if root is None:
        _KNOWN_TASK_REQS = frozenset()
        return _KNOWN_TASK_REQS

    adr_dir = root / "docs" / "design" / "adr"
    if not adr_dir.is_dir():
        _KNOWN_TASK_REQS = frozenset()
        return _KNOWN_TASK_REQS

    # Local import to avoid a top-level cycle (gzkit.traceability imports
    # gzkit.triangle; gzkit.tasks is independent of both at import time).
    from gzkit.triangle import scan_briefs

    discovered = scan_briefs(adr_dir)
    _KNOWN_TASK_REQS = frozenset(str(d.entity.id) for d in discovered)
    return _KNOWN_TASK_REQS


def _qualified_fn_name(fn: object) -> str:
    """Return the fully qualified name of a function or method."""
    module = getattr(fn, "__module__", None) or "<unknown>"
    qualname = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", "<unknown>")
    return f"{module}.{qualname}"


def advances(task_id_str: str) -> Callable[[_AF], _AF]:
    """Declare that a function advances a governance TASK.

    Validates the TASK identifier format at decoration time, then validates
    that the parent REQ derived from the TASK ID exists in an extracted
    brief. Registers a :class:`TaskAttributionRecord` mapping the function
    to the TASK. The decorated function's behavior is unchanged — this is
    metadata-only attribution, peer to ``@covers``.

    Raises:
        ValueError: If *task_id_str* has an invalid format, or if the
            derived parent REQ is not found in the extracted brief-defined
            REQ set.

    """
    task_id = TaskId.parse(task_id_str)
    parent_req = f"REQ-{task_id.semver}-{task_id.obpi_item}-{task_id.req_index}"

    known = _load_known_task_reqs()
    if parent_req not in known:
        msg = (
            f"Unknown parent REQ for TASK {task_id_str!r}: "
            f"{parent_req} not found in extracted briefs"
        )
        raise ValueError(msg)

    def decorator(fn: _AF) -> _AF:
        source_file: str | None = None
        source_line: int | None = None
        code = getattr(fn, "__code__", None)
        if isinstance(code, types.CodeType):
            source_file = pathlib.Path(code.co_filename).as_posix()
            source_line = code.co_firstlineno

        record = TaskAttributionRecord(
            task_id=str(task_id),
            source_fn=_qualified_fn_name(fn),
            source_file=source_file,
            source_line=source_line,
        )
        _ADVANCES_REGISTRY.append(record)
        return fn

    return decorator


def get_task_registry() -> list[TaskAttributionRecord]:
    """Return a copy of the global TASK attribution registry."""
    return list(_ADVANCES_REGISTRY)


def set_known_task_reqs(reqs: frozenset[str]) -> None:
    """Inject known parent REQ identifiers for testing."""
    global _KNOWN_TASK_REQS
    _KNOWN_TASK_REQS = reqs


def reset_task_registry() -> None:
    """Clear the TASK attribution registry and cached known REQs. For testing only."""
    global _KNOWN_TASK_REQS
    _ADVANCES_REGISTRY.clear()
    _KNOWN_TASK_REQS = None
