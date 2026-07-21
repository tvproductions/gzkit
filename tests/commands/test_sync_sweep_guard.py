"""Tests for the git-sync ceremony sweep guard (GHI #708).

`gz git-sync --apply` stages by wildcard. When a preceding `git commit` aborts
— a non-zero pre-commit hook is the common cause — its staged changes remain in
the index, and the next `git add -A` folds substantive `src/`/`tests/` work into
the sync's generated `chore: … (gz git-sync)` commit under
`Task: TASK-gz-git-sync`. Assertions derive from `.gzkit/rules/tests.md`
§ TASK-Driven Workflow, which scopes the mandatory `Task:` trailer to exactly
`src/**` and `tests/**`.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.sync import (
    _execute_git_sync,
    _filter_governed_staged,
    _staged_governed_paths,
)


class TestGovernedStagedFilter(unittest.TestCase):
    """The pure decision: which staged names are governed scope."""

    def test_src_and_tests_paths_are_governed(self) -> None:
        names = ["src/gzkit/commands/sync.py", "tests/commands/test_sync.py"]
        self.assertEqual(_filter_governed_staged(names), sorted(names))

    def test_ceremony_surfaces_are_not_governed(self) -> None:
        """Sweeping generated surfaces and ledger state is the ceremony's actual job."""
        names = [
            ".claude/skills/gz-check/SKILL.md",
            ".gzkit/ledger.jsonl",
            "docs/user/manpages/validate.md",
            "config/gzkit.json",
        ]
        self.assertEqual(_filter_governed_staged(names), [])

    def test_mixed_index_reports_only_the_governed_paths(self) -> None:
        names = [
            ".gzkit/ledger.jsonl",
            "src/gzkit/quality.py",
            ".claude/rules/tests.md",
        ]
        self.assertEqual(_filter_governed_staged(names), ["src/gzkit/quality.py"])


class TestSweepGuard(unittest.TestCase):
    """The guard refuses the sweep rather than absorbing interrupted work."""

    def _run(self, staged: str) -> tuple[list[str], list[str]]:
        """Drive _execute_git_sync with a stubbed index; return (blockers, executed)."""
        blockers: list[str] = []

        def fake_git(_root: Path, *args: str) -> tuple[int, str, str]:
            if args[:3] == ("diff", "--cached", "--name-only"):
                return 0, staged, ""
            return 0, "", ""

        with mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake_git):
            executed = _execute_git_sync(
                project_root=Path("/nonexistent"),
                dirty=True,
                auto_add=True,
                run_lint_gate=False,
                run_test_gate=False,
                allow_push=False,
                diverged=False,
                behind=0,
                remote="origin",
                target_branch="main",
                blockers=blockers,
                warnings=[],
            )
        return blockers, executed

    def test_staged_src_work_blocks_the_sweep(self) -> None:
        """An aborted commit's staged src/ work must not become a ceremony commit."""
        blockers, executed = self._run("src/gzkit/governance/brief_reconcile.py\n")
        self.assertTrue(blockers, "sweep proceeded over staged governed scope")
        self.assertNotIn("git add -A", executed)

    def test_block_prose_names_path_rule_and_recovery(self) -> None:
        """Three-part guardrail prose per .gzkit/rules/guardrail-feedback-prose.md."""
        blockers, _ = self._run("tests/governance/test_brief_reconcile.py\n")
        message = "\n".join(blockers)
        self.assertIn("tests/governance/test_brief_reconcile.py", message)  # what failed
        self.assertIn("Task:", message)  # why forbidden — the trailer-scope rule
        self.assertIn("git commit", message)  # governed next step

    def test_ceremony_only_index_still_sweeps(self) -> None:
        """Negative control: the guard must not disarm the ceremony's real job."""
        blockers, executed = self._run(".claude/skills/gz-check/SKILL.md\n.gzkit/ledger.jsonl\n")
        self.assertEqual(blockers, [])
        self.assertIn("git add -A", executed)

    def test_empty_index_still_sweeps(self) -> None:
        """Negative control: the common case — nothing staged — is unaffected."""
        blockers, executed = self._run("")
        self.assertEqual(blockers, [])
        self.assertIn("git add -A", executed)


class TestStagedGovernedPathsAdapter(unittest.TestCase):
    """The git edge: parse `git diff --cached --name-only` output."""

    def test_returns_governed_paths_from_index(self) -> None:
        with mock.patch(
            "gzkit.commands.sync.git_cmd",
            return_value=(0, "src/gzkit/a.py\n.gzkit/ledger.jsonl\ntests/test_a.py\n", ""),
        ):
            self.assertEqual(
                _staged_governed_paths(Path("/nonexistent")),
                ["src/gzkit/a.py", "tests/test_a.py"],
            )

    def test_git_failure_does_not_block_the_sweep(self) -> None:
        """A guard that cannot read the index must not strand the operator.

        Failing open here is deliberate: the guard defends against an unlikely
        interrupted-commit state, while failing closed on an unreadable index
        would break every sync in a repo the guard cannot inspect.
        """
        with mock.patch("gzkit.commands.sync.git_cmd", return_value=(128, "", "fatal")):
            self.assertEqual(_staged_governed_paths(Path("/nonexistent")), [])


if __name__ == "__main__":
    unittest.main()
