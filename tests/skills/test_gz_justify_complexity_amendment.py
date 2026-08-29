"""TDD RED-phase tests for OBPI-0.0.30-05 gz-justify SKILL.md amendment.

Tests verify that the gz-justify skill file is amended with:
- A bumped skill-version from "6.0.1" to "6.1.0"
- A new "Authoring-time complexity hints" section in the body

``test_existing_structure_preserved`` covers regression protection and is
expected to PASS immediately (existing H2 sections are not changed yet).

``test_skill_version_bumped`` and ``test_new_section_present`` are expected
to FAIL (RED) because the SKILL.md has not been amended yet.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from gzkit.traceability import covers
from tests.vendor_surfaces import skill_mirror_paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = PROJECT_ROOT / ".gzkit" / "skills" / "gz-justify" / "SKILL.md"
VENDOR_MIRRORS = skill_mirror_paths("gz-justify")

_EXISTING_H2_SECTIONS = (
    "Purpose",
    "Procedure",
    "Acceptance Criteria",
)


def _read_skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise AssertionError("skill file does not begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("skill file frontmatter block is not closed")
    return yaml.safe_load(text[4:end])


class TestGzJustifyComplexityAmendment(unittest.TestCase):
    """Tests for the additive SKILL.md amendment required by OBPI-0.0.30-05."""

    @covers("REQ-0.0.30-05-05")
    def test_skill_version_bumped(self) -> None:
        """skill-version must be at or above the "6.1.0" amendment baseline.

        The REQ requires the amendment to have landed with a *bumped* version,
        not to sit at one exact string forever. Pinning equality made every
        later edit to the skill fail this test (observed 2026-07-21, when a
        90-day staleness repair bumped 6.1.0 -> 6.1.1), so the assertion
        tracked a snapshot rather than the requirement (`.gzkit/rules/tests.md`
        § "Tests assert semantics, not strings").
        """
        text = _read_skill_text()
        fm = _parse_frontmatter(text)
        metadata = fm.get("metadata")
        self.assertIsInstance(metadata, dict, "frontmatter must have a 'metadata' dict")
        assert isinstance(metadata, dict)
        skill_version = metadata.get("skill-version")
        self.assertIsNotNone(skill_version, "frontmatter must declare metadata.skill-version")

        def parse(value: str) -> tuple[int, ...]:
            return tuple(int(part) for part in str(value).split("."))

        self.assertGreaterEqual(
            parse(skill_version),
            parse("6.1.0"),
            f"skill-version {skill_version!r} is below the amendment baseline '6.1.0'",
        )

    @covers("REQ-0.0.30-05-01")
    @covers("REQ-0.0.30-05-05")
    def test_new_section_present(self) -> None:
        """SKILL.md body must contain 'Authoring-time complexity hints' after amendment.

        Expected RED: the section does not exist in the current SKILL.md.
        """
        text = _read_skill_text()
        self.assertIn(
            "Authoring-time complexity hints",
            text,
            "SKILL.md must contain an 'Authoring-time complexity hints' section "
            "after the additive amendment (REQ-0.0.30-05-01)",
        )

    @covers("REQ-0.0.30-05-01")
    def test_existing_structure_preserved(self) -> None:
        """Existing H2 sections must still be present after the amendment.

        Expected to PASS immediately (regression protection — structure unchanged).
        """
        text = _read_skill_text()
        h2_headings = [
            line[3:].strip()
            for line in text.splitlines()
            if line.startswith("## ") and not line.startswith("### ")
        ]
        for section in _EXISTING_H2_SECTIONS:
            self.assertIn(
                section,
                h2_headings,
                f"Existing H2 section '## {section}' must still be present after amendment",
            )

    @covers("REQ-0.0.30-05-06")
    def test_vendor_mirrors_byte_identical(self) -> None:
        """After gz agent sync control-surfaces, vendor mirrors must be byte-identical.

        Tests the post-sync state directly — the mirrors are checked against the
        canonical SKILL.md. If they diverge, the sync was not run or a mirror was
        edited directly (both are defects per .gzkit/rules/skill-surface-sync.md).
        """
        canonical = SKILL_PATH.read_text(encoding="utf-8")
        for mirror_path in VENDOR_MIRRORS:
            # No existence assertion: `read_text` raises FileNotFoundError, which
            # names the missing mirror just as clearly without asserting on the
            # filesystem (`.claude/rules/tests.md` § The discriminator).
            mirror = mirror_path.read_text(encoding="utf-8")
            self.assertEqual(
                canonical,
                mirror,
                f"vendor mirror {mirror_path} diverges from canonical SKILL.md",
            )


if __name__ == "__main__":
    unittest.main()
