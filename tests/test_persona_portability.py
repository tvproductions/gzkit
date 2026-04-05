"""Cross-project persona portability integration tests — OBPI-0.0.13-06.

Validates that the portable persona stack (scaffold, sync, validate) works
in a clean project root with no gzkit source or pre-existing personas,
proving portability to external consumers like airlineops.

@covers ADR-0.0.13  OBPI-0.0.13-06 cross-project-validation
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.models.persona import parse_persona_file, validate_persona_structure
from gzkit.personas import DEFAULT_PERSONAS, scaffold_default_personas
from gzkit.sync_surfaces import sync_persona_mirrors
from gzkit.validate import validate_personas

# Terms that MUST NOT appear in project-agnostic default personas or their
# vendor mirrors.  Extended from test_persona_scaffolding._GZKIT_TERMS to
# cover additional gzkit-specific references.
_GZKIT_TERMS = [
    "gzkit",
    "obpi",
    " adr",
    "prd",
    "pipeline",
    "pep 8",
    "pep8",
    "python",
    "ruff",
    "gz init",
    "gz agent",
    ".gzkit",
    "airlineops",
    "pipeline-orchestrator",
]


class TestPortableScaffoldingEndToEnd(unittest.TestCase):
    """REQ-0.0.13-06-01: Scaffolding creates valid personas in a clean project."""

    def test_scaffold_in_clean_project_creates_personas_dir(self) -> None:
        """gz init equivalent creates .gzkit/personas/ with default files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = scaffold_default_personas(root)
            personas_dir = root / ".gzkit" / "personas"
            self.assertTrue(personas_dir.is_dir())
            self.assertEqual(len(created), len(DEFAULT_PERSONAS))
            for p in created:
                self.assertTrue(p.exists(), f"Expected {p} to exist")

    def test_scaffolded_personas_validate_against_schema(self) -> None:
        """REQ-0.0.13-06-02: Each scaffolded file passes structural validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = scaffold_default_personas(root)
            for persona_path in created:
                with self.subTest(persona=persona_path.stem):
                    errors = validate_persona_structure(persona_path)
                    self.assertEqual(errors, [], f"{persona_path.stem}: {errors}")

    def test_scaffolded_personas_parse_with_pydantic(self) -> None:
        """Each scaffolded file produces valid PersonaFrontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = scaffold_default_personas(root)
            for persona_path in created:
                with self.subTest(persona=persona_path.stem):
                    fm, body = parse_persona_file(persona_path)
                    self.assertEqual(fm.name, persona_path.stem)
                    self.assertGreater(len(fm.traits), 0)
                    self.assertGreater(len(fm.anti_traits), 0)
                    self.assertGreater(len(fm.grounding.strip()), 0)
                    self.assertGreater(len(body.strip()), 0)

    def test_scaffolded_defaults_contain_no_gzkit_content(self) -> None:
        """REQ-0.0.13-06-04/05: Default personas are project-agnostic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = scaffold_default_personas(root)
            for persona_path in created:
                content = persona_path.read_text(encoding="utf-8").lower()
                with self.subTest(persona=persona_path.stem):
                    for term in _GZKIT_TERMS:
                        self.assertNotIn(
                            term,
                            content,
                            f"Default persona '{persona_path.stem}' contains "
                            f"project-specific term '{term}'",
                        )


class TestPortableSyncEndToEnd(unittest.TestCase):
    """REQ-0.0.13-06-03: Sync mirrors personas to vendor surfaces in a clean project."""

    def test_sync_creates_vendor_mirrors_in_clean_project(self) -> None:
        """Scaffold + sync creates .claude/personas/ in a fresh project root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            config = GzkitConfig()
            updated = sync_persona_mirrors(root, config)
            claude_dir = root / ".claude" / "personas"
            self.assertTrue(claude_dir.is_dir(), "Expected .claude/personas/ to exist")
            self.assertGreater(len(updated), 0)
            for name in DEFAULT_PERSONAS:
                mirror = claude_dir / f"{name}.md"
                self.assertTrue(mirror.exists(), f"Expected {mirror.name} in vendor mirror")

    def test_synced_mirrors_contain_persona_content(self) -> None:
        """Vendor mirrors contain grounding text from canonical source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            config = GzkitConfig()
            sync_persona_mirrors(root, config)
            for name in DEFAULT_PERSONAS:
                with self.subTest(persona=name):
                    canonical = root / ".gzkit" / "personas" / f"{name}.md"
                    fm, _ = parse_persona_file(canonical)
                    mirror = root / ".claude" / "personas" / f"{name}.md"
                    mirror_content = mirror.read_text(encoding="utf-8")
                    self.assertIn(
                        fm.grounding[:40],
                        mirror_content,
                        f"Vendor mirror for '{name}' missing grounding text",
                    )

    def test_sync_roundtrip_preserves_persona_identity(self) -> None:
        """Persona names match across canonical and vendor mirror."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            config = GzkitConfig()
            sync_persona_mirrors(root, config)
            canonical_names = {p.stem for p in (root / ".gzkit" / "personas").glob("*.md")}
            mirror_names = {p.stem for p in (root / ".claude" / "personas").glob("*.md")}
            self.assertEqual(canonical_names, mirror_names)


