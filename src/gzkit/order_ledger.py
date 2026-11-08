"""The order's Layer-2 writer (RP-12 O2 task 3).

`docs/governance/harbor-ro12-contractor-kit.md`: an order's lifecycle lives only
in the ledger (ruling 44), as `order_transitioned`. `gz wp order new` books
`opened` on the operator's words (ruling 52), and the order then moves `frozen`,
`commenced` and `accepted`, one step at a time, and `closed` through Gate 5 at
the order: from `accepted`, or from `opened` as a terminate alone (ruling 74), with
the decision, the attestor, the operator's verbatim words and the field the
decision names, the others refused (ruling 73); a redirect names an order of the
same package already opened and not frozen (ruling 75). A freeze carries the risk note,
the reviewer's receipt and a baseline of the repair REQs held on the order's
package (rulings 2, 45), each REQ in one live order's frozen baseline at a time
(ruling 53), and never on an empty baseline (ruling 61). A freeze approves exactly
the package's planned alterations no earlier order's freeze approved (ruling 63),
since a repair package never freezes itself (ruling 44). A blocked order does not
move (ruling 59).

The writer takes the parsed catalog and the ledger as parameters, reads the
current state from the ledger rather than the caller, and refuses a move the
ruled grammar does not allow, writing nothing.
"""

from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field

