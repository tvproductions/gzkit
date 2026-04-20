"""Tests for ledger and skill-sync guards added under GHIs #207 / #210."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from gzkit.hooks import guards

_stdout_ctx: redirect_stdout[io.StringIO] | None = None
_stderr_ctx: redirect_stderr[io.StringIO] | None = None


def setUpModule() -> None:
    # The guards emit warnings via _safe_print on the failure paths. These
    # tests only assert the return code, so route the warning output to a
    # buffer to keep the test runner output clean (GHI #253 follow-up).
    global _stdout_ctx, _stderr_ctx
    _stdout_ctx = redirect_stdout(io.StringIO())
    _stderr_ctx = redirect_stderr(io.StringIO())
    _stdout_ctx.__enter__()
    _stderr_ctx.__enter__()


def tearDownModule() -> None:
    assert _stderr_ctx is not None and _stdout_ctx is not None
    _stderr_ctx.__exit__(None, None, None)
    _stdout_ctx.__exit__(None, None, None)


class TestForbidManualLedgerEdits(unittest.TestCase):
    """forbid_manual_ledger_edits rejects non-append staged diffs."""

    def test_no_staged_diff_returns_zero(self) -> None:
        with mock.patch.object(guards, "_run_git", return_value=""):
            self.assertEqual(guards.forbid_manual_ledger_edits(mock.sentinel.root), 0)

    def test_append_only_diff_returns_zero(self) -> None:
        diff = (
            "--- a/.gzkit/ledger.jsonl\n"
            "+++ b/.gzkit/ledger.jsonl\n"
            "@@ -1,1 +1,2 @@\n"
            ' {"event": "x"}\n'
            '+{"event": "y"}\n'
        )
        with mock.patch.object(guards, "_run_git", return_value=diff):
            self.assertEqual(guards.forbid_manual_ledger_edits(mock.sentinel.root), 0)

    def test_line_deletion_fails(self) -> None:
        diff = (
            "--- a/.gzkit/ledger.jsonl\n"
            "+++ b/.gzkit/ledger.jsonl\n"
            "@@ -1,2 +1,1 @@\n"
            '-{"event": "x"}\n'
            ' {"event": "y"}\n'
        )
        with mock.patch.object(guards, "_run_git", return_value=diff):
            self.assertEqual(guards.forbid_manual_ledger_edits(mock.sentinel.root), 1)


class TestForbidSkillSyncDrift(unittest.TestCase):
    """forbid_skill_sync_drift rejects canonical edits missing their mirrors."""

    def test_no_staged_diff_returns_zero(self) -> None:
        with mock.patch.object(guards, "_run_git", return_value=""):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_with_mirror_returns_zero(self) -> None:
        names = ".gzkit/skills/foo/SKILL.md\n.claude/skills/foo/SKILL.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_missing_mirror_fails(self) -> None:
        names = ".gzkit/skills/foo/SKILL.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 1)

    def test_canonical_rule_missing_mirror_fails(self) -> None:
        names = ".gzkit/rules/new-rule.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 1)

    def test_canonical_rule_with_github_mirror_returns_zero(self) -> None:
        names = ".gzkit/rules/new-rule.md\n.github/instructions/new-rule.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)


if __name__ == "__main__":
    unittest.main()
