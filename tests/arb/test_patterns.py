"""Tests for gzkit.arb.patterns.

@covers REQ-0.25.0-33-03
"""

import json
import tempfile
import unittest
from pathlib import Path


def _write_lint_receipt(directory: Path, name: str, findings: list[dict]) -> None:
    payload = {
        "schema": "gzkit.arb.lint_receipt.v1",
        "tool": {"name": "ruff", "version": "0.5.0"},
        "run_id": name,
        "timestamp_utc": "2026-04-14T00:00:00Z",
        "git": {"commit": "abc1234"},
        "findings": findings,
        "exit_status": 1 if findings else 0,
    }
    (directory / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")


class TestCollectPatterns(unittest.TestCase):
    """collect_patterns extracts recurring rules as PatternCandidates."""

    def test_empty_directory(self) -> None:
        from gzkit.arb.patterns import collect_patterns

        with tempfile.TemporaryDirectory() as tmpdir:
            report = collect_patterns(root=Path(tmpdir))

        self.assertEqual(report.scanned_receipts, 0)
        self.assertEqual(report.candidates, [])

    def test_recurring_rule_becomes_candidate(self) -> None:
        from gzkit.arb.patterns import collect_patterns

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [
                    {"rule": "F401", "path": "a.py", "line": 1, "message": "unused"},
                    {"rule": "F401", "path": "b.py", "line": 1, "message": "unused"},
                ],
            )
            report = collect_patterns(root=directory)

        self.assertEqual(report.scanned_receipts, 1)
        self.assertEqual(len(report.candidates), 1)
        candidate = report.candidates[0]
        self.assertEqual(candidate.rule, "F401")
        self.assertEqual(candidate.count, 2)
        self.assertIn("unused", candidate.anti_pattern.lower())

    def test_single_occurrence_ignored(self) -> None:
        """Rules with <2 occurrences are not candidates."""
        from gzkit.arb.patterns import collect_patterns

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [{"rule": "E501", "path": "a.py", "line": 1, "message": "x"}],
            )
            report = collect_patterns(root=directory)

        self.assertEqual(report.candidates, [])

    def test_prefix_guidance_for_up_sim_perf(self) -> None:
        """Rules matching prefix categories (UP*/SIM*/PERF*/COM*) fall back to prefix guidance."""
        from gzkit.arb.patterns import collect_patterns

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [
                    {"rule": "UP006", "path": "a.py", "line": 1, "message": "up"},
                    {"rule": "UP006", "path": "b.py", "line": 2, "message": "up"},
                ],
            )
            report = collect_patterns(root=directory)

        self.assertEqual(len(report.candidates), 1)
        candidate = report.candidates[0]
        self.assertEqual(candidate.rule, "UP006")
        # Guidance falls back to the UP prefix entry
        self.assertIn("outdated", candidate.anti_pattern.lower())

    def test_report_is_frozen_pydantic(self) -> None:
        from pydantic import ValidationError

        from gzkit.arb.patterns import PatternReport

        report = PatternReport(scanned_receipts=0, total_findings=0, candidates=[])
        with self.assertRaises(ValidationError):
            report.scanned_receipts = 99

    def test_render_patterns_markdown_produces_table(self) -> None:
        from gzkit.arb.patterns import collect_patterns, render_patterns_markdown

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [
                    {"rule": "F401", "path": "a.py", "line": 1, "message": "x"},
                    {"rule": "F401", "path": "b.py", "line": 1, "message": "x"},
                ],
            )
            report = collect_patterns(root=directory)
            output = render_patterns_markdown(report)

        self.assertIn("# ARB Pattern Extraction Report", output)
        self.assertIn("| Anti-pattern", output)
        self.assertIn("F401", output)
