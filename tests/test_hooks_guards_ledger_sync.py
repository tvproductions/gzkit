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
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        diff = (
            "--- a/.gzkit/ledger.jsonl\n"
            "+++ b/.gzkit/ledger.jsonl\n"
            "@@ -1,2 +1,1 @@\n"
            '-{"event": "x"}\n'
            ' {"event": "y"}\n'
        )
        with (
            mock.patch.object(guards, "_run_git", return_value=diff),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(guards.forbid_manual_ledger_edits(mock.sentinel.root), 1)


class TestForbidSkillSyncDrift(unittest.TestCase):
    """forbid_skill_sync_drift rejects canonical edits missing their mirrors."""

    def _project(self):
        """A project root declaring claude+codex and disabling copilot.

        The guard derives its mirror roots from `.gzkit.json`, so a test that
        asserts which vendors it names must supply a declared vendor set --
        `has_vendor_declaration` reads `model_fields_set`, and an undeclared
        config is deliberately treated as "every root applies".
        """
        import json  # noqa: PLC0415
        import tempfile  # noqa: PLC0415
        from pathlib import Path  # noqa: PLC0415

        tmp = tempfile.TemporaryDirectory()
        self.root = Path(tmp.name)
        (self.root / ".gzkit.json").write_text(
            json.dumps(
                {
                    "vendors": {
                        "claude": {"enabled": True, "surface_root": ".claude"},
                        "codex": {"enabled": True, "surface_root": ".agents"},
                        "copilot": {"enabled": False, "surface_root": ".github"},
                    }
                }
            ),
            encoding="utf-8",
        )
        return tmp

    def test_no_staged_diff_returns_zero(self) -> None:
        with mock.patch.object(guards, "_run_git", return_value=""):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_with_mirror_returns_zero(self) -> None:
        names = "M\t.gzkit/skills/foo/SKILL.md\nM\t.claude/skills/foo/SKILL.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_missing_mirror_fails(self) -> None:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        names = "M\t.gzkit/skills/foo/SKILL.md\n"
        with (
            mock.patch.object(guards, "_run_git", return_value=names),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 1)

    def test_canonical_skill_deletion_without_mirror_returns_zero(self) -> None:
        """Retire-on-delete (GHI #464): canonical deletions are exempt from the
        mirror requirement. The mirror is either already-absent or also being
        deleted in the same commit; either is non-drift."""
        names = "D\t.gzkit/skills/foo/SKILL.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_rule_missing_mirror_fails(self) -> None:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        names = "A\t.gzkit/rules/new-rule.md\n"
        with (
            mock.patch.object(guards, "_run_git", return_value=names),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 1)

    def test_canonical_rule_with_claude_mirror_returns_zero(self) -> None:
        """`.claude/rules/` is the surviving rule mirror.

        Retargeted 2026-08-29 (GHI #921) from `.github/instructions/`, which the
        Copilot drop deleted. The assertion this test makes -- a canonical rule
        staged with its vendor mirror satisfies the guard -- is unchanged; only
        the vendor that supplies the mirror moved. Codex consumes rules through
        the nested `AGENTS.md` projection and has no `.agents/rules/` tree, so
        `.claude/rules/` is the whole rule-mirror set.
        """
        names = "A\t.gzkit/rules/new-rule.md\nA\t.claude/rules/new-rule.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_with_codex_mirror_returns_zero(self) -> None:
        """`.agents/skills/` is a live mirror and must satisfy the skill guard.

        Added 2026-08-29 (GHI #921): the guard named `.github/skills/` as the
        alternative to `.claude/skills/` and never learned about Codex, so a
        skill staged with only its Codex mirror was reported as drift.
        """
        names = "M\t.gzkit/skills/foo/SKILL.md\nM\t.agents/skills/foo/SKILL.md\n"
        with self._project(), mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(self.root), 0)

    def test_guard_names_no_retired_vendor_tree(self) -> None:
        """The guard's error text may not name a dropped vendor's tree.

        A guard that tells an operator to look for `.github/skills/` after the
        Copilot drop sends them to a path that cannot exist; the remedy it
        prints is then unfollowable.
        """
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        buf = io.StringIO()
        names = "M\t.gzkit/skills/foo/SKILL.md\n"
        with (
            self._project(),
            mock.patch.object(guards, "_run_git", return_value=names),
            contextlib.redirect_stdout(buf),
        ):
            guards.forbid_skill_sync_drift(self.root)
        self.assertNotIn(".github/", buf.getvalue())

    def test_canonical_rule_deletion_without_mirror_returns_zero(self) -> None:
        """Retire-on-delete (GHI #464) applies to rule deletions identically."""
        names = "D\t.gzkit/rules/retired-rule.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_subtree_aggregator_agents_md_is_exempt(self) -> None:
        """`.gzkit/rules/AGENTS.md` is the subtree-rules aggregator, not a per-rule
        file. Sync regenerates it without per-vendor mirrors. The drift hook must
        exempt it from the mirror requirement (GHI #370)."""
        names = "M\t.gzkit/rules/AGENTS.md\n"
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_rename_with_mirror_renames_returns_zero(self) -> None:
        """A skill directory rename stages `R<score>\\t<old>\\t<new>` three-field
        entries. The drift hook must parse those, keying detection on the new
        path so a renamed canonical skill stays paired with its renamed mirrors.
        Keying on the new path is also immune to git rename detection
        cross-pairing byte-identical SKILL.md files across vendor trees (GHI
        #488)."""
        names = (
            "R098\t.gzkit/skills/foo/SKILL.md\t.gzkit/skills/gz-foo/SKILL.md\n"
            "R098\t.claude/skills/foo/SKILL.md\t.claude/skills/gz-foo/SKILL.md\n"
            "R098\t.github/skills/foo/SKILL.md\t.github/skills/gz-foo/SKILL.md\n"
        )
        with mock.patch.object(guards, "_run_git", return_value=names):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 0)

    def test_canonical_skill_rename_without_mirror_fails(self) -> None:
        """A renamed canonical skill still requires its mirror in the same
        commit — the rename's new path is checked exactly like an edit, so
        rename handling does not open a drift escape hatch (GHI #488)."""
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        names = "R098\t.gzkit/skills/foo/SKILL.md\t.gzkit/skills/gz-foo/SKILL.md\n"
        with (
            mock.patch.object(guards, "_run_git", return_value=names),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(guards.forbid_skill_sync_drift(mock.sentinel.root), 1)


if __name__ == "__main__":
    unittest.main()
