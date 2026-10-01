"""Unit tests for behave-ref dispatch in the REQ-coverage gate (GHI #395).

``_any_covering_test_passes`` previously routed every ``TestRef`` through
``uv run -m unittest``, producing a malformed target for ``.feature`` refs
(scenario names contain spaces, parens, double-colon) and marking every
BDD-only REQ as ``failing-cover``.  The fix adds ``_behave_ref_passes``
and dispatches on ``ref.file_path.endswith(".feature")``.

Coverage map:

| REQ              | Test class                                              |
|------------------|---------------------------------------------------------|
| REQ-0.0.25-01-06 | TestBehaveRefPasses.test_passes_for_passing_scenario    |
| REQ-0.0.25-01-05 | TestBehaveRefPasses.test_failing_marks_failing_cover    |
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.commands.obpi_complete import _any_covering_test_passes, _behave_ref_passes
from gzkit.governance.req_coverage import TestRef
from gzkit.traceability import covers

_BEHAVE_PASSED = "1 feature passed, 0 failed, 0 skipped\n1 scenario passed, 0 failed, 0 skipped\n"
_BEHAVE_NONE = "0 features passed, 0 failed, 0 skipped\n0 scenarios passed, 0 failed, 0 skipped\n"


def _completed(returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


class TestBehaveRefPasses(unittest.TestCase):
    """Direct unit tests for ``_behave_ref_passes`` and the dispatch in
    ``_any_covering_test_passes`` for ``.feature``-backed refs."""

    def _feature_ref(self, feature_path: str = "features/foo.feature") -> TestRef:
        return TestRef(
            qualified_name="My Feature::Some Scenario (with parens)",
            file_path=feature_path,
            line=42,
        )

    @covers("REQ-0.0.25-01-06")
    def test_passes_for_passing_scenario(self) -> None:
        """A behave run that exits 0 causes _behave_ref_passes to return True."""
        ref = self._feature_ref()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = _BEHAVE_PASSED

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            patch_target = "gzkit.commands.obpi_complete.subprocess.run"
            with patch(patch_target, return_value=mock_result) as mock_run:
                result = _behave_ref_passes(ref, root, "REQ-0.0.25-01-06")

        self.assertTrue(result)
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        self.assertIn("behave", cmd_args)
        joined = " ".join(cmd_args)
        self.assertIn("REQ-0.0.25-01-06", joined)
        self.assertIn("features/foo.feature", joined)
        # The summary is the witness that a scenario ran (GHI #1154).
        self.assertNotIn("--no-summary", cmd_args)

    @covers("REQ-0.0.25-01-05")
    def test_failing_marks_failing_cover(self) -> None:
        """A behave run that exits non-zero causes _any_covering_test_passes to return False."""
        ref = self._feature_ref()
        mock_result = MagicMock()
        mock_result.returncode = 1

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("gzkit.commands.obpi_complete.subprocess.run", return_value=mock_result):
                result = _any_covering_test_passes([ref], root, req_id="REQ-0.0.25-01-05")

        self.assertFalse(result)


class TestCoveringRunMustExecute(unittest.TestCase):
    """GHI #1154 — exit 0 shows a covering run did not fail, not that it ran.

    A skipped unittest and a behave tag selecting no scenario both exit 0, so
    the gate must read the run's own summary before counting it as proof.
    """

    def _unit_ref(self) -> TestRef:
        return TestRef(qualified_name="TestX.test_y", file_path="tests/test_x.py", line=1)

    def _feature_ref(self) -> TestRef:
        return TestRef(qualified_name="F::S", file_path="features/foo.feature", line=1)

    def _passes(self, ref: TestRef, completed: MagicMock) -> bool:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch("gzkit.commands.obpi_complete.subprocess.run", return_value=completed),
        ):
            root = Path(tmp)
            (root / "tests").mkdir()
            ref = ref.model_copy(update={"file_path": str(root / ref.file_path)})
            return _any_covering_test_passes([ref], root, req_id="REQ-0.0.1-01-01")

    def test_executed_unittest_counts(self) -> None:
        ok = _completed(0, stderr="Ran 1 test in 0.1s\n\nOK\n")
        self.assertTrue(self._passes(self._unit_ref(), ok))

    def test_skipped_unittest_does_not_count(self) -> None:
        skipped = _completed(0, stderr="Ran 1 test in 0.1s\n\nOK (skipped=1)\n")
        self.assertFalse(self._passes(self._unit_ref(), skipped))

    def test_unittest_that_ran_nothing_does_not_count(self) -> None:
        self.assertFalse(self._passes(self._unit_ref(), _completed(0, stderr="Ran 0 tests\nOK\n")))

    def test_behave_with_no_selected_scenario_does_not_count(self) -> None:
        self.assertFalse(self._passes(self._feature_ref(), _completed(0, stdout=_BEHAVE_NONE)))

    def test_behave_with_a_passed_scenario_counts(self) -> None:
        self.assertTrue(self._passes(self._feature_ref(), _completed(0, stdout=_BEHAVE_PASSED)))
