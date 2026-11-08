"""``gz wp order`` commands over the orders (RP-12 O2 task 1).

The verbs the operator named on 2026-11-05 (RP-12 ruling 47, *"a"*): a nested
group on the work-package surface. `accept` waits on the order's own acceptance
(ruling 60), and `close` is Gate 5 at the order (rulings 73 to 77). `new`
writes an order's record with the next `ORD-<NN>-<slug>` (ruling 43) through
`gzkit.order_store`, into a repair package that is initiated and not closed
(rulings 2, 44); `show` reads it with the kind of the package it sits in. The
record is thin (ruling 46). A refusal of the rulings exits 3 and writes nothing,
naming the flag at fault and the call to re-run; an unknown package or order
exits 1. `new` books the order's opening on the
operator's words before it writes the record (ruling 52), so a refusal writes
neither.
"""

import re
from typing import NoReturn

from pydantic import ValidationError as PydanticValidationError

from gzkit.acceptance_store import acceptance_blockers, round_bound_refusal
from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.core.exceptions import PolicyBreachError, ResourceNotFoundError
from gzkit.events import BaselinedReq, OrderTransitionedEvent
from gzkit.ledger import Ledger
from gzkit.models.catalog import Catalog, Order, WorkPackage, load_catalog
from gzkit.order_ledger import (
    OrderLedgerError,
    OrderMove,
    booked_order_ids,
    order_baseline,
    order_move_refusal,
    order_state,
    order_took_stopping_exit,
    record_order_transition,
)
from gzkit.order_store import OrderStoreError, next_order_id, stage_order, write_orders
from gzkit.work_package_ledger import work_package_state
from gzkit.work_package_transit import cross_airlock, footprint_refusal, freeze_refusal


def _package(catalog: Catalog, work_package: str) -> WorkPackage:
    held = next((wp for wp in catalog.work_packages if wp.id == work_package), None)
    if held is None:
        msg = (
            f"Work package {work_package!r} is not in data/catalog/work_packages.json. "
            "An order sits in a package the catalog holds; create one with `gz wp new`."
        )
        raise ResourceNotFoundError(msg)
    return held


def _order(catalog: Catalog, order_id: str) -> Order:
    held = next((order for order in catalog.orders if order.id == order_id), None)
    if held is None:
        msg = (
            f"Order {order_id!r} is not in data/catalog/orders.json. "
            "Write one with `uv run gz wp order new <WP-id> --slug <slug> --purpose <text> "
            "--operator-text <words>`."
        )
        raise ResourceNotFoundError(msg)
    return held


_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FLAGS = {
    "purpose": "--purpose",
    "procedure": "--procedure",
    "aliases": "--alias",
    "operator_text": "--operator-text",
    "evidence": "--evidence",
}
_OPEN = "initiated"


def _refuse(failed: str, why: str) -> NoReturn:
    msg = (
        f"{failed} {why} Nothing was written; correct the call and re-run "
        "`uv run gz wp order new <WP-id> --slug <slug> --purpose <text> --operator-text "
        "<words>`."
    )
    raise PolicyBreachError(msg)


def _schema_errors(exc: PydanticValidationError) -> str:
    """Name each refused field by the flag the operator typed, never the model's field.

    Returns:
        One clause per refused field, joined by semicolons.

    """
    return "; ".join(
        f"{_FLAGS.get(str(error['loc'][0]), str(error['loc'][0]))}: {error['msg']}"
        for error in exc.errors()
    )


def open_package_refusal(
    ledger: Ledger, package: WorkPackage, what: str, why: str
) -> tuple[str, str] | None:
    """Read whether a repair package is open to take ``what``, an order or a repair REQ.

    ``why`` is the ruling that keeps the package open for it.

    Returns:
        What failed and why, or None when the package is initiated and not closed.

    """
    state = work_package_state(ledger, package.id)
    if state == _OPEN:
        return None
    return (
        f"Work package {package.id} is {state or 'not initiated'}.",
        (
            f"{what} is written into a repair package that is initiated and not closed, "
            f"{why}; `uv run gz wp initiate {package.id} --operator-text <words>` initiates one."
        ),
    )


