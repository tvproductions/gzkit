"""The order store's one writer (RP-12 O2 task 1).

`data/catalog/orders.json` is edited only through `gz wp order` (RP-12 ruling
47), and this module is what it calls. Every write is checked against the rules
`gz validate --catalog` reads (`order_breaches`) before it reaches the file, so a
verb can never leave the store in a state the scope refuses. The store only
grows: no verb edits an order once written.
"""

import json
from typing import TYPE_CHECKING

from gzkit.governance.trust_audits.catalog import order_breaches
from gzkit.models.catalog import CATALOG_FILES, Catalog, Order
from gzkit.registries import load_registry, registry_path

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class OrderStoreError(ValueError):
    """A store edit RP-12's rulings refuse; nothing was written.

    Carries each breach as a sentence naming its ruling, so the verb can say what
    failed and why without the file-editing recovery a validator finding carries.
    """

    def __init__(self, breaches: list[str], *, in_store: bool = False) -> None:
        """Hold the breaches, and whether the store broke its rules before this edit."""
        super().__init__(" ".join(breaches))
        self.breaches = breaches
        self.in_store = in_store


def _number(order_id: str) -> int:
    return int(order_id.split("-")[1])


def next_order_id(catalog: Catalog, slug: str, booked: Iterable[str]) -> str:
    """Return the next id in the one series (ruling 43): the highest number plus one.

    ``booked`` is every order id the ledger names (`booked_order_ids`), so an id is
    never reused even if the store has lost a record (ruling 52).

    Returns:
        `ORD-<NN>-<slug>`, numbered past every order the store holds or the ledger names.

    """
    numbers = [_number(order_id) for order_id in {*(o.id for o in catalog.orders), *booked}]
    return f"ORD-{max(numbers, default=0) + 1:02d}-{slug}"


def stage_order(catalog: Catalog, order: Order) -> Catalog:
    """Return the catalog with the order added, refusing a breach.

    Returns:
        The catalog as it would read once written.

    Raises:
        OrderStoreError: The store breaks its rules already, the order's id is held,
            or the edit breaks a rule `gz validate --catalog` reads.

    """
    if existing := order_breaches(catalog):
        raise OrderStoreError(existing, in_store=True)
    if any(held.id == order.id for held in catalog.orders):
        raise OrderStoreError([f"Order {order.id} is in the store already; an id is never reused."])
    ordered = tuple(sorted((*catalog.orders, order), key=lambda held: _number(held.id)))
    staged = catalog.model_copy(update={"orders": ordered})
    if breaches := order_breaches(staged):
        raise OrderStoreError(breaches)
    return staged


def write_orders(project_root: Path, catalog: Catalog) -> Path:
    """Write the catalog's orders, keeping the file's `_doc` header.

    Returns:
        The path written.

    """
    name = CATALOG_FILES["orders"]
    doc = load_registry(project_root, name)["_doc"]
    orders = [order.model_dump(mode="json") for order in catalog.orders]
    path = registry_path(project_root, name)
    text = json.dumps({"_doc": doc, "orders": orders}, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")
    return path
