"""Regression test: `gz check` must surface a failing step's captured output.

Direct-fix. The aggregator previously discarded every step's stdout/stderr,
so a failing Test step surfaced only as ``❌ Test`` with no test name — the
cause of 28 consecutive undiagnosable red CI runs (only `uv run gz check` runs
in CI, so the swallowed unittest output never reached the log).
"""

from __future__ import annotations

import io
import tempfile
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

        # The full scope runs the stubbed step list as given. The per-change
        # scope would drop `Test` and run the real changed-test selection in its
        # place (GHI #1191), in every project since the scope policy ships in
        # the package (GHI #1192). The scratch root keeps the run's cache writes
        # out of the repository.
        with (
            tempfile.TemporaryDirectory() as scratch,
            patch.object(quality_mod, "console", recording),
            patch.object(quality_mod, "_build_check_steps", return_value=[("Test", _failing_step)]),
            patch.object(quality_mod, "get_project_root", return_value=Path(scratch)),
            patch("gzkit.quality.run_drift_advisory", return_value=no_drift),
            patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError),
            self.assertRaises(SystemExit),
        ):
            quality_mod.check(full=True)

        self.assertIn(marker, buf.getvalue())


class TestPerChangePassMessageOutputForm(unittest.TestCase):
    """What a passing per-change run tells the operator about the steps it dropped."""

    def test_the_message_names_the_dropped_steps_and_claims_no_ci(self) -> None:
        # output-contract: the message ships to every project that installs
        # gzkit, and such a project has no CI of gzkit's (GHI #1192). It says
        # how to run the dropped steps; it does not say something already does.
        buf = io.StringIO()
        recording = Console(file=buf, width=400, force_terminal=False)
        with (
            tempfile.TemporaryDirectory() as scratch,
            patch.object(quality_mod, "console", recording),
            patch.object(quality_mod, "_record_pass"),
        ):
            quality_mod._record_and_announce_pass(Path(scratch), scope="change")

        out = buf.getvalue()
        for step in quality_mod._scope_skips("change"):
            self.assertIn(step, out)
        self.assertIn("run `gz check --full` in CI and before a release", out)
        self.assertNotIn("CI runs", out)


if __name__ == "__main__":
    unittest.main()