def store_broken(breaches: list[str], store: str) -> NoReturn:
    """Refuse a write into a store that breaks its rules before the call (exit 3).

    Raises:
        PolicyBreachError: Always; nothing is written.

    """
    msg = (
        f"{' '.join(breaches)} data/catalog/{store} breaks its rules already, before this "
        "call, so nothing was written. Run `uv run gz validate --catalog`, which names each "
        "finding, and repair the store before writing again."
    )
    raise PolicyBreachError(msg)


def _booked_lost(catalog: Catalog, ledger: Ledger) -> None:
    """Refuse every write while the store has lost an order the ledger names (ruling 52)."""
    if missing := sorted(booked_order_ids(ledger) - {order.id for order in catalog.orders}):
        store_broken(
            [
                (
                    f"Orders {', '.join(missing)} have ledger events but no record; an order "
                    "is born on the ledger and its id is never reused (RP-12 rulings 43, 52)."
                )
            ],
            "orders.json",
        )


def wp_order_new_cmd(
    *, work_package: str, record: dict[str, object], opening: dict[str, str], as_json: bool
) -> None:
    """Write a new order's record and book its opening (RP-12 rulings 43 and 52).

    ``record`` carries the verb's fields bar the id and the package: the slug, the
    purpose, the procedure and the aliases. ``opening`` carries the operator's words
    and the evidence its `order_transitioned` to `opened` books.

    A refusal of the slug, a field, the package's state, the opening or a rule `gz
    validate --catalog` reads exits 3 through `_refuse` and writes nothing.
    """
    config = ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    ledger = Ledger(root / config.paths.ledger)
    package = _package(catalog, work_package)
    _booked_lost(catalog, ledger)
    for field, value in opening.items():
        if not value.strip():
            _refuse(
                f"{_FLAGS[field]} is empty.",
                "An order is opened on the operator's words and booked on the ledger "
                "(RP-12 ruling 52).",
            )
    slug = str(record["slug"])
    if not _SLUG.match(slug):
        _refuse(
            f"--slug {slug!r} is not lowercase words joined by hyphens.",
            "It is the last part of the order's id, ORD-<NN>-<slug> (RP-12 ruling 43).",
        )
    try:
        order = Order.model_validate(
            {
                **{key: value for key, value in record.items() if key != "slug"},
                "id": next_order_id(catalog, slug, booked_order_ids(ledger)),
                "work_package": package.id,
            }
        )
    except PydanticValidationError as exc:
        _refuse(f"{_schema_errors(exc)}.", "The order record is ruled by RP-12 ruling 46.")
    try:
        staged = stage_order(catalog, order)
    except OrderStoreError as exc:
        if exc.in_store:
            store_broken(exc.breaches, "orders.json")
        _refuse(
            " ".join(exc.breaches),
            "The rulings are in docs/governance/harbor-ro12-contractor-kit.md.",
        )
    why = "since its close reads every order's Gate 5 (RP-12 rulings 2 and 44)"
    if refusal := open_package_refusal(ledger, package, "An order", why):
        _refuse(*refusal)
    move = OrderMove(
        order=order.id,
        to_state="opened",
        evidence=opening["evidence"],
        operator_text=opening["operator_text"],
    )
    try:
        record_order_transition(staged, ledger, move)
    except OrderLedgerError as exc:
        _refuse(str(exc), "The rulings are in docs/governance/harbor-ro12-contractor-kit.md.")
    write_orders(root, staged)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(order if as_json else f"Wrote {order.id} in {package.id} ({package.kind}).")


