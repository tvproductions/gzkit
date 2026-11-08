"""``gz wp dispatch``, ``block`` and ``unblock``: the run's verbs (RO-14 tranche 1).

The bound itself is pinned in `tests/test_work_package_run.py`. These tests pin
the operator-facing surface: a refusal exits 3 and books nothing, and a human-act
flag is never defaulted.
"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV
from gzkit.work_package_ledger import WorkPackageLedgerError
from gzkit.work_package_run import read_dispatch_id
from tests.commands.test_wp_order_run import _CommencedOrder

_PACKAGE = "WP-01-stamp"
_ORDER = "ORD-01-import"
_ON_ORDER = ("--order", _ORDER)


_REAL_WRITE_TEXT = Path.write_text


def _refuse_marker_writes(path: Path, *args: object, **kwargs: object) -> int:
    """Stand in for a marker file that cannot be written, on any platform.

    Returns:
        What the real ``Path.write_text`` returns, for any other file.

    Raises:
        PermissionError: ``path`` is a pipeline marker.

    """
    if path.name.startswith(".pipeline-active"):
        message = f"Permission denied: {path}"
        raise PermissionError(message)
    return _REAL_WRITE_TEXT(path, *args, **kwargs)  # ty: ignore[invalid-argument-type]


def _rows(kind: str) -> list[dict]:
    text = (Path.cwd() / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row.get("event") == kind]


class _RunCase(_CommencedOrder):
    """A commenced order on a repair package, driven through the run's verbs."""

    def _dispatch(self, role: str, req: str = "REQ-1") -> int:
        args = ["wp", "dispatch", _PACKAGE, *_ON_ORDER, "--role", role, "--model", "m"]
        return self.runner.invoke(main, [*args, "--req", req]).exit_code

    def _block(self) -> int:
        args = ["wp", "block", _PACKAGE, *_ON_ORDER, "--reason", "r", "--next-action", "a"]
        return self.runner.invoke(main, args).exit_code


