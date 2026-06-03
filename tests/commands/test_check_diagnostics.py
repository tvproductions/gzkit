"""Regression test: `gz check` must surface a failing step's captured output.

Direct-fix. The aggregator previously discarded every step's stdout/stderr,
so a failing Test step surfaced only as ``❌ Test`` with no test name — the
cause of 28 consecutive undiagnosable red CI runs (only `uv run gz check` runs
in CI, so the swallowed unittest output never reached the log).
"""

from __future__ import annotations

import io
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

import gzkit.commands.quality as quality_mod
from gzkit.quality import QualityResult


class TestCheckFailingStepDiagnostics(unittest.TestCase):
    """A failing step's captured output must reach the operator (and CI log)."""

    def test_failing_step_output_is_surfaced(self):
        marker = "FAIL: test_some_marker_xyz (pkg.mod.Case.test_some_marker_xyz)"

        def _failing_step(_root: Path) -> QualityResult:
            return QualityResult(
                command="uv run -m unittest discover tests",
                success=False,
                stdout=marker,
                stderr="",
                returncode=1,
            )

        buf = io.StringIO()
        recording = Console(file=buf, width=240, force_terminal=False)
        no_drift = MagicMock()
        no_drift.has_drift = False

        with (
            patch.object(quality_mod, "console", recording),
            patch.object(quality_mod, "_build_check_steps", return_value=[("Test", _failing_step)]),
            patch.object(quality_mod, "get_project_root", return_value=Path(".")),
            patch("gzkit.quality.run_drift_advisory", return_value=no_drift),
            patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError),
            self.assertRaises(SystemExit),
        ):
            quality_mod.check()

        self.assertIn(marker, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
