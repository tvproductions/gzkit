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
package (rulings 2, 45), each REQ in one live order's frozen baseline at a time,
an accepted order holding its REQs until its Gate 5 (rulings 53 and 82), never a
REQ a proceed holds at that revision (ruling 81) nor a superseded REQ, the refusal
naming each head of its chains (rulings 85 and 87), and never on an empty baseline
(ruling 61). A freeze approves exactly
the package's planned alterations no earlier order's freeze approved (ruling 63),
since a repair package never freezes itself (ruling 44). An accepted move books
`acceptance_ready`, false only on an order a stopping exit stopped (rulings 84 and
86), and is refused while a tag the order hung is not cleared, a stopped order
included (refusal 6, ruling 142), unless one open due-by line of the coordinator's
cites it, a carry the move books as `carried` (rulings 171 and 184; two such lines
refuse it, ruling 186); while a carried tag still hangs, Gate 5 takes a pause alone
(ruling 171). A proceed reads the booked readiness and is refused
when another order's proceed already holds one of its REQs at that revision
(ruling 82). A blocked order does
not move (ruling 59).

The writer takes the parsed catalog and the ledger as parameters, reads the
current state from the ledger rather than the caller, and refuses a move the
ruled grammar does not allow, writing nothing.
"""

from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import BaselinedReq, CarriedTag, OrderTransitionedEvent, WorkPackageDecision
from gzkit.ledger import ledger_row
from gzkit.models.catalog import RepairReq
from gzkit.mx.record_rows import DUE_BY, malformed_row_message, open_discrepancies
from gzkit.mx.tag_rows import order_tags
from gzkit.work_package_ledger import (
    declared_modules,
    footprint_sealed,
    package_held_reqs,
    work_package_state,
)

if TYPE_CHECKING:
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
#: The states that end an order's hold on its baseline (ruling 53): only Gate 5, since
#: an accepted order holds it until then (ruling 82); a stopping exit ends it too,
#: though the order keeps its state (`order_took_stopping_exit`).
TERMINATED: frozenset[str] = frozenset({"closed"})
#: The exits that stop a run: an order's or, for a delivery package, the package's.
STOPPING_EXITS: frozenset[str] = frozenset({"reopen", "terminate"})
#: The payload fields each target state carries; any other is refused.
_STATE_FIELDS: dict[str, frozenset[str]] = {
    "opened": frozenset({"operator_text"}),
    "frozen": frozenset({"baseline", "risk_note", "review_receipt", "approved_alterations"}),
    "commenced": frozenset({"no_isolation"}),
    "accepted": frozenset({"acceptance_ready"}),
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
    acceptance_ready: bool | None = Field(None, description="Readiness read, at accepted")
    no_isolation: str | None = Field(
        None, description="Why an order with no tag isolates nothing, at commenced (ruling 117)"
    )


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
    if (holder := holders.get(entry.req)) not in {None, ""}:
        _refuse(
            f"{entry.req} is in the frozen baseline of live order {holder}; a repair REQ "
            "sits in one live order's baseline at a time, until that order is stopped or "
            "closed (RP-12 ruling 53); an accepted order holds it until its Gate 5 (ruling "
            "82). Freeze without it, or split it with a REQ that supersedes it."
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
    successors: dict[str, list[str]] = {}
    for req in catalog.reqs:
        if req.supersedes not in {None, ""}:
            successors.setdefault(req.supersedes, []).append(req.id)
    for entry in move.baseline:
        _check_entry(held, holders, order, entry)
        _check_not_superseded(successors, entry.req)
        if f"{entry.req}@{entry.revision}" in delivered:
            _refuse(
                f"{entry.req} at revision {entry.revision} is held: a proceed delivered it there "
                "(RP-12 ruling 78), so no later order freezes it at that revision (ruling 81). "
                "New work on it is a REQ that supersedes it, written with `uv run gz wp req "
                "new` (rulings 50 and 83)."
            )
    package = _package(catalog, order)
    _check_seal_grows(ledger, package)
    _check_alterations(ledger, order, package, move)


def _check_not_superseded(successors: dict[str, list[str]], req: str) -> None:
    """Refuse freezing a superseded REQ, naming every REQ to freeze instead (85, 87)."""
    if (later := successors.get(req)) is None:
        return
    heads = _chain_heads(successors, req)
    instead = (
        f"Freeze {' or '.join(heads)} instead (ruling 87)."
        if heads
        else "Its chain cycles, so no REQ ends it; correct one `supersedes` in "
        "data/catalog/reqs.json, as `uv run gz validate --catalog` reports (ruling 87)."
    )
    _refuse(
        f"{req} is superseded by {' and '.join(later)}, so it is retired whole (RP-12 "
        f"ruling 31) and no order freezes it (ruling 85). {instead}"
    )


def _chain_heads(successors: dict[str, list[str]], req: str) -> list[str]:
    """Name every REQ nothing supersedes that ``req``'s chains reach (rulings 85 and 87).

    A split gives one REQ two successors (ruling 53), so the chains are a tree. A head
    is a REQ no REQ supersedes; a cycle, which only a hand edit makes and the catalog
    validator refuses, has none, so the walk names none for it.

    Returns:
        The chain heads, in the order the walk reaches them.

    """
    heads: list[str] = []
    seen = {req}
    pending = list(successors.get(req, ()))
    while pending:
        current = pending.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if (later := successors.get(current)) is not None:
            pending.extend(later)
        else:
            heads.append(current)
    return heads


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
    given = {f for f in _DECISION_FIELD.values() if f is not None and getattr(move, f) is not None}
    if others := sorted(given - {own}):
        flags = ", ".join(f"--{f.replace('_', '-')}" for f in others)
        _refuse(f"A {move.decision} does not carry {flags} (RP-12 ruling 73).")


def _check_delivered(ledger: Ledger, order: Order) -> None:
    """Refuse a proceed on a stopped order whose acceptance never read ready (80, 84).

    The readiness is the one its `accepted` move booked; a move that booked none
    reads not ready, fail-closed.
    """
    accepted = [move for move in _moves(ledger, order.id) if move.get("to_state") == "accepted"]
    ready = bool(accepted) and accepted[-1].get("acceptance_ready") is True
    if order_took_stopping_exit(ledger, order.id) and not ready:
        _refuse(
            f"{order.id} took a stopping exit and its acceptance did not read ready, so it "
            "delivered nothing to proceed with, and a proceed would hold its REQs (RP-12 "
            "rulings 78, 80 and 84). Close it as `redirect`, `pause` or `terminate`."
        )


def carried_tags(ledger: Ledger, order_id: str) -> tuple[CarriedTag, ...]:
    """Read the carries the order's acceptance booked (ruling 184), never re-derived.

    Returns:
        Each carry its `accepted` move booked, or none when it booked none.

    """
    accepted = [
        row
        for row in ledger.query(event_type="order_transitioned")
        if row.extra.get("order") == order_id and row.extra.get("to_state") == "accepted"
    ]
    if not accepted:
        return ()
    try:
        return OrderTransitionedEvent.model_validate(accepted[-1].model_dump()).carried
    except ValidationError as exc:
        _refuse(
            malformed_row_message(
                accepted[-1], exc, f"{order_id}'s carry cannot be read", ruling=184
            )
        )


def paused_carried_tags(ledger: Ledger, order_id: str) -> frozenset[str]:
    """Read the tags a paused order's acceptance carried, which it still clears (ruling 187).

    A pause defers the order with a revisit condition rather than withdrawing it
    (ruling 30), so the order that carried a tag past acceptance clears it.

    Returns:
        The carried tags when the order's Gate 5 closed it as a pause, else none.

    """
    closes = [m for m in _moves(ledger, order_id) if m.get("to_state") == "closed"]
    if not closes or closes[-1].get("decision") != "pause":
        return frozenset()
    return frozenset(carry.tag_id for carry in carried_tags(ledger, order_id))


def carried_tags_hung(ledger: Ledger, order_id: str) -> tuple[CarriedTag, ...]:
    """Read the carries the order's acceptance booked whose tag still hangs (ruling 171).

    The one reading of "a carried tag still hangs": Gate 5's pause reads it, and so do
    the paused order's Restoration dispatch and block (rulings 187 and 188).

    Returns:
        Each booked carry whose tag is hung and not cleared, in booked order.

    """
    hung = set(order_tags(ledger, order_id).hung_uncleared)
    return tuple(carry for carry in carried_tags(ledger, order_id) if carry.tag_id in hung)


def holds_paused_carry(ledger: Ledger, order_id: str) -> bool:
    """Whether Gate 5 paused the order with a tag its acceptance carried still hung.

    Such an order still takes the Restoration dispatch that clears it (ruling 187) and
    the block an out-of-position find books on it (ruling 188).

    Returns:
        True when the order is paused and one of its carried tags still hangs.

    """
    return bool(paused_carried_tags(ledger, order_id)) and bool(carried_tags_hung(ledger, order_id))


def _check_carry_pause(ledger: Ledger, order: Order, move: OrderMove) -> None:
    """Refuse every decision but pause while a tag acceptance carried still hangs (ruling 171)."""
    if move.decision == "pause":
        return
    if still := carried_tags_hung(ledger, order.id):
        named = ", ".join(f"{c.tag_id} (carried by {c.discrepancy_id})" for c in still)
        _refuse(
            f"Order {order.id}'s acceptance carried tag(s) that still hang: {named}. While a "
            "carried tag hangs, Gate 5 takes a pause alone, since the surface is still "
            "isolated (RP-12 ruling 171, on ruling 30's pause). Close it as `pause` with "
            "--revisit-condition; the paused order's Restoration dispatch then clears the "
            "tag (ruling 187)."
        )


def _check_closed(
    catalog: Catalog,
    ledger: Ledger,
    order: Order,
    move: OrderMove,
) -> None:
    """Check Gate 5 at the order: the words, the decision and its fields (73 to 75, 80, 82, 84)."""
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
    _check_carry_pause(ledger, order, move)
    if move.decision == "redirect":
        _check_successor(catalog, ledger, order, str(move.superseded_by))
    if move.decision == "proceed":
        _check_delivered(ledger, order)
        _check_not_held(ledger, order)


def _check_commenced(ledger: Ledger, order: Order, move: OrderMove) -> None:
    """Hold commencement on the order's tags: each hung, or none and a stated reason.

    Ruling 108 waits on every tag issued on the order; ruling 117 has an order with
    none commence only on the coordinator's stated no-isolation, refused when a tag
    is issued; ruling 143 excuses a stopped order, which does no work.
    """
    stated = move.no_isolation
    if stated is not None and not stated.strip():
        _refuse(
            "--no-isolation is blank. An order with no tag commences on a stated reason that "
            "the repair isolates nothing (RP-12 ruling 117); state why, or issue the tags."
        )
    tags = order_tags(ledger, order.id)
    if tags.issued and stated is not None:
        _refuse(
            f"Order {order.id} has {len(tags.issued)} tag(s) issued "
            f"({', '.join(tags.issued)}), so it isolates something and --no-isolation is "
            "refused (RP-12 ruling 117). Commence it without the option once every tag is hung."
        )
    if order_took_stopping_exit(ledger, order.id):
        return
    if not tags.issued and stated is None:
        _refuse(
            f"Order {order.id} has no tag issued. An order commences once every surface it "
            "isolates has its tag hung, or on the coordinator's stated reason that it "
            "isolates nothing (RP-12 rulings 108 and 117). Issue its tags with `uv run gz wp "
            f'tag issue {order.id}`, or commence it with `--no-isolation "<why>"`.'
        )
    if tags.unhung:
        _refuse(
            f"Order {order.id} has tag(s) issued and not hung: {', '.join(tags.unhung)}. It "
            "commences only once every tag issued on it is hung, so no work runs on a "
            "surface not yet isolated (RP-12 ruling 108). Book a Repair dispatch on the "
            f"frozen order (`uv run gz wp dispatch {order.work_package} --order {order.id} "
            "--role Repair --model <tier>`) and have its subagent run `uv run gz wp tag "
            "hang <TAG-id> --dispatch D-<id>` for each, then commence."
        )


def _carrying_lines(ledger: Ledger, order_id: str) -> dict[str, list[str]]:
    """Map each tag of the order to the open lines that may carry it (ruling 171).

    A line carries a tag when it is open, graded *due by a named event*, recorded by
    the coordinator's unstamped call (no dispatch, ruling 114's mark), on the order,
    and cites the tag.

    Returns:
        Each cited tag with the ids of the lines citing it, oldest first.

    """
    lines: dict[str, list[str]] = {}
    for line in open_discrepancies(ledger):
        record = line.record
        if (
            record.order == order_id
            and record.grade == DUE_BY
            and record.dispatch_id is None
            and record.tag_id is not None
        ):
            lines.setdefault(record.tag_id, []).append(record.discrepancy_id)
    return lines


class CarryStanding(BaseModel):
    """Each hung tag of an order, read against the lines that may carry it (171, 184, 186)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    carried: tuple[CarriedTag, ...] = Field(..., description="Tags one open line carries")
    uncarried: tuple[str, ...] = Field(..., description="Hung tags no line carries")
    doubled: tuple[tuple[str, tuple[str, ...]], ...] = Field(
        ..., description="Hung tags two or more lines carry, each with its lines"
    )


