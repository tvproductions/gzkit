"""The position a pipeline run has reached: its model, its replay and its recorder.

One module owns the run-position concept (OBPI-0.35.0-15, operator ruling on
Open Design Question 6). The dependency runs one way: this module imports
``pipeline_markers`` and that module never imports this one. This module writes
no marker file itself, so every marker write stays in the marker module and a
position reaches it as plain data. The ledger is taken as a parameter: the
replay reads the rows it is handed, and the recorder appends through the ledger
it is handed and never opens one.

Which boundaries move the stage is said once, in :data:`RULED_BOUNDARIES`. A
command reports the boundary it marked by name and the recorder decides the
stage from that table and the ledger, so no command chooses a stage.

Which run a command means is said once too, in :func:`in_flight_launch_id`. A
command hands over the OBPI id it holds, and the recorder finds the run among
the launches in flight on the ledger, so no command resolves an id for it.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from gzkit.ledger import LedgerEvent, pipeline_stage_transition_event
from gzkit.ledger_semantics import _uncompleted_attestation_requirement
from gzkit.pipeline_markers import advance_pipeline_markers, pipeline_stage_name
from gzkit.pipeline_stage_fence import CANONICAL_STAGES

logger = logging.getLogger(__name__)


class PipelinePosition(BaseModel):
    """Where inside a stage a run is: the last recorded boundary it crossed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str = Field(
        ...,
        min_length=1,
        description="Stage 2 task, Stage 3 phase, Stage 4 round or Stage 5 step",
    )
    label: str = Field(
        ..., min_length=1, description="Which task, phase, round or step was reached"
    )
    boundary: str = Field(..., min_length=1, description="Command that marked the crossing")


#: The kind of position each stage holds (GHI #1172): the Stage 2 task, the
#: Stage 3 phase, the Stage 4 round and the Stage 5 step.
STAGE_POSITION_KIND: Mapping[str, str] = MappingProxyType(
    {"implement": "task", "verify": "phase", "ceremony": "round", "sync": "step"}
)

_PIPELINE = "gz obpi pipeline"

#: The short form of an OBPI id: its leading ``OBPI-<semver>-<item>``, which is
#: all a TASK id or a REQ id carries and what an operator types. The item is the
#: whole run of digits, whatever its width: the match ends at the ``-`` that
#: begins the slug or at the end of the id, so item 10 is never the short form
#: of item 100 and a one-digit item has one.
_SHORT_OBPI_ID = re.compile(r"OBPI-\d+\.\d+\.\d+-\d+(?=-|\Z)")

#: The cut length, in characters, of the diagnostic summary of one blocker that
#: a transition event carries. The ledger is append-only and every reader pays
#: for every row, so an event holds enough to say which command failed and how
#: its output began, never the whole output; the console prints the output in
#: full when the command fails. Nothing gates on this value: no check, verdict
#: or exit code reads it. The operator ruled it an implementation detail on
#: 2026-10-11 (OBPI-0.35.0-15 brief, Open Design Question 11), so it is named
#: as a width and stays here. It is not policy and does not belong in ``data/``.
BLOCKER_SUMMARY_WIDTH = 240


