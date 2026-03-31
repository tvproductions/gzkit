"""Tests for OBPI-0.0.9-04: Lifecycle auto-fix of brief frontmatter status."""

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.closeout_form import auto_fix_obpi_brief_frontmatter


class TestAutoFixObpiBriefFrontmatter(unittest.TestCase):
    """Verify auto_fix_obpi_brief_frontmatter syncs frontmatter to ledger state."""

    def _write_brief(self, tmp: Path, status: str) -> Path:
        brief = tmp / "OBPI-test.md"
        brief.write_text(
            f"---\nid: OBPI-test\nparent: ADR-test\nstatus: {status}\n---\n\n# Test\n",
            encoding="utf-8",
        )
        return brief

    def test_completed_state_fixes_draft_to_completed(self):
        """REQ-0.0.9-04-01/02/03: Frontmatter updated to Completed when ledger says so."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "attested_completed")
            self.assertTrue(changed)
            content = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", content)

    def test_validated_state_fixes_draft_to_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "validated")
            self.assertTrue(changed)
            content = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", content)

    def test_completed_runtime_fixes_draft_to_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "completed")
            self.assertTrue(changed)
            content = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", content)

    def test_no_change_when_already_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Completed")
            changed = auto_fix_obpi_brief_frontmatter(brief, "attested_completed")
            self.assertFalse(changed)

    def test_withdrawn_state_fixes_to_withdrawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "withdrawn")
            self.assertTrue(changed)
            content = brief.read_text(encoding="utf-8")
            self.assertIn("status: Withdrawn", content)

    def test_pending_state_does_not_change_draft(self):
        """Only fix toward terminal states — don't downgrade."""
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "pending")
            self.assertFalse(changed)

    def test_in_progress_state_does_not_change_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            changed = auto_fix_obpi_brief_frontmatter(brief, "in_progress")
            self.assertFalse(changed)

    def test_preserves_other_frontmatter_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "OBPI-test.md"
            brief.write_text(
                "---\nid: OBPI-test\nparent: ADR-test\nitem: 4\n"
                "lane: lite\nstatus: Draft\n---\n\n# Test\n",
                encoding="utf-8",
            )
            auto_fix_obpi_brief_frontmatter(brief, "attested_completed")
            content = brief.read_text(encoding="utf-8")
            self.assertIn("id: OBPI-test", content)
            self.assertIn("parent: ADR-test", content)
            self.assertIn("item: 4", content)
            self.assertIn("lane: lite", content)
            self.assertIn("status: Completed", content)


if __name__ == "__main__":
    unittest.main()
