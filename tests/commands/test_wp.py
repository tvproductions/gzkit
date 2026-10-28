"""``gz wp`` drives a work package end to end: RO-5 tranche 2.

`docs/governance/harbor-ro5-work-packages.md` § Tranches row 2, with the verb
names the operator ruled on 2026-10-28 ("gz wp <verb> (Recommended)"): the
record is written only through `gz wp new` and `gz wp attach` (ruling 3), the
lifecycle and the change ladder only through the ledger writers, and a refusal
exits 3 with nothing written.
"""

import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from gzkit.cli import main
from gzkit.governance.trust_audits.catalog import audit_catalog
from gzkit.work_package_github import WorkPackageGithubError
from tests.commands.common import CliRunner, _quick_init

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
_REQ = {
    "id": "REQ-1",
    "member_of": "H1",
    "statement": "A resumed session names its predecessor.",
    "criteria": [{"state_or_input": "a handoff", "required_outcome": "named", "evidence": "t"}],
    "kind": "BEHAVIOR",
    "revision": 2,
    "derives_from": ["FR-001"],
    "applies_to": [],
}


def _seed_catalog() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    family = {"code": "H", "band": "product", "name": "Session", "scope": "One."}
    for kind, entries in (
        ("families", [family]),
        ("outcomes", [_OUTCOME]),
        ("reqs", [_REQ]),
        ("externals", []),
        ("work_packages", []),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _store() -> list[dict[str, Any]]:
    text = (Path("data") / "catalog" / "work_packages.json").read_text(encoding="utf-8")
    return json.loads(text)["work_packages"]


def _ledger_rows(event: str) -> list[dict[str, Any]]:
    path = Path(".gzkit") / "ledger.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return [row for row in rows if row.get("event") == event]


class _WpCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()
        self.tag = self.enterContext(patch("gzkit.commands.wp.tag_issues"))

    def gz(self, *args: str, code: int = 0) -> str:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, code, result.output)
        return result.output

    def new_repair(self) -> None:
        self.gz("new", "--kind", "repair", "--slug", "astral", "--issue", "1183", "--lane", "lite")


class NewAndAttachTests(_WpCase):
    def test_new_numbers_the_series_and_the_store_passes_its_scope(self) -> None:
        self.new_repair()
        self.gz("new", "--kind", "delivery", "--slug", "resume", "--outcome", "H1")
        self.assertEqual([wp["id"] for wp in _store()], ["WP-01-astral", "WP-02-resume"])
        store_findings = [e for e in audit_catalog(Path.cwd()) if e.field == "work_packages"]
        self.assertEqual(store_findings, [])

    def test_new_writes_the_alteration_into_the_record(self) -> None:
        self.gz(
            "new", "--kind", "delivery", "--slug", "resume", "--outcome", "H1",
            "--alteration", "ALT-1:replaced:Rekey the matrix",
        )  # fmt: skip
        (record,) = _store()
        self.assertEqual(record["alterations"][0]["configuration_change"], "replaced")

    def test_a_record_the_rulings_refuse_is_never_written(self) -> None:
        self.gz("new", "--kind", "delivery", "--slug", "resume", "--outcome", "H9", code=3)
        self.gz("new", "--kind", "repair", "--slug", "astral", "--lane", "lite", code=3)
        self.assertEqual(_store(), [])

    def test_attach_adds_an_issue_and_refuses_one_another_package_holds(self) -> None:
        self.new_repair()
        self.gz("new", "--kind", "repair", "--slug", "ruff", "--issue", "7", "--lane", "lite")
        self.gz("attach", "WP-01-astral", "--issue", "1184")
        self.assertEqual(_store()[0]["issues"], [1183, 1184])
        self.gz("attach", "WP-02-ruff", "--issue", "1183", code=3)
        self.assertEqual(_store()[1]["issues"], [7])

    def test_an_unknown_package_exits_1(self) -> None:
        self.gz("attach", "WP-09-ghost", "--issue", "1", code=1)


class GithubTaggingTests(_WpCase):
    """Ruling 7 with the 2026-10-28 rulings: check the edit, tag on GitHub, then write."""

    def test_new_and_attach_tag_only_the_issues_they_add(self) -> None:
        self.gz(
            "new", "--kind", "repair", "--slug", "astral", "--issue", "1183",
            "--lane", "lite", "--alias", "RO-9",
        )  # fmt: skip
        self.gz("attach", "WP-01-astral", "--issue", "1184")
        calls = [call.args for call in self.tag.call_args_list]
        self.assertEqual(
            calls, [("WP-01-astral", ("RO-9",), (1183,)), ("WP-01-astral", ("RO-9",), (1184,))]
        )

    def test_a_delivery_package_reaches_no_github(self) -> None:
        self.gz("new", "--kind", "delivery", "--slug", "resume", "--outcome", "H1")
        self.tag.assert_not_called()

    def test_a_refused_edit_reaches_no_github(self) -> None:
        self.new_repair()
        self.gz(
            "new", "--kind", "repair", "--slug", "ruff", "--issue", "1183", "--lane", "lite", code=3
        )
        self.assertEqual(self.tag.call_count, 1)

    def test_a_github_failure_writes_nothing_and_exits_2(self) -> None:
        self.new_repair()
        self.tag.side_effect = WorkPackageGithubError("gh failed")
        self.gz("attach", "WP-01-astral", "--issue", "1184", code=2)
        self.gz(
            "new", "--kind", "repair", "--slug", "ruff", "--issue", "7", "--lane", "lite", code=2
        )
        self.assertEqual([wp["issues"] for wp in _store()], [[1183]])


