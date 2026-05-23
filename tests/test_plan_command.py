"""Tests for gz plan create nominal allocator (OBPI-0.0.57-02).

REQ-0.0.57-02-01: sparse tree {1,2,5,7} → returns "0.0.3" (lowest gap)
REQ-0.0.57-02-02: empty tree → returns "0.0.1"
REQ-0.0.57-02-03: contiguous {1,2,3} → returns "0.0.4" (degenerate)
REQ-0.0.57-02-04: old function absent; new function present
REQ-0.0.57-02-05: skill-version + last_reviewed advanced for gz-adr-create
REQ-0.0.57-02-06: vendor mirror is byte-equivalent to canonical skill
"""

from __future__ import annotations

import re
import unittest
from datetime import date
from pathlib import Path

from gzkit.commands.plan import _next_free_nominal_foundation_id
from gzkit.traceability import covers

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "foundation_nominal_allocator"
_PROJECT_ROOT = Path(__file__).parent.parent
_SKILL_CANONICAL = _PROJECT_ROOT / ".gzkit" / "skills" / "gz-adr-create" / "SKILL.md"
_SKILL_MIRROR_CLAUDE = _PROJECT_ROOT / ".claude" / "skills" / "gz-adr-create" / "SKILL.md"


class TestNextFreeNominalFoundationId(unittest.TestCase):
    @covers("REQ-0.0.57-02-01")
    def test_sparse_tree_returns_lowest_gap(self) -> None:
        """Given {1,2,5,7}, returns "0.0.3" — lowest unused integer."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "sparse_with_gap")
        self.assertEqual(result, "0.0.3")

    @covers("REQ-0.0.57-02-02")
    def test_empty_tree_returns_0_0_1(self) -> None:
        """Given empty foundation tree, returns "0.0.1"."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "empty")
        self.assertEqual(result, "0.0.1")

    @covers("REQ-0.0.57-02-03")
    def test_contiguous_tree_returns_next_after_max(self) -> None:
        """Given {1,2,3}, returns "0.0.4" — no gaps, degenerate case."""
        result = _next_free_nominal_foundation_id(FIXTURES_ROOT / "contiguous")
        self.assertEqual(result, "0.0.4")

    @covers("REQ-0.0.57-02-04")
    def test_old_odometer_name_absent(self) -> None:
        """_next_available_foundation_semver must not exist in plan module."""
        import gzkit.commands.plan as plan_module

        self.assertFalse(
            hasattr(plan_module, "_next_available_foundation_semver"),
            "_next_available_foundation_semver must be absent after rename",
        )

    @covers("REQ-0.0.57-02-04")
    def test_new_allocator_name_present(self) -> None:
        """_next_free_nominal_foundation_id must be importable from plan module."""
        import gzkit.commands.plan as plan_module

        self.assertTrue(
            hasattr(plan_module, "_next_free_nominal_foundation_id"),
            "_next_free_nominal_foundation_id must be present in plan module",
        )


class TestGzAdrCreateSkillEnrichment(unittest.TestCase):
    """Skill-surface-sync invariants enforced by this OBPI's edit to gz-adr-create."""

    @covers("REQ-0.0.57-02-05")
    def test_skill_version_bumped_to_6_5_or_higher(self) -> None:
        """Canonical SKILL.md skill-version must be >= 6.5.0 (minor bump for doctrine change)."""
        content = _SKILL_CANONICAL.read_text(encoding="utf-8")
        m = re.search(r'skill-version:\s*"(\d+)\.(\d+)\.(\d+)"', content)
        self.assertIsNotNone(m, "skill-version frontmatter field must exist")
        major, minor, _patch = (int(g) for g in m.groups())  # type: ignore[union-attr]
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
        reviewed = date.fromisoformat(m.group(1))  # type: ignore[union-attr]
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
