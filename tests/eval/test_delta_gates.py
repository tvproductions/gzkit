"""Tests for eval-delta release gates.

Covers all 6 OBPI-0.0.5-03 requirements:
  REQ-1: Gate 2 includes eval results when eval datasets exist
  REQ-2: Gate 2 does not fail when eval datasets are absent
  REQ-3: Eval thresholds are configurable via config/
  REQ-4: Regression = dimension score drop > configured threshold vs baseline
  REQ-5: Gate failure output includes surface, dimension, baseline, current
  REQ-6: Eval gate results recorded via gate_checked_event()
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.eval.delta import (
    DimensionRegression,
    EvalDeltaResult,
    EvalThresholdConfig,
    SurfaceBaseline,
    check_regressions,
    format_regression_output,
    load_baseline,
    load_thresholds,
    save_baseline,
)
from gzkit.eval.runner import EvalSuiteScore, SurfaceScore


class TestThresholdConfig(unittest.TestCase):
    """REQ-3: Eval thresholds configurable via config/."""

    def test_load_default_thresholds(self) -> None:
        """Default threshold is 0.5 when no config file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_thresholds(Path(tmpdir) / "nonexistent.json")
            self.assertEqual(config.default_threshold, 0.5)

    def test_load_custom_thresholds(self) -> None:
        """Custom thresholds loaded from config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "eval_thresholds.json"
            config_path.write_text(
                json.dumps(
                    {
                        "schema": "gzkit.eval_thresholds.v1",
                        "default_threshold": 1.0,
                        "surface_thresholds": {"adr_eval": 0.25},
                    }
                ),
                encoding="utf-8",
            )
            config = load_thresholds(config_path)
            self.assertEqual(config.default_threshold, 1.0)
            self.assertEqual(config.surface_thresholds["adr_eval"], 0.25)

    def test_threshold_for_surface_with_override(self) -> None:
        """Per-surface threshold overrides the default."""
        config = EvalThresholdConfig(
            default_threshold=0.5,
            surface_thresholds={"rules": 0.1},
        )
        self.assertEqual(config.threshold_for("rules"), 0.1)
        self.assertEqual(config.threshold_for("adr_eval"), 0.5)

    def test_threshold_for_surface_without_override(self) -> None:
        """Surfaces without override use default threshold."""
        config = EvalThresholdConfig(default_threshold=0.75)
        self.assertEqual(config.threshold_for("instruction_eval"), 0.75)

    def test_real_config_loads(self) -> None:
        """The actual config/eval_thresholds.json loads successfully."""
        config = load_thresholds()
        self.assertIsInstance(config, EvalThresholdConfig)
        self.assertGreater(config.default_threshold, 0.0)


class TestBaselineStorage(unittest.TestCase):
    """Baseline save/load round-trip."""

    def test_save_and_load_baseline(self) -> None:
        """Baselines round-trip through JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            surface_score = SurfaceScore(
                surface="test_surface",
                case_scores=[],
                dimension_averages={"clarity": 3.5, "depth": 2.0},
                overall=2.75,
                cases_passed=1,
                cases_total=2,
            )
            save_baseline(surface_score, baselines_dir)
            loaded = load_baseline("test_surface", baselines_dir)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.surface, "test_surface")
            self.assertEqual(loaded.dimension_scores["clarity"], 3.5)
            self.assertEqual(loaded.dimension_scores["depth"], 2.0)

    def test_load_missing_baseline_returns_none(self) -> None:
        """Missing baseline returns None, not an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_baseline("nonexistent", Path(tmpdir))
            self.assertIsNone(result)


class TestDeltaComparison(unittest.TestCase):
    """REQ-4: Regression = dimension score drop > threshold vs baseline."""

    def _make_suite(self, surface: str, dim_avgs: dict[str, float]) -> EvalSuiteScore:
        """Build a minimal EvalSuiteScore for testing."""
        import statistics

        overall = round(statistics.mean(dim_avgs.values()), 2) if dim_avgs else 0.0
        ss = SurfaceScore(
            surface=surface,
            case_scores=[],
            dimension_averages=dim_avgs,
            overall=overall,
            cases_passed=1,
            cases_total=1,
        )
        return EvalSuiteScore(
            surface_scores=[ss],
            surfaces_scored=1,
            overall_score=overall,
            success=True,
        )

    def test_no_regression_within_threshold(self) -> None:
        """Score drop within threshold is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            # Baseline: clarity=3.5
            baseline = SurfaceBaseline(surface="test", dimension_scores={"clarity": 3.5})
            (baselines_dir / "test.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # Current: clarity=3.2 (drop of 0.3, within default 0.5 threshold)
            current = self._make_suite("test", {"clarity": 3.2})
            config = EvalThresholdConfig(default_threshold=0.5)
            result = check_regressions(current, config=config, baselines_dir=baselines_dir)
            self.assertTrue(result.passed)
            self.assertEqual(len(result.regressions), 0)

    def test_regression_exceeds_threshold(self) -> None:
        """Score drop exceeding threshold is detected as regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            baseline = SurfaceBaseline(surface="test", dimension_scores={"clarity": 3.5})
            (baselines_dir / "test.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # Current: clarity=2.5 (drop of 1.0, exceeds 0.5 threshold)
            current = self._make_suite("test", {"clarity": 2.5})
            config = EvalThresholdConfig(default_threshold=0.5)
            result = check_regressions(current, config=config, baselines_dir=baselines_dir)
            self.assertFalse(result.passed)
            self.assertEqual(len(result.regressions), 1)
            reg = result.regressions[0]
            self.assertEqual(reg.surface, "test")
            self.assertEqual(reg.dimension, "clarity")
            self.assertEqual(reg.baseline_score, 3.5)
            self.assertEqual(reg.current_score, 2.5)
            self.assertEqual(reg.delta, -1.0)

    def test_exact_threshold_is_not_regression(self) -> None:
        """Score drop exactly equal to threshold is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            baseline = SurfaceBaseline(surface="test", dimension_scores={"clarity": 3.0})
            (baselines_dir / "test.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # Drop of exactly 0.5 (threshold) — NOT a regression (must exceed)
            current = self._make_suite("test", {"clarity": 2.5})
            config = EvalThresholdConfig(default_threshold=0.5)
            result = check_regressions(current, config=config, baselines_dir=baselines_dir)
            self.assertTrue(result.passed)

    def test_per_surface_threshold_override(self) -> None:
        """Per-surface threshold takes precedence over default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            baseline = SurfaceBaseline(surface="strict", dimension_scores={"clarity": 3.0})
            (baselines_dir / "strict.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # Drop of 0.3 — within default 0.5 but exceeds strict 0.2
            current = self._make_suite("strict", {"clarity": 2.7})
            config = EvalThresholdConfig(
                default_threshold=0.5,
                surface_thresholds={"strict": 0.2},
            )
            result = check_regressions(current, config=config, baselines_dir=baselines_dir)
            self.assertFalse(result.passed)
            self.assertEqual(result.regressions[0].threshold, 0.2)

    def test_no_baselines_returns_pass(self) -> None:
        """No baselines → no regressions (pass)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            current = self._make_suite("test", {"clarity": 2.0})
            result = check_regressions(current, baselines_dir=Path(tmpdir))
            self.assertTrue(result.passed)
            self.assertEqual(result.surfaces_checked, 0)

    def test_score_improvement_is_not_regression(self) -> None:
        """Score improvement (positive delta) is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            baseline = SurfaceBaseline(surface="test", dimension_scores={"clarity": 2.0})
            (baselines_dir / "test.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            current = self._make_suite("test", {"clarity": 3.5})
            result = check_regressions(current, baselines_dir=baselines_dir)
            self.assertTrue(result.passed)

    def test_multiple_dimensions_partial_regression(self) -> None:
        """Only regressed dimensions are reported, not passing ones."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            baseline = SurfaceBaseline(
                surface="test",
                dimension_scores={"clarity": 3.5, "depth": 3.0, "coverage": 4.0},
            )
            (baselines_dir / "test.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # clarity: 3.5 → 3.3 (ok), depth: 3.0 → 3.5 (improved),
            # coverage: 4.0 → 2.0 (regression of 2.0)
            current = self._make_suite("test", {"clarity": 3.3, "depth": 3.5, "coverage": 2.0})
            config = EvalThresholdConfig(default_threshold=0.5)
            result = check_regressions(current, config=config, baselines_dir=baselines_dir)
            self.assertFalse(result.passed)
            self.assertEqual(len(result.regressions), 1)
            self.assertEqual(result.regressions[0].dimension, "coverage")


class TestRegressionOutput(unittest.TestCase):
    """REQ-5: Gate failure output includes surface, dimension, baseline, current."""

    def test_pass_output(self) -> None:
        result = EvalDeltaResult(regressions=[], surfaces_checked=3, passed=True)
        output = format_regression_output(result)
        self.assertIn("PASS", output)
        self.assertIn("3 surfaces", output)

    def test_fail_output_includes_details(self) -> None:
        """Failure output names surface, dimension, baseline, current scores."""
        result = EvalDeltaResult(
            regressions=[
                DimensionRegression(
                    surface="adr_eval",
                    dimension="problem_clarity",
                    baseline_score=3.5,
                    current_score=2.0,
                    delta=-1.5,
                    threshold=0.5,
                )
            ],
            surfaces_checked=1,
            passed=False,
        )
        output = format_regression_output(result)
        self.assertIn("FAIL", output)
        self.assertIn("adr_eval", output)
        self.assertIn("problem_clarity", output)
        self.assertIn("3.5", output)
        self.assertIn("2.0", output)

    def test_skipped_output(self) -> None:
        result = EvalDeltaResult(
            regressions=[],
            surfaces_checked=0,
            passed=True,
            skipped=True,
            skip_reason="no eval datasets",
        )
        output = format_regression_output(result)
        self.assertIn("SKIPPED", output)
        self.assertIn("no eval datasets", output)


class TestGateIntegration(unittest.TestCase):
    """REQ-1, REQ-2, REQ-6: Gate integration tests."""

    def test_eval_delta_skips_without_datasets(self) -> None:
        """REQ-2: _run_eval_delta returns True when no datasets exist."""
        from unittest.mock import MagicMock, patch

        from gzkit.commands.gates import _run_eval_delta

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            ledger = MagicMock()
            with patch("gzkit.commands.gates.console"):
                result = _run_eval_delta(project_root, ledger, "ADR-0.0.5")
            self.assertTrue(result)
            # REQ-6: gate result recorded
            ledger.append.assert_called_once()

    def test_eval_delta_skips_without_baselines(self) -> None:
        """REQ-2: _run_eval_delta returns True when datasets exist but no baselines."""
        from unittest.mock import MagicMock, patch

        from gzkit.commands.gates import _run_eval_delta

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            # Create a fake dataset so the "no datasets" check passes
            data_dir = project_root / "data" / "eval"
            data_dir.mkdir(parents=True)
            (data_dir / "dummy.json").write_text(
                json.dumps(
                    {
                        "surface": "instruction_eval",
                        "version": "1.0.0",
                        "description": "test",
                        "cases": [
                            {
                                "id": "t1",
                                "type": "golden_path",
                                "description": "test",
                                "input": {
                                    "agents_md": "# Agents\n\n## Project Identity\ntest\n",
                                    "claude_rules": ["x.md"],
                                    "github_instructions": ["y.md"],
                                    "gzkit_skills": ["z"],
                                    "command_docs_index": "# Commands\n\n- test\n",
                                },
                                "expected_output": {"success": True},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            ledger = MagicMock()
            with patch("gzkit.commands.gates.console"):
                result = _run_eval_delta(project_root, ledger, "ADR-0.0.5")
            self.assertTrue(result)
            ledger.append.assert_called_once()

    def test_eval_delta_detects_regression(self) -> None:
        """REQ-1: Gate 2 includes eval results and detects regression."""
        from unittest.mock import MagicMock, patch

        from gzkit.commands.gates import _run_eval_delta

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            data_dir = project_root / "data" / "eval"
            data_dir.mkdir(parents=True)
            baselines_dir = data_dir / "baselines"
            baselines_dir.mkdir()

            # Create a dataset
            (data_dir / "dummy.json").write_text(
                json.dumps(
                    {
                        "surface": "instruction_eval",
                        "version": "1.0.0",
                        "description": "test",
                        "cases": [
                            {
                                "id": "t1",
                                "type": "golden_path",
                                "description": "test",
                                "input": {
                                    "agents_md": "",
                                    "claude_rules": [],
                                    "github_instructions": [],
                                    "gzkit_skills": [],
                                    "command_docs_index": "",
                                },
                                "expected_output": {"success": False},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            # Create a high baseline so current scores will regress
            baseline = SurfaceBaseline(
                surface="instruction_eval",
                dimension_scores={
                    "completeness": 4.0,
                    "surface_coverage": 4.0,
                    "control_balance": 4.0,
                },
            )
            (baselines_dir / "instruction_eval.baseline.json").write_text(
                json.dumps(baseline.model_dump()), encoding="utf-8"
            )
            # Create config with tight threshold
            config_dir = project_root / "config"
            config_dir.mkdir()
            (config_dir / "eval_thresholds.json").write_text(
                json.dumps(
                    {
                        "schema": "gzkit.eval_thresholds.v1",
                        "default_threshold": 0.5,
                        "surface_thresholds": {},
                    }
                ),
                encoding="utf-8",
            )
            ledger = MagicMock()
            with patch("gzkit.commands.gates.console"):
                result = _run_eval_delta(project_root, ledger, "ADR-0.0.5")
            self.assertFalse(result)
            # REQ-6: gate result recorded as fail
            ledger.append.assert_called_once()


if __name__ == "__main__":
    unittest.main()
