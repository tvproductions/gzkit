"""Tests for the evaluation-justify-binding gate (OBPI-0.0.26-02).

Gate fires when an ``adr-evaluation`` ledger event has low dimension scores
or enough red-team challenges and no qualifying ``gz-justify`` artifact exists.

@covers OBPI-0.0.26-02-justify-binding-gate
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
from gzkit.traceability import covers


class TestEvaluationJustifyBindingGate(unittest.TestCase):
    """Verify the evaluation-justify-binding gate returns correct results."""

    def _write_ledger_event(
        self,
        ledger_path: Path,
        artifact_id: str,
        dimensions: dict,
        red_team_challenges_fired: list | None = None,
    ) -> None:
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "adr-evaluation",
            "id": artifact_id,
            "dimensions": dimensions,
            "scores": dimensions,
            "weighted_total": sum(dimensions.values()) / len(dimensions),
            "red_team_challenges_fired": red_team_challenges_fired or [],
            "evaluator_persona": "main-session",
            "ts": "2026-01-01T00:00:00+00:00",
        }
        ledger_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

    @covers("REQ-0.0.26-02-01")
    def test_low_score_no_justify_artifact_exits_3(self) -> None:
        """Low score + no justify artifact → ValidationError naming the failing dimension."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_ledger_event(
                ledger_path,
                "ADR-0.0.26",
                {"clarity": 1.5, "structure": 4.0},
            )

            # Write threshold config
            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0, "Expected a ValidationError for low score")
            error = result[0]
            self.assertEqual(error.type, "evaluation-justify-binding")
            self.assertIn("clarity", error.message)

    @covers("REQ-0.0.26-02-02")
    def test_red_team_count_no_justify_artifact_exits_3(self) -> None:
        """Sufficient red-team challenges with no justify artifact returns ValidationError."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_ledger_event(
                ledger_path,
                "ADR-0.0.26",
                {"clarity": 4.0, "structure": 4.0},
                red_team_challenges_fired=["challenge-1", "challenge-2", "challenge-3"],
            )

            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0, "Expected a ValidationError for red-team count")
            self.assertEqual(result[0].type, "evaluation-justify-binding")

    @covers("REQ-0.0.26-02-03")
    def test_trigger_fires_justify_artifact_present_exits_0(self) -> None:
        """Trigger condition met but justify artifact exists — gate passes (empty list)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_ledger_event(
                ledger_path,
                "ADR-0.0.26",
                {"clarity": 1.5},
            )

            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            # Create a justify artifact for ADR-0.0.26
            justify_dir = root / "artifacts" / "justify"
            justify_dir.mkdir(parents=True, exist_ok=True)
            (justify_dir / "ADR-0.0.26-2026-01-01T00-00-00.md").write_text(
                "# Justify\n\nRationale here.", encoding="utf-8"
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")

    @covers("REQ-0.0.26-02-04")
    def test_no_trigger_all_scores_high_exits_0(self) -> None:
        """All dimensions >= threshold and no red-team challenges — gate passes (empty list)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_ledger_event(
                ledger_path,
                "ADR-0.0.26",
                {"clarity": 4.0, "structure": 5.0},
                red_team_challenges_fired=[],
            )

            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")

    @covers("REQ-0.0.26-02-05")
    def test_threshold_config_reflected(self) -> None:
        """Custom threshold config is respected — score passing at 3.0 fails at 4.0."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            # Score 3.5 is above 3.0 (passes) but below 4.0 (fails)
            self._write_ledger_event(
                ledger_path,
                "ADR-0.0.26",
                {"clarity": 3.5},
                red_team_challenges_fired=[],
            )

            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            # Override threshold to 4.0 — score 3.5 should now trigger the gate
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 4.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertGreater(
                len(result), 0, "Expected gate to fire when score is below custom threshold"
            )
            self.assertEqual(result[0].type, "evaluation-justify-binding")

    def test_no_adr_evaluation_events_returns_empty(self) -> None:
        """Empty ledger (no adr-evaluation events) — gate passes (empty list)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # No ledger file at all

            data_dir = root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            (data_dir / "eval_feedback_thresholds.json").write_text(
                json.dumps({"low_score_threshold": 3.0, "red_team_count_threshold": 3}),
                encoding="utf-8",
            )

            result = validate_evaluation_justify_binding("ADR-0.0.26", project_root=root)

            self.assertEqual(result, [], f"Expected empty list but got: {result}")
