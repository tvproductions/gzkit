"""gz insights remember command tests — OBPI-0.0.72-03 (GHI #575).

REQ-derived from the brief's Acceptance Criteria, not from the implementation:
the verb appends exactly one InsightRecord-valid line via the mechanical
helper, and fails closed (non-zero exit, no line written) on an empty
``--summary`` or an out-of-enum ``--type``.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.insights.model import InsightRecord
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_STORE = Path(".gzkit") / "insights" / "agent-insights.jsonl"


def _lines() -> list[str]:
    if not _STORE.exists():
        return []
    return [ln for ln in _STORE.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TestInsightsRemember(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.72-03-05")
    def test_appends_one_valid_line_for_improvement_payload(self) -> None:
        """A valid payload appends exactly one InsightRecord-valid line; exit 0."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main,
                [
                    "insights",
                    "remember",
                    "--type",
                    "improvement",
                    "--scope",
                    "obpi-pipeline",
                    "--summary",
                    "governed author verb replaces hand-authored appends",
                    "--evidence",
                    "uv run -m unittest tests.commands.test_insights_cmd",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            lines = _lines()
            self.assertEqual(len(lines), 1)
            record = InsightRecord.model_validate(json.loads(lines[0]))
            self.assertEqual(record.type, "improvement")
            self.assertEqual(record.scope, "obpi-pipeline")
            self.assertEqual(
                record.evidence,
                ["uv run -m unittest tests.commands.test_insights_cmd"],
            )

    @covers("REQ-0.0.72-03-05")
    def test_empty_summary_fails_closed_writes_no_line(self) -> None:
        """An empty --summary exits non-zero and writes no line."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main,
                [
                    "insights",
                    "remember",
                    "--type",
                    "improvement",
                    "--scope",
                    "obpi-pipeline",
                    "--summary",
                    "",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_lines(), [])

    @covers("REQ-0.0.72-03-05")
    def test_out_of_enum_type_fails_closed_writes_no_line(self) -> None:
        """An out-of-enum --type exits non-zero and writes no line."""
        with self._runner.isolated_filesystem():
            result = self._runner.invoke(
                main,
                [
                    "insights",
                    "remember",
                    "--type",
                    "bogus-kind",
                    "--scope",
                    "obpi-pipeline",
                    "--summary",
                    "should never be written",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_lines(), [])


if __name__ == "__main__":
    unittest.main()
