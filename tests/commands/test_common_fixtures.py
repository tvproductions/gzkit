"""Contract tests for the shared test-fixture helpers in ``tests.commands.common``.

These assert properties the fixtures must hold for *other* tests to be sound,
so a regression here is a regression in every suite that builds a repo fixture.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.commands.common import _ignore_transient_git, _init_git_repo


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


class TestIgnoreTransientGit(unittest.TestCase):
    """``copytree`` must not race the transient files git writes under ``.git``.

    Quiescing auto-maintenance removed one writer of one lock. It did not close
    the class: ``.git/index.lock``, ``HEAD.lock``, ``config.lock`` and
    ``.git/objects/pack/tmp_pack_*`` are written and removed by ordinary git
    commands, and every fixture builder runs ``git add`` and ``git commit``.
    Any of them existing at ``os.listdir`` time and gone by ``copy2`` time
    reproduces CI 32230349611's ``shutil.Error`` with a different filename
    (GHI #833).
    """

    def _repo(self, tmp: str) -> Path:
        root = Path(tmp) / "repo"
        root.mkdir()
        _init_git_repo(root)
        return root

    def _git(self, root: Path, *args: str) -> tuple[int, str]:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, (result.stdout + result.stderr).strip()

    def test_transient_git_files_are_ignored(self) -> None:
        """Every member of the class is dropped, not just maintenance.lock."""
        names = [
            "index.lock",
            "HEAD.lock",
            "config.lock",
            "maintenance.lock",
            "tmp_pack_abc123",
            "HEAD",
            "config",
            "objects",
        ]
        ignored = _ignore_transient_git(str(Path("/somewhere/repo/.git")), names)
        self.assertEqual(
            ignored,
            {"index.lock", "HEAD.lock", "config.lock", "maintenance.lock", "tmp_pack_abc123"},
            "every transient git file must be dropped; durable git state must be kept",
        )

    def test_uv_lock_outside_the_git_dir_is_kept(self) -> None:
        """The constraint that rules out ``ignore_patterns('*.lock')``.

        ``src/gzkit/commands/patch_release.py`` reads ``uv.lock`` from the tree,
        so a name-only lock filter would break the tests it claims to fix. The
        predicate must key on *where* the file lives, not what it is called.
        """
        ignored = _ignore_transient_git(
            str(Path("/somewhere/repo")), ["uv.lock", ".git", "README.md"]
        )
        self.assertEqual(ignored, set(), "uv.lock is durable tree state, not transient git state")

    def _copy_racing(self, src: Path, dest: Path, doomed: Path, *, guarded: bool) -> None:
        """Copy ``src`` while ``doomed`` vanishes inside the race window.

        ``shutil.copytree`` calls ``ignore(src, names)`` after ``os.listdir``
        and before ``copy2``, so unlinking from the callable lands in exactly
        the window the CI failure hit — deterministically, with no reliance on
        git's timing.
        """

        def _ignore(listed: str, names: list[str]) -> set[str]:
            result = _ignore_transient_git(listed, names) if guarded else set()
            if Path(listed) == doomed.parent and doomed.exists():
                doomed.unlink()
            return result

        shutil.copytree(src, dest, ignore=_ignore)

    def test_unguarded_copy_dies_when_a_lock_vanishes_mid_copy(self) -> None:
        """The race is real: without the guard the copy fails.

        Without this the guarded case below proves nothing — a copy that would
        have succeeded anyway is not evidence that the guard does any work.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            lock = root / ".git" / "index.lock"
            lock.write_text("", encoding="utf-8")
            with self.assertRaises(shutil.Error):
                self._copy_racing(root, Path(tmp) / "unguarded", lock, guarded=False)

    def test_guarded_copy_survives_a_lock_vanishing_mid_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            lock = root / ".git" / "index.lock"
            lock.write_text("", encoding="utf-8")
            dest = Path(tmp) / "guarded"
            self._copy_racing(root, dest, lock, guarded=True)
            # Assert the behaviour, not the absence of a path: a stale
            # index.lock in the copy is only a defect because git then refuses
            # to work. Measured 2026-08-19 — ``git status`` exits 0 with a
            # stale lock present and is the wrong probe; ``git add`` exits 128
            # ("Unable to create ... index.lock: File exists"), so it is the
            # one that actually distinguishes the two states.
            code, output = self._git(dest, "add", "-A")
            self.assertEqual(code, 0, f"copied repo must be writable by git, got: {output}")

    def test_guarded_copy_still_yields_a_usable_repo(self) -> None:
        """Dropping transient state must not break the repo the fixture provides."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "uv.lock").write_text("version = 1\n", encoding="utf-8")
            dest = Path(tmp) / "copy"
            shutil.copytree(root, dest, ignore=_ignore_transient_git)
            # Assert inside the context manager: the tempdir — and every path
            # under it — is gone the moment the block exits, so an assertion
            # outside it can only ever read a deleted tree.
            log_code, log = self._git(dest, "log", "--oneline", "-1")
            self.assertEqual(log_code, 0, f"copied repo must still be a repo, got: {log}")
            self.assertTrue(log, "copied repo must still have its history")
            # uv.lock's survival is read out of git's own view of the copied
            # tree rather than off the filesystem: it is untracked in the
            # fixture, so a surviving copy reports it as untracked.
            status_code, status = self._git(dest, "status", "--porcelain")
            self.assertEqual(status_code, 0, f"git must read the copied tree, got: {status}")
            self.assertIn("?? uv.lock", status, "uv.lock must survive the copy")


if __name__ == "__main__":
    unittest.main()
