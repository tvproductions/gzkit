"""Skill-surface-sync invariants from OBPI-0.0.57-02.

REQ-0.0.57-02-05: skill-version + last_reviewed advanced for gz-adr-create
REQ-0.0.57-02-06: vendor mirror is byte-equivalent to canonical skill

The allocator REQs this module once covered (REQ-0.0.57-02-01 through -02-04)
are superseded by ADR-0.34.0 (Foundation Sunset): `_next_free_nominal_
foundation_id` was deleted with the foundation authoring path it served, so
no honest test can cover them. They are annotated as superseded in the
OBPI-0.0.57-02 brief. They are deliberately NOT listed above — a REQ id left
in this docstring is read as coverage by the `gz covers` scanner, which would
report a deleted allocator as proven.
"""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).parent.parent
_SKILL_CANONICAL = _PROJECT_ROOT / ".gzkit" / "skills" / "gz-adr-create" / "SKILL.md"
_SKILL_MIRROR_CLAUDE = _PROJECT_ROOT / ".claude" / "skills" / "gz-adr-create" / "SKILL.md"


class TestGzAdrCreateSkillEnrichment(unittest.TestCase):
    """Skill-surface-sync invariants enforced by this OBPI's edit to gz-adr-create."""

    @covers("REQ-0.0.57-02-05")
    def test_skill_version_bumped_to_6_5_or_higher(self) -> None:
        """Canonical SKILL.md skill-version must be >= 6.5.0 (minor bump for doctrine change)."""
        content = _SKILL_CANONICAL.read_text(encoding="utf-8")
        m = re.search(r'skill-version:\s*"(\d+)\.(\d+)\.(\d+)"', content)
        self.assertIsNotNone(m, "skill-version frontmatter field must exist")
        major, minor, _patch = (int(g) for g in m.groups())
        self.assertGreaterEqual(
            (major, minor),
            (6, 5),
            "skill-version must be >= 6.5.0 after the nominal-allocator doctrine change",
        )

    @covers("REQ-0.0.57-02-05")
    def test_last_reviewed_bumped_to_landing_date_or_later(self) -> None:
        """Canonical SKILL.md last_reviewed must be on or after 2026-05-23 (landing-day floor)."""
        content = _SKILL_CANONICAL.read_text(encoding="utf-8")
        m = re.search(r"last_reviewed:\s*(\d{4}-\d{2}-\d{2})", content)
        self.assertIsNotNone(m, "last_reviewed frontmatter field must exist")
        reviewed = date.fromisoformat(m.group(1))
        self.assertGreaterEqual(
            reviewed,
            date(2026, 5, 23),
            "last_reviewed must be advanced in the same edit as skill-version (rule #6)",
        )

    @covers("REQ-0.0.57-02-06")
    def test_claude_mirror_is_byte_equivalent_to_canonical(self) -> None:
        """The .claude/skills mirror must be byte-equivalent to .gzkit/skills (sync invariant)."""
        canonical_bytes = _SKILL_CANONICAL.read_bytes()
        mirror_bytes = _SKILL_MIRROR_CLAUDE.read_bytes()
        self.assertEqual(
            canonical_bytes,
            mirror_bytes,
            ".claude/skills/gz-adr-create/SKILL.md must be byte-equivalent to canonical "
            "(run `uv run gz agent sync control-surfaces` to refresh)",
        )


if __name__ == "__main__":
    unittest.main()