class TestPortableValidationEndToEnd(unittest.TestCase):
    """REQ-0.0.13-06-02: Validation works in a clean external project."""

    def test_validate_personas_passes_in_clean_project(self) -> None:
        """validate_personas() returns no errors on a freshly scaffolded project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            errors = validate_personas(root)
            self.assertEqual(errors, [])

    def test_custom_persona_validates_if_schema_compliant(self) -> None:
        """A project-specific persona (airlineops-style) passes validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            custom = personas_dir / "ops-agent.md"
            custom.write_text(
                "---\n"
                "name: ops-agent\n"
                "traits:\n"
                "  - operational-rigor\n"
                "  - data-aware\n"
                "anti-traits:\n"
                "  - untested-deployments\n"
                "grounding: >-\n"
                "  I operate airline systems where correctness matters.\n"
                "  Every change is verified before deployment.\n"
                "---\n\n"
                "# Ops Agent\n\n"
                "Operations-focused agent for airline data pipelines.\n",
                encoding="utf-8",
            )
            errors = validate_personas(root)
            self.assertEqual(errors, [], f"Custom persona failed: {errors}")

    def test_malformed_persona_rejected_in_external_project(self) -> None:
        """Validation catches a persona with missing required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            bad = personas_dir / "broken.md"
            bad.write_text(
                "---\nname: broken\ntraits: []\nanti-traits: []\ngrounding: ''\n---\n",
                encoding="utf-8",
            )
            errors = validate_personas(root)
            self.assertGreater(len(errors), 0, "Expected validation errors for malformed persona")


class TestNoGzkitContentLeakage(unittest.TestCase):
    """REQ-0.0.13-06-04/05: No gzkit-specific content leaks into external projects."""

    def test_default_persona_terms_blocklist(self) -> None:
        """DEFAULT_PERSONAS content contains no gzkit-specific terms."""
        for name, content in DEFAULT_PERSONAS.items():
            lower = content.lower()
            with self.subTest(persona=name):
                for term in _GZKIT_TERMS:
                    self.assertNotIn(
                        term,
                        lower,
                        f"DEFAULT_PERSONAS['{name}'] contains '{term}'",
                    )

    def test_vendor_mirrors_contain_no_gzkit_terms(self) -> None:
        """After sync, vendor mirror files contain no gzkit-specific terms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            config = GzkitConfig()
            sync_persona_mirrors(root, config)
            claude_dir = root / ".claude" / "personas"
            for mirror_file in claude_dir.glob("*.md"):
                content = mirror_file.read_text(encoding="utf-8").lower()
                with self.subTest(mirror=mirror_file.stem):
                    for term in _GZKIT_TERMS:
                        self.assertNotIn(
                            term,
                            content,
                            f"Vendor mirror '{mirror_file.stem}' contains '{term}'",
                        )


if __name__ == "__main__":
    unittest.main()
