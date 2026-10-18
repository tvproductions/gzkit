"""gz insights remember books an insight_recorded ledger pointer.

Operator ruling 2026-10-18, verbatim: "what is the harm that the ledger notes that an
insight was recorded and references it?", then "Pointer + 3 fields (Rec.)". The insight
stays in the insights store; the ledger, the system of record, gains one event naming
it: the insight's ts, a content hash, whose words they are, and an optional supersedes
reference (docs/governance/ieee/requirements-model.md § 11).
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.events import InsightRecordedEvent, parse_typed_event
from tests.commands.common import CliRunner

_STORE = Path(".gzkit") / "insights" / "agent-insights.jsonl"
_LEDGER = Path(".gzkit") / "ledger.jsonl"


def _insight_lines() -> list[str]:
    if not _STORE.exists():
        return []
    return [ln for ln in _STORE.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _recorded() -> list[dict]:
    if not _LEDGER.exists():
        return []
    rows = [json.loads(ln) for ln in _LEDGER.read_text(encoding="utf-8").splitlines() if ln]
    return [row for row in rows if row.get("event") == "insight_recorded"]


def _remember(runner: CliRunner, *extra: str):
    return runner.invoke(
        main,
        [
            "insights",
            "remember",
            "--type",
            "discovery",
            "--scope",
            "requirements-model",
            "--summary",
            "a ruling the ledger must point at",
            *extra,
        ],
    )


class TestInsightRecordedPointer(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_one_pointer_names_the_insight_by_ts_and_hash(self) -> None:
        with self._runner.isolated_filesystem():
            result = _remember(self._runner)
            self.assertEqual(result.exit_code, 0, msg=result.output)
            (line,) = _insight_lines()
            (event,) = _recorded()
            self.assertEqual(event["insight_ts"], json.loads(line)["ts"])
            self.assertEqual(
                event["insight_sha256"], hashlib.sha256(line.encode("utf-8")).hexdigest()
            )

    def test_unclaimed_words_are_the_agents(self) -> None:
        with self._runner.isolated_filesystem():
            _remember(self._runner)
            (event,) = _recorded()
            self.assertEqual(event["source"], "agent")

    def test_operator_words_are_recorded_as_the_operators(self) -> None:
        with self._runner.isolated_filesystem():
            result = _remember(self._runner, "--source", "operator")
            self.assertEqual(result.exit_code, 0, msg=result.output)
            (event,) = _recorded()
            self.assertEqual(event["source"], "operator")

    def test_supersedes_names_an_earlier_insight(self) -> None:
        with self._runner.isolated_filesystem():
            _remember(self._runner)
            earlier = json.loads(_insight_lines()[0])["ts"]
            result = _remember(self._runner, "--supersedes", earlier)
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_recorded()[-1]["supersedes"], earlier)

    def test_superseding_an_unknown_insight_writes_nothing(self) -> None:
        with self._runner.isolated_filesystem():
            result = _remember(self._runner, "--supersedes", "2026-01-01T00:00:00+00:00")
            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_insight_lines(), [])
            self.assertEqual(_recorded(), [])

    def test_the_pointer_is_a_typed_ledger_event(self) -> None:
        with self._runner.isolated_filesystem():
            _remember(self._runner, "--source", "operator")
            (event,) = _recorded()
            self.assertIsInstance(parse_typed_event(event), InsightRecordedEvent)


if __name__ == "__main__":
    unittest.main()
