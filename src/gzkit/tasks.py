"""TASK entity model for fourth-tier governance (ADR-0.22.0).

Defines the TASK entity: identifier parsing, lifecycle states, valid
transitions, plan-derived creation, and git commit linkage (trailer
parsing, formatting, and four-tier chain resolution).

Follows the ReqId/ReqEntity pattern in ``triangle.py``.
"""

from __future__ import annotations

import enum
import re

from pydantic import BaseModel, ConfigDict, Field

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


def format_commit_trailer(task: TaskEntity | TaskId) -> str:
    """Produce a git commit trailer line from a TASK entity or identifier.

    Returns a string like ``Task: TASK-0.20.0-01-01-01``.
    """
    tid = task.id if isinstance(task, TaskEntity) else task
    return f"Task: {tid}"


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
