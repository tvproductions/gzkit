"""A scenario's `mock.patch` must not outlive the scenario (CI red, 2026-08-29).

`features/patch_release.feature` asserted `gz patch release --dry-run` exits 0.
That command fails closed when `gh auth status` is non-zero, and CI's `gh` is
never authenticated -- yet the scenario passed for months. It passed because
`evaluation_feedback_loop_steps` calls `mock.patch("<mod>.subprocess.run").start()`
and only ever stopped those patchers from one of its OWN `Given` steps. Since
`<mod>.subprocess` IS the singleton `subprocess` module, the patch was global,
and it stayed installed for every later scenario in the process -- silently
supplying a fake `gh` to a feature that never asked for one.

Behave sharding (GHI #906) split the two features into different processes and
the borrowed precondition vanished. The deeper defect is that the gate's answer
depended on shard membership at all, and shards are planned by FILE BYTE SIZE --
so an ordinary edit to an unrelated `.feature` could move a scenario between
shards and flip the verdict. `after_scenario` now calls `mock.patch.stopall()`.

These tests observe the STATE (is the patch still installed after teardown),
never the presence of the teardown call -- a presence check would pass against
a hook that called `stopall()` on an object that had nothing registered.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]


def _load_environment():
    """Import `features/environment.py`, which is a behave hook file, not a module."""
    spec = importlib.util.spec_from_file_location(
        "behave_environment_under_test", REPO / "features" / "environment.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Scenario:
    """Minimal stand-in for behave's scenario object."""

    tags: tuple[str, ...] = ()
    name = "isolation probe"


class _Context:
    """Minimal stand-in for behave's context object."""


def _context_in_a_temp_workspace(cwd: Path) -> _Context:
    context = _Context()
    context._original_cwd = cwd
    context._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-isolation-probe-"))
    return context


class TestPatchersDoNotOutliveTheirScenario(unittest.TestCase):
    """`after_scenario` must leave the process with no patches installed."""

    def test_a_started_patcher_is_stopped_by_after_scenario(self) -> None:
        env = _load_environment()
        original = subprocess.run
        mock.patch("subprocess.run", return_value=None).start()
        self.assertIsNot(subprocess.run, original, "probe is inert: the patch never took effect")

        # Sample the state BEFORE the safety-net cleanup. Asserting after the
        # `finally` would make this test pass against a hook that tears nothing
        # down, because the cleanup would have done the hook's job first.
        try:
            env.after_scenario(_context_in_a_temp_workspace(Path.cwd()), _Scenario())
            survived = subprocess.run is not original
        finally:
            mock.patch.stopall()

        self.assertFalse(
            survived,
            "a patcher started by a step survived after_scenario; the next "
            "scenario inherits it and can pass on a precondition it never set",
        )

    def test_patching_via_a_module_attribute_reaches_the_shared_module(self) -> None:
        """Why the leak was global rather than confined to one command module.

        This is the fact that makes the teardown load-bearing: the step modules
        patch `"<some.module>.subprocess.run"`, which reads as module-local and
        is not. Were it truly local, sharding would never have changed a verdict.
        """
        original = subprocess.run
        patcher = mock.patch("gzkit.utils.subprocess.run", return_value=None)
        patcher.start()
        try:
            self.assertIsNot(
                subprocess.run,
                original,
                "patching a module's `subprocess.run` attribute no longer "
                "rebinds the shared module; the leak's blast radius has changed",
            )
        finally:
            patcher.stop()


class TestPatchReleaseStandsAlone(unittest.TestCase):
    """The feature that borrowed a fake `gh` must now pass on its own.

    Reproduces CI exactly: ONE feature file, its own process, and a `gh` that
    cannot authenticate. Asserting on the feature file's text instead would only
    witness that a `Given` line is present, which is the presence-check failure
    `AGENTS.md` names -- a step can be written and still not arrange the thing
    it claims to. Running it is the only way to observe that it does.
    """

    def test_the_feature_passes_alone_with_gh_unauthenticated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="gzkit-empty-gh-") as empty_gh:
            env = os.environ.copy()
            # An empty config dir plus blank tokens is how the runner looks: `gh`
            # is on PATH and answers "not logged into any GitHub hosts". If `gh`
            # is absent entirely the probe returns 127 and the point still holds.
            env["GH_CONFIG_DIR"] = empty_gh
            env["GH_TOKEN"] = ""
            env["GITHUB_TOKEN"] = ""
            proc = subprocess.run(
                [sys.executable, "-m", "behave", "features/patch_release.feature"],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                # Windows runners hand back cp1252 for some tool output; without
                # this the decode raises mid-assert (`.claude/rules/cross-platform.md`
                # § Subprocess reads, GHI #582).
                encoding="utf-8",
                errors="replace",
                check=False,
            )

        self.assertEqual(
            proc.returncode,
            0,
            "features/patch_release.feature fails in isolation without ambient "
            "gh authentication, so it can only pass by borrowing a precondition "
            "from whatever else happens to share its shard:\n"
            f"{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}",
        )


if __name__ == "__main__":
    unittest.main()
