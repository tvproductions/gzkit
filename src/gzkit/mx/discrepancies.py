"""The list of discrepancies' writer and reducer (RP-12 O4 task 2).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the list of discrepancies
is ledger events, rendered as a view (ruling 9). A `discrepancy_recorded` event books
one line, graded *blocks return to service* or *due by a named event*, the event named
in text (ruling 179), always on an order (ruling 178); a `discrepancy_cleared` event
clears it with its evidence. The coordinator's unstamped call records any source but
an inspector's rejection, which waits on O6 (rulings 114 and 172), and may cite a tag
issued on the order (ruling 171); a live `Implementer`, `SingleDriver` or
`Restoration` dispatch's stamped call records a find in the work on its own order,
read from its dispatch record (rulings 1, 130, 172 and 175). The coordinator alone
clears a line, citing an entry or a cleared tag of its package, or an open GitHub
issue the line was filed as (rulings 172 and 180), with root cause and corrective
action on a blocking or recurring line (ruling 181). Each id is `DSC-<NN>-<slug>` in
one series that never reissues a number (rulings 169 and 176).

The writers take the ledger, the catalog, the stamped dispatch id, the open MX
session's id and the clear's witnesses as parameters; `gh` and the insight store sit
behind the `ClearWitnesses` port (`.gzkit/rules/hexagonal-architecture.md` rule 4). A
refusal writes nothing, and every check the ledger can answer runs before `gh` is asked.
"""

import re
from typing import TYPE_CHECKING, NoReturn, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import (
    SLUG_PATTERN,
    DiscrepancyClearedEvent,
    DiscrepancyGrade,
    DiscrepancyRecordedEvent,
    DiscrepancySource,
)
from gzkit.insights.recurrence import check_recurrence
from gzkit.ledger import ledger_row
from gzkit.mx.entries import PERFORMERS, maintenance_record, malformed_row_message
from gzkit.mx.series import next_series_id
from gzkit.mx.tag_out import tag_log
from gzkit.order_ledger import TERMINATED, order_state
from gzkit.work_package_ledger import work_package_state
from gzkit.work_package_run import dispatch_over, find_dispatch

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from gzkit.ledger import Ledger, LedgerEvent
    from gzkit.models.catalog import Catalog

#: The grade that holds return to service (ruling 9).
BLOCKS: DiscrepancyGrade = "blocks-return-to-service"
#: The grade a line is due by a named event under (rulings 9 and 179).
DUE_BY: DiscrepancyGrade = "due-by-event"
#: The source a performer's stamped call records (ruling 172).
FOUND_IN_WORK: DiscrepancySource = "found-in-work"
#: A discrepancy's slug: lowercase words joined by hyphens, as an entry's (ruling 169).
_SLUG = re.compile(f"^{SLUG_PATTERN}$")


class DiscrepancyError(ValueError):
    """A list-of-discrepancies act the ruled grammar refuses; nothing was written."""


class DiscrepancyUnavailableError(DiscrepancyError):
    """The issue a clear cites could not be read through `gh`; nothing was written."""


class ClearWitnesses(Protocol):
    """What a clear reads outside the ledger: an issue's state and a citation's time."""

    @property
    def min_occurrences(self) -> int:
        """The recurrence threshold (`data/recurrence_threshold.json`)."""
        ...

    @property
    def separation_hours(self) -> float:
        """The hours every pair of cited records must lie apart, one session lease."""
        ...

    def issue_state(self, number: int) -> str | None:
        """Return the issue's state, `open` or `closed`, or None when it cannot be read."""
        ...

    def cite_time(self, cite: str) -> datetime | None:
        """Return an insight record's or a GHI's full timestamp, or None when it names nothing."""
        ...


class DiscrepancyRecord(BaseModel):
    """One requested `discrepancy_recorded` act."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(..., description="The last part of the line's id, DSC-<NN>-<slug>")
    grade: DiscrepancyGrade = Field(..., description="Blocks return to service, or due by")
    source: DiscrepancySource = Field(..., description="Where the line comes from (ruling 9)")
    description: str = Field(..., description="What is wrong")
    due_by: str | None = Field(None, description="The event a due-by line is due by")
    order: str | None = Field(None, description="The order, the coordinator's call alone")
    dispatch: str | None = Field(None, description="The performer's dispatch, a find in the work")
    tag: str | None = Field(None, description="A tag issued on the order, the coordinator's")


class DiscrepancyClear(BaseModel):
    """One requested `discrepancy_cleared` act."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    discrepancy: str = Field(..., description="The line cleared, DSC-<NN>-<slug>")
    entry: str | None = Field(None, description="An entry of the line's package")
    tag: str | None = Field(None, description="A cleared tag of the line's package")
    ghi: int | None = Field(None, description="The open issue the line was filed as")
    root_cause: str | None = Field(None, description="Its root cause (ruling 181)")
    corrective_action: str | None = Field(None, description="Its corrective action")
    recurs: tuple[str, ...] = Field((), description="Citations the recurrence check reads")


