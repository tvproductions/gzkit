"""The position a pipeline run has reached: its model, replay, recorder and rebuild.

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

When a run is in flight is said once as well, in :func:`_launches_in_flight`.
The recorder and the marker rebuild both read it. :func:`rebuild_marker` decides
what ``gz state --repair`` does for the run launched last: restore one missing
marker file as a copy of its twin on disk, or, with neither file on disk, write
the payload it builds from the ledger rows it is handed. The command carries
out either through the marker module.
"""

import logging
import re
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from gzkit.core.models import OBPI_ANY_WIDTH_SHORT_ID_BODY
from gzkit.ledger import LedgerEvent, pipeline_stage_transition_event
from gzkit.ledger_semantics import _uncompleted_attestation_requirement
from gzkit.obpi_lifecycle import fold_renames
from gzkit.pipeline_markers import (
    STALE_MARKER_HOURS,
    advance_pipeline_markers,
    load_pipeline_json,
    load_plan_audit_receipt,
    marker_matches,
    pipeline_marker_paths,
    pipeline_marker_payload,
    pipeline_stage_name,
    pipeline_stage_output,
)
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


def marker_position(marker: Mapping[str, Any]) -> dict[str, str] | None:
    """Return the position inside its stage that ``marker`` records, or ``None``.

    This decides what counts as a recorded position when a marker is read, as
    the session orientation reads one for every run in flight (OBPI-0.35.0-15
    Requirement 10). A position is the last recorded boundary the run crossed:
    a ``kind`` (the Stage 2 task, the Stage 3 phase, the Stage 4 round or the
    Stage 5 step) and a ``label`` naming which one, each as text that is not
    blank, with the ``boundary`` command that marked the crossing. Anything
    short of a kind and a label in text is no position, never part of one: a
    launch with nothing after it records none, and a marker is a cache any
    process can write. A boundary that is missing or is no text is reported
    as empty and the position is still returned. Text comes back without the
    space around it.

    The result is plain data in the marker's own keys. It is a reading and no
    gate: nothing is refused on what a marker says (Requirement 12), and what
    a run has reached is decided from the ledger (:func:`replay_pipeline_position`).
    """
    held = marker.get("position")
    if not isinstance(held, Mapping):
        return None
    kind, label, boundary = (held.get(key) for key in ("kind", "label", "boundary"))
    if not isinstance(kind, str) or not isinstance(label, str):
        return None
    if not kind.strip() or not label.strip():
        return None
    marked_by = boundary.strip() if isinstance(boundary, str) else ""
    return {"kind": kind.strip(), "label": label.strip(), "boundary": marked_by}


_PIPELINE = "gz obpi pipeline"

#: The short form of an OBPI id: its leading ``OBPI-<semver>-<item>``, which is
#: all a TASK id or a REQ id carries and what an operator types. The item is the
#: whole run of digits, whatever its width: the match ends at the ``-`` that
#: begins the slug or at the end of the id, so item 10 is never the short form
#: of item 100 and a one-digit item has one.
_SHORT_OBPI_ID = re.compile(rf"{OBPI_ANY_WIDTH_SHORT_ID_BODY}(?=-|\Z)")

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


#: The entries ``gz obpi pipeline`` launches a run with: the full launch and each
#: ``--from`` re-entry. ``pipeline_launched`` is also written when ``gz adr
#: audit-begin`` opens an audit ceremony, under the ADR's id and the entry
#: ``audit`` (GHI #412: the nonce pairs a marker with its ledger row). That is
#: no OBPI pipeline run: the ceremony's marker carries the stage ``audit``,
#: which is no canonical stage, and no position, so it is never a run in flight.
_RUN_ENTRIES = frozenset({"full", *(stage for stage in CANONICAL_STAGES if stage != "implement")})

#: The receipt that ends a run (operator ruling 2026-10-11, OBPI-0.35.0-15
#: brief, Open Design Question 8: "Receipt ends the run"). The ruling is the
#: COMPLETION receipt. ``obpi_receipt_emitted`` carries other kinds too
#: (``validated``), and those end nothing.
_COMPLETION_RECEIPT = "completed"

#: The events that retire an OBPI and so end its run with no receipt (operator
#: ruling 2026-10-11, Open Design Question 12: retirement ends a run; operator
#: ruling 2026-10-12, Open Design Question 16: "supersede ends a run"). No
#: command writes a receipt for a retired OBPI, so its launch would otherwise
#: stay a run in flight for good. ``obpi_superseded`` is the row ``gz obpi
#: supersede`` writes under the superseded OBPI's id. ``obpi_unparked`` is
#: deliberately absent from every rule here: unparking releases the OBPI for
#: work and resumes nothing, and "a later launch starts a new run" (Question 12).
_RETIRING_EVENTS = frozenset({"obpi_parked", "obpi_withdrawn", "obpi_superseded"})


