"""Skill enrichment correctness tests for OBPI-0.0.35-02.

Verifies that the four kind-deciding skills (gz-design, gz-plan,
gz-adr-create, gz-adr-promote) contain the invariance test, hexagonal-ports
lens, and concept-page link as required by ADR-0.0.35.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.traceability import covers
from tests.vendor_surfaces import skill_mirror_roots

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CANONICAL_SKILLS_ROOT = _PROJECT_ROOT / ".gzkit" / "skills"
# Mirror roots follow vendor enablement; a hardcoded copilot root asserted a
# tree sync had correctly stopped writing (GHI #921).
_VENDOR_SKILL_ROOTS = skill_mirror_roots()

_INVARIANCE_TEST = "Foundation = without it, we wouldn't be doing the project"
_HEXAGONAL_LENS = "ports point to invariance; adapters are features"
_CONCEPT_PAGE_LINK = "foundation-feature-invariance-test"

# The versions OBPI-0.0.35-02 landed. REQ-0.0.35-02-04 asserts the version was
# *incremented from its pre-edit baseline*, not that it is frozen forever: the
# staleness gate (`.gzkit/rules/skill-surface-sync.md` #6) couples every review
# stamp to a version bump, so an equality pin here fails on each mandated review
# sweep. These are therefore a monotonic floor — the increment must have landed
# and must never regress.
_LANDED_VERSIONS: dict[str, str] = {
    "gz-plan": "1.3.2",
    "gz-adr-create": "6.6.2",
    "gz-design": "1.3.2",
    "gz-adr-promote": "1.6.0",
}


def _semver(raw: str) -> tuple[int, ...]:
    """Parse a dotted version into a comparable tuple."""
    return tuple(int(part) for part in raw.split("."))


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
    """REQ-0.0.35-02-04: all four skills carry a version at or above the landed increment."""

    def _read_skill_version(self, slug: str) -> str:
        for line in _skill_content(slug).splitlines():
            if "skill-version" in line and ":" in line:
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return ""

    def _assert_at_or_above_landed(self, slug: str) -> None:
        floor = _LANDED_VERSIONS[slug]
        actual = self._read_skill_version(slug)
        self.assertGreaterEqual(
            _semver(actual),
            _semver(floor),
            f"{slug} skill-version {actual!r} regressed below the "
            f"OBPI-0.0.35-02 landed increment {floor!r}",
        )

    @covers("REQ-0.0.35-02-04")
    def test_gz_plan_version_bumped(self) -> None:
        self._assert_at_or_above_landed("gz-plan")

    @covers("REQ-0.0.35-02-04")
    def test_gz_adr_create_version_bumped(self) -> None:
        self._assert_at_or_above_landed("gz-adr-create")

    @covers("REQ-0.0.35-02-04")
    def test_gz_design_version_bumped(self) -> None:
        self._assert_at_or_above_landed("gz-design")

    @covers("REQ-0.0.35-02-04")
    def test_gz_adr_promote_version_bumped(self) -> None:
        self._assert_at_or_above_landed("gz-adr-promote")


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
        self._assert_mirror_parity("gz-design", _VENDOR_SKILL_ROOTS[0])

    @covers("REQ-0.0.35-02-05")
    def test_gz_plan_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-plan", _VENDOR_SKILL_ROOTS[0])

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_create_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-create", _VENDOR_SKILL_ROOTS[0])

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_promote_claude_mirror_parity(self) -> None:
        self._assert_mirror_parity("gz-adr-promote", _VENDOR_SKILL_ROOTS[0])

    @covers("REQ-0.0.35-02-05")
    def test_gz_design_github_mirror_parity(self) -> None:
        for _root in _VENDOR_SKILL_ROOTS:
            self._assert_mirror_parity("gz-design", _root)

    @covers("REQ-0.0.35-02-05")
    def test_gz_plan_github_mirror_parity(self) -> None:
        for _root in _VENDOR_SKILL_ROOTS:
            self._assert_mirror_parity("gz-plan", _root)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_create_github_mirror_parity(self) -> None:
        for _root in _VENDOR_SKILL_ROOTS:
            self._assert_mirror_parity("gz-adr-create", _root)

    @covers("REQ-0.0.35-02-05")
    def test_gz_adr_promote_github_mirror_parity(self) -> None:
        for _root in _VENDOR_SKILL_ROOTS:
            self._assert_mirror_parity("gz-adr-promote", _root)


class TestSkillEditSurgical(unittest.TestCase):
    """REQ-0.0.35-02-06: Edits are surgical — key non-enrichment content preserved."""

    @covers("REQ-0.0.35-02-06")
    def test_gz_plan_adr_taxonomy_link_preserved(self) -> None:
        """ADR-0.0.18 taxonomy link coexists with the invariance test."""
        self.assertIn("adr-taxonomy.md", _skill_content("gz-plan"))

    @covers("REQ-0.0.35-02-06")
    def test_gz_adr_create_adr_taxonomy_link_preserved(self) -> None:
        self.assertIn("adr-taxonomy.md", _skill_content("gz-adr-create"))


class TestPoolAdrEvaluateGateCarveOut(unittest.TestCase):
    """GHI #595: gz-adr-evaluate cannot resolve a pool ADR (flat stub, no
    package), so both skills that mandate it must carve out the pool branch
    rather than mandating a step that errors on the artifact shape they
    themselves route to."""

    def test_gz_design_carves_out_pool_adrs_from_evaluate_step(self) -> None:
        self.assertIn("Pool ADRs are exempt", _skill_content("gz-design"))

    def test_gz_adr_create_carves_out_pool_adrs_from_evaluate_step(self) -> None:
        self.assertIn("Pool ADRs are exempt", _skill_content("gz-adr-create"))

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
