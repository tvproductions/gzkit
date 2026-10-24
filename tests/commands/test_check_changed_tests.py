"""The per-change gate runs the tests the change touches (GHI #1191).

Operator ruling 2026-10-11: the per-change gate drops the whole unit tier and
runs the changed tests in its place. These tests derive from that issue's
acceptance evidence: the selection must see a change that is already committed
(the pre-push hook runs after the commit), a deleted test module is not a test
to run, the selection goes to the canonical runner one exact module at a time,
and a selected test that runs the gate cannot start a second run.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS
from gzkit.commands import quality
from gzkit.quality import QualityResult
from tests.commands.common import _isolated_git_env


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@users.noreply.github.com", *args],
        cwd=cwd,
        env=_isolated_git_env(),
        check=True,
        capture_output=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestTheChangeIncludesWhatIsAlreadyCommitted(unittest.TestCase):
    def test_a_committed_unpushed_change_is_still_part_of_the_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            remote, work = Path(tmp) / "remote.git", Path(tmp) / "work"
            _git(["init", "--bare", "-b", "main", str(remote)], Path(tmp))
            work.mkdir()
            _git(["init", "-b", "main"], work)
            _write(work / "src" / "base.py", "A = 1\n")
            _git(["add", "-A"], work)
            _git(["commit", "-m", "base"], work)
            _git(["remote", "add", "origin", str(remote)], work)
            _git(["push", "-u", "origin", "main"], work)
            _write(work / "src" / "pushed_later.py", "B = 2\n")
            _git(["add", "-A"], work)
            _git(["commit", "-m", "change"], work)

            with mock.patch.dict(os.environ, _isolated_git_env(), clear=True):
                changed = quality._changed_paths(work)

        self.assertEqual(changed, ["src/pushed_later.py"])

    def test_without_an_upstream_the_working_tree_is_the_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            _git(["init", "-b", "main"], work)
            _write(work / "src" / "base.py", "A = 1\n")
            _git(["add", "-A"], work)
            _git(["commit", "-m", "base"], work)
            _write(work / "src" / "base.py", "A = 2\n")
            _write(work / "tests" / "test_new.py", "")

            with mock.patch.dict(os.environ, _isolated_git_env(), clear=True):
                changed = quality._changed_paths(work)

        self.assertEqual(changed, ["src/base.py", "tests/test_new.py"])


class TestSelection(unittest.TestCase):
    def test_a_deleted_test_module_is_not_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tests" / "test_kept.py", "")
            selected = quality._select_changed_tests(
                root, ["tests/test_kept.py", "tests/test_deleted.py"]
            )
        self.assertEqual(selected, ["tests.test_kept"])

    def test_a_changed_production_module_selects_the_tests_named_after_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tests" / "unit" / "test_ledger.py", "")
            _write(root / "tests" / "test_ledger_events.py", "")
            _write(root / "tests" / "test_other.py", "")
            selected = quality._select_changed_tests(root, ["src/gzkit/ledger.py", "README.md"])
        self.assertEqual(selected, ["tests.test_ledger_events", "tests.unit.test_ledger"])


class TestTheRun(unittest.TestCase):
    def _run(self, modules: list[str], env: dict[str, str]) -> mock.MagicMock:
        ok = QualityResult(success=True, command="x", stdout="", stderr="", returncode=0)
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(quality, "_changed_paths", return_value=[]),
            mock.patch.object(quality, "_select_changed_tests", return_value=modules),
            mock.patch("gzkit.quality.run_command", return_value=ok) as run_command,
        ):
            self.result = quality._run_changed_tests(Path("."))
        return run_command

    def test_each_selected_module_goes_to_the_canonical_runner_exactly(self) -> None:
        run_command = self._run(["tests.test_a", "tests.unit.test_b"], {})
        argv = run_command.call_args.args[0]
        self.assertEqual(
            argv[: len(CANONICAL_STEP_COMMANDS["unittest"])], CANONICAL_STEP_COMMANDS["unittest"]
        )
        # The trailing dot keeps `tests.test_a` from also selecting `tests.test_a_more`.
        self.assertEqual(
            argv[len(CANONICAL_STEP_COMMANDS["unittest"]) :],
            ["-k", "tests.test_a.", "-k", "tests.unit.test_b."],
        )

    def test_the_child_run_is_marked_so_it_cannot_nest(self) -> None:
        run_command = self._run(["tests.test_a"], {})
        marker = run_command.call_args.kwargs["env_overrides"]
        nested = self._run(["tests.test_a"], dict(marker))
        nested.assert_not_called()
        self.assertTrue(self.result.success)

    def test_an_empty_selection_runs_nothing(self) -> None:
        run_command = self._run([], {})
        run_command.assert_not_called()
        self.assertEqual(self.result.returncode, 0)

    def test_an_empty_selection_names_the_command_that_runs_the_whole_tier(self) -> None:
        # output-contract: the result is a selection, never a pass, so its text
        # must send the reader to the whole unit tier. Plain `gz check` no
        # longer runs it (GHI #1191).
        self._run([], {})
        self.assertIn("uv run gz test", self.result.stdout)
        self.assertNotIn("uv run gz check", self.result.stdout)


if __name__ == "__main__":
    unittest.main()