class ResolveTests(_WpCase):
    """Ruling 10: gz wp resolve books an issue's close; the package closes only through Gate 5."""

    def setUp(self) -> None:
        super().setUp()
        self.new_repair()
        self.gz("attach", "WP-01-astral", "--issue", "1184")
        self.gz("initiate", "WP-01-astral", "--operator-text", "go")

    def resolve(self, issue: str, code: int = 0) -> str:
        return self.gz(
            "resolve", "WP-01-astral", issue, "--commit", "abc1234",
            "--reviewer", "spec-reviewer", "--json", code=code,
        )  # fmt: skip

    def test_resolve_books_the_close_and_reports_the_issues_still_open(self) -> None:
        reported = json.loads(self.resolve("1183"))
        (event,) = _ledger_rows("work_package_issue_closed")
        self.assertEqual((event["issue"], event["commit"]), (1183, "abc1234"))
        self.assertEqual(reported["open_issues"], [1184])

    def test_the_last_issue_leaves_the_package_open_for_gate_5(self) -> None:
        self.resolve("1183")
        reported = json.loads(self.resolve("1184"))
        self.assertEqual((reported["open_issues"], reported["state"]), ([], "initiated"))
        shown = json.loads(self.gz("show", "WP-01-astral", "--json"))
        self.assertEqual(shown["state"], "initiated")
        self.assertIn("work_package_issue_closed", [row["event"] for row in shown["history"]])

    def test_a_refused_close_exits_3_and_books_nothing(self) -> None:
        self.resolve("7", code=3)
        self.resolve("1183")
        self.resolve("1183", code=3)
        self.assertEqual(len(_ledger_rows("work_package_issue_closed")), 1)


class LifecycleTests(_WpCase):
    def setUp(self) -> None:
        super().setUp()
        self.gz("new", "--kind", "delivery", "--slug", "resume", "--outcome", "H1")

    def test_the_verbs_walk_the_whole_lifecycle(self) -> None:
        self.gz("initiate", "WP-01-resume", "--operator-text", "start the resume package")
        self.gz(
            "freeze", "WP-01-resume", "--baseline", "REQ-1@2", "--risk-note", "R",
            "--review-receipt", "RV", "--evidence", "E",
        )  # fmt: skip
        self.gz("commence", "WP-01-resume", "--evidence", "E")
        self.gz("accept", "WP-01-resume", "--evidence", "E")
        self.gz(
            "close", "WP-01-resume", "--decision", "proceed", "--attestor", "g0",
            "--residual-risk", "none", "--evidence", "E",
        )  # fmt: skip
        moves = [row["to_state"] for row in _ledger_rows("work_package_transitioned")]
        self.assertEqual(moves, ["initiated", "frozen", "commenced", "accepted", "closed"])
        frozen = _ledger_rows("work_package_transitioned")[1]
        self.assertEqual(frozen["baseline"], [{"req": "REQ-1", "revision": 2}])

    def test_a_skipped_step_exits_3_and_books_nothing(self) -> None:
        self.gz("commence", "WP-01-resume", "--evidence", "E", code=3)
        self.assertEqual(_ledger_rows("work_package_transitioned"), [])

    def test_a_malformed_baseline_entry_exits_3(self) -> None:
        self.gz("initiate", "WP-01-resume", "--operator-text", "go")
        self.gz(
            "freeze", "WP-01-resume", "--baseline", "REQ-1", "--risk-note", "R",
            "--review-receipt", "RV", "--evidence", "E", code=3,
        )  # fmt: skip

    def test_show_reports_the_state_and_history(self) -> None:
        self.gz("initiate", "WP-01-resume", "--operator-text", "go")
        shown = json.loads(self.gz("show", "WP-01-resume", "--json"))
        self.assertEqual(shown["state"], "initiated")
        self.assertEqual(shown["record"]["outcome"], "H1")
        self.assertEqual(len(shown["history"]), 1)


class ChangeTests(_WpCase):
    def setUp(self) -> None:
        super().setUp()
        self.gz("new", "--kind", "delivery", "--slug", "resume", "--outcome", "H1")
        self.gz("initiate", "WP-01-resume", "--operator-text", "go")

    def test_a_departure_joins_the_record_with_the_event_that_records_it(self) -> None:
        self.gz(
            "change", "WP-01-resume", "--rung", "departure", "--approver", "operator",
            "--change", "No Windows runner yet.", "--item", "DFS-1", "--form", "waiver",
            "--duration", "temporary", "--clear-by", "the runner lands",
        )  # fmt: skip
        (departure,) = _store()[0]["departures"]
        self.assertEqual((departure["id"], departure["form"]), ("DFS-1", "waiver"))
        (event,) = _ledger_rows("work_package_changed")
        self.assertEqual((event["duration"], event["clear_by"]), ("temporary", "the runner lands"))

    def test_a_refused_change_leaves_the_record_and_the_ledger_as_they_were(self) -> None:
        self.gz(
            "change", "WP-01-resume", "--rung", "departure", "--approver", "coordinator",
            "--change", "No runner.", "--item", "DFS-1", "--form", "waiver",
            "--duration", "permanent", code=3,
        )  # fmt: skip
        self.assertEqual(_store()[0]["departures"], [])
        self.assertEqual(_ledger_rows("work_package_changed"), [])

    def test_pen_and_ink_is_booked_for_the_coordinator(self) -> None:
        self.gz(
            "change", "WP-01-resume", "--rung", "pen_and_ink", "--approver", "coordinator",
            "--change", "Resequence", "--superseded", "Cards 2, 1",
        )  # fmt: skip
        (event,) = _ledger_rows("work_package_changed")
        self.assertEqual(event["superseded"], "Cards 2, 1")


if __name__ == "__main__":
    unittest.main()