_RERUN = {
    "frozen": (
        "`uv run gz wp order freeze <ORD-id> --baseline REQ-<n>@<revision> --risk-note <text> "
        "--review-receipt <id> [--approve-alteration <id>] --evidence <text>`"
    ),
    "commenced": "`uv run gz wp order commence <ORD-id> --evidence <text>`",
    "accepted": "`uv run gz wp order accept <ORD-id> --evidence <text>`",
    "closed": (
        "`uv run gz wp order close <ORD-id> --decision <proceed|redirect|pause|terminate> "
        "--attestor g0 --attestation-text <words> --evidence <text> [--residual-risk <text> | "
        "--superseded-by <ORD-id> | --revisit-condition <text>]`"
    ),
}


def _refuse_move(to_state: str, failed: str) -> NoReturn:
    msg = f"{failed} Nothing was written; correct the call and re-run {_RERUN[to_state]}."
    raise PolicyBreachError(msg)


def _baseline_entry(to_state: str, entry: str) -> BaselinedReq:
    req, _, revision = entry.partition("@")
    if not req or not revision.isdigit():
        _refuse_move(to_state, f"--baseline {entry!r} is not REQ-<n>@<revision>.")
    return BaselinedReq(req=req, revision=int(revision))


def wp_order_transition_cmd(
    *, fields: dict[str, object], baseline: list[str] | None, as_json: bool
) -> None:
    """Move an order one step, `frozen` or `commenced` (RP-12 O2 task 3).

    ``fields`` are the ``OrderMove`` fields the verb's flags supplied; a freeze's
    ``baseline`` arrives as ``REQ-<n>@<revision>`` strings. A freeze seals the repair
    package's footprint (ruling 56), so it is refused while that footprint does not
    hold, and approves the package's alterations no earlier freeze approved (ruling
    63); a commencement crosses the airlock inward on the package's slice (ruling 65).
    An unknown order exits 1; any refusal exits 3 and writes nothing.
    """
    config = ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    ledger = Ledger(root / config.paths.ledger)
    to_state = str(fields["to_state"])
    _booked_lost(catalog, ledger)
    order = _order(catalog, str(fields["order"]))
    package = _package(catalog, order.work_package)
    if refusal := order_move_refusal(ledger, order, to_state):
        _refuse_move(to_state, refusal)
    if to_state == "frozen" and (refusal := freeze_refusal(root, package, ledger)):
        _refuse_move(to_state, f"{refusal} An order's freeze seals it (RP-12 ruling 56).")
    entries = [_baseline_entry(to_state, entry) for entry in baseline or ()]
    move = OrderMove.model_validate({**fields, **({"baseline": entries} if entries else {})})
    try:
        event = record_order_transition(catalog, ledger, move)
    except OrderLedgerError as exc:
        _refuse_move(to_state, str(exc))
    _emit_move(event, cross_airlock(root, ledger, package, event.to_state), as_json=as_json)


def _emit_move(event: OrderTransitionedEvent, crossed: str | None, *, as_json: bool) -> None:
    """Print the move and, for a move across the airlock, what it read (RP-12 ruling 65)."""
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        event if as_json else f"{event.id}: {event.from_state or 'nothing'} -> {event.to_state}"
    )
    if crossed and not as_json:
        fmt.emit(f"  {crossed}")


def wp_order_show_cmd(*, order_id: str, as_json: bool) -> None:
    """Show an order's record, its package's kind, and its state and baseline (ruling 44)."""
    config = ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    ledger = Ledger(root / config.paths.ledger)
    order = _order(catalog, order_id)
    package = _package(catalog, order.work_package)
    state = order_state(ledger, order.id)
    baseline = order_baseline(ledger, order.id)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(
            {
                "record": order.model_dump(mode="json"),
                "kind": package.kind,
                "state": state,
                "baseline": baseline,
            }
        )
        return
    fmt.emit(f"{order.id} in {package.id} ({package.kind})")
    fmt.emit(f"  state: {state or 'not opened'}")
    fmt.emit(f"  baseline: {', '.join(f'{r}@{n}' for r, n in baseline.items()) or 'none'}")
    fmt.emit(f"  aliases: {', '.join(order.aliases) or 'none'}")
    fmt.emit(f"  purpose: {order.purpose}")
    fmt.emit(f"  procedure: {order.procedure}")


