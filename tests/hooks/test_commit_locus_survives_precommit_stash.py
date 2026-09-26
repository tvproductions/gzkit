"""The commit-locus row must survive pre-commit's stash (GHI #1092).

pre-commit stashes unstaged changes before every hook stage, post-commit
included, and restores them with ``git apply`` afterwards. A post-commit hook
that appends to ``.gzkit/ledger.jsonl`` while the ledger itself carries
unstaged rows makes that restore conflict, so pre-commit rolls back every hook
write -- the recorder's row with it -- after the recorder has already printed
``recorded 1``. Mid-session the ledger nearly always carries unstaged rows, so
every partial-stage commit lost its row.

pre-commit runs ``<hook-type>.legacy`` before it stashes. ``gz init`` installs
the recorder there, which is what these tests drive through a real pre-commit.
The old wiring is kept as a control: if the fixture ever stops producing the
stash conflict, the acceptance assertions would pass vacuously, and the control
fails instead.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.hooks.commit_ledger import (
    RECORDER_HOOK_MARKER,
    RECORDER_HOOK_NAME,
    install_recorder_hook,
    recorder_undelivered_reason,
)
from tests.commands.common import _isolated_git_env

_BRIEF = "docs/design/adr/pre-release/ADR-0.35.0-x/obpis/OBPI-0.35.0-14-landing.md"
_LEDGER = ".gzkit/ledger.jsonl"
_SESSION_ROW = {
    "schema": "gzkit.ledger.v1",
    "event": "obpi_lock_ttl_warning",
    "id": "ttl-1",
    "ts": "2026-09-25T00:51:19+00:00",
}
_RECORDER = f"{sys.executable} -m gzkit.hooks.commit_ledger"

_NO_POST_COMMIT_HOOKS = """\
default_install_hook_types: [post-commit]
repos:
  - repo: local
    hooks:
      - id: noop
        name: noop
        entry: "true"
        language: system
        pass_filenames: false
        stages: [manual]
"""

_OLD_WIRING = f"""\
default_install_hook_types: [post-commit]
repos:
  - repo: local
    hooks:
      - id: ledger-commit-locus
        name: ledger-commit-locus
        entry: {_RECORDER}
        language: system
        pass_filenames: false
        always_run: true
        stages: [post-commit]
"""


def _pre_commit_command() -> list[str] | None:
    """Return a runnable pre-commit, or None. pre-commit is not a gzkit dependency."""
    candidates = [["pre-commit"]] if shutil.which("pre-commit") else []
    if shutil.which("uvx"):
        candidates.append(["uvx", "--offline", "pre-commit"])
    for command in candidates:
        try:
            probe = subprocess.run(
                [*command, "--version"],
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0:
            return command
    return None


_PRE_COMMIT = _pre_commit_command()


class _Repo:
    """A throwaway repository with pre-commit installed for post-commit."""

    def __init__(self, config: str) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="gzkit-1092-"))
        # pre-commit's store stays out of the operator's cache.
        self.base_env = {
            **os.environ,
            "PRE_COMMIT_HOME": str(self.root.parent / f"{self.root.name}-pc-home"),
        }
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "g0@users.noreply.github.com")
        self.git("config", "user.name", "g0")
        (self.root / ".gzkit").mkdir()
        (self.root / _LEDGER).write_text("", encoding="utf-8")
        (self.root / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        assert _PRE_COMMIT is not None
        subprocess.run(
            [*_PRE_COMMIT, "install", "--hook-type", "post-commit"],
            cwd=self.root,
            env=_isolated_git_env(self.base_env),
            check=True,
            capture_output=True,
        )

    @property
    def hooks_dir(self) -> Path:
        return self.root / ".git" / "hooks"

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=_isolated_git_env(self.base_env),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).stdout

    def session_appends_unstaged_row(self) -> None:
        with (self.root / _LEDGER).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_SESSION_ROW, separators=(",", ":")) + "\n")

    def partial_stage_commit_of_brief(self) -> str:
        """The bypass: a plain write, then a commit that stages only the brief."""
        target = self.root / _BRIEF
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("edited by sed\n", encoding="utf-8")
        self.git("add", _BRIEF)
        self.git("commit", "-qm", "brief edit")
        return self.git("rev-parse", "HEAD").strip()

    def rows(self) -> list[dict]:
        text = (self.root / _LEDGER).read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def commit_locus_rows(self, sha: str) -> list[dict]:
        return [
            r
            for r in self.rows()
            if r.get("event") == "artifact_edited"
            and r.get("path") == _BRIEF
            and r.get("commit") == sha
        ]


@unittest.skipIf(_PRE_COMMIT is None, "pre-commit is not runnable here (not a gzkit dependency)")
class RecorderSurvivesPreCommitStash(unittest.TestCase):
    """Acceptance for GHI #1092, driven through a real pre-commit."""

    def test_row_persists_alongside_unstaged_session_rows(self) -> None:
        repo = _Repo(_NO_POST_COMMIT_HOOKS)
        install_recorder_hook(repo.hooks_dir, command=_RECORDER)
        repo.session_appends_unstaged_row()

        sha = repo.partial_stage_commit_of_brief()

        self.assertEqual(len(repo.commit_locus_rows(sha)), 1, repo.rows())
        self.assertIn(_SESSION_ROW, repo.rows(), "the session's unstaged row must survive too")

    def test_clean_ledger_records_exactly_one_row(self) -> None:
        repo = _Repo(_NO_POST_COMMIT_HOOKS)
        install_recorder_hook(repo.hooks_dir, command=_RECORDER)

        sha = repo.partial_stage_commit_of_brief()

        self.assertEqual(len(repo.commit_locus_rows(sha)), 1, repo.rows())

    def test_fixture_reproduces_the_loss_under_the_old_wiring(self) -> None:
        """Control: the same commit through a pre-commit post-commit hook loses its row.

        Without this, a fixture that stopped provoking the stash conflict would
        let the acceptance tests pass on a mechanism nobody exercised.
        """
        repo = _Repo(_OLD_WIRING)
        repo.session_appends_unstaged_row()

        sha = repo.partial_stage_commit_of_brief()

        self.assertEqual(repo.commit_locus_rows(sha), [], repo.rows())
        self.assertIn(_SESSION_ROW, repo.rows())


