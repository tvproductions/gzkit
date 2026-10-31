"""``gz wp dispatch``, ``block`` and ``unblock``: the run's verbs (RO-14 tranche 1).

The bound itself is pinned in `tests/test_work_package_run.py`. These tests pin
the operator-facing surface: a refusal exits 3 and books nothing, and a human-act
flag is never defaulted.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.work_package_ledger import WorkPackageLedgerError
from tests.commands.common import CliRunner, _quick_init

_PACKAGE = "WP-01-loop"


def _seed_store() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    record = {
        "id": _PACKAGE,
        "kind": "repair",
        "outcome": None,
        "issues": [1200],
        "lane": "lite",
        "aliases": [],
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "NA",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }
    for kind, entries in (
        ("families", []),
        ("outcomes", []),
        ("reqs", []),
        ("externals", []),
        ("work_packages", [record]),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _rows(kind: str) -> list[dict]:
    text = (Path.cwd() / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row.get("event") == kind]


class TestRunVerbs(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_store()
        for args in (
            ["initiate", _PACKAGE, "--operator-text", "go"],
            ["freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e"],
            ["commence", _PACKAGE, "--evidence", "e"],
        ):
            result = self.runner.invoke(main, ["wp", *args])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def _dispatch(self, role: str, issue: str = "1200") -> int:
        args = ["wp", "dispatch", _PACKAGE, "--role", role, "--model", "m", "--issue", issue]
        return self.runner.invoke(main, args).exit_code

    def _block(self) -> int:
        args = ["wp", "block", _PACKAGE, "--reason", "r", "--next-action", "a"]
        return self.runner.invoke(main, args).exit_code

    def test_the_cycle_past_the_bound_exits_3_and_books_nothing(self) -> None:
        for role in ("Implementer", "SpecReviewer") * 3:
            self.assertEqual(self._dispatch(role), 0)
        booked = len(_rows("work_package_dispatched"))
        self.assertEqual(self._dispatch("Implementer"), 3)
        self.assertEqual(len(_rows("work_package_dispatched")), booked)

    def test_a_block_records_the_count_and_an_unblock_clears_it(self) -> None:
        self.assertEqual(self._dispatch("Implementer"), 0)
        self.assertEqual(self._block(), 0)
        self.assertEqual(_rows("work_package_blocked")[0]["fix_cycles"], {"#1200": 0})
        self.assertEqual(self._dispatch("SpecReviewer"), 3)
        args = ["wp", "unblock", _PACKAGE, "--ruling", "go on", "--operator", "g0"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 0)
        self.assertEqual(_rows("work_package_unblocked")[0]["ruling"], "go on")
        self.assertEqual(self._dispatch("SpecReviewer"), 0)

    def test_the_operator_is_never_defaulted(self) -> None:
        self.assertEqual(self._block(), 0)
        args = ["wp", "unblock", _PACKAGE, "--ruling", "go on"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 2)

    def test_an_issue_the_package_does_not_carry_is_a_refusal(self) -> None:
        self.assertEqual(self._dispatch("Implementer", "9"), 3)

    def test_the_exit_and_req_flags_reach_the_ledger(self) -> None:
        for role in ("Implementer", "SpecReviewer") * 3:
            self.assertEqual(self._dispatch(role), 0)
        self.assertEqual(self._block(), 0)
        args = ["wp", "unblock", _PACKAGE, "--ruling", "hold", "--operator", "g0", "--exit", "hold"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 0)
        self.assertEqual(_rows("work_package_unblocked")[0]["exit_taken"], "hold")

    def test_the_req_flags_reach_their_requests(self) -> None:
        with patch("gzkit.commands.wp.record_work_package_dispatch") as dispatch:
            dispatch.side_effect = WorkPackageLedgerError("stop")
            args = ["wp", "dispatch", _PACKAGE, "--role", "Implementer", "--model", "m"]
            self.runner.invoke(main, [*args, "--req", "REQ-1"])
        self.assertEqual(dispatch.call_args.args[2].req, "REQ-1")
        with patch("gzkit.commands.wp.record_work_package_unblock") as unblock:
            unblock.side_effect = WorkPackageLedgerError("stop")
            args = ["wp", "unblock", _PACKAGE, "--ruling", "r", "--operator", "g0"]
            self.runner.invoke(main, [*args, "--exit", "reopen", "--req", "REQ-1"])
        self.assertEqual(unblock.call_args.args[2].req, "REQ-1")

    def test_a_frozen_package_takes_no_new_issue(self) -> None:
        with patch("gzkit.commands.wp.tag_issues") as tag:
            result = self.runner.invoke(main, ["wp", "attach", _PACKAGE, "--issue", "1300"])
        self.assertEqual(result.exit_code, 3)
        tag.assert_not_called()

    def test_an_unknown_package_exits_1(self) -> None:
        args = ["wp", "block", "WP-99-none", "--reason", "r", "--next-action", "a"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 1)

    def test_show_lists_the_run_in_the_history(self) -> None:
        self.assertEqual(self._dispatch("Implementer"), 0)
        result = self.runner.invoke(main, ["wp", "show", _PACKAGE, "--json"])
        events = [row["event"] for row in json.loads(result.output)["history"]]
        self.assertIn("work_package_dispatched", events)


if __name__ == "__main__":
    unittest.main()