class RunBoundary(BaseModel):
    """One boundary of the ruled set: who marks it, and what crossing it settles."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., min_length=1, description="Command that marks the crossing")
    enters: str | None = Field(
        None, description="Stage a work-starting boundary moves the run to; None records in place"
    )
    names_task: bool = Field(
        False, description="Whether the crossing supplies its own label: the task it marks"
    )
    sets_blockers: bool = Field(
        False,
        description="Whether the crossing is a verification result: its blockers are the run's",
    )


#: Every boundary a run records, and the one place that says which of them move
#: the stage and which settle the run's blockers (OBPI-0.35.0-15 Requirement 2 as
#: amended 2026-10-11 on Open Design Questions 7 to 10). The key is the
#: boundary's name and, unless the boundary names a task, the label of the
#: position it records.
#:
#: (a) A command that begins a stage's work moves the run to that stage
#:     (``enters``). The launch and each ``--from`` re-entry move it too; they
#:     write ``pipeline_launched`` and are not recorded through this table.
#: (b) A check or a bookkeeping event records in place (``enters`` is ``None``):
#:     its stage is the one the ledger replay says the run has reached and its
#:     kind is that stage's. It never changes what the post-Stage-2 fence reads.
#: (c) Two kinds of boundary settle the run's blockers and no other does. A
#:     verification result sets them to its own (``sets_blockers``): what a
#:     failure found, or nothing on a pass. A work-starting boundary clears
#:     them, because the work it begins answers them. Every other boundary
#:     carries them forward unchanged, so a check or a bookkeeping event
#:     recorded after a failed verification never erases it.
#:
#: Not boundaries: a spec or quality review import (Question 7), and
#: ``gz obpi sync``, which runs after the receipt that ends the run (Question 8).
RULED_BOUNDARIES: Mapping[str, RunBoundary] = MappingProxyType(
    {
        # (a) Work-starting: the stage moves.
        "dispatch": RunBoundary(command="gz obpi dispatch", enters="implement", names_task=True),
        "task-start": RunBoundary(command="gz task start", enters="implement", names_task=True),
        "verification": RunBoundary(command=_PIPELINE, enters="verify"),
        "ceremony": RunBoundary(command=_PIPELINE, enters="ceremony"),
        "present-evidence": RunBoundary(command="gz obpi present-evidence", enters="ceremony"),
        "complete": RunBoundary(command="gz obpi complete", enters="sync"),
        # (b) Checks and bookkeeping: recorded in place.
        "task-complete": RunBoundary(command="gz task complete", names_task=True),
        "task-block": RunBoundary(command="gz task block", names_task=True),
        "task-escalate": RunBoundary(command="gz task escalate", names_task=True),
        "verification-passed": RunBoundary(command=_PIPELINE, sets_blockers=True),
        "verification-failed": RunBoundary(command=_PIPELINE, sets_blockers=True),
        "precomplete": RunBoundary(command="gz obpi precomplete"),
        "verify-packet": RunBoundary(command="gz obpi verify-packet"),
        "acceptance-review": RunBoundary(command="gz obpi acceptance"),
    }
)


class RunCrossing(BaseModel):
    """One crossing of a ruled boundary, as the command that marked it reports it.

    The command names the boundary and, where the boundary names a task, the
    task. It never names a stage or a kind: those are decided from
    :data:`RULED_BOUNDARIES` and the ledger when the crossing is recorded.
    Only a verification result names blockers, because only it sets them.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    boundary: str = Field(..., description="Name of the boundary in RULED_BOUNDARIES")
    task: str | None = Field(None, description="The task marked, for a boundary that names one")
    blockers: list[str] = Field(
        default_factory=list, description="What a verification result found; empty on a pass"
    )

    @model_validator(mode="after")
    def _names_a_ruled_boundary(self) -> RunCrossing:
        ruled = RULED_BOUNDARIES.get(self.boundary)
        if ruled is None:
            msg = f"{self.boundary!r} is not a ruled boundary: {sorted(RULED_BOUNDARIES)}"
            raise ValueError(msg)
        if ruled.names_task != bool(self.task):
            expected = "names the task it marks" if ruled.names_task else "names no task"
            msg = f"a {self.boundary!r} crossing {expected}, got task={self.task!r}"
            raise ValueError(msg)
        if self.blockers and not ruled.sets_blockers:
            msg = (
                f"a {self.boundary!r} crossing settles no blockers and cannot name any: "
                "only a verification result sets them"
            )
            raise ValueError(msg)
        return self


