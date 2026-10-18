"""gz insights recurrence — the maxim-13 recurrence check (drydock RO-1).

Operator rulings 2026-10-18, verbatim selections: '3 occurrences (Rec.)',
'Cited records (Rec.)' and 'One lease apart (Rec.)'. A failure becomes a rule
only when a proposal cites at least the threshold of insight or GHI records, each
pair of them at least one session lease apart by full timestamp.
"""

from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
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


def _rewrite_ts(old: str, new: datetime) -> str:
    store = Path(".gzkit") / "insights" / "agent-insights.jsonl"
    text = store.read_text(encoding="utf-8").replace(old, new.isoformat())
    store.write_text(text, encoding="utf-8")
    return new.isoformat()


class TestInsightsRecurrenceCommand(unittest.TestCase):
    """The verb resolves citations to full timestamps and applies the JSON threshold."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _three_insights(self, *hours: float) -> list[str]:
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
            Path("data").mkdir()
            Path("data/recurrence_threshold.json").write_text(
                json.dumps({"min_occurrences": 2}), encoding="utf-8"
            )
            result = self._runner.invoke(main, ["insights", "recurrence", *cites, "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(json.loads(result.output)["required"], 2)


if __name__ == "__main__":
    unittest.main()
