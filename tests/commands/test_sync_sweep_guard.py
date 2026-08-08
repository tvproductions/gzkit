"""Tests for the git-sync ceremony sweep guard (GHI #708).

`gz git-sync --apply` stages by wildcard, so substantive `src/`/`tests/` work
lands in the sync's generated `chore: … (gz git-sync)` commit under
`Task: TASK-gz-git-sync`. Assertions derive from `.gzkit/rules/tests.md`
§ TASK-Driven Workflow, which scopes the mandatory `Task:` trailer to exactly
`src/**` and `tests/**`.

Two disjoint causes populate the swept set, and the guard owes both:

* **already staged** — a preceding `git commit` aborted (a non-zero pre-commit
  hook is the usual cause) and left its work in the index.
* **not yet staged** — an ordinary dirty working tree, which is the entire
  premise of the `--auto-add` flag the guard sits inside.

The first shipped at `6c26d67b`; the second did not, and `57bd15f91` swept six
governed files (165 lines) eighteen days later. The predicate now reads what
`git add -A` *would* stage rather than what is already staged.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.sync import (
    _execute_git_sync,
    _filter_governed_paths,
    _sweep_governed_paths,
)


class TestGovernedStagedFilter(unittest.TestCase):
    """The pure decision: which staged names are governed scope."""

    def test_src_and_tests_paths_are_governed(self) -> None:
        names = ["src/gzkit/commands/sync.py", "tests/commands/test_sync.py"]
        self.assertEqual(_filter_governed_paths(names), sorted(names))

    def test_ceremony_surfaces_are_not_governed(self) -> None:
        """Sweeping generated surfaces and ledger state is the ceremony's actual job."""
        names = [
            ".claude/skills/gz-check/SKILL.md",
            ".gzkit/ledger.jsonl",
            "docs/user/manpages/validate.md",
            "config/gzkit.json",
        ]
        self.assertEqual(_filter_governed_paths(names), [])

    def test_mixed_index_reports_only_the_governed_paths(self) -> None:
        names = [
            ".gzkit/ledger.jsonl",
            "src/gzkit/quality.py",
            ".claude/rules/tests.md",
        ]
        self.assertEqual(_filter_governed_paths(names), ["src/gzkit/quality.py"])


class TestSweepGuard(unittest.TestCase):
    """The guard refuses the sweep rather than absorbing governed work."""

    def _run(
        self, staged: str = "", *, unstaged: str = "", untracked: str = ""
    ) -> tuple[list[str], list[str]]:
        """Drive _execute_git_sync with a stubbed worktree; return (blockers, executed)."""
        blockers: list[str] = []

        def fake_git(_root: Path, *args: str) -> tuple[int, str, str]:
            if args[:3] == ("diff", "--cached", "--name-only"):
                return 0, staged, ""
            if args[:2] == ("diff", "--name-only"):
                return 0, unstaged, ""
            if args[:1] == ("ls-files",):
                return 0, untracked, ""
            return 0, "", ""

        with mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake_git):
            executed = _execute_git_sync(
                project_root=Path("/nonexistent"),
                dirty=True,
                auto_add=True,
                run_lint_gate=False,
                run_test_gate=False,
                allow_push=False,
                remote="origin",
                target_branch="main",
                blockers=blockers,
                warnings=[],
            )
        return blockers, executed

    def test_staged_src_work_blocks_the_sweep(self) -> None:
        """An aborted commit's staged src/ work must not become a ceremony commit."""
        blockers, executed = self._run(staged="src/gzkit/governance/brief_reconcile.py\n")
        self.assertTrue(blockers, "sweep proceeded over staged governed scope")
        self.assertNotIn("git add -A", executed)

    def test_unstaged_src_modification_blocks_the_sweep(self) -> None:
        """The `57bd15f91` reproduction: dirty-but-unstaged source is still swept.

        `--auto-add` exists precisely to stage a dirty tree, so reading only the
        index leaves the flag's own common case undefended.
        """
        blockers, executed = self._run(unstaged="src/gzkit/req_kind_support.py\n")
        self.assertTrue(blockers, "sweep proceeded over unstaged governed scope")
        self.assertNotIn("git add -A", executed)

    def test_untracked_test_file_blocks_the_sweep(self) -> None:
        """A brand-new covering test is governed scope before it is ever staged."""
        blockers, executed = self._run(untracked="tests/commands/test_new_surface.py\n")
        self.assertTrue(blockers, "sweep proceeded over untracked governed scope")
        self.assertNotIn("git add -A", executed)

    def test_block_prose_names_path_rule_and_recovery(self) -> None:
        """Three-part guardrail prose per .gzkit/rules/guardrail-feedback-prose.md."""
        blockers, _ = self._run(staged="tests/governance/test_brief_reconcile.py\n")
        message = "\n".join(blockers)
        self.assertIn("tests/governance/test_brief_reconcile.py", message)  # what failed
        self.assertIn("Task:", message)  # why forbidden — the trailer-scope rule
        self.assertIn("git commit", message)  # governed next step

    def test_ceremony_only_index_still_sweeps(self) -> None:
        """Negative control: the guard must not disarm the ceremony's real job."""
        blockers, executed = self._run(
            staged=".claude/skills/gz-check/SKILL.md\n.gzkit/ledger.jsonl\n"
        )
        self.assertEqual(blockers, [])
        self.assertIn("git add -A", executed)

    def test_ceremony_only_dirty_tree_still_sweeps(self) -> None:
        """Negative control across all three probes: a real sync ceremony is untouched."""
        blockers, executed = self._run(
            staged=".gzkit/ledger.jsonl\n",
            unstaged=".claude/rules/tests.md\ndocs/user/manpages/validate.md\n",
            untracked=".gzkit/handoffs/20260808T000000Z-example.md\n",
        )
        self.assertEqual(blockers, [])
        self.assertIn("git add -A", executed)

    def test_empty_index_still_sweeps(self) -> None:
        """Negative control: the common case — nothing staged — is unaffected."""
        blockers, executed = self._run()
        self.assertEqual(blockers, [])
        self.assertIn("git add -A", executed)


