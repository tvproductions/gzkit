"""``gzkit.git_spawn_boundary`` — the predicate behind the git-fixture-isolation fence.

GHI #977.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.git_spawn_boundary import git_spawns_outside_boundary


def _tree(tmp: str, source: str) -> Path:
    tests = Path(tmp) / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text(source, encoding="utf-8")
    return tests


class TestGitSpawnsOutsideBoundary(unittest.TestCase):
    def test_literal_git_spawn_without_env_is_an_offender(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tests = _tree(tmp, 'import subprocess\nsubprocess.run(["git", "init"], cwd=".")\n')
            self.assertEqual(git_spawns_outside_boundary(tests), ["tests/test_x.py:2"])

    def test_boundary_call_and_bound_name_are_inside(self) -> None:
        source = (
            "import subprocess\n"
            'subprocess.check_output(["git", "-C", "x", "log"], env=_isolated_git_env())\n'
            "env = _isolated_git_env()\n"
            'subprocess.Popen(["git", "status"], env=env)\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(git_spawns_outside_boundary(_tree(tmp, source)), [])

    def test_inherited_environ_passed_explicitly_is_still_outside(self) -> None:
        """``env=os.environ`` inherits exactly what the boundary exists to drop."""
        source = 'import os, subprocess\nsubprocess.run(["git", "init"], env=os.environ)\n'
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(git_spawns_outside_boundary(_tree(tmp, source)), ["tests/test_x.py:2"])

    def test_non_git_spawns_and_parameter_argv_are_out_of_scope(self) -> None:
        source = (
            "import subprocess\n"
            'subprocess.run(["uv", "run", "x"])\n'
            "def run(args):\n"
            "    return subprocess.run(args)\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(git_spawns_outside_boundary(_tree(tmp, source)), [])

    def test_unparseable_file_is_reported_not_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                git_spawns_outside_boundary(_tree(tmp, "def broken(:\n")),
                ["tests/test_x.py:0 (unparseable)"],
            )


if __name__ == "__main__":
    unittest.main()