def _starts_run(row: PipelineLedgerRow) -> bool:
    """Return whether ``row`` launches an OBPI pipeline run.

    A launch row that names no entry is the full launch, as the replay reads it.
    """
    return row.event == "pipeline_launched" and (row.extra.get("entry") or "full") in _RUN_ENTRIES


def _ends_run(row: PipelineLedgerRow) -> bool:
    """Return whether ``row`` ends the run of the id it carries.

    The completion receipt ends it, and so does the OBPI being parked,
    withdrawn or superseded. A receipt of any other kind, or of no kind, ends
    nothing.
    """
    if row.event == "obpi_receipt_emitted":
        return row.extra.get("receipt_event") == _COMPLETION_RECEIPT
    return row.event in _RETIRING_EVENTS


def _launches_in_flight(events: Iterable[PipelineLedgerRow]) -> dict[str, PipelineLedgerRow]:
    """Return the launch of every run in flight, keyed by the id it carries.

    The one rule for when a run is in flight, read by the recorder and by the
    marker rebuild alike. A run is in flight from its latest launch
    (:func:`_starts_run`) until a row that ends it (:func:`_ends_run`) follows
    under the same id, in ledger order; a launch after that starts a new run.
    The marker is not consulted: a deleted marker would otherwise drop a
    crossing, and a stale one would invent a run. The launches come back
    oldest first, by the order their runs began.

    "The same id" is the same CURRENT NAME (operator rulings 2026-10-12, Open
    Design Questions 21 and 22): a rename ends no run, a receipt or a
    retirement written under the new id ends the run launched under the old
    one, and a later launch under either id starts a new run in its place. An
    id's current name is the ledger's own answer to where an artifact is now,
    :func:`gzkit.obpi_lifecycle.fold_renames` over the rename rows
    (:func:`_renames`), so a rename that is later reversed leaves both ids
    with the one name the OBPI has. Each launch is still keyed by the id its
    own row carries, the one key the replay, the rebuild and the marker files
    share.
    """
    rows = list(events)
    by_name = _launches_by_current_name(rows, fold_renames(_renames(rows)))
    return {launch.id: launch for launch in by_name.values()}


def _renames(rows: Iterable[PipelineLedgerRow]) -> list[tuple[str, str]]:
    """Return the ``(id, new id)`` pair of every ``artifact_renamed`` row, in ledger order.

    The rows are the ledger rows the recorder already reads: this module opens
    no ledger of its own. A row naming no new id contributes no pair. The
    pairs are what :func:`gzkit.obpi_lifecycle.fold_renames` folds; no rename
    is followed here.
    """
    pairs: list[tuple[str, str]] = []
    for row in rows:
        new_id = row.extra.get("new_id") if row.event == "artifact_renamed" else None
        if isinstance(new_id, str) and new_id:
            pairs.append((row.id, new_id))
    return pairs


def _launches_by_current_name(
    rows: Iterable[PipelineLedgerRow], current_names: Mapping[str, str]
) -> dict[str, PipelineLedgerRow]:
    """Return the launch of every run in flight, keyed by its id's current name.

    The loop of the in-flight rule (:func:`_launches_in_flight`): a launch
    replaces the run in flight under the same current name, and a row that
    ends a run ends the one under its id's current name. ``current_names`` is
    the fold of the ledger's renames; an id it does not hold was never
    renamed and is its own current name.
    """
    launches: dict[str, PipelineLedgerRow] = {}
    for row in rows:
        name = current_names.get(row.id, row.id)
        if _starts_run(row):
            launches.pop(name, None)
            launches[name] = row
        elif _ends_run(row):
            launches.pop(name, None)
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
    its OBPI is parked, withdrawn or superseded (:func:`_launches_in_flight`). A sibling
    under a reused semver is no ambiguity once its run has ended, or if it was
    never launched. A run is ended only by a row that follows its launch in the
    ledger, so a sibling launched after it was retired holds a run in flight
    until a later row ends it. Two siblings both launched
    and neither ended are two runs, and the short form then names neither.

    Ids are compared by current name (Open Design Questions 21 and 22),
    because the resolver the commands name an OBPI by follows the ledger's
    renames, and by the same fold
    (:func:`gzkit.obpi_lifecycle.fold_renames`): the id IS a launch's id when
    the two have one current name, so the old id and the new id both name a
    run launched before the rename, or between a rename and its reversal. The
    short form is that of the launch row's own id, the form its TASK ids
    carry, or of its current name.
    """
    rows = list(events)
    current_names = fold_renames(_renames(rows))
    by_name = _launches_by_current_name(rows, current_names)
    exact = by_name.get(current_names.get(obpi_id, obpi_id))
    if exact is not None:
        return [exact]
    return [
        launch
        for name, launch in by_name.items()
        if obpi_id in (_short_form(launch.id), _short_form(name))
    ]


def in_flight_launch_id(events: Iterable[PipelineLedgerRow], obpi_id: str) -> str | None:
    """Return the id the launch of the run ``obpi_id`` names carries, or ``None``.

    ``obpi_id`` is the launch id, an id the ledger renamed it to or from, or
    the short ``OBPI-<semver>-<item>`` form of either. The id returned is the
    launch row's own, whatever the OBPI is called now.
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
    flight: the launch that carries that id or an id the ledger renamed it to
    or from, or the one launch whose short ``OBPI-<semver>-<item>`` form it is
    (:func:`in_flight_launch_id`). The
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

    Returns what the ledger says the run has reached, or ``None`` when the id
    names no run in flight or names more than one, or the record could not be
    written.
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


