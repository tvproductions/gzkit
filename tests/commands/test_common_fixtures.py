"""Contract tests for the shared test-fixture helpers in ``tests.commands.common``.

These assert properties the fixtures must hold for *other* tests to be sound,
so a regression here is a regression in every suite that builds a repo fixture.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.commands.common import _init_git_repo


class TestFixtureRepoQuiescence(unittest.TestCase):
    """A fixture repo must not run background maintenance.

    Several suites build one repo per module and ``shutil.copytree`` it per
    test. Git's post-command auto-maintenance writes a transient
    ``.git/objects/maintenance.lock``; ``copytree`` enumerates the directory,
    the lock is removed before the copy reads it, and the copy dies with
    ``shutil.Error: [Errno 2] No such file or directory``. The failure is a
    race, so it is intermittent — CI run 32230349611 failed on it while the
    next commit passed. Quiescing the fixture removes the racing writer.
    """

    def _config(self, root: Path, key: str) -> tuple[int, str]:
        result = subprocess.run(
            ["git", "config", "--get", key],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, result.stdout.strip()

    def test_fixture_repo_disables_auto_gc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            code, value = self._config(root, "gc.auto")
        self.assertEqual(code, 0, "gc.auto is unset, so git may auto-gc a fixture repo")
        self.assertEqual(int(value), 0, "gc.auto must be 0 so no gc races a copytree")

    def test_fixture_repo_disables_auto_maintenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            code, value = self._config(root, "maintenance.auto")
        self.assertEqual(
            code, 0, "maintenance.auto is unset, so git may run maintenance on a fixture repo"
        )
        self.assertEqual(
            value.lower(),
            "false",
            "maintenance.auto must be false; it is what writes objects/maintenance.lock",
        )

    def test_fixture_repo_is_still_usable_after_quiescing(self) -> None:
        """The quiesce must not break the repo the fixture exists to provide."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha = _init_git_repo(root)
            log = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            ).stdout
        self.assertTrue(sha, "helper must still return the initial short SHA")
        self.assertIn(sha, log, "returned SHA must name the commit the fixture created")


if __name__ == "__main__":
    unittest.main()
