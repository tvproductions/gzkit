"""The order's Layer-2 writer (RP-12 O2 task 3).

`docs/governance/harbor-ro12-contractor-kit.md`: an order's lifecycle lives only
in the ledger (ruling 44), as `order_transitioned`. `gz wp order new` books
`opened` on the operator's words (ruling 52), and the order then moves `frozen`,
`commenced` and `accepted`, one step at a time; `closed` is Gate 5 at the order
and lands with O2 task 4, so it is refused here. A freeze carries the risk note,
the reviewer's receipt and a baseline of the repair REQs held on the order's
package (rulings 2, 45), each REQ in one live order's frozen baseline at a time
(ruling 53).

The writer takes the parsed catalog and the ledger as parameters, reads the
current state from the ledger rather than the caller, and refuses a move the
ruled grammar does not allow, writing nothing.
"""

from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import BaselinedReq, OrderTransitionedEvent
from gzkit.ledger import ledger_row
from gzkit.models.catalog import RepairReq
from gzkit.work_package_ledger import work_package_state

if TYPE_CHECKING:
    from gzkit.ledger import Ledger
    from gzkit.models.catalog import Catalog, CatalogReq, Order

#: Each state's next state. A table rather than an order of states, so task 4's
#: close and its re-freeze add edges without reshaping the lifecycle (question 11).
_NEXT: dict[str | None, str | None] = {
    None: "opened",
    "opened": "frozen",
    "frozen": "commenced",
    "commenced": "accepted",
    "accepted": None,
}
#: The states that end an order's hold on its baseline (ruling 53). O5 adds stopped.
TERMINATED: frozenset[str] = frozenset({"accepted", "closed"})
#: The payload fields each target state carries; any other is refused.
_STATE_FIELDS: dict[str, frozenset[str]] = {
    "opened": frozenset({"operator_text"}),
    "frozen": frozenset({"baseline", "risk_note", "review_receipt"}),
    "commenced": frozenset(),
    "accepted": frozenset(),
}
_MOVE_FIELDS = frozenset({"order", "to_state", "evidence"})


class OrderLedgerError(ValueError):
    """An order move the ruled grammar refuses; nothing was written."""


class OrderMove(BaseModel):
    """One requested `order_transitioned` move and its state-specific fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    order: str = Field(..., description="The order's id")
    to_state: str = Field(..., description="The state to move to")
    evidence: str = Field(..., description="What justifies the move")
    operator_text: str | None = Field(None, description="The operator's words, at opened")
    baseline: tuple[BaselinedReq, ...] = Field((), description="The frozen REQ baseline")
    risk_note: str | None = Field(None, description="The short risk note, at frozen")
    review_receipt: str | None = Field(None, description="The nine-criteria review receipt")


def _refuse(message: str) -> NoReturn:
    raise OrderLedgerError(message)


def _moves(ledger: Ledger, order: str | None = None) -> list[dict[str, object]]:
    return [
        row.extra
        for row in ledger.query(event_type="order_transitioned")
        if order is None or row.extra.get("order") == order
    ]


def order_state(ledger: Ledger, order: str) -> str | None:
    """Read the order's lifecycle state from the ledger.

    Returns:
        The state its last `order_transitioned` moved it to, or None before it is opened.

    """
    moves = _moves(ledger, order)
    return str(moves[-1]["to_state"]) if moves else None


def booked_order_ids(ledger: Ledger) -> set[str]:
    """Read every order the ledger names, so none is dropped from the store or reused.

    Returns:
        The order ids.

    """
    return {str(move["order"]) for move in _moves(ledger)}


def order_baseline(ledger: Ledger, order: str) -> dict[str, int]:
    """Read the order's frozen baseline, REQ to revision.

    Returns:
        The baseline its last `frozen` move recorded, empty before a freeze.

    """
    frozen = [move for move in _moves(ledger, order) if move.get("to_state") == "frozen"]
    entries = frozen[-1].get("baseline") if frozen else None
    if not isinstance(entries, list):
        return {}
    return {str(entry["req"]): int(entry["revision"]) for entry in entries}


def _order(catalog: Catalog, order_id: str) -> Order:
    held = next((order for order in catalog.orders if order.id == order_id), None)
    if held is None:
        _refuse(f"Order {order_id!r} is not in data/catalog/orders.json.")
    return held


def _live_holders(ledger: Ledger, order: Order) -> dict[str, str]:
    """Map each REQ another live order's frozen baseline holds to that order (ruling 53).

    Returns:
        REQ id to the order holding it.

    """
    others = booked_order_ids(ledger) - {order.id}
    return {
        req: other
        for other in sorted(others)
        if order_state(ledger, other) not in TERMINATED
        for req in order_baseline(ledger, other)
    }


def _check_entry(
    held: dict[str, CatalogReq | RepairReq],
    holders: dict[str, str],
    order: Order,
    entry: BaselinedReq,
) -> None:
    """One baseline entry: the package's own repair REQ, outside every other live baseline."""
    req = held.get(entry.req)
    if req is None or req.revision != entry.revision:
        _refuse(f"{entry.req} at revision {entry.revision} is not a REQ the catalog holds.")
    if not isinstance(req, RepairReq) or req.held_on != order.work_package:
        where = f"held on {req.held_on}" if isinstance(req, RepairReq) else "a catalog REQ"
        _refuse(
            f"{entry.req} is {where}; order {order.id} freezes only the repair REQs held "
            f"on its package {order.work_package} (RP-12 rulings 2 and 45)."
        )
    if holder := holders.get(entry.req):
        _refuse(
            f"{entry.req} is in the frozen baseline of live order {holder}; a repair REQ "
            "sits in one live order's baseline at a time, until that order is accepted, "
            "stopped or closed (RP-12 ruling 53). Freeze without it, or split it with a "
            "REQ that supersedes it."
        )


