"""TDD proofs for the mechanical insight-append helper — OBPI-0.0.72-03 (GHI #575).

REQ-derived from the brief's Acceptance Criteria, not from the implementation:
the helper constructs an ``InsightRecord`` first (so a missing required field
fails closed at construction), then serializes with ``exclude_none`` and appends
exactly one round-trippable line to a caller-supplied path.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.insights.append import append_insight_record
from gzkit.insights.model import InsightRecord
from gzkit.traceability import covers


class TestInsightAppend(unittest.TestCase):
    @covers("REQ-0.0.72-03-01")
    def test_appends_one_schema_valid_line_for_payload(self) -> None:
        """A defect payload writes exactly one line that validates as InsightRecord."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "insights.jsonl"
            append_insight_record(
                type="defect",
                scope="gzkit.insights.append",
                summary="hand-authored insight lines drift from the schema",
                evidence=["uv run -m unittest tests.governance.test_insight_append"],
                path=path,
            )
            self.assertTrue(path.exists(), "the helper must write the insights line to disk")
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            record = InsightRecord.model_validate(json.loads(lines[0]))
            self.assertEqual(record.type, "defect")
            self.assertEqual(record.scope, "gzkit.insights.append")
            self.assertEqual(
                record.summary,
                "hand-authored insight lines drift from the schema",
            )
            self.assertEqual(
                record.evidence,
                ["uv run -m unittest tests.governance.test_insight_append"],
            )
            self.assertIsNotNone(record.ts)

    @covers("REQ-0.0.72-03-02")
    def test_emitted_line_round_trips_and_missing_field_fails_closed(self) -> None:
        """The actual emitted line re-validates with no divergence; a missing
        required field raises ValidationError before anything reaches disk."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "insights.jsonl"
            returned = append_insight_record(
                type="improvement",
                scope="obpi-pipeline",
                summary="governed author verb replaces hand-authored appends",
                path=path,
            )
            self.assertTrue(path.exists(), "the helper must write the insights line to disk")
            emitted = path.read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(returned, emitted)
            record = InsightRecord.model_validate_json(emitted)
            self.assertEqual(record.type, "improvement")
            self.assertEqual(record.scope, "obpi-pipeline")
            # exclude_none: unset optional fields never serialize as null keys.
            self.assertNotIn("adr_id", json.loads(emitted))

            # A missing/empty required field fails closed at construction.
            with self.assertRaises(ValidationError):
                append_insight_record(
                    type="improvement",
                    scope="",
                    summary="empty scope must fail closed",
                    path=path,
                )
            # The failed construction wrote no second line.
            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
