"""The order record in the catalog: RP-12 O2 task 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: an order is
`ORD-<NN>-<slug>`, one grammar for both kinds, its kind read from its package
(ruling 43); the catalog's record is thin, holding its id, its package, its
aliases, its purpose and its procedure and no REQ list, since the `frozen`
event is the binding (ruling 46); a delivery package keeps its five states
until RP-14 moves construction onto the order (ruling 44).
"""

import unittest

from pydantic import ValidationError as PydanticValidationError

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.models.catalog import Order, load_catalog
from tests.governance.test_catalog import _Tree, _wp


def _order(order_id: str, work_package: str = "WP-01-x", **fields: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": order_id,
        "work_package": work_package,
        "aliases": [],
        "purpose": "Restore the dispatch stamp's import.",
        "procedure": "NA",
    }
    return {**base, **fields}


class TestOrderModel(unittest.TestCase):
    """Rulings 43 and 46: the id's grammar, and a record that carries no binding or state."""

    def test_the_id_is_the_sequential_area_free_grammar(self):
        self.assertEqual(Order.model_validate(_order("ORD-01-stamp")).id, "ORD-01-stamp")
        for order_id in ("WO-01-stamp", "ORD-1-stamp", "ORD-01", "ORD-01-Stamp", "O2", "RO-12"):
            with self.subTest(order_id=order_id), self.assertRaises(PydanticValidationError):
                Order.model_validate(_order(order_id))

    def test_the_record_names_a_work_package_by_its_id(self):
        with self.assertRaises(PydanticValidationError):
            Order.model_validate(_order("ORD-01-x", work_package="RP-12"))

    def test_the_record_carries_no_kind_binding_or_state(self):
        """The kind is the package's (43), the binding the freeze's (46), the state the ledger's."""
        for field, value in (("kind", "repair"), ("reqs", ["REQ-1"]), ("state", "frozen")):
            with self.subTest(field=field), self.assertRaises(PydanticValidationError):
                Order.model_validate({**_order("ORD-01-x"), field: value})

    def test_purpose_and_procedure_are_never_empty(self):
        for field in ("purpose", "procedure"):
            with self.subTest(field=field), self.assertRaises(PydanticValidationError):
                Order.model_validate({**_order("ORD-01-x"), field: ""})


class TestOrderStore(_Tree):
    """`gz validate --catalog` over `data/catalog/orders.json`."""

    def setUp(self) -> None:
        super().setUp()
        self.write("work_packages", [_wp("WP-01-x"), _wp("WP-02-d", "delivery")])

    def test_an_order_on_a_repair_package_the_catalog_holds_passes(self):
        self.write("orders", [_order("ORD-01-a"), _order("ORD-02-b", aliases=["O2"])])
        self.assertEqual(audit_catalog(self.root), [])
        catalog = load_catalog(self.root)
        self.assertEqual([order.id for order in catalog.orders], ["ORD-01-a", "ORD-02-b"])

    def test_an_order_names_a_package_the_catalog_holds(self):
        self.write("orders", [_order("ORD-01-a", work_package="WP-09-gone")])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["orders"])
        self.assertIn("WP-09-gone", errors[0].message)

    def test_an_order_on_a_delivery_package_waits_for_rp14(self):
        self.write("orders", [_order("ORD-01-a", work_package="WP-02-d")])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["orders"])
        self.assertIn("ruling 44", errors[0].message)

    def test_an_id_or_its_number_is_never_reused(self):
        for second in ("ORD-01-a", "ORD-01-other"):
            with self.subTest(second=second):
                self.write("orders", [_order("ORD-01-a"), _order(second)])
                self.assertEqual(self.fields(), ["orders"])

    def test_an_alias_names_one_order(self):
        self.write(
            "orders", [_order("ORD-01-a", aliases=["O2"]), _order("ORD-02-b", aliases=["O2"])]
        )
        self.assertEqual(self.fields(), ["orders"])

    def test_a_missing_store_is_a_tree_defect(self):
        """A registry the tree lacks fails the scope rather than reading as empty (GHI #1067)."""
        (self.root / "data" / "catalog" / "orders.json").unlink()
        self.assertEqual(self.fields(), ["orders"])


if __name__ == "__main__":
    unittest.main()