def _check_frozen(catalog: Catalog, ledger: Ledger, order: Order, move: OrderMove) -> None:
    """Freeze: the note, the receipt, and a baseline of the package's own repair REQs."""
    if not (move.risk_note or "").strip() or not (move.review_receipt or "").strip():
        _refuse("A freeze carries the risk note and the reviewer's nine-criteria receipt.")
    held = {req.id: req for req in catalog.reqs}
    holders = _live_holders(ledger, order)
    for entry in move.baseline:
        _check_entry(held, holders, order, entry)


def _check_move(catalog: Catalog, ledger: Ledger, order: Order, move: OrderMove) -> None:
    if move.to_state == "closed":
        _refuse(
            f"Order {order.id} closes only through Gate 5 at the order, which lands with RP-12 "
            "O2 task 4; nothing moves an order to closed before it."
        )
    stray = sorted(move.model_fields_set - _MOVE_FIELDS - _STATE_FIELDS[move.to_state])
    if stray:
        _refuse(f"A move to {move.to_state} does not carry {', '.join(stray)}.")
    if move.to_state == "opened" and not (move.operator_text or "").strip():
        _refuse(f"Order {order.id} is opened on the operator's words; none were given.")
    package_state = work_package_state(ledger, order.work_package)
    if package_state != "initiated":
        _refuse(
            f"Work package {order.work_package} is {package_state or 'not initiated'}; an order "
            "moves only while its repair package is initiated and not closed, since the "
            "package's close reads every order's Gate 5 (RP-12 rulings 2 and 44)."
        )
    if move.to_state == "frozen":
        _check_frozen(catalog, ledger, order, move)


def record_order_transition(
    catalog: Catalog, ledger: Ledger, move: OrderMove
) -> OrderTransitionedEvent:
    """Book one lifecycle move for an order, or refuse it and write nothing.

    Returns:
        The event booked.

    """
    order = _order(catalog, move.order)
    if not move.evidence.strip():
        _refuse("A transition names what justifies it; evidence is empty.")
    current = order_state(ledger, order.id)
    expected = _NEXT.get(current)
    if move.to_state not in {"closed", expected}:
        _refuse(
            f"Order {order.id} cannot move from {current or 'nothing'} to {move.to_state!r}; "
            f"the lifecycle allows {expected or 'no move'} from here."
        )
    _check_move(catalog, ledger, order, move)
    event = OrderTransitionedEvent.model_validate(
        {
            **move.model_dump(exclude_unset=True),
            "event": "order_transitioned",
            "id": order.id,
            "work_package": order.work_package,
            "from_state": current,
            "evidence": move.evidence.strip(),
        }
    )
    ledger.append(ledger_row(event))
    return event