class Discrepancy(BaseModel):
    """One line of the list as its view reads it: the record, its clear, whether open."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    record: DiscrepancyRecordedEvent = Field(..., description="The line as recorded")
    clear: DiscrepancyClearedEvent | None = Field(None, description="Its clear, None while open")

    @property
    def is_open(self) -> bool:
        """Whether the line is still on the list: it has no clear."""
        return self.clear is None


def _refuse(message: str) -> NoReturn:
    raise DiscrepancyError(message)


def _parsed[T: BaseModel](ledger: Ledger, event_type: str, model: type[T]) -> list[T]:
    rows: list[T] = []
    for row in ledger.query(event_type=event_type):
        try:
            rows.append(model.model_validate(row.model_dump()))
        except ValidationError as exc:
            _refuse(_malformed(row, exc))
    return rows


def _malformed(row: LedgerEvent, exc: ValidationError) -> str:
    return malformed_row_message(row, exc, "the list of discrepancies cannot be read", ruling=9)


def discrepancy_list(ledger: Ledger) -> list[Discrepancy]:
    """Read every line the ledger records, oldest first, each with its clear (ruling 9).

    A void correction drops a row from the live stream, so a malformed row is
    recovered by voiding it, never by editing the ledger. A line's first clear is its
    clear; the writer refuses a second.

    Returns:
        Each line the live ledger holds.

    """
    clears: dict[str, DiscrepancyClearedEvent] = {}
    for clear in _parsed(ledger, "discrepancy_cleared", DiscrepancyClearedEvent):
        clears.setdefault(clear.discrepancy_id, clear)
    return [
        Discrepancy(record=record, clear=clears.get(record.discrepancy_id))
        for record in _parsed(ledger, "discrepancy_recorded", DiscrepancyRecordedEvent)
    ]


def open_discrepancies(ledger: Ledger) -> list[Discrepancy]:
    """Read the lines still open, the list's default view.

    Returns:
        The lines with no clear, oldest first.

    """
    return [line for line in discrepancy_list(ledger) if line.is_open]


def next_discrepancy_id(ledger: Ledger, slug: str) -> str:
    """Return the next id in the one series (ruling 169), past every number (ruling 176).

    Returns:
        `DSC-<NN>-<slug>`, numbered past every line the ledger's history names.

    """
    return next_series_id(ledger, "discrepancy_recorded", "DSC", slug)


def _check_session(mx_session_id: str | None, act: str) -> None:
    if not (mx_session_id or "").strip():
        _refuse(
            f"No MX session is open, and a discrepancy's {act} records the MX session it was "
            "made under (RP-12 rulings 9 and 114). Have the operator open one through the "
            f"gz-mx skill (`uv run gz mx enter`), then {act} it again."
        )


def _check_line(request: DiscrepancyRecord) -> None:
    """Refuse a line the grammar refuses before the ledger is read (rulings 9, 169, 172, 179)."""
    if not _SLUG.match(request.slug):
        _refuse(
            f"--slug {request.slug!r} is not lowercase words joined by hyphens. It is the "
            "last part of the line's id, DSC-<NN>-<slug>, the grammar of orders, tags and "
            "entries (RP-12 ruling 169). Record it again with a slug such as `hook-left-off`."
        )
    if not request.description.strip():
        _refuse(
            "--description is blank. A discrepancy says what is wrong (RP-12 ruling 9). "
            "Record it again with the description written out."
        )
    due_by = (request.due_by or "").strip()
    if request.grade == DUE_BY and not due_by:
        _refuse(
            "--due-by is required on a line graded due by a named event, and names the event "
            "in text, such as `O9's carry` (RP-12 ruling 179). Record it again with the event."
        )
    if request.grade == BLOCKS and request.due_by is not None:
        _refuse(
            "--due-by names the event a line is due by, and this line blocks return to "
            "service, which waits on no event (RP-12 rulings 9 and 179). Record it again "
            "without --due-by, or grade it --grade due-by-event."
        )
    if request.source == "inspector-rejection":
        _refuse(
            "An inspector's rejection is recorded by the QAI dispatch O6 lands, which is not "
            "built (RP-12 ruling 172). Record the line as `left-broken` from the coordinator's "
            "call if the work left it broken, or wait on O6."
        )


def _refuse_unstamped(dispatch_id: str, stamped_id: str | None) -> NoReturn:
    """Refuse a performer's line whose call is not stamped as the dispatch it names."""
    if stamped_id:
        stamp = f"stamped with {stamped_id}"
        step = (
            f"If {stamped_id} found it, name it: `uv run gz wp discrepancy record --dispatch "
            f"{stamped_id} ...`; otherwise the line belongs to {dispatch_id}'s own subagent."
        )
    else:
        stamp = "not stamped with a dispatch id"
        step = (
            f"A find in the work is recorded from {dispatch_id}'s own subagent, its prompt "
            "carrying the dispatch line; the coordinator records its own line with --order "
            "and no --dispatch."
        )
    _refuse(
        f"This call is {stamp}, and a performer's line is the stamped call of the dispatch "
        f"that found it, {dispatch_id} (RP-12 rulings 172 and 175). {step}"
    )


