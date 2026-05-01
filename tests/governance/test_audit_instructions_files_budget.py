"""Fixture-level tests for ``audit_instructions_files_budget`` (GHI #373).

These tests pin the boundary semantics — at-budget passes, +1 char fails —
and isolate the audit from the live AGENTS.md / CLAUDE.md / .claude/rules/.
The repo-lock check is `gz check`'s responsibility; this module gates the
scan semantics.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_instructions_files_budget


class InstructionsFilesBudgetAuditTests(unittest.TestCase):
    """Audit walks AGENTS.md / CLAUDE.md / glob-matched rule files."""

    def _write_budget(
        self, root: Path, files: dict[str, int], globs: list[dict[str, object]] | None = None
    ) -> None:
        target = root / "data" / "instructions_files_budget.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {"files": files}
        if globs is not None:
            payload["globs"] = globs
        target.write_text(json.dumps(payload), encoding="utf-8")

    def test_at_budget_boundary_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(errors, [])

    def test_overrun_by_one_char_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 101, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].type, "instructions_files_budget")
            self.assertIn("AGENTS.md", errors[0].artifact)

    def test_under_budget_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"CLAUDE.md": 100})
            (root / "CLAUDE.md").write_text("x" * 50, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(errors, [])

    def test_missing_file_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100, "CLAUDE.md": 100})
            errors = audit_instructions_files_budget(root)
            self.assertEqual(errors, [])

    def test_glob_per_file_budget_flags_overrun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "ok.md").write_text("x" * 100, encoding="utf-8")
            (rules / "fat.md").write_text("x" * 200, encoding="utf-8")
            self._write_budget(
                root,
                {},
                [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}],
            )
            errors = audit_instructions_files_budget(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("fat.md", errors[0].artifact)

    def test_glob_no_matches_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(
                root,
                {},
                [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}],
            )
            errors = audit_instructions_files_budget(root)
            self.assertEqual(errors, [])

    def test_remediation_pointer_in_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10})
            (root / "AGENTS.md").write_text("x" * 11, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("gz-context-diet", errors[0].message)

    def test_message_names_chars_and_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 50})
            (root / "AGENTS.md").write_text("x" * 75, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("75", errors[0].message)
            self.assertIn("50", errors[0].message)

    def test_missing_budget_data_uses_packaged_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertEqual(errors, [])

    def test_error_type_is_instructions_files_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10})
            (root / "AGENTS.md").write_text("x" * 50, encoding="utf-8")
            errors = audit_instructions_files_budget(root)
            self.assertTrue(all(e.type == "instructions_files_budget" for e in errors))


if __name__ == "__main__":
    unittest.main()
