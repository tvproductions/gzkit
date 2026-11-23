"""gz insights recurrence — the maxim-13 recurrence check (drydock RO-1).

Operator rulings 2026-10-18, verbatim selections: '3 occurrences (Rec.)',
'Cited records (Rec.)' and 'One lease apart (Rec.)'. A failure becomes a rule
only when a proposal cites at least the threshold of insight or GHI records, each
pair of them at least one session lease apart by full timestamp.
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import override
from unittest.mock import patch

from gzkit.cli.main import main
from gzkit.commands.insights import gh_issue_created_at, resolve_cite
from gzkit.commands.reference_checker import GhUnansweredError
from tests.commands.common import CliRunner

_BASE = datetime(2026, 1, 1, tzinfo=UTC)
_LEASE = 24.0


def _check(*hours: float, min_occurrences: int = 3):
    from gzkit.insights.recurrence import check_recurrence

    cited = {f"r{i}": _BASE + timedelta(hours=h) for i, h in enumerate(hours)}
    return check_recurrence(cited, min_occurrences=min_occurrences, separation_hours=_LEASE)


class TestCheckRecurrence(unittest.TestCase):
    """The pure check: enough citations, every pair a lease apart."""

    def test_three_records_a_lease_apart_meet_the_threshold(self) -> None:
        verdict = _check(0, 24, 48)
        self.assertTrue(verdict.met)
        self.assertEqual((verdict.cited, verdict.required), (3, 3))
        self.assertEqual(verdict.too_close, [])

    def test_two_records_fall_short(self) -> None:
        verdict = _check(0, 48)
        self.assertFalse(verdict.met)
        self.assertEqual(verdict.cited, 2)

    def test_records_inside_one_lease_are_one_occurrence(self) -> None:
        verdict = _check(0, 1, 48)
        self.assertFalse(verdict.met)
        self.assertEqual(verdict.too_close, [("r0", "r1")])

    def test_every_pair_is_checked_not_only_neighbours(self) -> None:
        # r0 and r2 are 23 h apart but not adjacent in citation order; a
        # neighbours-only scan would miss them. Pairs report in citation order.
        verdict = _check(23, 100, 0)
        self.assertEqual(verdict.too_close, [("r0", "r2")])

    def test_exactly_one_lease_apart_counts(self) -> None:
        self.assertTrue(_check(0, 24, 48).met)
        self.assertFalse(_check(0, 23.99, 48).met)

    def test_the_threshold_is_a_parameter(self) -> None:
        self.assertTrue(_check(0, 48, min_occurrences=2).met)


def _remember(runner: CliRunner, summary: str) -> str:
    result = runner.invoke(
        main, ["insights", "remember", "--type", "defect", "--scope", "s", "--summary", summary]
    )
    assert result.exit_code == 0, result.output
    store = Path(".gzkit") / "insights" / "agent-insights.jsonl"
    return json.loads(store.read_text(encoding="utf-8").splitlines()[-1])["ts"]


def _registry(min_occurrences: int) -> None:
    Path("data").mkdir(exist_ok=True)
    Path("data/recurrence_threshold.json").write_text(
        json.dumps({"min_occurrences": min_occurrences}), encoding="utf-8"
    )


def _rewrite_ts(old: str, new: datetime) -> str:
    store = Path(".gzkit") / "insights" / "agent-insights.jsonl"
    text = store.read_text(encoding="utf-8").replace(old, new.isoformat())
    store.write_text(text, encoding="utf-8")
    return new.isoformat()


class TestInsightsRecurrenceCommand(unittest.TestCase):
    """The verb resolves citations to full timestamps and applies the JSON threshold."""

    @override
    def setUp(self) -> None:
        self._runner = CliRunner()

    def _three_insights(self, *hours: float) -> list[str]:
        _registry(3)
        return [
            _rewrite_ts(_remember(self._runner, f"failure {i}"), _BASE + timedelta(hours=h))
            for i, h in enumerate(hours)
        ]

    def test_met_exits_zero_and_reports_json(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 30, 60)
            result = self._runner.invoke(main, ["insights", "recurrence", *cites, "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            payload = json.loads(result.output)
            self.assertTrue(payload["met"])
            self.assertEqual(payload["required"], 3)
            self.assertEqual(payload["separation_hours"], _LEASE)

    def test_records_inside_one_lease_exit_three(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 2, 60)
            result = self._runner.invoke(main, ["insights", "recurrence", *cites, "--json"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertEqual(json.loads(result.output)["too_close"], [[cites[0], cites[1]]])

    def test_an_unknown_citation_exits_one(self) -> None:
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main, ["insights", "recurrence", "2026-01-01T00:00:00+00:00"]
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("names no insight record or resolvable GHI", result.output)

    def test_a_naive_insight_ts_is_read_as_utc(self) -> None:
        with self._runner.isolated_filesystem():
            naive = _rewrite_ts(_remember(self._runner, "f"), datetime(2026, 1, 1))
            cites = [naive, *self._three_insights(30, 60)]
            result = self._runner.invoke(main, ["insights", "recurrence", *cites, "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_human_output_names_each_pair_inside_one_lease(self) -> None:
        # output-contract: the human verdict names the pairs counted as one occurrence
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 2, 60)
            result = self._runner.invoke(main, ["insights", "recurrence", *cites])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Recurrence not met", result.output)
            self.assertIn(cites[0], result.output)
            self.assertIn(cites[1], result.output)
            self.assertIn("inside one lease", result.output)

    def test_a_missing_registry_exits_one_and_names_it(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 30, 60)
            Path("data/recurrence_threshold.json").unlink()
            result = self._runner.invoke(main, ["insights", "recurrence", *cites])
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("recurrence_threshold.json", result.output)
            # Reported by the verb, not caught as an unexpected crash by gz main.
            self.assertNotIn("Unexpected error", result.output)

    def test_a_non_positive_threshold_exits_one(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 30, 60)
            _registry(0)
            result = self._runner.invoke(main, ["insights", "recurrence", *cites])
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("positive integer", result.output)
            self.assertNotIn("Unexpected error", result.output)

    def test_a_ghi_citation_resolves_to_its_creation_time(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 30)
            created = {"1257": _BASE + timedelta(hours=90)}
            with patch(
                "gzkit.commands.insights.gh_issue_created_at",
                side_effect=lambda n, root: created.get(n),
            ):
                result = self._runner.invoke(
                    main, ["insights", "recurrence", *cites, "#1257", "--json"]
                )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(json.loads(result.output)["cited"], 3)

    def test_the_threshold_is_read_from_the_registry(self) -> None:
        with self._runner.isolated_filesystem():
            cites = self._three_insights(0, 30)
            _registry(2)
            result = self._runner.invoke(main, ["insights", "recurrence", *cites, "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(json.loads(result.output)["required"], 2)


def _api(status: str, body: str) -> str:
    """One `gh api --include` answer: the status line (LF), a header (CRLF), a blank line, the body.

    gh's own line endings, observed 2026-11-20.

    Returns:
        The stdout `gh api --include` prints for *status* and *body*.

    """
    return f"HTTP/2.0 {status}\nContent-Type: application/json\r\n\r\n{body}"


class TestGhIssueCreatedAt(unittest.TestCase):
    """The gh adapter resolves a found issue's creation time; a missing issue is None,
    and an unanswered call raises, so it is never read as a citation naming nothing
    (RP-12 ruling 182)."""

    def _call(self, rc: int, out: str) -> datetime | None:
        with patch("gzkit.commands.reference_checker.run_exec", return_value=(rc, out, "")) as run:
            value = gh_issue_created_at("1257", Path("."))
        self.assertEqual(run.call_args.args[0][:3], ["gh", "api", "--include"])
        return value

    def test_created_at_resolves(self) -> None:
        body = '{"state": "open", "created_at": "2026-10-18T13:00:00Z"}'
        self.assertEqual(
            self._call(0, _api("200 OK", body)), datetime(2026, 10, 18, 13, tzinfo=UTC)
        )

    def test_an_issue_the_api_says_does_not_exist_is_none(self) -> None:
        self.assertIsNone(self._call(1, _api("404 Not Found", '{"message": "Not Found"}')))

    def test_an_unanswered_call_raises(self) -> None:
        for out in ("", _api("502 Bad Gateway", "{}"), _api("200 OK", "not json")):
            with self.subTest(out=out[:20]), self.assertRaises(GhUnansweredError):
                self._call(1 if not out.startswith("HTTP/2.0 200") else 0, out)

    def test_a_ghi_cited_with_or_without_its_hash_is_one_label(self) -> None:
        # The clear's --recurs counts a record once by this label (RP-12 ruling 181), so
        # the bare and the hashed number must name the same occurrence.
        out = _api("200 OK", '{"state": "open", "created_at": "2026-10-18T13:00:00Z"}')
        with patch("gzkit.commands.reference_checker.run_exec", return_value=(0, out, "")):
            bare = resolve_cite("1412", {}, Path("."))
            hashed = resolve_cite("#1412", {}, Path("."))
        self.assertIsNotNone(bare)
        self.assertEqual(bare, hashed)
        self.assertEqual(bare, ("#1412", datetime(2026, 10, 18, 13, tzinfo=UTC)))

    def test_a_found_issue_with_no_usable_creation_time_raises(self) -> None:
        # The API says the issue exists, so it cannot be read as naming nothing; with no
        # time to measure the separation by, the answer is no answer (ruling 182).
        for body in ('{"state": "open"}', '{"state": "closed", "created_at": "yesterday"}'):
            with self.subTest(body=body), self.assertRaises(GhUnansweredError):
                self._call(0, _api("200 OK", body))

    def test_recurrence_exits_two_when_gh_gives_no_answer(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            with patch("gzkit.commands.reference_checker.run_exec", return_value=(1, "", "")):
                result = runner.invoke(main, ["insights", "recurrence", "#1257"])
            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("#1257", result.output)
            self.assertNotIn("names no insight record", result.output)


if __name__ == "__main__":
    unittest.main()
