"""``gz wp order`` commands over the orders (RP-12 O2 task 1).

The verbs the operator named on 2026-11-05 (RP-12 ruling 47, *"a"*): a nested
group on the work-package surface. `new` writes an order's record with the next
`ORD-<NN>-<slug>` (ruling 43) through `gzkit.order_store`, into a repair package
that is initiated and not closed (rulings 2, 44); `show` reads it with the kind of
the package it sits in. The record is thin (ruling 46). A refusal of the rulings
exits 3 and writes nothing, naming the flag at fault and the call to re-run; an
unknown package or order exits 1. `new` books the order's opening on the
operator's words before it writes the record (ruling 52), so a refusal writes
neither.
"""

import re
from typing import NoReturn

from pydantic import ValidationError as PydanticValidationError

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.core.exceptions import PolicyBreachError, ResourceNotFoundError
from gzkit.ledger import Ledger
from gzkit.models.catalog import Catalog, Order, WorkPackage, load_catalog
from gzkit.order_ledger import (
    OrderLedgerError,
    OrderMove,
    booked_order_ids,
    record_order_transition,
)
from gzkit.order_store import OrderStoreError, next_order_id, stage_order, write_orders
from gzkit.work_package_ledger import work_package_state


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


def wp_order_show_cmd(*, order_id: str, as_json: bool) -> None:
    """Show an order's record with the kind of the package it sits in (ruling 43)."""
    ensure_initialized()
    catalog = load_catalog(get_project_root())
    order = _order(catalog, order_id)
    package = _package(catalog, order.work_package)
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit({"record": order.model_dump(mode="json"), "kind": package.kind})
        return
    fmt.emit(f"{order.id} in {package.id} ({package.kind})")
    fmt.emit(f"  aliases: {', '.join(order.aliases) or 'none'}")
    fmt.emit(f"  purpose: {order.purpose}")
    fmt.emit(f"  procedure: {order.procedure}")
