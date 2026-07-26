"""Tests for git-sync pull-verb selection across the auto-commit (GHI #720).

`gz git-sync --apply` computed `ahead`/`behind`/`diverged` once, in
`_plan_git_sync`, then created the ceremony auto-commit, then chose its pull verb
from those pre-commit values. The commit moves `ahead` 0 -> 1, so a clean
behind-N clone becomes genuinely diverged mid-ritual and the planned
`git pull --ff-only` aborts (`fatal: Not possible to fast-forward`) — leaving the
commit landed, the pull unrun, and the tree in a state the ceremony refuses to
resolve.

Assertions derive from the invariant the sibling `_push_if_ahead` already
honors: a step whose predicate depends on ahead/behind must read that state
*after* the actions that mutate it, not before ("Push only when branch is ahead
after sync actions").
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.sync import _execute_git_sync, _plan_git_sync


class _FakeGit:
    """Stateful git stub whose auto-commit moves `ahead`, as the real one does."""

    def __init__(
        self, *, behind: int, ahead: int = 0, staged: str = ".gzkit/ledger.jsonl\n"
    ) -> None:
        self.behind = behind
        self.ahead = ahead
        self.staged = staged
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, _root: Path, *args: str) -> tuple[int, str, str]:
        self.calls.append(args)
        if args[:3] == ("diff", "--cached", "--name-only"):
            return 0, self.staged, ""
        if args[0] == "commit":
            # The mutation at the heart of GHI #720.
            self.ahead += 1
            return 0, "", ""
        if args[:2] == ("rev-list", "--count"):
            spec = args[2]
            if spec == "origin/main..main":
                return 0, str(self.ahead), ""
            if spec == "main..origin/main":
                return 0, str(self.behind), ""
            return 0, "0", ""
        if args[0] == "rev-parse":
            return 0, "deadbeef", ""
        return 0, "", ""

    @property
    def pull_invocations(self) -> list[tuple[str, ...]]:
        return [args for args in self.calls if args and args[0] == "pull"]


def _run(fake: _FakeGit, *, dirty: bool) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    # Both namespaces: `_pull_if_needed` and `_push_if_ahead` reach state through
    # `_compute_git_sync_state`, which lives in `gzkit.git_sync` and resolves
    # `git_cmd` there. Patching only the `commands.sync` name leaves the real git
    # running against a nonexistent root, which silently reports behind=0 and
    # makes every pull assertion vacuous.
    with (
        mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake),
        mock.patch("gzkit.git_sync.git_cmd", side_effect=fake),
    ):
        executed = _execute_git_sync(
            project_root=Path("/nonexistent"),
            dirty=dirty,
            auto_add=dirty,
            run_lint_gate=False,
            run_test_gate=False,
            allow_push=False,
            remote="origin",
            target_branch="main",
            blockers=blockers,
            warnings=[],
        )
    return blockers, executed


class TestPullVerbAcrossAutoCommit(unittest.TestCase):
    """The pull verb must be chosen from post-commit state, not entry state."""

    def test_behind_and_dirty_rebases_instead_of_failing_fast_forward(self) -> None:
        # Entry state is behind-only (ahead=0), so the pre-commit plan says
        # --ff-only. The auto-commit makes the branch diverged, at which point
        # --ff-only cannot succeed. Reading state after the commit selects
        # --rebase, which can.
        fake = _FakeGit(behind=24)
        blockers, executed = _run(fake, dirty=True)

        self.assertEqual(
            [args[1] for args in fake.pull_invocations],
            ["--rebase"],
            msg=(
                f"pull verb was chosen from pre-commit state; invocations={fake.pull_invocations}"
            ),
        )
        self.assertIn("git commit", executed)
        self.assertEqual(blockers, [])

    def test_clean_tree_behind_still_fast_forwards(self) -> None:
        # Negative control: with no auto-commit there is no divergence to create,
        # so the cheap fast-forward must survive. A fix that always rebases would
        # pass the test above and fail here.
        fake = _FakeGit(behind=24, staged="")
        blockers, _executed = _run(fake, dirty=False)

        self.assertEqual(
            [args[1] for args in fake.pull_invocations],
            ["--ff-only"],
            msg=f"clean behind-N tree should fast-forward; invocations={fake.pull_invocations}",
        )
        self.assertEqual(blockers, [])

    def test_level_tree_does_not_pull(self) -> None:
        # Second negative control: nothing to reconcile, no pull at all.
        fake = _FakeGit(behind=0, staged="")
        blockers, _executed = _run(fake, dirty=False)

        self.assertEqual(fake.pull_invocations, [])
        self.assertEqual(blockers, [])


class TestPlanMatchesExecution(unittest.TestCase):
    """The dry-run plan must describe the commands apply-mode actually runs.

    `.claude/skills/git-sync/SKILL.md` § Steps tells the operator to preview with
    a dry-run before applying, and its Red Flags name "Dry-run run without
    follow-through apply". That contract is only worth anything if the plan agrees
    with the execution — a plan promising `--ff-only` while apply rebases teaches
    the operator to distrust the preview.
    """

    def _plan_actions(self, *, behind: int, ahead: int, dirty: bool) -> list[str]:
        fake = _FakeGit(behind=behind, ahead=ahead)
        with (
            mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake),
            mock.patch("gzkit.git_sync.git_cmd", side_effect=fake),
            mock.patch("gzkit.commands.sync._head_is_merge_commit", return_value=False),
            mock.patch(
                "gzkit.commands.sync._git_status_lines",
                return_value=([" M .gzkit/ledger.jsonl"] if dirty else [], None),
            ),
        ):
            plan = _plan_git_sync(
                project_root=Path("/nonexistent"),
                current_branch="main",
                target_branch="main",
                remote="origin",
                apply=False,
                auto_add=True,
                allow_push=True,
            )
        return list(plan["actions"])

    def test_behind_and_dirty_plan_predicts_rebase_and_push(self) -> None:
        # The exact state that broke: entry ahead=0/behind=24 with a dirty tree.
        # Pre-fix the plan read "--ff-only" and omitted the push, while apply-mode
        # rebased and pushed.
        actions = self._plan_actions(behind=24, ahead=0, dirty=True)

        self.assertIn("git pull --rebase origin main", actions)
        self.assertNotIn("git pull --ff-only origin main", actions)
        self.assertIn("git push origin main", actions)

    def test_behind_and_clean_plan_still_predicts_fast_forward(self) -> None:
        # Negative control: with no auto-commit pending there is no projected
        # divergence, so the cheap fast-forward stays in the plan and no push is
        # predicted.
        actions = self._plan_actions(behind=24, ahead=0, dirty=False)

        self.assertIn("git pull --ff-only origin main", actions)
        self.assertNotIn("git pull --rebase origin main", actions)
        self.assertNotIn("git push origin main", actions)


if __name__ == "__main__":
    unittest.main()