from gzkit.events import BaselinedReq, OrderTransitionedEvent, WorkPackageDecision
from gzkit.ledger import ledger_row
from gzkit.models.catalog import RepairReq
from gzkit.work_package_ledger import (
    declared_modules,
    footprint_sealed,
    package_held_reqs,
    work_package_state,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from gzkit.ledger import Ledger, LedgerEvent
    from gzkit.models.catalog import Catalog, CatalogReq, Order, WorkPackage

#: Each state's next state. A table rather than an order of states, so an edge is
#: added without reshaping the lifecycle (question 11): `closed` is Gate 5 (ruling 74).
_NEXT: dict[str | None, str | None] = {
    None: "opened",
    "opened": "frozen",
    "frozen": "commenced",
    "commenced": "accepted",
    "accepted": "closed",
    "closed": None,
}
#: The states that end an order's hold on its baseline (ruling 53); a stopping exit
#: ends it too, though the order keeps its state (`order_took_stopping_exit`).
TERMINATED: frozenset[str] = frozenset({"accepted", "closed"})
#: The exits that stop a run: an order's or, for a delivery package, the package's.
STOPPING_EXITS: frozenset[str] = frozenset({"reopen", "terminate"})
#: The payload fields each target state carries; any other is refused.
_STATE_FIELDS: dict[str, frozenset[str]] = {
    "opened": frozenset({"operator_text"}),
    "frozen": frozenset({"baseline", "risk_note", "review_receipt", "approved_alterations"}),
    "commenced": frozenset(),
    "accepted": frozenset(),
    "closed": frozenset(
        {
            "decision",
            "attestor",
            "attestation_text",
            "residual_risk",
            "superseded_by",
            "revisit_condition",
        }
    ),
}
#: The field each Gate 5 decision carries (ruling 73); a decision refuses the others'.
_DECISION_FIELD: dict[str, str | None] = {
    "proceed": "residual_risk",
    "redirect": "superseded_by",
    "pause": "revisit_condition",
    "terminate": None,
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
    approved_alterations: tuple[str, ...] = Field((), description="Alterations approved")
    decision: WorkPackageDecision | None = Field(None, description="The Gate 5 decision")
    attestor: str | None = Field(None, description="The Gate 5 attestor, at closed")
    attestation_text: str | None = Field(None, description="The operator's Gate 5 words")
    residual_risk: str | None = Field(None, description="The residual risk, at a proceed")
    superseded_by: str | None = Field(None, description="The order a redirect names")
    revisit_condition: str | None = Field(None, description="When a pause is revisited")


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


def order_rows(ledger: Ledger, event_type: str, order: str) -> list[LedgerEvent]:
    """Read one order's rows of one run event type: its dispatches, blocks and unblocks.

    Returns:
        The rows naming the order, oldest first.

    """
    return [row for row in ledger.query(event_type=event_type) if row.extra.get("order") == order]


def is_order_blocked(ledger: Ledger, order: str) -> bool:
    """Read whether the order's latest block or unblock is a block (RP-12 ruling 59).

    Returns:
        True while the order awaits the operator; its package's other orders are not held.

    """
    kinds = {"work_package_blocked", "work_package_unblocked"}
    rows = [
        row.event
        for row in ledger.query()
        if row.event in kinds and row.extra.get("order") == order
    ]
    return bool(rows) and rows[-1] == "work_package_blocked"


def order_took_stopping_exit(ledger: Ledger, order: str) -> bool:
    """Read whether an exit has stopped the order (RP-12 ruling 59).

    Returns:
        True once a `reopen` or `terminate` exit on the order is on the ledger.

    """
    return any(
        row.extra.get("exit_taken") in STOPPING_EXITS
        for row in order_rows(ledger, "work_package_unblocked", order)
    )


def order_holds(ledger: Ledger, order: str) -> dict[str, int]:
    """Read the repair REQs an order holds: its frozen baseline, once closed as proceed.

    Ruling 78: a repair REQ holds at the revision a proceed-closed order froze it.

    Returns:
        Each REQ the order holds to its revision; empty unless it closed as proceed.

    """
    moves = _moves(ledger, order)
    if not moves or moves[-1].get("to_state") != "closed" or moves[-1].get("decision") != "proceed":
        return {}
    return order_baseline(ledger, order)


def booked_order_ids(ledger: Ledger) -> set[str]:
    """Read every order the ledger names, so none is dropped from the store or reused.

    Returns:
        The order ids.

    """
    return {str(move["order"]) for move in _moves(ledger)}


def order_work_package(ledger: Ledger, order: str) -> str | None:
    """Read the package an order sits in, from its own ledger rows.

    Returns:
        The package its first `order_transitioned` names, or None before it is opened.

    """
    moves = _moves(ledger, order)
    return str(moves[0]["work_package"]) if moves else None


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


def _package(catalog: Catalog, order: Order) -> WorkPackage:
    return next(wp for wp in catalog.work_packages if wp.id == order.work_package)


def approved_alterations(ledger: Ledger, work_package: str) -> set[str]:
    """Read the alterations the package's orders' freezes have approved (RP-12 ruling 63).

    Returns:
        Those alteration ids.

    """
    approved: set[str] = set()
    for move in _moves(ledger):
        items = move.get("approved_alterations")
        if move.get("work_package") == work_package and isinstance(items, list):
            approved.update(str(item) for item in items)
    return approved


def _check_alterations(ledger: Ledger, order: Order, package: WorkPackage, move: OrderMove) -> None:
    """Ruling 63: the freeze approves each planned alteration no earlier freeze approved."""
    due = {a.id for a in package.alterations} - approved_alterations(ledger, package.id)
    if set(move.approved_alterations) != due:
        _refuse(
            f"Order {order.id}'s freeze approves each alteration of {package.id} that no "
            f"earlier order's freeze approved: {sorted(due)} are due, "
            f"{sorted(move.approved_alterations)} were approved (RP-12 ruling 63)."
        )


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
        and not order_took_stopping_exit(ledger, other)
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
    if not move.baseline:
        _refuse(
            f"Order {order.id} freezes at least one repair REQ held on {order.work_package}; "
            "an order frozen on nothing takes no dispatch and reaches no acceptance (RP-12 "
            "ruling 61). Write one with `uv run gz wp req new`, then freeze on it."
        )
    held = {req.id: req for req in catalog.reqs}
    holders = _live_holders(ledger, order)
    delivered = set(package_held_reqs(ledger, order.work_package))
    for entry in move.baseline:
        _check_entry(held, holders, order, entry)
        if f"{entry.req}@{entry.revision}" in delivered:
            _refuse(
                f"{entry.req} at revision {entry.revision} is held: a proceed delivered it there "
                "(RP-12 ruling 78), so no later order freezes it at that revision (ruling 81). "
                "New work on it is a new revision through a `reopen` exit, or a REQ that "
                "supersedes it."
            )
    package = _package(catalog, order)
    _check_seal_grows(ledger, package)
    _check_alterations(ledger, order, package, move)


def _check_seal_grows(ledger: Ledger, package: WorkPackage) -> None:
    """Refuse a freeze whose store dropped a path the seal declares (RP-12 ruling 71)."""
    if not footprint_sealed(ledger, package.id):
        return
    if dropped := [m for m in declared_modules(ledger, package) if m not in package.modules]:
        _refuse(
            f"{package.id}'s store dropped {', '.join(dropped)}, which an order's freeze "
            "sealed; a sealed footprint only grows (RP-12 rulings 56 and 71). Restore each "
            "path in data/catalog/work_packages.json, then freeze again."
        )


def _check_successor(catalog: Catalog, ledger: Ledger, order: Order, successor: str) -> None:
    """Refuse a redirect's successor unless it is opened, unfrozen, in the same package."""
    held = next((o for o in catalog.orders if o.id == successor), None)
    state = order_state(ledger, successor) if held else None
    if held is None or held.id == order.id or held.work_package != order.work_package:
        _refuse(
            f"--superseded-by {successor} is not another order of {order.work_package}; a "
            "redirect names the order of the same package that supersedes it (RP-12 ruling 75)."
        )
    if state != "opened":
        _refuse(
            f"{successor} is {state or 'not opened'}; a redirect names an order already opened "
            "with `uv run gz wp order new` and not yet frozen, so it freezes next (RP-12 "
            "ruling 75)."
        )


def _check_decision_fields(move: OrderMove) -> None:
    """Refuse a decision missing its own field or carrying another's (RP-12 ruling 73)."""
    own = _DECISION_FIELD[str(move.decision)]
    if own is not None and not (getattr(move, own) or "").strip():
        _refuse(f"A {move.decision} carries {own.replace('_', '-')} (RP-12 ruling 73).")
    # Another decision's field is refused whenever it is given, blank or not.
    given = {f for f in _DECISION_FIELD.values() if f and getattr(move, f) is not None}
    if others := sorted(given - {own}):
        flags = ", ".join(f"--{f.replace('_', '-')}" for f in others)
        _refuse(f"A {move.decision} does not carry {flags} (RP-12 ruling 73).")


def _check_delivered(
    ledger: Ledger, order: Order, acceptance_ready: Callable[[str], bool] | None
) -> None:
    """Refuse a proceed on a stopped order whose acceptance never read ready (ruling 80)."""
    ready = acceptance_ready is not None and acceptance_ready(order.id)
    if order_took_stopping_exit(ledger, order.id) and not ready:
        _refuse(
            f"{order.id} took a stopping exit and acceptance does not read ready, so it "
            "delivered nothing to proceed with, and a proceed would hold its REQs (RP-12 "
            "rulings 78 and 80). Close it as `redirect`, `pause` or `terminate`."
        )


def _check_closed(
    catalog: Catalog,
    ledger: Ledger,
    order: Order,
    move: OrderMove,
    acceptance_ready: Callable[[str], bool] | None,
) -> None:
    """Check Gate 5 at the order: the words, the decision and its own field (73 to 75, 80)."""
    if not (move.attestor or "").strip() or not (move.attestation_text or "").strip():
        _refuse(
            f"Order {order.id} closes only through Gate 5: an attestor and the operator's "
            "verbatim words, --attestation-text (AGENTS.md § Attestation)."
        )
    if move.decision is None:
        _refuse("Gate 5 records one of proceed, redirect, pause or terminate (RP-12 ruling 30).")
    if order_state(ledger, order.id) == "opened" and move.decision != "terminate":
        _refuse(
            f"Order {order.id} was never frozen and holds no REQ, so it closes only as "
            "terminate; a frozen order closes once it is accepted (RP-12 ruling 74)."
        )
    _check_decision_fields(move)
    if move.decision == "redirect":
        _check_successor(catalog, ledger, order, str(move.superseded_by))
    if move.decision == "proceed":
        _check_delivered(ledger, order, acceptance_ready)


def _check_move(
    catalog: Catalog,
    ledger: Ledger,
    order: Order,
    move: OrderMove,
    acceptance_ready: Callable[[str], bool] | None = None,
) -> None:
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
    if move.to_state == "closed":
        _check_closed(catalog, ledger, order, move, acceptance_ready)


def order_move_refusal(ledger: Ledger, order: Order, to_state: str) -> str | None:
    """Say why the order's lifecycle or block refuses the move, or None when it may move.

    Read before the move's own checks, by the writer and by the verbs, so a refusal
    names the lifecycle or the block (RP-12 ruling 59) before readiness or the seal.

    Returns:
        The refusal, or None when the move is the next step and the order is not blocked.

    """
    current = order_state(ledger, order.id)
    expected = _NEXT.get(current)
    # An order never frozen holds no REQ, so Gate 5 may withdraw it (ruling 74).
    allowed = {expected, "closed"} if current == "opened" else {expected}
    if to_state not in allowed:
        closing = (
            " An order closes from accepted, or from opened as a terminate (RP-12 ruling 74)."
            if to_state == "closed"
            else ""
        )
        return (
            f"Order {order.id} cannot move from {current or 'nothing'} to {to_state!r}; "
            f"the lifecycle allows {expected or 'no move'} from here.{closing}"
        )
    if is_order_blocked(ledger, order.id):
        return (
            f"Order {order.id} is blocked on the operator; it does not move until "
            f"`uv run gz wp unblock {order.work_package} --order {order.id} --ruling <words> "
            "--operator <who>` records the ruling (RP-12 ruling 59)."
        )
    return None


def record_order_transition(
    catalog: Catalog,
    ledger: Ledger,
    move: OrderMove,
    *,
    acceptance_ready: Callable[[str], bool] | None = None,
) -> OrderTransitionedEvent:
    """Book one lifecycle move for an order, or refuse it and write nothing.

    ``acceptance_ready`` reads whether an order's acceptance reads ready, taken as a
    parameter since the writer holds no project root; a proceed on an order a
    stopping exit excused is refused unless it says so, fail-closed (ruling 80).

    Returns:
        The event booked.

    """
    order = _order(catalog, move.order)
    if not move.evidence.strip():
        _refuse("A transition names what justifies it; evidence is empty.")
    current = order_state(ledger, order.id)
    if refusal := order_move_refusal(ledger, order, move.to_state):
        _refuse(refusal)
    _check_move(catalog, ledger, order, move, acceptance_ready)
    event = OrderTransitionedEvent.model_validate(
        {
            **move.model_dump(exclude_unset=True),
            "event": "order_transitioned",
            "id": order.id,
            "work_package": order.work_package,
            "from_state": current,
            "evidence": move.evidence.strip(),
            "modules": _package(catalog, order).modules if move.to_state == "frozen" else (),
            # The attestor is an identity, stripped as the package writer strips it; the
            # operator's words are booked verbatim (AGENTS.md § Attestation).
            "attestor": move.attestor.strip() if move.attestor else None,
        }
    )
    ledger.append(ledger_row(event))
    return event