def carry_standing(ledger: Ledger, order_id: str) -> CarryStanding:
    """Read each hung tag of the order against its carrying lines, once (rulings 171, 186).

    The one reading both the acceptance refusal and the booked carry take: a tag one
    open line carries is carried, a tag no line carries holds acceptance, and a tag two
    or more lines carry holds it too (ruling 186).

    Returns:
        The order's carried, uncarried and doubly carried tags, each in issue order.

    """
    lines = _carrying_lines(ledger, order_id)
    hung = order_tags(ledger, order_id).hung_uncleared
    return CarryStanding(
        carried=tuple(
            CarriedTag(tag_id=tag, discrepancy_id=lines[tag][0])
            for tag in hung
            if len(lines.get(tag, ())) == 1
        ),
        uncarried=tuple(tag for tag in hung if lines.get(tag) is None),
        doubled=tuple((tag, tuple(lines[tag])) for tag in hung if len(lines.get(tag, ())) > 1),
    )


def hung_tag_refusal(ledger: Ledger, order: Order) -> str | None:
    """Say why a tag the order hung and nobody cleared holds its acceptance (refusal 6).

    Ruling 142 refused every hung tag, a stopped order's included (ruling 135), until
    O4's discrepancy record admitted a carry; ruling 171 admits a tag one open due-by
    line of the coordinator's cites, and ruling 186 holds a tag two such lines cite.
    Read by the writer and by `gz wp order accept`, which names it beside its other
    blockers.

    Returns:
        The refusal naming each tag held and its recovery, or None when none is held.

    """
    standing = carry_standing(ledger, order.id)
    refusals: list[str] = []
    if standing.uncarried:
        first = standing.uncarried[0]
        refusals.append(
            f"Order {order.id} has tag(s) hung, not cleared and not carried: "
            f"{', '.join(standing.uncarried)}. It is accepted only once every tag it hung is "
            "cleared or carried, so no surface is left isolated past acceptance unrecorded "
            "(refusal 6; RP-12 rulings 129, 142 and 171). To clear one, the coordinator "
            f"authorizes the clearance (`uv run gz wp tag authorize {first}`), books a "
            f"Restoration dispatch (`uv run gz wp dispatch {order.work_package} --order "
            f"{order.id} --role Restoration --model <tier>`), and its subagent runs `uv run gz "
            f"wp tag clear {first} --dispatch D-<id> --position-found <position>`. To carry "
            "one, the coordinator records a line graded due by a named event that cites it "
            f"(`uv run gz wp discrepancy record --order {order.id} --tag {first} --grade "
            'due-by-event --due-by "<event>" --source left-broken --slug <slug> --description '
            '"<what>"`); its Gate 5 then takes a pause alone, and the paused order\'s '
            "Restoration dispatch clears the tag (ruling 187). Then accept."
        )
    if standing.doubled:
        named = "; ".join(f"{tag} by {', '.join(ids)}" for tag, ids in standing.doubled)
        refusals.append(
            f"Order {order.id} has tag(s) carried by more than one open line: {named}. One "
            "line carries a tag, so its due-by event is never chosen silently (RP-12 ruling "
            "186). Clear all but one, citing the entry or the open issue that settles it "
            "(`uv run gz wp discrepancy clear <DSC-id> --entry <ENT-id>` or `--ghi <n>`), "
            "then accept."
        )
    return "\n".join(refusals) or None


