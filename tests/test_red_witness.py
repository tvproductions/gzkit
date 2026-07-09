"""Tests for the base-tree RED falsifiability witness (GHI #642).

Assertions derive from the requirement — a BEHAVIOR test must demonstrate it can fail
in the absence of its implementation — not from a run of the implementation.

The three failure classes are tested apart because collapsing them is the specific
defect GHI #642 forbids: an ImportError against a not-yet-existing symbol is a *weak*
RED and must never be recorded as an assertion RED.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.red_witness import (
    changed_test_files,
    classify_failure,
    resolve_base_commit,
    run_red_witness,
)

# Hermetic runner: the temp fixtures have no pyproject.toml, so `uv run` would build
# an env (slow) or fail (an "error" class that would mask the assertion RED we assert).
_RUNNER = [sys.executable, "-m", "unittest"]


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


class TestClassifyFailure(unittest.TestCase):
    """`failure_class` is the verdict, not decoration."""

    def test_exit_zero_is_no_red(self) -> None:
        """A test that passes without its implementation cannot fail (Rule 6)."""
        self.assertEqual(classify_failure(0, "Ran 1 test\n\nOK"), "none")

    def test_assertion_failure_is_strong_red(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (failures=1)"), "assertion")

    def test_error_is_weak_red(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (errors=1)"), "error")

    def test_errors_dominate_failures(self) -> None:
        """A run that raised failed for the wrong reason, whatever else also failed.

        Collapsing this to `assertion` would launder a weak RED into a strong one.
        """
        self.assertEqual(classify_failure(1, "FAILED (failures=2, errors=1)"), "error")

    def test_nonzero_without_a_unittest_summary_is_an_error(self) -> None:
        """A crash, a collection failure, or a timeout is never an assertion RED."""
        self.assertEqual(classify_failure(1, "Segmentation fault"), "error")

    def test_zero_failures_and_zero_errors_but_nonzero_exit_is_an_error(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (failures=0, errors=0)"), "error")


class _GitFixture(unittest.TestCase):
    """A real git repo: a base commit, then working-tree changes on top."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _git(["init", "-q", "-b", "main"], self.root)
        _git(["config", "user.email", "t@example.invalid"], self.root)
        _git(["config", "user.name", "t"], self.root)
        (self.root / "tests").mkdir()
        (self.root / "tests" / "__init__.py").write_text("", encoding="utf-8")

    def _commit(self, message: str) -> None:
        _git(["add", "-A"], self.root)
        _git(["commit", "-q", "-m", message], self.root)


class TestChangedTestFiles(_GitFixture):
    """Both arms matter: modified files AND brand-new untracked ones."""

    def test_modified_test_file_is_detected(self) -> None:
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "test_a.py").write_text("x = 2\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertEqual(changed_test_files(self.root, base), [Path("tests/test_a.py")])

    def test_untracked_new_test_file_is_detected(self) -> None:
        """A brand-new test module appears only in `ls-files --others`.

        Missing this arm would silently witness nothing for every new test file —
        the common case for a REQ's first covering test.
        """
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "test_new.py").write_text("y = 1\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertIn(Path("tests/test_new.py"), changed_test_files(self.root, base))

    def test_non_python_files_are_ignored(self) -> None:
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "fixture.txt").write_text("data\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertEqual(changed_test_files(self.root, base), [])


class TestRunRedWitness(_GitFixture):
    """The end-to-end experiment: test hunks graft onto the base tree, production does not."""

    def _seed_base(self) -> None:
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")

    def test_new_symbol_yields_a_weak_error_red(self) -> None:
        """The GHI's named edge: a not-yet-existing symbol is an ImportError.

        Non-zero, but for the wrong reason. It must be classed `error`, never
        silently equated with an assertion RED.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import added\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_added(self):\n        self.assertEqual(added(), 1)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "error")
        self.assertNotEqual(witness.exit_status, 0)
        self.assertTrue(witness.is_red, "a weak RED still witnesses falsifiability")

    def test_changed_behavior_yields_a_strong_assertion_red(self) -> None:
        """The symbol exists at base but behaves differently: a real assertion RED."""
        (self.root / "impl.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def value():\n    return 2\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import value\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_value(self):\n        self.assertEqual(value(), 2)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "assertion")
        self.assertTrue(witness.is_red)

    def test_test_that_passes_without_its_implementation_is_not_red(self) -> None:
        """The defect this whole module exists to surface.

        The test asserts nothing about the production change, so it passes against
        the base tree — it cannot fail when the business logic changes.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_tautology(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "none")
        self.assertEqual(witness.exit_status, 0)
        self.assertFalse(witness.is_red, "a test that passes without the code proves nothing")

    def test_production_hunks_are_never_grafted(self) -> None:
        """The asymmetry IS the experiment.

        If production files were copied in too, the test would pass and every REQ
        would report `none` — the witness would be inverted into a rubber stamp.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest, pathlib\n\nclass T(unittest.TestCase):\n"
            "    def test_base_impl_is_empty(self):\n"
            "        self.assertEqual(pathlib.Path('impl.py').read_text(), '')\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        # The test asserts impl.py is EMPTY in the worktree; it passes => not grafted.
        self.assertEqual(witness.exit_status, 0, "production hunks leaked into the base tree")

    def test_no_covering_tests_raises(self) -> None:
        self._seed_base()
        with self.assertRaises(ValueError):
            run_red_witness(project_root=self.root, req_id="REQ-1.2.3-01-01", test_names=[])

    def test_witness_records_the_base_commit_it_ran_against(self) -> None:
        self._seed_base()
        base = resolve_base_commit(self.root)
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.base_commit, base)

    def test_worktree_is_removed_after_the_run(self) -> None:
        """A leaked worktree would poison every later `git worktree` operation."""
        self._seed_base()
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        listing = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            len(listing.stdout.strip().splitlines()), 1, "the throwaway worktree leaked"
        )


if __name__ == "__main__":
    unittest.main()
