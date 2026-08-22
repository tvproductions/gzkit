"""The gate must not re-run over a tree it already passed (GHI #835).

`gz check` costs ~148s (measured 2026-08-22: Test 44s, Behave 33s, ~46 validator
subprocesses ~15s, docs build 4s). A fix paid it TWICE -- once when the agent
verified, then again when `git push` fired the pre-push gate over a tree that had
not changed since. The second run cannot reach a different verdict.

The fingerprint is the tree's CONTENT, deliberately not HEAD: a commit is created
between the two runs, so a HEAD-keyed check would never fire the skip. These
tests pin that property directly, because it is the one an obvious
implementation gets wrong.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.check_fingerprint import (
    already_verified,
    record_verified,
    verified_fingerprint,
    worktree_fingerprint,
)


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _repo() -> Path:
    root = Path(tempfile.mkdtemp(prefix="gzkit-fp-"))
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "g0@users.noreply.github.com"], root)
    _git(["config", "user.name", "g0"], root)
    (root / "src").mkdir()
    (root / "src" / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / ".gitignore").write_text("build/\n", encoding="utf-8")
    _git(["add", "-A"], root)
    _git(["commit", "-qm", "base"], root)
    return root


class TestFingerprintTracksContentNotCommits(unittest.TestCase):
    """The property an obvious implementation gets wrong."""

    def test_committing_does_not_change_the_fingerprint(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 2\n", encoding="utf-8")
        before = worktree_fingerprint(root)
        _git(["add", "-A"], root)
        _git(["commit", "-qm", "land it"], root)
        self.assertEqual(
            worktree_fingerprint(root),
            before,
            "a commit changes HEAD but not the files; keying on HEAD would mean the "
            "skip never fires, since a commit ALWAYS happens between verify and push",
        )

    def test_editing_a_file_changes_the_fingerprint(self) -> None:
        root = _repo()
        before = worktree_fingerprint(root)
        (root / "src" / "mod.py").write_text("VALUE = 99\n", encoding="utf-8")
        self.assertNotEqual(worktree_fingerprint(root), before)

    def test_untracked_file_changes_the_fingerprint(self) -> None:
        root = _repo()
        before = worktree_fingerprint(root)
        (root / "src" / "new.py").write_text("X = 1\n", encoding="utf-8")
        self.assertNotEqual(
            worktree_fingerprint(root),
            before,
            "an untracked module is code the suite would import; ignoring it would "
            "skip the gate over a tree the gate never saw",
        )

    def test_gitignored_noise_does_not_change_the_fingerprint(self) -> None:
        root = _repo()
        before = worktree_fingerprint(root)
        (root / "build").mkdir()
        (root / "build" / "artifact.bin").write_text("noise\n", encoding="utf-8")
        self.assertEqual(
            worktree_fingerprint(root),
            before,
            "build output and receipts must not defeat the skip",
        )

    def test_the_real_index_is_left_alone(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 3\n", encoding="utf-8")
        worktree_fingerprint(root)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        ).stdout
        self.assertIn(
            " M src/mod.py",
            status,
            "the edit must still read as UNSTAGED: taking a fingerprint may never "
            "stage the operator's working tree as a side effect",
        )


class TestSkipRequiresBothSidesToAgree(unittest.TestCase):
    """A missing, partial, or stale receipt must fall through to running the gate."""

    def test_matching_tree_reports_verified(self) -> None:
        root = _repo()
        record_verified(root, worktree_fingerprint(root), scope="full")
        self.assertIsNotNone(already_verified(root))

    def test_edit_after_recording_falls_through(self) -> None:
        root = _repo()
        record_verified(root, worktree_fingerprint(root), scope="full")
        (root / "src" / "mod.py").write_text("VALUE = 4\n", encoding="utf-8")
        self.assertIsNone(
            already_verified(root),
            "any edit must re-run the gate; this is the whole safety property",
        )

    def test_no_receipt_falls_through(self) -> None:
        self.assertIsNone(already_verified(_repo()))

    def test_a_fast_scope_is_never_recorded(self) -> None:
        root = _repo()
        record_verified(root, worktree_fingerprint(root), scope="fast")
        self.assertIsNone(
            verified_fingerprint(root),
            "a scoped run skips the expensive steps by design; letting one satisfy "
            "the gate is the presence-check failure AGENTS.md names",
        )

    def test_a_non_git_directory_fails_open(self) -> None:
        plain = Path(tempfile.mkdtemp(prefix="gzkit-nogit-"))
        self.assertIsNone(
            worktree_fingerprint(plain),
            "no fingerprint ever matches, so the gate runs -- a fingerprint that "
            "failed CLOSED would refuse pushes on a repo it merely could not read",
        )
