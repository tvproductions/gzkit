"""Tests for OBPI audit prior state reading (GHI #97).

@covers ADR-0.19.0
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.obpi_audit_cmd import _read_prior_audits


class TestReadPriorAudits(unittest.TestCase):
    """Table-driven tests for _read_prior_audits."""

    def test_missing_ledger_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(result, {})

    def test_empty_ledger_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "obpi-audit.jsonl").write_text("", encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(result, {})

    def test_single_entry(self):
        entry = {
            "type": "obpi-audit",
            "timestamp": "2026-03-22T00:00:00Z",
            "obpi_id": "OBPI-0.19.0-01",
            "adr_id": "ADR-0.19.0",
            "criteria_evaluated": [{"criterion": "Tests pass", "result": "PASS"}],
            "evidence": {"coverage_percent": 46.0},
        }
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "obpi-audit.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(len(result), 1)
            self.assertIn("OBPI-0.19.0-01", result)
            self.assertEqual(result["OBPI-0.19.0-01"]["timestamp"], "2026-03-22T00:00:00Z")

    def test_last_entry_wins(self):
        """When multiple entries exist for the same OBPI, the last one wins."""
        early = {
            "type": "obpi-audit",
            "timestamp": "2026-03-20T00:00:00Z",
            "obpi_id": "OBPI-0.1.0-01",
            "adr_id": "ADR-0.1.0",
            "criteria_evaluated": [{"criterion": "Tests pass", "result": "FAIL"}],
            "evidence": {"coverage_percent": 30.0},
        }
        late = {
            "type": "obpi-audit",
            "timestamp": "2026-03-22T00:00:00Z",
            "obpi_id": "OBPI-0.1.0-01",
            "adr_id": "ADR-0.1.0",
            "criteria_evaluated": [{"criterion": "Tests pass", "result": "PASS"}],
            "evidence": {"coverage_percent": 50.0},
        }
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            content = json.dumps(early) + "\n" + json.dumps(late) + "\n"
            (logs / "obpi-audit.jsonl").write_text(content, encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(result["OBPI-0.1.0-01"]["timestamp"], "2026-03-22T00:00:00Z")
            self.assertEqual(result["OBPI-0.1.0-01"]["evidence"]["coverage_percent"], 50.0)

    def test_multiple_obpis(self):
        entries = [
            {"type": "obpi-audit", "obpi_id": "OBPI-0.1.0-01", "timestamp": "2026-03-20T00:00:00Z"},
            {"type": "obpi-audit", "obpi_id": "OBPI-0.1.0-02", "timestamp": "2026-03-21T00:00:00Z"},
            {"type": "obpi-audit", "obpi_id": "OBPI-0.1.0-03", "timestamp": "2026-03-22T00:00:00Z"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            content = "\n".join(json.dumps(e) for e in entries) + "\n"
            (logs / "obpi-audit.jsonl").write_text(content, encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(len(result), 3)

    def test_malformed_lines_skipped(self):
        good = {
            "type": "obpi-audit",
            "obpi_id": "OBPI-0.1.0-01",
            "timestamp": "2026-03-22T00:00:00Z",
        }
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            content = "not json\n" + json.dumps(good) + "\n{broken\n"
            (logs / "obpi-audit.jsonl").write_text(content, encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(len(result), 1)
            self.assertIn("OBPI-0.1.0-01", result)

    def test_non_audit_entries_ignored(self):
        audit = {
            "type": "obpi-audit",
            "obpi_id": "OBPI-0.1.0-01",
            "timestamp": "2026-03-22T00:00:00Z",
        }
        other = {"type": "adr_created", "adr_id": "ADR-0.1.0", "timestamp": "2026-03-20T00:00:00Z"}
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            content = json.dumps(other) + "\n" + json.dumps(audit) + "\n"
            (logs / "obpi-audit.jsonl").write_text(content, encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(len(result), 1)

    def test_blank_lines_skipped(self):
        entry = {
            "type": "obpi-audit",
            "obpi_id": "OBPI-0.1.0-01",
            "timestamp": "2026-03-22T00:00:00Z",
        }
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            content = "\n\n" + json.dumps(entry) + "\n\n"
            (logs / "obpi-audit.jsonl").write_text(content, encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(len(result), 1)

    def test_entry_without_obpi_id_skipped(self):
        entry = {"type": "obpi-audit", "timestamp": "2026-03-22T00:00:00Z"}
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "obpi-audit.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")
            result = _read_prior_audits(Path(tmp))
            self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
