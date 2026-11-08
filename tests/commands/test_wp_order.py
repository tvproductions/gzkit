"""``gz wp order new`` and ``show``: RP-12 O2 task 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: `gz wp order new`
writes an order's record with the next `ORD-<NN>-<slug>` (rulings 43, 47), a thin
record naming its package, aliases, purpose and procedure (ruling 46), on a
repair package only until RP-14 (ruling 44). A refusal exits 3 and writes
nothing; an unknown package or order exits 1.
"""

import argparse
import json
import shlex
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from gzkit.cli import main
from gzkit.cli.main import _build_parser
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
    packages = [
        _package("WP-01-stamp", "repair", [1301]),
        _package("WP-02-resume", "delivery", []),
        _package("WP-03-idle", "repair", [1302]),
    ]
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


def _ledger_rows() -> list[dict[str, Any]]:
    text = (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


class _OrderCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()
        result = self.runner.invoke(
            main, ["wp", "initiate", "WP-01-stamp", "--operator-text", "open it"]
        )
        self.assertEqual(result.exit_code, 0, result.output)

    def gz(self, *args: str, code: int = 0) -> str:
        result = self.runner.invoke(main, ["wp", "order", *args])
        self.assertEqual(result.exit_code, code, result.output)
        # The console wraps long lines; a refusal's words are read unwrapped.
        return result.output if code == 0 else " ".join(result.output.split())

    def new(self, slug: str, *extra: str, package: str = "WP-01-stamp", code: int = 0) -> str:
        words = ("--operator-text", "open it")
        return self.gz(
            "new", package, "--slug", slug, "--purpose", "Restore it.", *words, *extra, code=code
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

    def test_new_numbers_past_the_highest_held_not_the_count(self) -> None:
        catalog = Path("data") / "catalog" / "orders.json"
        held = {
            "id": "ORD-05-held",
            "work_package": "WP-01-stamp",
            "aliases": [],
            "purpose": "Held.",
            "procedure": "NA",
        }
        catalog.write_text(json.dumps({"_doc": "Fixture.", "orders": [held]}), encoding="utf-8")
        self.new("next")
        self.assertEqual([order["id"] for order in _orders()], ["ORD-05-held", "ORD-06-next"])

    def test_new_books_the_orders_opening_on_the_operators_words(self) -> None:
        """Ruling 52: the order is born on the ledger, opened with the operator's words."""
        self.new("import")
        rows = [r for r in _ledger_rows() if r["event"] == "order_transitioned"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            (rows[0]["order"], rows[0]["work_package"], rows[0]["to_state"]),
            ("ORD-01-import", "WP-01-stamp", "opened"),
        )
        self.assertEqual(rows[0]["operator_text"], "open it")

    def test_new_without_the_operators_words_is_refused_and_nothing_written(self) -> None:
        before = _ledger_rows()
        args = ("new", "WP-01-stamp", "--slug", "x", "--purpose", "P.", "--operator-text", " ")
        output = self.gz(*args, code=3)
        self.assertIn("--operator-text", output)
        self.assertIn("ruling 52", output)
        self.assertEqual((_orders(), _ledger_rows()), ([], before))

    def test_new_numbers_past_an_order_the_ledger_names(self) -> None:
        """Rulings 43 and 52: a booked id is never reused, even once its record is lost."""
        self.new("import")
        catalog = Path("data") / "catalog" / "orders.json"
        catalog.write_text(json.dumps({"_doc": "Fixture.", "orders": []}), encoding="utf-8")
        output = self.new("next", code=3)
        self.assertIn("ORD-01-import", output)
        self.assertIn("gz validate --catalog", output)

    def test_a_failed_store_write_leaves_the_opening_booked_and_refuses_later_writes(
        self,
    ) -> None:
        """Ruling 70: the opening is booked first, so a lost record is refused, never silent."""
        with patch("gzkit.commands.wp_order.write_orders", side_effect=OSError("disk full")):
            result = self.runner.invoke(
                main,
                ["wp", "order", "new", "WP-01-stamp", "--slug", "import", "--purpose", "P.",
                 "--operator-text", "open it"],
            )  # fmt: skip
        self.assertNotEqual(result.exit_code, 0)
        opened = [r["order"] for r in _ledger_rows() if r["event"] == "order_transitioned"]
        self.assertEqual((opened, _orders()), (["ORD-01-import"], []))
        output = self.new("next", code=3)
        self.assertIn("Orders ORD-01-import have ledger events but no record", output)

    def test_a_refused_order_books_no_opening(self) -> None:
        before = _ledger_rows()
        self.new("resume", package="WP-02-resume", code=3)
        self.new("idle", package="WP-03-idle", code=3)
        self.assertEqual(_ledger_rows(), before)

    def test_an_order_on_a_delivery_package_is_refused_and_nothing_written(self) -> None:
        output = self.new("resume", package="WP-02-resume", code=3)
        self.assertIn("ruling 44", output)
        self.assertEqual(_orders(), [])

    def test_a_package_not_initiated_or_closed_takes_no_order(self) -> None:
        """Rulings 2 and 44: the package is open while its orders are found."""
        output = self.new("idle", package="WP-03-idle", code=3)
        self.assertIn("not initiated", output)
        self.assertIn("gz wp initiate WP-03-idle", output)
        with patch("gzkit.commands.wp_order.work_package_state", return_value="closed"):
            output = self.new("late", code=3)
        self.assertIn("is closed", output)
        self.assertEqual(_orders(), [])

    def test_a_repeated_alias_in_one_package_is_refused_and_nothing_written(self) -> None:
        self.new("import", "--alias", "O2")
        output = self.new("matcher", "--alias", "O2", code=3)
        self.assertIn("ruling 49", output)
        self.assertEqual([order["id"] for order in _orders()], ["ORD-01-import"])

    def test_a_refusal_names_the_flag_and_the_call_to_rerun(self) -> None:
        """Guardrail prose: what failed by the flag typed, why, and the runnable next step."""
        for extra, flag in (
            (("--slug", "Import"), "--slug 'Import'"),
            (("--procedure", ""), "--procedure"),
        ):
            with self.subTest(flag=flag):
                args = ("new", "WP-01-stamp", "--purpose", "Restore it.", "--operator-text", "go")
                args += extra if extra[0] == "--slug" else ("--slug", "ok", *extra)
                output = self.gz(*args, code=3)
                self.assertIn(flag, output)
                self.assertIn("Nothing was written", output)
                self.assertIn("uv run gz wp order new", output)
                self.assertIn("--operator-text <words>", output)
                self.assertNotIn("errors.pydantic.dev", output)
                self.assertNotIn("Correct the file", output)
        self.assertEqual(_orders(), [])

    def test_an_unknown_package_exits_1_and_nothing_written(self) -> None:
        self.new("import", package="WP-09-ghost", code=1)
        self.assertEqual(_orders(), [])


class OrderLifecycleTests(_OrderCase):
    """`gz wp order freeze` and `commence` (RP-12 O2 task 3, rulings 53 and 56)."""

    def setUp(self) -> None:
        super().setUp()
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["modules"] = ["src/stamp.py"]
        store.write_text(json.dumps(held), encoding="utf-8")
        Path("src").mkdir(exist_ok=True)
        Path("src/stamp.py").write_text("STAMP = 1\n", encoding="utf-8")
        result = self.runner.invoke(
            main,
            [
                "wp",
                "req",
                "new",
                "WP-01-stamp",
                "--statement",
                "The stamp imports again.",
                "--criterion",
                "an import|ok|a test",
                "--kind",
                "BEHAVIOR",
                "--problem-report",
                "1301",
            ],
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.new("import")

    def freeze(self, *extra: str, order: str = "ORD-01-import", code: int = 0) -> str:
        args = (
            "--risk-note",
            "Touches the hook.",
            "--review-receipt",
            "review-01",
            "--evidence",
            "E",
        )
        return self.gz("freeze", order, "--baseline", "REQ-1@1", *args, *extra, code=code)

    def moves(self) -> list[dict[str, Any]]:
        return [r for r in _ledger_rows() if r["event"] == "order_transitioned"]

    def test_freeze_then_commence_book_one_step_each(self) -> None:
        self.assertIn("ORD-01-import: opened -> frozen", self.freeze())
        commenced = self.gz("commence", "ORD-01-import", "--evidence", "tags")
        self.assertIn("ORD-01-import: frozen -> commenced", commenced)
        self.assertIn("airlock in:", commenced)  # ruling 65: the order crosses inward
        moves = self.moves()
        self.assertEqual([m["to_state"] for m in moves], ["opened", "frozen", "commenced"])
        self.assertEqual(moves[1]["baseline"], [{"req": "REQ-1", "revision": 1}])
        self.assertEqual(moves[1]["modules"], ["src/stamp.py"])
        self.assertEqual(moves[1]["risk_note"], "Touches the hook.")

    def test_the_freeze_approves_the_packages_planned_alterations(self) -> None:
        """Ruling 63: `--approve-alteration` names each alteration due at this freeze."""
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        alteration = {
            "id": "ALT-1",
            "description": "A remodel.",
            "configuration_change": "replaced",
        }
        held["work_packages"][0]["alterations"] = [alteration]
        store.write_text(json.dumps(held), encoding="utf-8")
        before = _ledger_rows()
        refused = self.freeze(code=3)
        self.assertIn("ruling 63", refused)
        self.assertIn("[--approve-alteration <id>]", refused)  # the re-run names the fix
        self.assertEqual(_ledger_rows(), before)
        self.freeze("--approve-alteration", "ALT-1")
        self.assertEqual(self.moves()[-1]["approved_alterations"], ["ALT-1"])

    def test_commence_before_the_freeze_is_refused_and_nothing_written(self) -> None:
        before = _ledger_rows()
        output = self.gz("commence", "ORD-01-import", "--evidence", "tags", code=3)
        self.assertIn("allows frozen", output)
        self.assertIn("Nothing was written", output)
        self.assertEqual(_ledger_rows(), before)

    def test_a_baseline_entry_not_req_at_revision_is_refused(self) -> None:
        before = _ledger_rows()
        output = self.gz(
            "freeze",
            "ORD-01-import",
            "--baseline",
            "REQ-1",
            "--risk-note",
            "r",
            "--review-receipt",
            "x",
            "--evidence",
            "E",
            code=3,
        )
        self.assertIn("REQ-<n>@<revision>", output)
        self.assertEqual(_ledger_rows(), before)

    def test_a_freeze_the_writer_refuses_names_the_ruling_and_writes_nothing(self) -> None:
        before = _ledger_rows()
        output = self.gz(
            "freeze",
            "ORD-01-import",
            "--baseline",
            "REQ-1@2",
            "--risk-note",
            "r",
            "--review-receipt",
            "x",
            "--evidence",
            "E",
            code=3,
        )
        self.assertIn("is not a REQ the catalog holds", output)
        self.assertIn("uv run gz wp order freeze", output)
        self.assertEqual(_ledger_rows(), before)

    def test_a_package_with_no_footprint_cannot_seal_one(self) -> None:
        """Ruling 56: the freeze seals the package's footprint, so it must hold one."""
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["modules"] = []
        store.write_text(json.dumps(held), encoding="utf-8")
        before = _ledger_rows()
        output = self.freeze(code=3)
        self.assertIn("declares no footprint", output)
        self.assertEqual(_ledger_rows(), before)

    def test_the_sealed_footprint_drops_no_path(self) -> None:
        self.freeze()
        result = self.runner.invoke(
            main,
            [
                "wp",
                "change",
                "WP-01-stamp",
                "--rung",
                "change_order",
                "--approver",
                "operator",
                "--change",
                "Narrow it.",
                "--superseded",
                "src/stamp.py",
                "--work-stopped",
                "--drop-module",
                "src/stamp.py",
            ],
        )
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("ruling 56", " ".join(result.output.split()))

    def test_an_unknown_order_exits_1(self) -> None:
        self.gz("commence", "ORD-09-ghost", "--evidence", "tags", code=1)
        self.freeze(order="ORD-09-ghost", code=1)

    def test_show_prints_the_state_and_baseline_lines(self) -> None:
        # output-contract: the text form is the verb's human rendering.
        lines = self.gz("show", "ORD-01-import").splitlines()
        self.assertIn("  state: opened", lines)
        self.assertIn("  baseline: none", lines)
        self.freeze()
        lines = self.gz("show", "ORD-01-import").splitlines()
        self.assertIn("  state: frozen", lines)
        self.assertIn("  baseline: REQ-1@1", lines)

    def test_show_reads_the_state_and_baseline_from_the_ledger(self) -> None:
        self.assertEqual(json.loads(self.gz("show", "ORD-01-import", "--json"))["state"], "opened")
        self.freeze()
        shown = json.loads(self.gz("show", "ORD-01-import", "--json"))
        self.assertEqual(shown["state"], "frozen")
        self.assertEqual(shown["baseline"], {"REQ-1": 1})


class OrderShowTests(_OrderCase):
    def test_show_reads_the_kind_from_the_package(self) -> None:
        self.new("import", "--alias", "O2")
        shown = json.loads(self.gz("show", "ORD-01-import", "--json"))
        self.assertEqual(shown["record"]["id"], "ORD-01-import")
        self.assertEqual(shown["record"]["work_package"], "WP-01-stamp")
        self.assertEqual(shown["kind"], "repair")

    def test_show_prints_the_record_beside_its_package(self) -> None:
        # output-contract: the text form is the verb's human rendering.
        self.new("import", "--alias", "O2")
        lines = self.gz("show", "ORD-01-import").splitlines()
        self.assertEqual(lines[0], "ORD-01-import in WP-01-stamp (repair)")
        self.assertIn("  aliases: O2", lines)
        self.assertIn("  purpose: Restore it.", lines)

    def test_an_unknown_order_exits_1_naming_the_call_that_writes_one(self) -> None:
        output = self.gz("show", "ORD-09-ghost", code=1)
        self.assertIn("--operator-text <words>", output)


def _help_parser(parser: argparse.ArgumentParser, path: list[str]) -> argparse.ArgumentParser:
    """Walk the subparsers to the command ``path`` names.

    Returns:
        That command's parser.

    """
    for name in path:
        actions = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
        parser = actions[0].choices[name]
    return parser


class OrderEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        """The help's examples are runnable: each parses, every required flag present."""
        parser = _build_parser()
        examples = [
            line.strip()
            for args in (
                ["wp", "order"],
                ["wp", "order", "new"],
                ["wp", "order", "freeze"],
                ["wp", "order", "commence"],
            )
            for line in (_help_parser(parser, args).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        self.assertGreaterEqual(len(examples), 5)
        for example in examples:
            with self.subTest(example=example):
                parsed = parser.parse_args(shlex.split(example)[1:])
                self.assertTrue(callable(parsed.func))


if __name__ == "__main__":
    unittest.main()
