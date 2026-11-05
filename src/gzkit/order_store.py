"""The order store's one writer (RP-12 O2 task 1).

`data/catalog/orders.json` is edited only through `gz wp order` (RP-12 ruling
47), and this module is what it calls. Every write is checked against the rules
`gz validate --catalog` reads (`order_findings`) before it reaches the file, so a
verb can never leave the store in a state the scope refuses.
"""

import json
from typing import TYPE_CHECKING

from gzkit.governance.trust_audits.catalog import order_findings
from gzkit.models.catalog import CATALOG_FILES, Catalog, Order
from gzkit.registries import load_registry, registry_path

if TYPE_CHECKING:
    from pathlib import Path


class OrderStoreError(ValueError):
    """A store edit RP-12's rulings refuse; nothing was written."""


def _number(order_id: str) -> int:
    return int(order_id.split("-")[1])


def next_order_id(catalog: Catalog, slug: str) -> str:
    """Return the next id in the one series (ruling 43): the highest number plus one.

    Returns:
        `ORD-<NN>-<slug>`, numbered past every order the store holds.

    """
    numbers = [_number(order.id) for order in catalog.orders]
    return f"ORD-{max(numbers, default=0) + 1:02d}-{slug}"


def stage_order(catalog: Catalog, order: Order) -> Catalog:
    """Return the catalog with the order added or replaced, refusing a breach.

    Returns:
        The catalog as it would read once written.

    Raises:
        OrderStoreError: The edit breaks a rule `gz validate --catalog` reads.

    """
    others = tuple(held for held in catalog.orders if held.id != order.id)
    ordered = tuple(sorted((*others, order), key=lambda held: _number(held.id)))
    staged = catalog.model_copy(update={"orders": ordered})
    findings = order_findings(staged)
    if findings:
        raise OrderStoreError(" ".join(finding.message for finding in findings))
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
