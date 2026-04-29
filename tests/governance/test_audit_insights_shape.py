"""Fixture-level tests for ``audit_insights_shape`` (GHI #358).

These tests exercise the audit against synthetic temp trees so the
shape rules are isolated from the live ``.gzkit/insights/agent-insights.jsonl``.
The repo-lock test in ``test_promoted_advisory_audits.py`` continues to gate
current repo state; this module gates the scan semantics.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.governance.trust_audits import audit_insights_shape
from gzkit.insights import InsightRecord


class InsightRecordModelTests(unittest.TestCase):
    """Pydantic model accepts canonical records and rejects drift."""

    def test_minimal_required_fields_accepted(self) -> None:
        record = InsightRecord(
            ts="2026-04-29T11:00:00Z",
            type="defect",
            scope="example/scope",
            summary="example finding",
        )
        self.assertEqual(record.scope, "example/scope")

    def test_full_record_accepted(self) -> None:
        record = InsightRecord(
            ts="2026-04-29T11:00:00+00:00",
            type="defect-resolution",
            scope="example/scope",
            summary="example resolution",
            id="DEFECT-2026-04-29-example",
            adr_id="ADR-0.0.1",
            obpi_id="OBPI-0.0.1-01",
            evidence=["uv run gz status"],
            next_action="follow up",
            verification=["uv run gz validate"],
            result="resolved",
        )
        self.assertEqual(record.type, "defect-resolution")

    def test_date_only_ts_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            InsightRecord(
                ts="2026-04-29",
                type="defect",
                scope="example",
                summary="example",
            )

    def test_naive_datetime_without_tz_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            InsightRecord(
                ts="2026-04-29T11:00:00",
                type="defect",
                scope="example",
                summary="example",
            )

    def test_unknown_type_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            InsightRecord(
                ts="2026-04-29T11:00:00Z",
                type="advisory",
                scope="example",
                summary="example",
            )

    def test_extra_field_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            InsightRecord(
                ts="2026-04-29T11:00:00Z",
                type="defect",
                scope="example",
                summary="example",
                resolution="legacy field",
            )

    def test_evidence_must_be_list_of_str(self) -> None:
        with self.assertRaises(ValidationError):
            InsightRecord(
                ts="2026-04-29T11:00:00Z",
                type="defect",
                scope="example",
                summary="example",
                evidence={"key": "value"},
            )


class InsightShapeAuditTests(unittest.TestCase):
    """Audit walks `.gzkit/insights/agent-insights.jsonl` line-by-line."""

    def _write_insights(self, root: Path, lines: list[dict[str, object]]) -> Path:
        target = root / ".gzkit" / "insights" / "agent-insights.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "\n".join(json.dumps(line) for line in lines) + "\n",
            encoding="utf-8",
        )
        return target

    def test_clean_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_insights(
                root,
                [
                    {
                        "ts": "2026-04-29T11:00:00Z",
                        "type": "defect",
                        "scope": "example",
                        "summary": "example finding",
                    },
                    {
                        "ts": "2026-04-29T12:00:00Z",
                        "type": "defect-resolution",
                        "scope": "example",
                        "summary": "example fix",
                        "verification": ["uv run gz validate"],
                        "result": "resolved",
                    },
                ],
            )
            errors = audit_insights_shape(root)
            self.assertEqual(errors, [])

    def test_missing_required_field_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_insights(
                root,
                [{"type": "defect", "scope": "example", "summary": "missing ts"}],
            )
            errors = audit_insights_shape(root)
            self.assertTrue(
                any(e.type == "insights_shape" for e in errors),
                msg=f"expected insights_shape error, got: {errors}",
            )

    def test_unknown_type_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_insights(
                root,
                [
                    {
                        "ts": "2026-04-29T11:00:00Z",
                        "type": "advisory",
                        "scope": "example",
                        "summary": "example",
                    }
                ],
            )
            errors = audit_insights_shape(root)
            self.assertTrue(any(e.type == "insights_shape" for e in errors))

    def test_nested_evidence_object_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_insights(
                root,
                [
                    {
                        "ts": "2026-04-29T11:00:00Z",
                        "type": "defect",
                        "scope": "example",
                        "summary": "example",
                        "evidence": {"cmd": "x", "error": "y"},
                    }
                ],
            )
            errors = audit_insights_shape(root)
            self.assertTrue(any(e.type == "insights_shape" for e in errors))

    def test_extra_field_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_insights(
                root,
                [
                    {
                        "ts": "2026-04-29T11:00:00Z",
                        "type": "defect",
                        "scope": "example",
                        "summary": "example",
                        "adr_ids": ["ADR-0.0.1", "ADR-0.0.2"],
                    }
                ],
            )
            errors = audit_insights_shape(root)
            self.assertTrue(any(e.type == "insights_shape" for e in errors))

    def test_malformed_json_line_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".gzkit" / "insights" / "agent-insights.jsonl"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{not json\n", encoding="utf-8")
            errors = audit_insights_shape(root)
            self.assertTrue(any(e.type == "insights_shape" for e in errors))

    def test_blank_lines_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / ".gzkit" / "insights" / "agent-insights.jsonl"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(
                    {
                        "ts": "2026-04-29T11:00:00Z",
                        "type": "defect",
                        "scope": "example",
                        "summary": "example",
                    }
                )
                + "\n\n   \n",
                encoding="utf-8",
            )
            errors = audit_insights_shape(root)
            self.assertEqual(errors, [])

    def test_missing_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = audit_insights_shape(root)
            self.assertEqual(errors, [])

    def test_error_type_is_in_policy_breach_set(self) -> None:
        """Schema drift exits 3 (policy breach), not 1 (general error).

        Per `cli.md`: exit 3 = policy breach. The audit's error type must
        be a member of `_POLICY_BREACH_ERROR_TYPES` so the dispatcher
        promotes the exit code.
        """
        from gzkit.commands.validate_cmd import _POLICY_BREACH_ERROR_TYPES

        self.assertIn("insights_shape", _POLICY_BREACH_ERROR_TYPES)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
