"""``gz wp order`` commands over the orders (RP-12 O2 task 1).

The verbs the operator named on 2026-11-05 (RP-12 ruling 47, *"a"*): a nested
group on the work-package surface. `new` writes an order's record with the next
`ORD-<NN>-<slug>` (ruling 43) through `gzkit.order_store`; `show` reads it with
the kind of the package it sits in. The record is thin (ruling 46). A refusal of
the rulings exits 3 and writes nothing; an unknown package or order exits 1.
"""

from pydantic import ValidationError as PydanticValidationError

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.core.exceptions import PolicyBreachError, ResourceNotFoundError
from gzkit.models.catalog import Catalog, Order, WorkPackage, load_catalog
from gzkit.order_store import OrderStoreError, next_order_id, stage_order, write_orders


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
            "Write one with `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>`."
        )
        raise ResourceNotFoundError(msg)
    return held


def wp_order_new_cmd(*, work_package: str, record: dict[str, object], as_json: bool) -> None:
    """Write a new order's record with the next id in the one series (RP-12 ruling 43).

    ``record`` carries the verb's fields bar the id and the package: the slug, the
    purpose, the procedure and the aliases.

    Raises:
        PolicyBreachError: The record breaks its schema or a rule `gz validate --catalog`
            reads, such as an order on a delivery package (ruling 44); nothing is written.

    """
    ensure_initialized()
    root = get_project_root()
    catalog = load_catalog(root)
    package = _package(catalog, work_package)
    try:
        order = Order.model_validate(
            {
                **{key: value for key, value in record.items() if key != "slug"},
                "id": next_order_id(catalog, str(record["slug"])),
                "work_package": package.id,
            }
        )
        staged = stage_order(catalog, order)
    except (PydanticValidationError, OrderStoreError) as exc:
        msg = f"The order record is refused: {exc}"
        raise PolicyBreachError(msg) from exc
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