class RecorderHookInstallation(unittest.TestCase):
    """``install_recorder_hook`` writes a hook pre-commit will run, and never clobbers."""

    def setUp(self) -> None:
        self.hooks_dir = Path(tempfile.mkdtemp(prefix="gzkit-1092-hooks-"))

    def test_installed_hook_is_executable_and_delivered(self) -> None:
        self.assertIsNotNone(recorder_undelivered_reason(self.hooks_dir))
        install_recorder_hook(self.hooks_dir)
        target = self.hooks_dir / RECORDER_HOOK_NAME
        self.assertTrue(os.access(target, os.X_OK))
        self.assertIsNone(recorder_undelivered_reason(self.hooks_dir))

    def test_reinstall_is_idempotent(self) -> None:
        install_recorder_hook(self.hooks_dir)
        first = (self.hooks_dir / RECORDER_HOOK_NAME).read_bytes()
        install_recorder_hook(self.hooks_dir)
        self.assertEqual((self.hooks_dir / RECORDER_HOOK_NAME).read_bytes(), first)

    def test_foreign_legacy_hook_is_never_overwritten(self) -> None:
        foreign = "#!/bin/sh\necho someone else's hook\n"
        target = self.hooks_dir / RECORDER_HOOK_NAME
        target.write_text(foreign, encoding="utf-8")
        status = install_recorder_hook(self.hooks_dir)
        self.assertEqual(target.read_text(encoding="utf-8"), foreign)
        self.assertIn("NOT installed", status)
        self.assertIsNotNone(recorder_undelivered_reason(self.hooks_dir))

    def test_non_executable_recorder_is_not_delivered(self) -> None:
        """pre-commit skips a legacy hook it cannot execute, so presence is not delivery."""
        install_recorder_hook(self.hooks_dir)
        target = self.hooks_dir / RECORDER_HOOK_NAME
        target.chmod(0o644)
        self.assertIn(RECORDER_HOOK_MARKER, target.read_text(encoding="utf-8"))
        self.assertIsNotNone(recorder_undelivered_reason(self.hooks_dir))


_SHIM = "#!/usr/bin/env bash\n# File generated by pre-commit: https://pre-commit.com\n"
_DECLARES_POST_COMMIT = """\
default_install_hook_types: [pre-push, post-commit]
repos:
  - repo: local
    hooks:
      - id: gz-check-pre-push
        name: gz check
        entry: uv run gz check
        language: system
        pass_filenames: false
        stages: [pre-push]
"""


class InitDeliversWhatTheAuditChecks(unittest.TestCase):
    """``gz init`` installs the recorder; the delivery audit reports when it is missing."""

    def _worktree(self, config: str) -> Path:
        root = Path(tempfile.mkdtemp(prefix="gzkit-1092-init-"))
        hooks = root / ".git" / "hooks"
        hooks.mkdir(parents=True)
        (root / ".pre-commit-config.yaml").write_text(config, encoding="utf-8")
        for hook_type in ("pre-push", "post-commit"):
            (hooks / hook_type).write_text(_SHIM, encoding="utf-8")
        return root

    def _advisories(self, root: Path) -> list[str]:
        from unittest import mock

        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        seen: list[str] = []
        with mock.patch(
            "gzkit.governance.trust_audits.session_green_gate.emit_advisory", seen.append
        ):
            errors = audit_session_green_gate(root, check_delivery=True)
        self.assertEqual(errors, [])
        return seen

    def test_missing_recorder_is_reported_with_its_recovery(self) -> None:
        root = self._worktree(_DECLARES_POST_COMMIT)
        advisories = self._advisories(root)
        self.assertEqual(len(advisories), 1, advisories)
        self.assertIn("commit-locus recorder is not installed", advisories[0])
        self.assertIn("gzkit.hooks.commit_ledger --install", advisories[0])

    def test_init_installs_the_recorder_the_audit_then_accepts(self) -> None:
        from gzkit.commands.init_cmd import _install_commit_locus_recorder

        root = self._worktree(_DECLARES_POST_COMMIT)
        status = _install_commit_locus_recorder(root)
        self.assertIn("Installed", status or "")
        self.assertEqual(self._advisories(root), [])

    def test_the_advised_recovery_installs_what_the_audit_checks(self) -> None:
        """The advisory's recovery command must actually clear the advisory."""
        root = self._worktree(_DECLARES_POST_COMMIT)
        subprocess.run(["git", "init", "-q"], cwd=root, env=_isolated_git_env(), check=True)
        result = subprocess.run(
            [sys.executable, "-m", "gzkit.hooks.commit_ledger", "--install"],
            cwd=root,
            env=_isolated_git_env(),
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self._advisories(root), [])

    def test_init_installs_nothing_when_post_commit_is_not_declared(self) -> None:
        from gzkit.commands.init_cmd import _install_commit_locus_recorder

        root = self._worktree(_DECLARES_POST_COMMIT.replace(", post-commit", ""))
        self.assertIsNone(_install_commit_locus_recorder(root))
        self.assertFalse((root / ".git" / "hooks" / RECORDER_HOOK_NAME).exists())


if __name__ == "__main__":
    unittest.main()