class TestSweepGovernedPathsAdapter(unittest.TestCase):
    """The git edge: union the three probes `git add -A` would stage from."""

    def test_returns_governed_paths_from_index(self) -> None:
        with mock.patch(
            "gzkit.commands.sync.git_cmd",
            return_value=(0, "src/gzkit/a.py\n.gzkit/ledger.jsonl\ntests/test_a.py\n", ""),
        ):
            self.assertEqual(
                _sweep_governed_paths(Path("/nonexistent")),
                ["src/gzkit/a.py", "tests/test_a.py"],
            )

    def test_unions_staged_unstaged_and_untracked(self) -> None:
        """One path per probe; a path seen twice is reported once."""

        def fake_git(_root: Path, *args: str) -> tuple[int, str, str]:
            if args[:3] == ("diff", "--cached", "--name-only"):
                return 0, "src/gzkit/staged.py\n", ""
            if args[:2] == ("diff", "--name-only"):
                return 0, "src/gzkit/staged.py\ntests/unstaged.py\n", ""
            return 0, "src/gzkit/untracked.py\n", ""

        with mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake_git):
            self.assertEqual(
                _sweep_governed_paths(Path("/nonexistent")),
                ["src/gzkit/staged.py", "src/gzkit/untracked.py", "tests/unstaged.py"],
            )

    def test_git_failure_does_not_block_the_sweep(self) -> None:
        """A guard that cannot read the worktree must not strand the operator.

        Failing open here is deliberate (ratified under GHI #708): failing
        closed on an unreadable worktree would break every sync in a repo the
        guard cannot inspect.
        """
        with mock.patch("gzkit.commands.sync.git_cmd", return_value=(128, "", "fatal")):
            self.assertEqual(_sweep_governed_paths(Path("/nonexistent")), [])

    def test_a_later_probe_failing_still_fails_open(self) -> None:
        """Fail-open binds every probe, not just the first one read."""

        def fake_git(_root: Path, *args: str) -> tuple[int, str, str]:
            if args[:3] == ("diff", "--cached", "--name-only"):
                return 0, "src/gzkit/a.py\n", ""
            return 128, "", "fatal"

        with mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake_git):
            self.assertEqual(_sweep_governed_paths(Path("/nonexistent")), [])


if __name__ == "__main__":
    unittest.main()


class SyncPrechecksVerifyGateDelivery(unittest.TestCase):
    """git-sync must not defer to a pre-commit gate that is not installed.

    `_run_sync_prechecks` skips lint/test by default on the stated grounds that
    "pre-commit enforces unittest/lint/type checks". That deferral is only sound
    if the hook is actually delivered. In this repo it was not — `.git/hooks/`
    held stock samples while the config declared the gate — so `gz git-sync
    --apply` pushed a red tree with nothing in the chain objecting.
    """

    def test_undelivered_gate_blocks_sync(self) -> None:
        from gzkit.commands.sync import _run_sync_prechecks

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(
                "repos:\n  - repo: local\n    hooks:\n      - id: gz-check-pre-push\n"
                "        entry: uv run gz check\n        stages: [pre-push]\n",
                encoding="utf-8",
            )
            (root / ".git" / "hooks").mkdir(parents=True)
            blockers: list[str] = []
            executed: list[str] = []
            _run_sync_prechecks(root, False, False, blockers, executed)

        self.assertTrue(blockers, "undelivered pre-push gate must block sync")
        self.assertIn("pre-commit install", blockers[0])

    def test_delivered_gate_does_not_block(self) -> None:
        from gzkit.commands.sync import _run_sync_prechecks

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(
                "repos:\n  - repo: local\n    hooks:\n      - id: gz-check-pre-push\n"
                "        entry: uv run gz check\n        stages: [pre-push]\n",
                encoding="utf-8",
            )
            hooks = root / ".git" / "hooks"
            hooks.mkdir(parents=True)
            (hooks / "pre-push").write_text(
                "exec pre-commit hook-impl --hook-type=pre-push\n", encoding="utf-8"
            )
            blockers: list[str] = []
            _run_sync_prechecks(root, False, False, blockers, [])

        self.assertEqual(blockers, [])

    def test_non_git_tree_does_not_block(self) -> None:
        """Delivery is unassertable outside a worktree; do not invent a blocker."""
        from gzkit.commands.sync import _run_sync_prechecks

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(
                "repos:\n  - repo: local\n    hooks:\n      - id: gz-check-pre-push\n"
                "        entry: uv run gz check\n        stages: [pre-push]\n",
                encoding="utf-8",
            )
            blockers: list[str] = []
            _run_sync_prechecks(root, False, False, blockers, [])

        self.assertEqual(blockers, [])
