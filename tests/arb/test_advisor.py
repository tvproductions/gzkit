"""Tests for gzkit.arb.advisor.

@covers REQ-0.25.0-33-03
"""

import json
import tempfile
import unittest
from pathlib import Path


def _write_lint_receipt(
    directory: Path,
    name: str,
    findings: list[dict],
    exit_status: int = 1,
) -> None:
    payload = {
        "schema": "gzkit.arb.lint_receipt.v1",
        "tool": {"name": "ruff", "version": "0.5.0"},
        "run_id": name,
        "timestamp_utc": "2026-04-14T00:00:00Z",
        "git": {"commit": "abc1234"},
        "findings": findings,
        "findings_total": len(findings),
        "exit_status": exit_status,
    }
    (directory / f"{name}.json").write_text(json.dumps(payload), encoding="utf-8")


class TestCollectArbAdvice(unittest.TestCase):
    """collect_arb_advice aggregates recent receipts and recommends actions."""

    def test_empty_directory_returns_zero_state(self) -> None:
        from gzkit.arb.advisor import collect_arb_advice

        with tempfile.TemporaryDirectory() as tmpdir:
            advice = collect_arb_advice(root=Path(tmpdir))

        self.assertEqual(advice.scanned_receipts, 0)
        self.assertEqual(advice.failed_receipts, 0)
        self.assertEqual(advice.findings_total, 0)
        self.assertEqual(advice.top_rules, [])
        self.assertIn("No findings in recent receipts.", advice.recommendations)

    def test_style_dominant_receipts(self) -> None:
        from gzkit.arb.advisor import collect_arb_advice

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [
                    {"rule": "E501", "path": "a.py", "line": 1, "message": "line too long"},
                    {"rule": "W291", "path": "b.py", "line": 2, "message": "trailing ws"},
                    {"rule": "I001", "path": "c.py", "line": 3, "message": "isort"},
                ],
            )

            advice = collect_arb_advice(root=directory)

        self.assertEqual(advice.scanned_receipts, 1)
        self.assertEqual(advice.failed_receipts, 1)
        self.assertEqual(advice.findings_total, 3)
        style_reco = any("Style-dominant" in rec for rec in advice.recommendations)
        self.assertTrue(style_reco, msg=advice.recommendations)

    def test_correctness_rules_trigger_recommendation(self) -> None:
        from gzkit.arb.advisor import collect_arb_advice

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [{"rule": "F401", "path": "a.py", "line": 1, "message": "unused import"}],
            )

            advice = collect_arb_advice(root=directory)

        self.assertTrue(
            any("Correctness-class" in rec for rec in advice.recommendations),
            msg=advice.recommendations,
        )

    def test_tidy_nudge_references_gz_arb_form(self) -> None:
        """Tidy nudge must reference `gz arb tidy`, never `opsdev`."""
        from gzkit.arb.advisor import collect_arb_advice

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            _write_lint_receipt(
                directory,
                "r1",
                [{"rule": "E501", "path": "a.py", "line": 1, "message": "x"}],
            )

            advice = collect_arb_advice(root=directory)

        tidy_nudges = [rec for rec in advice.recommendations if "tidy" in rec.lower()]
        self.assertEqual(len(tidy_nudges), 1)
        self.assertIn("gz arb tidy", tidy_nudges[0])
        self.assertNotIn("opsdev", tidy_nudges[0])

    def test_limit_honored(self) -> None:
        from gzkit.arb.advisor import collect_arb_advice

        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            for i in range(5):
                _write_lint_receipt(
                    directory,
                    f"r{i}",
                    [{"rule": "E501", "path": f"p{i}.py", "line": 1, "message": "x"}],
                )

            advice = collect_arb_advice(root=directory, limit=2)

        self.assertEqual(advice.scanned_receipts, 2)

    def test_advice_is_frozen_pydantic(self) -> None:
        from pydantic import ValidationError

        from gzkit.arb.advisor import ArbAdvice

        advice = ArbAdvice(
            scanned_receipts=0,
            failed_receipts=0,
            findings_total=0,
            top_rules=[],
            top_paths=[],
            recommendations=[],
        )
        with self.assertRaises(ValidationError):
            advice.scanned_receipts = 5