def _performer_order(ledger: Ledger, request: DiscrepancyRecord, stamped_id: str) -> str:
    """Read a performer's order from its dispatch, refusing what it may not record.

    Returns:
        The order the live performing dispatch is bound to.

    """
    if request.dispatch != stamped_id:
        _refuse_unstamped(request.dispatch or stamped_id, stamped_id)
    if request.source != FOUND_IN_WORK:
        _refuse(
            f"A stamped call records a find in the work alone, and this line's source is "
            f"{request.source} (RP-12 ruling 172). The coordinator's unstamped call records "
            "any other source; report it in the handback."
        )
    if request.order is not None:
        _refuse(
            "--order is read from the performer's dispatch record, never typed (RP-12 rulings "
            "1, 130 and 178). Record the line again without --order."
        )
    if request.tag is not None:
        _refuse(
            "--tag is the coordinator's: a line carrying a hung tag is recorded by its "
            "unstamped call (RP-12 ruling 171). Record the find without --tag and report the "
            "tag in the handback."
        )
    dispatch = find_dispatch(ledger, stamped_id)
    over = dispatch_over(ledger, stamped_id)
    if dispatch is None or over is not None:
        _refuse(
            f"Dispatch {stamped_id} is not a live dispatch in the ledger "
            f"({over or 'not booked'}), so the ledger says it may do nothing (RP-12 rulings "
            "1, 42, 115 and 160). A find in the work is recorded by the live dispatch that "
            "found it."
        )
    if dispatch.role not in PERFORMERS or dispatch.order is None:
        _refuse(
            f"Dispatch {stamped_id} is a {dispatch.role} dispatch"
            f"{'' if dispatch.order else ' on no order'}; a find in the work is recorded by a "
            "dispatch that performs maintenance on an order, Implementer, SingleDriver or "
            "Restoration (RP-12 rulings 172 and 175)."
        )
    return dispatch.order


def _coordinator_order(request: DiscrepancyRecord) -> str:
    if request.dispatch is not None:
        _refuse_unstamped(request.dispatch, None)
    if request.order is None:
        _refuse(
            "--order is required: every discrepancy is recorded against an order, a line "
            "with no order waiting on O9's carry (RP-12 ruling 178). Record it again with "
            "--order <ORD-id>."
        )
    return request.order


def _check_order(catalog: Catalog, ledger: Ledger, order_id: str) -> str:
    """Refuse an order not held, of a package not initiated, or not opened or closed.

    Returns:
        The order's repair package.

    """
    order = next((held for held in catalog.orders if held.id == order_id), None)
    if order is None:
        _refuse(
            f"Order {order_id!r} is not in data/catalog/orders.json, and a discrepancy is "
            "recorded against an order the store holds (RP-12 rulings 47 and 178). Name an "
            "order `uv run gz wp order show <ORD-id>` finds."
        )
    package_state = work_package_state(ledger, order.work_package)
    if package_state != "initiated":
        _refuse(
            f"Work package {order.work_package} is {package_state or 'not initiated'}; a line "
            "is recorded on an order of a repair package initiated and not closed (RP-12 "
            f"rulings 2, 44 and 178). `uv run gz wp show {order.work_package}` shows its state."
        )
    order_now = order_state(ledger, order_id)
    if order_now is None or order_now in TERMINATED:
        _refuse(
            f"Order {order_id} is {order_now or 'not opened'}; a line is recorded on an "
            "order in any state but closed, and an order never opened has none (RP-12 ruling "
            f"178). `uv run gz wp order show {order_id}` reads its state."
        )
    return order.work_package


