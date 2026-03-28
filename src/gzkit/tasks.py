"""TASK entity model for fourth-tier governance (ADR-0.22.0).

Defines the TASK entity: identifier parsing, lifecycle states, valid
transitions, and plan-derived creation.  Follows the ReqId/ReqEntity
pattern in ``triangle.py``.
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