def _check_accepted(ledger: Ledger, order: Order, move: OrderMove) -> None:
    """Refuse an acceptance that books no readiness, a held tag, or an unstopped one not ready.

    Rulings 86, 142 and 171: a hung tag neither cleared nor carried by one open due-by
    line holds it whatever its stop (refusal 6), and so does one two lines carry (186).
    """
    if move.acceptance_ready is None:
        _refuse(
            f"Order {order.id}'s acceptance books whether it read ready, `acceptance_ready`, "
            "which its Gate 5 reads (RP-12 rulings 84 and 86)."
        )
    if (refusal := hung_tag_refusal(ledger, order)) is not None:
        _refuse(refusal)
    if not move.acceptance_ready and not order_took_stopping_exit(ledger, order.id):
        _refuse(
            f"Order {order.id} took no stopping exit, so it is accepted only once its "
            "acceptance reads ready (RP-12 rulings 60 and 86)."
        )


def _check_not_held(ledger: Ledger, order: Order) -> None:
    """Refuse a proceed whose baseline another order's proceed already holds (ruling 82)."""
    held = set(package_held_reqs(ledger, order.work_package))
    baseline = order_baseline(ledger, order.id)
    if twice := sorted(f"{r}@{v}" for r, v in baseline.items() if f"{r}@{v}" in held):
        _refuse(
            f"{', '.join(twice)} already holds through another order's proceed (RP-12 ruling "
            f"78), so {order.id}'s proceed would hold it twice (ruling 82). Close it as "
            "`redirect`, `pause` or `terminate`."
        )