class PipelineReplay(BaseModel):
    """What the ledger says a pipeline run has reached."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    stage: str = Field(..., description="Canonical stage the run has reached")
    position: PipelinePosition | None = Field(
        ..., description="Position inside the stage; None when nothing follows the launch"
    )
    blockers: list[str] = Field(..., description="Blockers the last crossing recorded")
    updated_at: str = Field(..., description="Time of the last recorded crossing")


class PipelineLedgerRow(Protocol):
    """The ledger-row shape the replay and the recorder read."""

    event: str
    id: str
    parent: str | None
    ts: str
    extra: dict[str, Any]


class PipelineLedger(Protocol):
    """The ledger shape the recorder writes through, so no ledger is opened here."""

    def read_all(self) -> Iterable[PipelineLedgerRow]:
        """Return the rows the ledger currently asserts, oldest first."""
        ...

    def append(self, event: LedgerEvent) -> None:
        """Append one row durably."""
        ...


def _recorded_crossing(row: PipelineLedgerRow) -> PipelineReplay | None:
    """Return what a transition row records, or ``None`` when it is not a crossing.

    A row is a crossing only when it carries what the event type requires: a
    canonical stage and a position's kind, label and boundary. Nothing is
    defaulted, so a malformed row never becomes a stage or a position.
    """
    recorded = row.extra
    if recorded.get("stage") not in CANONICAL_STAGES:
        return None
    try:
        return PipelineReplay.model_validate(
            {
                "stage": recorded["stage"],
                "position": {
                    "kind": recorded.get("position_kind"),
                    "label": recorded.get("position_label"),
                    "boundary": recorded.get("boundary"),
                },
                "blockers": recorded.get("blockers") or [],
                "updated_at": row.ts,
            }
        )
    except ValidationError:
        return None


def _launch_replay(launch: PipelineLedgerRow) -> PipelineReplay:
    """Return what a launch alone says: its stage, no position and its own time."""
    entry = str(launch.extra.get("entry") or "full")
    stage = pipeline_stage_name(None if entry == "full" else entry)
    return PipelineReplay(stage=stage, position=None, blockers=[], updated_at=launch.ts)


def replay_pipeline_position(
    events: Iterable[PipelineLedgerRow], obpi_id: str
) -> PipelineReplay | None:
    """Replay what a run has reached from the ledger rows alone.

    The run is the LATEST ``pipeline_launched`` for ``obpi_id`` and its position
    the last ``pipeline_stage_transition`` after it that records a crossing; a
    row of that type lacking a required field is skipped. With no crossing after
    the launch the result is the launch stage, no position and the launch's
    time. Returns ``None`` when no launch is recorded: a position with no
    Layer-2 source is never invented.
    """
    launch: PipelineLedgerRow | None = None
    reached: PipelineReplay | None = None
    for row in events:
        if row.id != obpi_id:
            continue
        if row.event == "pipeline_launched":
            launch, reached = row, None
        elif launch is not None and row.event == "pipeline_stage_transition":
            crossing = _recorded_crossing(row)
            if crossing is not None:
                reached = crossing
    if launch is None:
        return None
    return reached if reached is not None else _launch_replay(launch)


#: The events that end a run for the id they carry (operator ruling 2026-10-11,
#: OBPI-0.35.0-15 brief, Open Design Question 12: retirement ends a run). The
#: completion receipt ends it, and so does the OBPI being parked or withdrawn:
#: no command writes a receipt for a retired OBPI, so its launch would otherwise
#: stay a run in flight for good. ``obpi_parked`` and ``obpi_withdrawn`` are the
#: two events that make a ledger-graph key inactive for the launcher's short-id
#: resolution (``gzkit.artifact_prefix``).
_RUN_ENDING_EVENTS = frozenset({"obpi_receipt_emitted", "obpi_parked", "obpi_withdrawn"})


def _launches_in_flight(events: Iterable[PipelineLedgerRow]) -> dict[str, PipelineLedgerRow]:
    """Return the launch of every run in flight, keyed by the id it carries.

    A run is in flight from its latest ``pipeline_launched`` until one of
    :data:`_RUN_ENDING_EVENTS` follows it under the same id, in ledger order;
    a ``pipeline_launched`` after that starts a new run. The marker is not
    consulted: a deleted marker would otherwise drop a crossing, and a stale
    one would invent a run.
    """
    launches: dict[str, PipelineLedgerRow] = {}
    for row in events:
        if row.event == "pipeline_launched":
            launches[row.id] = row
        elif row.event in _RUN_ENDING_EVENTS:
            launches.pop(row.id, None)
    return launches


def _short_form(launch_id: str) -> str | None:
    """Return the short form a launch id begins with, or ``None`` when it has none."""
    match = _SHORT_OBPI_ID.match(launch_id)
    return match.group(0) if match else None


def _runs_named(events: Iterable[PipelineLedgerRow], obpi_id: str) -> list[PipelineLedgerRow]:
    """Return the launches in flight that ``obpi_id`` names: one, none or several.

    The one rule for which run an id means. The launch whose id IS the id
    given is the run, whatever else is in flight. Failing that, the runs are
    those whose short form is the id given: a command that holds only
    ``OBPI-<semver>-<item>`` (every ``gz task`` verb, an operator's typing)
    names the run that launch began. The match is the whole short form, never
    a prefix: the item number entire, so item 10 never names item 100, and
    nothing of the slug, so a sibling's full id names no run but its own.

    Only a run in flight is a candidate, and a run ends at its receipt or when
    its OBPI is parked or withdrawn (:func:`_launches_in_flight`). A sibling
    under a reused semver is therefore no ambiguity once it is finished or
    retired, whether or not it was ever launched. Two siblings both launched
    and neither ended are two runs, and the short form then names neither.
    """
    in_flight = _launches_in_flight(events)
    exact = in_flight.get(obpi_id)
    if exact is not None:
        return [exact]
    return [launch for launch_id, launch in in_flight.items() if _short_form(launch_id) == obpi_id]


def in_flight_launch_id(events: Iterable[PipelineLedgerRow], obpi_id: str) -> str | None:
    """Return the id the launch of the run ``obpi_id`` names carries, or ``None``.

    ``obpi_id`` is the launch id or its short ``OBPI-<semver>-<item>`` form.
    ``None`` when it names no run in flight, and when it names more than one:
    two runs in flight sharing a short form are not told apart by a guess.
    Pure: it reads the rows it is handed and nothing else.
    """
    named = _runs_named(events, obpi_id)
    return named[0].id if len(named) == 1 else None


def _run_in_flight(events: Iterable[PipelineLedgerRow], obpi_id: str) -> PipelineLedgerRow | None:
    """Return the launch of the one run ``obpi_id`` names, warning when it names several."""
    named = _runs_named(events, obpi_id)
    if len(named) > 1:
        logger.warning(
            "pipeline position for %s was not recorded: that id names %d runs in "
            "flight (%s); name the run by the full id its launch carries",
            obpi_id,
            len(named),
            ", ".join(launch.id for launch in named),
        )
    return named[0] if len(named) == 1 else None


def _blocker_summary(blocker: str) -> str:
    """Return ``blocker`` as a transition event carries it: at most the bound.

    A blocker within :data:`BLOCKER_SUMMARY_WIDTH` is kept as it is. A longer one,
    typically a failed command's whole output, becomes one line cut to the
    bound, which keeps how it began and ends by saying how long it was.
    """
    if len(blocker) <= BLOCKER_SUMMARY_WIDTH:
        return blocker
    line = " ".join(blocker.split())
    ending = f" ... [{len(blocker)} characters in all]"
    return line[: BLOCKER_SUMMARY_WIDTH - len(ending)] + ending


def _position_at(crossing: RunCrossing, reached: str) -> tuple[str, PipelinePosition]:
    """Return the stage and the position ``crossing`` records for a run at ``reached``.

    A work-starting boundary names the stage it enters; any other records
    inside ``reached``. The kind is the kind of the stage recorded, and the
    label is the task the crossing names or the boundary's own name.
    """
    ruled = RULED_BOUNDARIES[crossing.boundary]
    stage = ruled.enters or reached
    position = PipelinePosition(
        kind=STAGE_POSITION_KIND[stage],
        label=crossing.task or crossing.boundary,
        boundary=ruled.command,
    )
    return stage, position


def _blockers_after(crossing: RunCrossing, carried: list[str]) -> list[str]:
    """Return the run's blockers once ``crossing`` is recorded (ruling (c) of the table).

    A verification result sets them to its own, each as a bounded summary. A
    work-starting boundary clears them. Any other boundary carries forward the
    blockers the ledger replay says the run already has.
    """
    ruled = RULED_BOUNDARIES[crossing.boundary]
    if ruled.sets_blockers:
        return [_blocker_summary(blocker) for blocker in crossing.blockers]
    return [] if ruled.enters is not None else list(carried)


def record_position(
    ledger: PipelineLedger, plans_dir: Path, obpi_id: str, crossing: RunCrossing
) -> PipelineReplay | None:
    """Record one boundary a run crossed: the ledger first, the marker second.

    Nothing is recorded unless the ledger shows the run ``obpi_id`` names in
    flight: the launch that carries that id, or the one launch whose short
    ``OBPI-<semver>-<item>`` form it is (:func:`in_flight_launch_id`). The
    record is filed under THAT LAUNCH'S id, never the id as given, so a
    command that holds only the short form still records the boundary where
    every reader looks for it. An id that names two runs in flight records
    nothing and warns. Then one ``pipeline_stage_transition`` event is appended and
    both marker files are advanced to what a replay of the ledger now says, so
    a marker never holds a position the ledger lacks and takes the event's own
    time. Whether the stage moves is decided by :data:`RULED_BOUNDARIES`; a
    boundary that does not move it records inside the stage the ledger replay
    says the run has reached, never the stage a marker names (Requirement 12).
    The table also settles the blockers the event carries: a check recorded
    after a failed verification carries that failure's blockers forward.

    The record never fails the command that hosts it. A position is never gate
    evidence, so an I/O failure reading the ledger, appending the event or
    writing a marker warns and returns ``None``, and the command's own outcome
    stands. Only I/O is contained: a crossing is built before this is called,
    so a malformed one has already raised ``ValueError``, and any other defect
    in the record still raises.

    Returns what the ledger says the run has reached, or ``None`` when no run
    is in flight or the record could not be written.
    """
    try:
        return _record_crossing(ledger, plans_dir, obpi_id, crossing)
    except OSError as exc:
        logger.warning(
            "pipeline position for %s at boundary %r was not recorded in full: %s; "
            "the ledger holds whatever was recorded, and the command that marked "
            "the boundary is unaffected",
            obpi_id,
            crossing.boundary,
            exc,
        )
        return None


def _record_crossing(
    ledger: PipelineLedger, plans_dir: Path, obpi_id: str, crossing: RunCrossing
) -> PipelineReplay | None:
    """Append the crossing and advance the markers; I/O errors are the caller's."""
    rows = list(ledger.read_all())
    launch = _run_in_flight(rows, obpi_id)
    if launch is None:
        return None
    before = replay_pipeline_position(rows, launch.id)
    if before is None:
        return None
    stage, position = _position_at(crossing, before.stage)
    ledger.append(
        pipeline_stage_transition_event(
            obpi_id=launch.id,
            parent_adr=launch.parent or "",
            stage=stage,
            position_kind=position.kind,
            position_label=position.label,
            boundary=position.boundary,
            blockers=_blockers_after(crossing, before.blockers) or None,
        )
    )
    reached = replay_pipeline_position(ledger.read_all(), launch.id)
    if reached is not None and reached.position is not None:
        advance_pipeline_markers(
            plans_dir,
            launch.id,
            stage=reached.stage,
            position=reached.position.model_dump(),
            updated_at=reached.updated_at,
            blockers=reached.blockers,
            requires_human_attestation=_uncompleted_attestation_requirement() == "required",
        )
    return reached
