"""Skill enrichment correctness tests for OBPI-0.0.35-02.

Verifies that the four kind-deciding skills (gz-design, gz-plan,
gz-adr-create, gz-adr-promote) contain the invariance test, hexagonal-ports
lens, and concept-page link as required by ADR-0.0.35.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CANONICAL_SKILLS_ROOT = _PROJECT_ROOT / ".gzkit" / "skills"
_CLAUDE_SKILLS_ROOT = _PROJECT_ROOT / ".claude" / "skills"
_GITHUB_SKILLS_ROOT = _PROJECT_ROOT / ".github" / "skills"

_INVARIANCE_TEST = "Foundation = without it, we wouldn't be doing the project"
_HEXAGONAL_LENS = "ports point to invariance; adapters are features"
_CONCEPT_PAGE_LINK = "foundation-feature-invariance-test"

_EXPECTED_VERSIONS: dict[str, str] = {
    "gz-plan": "1.3.2",
    "gz-adr-create": "6.5.0",
    "gz-design": "1.3.1",
    "gz-adr-promote": "1.5.0",
}


def _skill_content(slug: str) -> str:
    return (_CANONICAL_SKILLS_ROOT / slug / "SKILL.md").read_text(encoding="utf-8")


class TestSkillInvarianceTestEnrichment(unittest.TestCase):
    """REQ-0.0.35-02-01: All four skills contain the verbatim invariance test."""

    @covers("REQ-0.0.35-02-01")
    def test_gz_design_has_invariance_test(self) -> None:
        self.assertIn(_INVARIANCE_TEST, _skill_content("gz-design"))

    @covers("REQ-0.0.35-02-01")
    def test_gz_plan_has_invariance_test(self) -> None:
        self.assertIn(_INVARIANCE_TEST, _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-01")
    def test_gz_adr_create_has_invariance_test(self) -> None:
        self.assertIn(_INVARIANCE_TEST, _skill_content("gz-adr-create"))

    @covers("REQ-0.0.35-02-01")
    def test_gz_adr_promote_has_invariance_test(self) -> None:
        self.assertIn(_INVARIANCE_TEST, _skill_content("gz-adr-promote"))


class TestSkillHexagonalLens(unittest.TestCase):
    """REQ-0.0.35-02-02: All four skills contain the hexagonal-ports lens."""

    @covers("REQ-0.0.35-02-02")
    def test_gz_design_has_hexagonal_lens(self) -> None:
        self.assertIn(_HEXAGONAL_LENS, _skill_content("gz-design"))

    @covers("REQ-0.0.35-02-02")
    def test_gz_plan_has_hexagonal_lens(self) -> None:
        self.assertIn(_HEXAGONAL_LENS, _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-02")
    def test_gz_adr_create_has_hexagonal_lens(self) -> None:
        self.assertIn(_HEXAGONAL_LENS, _skill_content("gz-adr-create"))

    @covers("REQ-0.0.35-02-02")
    def test_gz_adr_promote_has_hexagonal_lens(self) -> None:
        self.assertIn(_HEXAGONAL_LENS, _skill_content("gz-adr-promote"))


class TestSkillConceptPageLink(unittest.TestCase):
    """REQ-0.0.35-02-03: All four skills link to the concept page."""

    @covers("REQ-0.0.35-02-03")
    def test_gz_design_has_concept_page_link(self) -> None:
        self.assertIn(_CONCEPT_PAGE_LINK, _skill_content("gz-design"))

    @covers("REQ-0.0.35-02-03")
    def test_gz_plan_has_concept_page_link(self) -> None:
        self.assertIn(_CONCEPT_PAGE_LINK, _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-03")
    def test_gz_adr_create_has_concept_page_link(self) -> None:
        self.assertIn(_CONCEPT_PAGE_LINK, _skill_content("gz-adr-create"))

    @covers("REQ-0.0.35-02-03")
    def test_gz_adr_promote_has_concept_page_link(self) -> None:
        self.assertIn(_CONCEPT_PAGE_LINK, _skill_content("gz-adr-promote"))


class TestSkillVersionBump(unittest.TestCase):
    """REQ-0.0.35-02-04: All four skills have their skill-version at expected post-edit value."""

    def _read_skill_version(self, slug: str) -> str:
        for line in _skill_content(slug).splitlines():
            if "skill-version" in line and ":" in line:
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return ""

    @covers("REQ-0.0.35-02-04")
    def test_gz_plan_version_bumped(self) -> None:
        self.assertEqual(self._read_skill_version("gz-plan"), _EXPECTED_VERSIONS["gz-plan"])

    @covers("REQ-0.0.35-02-04")
    def test_gz_adr_create_version_bumped(self) -> None:
        expected = _EXPECTED_VERSIONS["gz-adr-create"]
        self.assertEqual(self._read_skill_version("gz-adr-create"), expected)

    @covers("REQ-0.0.35-02-04")
    def test_gz_design_version_bumped(self) -> None:
        self.assertEqual(self._read_skill_version("gz-design"), _EXPECTED_VERSIONS["gz-design"])

    @covers("REQ-0.0.35-02-04")
    def test_gz_adr_promote_version_bumped(self) -> None:
        expected = _EXPECTED_VERSIONS["gz-adr-promote"]
        self.assertEqual(self._read_skill_version("gz-adr-promote"), expected)


class TestSkillMirrorParity(unittest.TestCase):
    """REQ-0.0.35-02-05: Mirror files match canonical after sync."""

    def _assert_mirror_parity(self, slug: str, mirror_root: Path) -> None:
        canonical = (_CANONICAL_SKILLS_ROOT / slug / "SKILL.md").read_bytes()
        mirror_path = mirror_root / slug / "SKILL.md"
        self.assertTrue(mirror_path.exists(), f"Mirror missing: {mirror_path}")
        mirror = mirror_path.read_bytes()
        self.assertEqual(
            canonical,
            mirror,
            f"Mirror drift for {slug} at {mirror_root.name}/skills/",
        )

    @covers("REQ-0.0.35-02-05")
    def test_gz_design_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-design", _CLAUDE_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_plan_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-plan", _CLAUDE_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_create_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-create", _CLAUDE_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_promote_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-promote", _CLAUDE_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_design_github_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-design", _GITHUB_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_plan_github_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-plan", _GITHUB_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_create_github_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-create", _GITHUB_SKILLS_ROOT)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_promote_github_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-promote", _GITHUB_SKILLS_ROOT)


class TestSkillEditSurgical(unittest.TestCase):
    """REQ-0.0.35-02-06: Edits are surgical — key non-enrichment content preserved."""

    @covers("REQ-0.0.35-02-06")
    def test_gz_plan_adr_taxonomy_link_preserved(self) -> None:
        """ADR-0.0.18 taxonomy link coexists with the invariance test."""
        self.assertIn("adr-taxonomy.md", _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_adr_create_adr_taxonomy_link_preserved(self) -> None:
        self.assertIn("adr-taxonomy.md", _skill_content("gz-adr-create"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_plan_workflow_section_preserved(self) -> None:
        """Core Workflow section is intact."""
        self.assertIn("gz plan create", _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_adr_create_procedure_section_preserved(self) -> None:
        """Procedure section is intact."""
        self.assertIn("## Procedure", _skill_content("gz-adr-create"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_design_step5_book_artifact_preserved(self) -> None:
        """Step 5 Book the Artifact section is intact."""
        self.assertIn("Book the Artifact", _skill_content("gz-design"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_adr_promote_options_section_preserved(self) -> None:
        """Options section is intact."""
        self.assertIn("## Options", _skill_content("gz-adr-promote"))


if __name__ == "__main__":
    unittest.main()