def _check_tag(ledger: Ledger, tag_id: str, order_id: str) -> None:
    tag = next((tag for tag in tag_log(ledger) if tag.issue.tag_id == tag_id), None)
    if tag is None:
        _refuse(
            f"Tag {tag_id!r} is not issued in the ledger, and a line cites a tag issued on "
            "its own order (RP-12 ruling 171). Read the log with `uv run gz wp tag show --all`."
        )
    if tag.issue.order != order_id:
        _refuse(
            f"Tag {tag_id} is issued on {tag.issue.order}, and this line is on {order_id}; a "
            "line cites a tag of its own order, the carry reading the tag and the order "
            "together (RP-12 ruling 171). Record the line on the tag's order."
        )


def record_discrepancy(
    catalog: Catalog,
    ledger: Ledger,
    request: DiscrepancyRecord,
    *,
    stamped_id: str | None,
    mx_session_id: str | None,
) -> DiscrepancyRecordedEvent:
    """Record one line of the list of discrepancies, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    _check_session(mx_session_id, "record")
    _check_line(request)
    if stamped_id:
        order_id = _performer_order(ledger, request, stamped_id)
    else:
        order_id = _coordinator_order(request)
    work_package = _check_order(catalog, ledger, order_id)
    if request.tag is not None:
        _check_tag(ledger, request.tag, order_id)
    discrepancy_id = next_discrepancy_id(ledger, request.slug)
    event = DiscrepancyRecordedEvent.model_validate(
        {
            "event": "discrepancy_recorded",
            "id": discrepancy_id,
            "discrepancy_id": discrepancy_id,
            "order": order_id,
            "work_package": work_package,
            "grade": request.grade,
            "due_by": request.due_by,
            "source": request.source,
            "description": request.description,
            "tag_id": request.tag,
            "dispatch_id": stamped_id or None,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event


def _open_line(ledger: Ledger, discrepancy_id: str) -> DiscrepancyRecordedEvent:
    line = next(
        (line for line in discrepancy_list(ledger) if line.record.discrepancy_id == discrepancy_id),
        None,
    )
    if line is None:
        _refuse(
            f"Discrepancy {discrepancy_id!r} is not recorded in the ledger, so there is nothing "
            "to clear (RP-12 ruling 9). Read the list with `uv run gz wp discrepancy show`."
        )
    if line.clear is not None:
        _refuse(
            f"Discrepancy {discrepancy_id} is already cleared, by MX session "
            f"{line.clear.mx_session_id}; a line is cleared once (RP-12 ruling 9)."
        )
    return line.record


def _check_evidence(ledger: Ledger, request: DiscrepancyClear, package: str) -> None:
    """Refuse a clear whose ledger evidence does not resolve in the line's package (ruling 172)."""
    if request.entry is None and request.tag is None and request.ghi is None:
        _refuse(
            f"The clear of {request.discrepancy} cites no evidence; a line is cleared with "
            "evidence the ledger resolves, an entry (--entry), a cleared tag (--tag) or the "
            "open issue it was filed as (--ghi) (RP-12 rulings 9, 172 and 180)."
        )
    if request.entry is not None:
        entry = next((e for e in maintenance_record(ledger) if e.entry_id == request.entry), None)
        if entry is None:
            _refuse(
                f"Entry {request.entry!r} is not in the maintenance record, so it cannot clear "
                "the line (RP-12 ruling 172). Read the record with `uv run gz wp entry show`."
            )
        if entry.work_package != package:
            _refuse(
                f"{request.entry} is an entry of {entry.work_package}, and the line is "
                f"{package}'s; a line is cleared by work in its own package, and one that "
                "leaves it is filed as an issue (RP-12 rulings 9 and 180)."
            )
    if request.tag is not None:
        tag = next((t for t in tag_log(ledger) if t.issue.tag_id == request.tag), None)
        if tag is None or tag.issue.work_package != package:
            _refuse(
                f"Tag {request.tag!r} is not issued in {package} in the ledger, so it cannot "
                "clear the line (RP-12 ruling 172). Read the log with "
                "`uv run gz wp tag show --all`."
            )
        if tag.clear is None:
            _refuse(
                f"Tag {request.tag} is not cleared; a tag clears a line once its Restoration "
                "dispatch has cleared it (RP-12 rulings 6 and 172)."
            )


