"""Tests for regression detection — OBPI-0.0.5-04.

Covers all 5 acceptance criteria:
  REQ-0.0.5-04-01: Baseline store in artifacts/baselines/ persists eval scores
  REQ-0.0.5-04-02: Comparison engine produces RegressionReport with before/after
  REQ-0.0.5-04-03: First run with no baseline creates baseline, reports "no prior baseline"
  REQ-0.0.5-04-04: Regression reports serializable to ARB-compatible JSON
  REQ-0.0.5-04-05: Baseline updates require explicit invocation
"""

import json
import statistics
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.eval.regression import (
    DimensionDelta,
    EvalBaseline,
    RegressionReceiptPayload,
    RegressionReport,
    build_receipt,
    compare_scores,
    create_initial_baselines,
    load_baseline,
    save_baseline,
)
from gzkit.eval.runner import EvalSuiteScore, SurfaceScore


def _make_surface_score(surface: str, dim_avgs: dict[str, float]) -> SurfaceScore:
    """Build a minimal SurfaceScore for testing."""
    overall = round(statistics.mean(dim_avgs.values()), 2) if dim_avgs else 0.0
    return SurfaceScore(
        surface=surface,
        case_scores=[],
        dimension_averages=dim_avgs,
        overall=overall,
        cases_passed=1,
        cases_total=1,
    )


def _make_suite(surfaces: list[SurfaceScore]) -> EvalSuiteScore:
    """Build a minimal EvalSuiteScore from surface scores."""
    overalls = [s.overall for s in surfaces]
    grand = round(statistics.mean(overalls), 2) if overalls else 0.0
    return EvalSuiteScore(
        surface_scores=surfaces,
        surfaces_scored=len(surfaces),
        overall_score=grand,
        success=True,
    )


