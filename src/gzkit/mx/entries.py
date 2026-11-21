"""The maintenance record's writer and reducer (RP-12 O4 task 1).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the maintenance record
is ledger events, rendered as a view (ruling 8), one `entry_booked` event per act,
each element of 14 CFR § 43.9(a) a field. The performer books its own entry (ruling
167): the stamped call of a live `Implementer`, `SingleDriver` or `Restoration`
dispatch it names (ruling 133's form; rulings 160 and 175), on that dispatch's
order, read from the dispatch record and never typed (rulings 1 and 130), the order
commenced, where its performers are dispatched (rulings 57 and 132; refusal 2), and
not blocked (ruling 59). The entry
carries what was done and the measurement before and after with the witness that
measured it, none blank (ruling 173), and the open MX session (ruling 8). Its id is
`ENT-<NN>-<slug>` (ruling 169); the commit that lands the work names it in its
subject (ruling 170), so the event cites no commit.

The writer sits beside the tag-out log and the MX log that renders the record at
exit (rulings 166 and 174). It takes the ledger, the stamped dispatch id and the
open MX session's id as parameters and reads neither the stamp nor the marker
itself (`.gzkit/rules/hexagonal-architecture.md` rule 4). A refusal writes nothing.
"""

import re
from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import SLUG_PATTERN, EntryBookedEvent, OrderTransitionedEvent
from gzkit.ledger import ledger_row
from gzkit.mx.record_rows import malformed_row_message
from gzkit.mx.series import next_series_id
from gzkit.order_ledger import is_order_blocked, order_state
from gzkit.work_package_run import (
    IMPLEMENTER,
    RESTORATION,
    SINGLE_DRIVER,
    dispatch_over,
    find_dispatch,
)

if TYPE_CHECKING:
    from gzkit.ledger import Ledger, LedgerEvent
    from gzkit.work_package_run import DispatchRecord

#: The roles that perform maintenance on an order, so book its entries (ruling 175).
PERFORMERS: tuple[str, ...] = (IMPLEMENTER, SINGLE_DRIVER, RESTORATION)
#: The fields an entry requires written out, none blank (rulings 8 and 173).
_REQUIRED_TEXT: tuple[str, ...] = ("description", "before", "after", "witness")
#: An entry's slug: lowercase words joined by hyphens, as an order's or a tag's (ruling 169).
_SLUG = re.compile(f"^{SLUG_PATTERN}$")


class EntryError(ValueError):
    """A maintenance-record act the ruled grammar refuses; nothing was written."""


class EntryBook(BaseModel):
    """One requested `entry_booked` act, as the performer writes it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(..., description="The last part of the entry's id, ENT-<NN>-<slug>")
    dispatch: str = Field(..., description="The performer's dispatch, D-<id>")
    description: str = Field(..., description="What was done (14 CFR 43.9(a)(1))")
    before: str = Field(..., description="The measurement before (ruling 173)")
    after: str = Field(..., description="The measurement after (ruling 173)")
    witness: str = Field(..., description="The command or receipt that measured them")


def _refuse(message: str) -> NoReturn:
    raise EntryError(message)


def _refuse_malformed(row: LedgerEvent, exc: ValidationError, reading: str) -> NoReturn:
    """Refuse a row its event's shape does not admit, naming the void that recovers it."""
    _refuse(malformed_row_message(row, exc, reading))


def maintenance_record(ledger: Ledger) -> list[EntryBookedEvent]:
    """Read every entry the ledger books, oldest first: the maintenance record (ruling 8).

    A void correction drops a row from the live stream (`gzkit.ledger_corrections`),
    so a malformed row is recovered by voiding it, never by editing the ledger.

    Returns:
        Each entry the live ledger holds.

    """
    entries: list[EntryBookedEvent] = []
    for row in ledger.query(event_type="entry_booked"):
        try:
            entries.append(EntryBookedEvent.model_validate(row.model_dump()))
        except ValidationError as exc:
            _refuse_malformed(row, exc, "the maintenance record cannot be read")
    return entries


