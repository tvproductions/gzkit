"""``gz wp runs`` and the position on ``gz wp show`` (RO-14 tranche 1, act 3).

GHI #1203 read on the work-package surface: for every run in flight, an operator
command reports what the ledger says the run has reached, with no marker on disk
and whatever its age. The position is replayed from the rows the package's verbs
already book (the specification's ruling 18), so there is no second row to lose.
"""

import json
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init

_FIRST = "WP-01-older"
_SECOND = "WP-02-later"


def _record(package: str, *issues: int) -> dict[str, object]:
    return {
        "id": package,
        "kind": "repair",
        "outcome": None,
        "issues": list(issues),
        "lane": "lite",
        "aliases": [],
        "modules": ["data/catalog/"],
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "NA",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }


def _seed_store() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    packages = [_record(_FIRST, 1203, 1205), _record(_SECOND, 1208)]
    for kind, entries in (
        ("families", []),
        ("outcomes", []),
        ("reqs", []),
        ("externals", []),
        ("work_packages", packages),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


class _RunsCase(unittest.TestCase):
    def setUp(self) -> None:
        # Acceptance is not this suite's subject: tests/commands/test_wp_acceptance.py is.
        gate = mock.patch("gzkit.commands.wp.acceptance_blockers", return_value=[])
        gate.start()
        self.addCleanup(gate.stop)
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_store()

    def _wp(self, *args: str) -> None:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, 0, msg=result.output)

    def _commence(self, package: str) -> None:
        self._wp("initiate", package, "--operator-text", "go")
        self._wp("freeze", package, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e")
        self._wp("commence", package, "--evidence", "e")

    def _dispatch(self, package: str, issue: int, role: str = "Implementer") -> None:
        self._wp("dispatch", package, "--role", role, "--model", "m", "--issue", str(issue))

    def _runs(self) -> list[dict]:
        result = self.runner.invoke(main, ["wp", "runs", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return json.loads(result.output)


class TestRunsReadTheLedger(_RunsCase):
    def test_no_run_in_flight_reports_nothing(self) -> None:
        self.assertEqual(self._runs(), [])

    def test_a_package_before_commencement_is_no_run(self) -> None:
        self._wp("initiate", _FIRST, "--operator-text", "go")
        self.assertEqual(self._runs(), [])
        self._wp("freeze", _FIRST, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e")
        self.assertEqual(self._runs(), [])

    def test_two_runs_in_flight_are_both_reported_with_no_marker_on_disk(self) -> None:
        """The case #1203 names: the older run is read beside a later one."""
        self._commence(_FIRST)
        self._commence(_SECOND)
        self._dispatch(_FIRST, 1203)
        self._dispatch(_SECOND, 1208)
        self.assertFalse(list(Path(".claude/plans").glob(".pipeline-active*")))
        by_id = {run["work_package"]: run for run in self._runs()}
        self.assertEqual(set(by_id), {_FIRST, _SECOND})
        self.assertEqual(by_id[_FIRST]["subject"], "#1203")
        self.assertEqual(by_id[_SECOND]["subject"], "#1208")
        self.assertEqual(by_id[_FIRST]["event"], "work_package_dispatched")
        self.assertEqual(by_id[_FIRST]["move"], "Implementer #1203")

    def test_a_run_whose_last_row_is_old_is_still_read(self) -> None:
        """No stale bound stands between the operator and a recorded position."""
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        path = Path(".gzkit") / "ledger.jsonl"
        kept = []
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("event") == "work_package_dispatched":
                row["ts"] = "2020-01-01T00:00:00+00:00"
            kept.append(json.dumps(row))
        path.write_text("\n".join(kept) + "\n", encoding="utf-8")
        run = self._runs()[0]
        self.assertEqual(run["at"], "2020-01-01T00:00:00+00:00")
        self.assertEqual(run["subject"], "#1203")

    def test_a_marker_naming_something_else_moves_no_position(self) -> None:
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        marker = Path(f".claude/plans/.pipeline-active-{_FIRST}.json")
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text('{"current_stage": "sync", "position": 1}', encoding="utf-8")
        self.assertEqual(self._runs()[0]["event"], "work_package_dispatched")

    def test_the_position_follows_the_last_row_and_keeps_the_subject(self) -> None:
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        self._wp("block", _FIRST, "--reason", "r", "--next-action", "a")
        run = self._runs()[0]
        self.assertTrue(run["blocked"])
        self.assertEqual(run["event"], "work_package_blocked")
        self.assertEqual(run["subject"], "#1203")
        self._wp("unblock", _FIRST, "--ruling", "go on", "--operator", "g0")
        run = self._runs()[0]
        self.assertFalse(run["blocked"])
        self.assertEqual(run["event"], "work_package_unblocked")

    def test_a_run_ends_at_the_close_and_not_at_acceptance(self) -> None:
        self._commence(_FIRST)
        with mock.patch("gzkit.commands.wp.footprint_refusal", return_value=None):
            self._wp("accept", _FIRST, "--evidence", "e")
        self.assertEqual([run["state"] for run in self._runs()], ["accepted"])
        self._wp(
            "close",
            _FIRST,
            "--decision",
            "proceed",
            "--residual-risk",
            "none",
            "--attestor",
            "g0",
            "--evidence",
            "e",
        )
        self.assertEqual(self._runs(), [])

    def test_the_subject_is_the_one_dispatched_last(self) -> None:
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        self._dispatch(_FIRST, 1205)
        self.assertEqual(self._runs()[0]["subject"], "#1205")

    def test_a_package_with_no_dispatch_has_no_subject(self) -> None:
        self._commence(_FIRST)
        run = self._runs()[0]
        self.assertIsNone(run["subject"])
        self.assertEqual(run["state"], "commenced")


class TestShowCarriesThePosition(_RunsCase):
    def _show(self, package: str) -> dict:
        result = self.runner.invoke(main, ["wp", "show", package, "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return json.loads(result.output)

    def test_a_run_in_flight_carries_the_position_the_list_reports(self) -> None:
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        self.assertEqual(self._show(_FIRST)["position"], self._runs()[0])

    def test_a_package_with_no_run_carries_none(self) -> None:
        self._wp("initiate", _FIRST, "--operator-text", "go")
        self.assertIsNone(self._show(_FIRST)["position"])


class TestRunsRendering(_RunsCase):
    """Rendering is the named contract of a read-only verb's human report."""

    # output-contract: the operator reads each run's last move and subject here

    def test_the_report_names_each_run(self) -> None:
        self._commence(_FIRST)
        self._dispatch(_FIRST, 1203)
        result = self.runner.invoke(main, ["wp", "runs"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(_FIRST, result.output)
        self.assertIn("#1203", result.output)

    def test_a_block_reason_is_text_and_never_markup(self) -> None:
        """A free-text reason reaches the report whole, whatever brackets it holds."""
        self._commence(_FIRST)
        for reason in ("REQ-1 [behavior] fails", "see [/x]", "see :x:"):
            with self.subTest(reason):
                self._wp("block", _FIRST, "--reason", reason, "--next-action", "a")
                for args in (["wp", "runs"], ["wp", "show", _FIRST]):
                    result = self.runner.invoke(main, args)
                    self.assertEqual(result.exit_code, 0, msg=result.output)
                    self.assertIn(reason, result.output)
                self._wp("unblock", _FIRST, "--ruling", "go on", "--operator", "g0")

    def test_show_carries_the_position_only_for_a_run_in_flight(self) -> None:
        self._wp("initiate", _FIRST, "--operator-text", "go")
        before = self.runner.invoke(main, ["wp", "show", _FIRST])
        self.assertNotIn("blocked:", before.output)
        self._wp("freeze", _FIRST, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e")
        self._wp("commence", _FIRST, "--evidence", "e")
        self._dispatch(_FIRST, 1203)
        during = self.runner.invoke(main, ["wp", "show", _FIRST])
        self.assertIn("blocked: no", during.output)
        self.assertIn("last: dispatched Implementer #1203", during.output)

    def test_no_run_says_so(self) -> None:
        result = self.runner.invoke(main, ["wp", "runs"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("No work package is in flight", result.output)
