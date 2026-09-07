"""Contract tests for the shared test-fixture helpers in ``tests.commands.common``.

These assert properties the fixtures must hold for *other* tests to be sound,
so a regression here is a regression in every suite that builds a repo fixture.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.git_spawn_boundary import git_spawns_outside_boundary
from tests.commands.common import _ignore_transient_git, _init_git_repo, _isolated_git_env

_TESTS_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _TESTS_ROOT.parent


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
            env=_isolated_git_env(),
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
                env=_isolated_git_env(),
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
            env=_isolated_git_env(),
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


def _git_out(root: Path, *args: str, env: dict[str, str] | None = None) -> str:
    """Run ``git`` in *root* and return stdout, under the isolated env by default."""
    env = _isolated_git_env() if env is None else env
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        env=env,
    ).stdout.strip()


class _Sentinel:
    """A disposable hosting repository with one linked worktree (GHI #977).

    Models the layout the defect fired in: a checkout whose ``.git`` is a
    gitfile pointing at ``<repo>/.git/worktrees/<name>``. Git exports that
    directory — absolute — as ``GIT_DIR`` to every hook it runs from the
    linked worktree (measured 2026-09-07: ``GIT_DIR``, ``GIT_PREFIX=``,
    ``GIT_EXEC_PATH`` and ``GIT_EDITOR`` are the whole exported set; no
    ``GIT_WORK_TREE``). Its basename is not ``.git``, so a ``git init`` that
    inherits it re-initialises the hosting repo *and* guesses bare.
    """

    def __init__(self, tmp: Path) -> None:
        self.root = tmp / "sentinel"
        self.root.mkdir()
        _init_git_repo(self.root)
        # A distinctive identity: the fixture identities are what leaked.
        _git_out(self.root, "config", "user.name", "Sentinel")
        _git_out(self.root, "config", "user.email", "sentinel@example.invalid")
        self.linked = tmp / "linked"
        _git_out(self.root, "worktree", "add", "-q", str(self.linked), "-b", "linked")
        self.linked_gitdir = self.root / ".git" / "worktrees" / "linked"

    def hook_env(self) -> dict[str, str]:
        """Exactly what git exported to a pre-push hook from the linked worktree."""
        return {"GIT_DIR": str(self.linked_gitdir), "GIT_PREFIX": ""}

    def snapshot(self) -> dict[str, object]:
        """Every surface the defect rewrote or could have: config, index, refs, files."""
        return {
            "config": (self.root / ".git" / "config").read_bytes(),
            "index": (self.root / ".git" / "index").read_bytes(),
            "refs": _git_out(self.root, "for-each-ref"),
            "head": _git_out(self.root, "rev-parse", "HEAD"),
            "worktree_head": _git_out(self.linked, "rev-parse", "HEAD"),
            "files": sorted(
                (p.relative_to(self.root).as_posix(), p.read_bytes())
                for p in self.root.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(self.root).parts
            ),
        }


class TestFixtureGitIsolation(unittest.TestCase):
    """A fixture targeting a temp repo must operate on that repo alone (GHI #977).

    Measured 2026-09-07: a ``git push`` from a linked worktree ran the pre-push
    ``gz check`` hook, the suite's git-spawning fixtures inherited the hook's
    ``GIT_DIR``, and ``git init`` in a temp dir re-initialised the HOSTING
    repository as bare while ``git config user.name`` wrote the fixture
    identity into its shared ``.git/config``. ``.gzkit/rules/tests.md``
    § Isolation forbids touching the live store; the repository the suite
    runs in is that store.
    """

    def test_repo_local_git_variables_are_dropped_and_everything_else_is_kept(self) -> None:
        """The boundary is git's own repo-local set, not a blanket ``GIT_*`` scrub.

        Dropped: the variables git itself clears before running a child git
        against a different repository (``local_repo_env`` in git's
        ``environment.c``) plus the ``GIT_CONFIG_KEY_n``/``VALUE_n`` pairs
        that only mean anything under ``GIT_CONFIG_COUNT``. Kept: auth,
        transport, identity, diagnostics and the user's own global/system
        config routing — a fixture inherits those today by design, and a
        scrub that took them would change what the suite tests.
        """
        dropped = {
            "GIT_DIR": "/elsewhere/.git/worktrees/x",
            "GIT_WORK_TREE": "/elsewhere",
            "GIT_INDEX_FILE": "/elsewhere/.git/index",
            "GIT_COMMON_DIR": "/elsewhere/.git",
            "GIT_OBJECT_DIRECTORY": "/elsewhere/.git/objects",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/elsewhere/alt",
            "GIT_PREFIX": "",
            "GIT_CONFIG": "/elsewhere/config",
            "GIT_CONFIG_PARAMETERS": "'core.bare=true'",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Injected",
            "GIT_IMPLICIT_WORK_TREE": "1",
            "GIT_GRAFT_FILE": "/elsewhere/grafts",
            "GIT_SHALLOW_FILE": "/elsewhere/shallow",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_REPLACE_REF_BASE": "refs/replace/",
        }
        kept = {
            "GIT_SSH_COMMAND": "ssh -i key",
            "GIT_ASKPASS": "/usr/bin/askpass",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Hook Author",
            "GIT_COMMITTER_EMAIL": "hook@example.invalid",
            "GIT_CONFIG_GLOBAL": "/home/u/.gitconfig",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_EXEC_PATH": "/usr/libexec/git-core",
            "GIT_EDITOR": "true",
            "GIT_TRACE": "1",
            "PATH": "/usr/bin",
            "HOME": "/home/u",
        }
        scrubbed = _isolated_git_env({**dropped, **kept})
        self.assertEqual(
            scrubbed, kept, "only repo-local and config-injecting variables may be removed"
        )

    def test_the_boundary_reads_the_live_environment_by_default(self) -> None:
        with patch.dict(os.environ, {"GIT_DIR": "/elsewhere/.git", "GIT_SSH_COMMAND": "ssh"}):
            scrubbed = _isolated_git_env()
        self.assertNotIn("GIT_DIR", scrubbed, "the inherited GIT_DIR is the defect's carrier")
        self.assertEqual(scrubbed.get("GIT_SSH_COMMAND"), "ssh", "transport settings pass through")

    def test_fixture_init_lands_in_its_own_dir_under_a_foreign_git_dir(self) -> None:
        """The reported failure, against a disposable sentinel, guarded."""
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = _Sentinel(Path(tmp))
            before = sentinel.snapshot()
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            with patch.dict(os.environ, sentinel.hook_env()):
                sha = _init_git_repo(fixture)
            # The fixture got its OWN repository, with the commit the helper reports.
            self.assertEqual(
                Path(_git_out(fixture, "rev-parse", "--show-toplevel")).resolve(),
                fixture.resolve(),
                "the fixture's git commands must resolve to the fixture directory",
            )
            self.assertTrue(
                _git_out(fixture, "rev-parse", "HEAD").startswith(sha),
                "the fixture's HEAD must be the commit the helper created",
            )
            # The hosting repository is byte-for-byte what it was.
            self.assertEqual(sentinel.snapshot(), before, "the hosting repo must be untouched")
            self.assertEqual(_git_out(sentinel.root, "config", "--get", "core.bare"), "false")
            self.assertEqual(_git_out(sentinel.root, "config", "--get", "user.name"), "Sentinel")
            self.assertEqual(
                _git_out(sentinel.root, "status", "--porcelain"),
                "",
                "the hosting checkout must still be a clean, operable work tree",
            )

    def test_unguarded_fixture_shape_rewrites_the_hosting_repo(self) -> None:
        """The harness bites: the raw fixture shape corrupts the sentinel.

        Without this the guarded test above proves nothing — a sentinel that
        would have survived anyway is not evidence the boundary does work.
        This is the verbatim shape of ``tests/mx/test_mx_log.py::_init_git_repo``
        and ``tests/test_ledger.py:1767-1773`` before the repair.
        """
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = _Sentinel(Path(tmp))
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            raw = {**os.environ, **sentinel.hook_env()}
            subprocess.run(["git", "init", "-q"], cwd=fixture, check=True, env=raw)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=fixture, check=True, env=raw)
            self.assertEqual(
                _git_out(sentinel.root, "config", "--get", "core.bare"),
                "true",
                "git init under a linked worktree's GIT_DIR re-inits the hosting repo as bare",
            )
            self.assertEqual(
                _git_out(sentinel.root, "config", "--get", "user.name"),
                "Test",
                "git config under the inherited GIT_DIR writes the fixture identity upstream",
            )
            # The fixture dir never became a repository: git cannot resolve one there.
            probe = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=fixture,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=_isolated_git_env(),
            )
            self.assertNotEqual(probe.returncode, 0, "the fixture dir never got a repo")
            self.assertIn("not a git repository", probe.stderr)

    def test_scrubbing_does_not_redirect_a_command_run_inside_its_own_checkout(self) -> None:
        """Sanitisation must not move a command that means to inspect its hosting repo.

        A scrubbed ``git`` run inside a checkout discovers that checkout —
        the main one through ``.git/``, the linked one through its gitfile —
        so a test that inspects the repository it lives in reads the same
        repository with or without the boundary. Only a command run OUTSIDE
        any checkout changes meaning, and there the change is the repair.
        """
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = _Sentinel(Path(tmp))
            with patch.dict(os.environ, sentinel.hook_env()):
                scrubbed = _isolated_git_env()
                raw = dict(os.environ)
                for checkout, gitdir in (
                    (sentinel.linked, sentinel.linked_gitdir),
                    (sentinel.root, sentinel.root / ".git"),
                ):
                    with self.subTest(checkout=checkout.name):
                        self.assertEqual(
                            Path(
                                _git_out(checkout, "rev-parse", "--absolute-git-dir", env=scrubbed)
                            ).resolve(),
                            gitdir.resolve(),
                            "a scrubbed command resolves the checkout it runs in",
                        )
                        self.assertEqual(
                            Path(
                                _git_out(checkout, "rev-parse", "--show-toplevel", env=scrubbed)
                            ).resolve(),
                            checkout.resolve(),
                        )
                # In the linked worktree — where the hook actually ran — the
                # scrubbed and inherited views agree, so nothing was redirected.
                self.assertEqual(
                    _git_out(sentinel.linked, "rev-parse", "--absolute-git-dir", env=scrubbed),
                    _git_out(sentinel.linked, "rev-parse", "--absolute-git-dir", env=raw),
                )
                self.assertEqual(
                    _git_out(sentinel.linked, "rev-parse", "HEAD", env=scrubbed),
                    _git_out(sentinel.linked, "rev-parse", "HEAD", env=raw),
                )

    # --- the real hook path -------------------------------------------------

    def _install_pre_push(self, sentinel: _Sentinel, body: str) -> Path:
        """Install a pre-push hook through git's own hook mechanism and a local remote."""
        remote = sentinel.root.parent / "remote.git"
        _git_out(sentinel.root, "init", "-q", "--bare", str(remote))
        _git_out(sentinel.root, "remote", "add", "origin", str(remote))
        hooks = sentinel.root / ".git" / "hooks"
        hooks.mkdir(exist_ok=True)
        hook = hooks / "pre-push"
        hook.write_text("#!/bin/sh\n" + body, encoding="utf-8", newline="\n")
        hook.chmod(0o755)
        return hook

    def _push_from_linked(self, sentinel: _Sentinel) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "push", "origin", "linked"],
            cwd=sentinel.linked,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_isolated_git_env(),
        )

    def test_real_pre_push_hook_from_a_linked_worktree_leaves_the_hosting_repo_untouched(
        self,
    ) -> None:
        """End to end: git's real hook, a real push from a real linked worktree.

        The hook runs the shared fixture helper — the same code every suite
        calls — against an unrelated directory, exactly as the pre-push
        ``gz check`` gate did on 2026-09-07. A helper-only test would leave
        the hook's own environment export unexercised.
        """
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = _Sentinel(Path(tmp))
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            script = (
                "import pathlib, sys\n"
                f"sys.path.insert(0, {str(_PROJECT_ROOT)!r})\n"
                "from tests.commands.common import _init_git_repo\n"
                f"print('fixture', _init_git_repo(pathlib.Path({str(fixture)!r})))\n"
            )
            (Path(tmp) / "hook_body.py").write_text(script, encoding="utf-8")
            # git forwards a pre-push hook's stdout to the push's stdout (and
            # its stderr to stderr; measured 2026-09-07), so the hook's report
            # is read from the push itself, not from a file.
            self._install_pre_push(
                sentinel, f'"{sys.executable}" "{Path(tmp) / "hook_body.py"}" 2>&1\n'
            )
            before = sentinel.snapshot()
            pushed = self._push_from_linked(sentinel)
            self.assertEqual(pushed.returncode, 0, pushed.stdout + pushed.stderr)
            self.assertIn(
                "fixture ", pushed.stdout, f"the hook must have run the helper: {pushed.stdout}"
            )
            self.assertEqual(
                Path(_git_out(fixture, "rev-parse", "--show-toplevel")).resolve(),
                fixture.resolve(),
                "under the real hook the fixture must still initialise its own directory",
            )
            after = sentinel.snapshot()
            # The push itself legitimately adds the remote-tracking ref; the
            # rest of the hosting repo — config, index, HEAD, files — is untouched.
            self.assertEqual(after["config"], before["config"], "shared config must be untouched")
            self.assertEqual(after["index"], before["index"], "index must be untouched")
            self.assertEqual(after["head"], before["head"])
            self.assertEqual(after["worktree_head"], before["worktree_head"])
            self.assertEqual(after["files"], before["files"], "working files must be untouched")
            self.assertEqual(_git_out(sentinel.root, "config", "--get", "core.bare"), "false")
            self.assertEqual(_git_out(sentinel.root, "status", "--porcelain"), "")

    def test_real_pre_push_hook_exports_git_dir_and_the_raw_shape_corrupts(self) -> None:
        """The hook path really carries the defect: the raw shape under it bites."""
        with tempfile.TemporaryDirectory() as tmp:
            sentinel = _Sentinel(Path(tmp))
            fixture = Path(tmp) / "fixture"
            fixture.mkdir()
            self._install_pre_push(
                sentinel,
                'echo "GIT_DIR=$GIT_DIR"\n'
                f'cd "{fixture}" && git init -q && git config user.name Test\n',
            )
            pushed = self._push_from_linked(sentinel)
            self.assertEqual(pushed.returncode, 0, pushed.stdout + pushed.stderr)
            exported = [
                line.strip() for line in pushed.stdout.splitlines() if line.startswith("GIT_DIR=")
            ]
            self.assertEqual(len(exported), 1, pushed.stdout + pushed.stderr)
            self.assertEqual(
                Path(exported[0].removeprefix("GIT_DIR=")).resolve(),
                sentinel.linked_gitdir.resolve(),
                "git exports the linked worktree's gitdir as GIT_DIR to the hook",
            )
            self.assertEqual(_git_out(sentinel.root, "config", "--get", "core.bare"), "true")
            self.assertEqual(_git_out(sentinel.root, "config", "--get", "user.name"), "Test")


class TestEveryGitSpawnIsInsideTheBoundary(unittest.TestCase):
    """Structural fence: no test spawns ``git`` with the inherited environment.

    The repair is only as wide as the callers that go through it. A new
    fixture written the old way re-opens GHI #977 in full, so every
    ``subprocess.*(["git", ...])`` under ``tests/`` must pass an ``env``
    built by ``_isolated_git_env`` (or a local name bound from it). Scoped
    to literal ``git`` argv — the shape every one of the 86 sites measured
    2026-09-07 had; a helper taking its argv as a parameter is outside the
    fence and must be read. The predicate is production code
    (``gzkit.git_spawn_boundary``) so the enforcement floor's negative control
    ``git-fixture-isolation`` can drive it against a planted offender.
    """

    def _offenders(self) -> list[str]:
        return git_spawns_outside_boundary(_TESTS_ROOT)

    def test_no_git_subprocess_in_tests_inherits_the_environment(self) -> None:
        offenders = self._offenders()
        self.assertEqual(
            offenders,
            [],
            "git spawned with the inherited env rewrites whatever GIT_DIR names (GHI #977):\n"
            + "\n".join(offenders),
        )


if __name__ == "__main__":
    unittest.main()