class TestTheRepairClose(_RunCase):
    """A repair package's close waits on its orders' Gate 5 (RP-12 rulings 76, 77)."""

    def _stop_and_close_the_order(self) -> None:
        """Stop the order by a terminate exit, accept it excused, close it through Gate 5."""
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self.assertEqual(self._dispatch(role), 0)
        self.assertEqual(self._block(), 0)
        for args in (
            ["wp", "unblock", _PACKAGE, *_ON_ORDER, "--ruling", "stop", "--operator", "g0",
             "--exit", "terminate"],
            ["wp", "order", "accept", _ORDER, "--evidence", "stopped"],
            ["wp", "order", "close", _ORDER, "--decision", "terminate", "--attestor", "g0",
             "--attestation-text", "the stop stands", "--evidence", "gate 5"],
        ):  # fmt: skip
            result = self.runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_a_repair_package_closes_only_once_its_orders_have_closed(self) -> None:
        """RP-12 ruling 76: its Gate 5 is its orders', so it carries no decision."""
        close = ["wp", "close", _PACKAGE, "--attestor", "g0", "--residual-risk", "R"]
        result = self.runner.invoke(main, [*close, "--evidence", "E"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn(f"{_ORDER} still stands open", " ".join(result.output.split()))
        self._stop_and_close_the_order()
        decided = self.runner.invoke(main, [*close, "--decision", "proceed", "--evidence", "E"])
        self.assertEqual(decided.exit_code, 3, msg=decided.output)
        result = self.runner.invoke(main, [*close, "--evidence", "E", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(json.loads(result.output)["order_decisions"], {_ORDER: "terminate"})

    def test_the_repair_close_prints_its_orders_decisions_and_holds(self) -> None:
        """Ruling 78: the repair package's close shows what holds, as order show does."""
        self._stop_and_close_the_order()
        close = ["wp", "close", _PACKAGE, "--attestor", "g0", "--residual-risk", "R"]
        result = self.runner.invoke(main, [*close, "--evidence", "E"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        # output-contract: the text form names each order's decision and the holds
        lines = result.output.splitlines()
        self.assertIn(f"  orders: {_ORDER} terminate", lines)
        self.assertIn("  holds: none", lines)

    def test_gate_5_on_a_package_refuses_a_subagents_call(self) -> None:
        """RP-12 ruling 77: Gate 5 is the operator's act, at the package as at the order."""
        self._stop_and_close_the_order()
        stamp = {STAMP_ROOT_ENV: Path.cwd().resolve().as_posix(), STAMP_ID_ENV: ""}
        close = ["wp", "close", _PACKAGE, "--attestor", "g0", "--residual-risk", "R"]
        with patch.dict(os.environ, stamp):
            result = self.runner.invoke(main, [*close, "--evidence", "E"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("ruling 77", " ".join(result.output.split()))
        self.assertEqual(_rows("work_package_transitioned")[-1]["to_state"], "initiated")

    def test_a_closed_package_takes_no_new_issue(self) -> None:
        self._stop_and_close_the_order()
        close = ["wp", "close", _PACKAGE, "--attestor", "g0"]
        result = self.runner.invoke(main, [*close, "--residual-risk", "R", "--evidence", "E"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        with patch("gzkit.commands.wp.tag_issues") as tag:
            result = self.runner.invoke(main, ["wp", "attach", _PACKAGE, "--issue", "1300"])
        self.assertEqual(result.exit_code, 3)
        self.assertIn(f"{_PACKAGE} is closed", " ".join(result.output.split()))
        tag.assert_not_called()


class TestRunVerbs(_RunCase):
    """A repair package's run is its order's (RP-12 ruling 44), so each verb names it."""

    def test_the_cycle_past_the_bound_exits_3_and_books_nothing(self) -> None:
        for role in ("Implementer", "SpecReviewer") * 3:
            self.assertEqual(self._dispatch(role), 0)
        booked = len(_rows("work_package_dispatched"))
        self.assertEqual(self._dispatch("Implementer"), 3)
        self.assertEqual(len(_rows("work_package_dispatched")), booked)

    def test_a_marker_fault_costs_the_dispatch_no_row(self) -> None:
        """GHI #1208's invariant on the successor: the verb's only store is the ledger."""
        marker = Path(f".claude/plans/.pipeline-active-{_PACKAGE}.json")
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text('{"dispatch_state": [{"task_id": "not a record"}]}', encoding="utf-8")
        with patch.object(Path, "write_text", _refuse_marker_writes):
            self.assertEqual(self._dispatch("Implementer"), 0)
        self.assertEqual(len(_rows("work_package_dispatched")), 1)

    def test_a_block_records_the_count_and_an_unblock_clears_it(self) -> None:
        self.assertEqual(self._dispatch("Implementer"), 0)
        self.assertEqual(self._block(), 0)
        self.assertEqual(_rows("work_package_blocked")[0]["fix_cycles"], {"REQ-1@1": 0})
        self.assertEqual(self._dispatch("SpecReviewer"), 3)
        args = ["wp", "unblock", _PACKAGE, *_ON_ORDER, "--ruling", "go on", "--operator", "g0"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 0)
        self.assertEqual(_rows("work_package_unblocked")[0]["ruling"], "go on")
        self.assertEqual(self._dispatch("SpecReviewer"), 0)

    def test_the_intended_root_defaults_to_this_project_and_the_line_names_the_dispatch(
        self,
    ) -> None:
        args = ["wp", "dispatch", _PACKAGE, *_ON_ORDER, "--role", "Implementer", "--model", "m"]
        result = self.runner.invoke(main, [*args, "--req", "REQ-1"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        (row,) = _rows("work_package_dispatched")
        self.assertEqual(row["intended_root"], Path.cwd().resolve().as_posix())
        self.assertEqual(read_dispatch_id(result.output), row["dispatch_id"])

    def test_a_named_root_reaches_the_ledger_and_a_missing_one_exits_1(self) -> None:
        scratch = Path("scratch")
        scratch.mkdir()
        args = ["wp", "dispatch", _PACKAGE, *_ON_ORDER, "--role", "Implementer", "--model", "m"]
        args = [*args, "--req", "REQ-1"]
        named = self.runner.invoke(main, [*args, "--root", "scratch"])
        self.assertEqual(named.exit_code, 0, msg=named.output)
        self.assertEqual(
            _rows("work_package_dispatched")[0]["intended_root"], scratch.resolve().as_posix()
        )
        missing = self.runner.invoke(main, [*args, "--root", "nowhere"])
        self.assertEqual(missing.exit_code, 1, msg=missing.output)
        blank = self.runner.invoke(main, [*args, "--root", ""])
        self.assertEqual(blank.exit_code, 1, msg=blank.output)
        self.assertEqual(len(_rows("work_package_dispatched")), 1)

    def _ledger_lines(self) -> int:
        return len(
            (Path.cwd() / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        )

    def _stamped(self, root: str) -> int:
        stamp = {STAMP_ROOT_ENV: root, STAMP_ID_ENV: "D-0123456789abcdef"}
        with patch.dict(os.environ, stamp):
            return self._dispatch("Implementer")

    def test_a_call_stamped_for_another_root_is_refused_before_any_write(self) -> None:
        """#1296 case 1: a dispatch meant for a throwaway project, its shell left here."""
        throwaway = Path("throwaway").resolve()
        throwaway.mkdir()
        before = self._ledger_lines()
        self.assertEqual(self._stamped(throwaway.as_posix()), 3)
        self.assertEqual(self._stamped(""), 3)
        self.assertEqual(self._ledger_lines(), before)

    def test_a_call_stamped_for_this_root_proceeds(self) -> None:
        """#1296 case 2, the valid control."""
        self.assertEqual(self._stamped(Path.cwd().resolve().as_posix()), 0)
        self.assertEqual(len(_rows("work_package_dispatched")), 1)

    def test_a_call_that_passes_runs_on_without_the_stamp(self) -> None:
        """Ruling 37: what a passing verb runs, a test or a nested gz, is not refused."""
        stamp = {STAMP_ROOT_ENV: Path.cwd().resolve().as_posix(), STAMP_ID_ENV: "D-x"}
        with patch.dict(os.environ, stamp):
            self.assertEqual(self._dispatch("Implementer"), 0)
            self.assertNotIn(STAMP_ROOT_ENV, os.environ)
            self.assertNotIn(STAMP_ID_ENV, os.environ)

    def test_an_unstamped_call_proceeds(self) -> None:
        """#1296 case 3: the main session carries no stamp."""
        with patch.dict(os.environ):
            os.environ.pop(STAMP_ROOT_ENV, None)
            self.assertEqual(self._dispatch("Implementer"), 0)
        self.assertEqual(len(_rows("work_package_dispatched")), 1)

    def _void(self, dispatch_id: str, *extra: str) -> int:
        args = ["wp", "dispatch", _PACKAGE, "--void", dispatch_id, *extra]
        return self.runner.invoke(main, args).exit_code

    def test_a_void_books_its_reason_and_needs_one(self) -> None:
        """RP-12 ruling 42."""
        self.assertEqual(self._dispatch("Implementer"), 0)
        (row,) = _rows("work_package_dispatched")
        self.assertEqual(self._void(row["dispatch_id"]), 1)
        self.assertEqual(self._void(row["dispatch_id"], "--reason", "never spawned"), 0)
        (void,) = _rows("dispatch_voided")
        self.assertEqual(
            (void["dispatch_id"], void["reason"]), (row["dispatch_id"], "never spawned")
        )
        self.assertEqual(self._void(row["dispatch_id"], "--reason", "again"), 3)

    def test_a_void_from_a_subagents_call_is_refused(self) -> None:
        """Ruling 42: no subagent voids its way out, as rulings 24 and 32 refuse."""
        self.assertEqual(self._dispatch("Implementer"), 0)
        (row,) = _rows("work_package_dispatched")
        stamp = {STAMP_ROOT_ENV: Path.cwd().resolve().as_posix(), STAMP_ID_ENV: ""}
        with patch.dict(os.environ, stamp):
            self.assertEqual(self._void(row["dispatch_id"], "--reason", "why"), 3)
        self.assertEqual(_rows("dispatch_voided"), [])

    def test_a_booking_still_needs_its_role_and_model(self) -> None:
        bare = ["wp", "dispatch", _PACKAGE, *_ON_ORDER, "--req", "REQ-1"]
        self.assertEqual(self.runner.invoke(main, bare).exit_code, 2)
        self.assertEqual(self.runner.invoke(main, [*bare, "--role", "Implementer"]).exit_code, 2)
        both = [*bare, "--role", "Implementer", "--model", "m", "--void", "D-0123456789abcdef"]
        self.assertEqual(self.runner.invoke(main, both).exit_code, 2)
        void = ["wp", "dispatch", _PACKAGE, "--void", "D-0123456789abcdef", "--reason", "r"]
        for extra in (["--req", "REQ-1"], ["--root", "."], list(_ON_ORDER)):
            with self.subTest(extra=extra):
                self.assertEqual(self.runner.invoke(main, [*void, *extra]).exit_code, 2)

    def test_the_operator_is_never_defaulted(self) -> None:
        self.assertEqual(self._block(), 0)
        args = ["wp", "unblock", _PACKAGE, *_ON_ORDER, "--ruling", "go on"]
        self.assertEqual(self.runner.invoke(main, args).exit_code, 2)

    def test_an_issue_is_no_dispatch_subject(self) -> None:
        """RP-12 ruling 64: `--issue` is retired, a usage error that books nothing."""
        args = ["wp", "dispatch", _PACKAGE, *_ON_ORDER, "--role", "Implementer", "--model", "m"]
        self.assertEqual(self.runner.invoke(main, [*args, "--issue", "1301"]).exit_code, 2)
        self.assertEqual(_rows("work_package_dispatched"), [])

    def test_a_dispatch_on_the_repair_package_alone_exits_3(self) -> None:
        """RP-12 ruling 44: the dispatch names the order, and a refusal books nothing."""
        args = ["wp", "dispatch", _PACKAGE, "--role", "Implementer", "--model", "m"]
        self.assertEqual(self.runner.invoke(main, [*args, "--req", "REQ-1"]).exit_code, 3)
        self.assertEqual(_rows("work_package_dispatched"), [])

    def test_the_exit_and_req_flags_reach_the_ledger(self) -> None:
        for role in ("Implementer", "SpecReviewer") * 3:
            self.assertEqual(self._dispatch(role), 0)
        self.assertEqual(self._block(), 0)
        args = ["wp", "unblock", _PACKAGE, *_ON_ORDER, "--ruling", "hold", "--operator", "g0"]
        args = [*args, "--exit", "hold"]
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