def wp_order_accept_cmd(*, order_id: str, evidence: str, as_json: bool) -> None:
    """Accept a commenced order once its acceptance reads ready (RP-12 ruling 60).

    The lifecycle and the order's block are read first, so a refusal names them
    (ruling 59) before readiness. Then the order's own readiness is read, its
    obligations its frozen REQs and its proofs and reviews under its id, with the
    review-round limit of GHI #1028; then the repair package's sealed footprint
    (ruling 56). An order stopped by an exit is excused both, as a stopped package
    is: it claims no delivery, and Gate 5 is how it closes. The move crosses the
    airlock outward on the package's slice (ruling 65). An unknown order exits 1;
    any refusal exits 3 and books nothing.

    Raises:
        PolicyBreachError: The lifecycle or the block refuses the move, acceptance
            reports its blockers, or a file lies outside the footprint.

    """
    config = ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    ledger = Ledger(root / config.paths.ledger)
    _booked_lost(catalog, ledger)
    order = _order(catalog, order_id)
    package = _package(catalog, order.work_package)
    if refusal := order_move_refusal(ledger, order, "accepted"):
        _refuse_move("accepted", refusal)
    if not order_took_stopping_exit(ledger, order.id):
        refusal = round_bound_refusal(root, order.id)
        blockers = [*acceptance_blockers(root, order.id), *([refusal] if refusal else [])]
        if blockers:
            raise PolicyBreachError("\n".join(blockers))
        if outside := footprint_refusal(root, package, ledger):
            raise PolicyBreachError(outside)
    move = OrderMove(order=order.id, to_state="accepted", evidence=evidence)
    try:
        event = record_order_transition(catalog, ledger, move)
    except OrderLedgerError as exc:
        _refuse_move("accepted", str(exc))
    _emit_move(event, cross_airlock(root, ledger, package, event.to_state), as_json=as_json)


def wp_order_close_cmd(
    *, fields: dict[str, object], called_by_subagent: bool, as_json: bool
) -> None:
    """Close an order through Gate 5 at the order (RP-12 rulings 30 and 73 to 77).

    ``fields`` are the ``OrderMove`` fields the verb's flags supplied, those not given
    left out so a decision's refusal of another decision's field reads them. Gate 5
    is the operator's act, so a call the dispatch stamp marks as a subagent's is
    refused (ruling 77). The order closes from `accepted`, or from `opened` as a
    terminate alone (ruling 74), with the decision, the attestor, the operator's
    verbatim words and the field the decision names (ruling 73); a redirect names an
    order of the same package already opened and not frozen (ruling 75). An unknown
    order exits 1; any refusal exits 3 and books nothing.

    Raises:
        PolicyBreachError: The call is a subagent's, a booked order lost its record,
            or the lifecycle, the block or Gate 5's own rules refuse the close.

    """
    if called_by_subagent:
        msg = (
            "Gate 5 is refused from a subagent's call: it is the operator's act, recorded "
            "on the operator's own words (RP-12 ruling 77, AGENTS.md § Attestation). Run "
            "it from the main session."
        )
        raise PolicyBreachError(msg)
    config = ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    ledger = Ledger(root / config.paths.ledger)
    _booked_lost(catalog, ledger)
    order = _order(catalog, str(fields["order"]))
    if refusal := order_move_refusal(ledger, order, "closed"):
        _refuse_move("closed", refusal)
    move = OrderMove.model_validate({**fields, "to_state": "closed"})
    try:
        event = record_order_transition(catalog, ledger, move)
    except OrderLedgerError as exc:
        _refuse_move("closed", str(exc))
    _emit_move(event, None, as_json=as_json)
