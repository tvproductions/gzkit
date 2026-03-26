"""Tests for eval harness scoring and runner.

Verifies that:
- Scorers produce numeric 0-4 dimension scores
- Golden-path fixtures score high (>= 3.0 average)
- Edge-case fixtures score low (< 3.0 average)
- The runner aggregates scores correctly
- run_eval() returns a QualityResult
"""

import unittest

from gzkit.eval.datasets import KNOWN_SURFACES, load_dataset
from gzkit.eval.runner import EvalSuiteScore, SurfaceScore, run_eval_suite
from gzkit.eval.scorer import CaseScore, DimensionResult, score_case
from gzkit.quality import QualityResult, run_eval


class TestDimensionScoring(unittest.TestCase):
    """Verify scorers produce valid dimension results."""

    def test_all_surfaces_have_scorers(self) -> None:
        for surface in KNOWN_SURFACES:
            with self.subTest(surface=surface):
                ds = load_dataset(surface)
                case = ds.cases[0]
                results = score_case(surface, dict(case.input))
                self.assertGreater(len(results), 0)

    def test_scores_are_0_to_4(self) -> None:
        for surface in KNOWN_SURFACES:
            ds = load_dataset(surface)
            for case in ds.cases:
                with self.subTest(case=case.id):
                    results = score_case(surface, dict(case.input))
                    for dim in results:
                        self.assertIsInstance(dim, DimensionResult)
                        self.assertGreaterEqual(dim.score, 0)
                        self.assertLessEqual(dim.score, 4)

    def test_unknown_surface_raises(self) -> None:
        with self.assertRaises(KeyError):
            score_case("nonexistent", {})


class TestGoldenPathScoring(unittest.TestCase):
    """Verify golden-path fixtures score high."""

    def test_golden_paths_score_above_threshold(self) -> None:
        for surface in KNOWN_SURFACES:
            ds = load_dataset(surface)
            golden_cases = [c for c in ds.cases if c.type == "golden_path"]
            for case in golden_cases:
                with self.subTest(case=case.id):
                    results = score_case(surface, dict(case.input))
                    scores = [d.score for d in results]
                    avg = sum(scores) / len(scores) if scores else 0
                    self.assertGreaterEqual(
                        avg,
                        3.0,
                        f"Golden path {case.id} scored {avg:.2f}, expected >= 3.0",
                    )


class TestEdgeCaseScoring(unittest.TestCase):
    """Verify edge-case fixtures score lower than golden paths."""

    def test_edge_cases_score_below_golden(self) -> None:
        for surface in KNOWN_SURFACES:
            ds = load_dataset(surface)
            golden_cases = [c for c in ds.cases if c.type == "golden_path"]
            edge_cases = [c for c in ds.cases if c.type == "edge_case"]
            if not golden_cases or not edge_cases:
                continue

            golden_scores = []
            for case in golden_cases:
                results = score_case(surface, dict(case.input))
                golden_scores.append(sum(d.score for d in results) / len(results))
            golden_avg = sum(golden_scores) / len(golden_scores)

            for case in edge_cases:
                with self.subTest(case=case.id):
                    results = score_case(surface, dict(case.input))
                    scores = [d.score for d in results]
                    edge_avg = sum(scores) / len(scores) if scores else 0
                    self.assertLess(
                        edge_avg,
                        golden_avg,
                        f"Edge case {case.id} ({edge_avg:.2f}) should score "
                        f"below golden ({golden_avg:.2f})",
                    )


class TestEvalRunner(unittest.TestCase):
    """Verify the eval suite runner."""

    def test_run_all_surfaces(self) -> None:
        result = run_eval_suite()
        self.assertIsInstance(result, EvalSuiteScore)
        self.assertEqual(result.surfaces_scored, len(KNOWN_SURFACES))

    def test_run_single_surface(self) -> None:
        result = run_eval_suite(surfaces=["instruction_eval"])
        self.assertEqual(result.surfaces_scored, 1)
        self.assertEqual(result.surface_scores[0].surface, "instruction_eval")

    def test_surface_score_structure(self) -> None:
        result = run_eval_suite()
        for ss in result.surface_scores:
            self.assertIsInstance(ss, SurfaceScore)
            self.assertGreater(ss.cases_total, 0)
            self.assertGreater(len(ss.dimension_averages), 0)
            for dim, avg in ss.dimension_averages.items():
                self.assertIsInstance(dim, str)
                self.assertGreaterEqual(avg, 0.0)
                self.assertLessEqual(avg, 4.0)

    def test_case_scores_typed(self) -> None:
        result = run_eval_suite(surfaces=["adr_eval"])
        for ss in result.surface_scores:
            for cs in ss.case_scores:
                self.assertIsInstance(cs, CaseScore)
                self.assertIn(cs.surface, KNOWN_SURFACES)

    def test_overall_score_in_range(self) -> None:
        result = run_eval_suite()
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 4.0)


class TestQualityIntegration(unittest.TestCase):
    """Verify run_eval() returns QualityResult."""

    def test_run_eval_returns_quality_result(self) -> None:
        from pathlib import Path

        result = run_eval(Path("."))
        self.assertIsInstance(result, QualityResult)
        self.assertEqual(result.command, "eval harness")
        self.assertIn("surfaces scored", result.stdout)

    def test_run_eval_has_surface_details(self) -> None:
        from pathlib import Path

        result = run_eval(Path("."))
        for surface in KNOWN_SURFACES:
            self.assertIn(surface, result.stdout)


class TestDeterminism(unittest.TestCase):
    """Verify eval results are deterministic across runs."""

    def test_same_results_twice(self) -> None:
        result1 = run_eval_suite()
        result2 = run_eval_suite()
        self.assertEqual(result1.overall_score, result2.overall_score)
        self.assertEqual(result1.success, result2.success)
        for s1, s2 in zip(result1.surface_scores, result2.surface_scores, strict=True):
            self.assertEqual(s1.overall, s2.overall)


if __name__ == "__main__":
    unittest.main()