def _check_move(
    catalog: Catalog,
    ledger: Ledger,
    order: Order,
    move: OrderMove,
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
    if move.to_state == "commenced":
        _check_commenced(ledger, order, move)
    if move.to_state == "accepted":
        _check_accepted(ledger, order, move)
    if move.to_state == "closed":
        _check_closed(catalog, ledger, order, move)


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
) -> OrderTransitionedEvent:
    """Book one lifecycle move for an order, or refuse it and write nothing.

    A proceed on an order a stopping exit excused is refused unless its `accepted`
    move booked `acceptance_ready` true, fail-closed (rulings 80 and 84). An
    `accepted` move that books no `acceptance_ready`, or books it false on an order
    no stopping exit stopped, is refused (ruling 86).

    Returns:
        The event booked.

    """
    order = _order(catalog, move.order)
    if not move.evidence.strip():
        _refuse("A transition names what justifies it; evidence is empty.")
    current = order_state(ledger, order.id)
    if (refusal := order_move_refusal(ledger, order, move.to_state)) is not None:
        _refuse(refusal)
    _check_move(catalog, ledger, order, move)
    event = OrderTransitionedEvent.model_validate(
        {
            **move.model_dump(exclude_unset=True),
            "event": "order_transitioned",
            "id": order.id,
            "work_package": order.work_package,
            "from_state": current,
            "evidence": move.evidence.strip(),
            "modules": _package(catalog, order).modules if move.to_state == "frozen" else (),
            # Ruling 184: acceptance books each carry it admitted, which Gate 5 reads.
            "carried": (
                carry_standing(ledger, order.id).carried if move.to_state == "accepted" else ()
            ),
            # The attestor is an identity, stripped as the package writer strips it; the
            # operator's words are booked verbatim (AGENTS.md § Attestation).
            "attestor": move.attestor.strip() if move.attestor not in {None, ""} else None,
        }
    )
    ledger.append(ledger_row(event))
    return event