def _check_cause(
    request: DiscrepancyClear, grade: DiscrepancyGrade, witnesses: ClearWitnesses
) -> None:
    """Refuse a clear whose root cause and corrective action ruling 181 requires and lacks."""
    for flag, given in (
        ("--root-cause", request.root_cause),
        ("--corrective-action", request.corrective_action),
    ):
        if given is not None and not given.strip():
            _refuse(f"{flag} is blank. A field given is written out (RP-12 ruling 181).")
    required = grade == BLOCKS
    if request.recurs:
        if grade != DUE_BY:
            _refuse(
                "--recurs is read on a line graded due by a named event; a line that blocks "
                "return to service carries its root cause and corrective action whether it "
                "recurs or not (RP-12 ruling 181). Clear it again without --recurs."
            )
        required = _recurs(request.recurs, witnesses)
    if required and not (request.root_cause and request.corrective_action):
        why = "blocks return to service" if grade == BLOCKS else "recurs"
        _refuse(
            f"--root-cause and --corrective-action are required: the line {why}, and such a "
            "line carries the fuller record (RP-12 rulings 9 and 181; JFMM I-9.3.1.a). Clear "
            "it again with both written out."
        )


def _recurs(cites: Sequence[str], witnesses: ClearWitnesses) -> bool:
    """Read the recurrence threshold over *cites*, refusing a shortfall (ruling 181).

    Returns:
        True: the threshold is met, so the line recurs.

    """
    resolved: dict[str, datetime] = {}
    for cite in cites:
        stamp = witnesses.cite_time(cite)
        if stamp is None:
            _refuse(
                f"--recurs {cite} names no insight record or resolvable GHI, so the "
                "recurrence check cannot read it (RP-12 ruling 181; `gz insights recurrence`)."
            )
        resolved[cite] = stamp
    verdict = check_recurrence(
        resolved,
        min_occurrences=witnesses.min_occurrences,
        separation_hours=witnesses.separation_hours,
    )
    if not verdict.met:
        close = (
            f"; {len(verdict.too_close)} pair(s) closer than {verdict.separation_hours:g}h"
            if verdict.too_close
            else ""
        )
        _refuse(
            f"--recurs does not meet the recurrence threshold: {verdict.cited} cited of "
            f"{verdict.required} required{close} (RP-12 ruling 181; "
            "data/recurrence_threshold.json). "
            "Clear it again without --recurs, or cite records of the same failure a lease apart."
        )
    return True


def _check_issue(number: int, witnesses: ClearWitnesses) -> None:
    state = witnesses.issue_state(number)
    if state is None:
        msg = (
            f"Issue #{number} could not be read through `gh`, so the clear cannot confirm the "
            "line was filed as it (RP-12 ruling 180). Check `gh auth status` and the network, "
            "then clear it again; nothing was written."
        )
        raise DiscrepancyUnavailableError(msg)
    if state != "open":
        _refuse(
            f"Issue #{number} is {state}; a line filed as an issue leaves the list as an open "
            "problem report (RP-12 rulings 9 and 180). Cite the open issue it was filed as, "
            "or the entry that fixed it."
        )


def record_discrepancy_clear(
    ledger: Ledger,
    request: DiscrepancyClear,
    *,
    stamped_id: str | None,
    mx_session_id: str | None,
    witnesses: ClearWitnesses,
) -> DiscrepancyClearedEvent:
    """Clear one line on its evidence, or refuse it and write nothing.

    Every check the ledger answers runs first; `gh` is asked last, and only for a
    clear that cites an issue (ruling 180).

    Returns:
        The event booked.

    """
    if stamped_id:
        _refuse(
            f"This call is stamped with {stamped_id}, and a discrepancy is cleared by the "
            "coordinator's unstamped call alone (RP-12 rulings 114 and 172). Report the "
            "evidence in the handback; the coordinator clears the line."
        )
    _check_session(mx_session_id, "clear")
    line = _open_line(ledger, request.discrepancy)
    _check_evidence(ledger, request, line.work_package)
    _check_cause(request, line.grade, witnesses)
    if request.ghi is not None:
        _check_issue(request.ghi, witnesses)
    event = DiscrepancyClearedEvent.model_validate(
        {
            "event": "discrepancy_cleared",
            "id": line.discrepancy_id,
            "discrepancy_id": line.discrepancy_id,
            "order": line.order,
            "work_package": line.work_package,
            "entry_id": request.entry,
            "tag_id": request.tag,
            "ghi": request.ghi,
            "root_cause": request.root_cause,
            "corrective_action": request.corrective_action,
            "recurs": list(request.recurs),
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event
