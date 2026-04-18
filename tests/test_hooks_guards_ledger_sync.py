"""Tests for ledger and skill-sync guards added under GHIs #207 / #210."""

from __future__ import annotations

import unittest
from unittest import mock

from gzkit.hooks import guards


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
