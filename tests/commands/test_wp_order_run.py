"""``gz wp dispatch``, ``block`` and ``unblock`` with ``--order``: RP-12 O2 task 3, act 3.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings 57 and 59: the verbs
take ``--order``, a dispatch on it targets only a REQ its freeze holds, and a
block on it holds that order alone until the operator's ruling lifts it. A
refusal exits 3 and books nothing; a wrong flag combination exits 2.
"""

import json
import unittest
from pathlib import Path
from typing import Any

from gzkit.cli import main
from tests.commands.test_wp_order import _ledger_rows, _OrderCase

_PACKAGE = "WP-01-stamp"
_ORDER = "ORD-01-import"


class _CommencedOrder(_OrderCase):
    """One repair REQ, frozen into ORD-01-import, which is commenced."""

    def setUp(self) -> None:
        super().setUp()
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["modules"] = ["src/stamp.py"]
        store.write_text(json.dumps(held), encoding="utf-8")
        Path("src").mkdir(exist_ok=True)
        Path("src/stamp.py").write_text("STAMP = 1\n", encoding="utf-8")
        self.wp(
            "req", "new", _PACKAGE, "--statement", "The stamp imports again.", "--criterion",
            "an import|ok|a test", "--kind", "BEHAVIOR", "--problem-report", "1301",
        )  # fmt: skip
        self.new("import")
        self.gz(
            "freeze", _ORDER, "--baseline", "REQ-1@1", "--risk-note", "Touches the hook.",
            "--review-receipt", "review-01", "--evidence", "E",
        )  # fmt: skip
        self.gz("commence", _ORDER, "--evidence", "tags")

    def wp(self, *args: str, code: int = 0) -> str:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, code, result.output)
        return result.output if code == 0 else " ".join(result.output.split())

    def dispatch(self, *extra: str, code: int = 0) -> str:
        words = ("--role", "Implementer", "--model", "sonnet", "--req", "REQ-1")
        return self.wp("dispatch", _PACKAGE, "--order", _ORDER, *words, *extra, code=code)

    def rows(self, event: str) -> list[dict[str, Any]]:
        return [row for row in _ledger_rows() if row["event"] == event]


class DispatchOrderCli(_CommencedOrder):
    def test_dispatch_on_the_order_books_its_frozen_subject(self) -> None:
        payload = json.loads(self.dispatch("--json"))
        self.assertEqual(
            (payload["order"], payload["subject"], payload["work_package"]),
            (_ORDER, "REQ-1@1", _PACKAGE),
        )
        self.assertEqual(len(self.rows("work_package_dispatched")), 1)

    def test_a_req_outside_the_orders_freeze_exits_3_and_books_nothing(self) -> None:
        output = self.wp(
            "dispatch", _PACKAGE, "--order", _ORDER, "--role", "Implementer", "--model", "m",
            "--req", "REQ-2", code=3,
        )  # fmt: skip
        self.assertIn("ruling 57", output)
        self.assertEqual(self.rows("work_package_dispatched"), [])

    def test_void_takes_no_order(self) -> None:
        self.wp("dispatch", _PACKAGE, "--void", "D-0123456789abcdef", "--reason", "r",
                "--order", _ORDER, code=2)  # fmt: skip


class BlockOrderCli(_CommencedOrder):
    def test_block_holds_the_order_and_unblock_lifts_it(self) -> None:
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "R", "--next-action", "rule")
        self.assertEqual(self.rows("work_package_blocked")[-1]["order"], _ORDER)
        self.assertIn("blocked", self.dispatch(code=3))
        payload = json.loads(
            self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "go", "--operator", "g0",
                    "--json")
        )  # fmt: skip
        self.assertEqual((payload["event"]["order"], payload["blocked"]), (_ORDER, False))
        self.dispatch()

    def test_the_json_reports_the_orders_block_not_the_packages(self) -> None:
        self.wp("block", _PACKAGE, "--reason", "R", "--next-action", "rule")
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "R", "--next-action", "rule")
        payload = json.loads(
            self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "go", "--operator", "g0",
                    "--json")
        )  # fmt: skip
        self.assertFalse(payload["blocked"])

    def test_an_unblock_on_the_package_leaves_the_orders_block(self) -> None:
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "R", "--next-action", "rule")
        self.wp("unblock", _PACKAGE, "--ruling", "go", "--operator", "g0", code=3)
        self.assertEqual(len(self.rows("work_package_unblocked")), 0)


class OrderRunOutputContract(_CommencedOrder):
    """The human lines name the order, as the manpage examples show them."""

    # output-contract: each verb's line names the order it acted on.
    def test_each_verb_names_the_order(self) -> None:
        held = f"order {_ORDER} of {_PACKAGE}"
        self.assertIn(f"REQ-1@1 of {held}", " ".join(self.dispatch().split()))
        blocked = self.wp(
            "block", _PACKAGE, "--order", _ORDER, "--reason", "R", "--next-action", "rule"
        )
        self.assertIn(f"Blocked {held} on the operator", blocked)
        self.assertIn(f"{held} (repair), state: commenced", self.wp("runs"))
        unblocked = self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "go",
                            "--operator", "g0")  # fmt: skip
        self.assertIn(f"Unblocked {held}.", unblocked)


if __name__ == "__main__":
    unittest.main()
