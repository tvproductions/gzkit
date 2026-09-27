"""The trailer witness covers every commit a push publishes, not HEAD alone (GHI #1017).

``.claude/rules/task-discovery.md`` § Invariant binds *any* commit touching
``src/**`` or ``tests/**``. The validator read HEAD only, so at pre-push a
trailer-less code commit passed whenever a non-code commit sat on top of it --
and ``gz git-sync`` puts a ``.gzkit`` chore commit on top in most sessions.
``d9c099add`` reached ``origin`` that way. These fixtures push a seed to a real
bare remote so ``@{upstream}`` exists, then build the unpushed range.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.validate_commit_trailers import (
    _validate_commit_trailers,
    _validate_eval_feedback_trailer,
)
from tests.commands.common import _init_git_repo, _isolated_git_env


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_isolated_git_env(),
    ).stdout.strip()


def _commit(root: Path, rel: str, message: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{message}\n", encoding="utf-8")
    _git(root, "add", rel)
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "--short=7", "HEAD")


class PushedRangeTests(unittest.TestCase):
    """Every unpushed commit is checked; published ones are not re-flagged."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        remote = base / "remote.git"
        _git(base, "init", "--bare", "-b", "main", str(remote))
        self.root = base / "work"
        self.root.mkdir()
        _init_git_repo(self.root)
        _git(self.root, "remote", "add", "origin", str(remote))
        _git(self.root, "push", "-u", "origin", "main")

    def test_trailerless_code_commit_under_a_non_code_tip_is_flagged(self) -> None:
        """The d9c099add shape: the offender is not HEAD, and is still named."""
        offender = _commit(self.root, "tests/test_x.py", "fix: skip a test")
        _commit(self.root, ".gzkit/ledger.jsonl", "chore: update .gzkit (gz git-sync)")
        errors = _validate_commit_trailers(self.root)
        self.assertEqual([e.artifact for e in errors], [offender])

    def test_every_offender_in_the_range_is_named(self) -> None:
        first = _commit(self.root, "src/a.py", "feat: a")
        second = _commit(self.root, "tests/test_a.py", "test: a")
        _commit(self.root, "docs/a.md", "docs: a")
        errors = _validate_commit_trailers(self.root)
        self.assertEqual(sorted(e.artifact for e in errors), sorted([first, second]))

    def test_conforming_code_commit_under_a_non_code_tip_passes(self) -> None:
        """Control: the widened population does not flag a commit that complies."""
        _commit(self.root, "src/a.py", "feat: a\n\nTask: TASK-a-#1017")
        _commit(self.root, ".gzkit/ledger.jsonl", "chore: update .gzkit (gz git-sync)")
        self.assertEqual(_validate_commit_trailers(self.root), [])

    def test_range_without_code_commits_passes(self) -> None:
        """Control: a push of docs and .gzkit rows needs no Task: trailer."""
        _commit(self.root, "docs/a.md", "docs: a")
        _commit(self.root, ".gzkit/ledger.jsonl", "chore: update .gzkit (gz git-sync)")
        self.assertEqual(_validate_commit_trailers(self.root), [])

    def test_published_commits_are_not_re_flagged(self) -> None:
        """A trailer-less commit already on the upstream is history, not this push."""
        _commit(self.root, "src/a.py", "feat: a")
        _git(self.root, "push")
        _commit(self.root, "docs/a.md", "docs: a")
        self.assertEqual(_validate_commit_trailers(self.root), [])

    def test_eval_feedback_offender_under_a_non_code_tip_is_flagged(self) -> None:
        """The same scope's second witness reads the same range (same mechanism)."""
        offender = _commit(self.root, ".gzkit/rules/r.md", "docs: tighten rule\n\nCloses #42")
        _commit(self.root, "docs/a.md", "docs: a")
        with patch(
            "gzkit.commands.validate_commit_trailers._issue_labels",
            return_value=["eval-feedback"],
        ):
            errors = _validate_eval_feedback_trailer(self.root)
        self.assertEqual([e.artifact for e in errors], [offender])


class NoUpstreamTests(unittest.TestCase):
    """Without an upstream the range is unknowable, so HEAD alone is checked."""

    def test_head_is_checked_when_no_upstream_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_git_repo(root)
            head = _commit(root, "src/a.py", "feat: a")
            errors = _validate_commit_trailers(root)
            self.assertEqual([e.artifact for e in errors], [head])


if __name__ == "__main__":
    unittest.main()