class MarkerRebuild(BaseModel):
    """What a repair decides for one run in flight whose two marker files are not both on disk.

    Exactly one of three: the marker the ledger rebuilds, written to both
    files when neither is on disk; the missing file to restore as a copy of
    its twin, when one of the two is on disk; or the reason the run is declined.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="The id the run's launch carries")
    payload: dict[str, Any] | None = Field(
        None, description="The marker the ledger rebuilds; None when the run is not rebuilt"
    )
    restores: str | None = Field(
        None,
        description="Name of the missing marker file to restore as a copy of its twin on disk",
    )
    declined: str | None = Field(None, description="Why the run is not repaired; None when it is")

    @model_validator(mode="after")
    def _decides_one_thing(self) -> MarkerRebuild:
        decided = [self.payload, self.restores, self.declined]
        if sum(each is not None for each in decided) != 1:
            msg = "a rebuild carries a payload, a file to restore or the reason it declined: one"
            raise ValueError(msg)
        return self


def runs_in_flight(events: Iterable[PipelineLedgerRow]) -> list[str]:
    """Return the id of every run in flight, the latest launched first.

    The runs are the recorder's own (:func:`_launches_in_flight`): a rebuild
    considers exactly the runs a boundary would be recorded for.
    """
    return list(reversed(_launches_in_flight(events)))


def _marker_from_ledger(
    launch: PipelineLedgerRow, reached: PipelineReplay, receipt_state: str
) -> dict[str, Any]:
    """Return the marker a run's launch and its last crossing give, and nothing else.

    The payload is built as the launcher builds it and then advanced as the
    recorder advances it, so it holds what the deleted marker held. Its two
    times are the ledger's: the launch event's and the last crossing's. The
    dispatch caches are not here, because no launch or crossing carries them.
    """
    entry = str(launch.extra.get("entry") or "full")
    asks_a_human = _uncompleted_attestation_requirement() == "required"
    payload = pipeline_marker_payload(
        launch.id,
        launch.parent or "",
        str(launch.extra.get("lane") or ""),
        None if entry == "full" else entry,
        receipt_state,
        requires_human_attestation=asks_a_human,
        nonce=str(launch.extra["nonce"]),
    )
    payload["started_at"] = launch.ts
    payload["updated_at"] = reached.updated_at
    if reached.position is not None:
        payload["current_stage"] = reached.stage
        payload["position"] = reached.position.model_dump()
        payload.update(
            pipeline_stage_output(
                launch.id,
                reached.stage,
                blockers=reached.blockers,
                requires_human_attestation=asks_a_human,
            )
        )
    return payload


def _stale_on_arrival(updated_at: str, now: datetime) -> bool:
    """Return whether a marker last updated at ``updated_at`` would be stale at ``now``.

    The rule ``find_stale_pipeline_markers`` applies to a marker on disk,
    applied to one before it is written: older than ``STALE_MARKER_HOURS``, or
    a time that cannot be read.
    """
    try:
        crossed = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (now - crossed).total_seconds() / 3600 > STALE_MARKER_HOURS
    except ValueError, TypeError:
        return True


def _file_in_the_way(per_obpi: Path, legacy: Path, obpi_id: str) -> str | None:
    """Return why a file on disk stops the repair, or ``None`` when none does.

    A repair overwrites no file. A marker file that is on disk and does not
    read as this run's marker, whether it names another run or cannot be
    read, is left exactly as it is, and the run is declined.
    """
    if per_obpi.exists() and not marker_matches(per_obpi, obpi_id):
        return (
            f"its marker file {per_obpi.name} is on disk and does not read as this "
            "run's marker; a repair overwrites no file. Clear it with "
            "`uv run gz obpi pipeline --clear-stale`, then repair again"
        )
    if legacy.exists() and not marker_matches(legacy, obpi_id):
        named = (load_pipeline_json(legacy) or {}).get("obpi_id") or "no readable run"
        return (
            f"the legacy marker {legacy.name} is on disk and names {named}; a repair "
            "overwrites no file and no other run's marker"
        )
    return None


def _rebuild_refusal(
    launch: PipelineLedgerRow, reached: PipelineReplay, now: datetime
) -> str | None:
    """Return why the ledger rebuilds no marker for the run, or ``None`` when it may.

    A rebuild invents no nonce, and it writes no marker that stale detection
    would flag the moment it landed.
    """
    if not launch.extra.get("nonce"):
        return "its pipeline_launched event records no nonce, and a rebuild invents none"
    if _stale_on_arrival(reached.updated_at, now):
        return (
            f"its last recorded crossing ({reached.updated_at}) is older than "
            f"{STALE_MARKER_HOURS} hours, so its marker would be stale on arrival; "
            "launch the run again to resume it"
        )
    return None


def rebuild_marker(
    events: Iterable[PipelineLedgerRow], plans_dir: Path, obpi_id: str, *, now: datetime
) -> MarkerRebuild | None:
    """Return what a repair does for the run ``obpi_id`` carries, or ``None``.

    ``gz state --repair`` is the one caller and the one verb that rebuilds a
    marker (OBPI-0.35.0-15 Requirement 18). ``obpi_id`` is the id a launch in
    flight carries (:func:`runs_in_flight`). ``None`` means there is nothing
    to repair: no run is in flight under that id, or both its marker files
    are on disk and read as its own, in which case nothing is moved.

    Only the run launched last is repaired. The legacy marker is one file for
    the whole project and names the latest launch, as a launch leaves it, so
    an older run in flight is declined while a later one is in flight,
    whatever files are on disk: a marker written for it could take the legacy
    file and block the live run (Requirement 6).

    For the run launched last the result is one of three. A file on disk that
    does not read as its marker declines it (:func:`_file_in_the_way`): a
    repair overwrites no file. With exactly one of its two files on disk, the
    result names the missing one, which the caller restores as a copy of its
    twin, byte for byte, so nothing on disk is moved (Requirement 7). With
    neither on disk, the result carries the payload to write, built from the
    ledger rows, the plan-audit receipt read back from disk and the
    launcher's constants, or the reason the ledger rebuilds none
    (:func:`_rebuild_refusal`). A rebuilt ``updated_at`` is the time of the
    last recorded crossing and never ``now``, which only decides whether that
    crossing is already past the stale bound. This function reads the plans
    directory and writes nothing: the caller hands the decision to the marker
    module's writers.
    """
    rows = list(events)
    in_flight = _launches_in_flight(rows)
    launch = in_flight.get(obpi_id)
    reached = replay_pipeline_position(rows, obpi_id)
    if launch is None or reached is None:
        return None
    launched_last = next(reversed(in_flight))
    if obpi_id != launched_last:
        return MarkerRebuild(
            obpi_id=obpi_id,
            declined=(
                f"a later run is in flight ({launched_last}); the legacy marker belongs to "
                "the run launched last, and a repair writes no marker for an older one"
            ),
        )
    per_obpi, legacy = pipeline_marker_paths(plans_dir, obpi_id)
    own = [path for path in (per_obpi, legacy) if marker_matches(path, obpi_id)]
    if len(own) == 2:
        return None
    in_the_way = _file_in_the_way(per_obpi, legacy, obpi_id)
    if in_the_way is not None:
        return MarkerRebuild(obpi_id=obpi_id, declined=in_the_way)
    if own:
        missing = legacy if own[0] == per_obpi else per_obpi
        return MarkerRebuild(obpi_id=obpi_id, restores=missing.name)
    refusal = _rebuild_refusal(launch, reached, now)
    if refusal is not None:
        return MarkerRebuild(obpi_id=obpi_id, declined=refusal)
    receipt_state = load_plan_audit_receipt(plans_dir, obpi_id)[0]
    return MarkerRebuild(
        obpi_id=obpi_id, payload=_marker_from_ledger(launch, reached, receipt_state)
    )
