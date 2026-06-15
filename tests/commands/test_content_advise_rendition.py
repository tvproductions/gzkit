"""gz content advise-rendition command tests — OBPI-0.0.37-24 (BEHAVIOR REQ proofs).

REQ-derived from the brief's Acceptance Criteria, not from implementation:
the advisor-QC command records an info-retained-per-byte verdict as an ARB
receipt and stays advisory (exit 0 for any score), and fails closed (non-zero
exit, no receipt) only when the verdict is structurally malformed (empty
explanation) — never on the verdict value itself (ADR-0.0.39).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner


def _receipts() -> list[Path]:
    return sorted((Path(".") / "artifacts" / "receipts").glob("arb-step-judge-*.json"))


def _ledger_events() -> list[dict]:
    ledger = Path(".") / ".gzkit" / "ledger.jsonl"
    if not ledger.exists():
        return []
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]


class TestContentAdviseRenditionCmd(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-24-01")
    def test_records_verdict_and_exits_zero_for_low_score(self) -> None:
        """A low retention score is advisory — receipt written, ledger event, exit 0."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            args = [
                "content",
                "advise-rendition",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--score",
                "0.12",
                "--explanation",
                "Two Promotable bullets dropped — measurable info loss, surfaced for the operator.",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            receipts = _receipts()
            self.assertEqual(len(receipts), 1, "exactly one verdict receipt should be written")
            receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
            self.assertEqual(receipt["exit_status"], 0)
            self.assertEqual(receipt["verdict"]["score"], 0.12)

            events = [e for e in _ledger_events() if e.get("event") == "rendition_advisor_verdict"]
            self.assertEqual(len(events), 1, "one rendition_advisor_verdict event should emit")
            self.assertEqual(events[0]["surface"], "AGENTS.md")
            self.assertEqual(events[0]["consumer"], "codex")
            self.assertEqual(events[0]["score"], 0.12)
            self.assertEqual(events[0]["receipt_id"], receipts[0].stem)

    @covers("REQ-0.0.37-24-01")
    def test_records_verdict_and_exits_zero_for_high_score(self) -> None:
        """A high score path also records and exits 0 — symmetry confirms non-gating."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            args = [
                "content",
                "advise-rendition",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--score",
                "0.94",
                "--explanation",
                "All Mechanical bullets retained; two Promotable bullets combined cleanly.",
            ]
            result = self._runner.invoke(main, args)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(len(_receipts()), 1)

    @covers("REQ-0.0.37-24-02")
    def test_empty_explanation_fails_closed_no_receipt(self) -> None:
        """Empty explanation → non-zero exit, NO receipt, NO ledger event."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            args = [
                "content",
                "advise-rendition",
                "AGENTS.md",
                "--consumer",
                "codex",
                "--score",
                "0.5",
                "--explanation",
                "   ",
            ]
            result = self._runner.invoke(main, args)

            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_receipts(), [], "no receipt on malformed (explanation-less) verdict")
            events = [e for e in _ledger_events() if e.get("event") == "rendition_advisor_verdict"]
            self.assertEqual(events, [], "no ledger event when the verdict is rejected")


if __name__ == "__main__":
    unittest.main()
