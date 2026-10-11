"""A release pushes only behind the full quality sweep (GHI #1191).

Operator ruling 2026-10-11: the per-change gate runs only the tests a change
touches, and a release is one of the places the full sweep runs. So the release
push must run `gz check --full` and refuse to push when it fails.
"""

import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.common import GzCliError
from gzkit.commands.patch_release import _push_release
from gzkit.quality import QualityResult


def _result(success: bool) -> QualityResult:
    return QualityResult(
        success=success,
        command="gz check --full",
        stdout="" if success else "  ❌ Behave 31.20s",
        stderr="",
        returncode=0 if success else 1,
    )


class TestReleasePushRunsTheFullSweep(unittest.TestCase):
    def _push(self, sweep_passes: bool):
        with (
            patch("gzkit.commands.patch_release.console", Console(file=StringIO())),
            patch("gzkit.quality.run_command", return_value=_result(sweep_passes)) as sweep,
            patch("gzkit.commands.patch_release.git_cmd", return_value=(0, "", "")) as git,
        ):
            try:
                _push_release(Path("."))
            except GzCliError as exc:
                return sweep, git, exc
        return sweep, git, None

    def test_the_gate_is_the_full_sweep(self) -> None:
        sweep, _git, _exc = self._push(sweep_passes=True)
        argv = sweep.call_args.args[0]
        self.assertEqual(argv[1:], ["-m", "gzkit", "check", "--full"])

    def test_a_passing_sweep_pushes(self) -> None:
        _sweep, git, exc = self._push(sweep_passes=True)
        self.assertIsNone(exc)
        self.assertEqual(git.call_args.args[1:], ("push", "origin", "main"))

    def test_a_failing_sweep_refuses_the_push_and_names_the_failing_step(self) -> None:
        _sweep, git, exc = self._push(sweep_passes=False)
        self.assertIsNotNone(exc)
        self.assertIn("Behave", str(exc))
        git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
