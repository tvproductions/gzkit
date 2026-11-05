"""``gz wp order new`` and ``show``: RP-12 O2 task 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: `gz wp order new`
writes an order's record with the next `ORD-<NN>-<slug>` (rulings 43, 47), a thin
record naming its package, aliases, purpose and procedure (ruling 46), on a
repair package only until RP-14 (ruling 44). A refusal exits 3 and writes
nothing; an unknown package or order exits 1.
"""

import json
import unittest
from pathlib import Path
from typing import Any

from gzkit.cli import main
from gzkit.governance.trust_audits.catalog import audit_catalog
from tests.commands.common import CliRunner, _quick_init


def _package(wp_id: str, kind: str, issues: list[int]) -> dict[str, object]:
    return {
        "id": wp_id,
        "kind": kind,
        "outcome": "H1" if kind == "delivery" else None,
        "issues": issues,
        "lane": None if kind == "delivery" else "lite",
        "aliases": [],
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "NA",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }


_OUTCOME = {
    "code": "H1",
    "statement": "The operator can resume a session.",
    "owner": "g0",
    "user_facing": False,
    "governed_by": [],
    "depends_on": [],
    "feature": None,
    "retired": False,
}


def _seed_catalog() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    family = {"code": "H", "band": "product", "name": "Session", "scope": "One."}
    packages = [_package("WP-01-stamp", "repair", [1301]), _package("WP-02-resume", "delivery", [])]
    for kind, entries in (
        ("families", [family]),
        ("outcomes", [_OUTCOME]),
        ("reqs", []),
        ("externals", []),
        ("work_packages", packages),
        ("orders", []),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _orders() -> list[dict[str, Any]]:
    text = (Path("data") / "catalog" / "orders.json").read_text(encoding="utf-8")
    return json.loads(text)["orders"]


class _OrderCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()

    def gz(self, *args: str, code: int = 0) -> str:
        result = self.runner.invoke(main, ["wp", "order", *args])
        self.assertEqual(result.exit_code, code, result.output)
        return result.output

    def new(self, slug: str, *extra: str, package: str = "WP-01-stamp", code: int = 0) -> str:
        return self.gz(
            "new", package, "--slug", slug, "--purpose", "Restore it.", *extra, code=code
        )


class OrderNewTests(_OrderCase):
    def test_new_numbers_one_series_and_the_store_passes_its_scope(self) -> None:
        self.new("import", "--alias", "O2")
        self.new("matcher", "--procedure", "Task one, then task two.")
        orders = _orders()
        self.assertEqual([order["id"] for order in orders], ["ORD-01-import", "ORD-02-matcher"])
        self.assertEqual(orders[0]["aliases"], ["O2"])
        self.assertEqual(orders[0]["procedure"], "NA")
        self.assertEqual(orders[1]["procedure"], "Task one, then task two.")
        self.assertEqual({order["work_package"] for order in orders}, {"WP-01-stamp"})
        self.assertEqual([e for e in audit_catalog(Path.cwd()) if e.field == "orders"], [])

    def test_an_order_on_a_delivery_package_is_refused_and_nothing_written(self) -> None:
        output = self.new("resume", package="WP-02-resume", code=3)
        self.assertIn("ruling 44", output)
        self.assertEqual(_orders(), [])

    def test_a_repeated_alias_is_refused_and_nothing_written(self) -> None:
        self.new("import", "--alias", "O2")
        self.new("matcher", "--alias", "O2", code=3)
        self.assertEqual([order["id"] for order in _orders()], ["ORD-01-import"])

    def test_a_slug_outside_the_grammar_is_refused(self) -> None:
        self.new("Import", code=3)
        self.assertEqual(_orders(), [])

    def test_an_unknown_package_exits_1_and_nothing_written(self) -> None:
        self.new("import", package="WP-09-ghost", code=1)
        self.assertEqual(_orders(), [])


class OrderShowTests(_OrderCase):
    def test_show_reads_the_kind_from_the_package(self) -> None:
        self.new("import", "--alias", "O2")
        shown = json.loads(self.gz("show", "ORD-01-import", "--json"))
        self.assertEqual(shown["record"]["id"], "ORD-01-import")
        self.assertEqual(shown["record"]["work_package"], "WP-01-stamp")
        self.assertEqual(shown["kind"], "repair")

    def test_an_unknown_order_exits_1(self) -> None:
        self.gz("show", "ORD-09-ghost", code=1)


if __name__ == "__main__":
    unittest.main()
