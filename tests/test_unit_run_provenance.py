"""GHI #1154 — the unit tier's green must witness that tests actually ran.

``unittest-parallel`` exits 0 for a suite that collected nothing and for a suite
whose every test was skipped, so a return code alone cannot witness the claim
"Tests pass". The judge reads the run's own summary and a declared collection
floor.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.quality import QualityResult, run_tests
from gzkit.unit_run_provenance import judge_behave_run, judge_executed, judge_unit_run


def _summary(ran: int, verdict: str = "OK") -> str:
    noun = "test" if ran == 1 else "tests"
    return f"Running x\n\n{'-' * 70}\nRan {ran} {noun} in 1.0s\n\n{verdict}\n"


def _floor(root: Path, body: str) -> None:
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "unit_collection_floor.json").write_text(body, encoding="utf-8")


class TestJudgeUnitRun(unittest.TestCase):
    def test_executed_tests_pass(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(judge_unit_run(_summary(10), Path(td)))

    def test_partial_skips_still_pass(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(judge_unit_run(_summary(10, "OK (skipped=3)"), Path(td)))

    def test_zero_tests_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIn("0 tests", judge_unit_run(_summary(0), Path(td)) or "")

    def test_all_skipped_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            reason = judge_unit_run(_summary(4, "OK (skipped=4)"), Path(td))
            self.assertIn("skipped", reason or "")

    def test_missing_summary_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIn("summary", judge_unit_run("no summary here\n", Path(td)) or "")

    def test_summary_found_when_failures_carry_counts(self):
        with tempfile.TemporaryDirectory() as td:
            out = _summary(7, "FAILED (failures=1, skipped=2)")
            self.assertIsNone(judge_unit_run(out, Path(td)))

    def test_collection_below_floor_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _floor(root, json.dumps({"min_tests": 100}))
            reason = judge_unit_run(_summary(99), root)
            self.assertIn("floor", reason or "")

    def test_collection_at_floor_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _floor(root, json.dumps({"min_tests": 100}))
            self.assertIsNone(judge_unit_run(_summary(100), root))

    def test_malformed_floor_fails_closed(self):
        for body in ("{not json", json.dumps({"min_tests": "many"}), json.dumps({})):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                _floor(root, body)
                self.assertIn("floor", judge_unit_run(_summary(500), root) or "")

    def test_no_floor_declared_checks_only_execution(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(judge_unit_run(_summary(1), Path(td)))


class TestJudgeExecuted(unittest.TestCase):
    """The floor-free witness shared by every lane that runs a covering test."""

    def test_one_executed_test_passes(self):
        self.assertIsNone(judge_executed(_summary(1)))

    def test_zero_and_all_skipped_and_missing_are_refused(self):
        for out in (_summary(0), _summary(2, "OK (skipped=2)"), "nothing\n"):
            with self.subTest(out=out):
                self.assertIsNotNone(judge_executed(out))


class TestJudgeBehaveRun(unittest.TestCase):
    def test_a_passed_scenario_is_witnessed(self):
        out = "1 feature passed, 0 failed, 0 skipped\n1 scenario passed, 0 failed, 0 skipped\n"
        self.assertIsNone(judge_behave_run(out))

    def test_no_selected_scenario_is_refused(self):
        out = "0 features passed, 0 failed, 0 skipped\n0 scenarios passed, 0 failed, 0 skipped\n"
        self.assertIn("scenario", judge_behave_run(out) or "")

    def test_only_skipped_scenarios_are_refused(self):
        out = "0 features passed, 0 failed, 1 skipped\n0 scenarios passed, 0 failed, 1 skipped\n"
        self.assertIsNotNone(judge_behave_run(out))

    def test_missing_summary_is_refused(self):
        self.assertIsNotNone(judge_behave_run("no summary\n"))


class TestRunTestsWitnessesExecution(unittest.TestCase):
    """run_tests must not report success on a zero-exit run that tested nothing."""

    def _run(self, stderr: str, returncode: int = 0) -> QualityResult:
        fake = QualityResult(
            success=returncode == 0, command="x", stdout="", stderr=stderr, returncode=returncode
        )
        with (
            tempfile.TemporaryDirectory() as td,
            mock.patch("gzkit.quality.run_command", return_value=fake),
        ):
            return run_tests(Path(td))

    def test_zero_exit_with_no_tests_is_not_success(self):
        result = self._run(_summary(0))
        self.assertFalse(result.success)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("0 tests", result.stderr)

    def test_zero_exit_with_all_skipped_is_not_success(self):
        self.assertFalse(self._run(_summary(2, "OK (skipped=2)")).success)

    def test_real_run_passes(self):
        self.assertTrue(self._run(_summary(50)).success)

    def test_nonzero_exit_is_untouched(self):
        result = self._run(_summary(50, "FAILED (failures=1)"), returncode=1)
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
