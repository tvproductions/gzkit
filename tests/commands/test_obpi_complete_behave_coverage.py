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