class RecordedEntry(BaseModel):
    """One entry of the maintenance record as its view reads it, with its order's Gate 5."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entry: EntryBookedEvent = Field(..., description="The entry the performer booked")
    gate5: OrderTransitionedEvent | None = Field(
        None, description="The entry's order closing at Gate 5, the signature (ruling 8)"
    )


def record_view(ledger: Ledger) -> list[RecordedEntry]:
    """Read the maintenance record with each entry's signature: its order's Gate 5 (ruling 8).

    Ruling 8 makes the order's Gate 5 event the signature that closes the record of
    the work done on it, 14 CFR § 43.9(a)'s fourth element beside the description,
    the date and the performer. The view joins it from the ledger; the entry carries
    none, since the entry is booked before the order closes.

    Returns:
        Each entry, oldest first, with its order's `order_transitioned` to `closed`,
        or None while the order is not closed.

    """
    closes: dict[str, OrderTransitionedEvent] = {}
    for row in ledger.query(event_type="order_transitioned"):
        if row.extra.get("to_state") != "closed":
            continue
        try:
            closed = OrderTransitionedEvent.model_validate(row.model_dump())
        except ValidationError as exc:
            _refuse_malformed(row, exc, "no entry's Gate 5 can be read")
        closes[closed.order] = closed
    return [
        RecordedEntry(entry=entry, gate5=closes.get(entry.order))
        for entry in maintenance_record(ledger)
    ]


def next_entry_id(ledger: Ledger, slug: str) -> str:
    """Return the next id in the one series (ruling 169): the highest number plus one.

    The series is read from the ledger's history, a voided entry's number included,
    so a number never returns (ruling 176).

    Returns:
        `ENT-<NN>-<slug>`, numbered past every entry the ledger's history names.

    """
    return next_series_id(ledger, "entry_booked", "ENT", slug)


def _refuse_unstamped(dispatch_id: str, stamped_id: str | None) -> NoReturn:
    """Refuse an entry whose call is not stamped as the dispatch it names (ruling 167).

    The next step is one that can succeed: naming the dispatch the call is stamped
    with, or booking from the named dispatch's own subagent, never the same call.
    """
    if stamped_id:
        stamp = f"stamped with {stamped_id}"
        step = (
            f"If {stamped_id} did the work, name it: `uv run gz wp entry book --dispatch "
            f"{stamped_id} ...`; otherwise the entry belongs to {dispatch_id}'s own subagent."
        )
    else:
        stamp = "not stamped with a dispatch id"
        step = (
            f"The entry is booked from {dispatch_id}'s own subagent, its prompt carrying the "
            "dispatch line; the coordinator relays nothing (14 CFR 43.9(a))."
        )
    _refuse(
        f"This call is {stamp}, and a maintenance-record entry is the stamped call of the "
        f"dispatch that did the work, {dispatch_id} (RP-12 ruling 167). {step}"
    )


def _check_request(request: EntryBook, stamped_id: str | None, mx_session_id: str | None) -> None:
    """Refuse a request the grammar refuses before the ledger is read (rulings 8, 167, 169, 173)."""
    if not (mx_session_id or "").strip():
        _refuse(
            "No MX session is open, and an entry records the MX session its work was done "
            "under (RP-12 ruling 8). Have the operator open one through the gz-mx skill "
            "(`uv run gz mx enter`), then book the entry."
        )
    if stamped_id != request.dispatch:
        _refuse_unstamped(request.dispatch, stamped_id)
    if not _SLUG.match(request.slug):
        _refuse(
            f"--slug {request.slug!r} is not lowercase words joined by hyphens. It is the "
            "last part of the entry's id, ENT-<NN>-<slug>, the grammar of orders and tags "
            "(RP-12 ruling 169). Book it again with a slug such as `stamp-import`."
        )
    if blank := [field for field in _REQUIRED_TEXT if not getattr(request, field).strip()]:
        flags = " and ".join(f"--{field}" for field in blank)
        _refuse(
            f"{flags} is blank. An entry says what was done and the measurement before and "
            "after, with the command or receipt that measured them (RP-12 rulings 8 and 173; "
            "14 CFR 43.9(a)). Book it again with each written out."
        )


def _performer(ledger: Ledger, dispatch_id: str) -> tuple[DispatchRecord, str]:
    """Read the performing dispatch and its order, refusing one that may not book an entry.

    Returns:
        The live dispatch's record and the commenced, unblocked order it is bound to.

    """
    dispatch = find_dispatch(ledger, dispatch_id)
    over = dispatch_over(ledger, dispatch_id)
    if dispatch is None or over is not None:
        _refuse(
            f"Dispatch {dispatch_id} is not a live dispatch in the ledger "
            f"({over or 'not booked'}), so the ledger says it may do nothing (RP-12 rulings "
            "1, 42, 115 and 160). The entry is booked by the live dispatch that did the work."
        )
    order = dispatch.order
    if dispatch.role not in PERFORMERS or order is None:
        _refuse(
            f"Dispatch {dispatch_id} is a {dispatch.role} dispatch"
            f"{'' if order else ' on no order'}; an entry is booked by a dispatch that performs "
            "maintenance on an order, Implementer, SingleDriver or Restoration (RP-12 ruling "
            "175). Book it from the dispatch that did the work."
        )
    order_now = order_state(ledger, order)
    if order_now != "commenced":
        _refuse(
            f"Order {order} is {order_now or 'not opened'}; maintenance is done on a commenced "
            "order, where its performers are dispatched, and no work lands before commencement "
            f"(refusal 2; RP-12 rulings 57 and 132). `uv run gz wp order show {order}` reads "
            "its state."
        )
    if is_order_blocked(ledger, order):
        _refuse(
            f"Order {order} is blocked on the operator, and a blocked order's acts are held, "
            "its entries among them (RP-12 rulings 59 and 137). Book the entry once `uv run gz "
            f"wp unblock {dispatch.work_package} --order {order} --ruling <words> --operator "
            "<who>` records the ruling."
        )
    return dispatch, order


def record_entry_book(
    ledger: Ledger,
    request: EntryBook,
    *,
    stamped_id: str | None,
    mx_session_id: str | None,
) -> EntryBookedEvent:
    """Book the performer's entry for one act, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    _check_request(request, stamped_id, mx_session_id)
    dispatch, order = _performer(ledger, request.dispatch)
    entry_id = next_entry_id(ledger, request.slug)
    event = EntryBookedEvent.model_validate(
        {
            "event": "entry_booked",
            "id": entry_id,
            "entry_id": entry_id,
            "order": order,
            "work_package": dispatch.work_package,
            "dispatch_id": request.dispatch,
            "description": request.description,
            "before": request.before,
            "after": request.after,
            "witness": request.witness,
            "mx_session_id": mx_session_id,
        }
    )
    ledger.append(ledger_row(event))
    return event
