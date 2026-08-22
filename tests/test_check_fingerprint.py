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
    staged_fingerprint,
    tree_is_fully_staged,
    verified_fingerprint,
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


class TestFingerprintNamesTheCommittableTree(unittest.TestCase):
    """The index is the only object both sides of the skip can observe."""

    def test_committing_does_not_change_the_fingerprint(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 2\n", encoding="utf-8")
        _git(["add", "-A"], root)
        staged = staged_fingerprint(root)
        _git(["commit", "-qm", "land it"], root)
        self.assertEqual(
            staged_fingerprint(root),
            staged,
            "the whole point: verify then commit then push must see ONE hash. A "
            "HEAD-keyed check would differ here and the skip would never fire",
        )

    def test_staging_an_edit_changes_the_fingerprint(self) -> None:
        root = _repo()
        before = staged_fingerprint(root)
        (root / "src" / "mod.py").write_text("VALUE = 99\n", encoding="utf-8")
        _git(["add", "-A"], root)
        self.assertNotEqual(staged_fingerprint(root), before)

    def test_gitignored_noise_does_not_change_the_fingerprint(self) -> None:
        root = _repo()
        before = staged_fingerprint(root)
        (root / "build").mkdir()
        (root / "build" / "artifact.bin").write_text("noise\n", encoding="utf-8")
        _git(["add", "-A"], root)
        self.assertEqual(
            staged_fingerprint(root),
            before,
            "build output and receipts must not defeat the skip",
        )

    def test_the_real_index_is_left_alone(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 3\n", encoding="utf-8")
        staged_fingerprint(root)
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


class TestOnlyAnExactlyStagedTreeIsRecordable(unittest.TestCase):
    """The gate runs on the WORKING tree; the fingerprint names the INDEX tree.

    They are the same object only when nothing is outstanding, so that is the one
    condition under which the pass is recordable. This is what keeps the skip from
    attesting a tree that was never the one tested.
    """

    def test_clean_staged_tree_is_recordable(self) -> None:
        root = _repo()
        self.assertTrue(tree_is_fully_staged(root))

    def test_unstaged_edit_is_not_recordable(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 5\n", encoding="utf-8")
        self.assertFalse(
            tree_is_fully_staged(root),
            "an unstaged edit was verified but will not be pushed; recording the "
            "index tree here would attest content the gate never ran against",
        )

    def test_untracked_file_is_not_recordable(self) -> None:
        root = _repo()
        (root / "src" / "new.py").write_text("X = 1\n", encoding="utf-8")
        self.assertFalse(
            tree_is_fully_staged(root),
            "an untracked module is code the run could import but the commit will not carry",
        )

    def test_unstaged_edit_blocks_the_skip_end_to_end(self) -> None:
        root = _repo()
        (root / "src" / "mod.py").write_text("VALUE = 6\n", encoding="utf-8")
        record_verified(root, staged_fingerprint(root), scope="full")
        # record_verified is only ever CALLED behind tree_is_fully_staged; this
        # asserts the end-to-end path the command takes.
        self.assertFalse(tree_is_fully_staged(root))


class TestSkipRequiresBothSidesToAgree(unittest.TestCase):
    """A missing, partial, or stale receipt must fall through to running the gate."""

    def test_matching_tree_reports_verified(self) -> None:
        root = _repo()
        record_verified(root, staged_fingerprint(root), scope="full")
        self.assertIsNotNone(already_verified(root))

    def test_staged_edit_after_recording_falls_through(self) -> None:
        root = _repo()
        record_verified(root, staged_fingerprint(root), scope="full")
        (root / "src" / "mod.py").write_text("VALUE = 4\n", encoding="utf-8")
        _git(["add", "-A"], root)
        self.assertIsNone(
            already_verified(root),
            "any change to what will be committed must re-run the gate; this is "
            "the whole safety property",
        )

    def test_no_receipt_falls_through(self) -> None:
        self.assertIsNone(already_verified(_repo()))

    def test_a_fast_scope_is_never_recorded(self) -> None:
        root = _repo()
        record_verified(root, staged_fingerprint(root), scope="fast")
        self.assertIsNone(
            verified_fingerprint(root),
            "a scoped run skips the expensive steps by design; letting one satisfy "
            "the gate is the presence-check failure AGENTS.md names",
        )

    def test_a_non_git_directory_fails_open(self) -> None:
        plain = Path(tempfile.mkdtemp(prefix="gzkit-nogit-"))
        self.assertIsNone(
            staged_fingerprint(plain),
            "no fingerprint ever matches, so the gate runs -- a fingerprint that "
            "failed CLOSED would refuse pushes on a repo it merely could not read",
        )
