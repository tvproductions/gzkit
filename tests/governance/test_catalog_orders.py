"""The order record in the catalog: RP-12 O2 task 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: an order is
`ORD-<NN>-<slug>`, one grammar for both kinds, its kind read from its package
(ruling 43); the catalog's record is thin, holding its id, its package, its
aliases, its purpose and its procedure and no REQ list, since the `frozen`
event is the binding (ruling 46); a delivery package keeps its five states
until RP-14 moves construction onto the order (ruling 44).
"""

import json
import unittest

from pydantic import ValidationError as PydanticValidationError

from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.models.catalog import Order, load_catalog
from gzkit.order_store import next_order_id
from gzkit.registries import RegistryError
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
        self.write(
            "work_packages",
            [_wp("WP-01-x"), _wp("WP-02-d", "delivery"), _wp("WP-03-y", issues=[7])],
        )

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
        """The series compares numbers, so ORD-001 reuses ORD-01's number."""
        for second in ("ORD-01-a", "ORD-01-other", "ORD-001-b"):
            with self.subTest(second=second):
                self.write("orders", [_order("ORD-01-a"), _order(second)])
                self.assertEqual(self.fields(), ["orders"])

    def test_an_alias_is_unique_within_its_package(self):
        """Ruling 49: two orders of one package may not share an alias."""
        self.write(
            "orders", [_order("ORD-01-a", aliases=["O2"]), _order("ORD-02-b", aliases=["O2"])]
        )
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["orders"])
        self.assertIn("ruling 49", errors[0].message)

    def test_orders_of_two_packages_may_share_an_alias(self):
        """Ruling 49: a specification's short name numbers the orders of one package."""
        self.write(
            "orders",
            [_order("ORD-01-a", aliases=["O2"]), _order("ORD-02-b", "WP-03-y", aliases=["O2"])],
        )
        self.assertEqual(audit_catalog(self.root), [])

    def test_an_alias_is_never_an_order_or_package_id(self):
        for alias in ("ORD-02-b", "WP-03-y"):
            with self.subTest(alias=alias):
                self.write("orders", [_order("ORD-01-a", aliases=[alias])])
                self.assertEqual(self.fields(), ["orders"])

    def test_an_alias_is_one_word(self):
        for alias in ("", "O 2", "-O2"):
            with self.subTest(alias=alias), self.assertRaises(PydanticValidationError):
                Order.model_validate(_order("ORD-01-a", aliases=[alias]))

    def test_a_missing_store_is_a_tree_defect(self):
        """A registry the tree lacks fails the scope rather than reading as empty (GHI #1067)."""
        (self.root / "data" / "catalog" / "orders.json").unlink()
        self.assertEqual(self.fields(), ["orders"])

    def test_a_reader_of_a_catalog_missing_a_file_is_told_the_repair(self):
        """A project initialized before a catalog file landed is pointed at `gz init`'s repair."""
        (self.root / "data" / "catalog" / "orders.json").unlink()
        with self.assertRaises(RegistryError) as caught:
            load_catalog(self.root)
        self.assertIn("data/catalog/orders.json", str(caught.exception))
        self.assertIn("uv run gz init", str(caught.exception))


class TestBookedOrders(_Tree):
    """Ruling 52: an order is born on the ledger, so the store keeps every order it names."""

    def setUp(self) -> None:
        super().setUp()
        self.write("work_packages", [_wp("WP-01-x")])

    def book(self, to_state: str, **fields: object) -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "order_transitioned",
            "id": "ORD-07-gone",
            "ts": "2026-11-07T08:00:00+00:00",
            "order": "ORD-07-gone",
            "work_package": "WP-01-x",
            "to_state": to_state,
            "evidence": "evt-1",
            **fields,
        }
        ledger = self.root / ".gzkit" / "ledger.jsonl"
        ledger.parent.mkdir(exist_ok=True)
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")

    def test_an_order_the_ledger_names_stays_in_the_store(self):
        self.book("opened", operator_text="open it")
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["orders"])
        self.assertIn("ORD-07-gone", errors[0].message)
        self.write("orders", [_order("ORD-07-gone")])
        self.assertEqual(audit_catalog(self.root), [])

    def test_a_package_an_order_names_stays_in_the_store(self):
        """RO-5 ruling 6: a package the ledger names, by an order's event too, is kept."""
        self.book("opened", operator_text="open it")
        self.write("work_packages", [])
        errors = [e for e in audit_catalog(self.root) if e.field == "work_packages"]
        self.assertEqual(len(errors), 1)
        self.assertIn("WP-01-x", errors[0].message)

    def test_a_req_an_orders_freeze_names_stays_in_the_store(self):
        """Requirements model § 2: a REQ id the ledger names is never minted again."""
        self.write("orders", [_order("ORD-07-gone")])
        self.book("frozen", baseline=[{"req": "REQ-9", "revision": 1}])
        errors = audit_catalog(self.root)
        self.assertEqual([e.field for e in errors], ["reqs"])
        self.assertIn("REQ-9", errors[0].message)

    def test_the_next_id_numbers_past_every_booked_order(self):
        """Ruling 43: one series, never reused, even past an order the store has lost."""
        catalog = load_catalog(self.root)
        self.assertEqual(next_order_id(catalog, "next", {"ORD-07-gone"}), "ORD-08-next")
        self.assertEqual(next_order_id(catalog, "next", set()), "ORD-01-next")


class TestWorkPackageSeries(_Tree):
    """The work-package series compares numbers too, so WP-001 reuses WP-01's (RO-5 ruling 6)."""

    def test_a_padded_number_is_the_same_number(self):
        self.write("work_packages", [_wp("WP-01-a"), _wp("WP-001-b", issues=[7])])
        self.assertEqual(self.fields(), ["work_packages"])


if __name__ == "__main__":
    unittest.main()