class TestBaselineStore(unittest.TestCase):
    """REQ-0.0.5-04-01: Baseline store persists eval scores keyed by commit and surface."""

    def test_save_and_load_round_trip(self) -> None:
        """Baselines round-trip through JSON with all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            ss = _make_surface_score("instruction_eval", {"clarity": 3.5, "depth": 2.0})

            path = save_baseline(ss, "1.0.0", baselines_dir=baselines_dir, commit_hash="abc123")

            self.assertTrue(path.exists())
            self.assertEqual(path.name, "instruction_eval.baseline.json")

            loaded = load_baseline("instruction_eval", baselines_dir)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.surface, "instruction_eval")
            self.assertEqual(loaded.commit_hash, "abc123")
            self.assertEqual(loaded.dataset_version, "1.0.0")
            self.assertEqual(loaded.dimension_scores["clarity"], 3.5)
            self.assertEqual(loaded.dimension_scores["depth"], 2.0)
            self.assertIsInstance(loaded.timestamp, str)

    def test_baseline_stored_as_json(self) -> None:
        """Baseline files are valid JSON with all required fields (REQ-02)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            ss = _make_surface_score("adr_eval", {"problem_clarity": 4.0})
            save_baseline(ss, "2.0.0", baselines_dir=baselines_dir, commit_hash="def456")

            raw = json.loads((baselines_dir / "adr_eval.baseline.json").read_text(encoding="utf-8"))
            self.assertIn("surface", raw)
            self.assertIn("commit_hash", raw)
            self.assertIn("timestamp", raw)
            self.assertIn("dimension_scores", raw)
            self.assertIn("dataset_version", raw)
            self.assertEqual(raw["commit_hash"], "def456")
            self.assertEqual(raw["dataset_version"], "2.0.0")

    def test_load_missing_baseline_returns_none(self) -> None:
        """Missing baseline returns None (not an error)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_baseline("nonexistent", Path(tmpdir))
            self.assertIsNone(result)

    def test_baseline_model_is_frozen(self) -> None:
        """EvalBaseline model is immutable."""
        baseline = EvalBaseline(
            surface="test",
            commit_hash="abc",
            timestamp="2026-01-01T00:00:00Z",
            dimension_scores={"x": 1.0},
            dataset_version="1.0.0",
        )
        with self.assertRaises(ValidationError):
            baseline.surface = "modified"  # type: ignore[misc]

    def test_baseline_model_forbids_extra(self) -> None:
        """EvalBaseline rejects extra fields."""
        with self.assertRaises((TypeError, ValidationError)):
            EvalBaseline(
                surface="test",
                commit_hash="abc",
                timestamp="2026-01-01T00:00:00Z",
                dimension_scores={"x": 1.0},
                dataset_version="1.0.0",
                extra_field="should fail",  # type: ignore[call-arg]
            )


class TestComparisonEngine(unittest.TestCase):
    """REQ-0.0.5-04-02: Comparison engine produces RegressionReport."""

    def test_regression_detected(self) -> None:
        """Score drop exceeding threshold is detected as regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            # Save a high baseline
            ss_baseline = _make_surface_score("test", {"clarity": 3.5, "depth": 3.0})
            save_baseline(ss_baseline, "1.0.0", baselines_dir=baselines_dir, commit_hash="old")

            # Current scores with regression in clarity
            ss_current = _make_surface_score("test", {"clarity": 2.0, "depth": 3.0})
            suite = _make_suite([ss_current])

            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)

            self.assertFalse(report.passed)
            self.assertEqual(len(report.regressions), 1)
            self.assertEqual(report.regressions[0].dimension, "clarity")
            self.assertEqual(report.regressions[0].baseline_score, 3.5)
            self.assertEqual(report.regressions[0].current_score, 2.0)
            self.assertEqual(report.regressions[0].delta, -1.5)
            self.assertTrue(report.regressions[0].regressed)

    def test_no_regression_within_threshold(self) -> None:
        """Score drop within threshold is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            ss_baseline = _make_surface_score("test", {"clarity": 3.5})
            save_baseline(ss_baseline, "1.0.0", baselines_dir=baselines_dir, commit_hash="old")

            ss_current = _make_surface_score("test", {"clarity": 3.2})
            suite = _make_suite([ss_current])

            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)
            self.assertTrue(report.passed)
            self.assertEqual(len(report.regressions), 0)

    def test_exact_threshold_not_regression(self) -> None:
        """Score drop exactly equal to threshold is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            ss_baseline = _make_surface_score("test", {"clarity": 3.0})
            save_baseline(ss_baseline, "1.0.0", baselines_dir=baselines_dir, commit_hash="old")

            ss_current = _make_surface_score("test", {"clarity": 2.5})
            suite = _make_suite([ss_current])

            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)
            self.assertTrue(report.passed)

    def test_improvement_not_regression(self) -> None:
        """Score improvement is not a regression."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            ss_baseline = _make_surface_score("test", {"clarity": 2.0})
            save_baseline(ss_baseline, "1.0.0", baselines_dir=baselines_dir, commit_hash="old")

            ss_current = _make_surface_score("test", {"clarity": 3.5})
            suite = _make_suite([ss_current])

            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)
            self.assertTrue(report.passed)
            self.assertEqual(len(report.deltas), 1)
            self.assertFalse(report.deltas[0].regressed)

    def test_multiple_surfaces_partial_regression(self) -> None:
        """Reports regressions per-dimension across multiple surfaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            # Surface A: high baseline
            save_baseline(
                _make_surface_score("a", {"x": 4.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="old",
            )
            # Surface B: moderate baseline
            save_baseline(
                _make_surface_score("b", {"y": 3.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="old",
            )

            suite = _make_suite(
                [
                    _make_surface_score("a", {"x": 2.0}),  # regression
                    _make_surface_score("b", {"y": 3.0}),  # no change
                ]
            )

            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)
            self.assertFalse(report.passed)
            self.assertEqual(report.surfaces_checked, 2)
            self.assertEqual(len(report.regressions), 1)
            self.assertEqual(report.regressions[0].surface, "a")

    def test_report_model_is_frozen(self) -> None:
        """RegressionReport model is immutable (frozen=True)."""
        report = RegressionReport(
            timestamp="2026-01-01T00:00:00Z",
            commit_hash="abc",
            passed=True,
        )
        with self.assertRaises(ValidationError):
            report.passed = False  # type: ignore[misc]

    def test_report_model_forbids_extra(self) -> None:
        """RegressionReport rejects extra fields (extra='forbid')."""
        with self.assertRaises((TypeError, ValidationError)):
            RegressionReport(
                timestamp="2026-01-01T00:00:00Z",
                commit_hash="abc",
                passed=True,
                extra_field="bad",  # type: ignore[call-arg]
            )

    def test_deltas_include_all_dimensions(self) -> None:
        """Report deltas list includes both regressed and non-regressed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            save_baseline(
                _make_surface_score("test", {"a": 3.0, "b": 3.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="old",
            )
            suite = _make_suite([_make_surface_score("test", {"a": 2.0, "b": 3.0})])
            report = compare_scores(suite, threshold=0.5, baselines_dir=baselines_dir)
            self.assertEqual(len(report.deltas), 2)
            regressed = [d for d in report.deltas if d.regressed]
            self.assertEqual(len(regressed), 1)


class TestFirstRunHandling(unittest.TestCase):
    """REQ-0.0.5-04-03: First run with no baseline reports 'no prior baseline'."""

    def test_no_baseline_reports_no_prior(self) -> None:
        """Surfaces with no baseline appear in no_prior_baseline list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = _make_suite([_make_surface_score("new_surface", {"x": 3.0})])
            report = compare_scores(suite, baselines_dir=Path(tmpdir))
            self.assertTrue(report.passed)
            self.assertIn("new_surface", report.no_prior_baseline)
            self.assertEqual(report.surfaces_checked, 0)

    def test_comparison_does_not_auto_create_baseline(self) -> None:
        """compare_scores() never creates baselines automatically (REQ-06)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            suite = _make_suite([_make_surface_score("new_surface", {"x": 3.0})])
            compare_scores(suite, baselines_dir=baselines_dir)
            # No baseline file should be created
            self.assertFalse((baselines_dir / "new_surface.baseline.json").exists())

    def test_create_initial_baselines(self) -> None:
        """create_initial_baselines() creates baselines for surfaces without one."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            suite = _make_suite(
                [
                    _make_surface_score("new_a", {"x": 3.0}),
                    _make_surface_score("new_b", {"y": 2.0}),
                ]
            )
            paths = create_initial_baselines(
                suite, "1.0.0", baselines_dir=baselines_dir, commit_hash="abc"
            )
            self.assertEqual(len(paths), 2)
            self.assertTrue((baselines_dir / "new_a.baseline.json").exists())
            self.assertTrue((baselines_dir / "new_b.baseline.json").exists())

    def test_create_initial_skips_existing(self) -> None:
        """create_initial_baselines() does not overwrite existing baselines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            # Pre-create a baseline
            save_baseline(
                _make_surface_score("existing", {"x": 4.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="old",
            )
            suite = _make_suite(
                [
                    _make_surface_score("existing", {"x": 1.0}),
                    _make_surface_score("new", {"y": 2.0}),
                ]
            )
            paths = create_initial_baselines(
                suite, "2.0.0", baselines_dir=baselines_dir, commit_hash="new"
            )
            # Only the new surface gets a baseline
            self.assertEqual(len(paths), 1)
            self.assertEqual(paths[0].name, "new.baseline.json")
            # Existing baseline unchanged
            loaded = load_baseline("existing", baselines_dir)
            self.assertEqual(loaded.commit_hash, "old")


class TestArbReceiptCompatibility(unittest.TestCase):
    """REQ-0.0.5-04-04: Regression reports serializable to ARB-compatible JSON."""

    def test_receipt_serializes_to_json(self) -> None:
        """Receipt payload produces valid JSON."""
        report = RegressionReport(
            timestamp="2026-01-01T00:00:00Z",
            commit_hash="abc123",
            surfaces_checked=2,
            regressions=[
                DimensionDelta(
                    surface="test",
                    dimension="clarity",
                    baseline_score=3.5,
                    current_score=2.0,
                    delta=-1.5,
                    regressed=True,
                )
            ],
            passed=False,
        )
        receipt = build_receipt(report)
        json_str = receipt.to_arb_json()
        parsed = json.loads(json_str)

        self.assertEqual(parsed["schema"], "gzkit.regression_receipt.v1")
        self.assertEqual(parsed["tool"], "eval-regression")
        self.assertEqual(parsed["commit_hash"], "abc123")
        self.assertEqual(parsed["regressions_found"], 1)
        self.assertFalse(parsed["passed"])
        self.assertEqual(len(parsed["regression_details"]), 1)
        self.assertEqual(parsed["regression_details"][0]["surface"], "test")

    def test_receipt_pass_case(self) -> None:
        """Passing report produces a clean receipt."""
        report = RegressionReport(
            timestamp="2026-01-01T00:00:00Z",
            commit_hash="def456",
            surfaces_checked=3,
            passed=True,
        )
        receipt = build_receipt(report)
        self.assertTrue(receipt.passed)
        self.assertEqual(receipt.regressions_found, 0)
        self.assertEqual(receipt.regression_details, [])

    def test_receipt_with_baselines_created(self) -> None:
        """Receipt includes baselines_created when first run creates them."""
        report = RegressionReport(
            timestamp="2026-01-01T00:00:00Z",
            commit_hash="abc",
            passed=True,
            baseline_created=True,
            no_prior_baseline=["new_surface"],
        )
        receipt = build_receipt(report)
        self.assertEqual(receipt.baselines_created, ["new_surface"])

    def test_receipt_model_is_frozen(self) -> None:
        """Receipt model is immutable."""
        receipt = RegressionReceiptPayload(commit_hash="abc", passed=True)
        with self.assertRaises(ValidationError):
            receipt.passed = False  # type: ignore[misc]


class TestExplicitUpdateControl(unittest.TestCase):
    """REQ-0.0.5-04-05: Baseline updates require explicit invocation."""

    def test_save_baseline_overwrites(self) -> None:
        """Explicit save_baseline() overwrites existing baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            # Save initial
            save_baseline(
                _make_surface_score("test", {"x": 3.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="v1",
            )
            # Explicit update
            save_baseline(
                _make_surface_score("test", {"x": 4.0}),
                "2.0.0",
                baselines_dir=baselines_dir,
                commit_hash="v2",
            )
            loaded = load_baseline("test", baselines_dir)
            self.assertEqual(loaded.commit_hash, "v2")
            self.assertEqual(loaded.dataset_version, "2.0.0")
            self.assertEqual(loaded.dimension_scores["x"], 4.0)

    def test_comparison_never_updates_baseline(self) -> None:
        """compare_scores() does not modify existing baselines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir)
            save_baseline(
                _make_surface_score("test", {"x": 3.0}),
                "1.0.0",
                baselines_dir=baselines_dir,
                commit_hash="original",
            )
            # Run comparison with different scores
            suite = _make_suite([_make_surface_score("test", {"x": 4.0})])
            compare_scores(suite, baselines_dir=baselines_dir)

            # Baseline unchanged
            loaded = load_baseline("test", baselines_dir)
            self.assertEqual(loaded.commit_hash, "original")
            self.assertEqual(loaded.dimension_scores["x"], 3.0)


if __name__ == "__main__":
    unittest.main()
