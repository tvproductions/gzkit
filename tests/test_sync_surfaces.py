"""Regression tests for sync-generated surfaces.

@covers ADR-0.0.11  OBPI-0.0.11-04 agents-md-persona-section
@covers ADR-0.0.12  OBPI-0.0.12-07 agents-md-persona-reference
@covers ADR-0.0.13  OBPI-0.0.13-03 manifest-schema-persona-sync
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.templates import load_template, render_template
from gzkit.traceability import covers


class TestAgentsPersonaSection(unittest.TestCase):
    """Verify the mandatory Persona section in generated AGENTS.md."""

    def setUp(self) -> None:
        self.content = render_template(
            "agents",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            skills_catalog="(none)",
            sync_date="2026-01-01",
            local_content="",
        )

    @covers("REQ-0.0.11-04-01")
    def test_agents_template_has_persona_section(self) -> None:
        """Rendered AGENTS template contains ## Persona heading."""
        self.assertIn("## Persona", self.content)

    @covers("REQ-0.0.11-04-01")
    def test_agents_persona_references_control_surface(self) -> None:
        """Persona section references .gzkit/personas/ control surface."""
        self.assertIn(".gzkit/personas/", self.content)

    @covers("REQ-0.0.11-04-03")
    def test_agents_persona_forbids_expertise_claims(self) -> None:
        """Persona section warns against generic expertise claims."""
        self.assertIn("You are an expert", self.content)
        self.assertIn("never generic", self.content.lower())

    @covers("REQ-0.0.11-04-03")
    def test_agents_persona_frames_behavioral_identity(self) -> None:
        """Persona section describes virtue-ethics behavioral identity."""
        self.assertIn("behavioral", self.content.lower())
        self.assertIn("craftsmanship", self.content.lower())

    @covers("REQ-0.0.11-04-01")
    def test_persona_discovery_command(self) -> None:
        """Persona section includes discovery command."""
        self.assertIn("uv run gz personas list", self.content)


class TestAgentsPersonaReference(unittest.TestCase):
    """Verify persona reference integration in AGENTS.md (ADR-0.0.12-07)."""

    def setUp(self) -> None:
        self.content = render_template(
            "agents",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            skills_catalog="(none)",
            sync_date="2026-01-01",
            local_content="",
        )

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_references_main_session_grounding(self) -> None:
        """Persona section references the main-session persona grounding."""
        self.assertIn("main-session", self.content)
        self.assertIn("craftsperson", self.content)
        self.assertIn("governance not as overhead", self.content)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_lists_role_mapping(self) -> None:
        """Persona section contains role-mapping table with all personas."""
        for persona in [
            "main-session",
            "implementer",
            "narrator",
            "pipeline-orchestrator",
            "quality-reviewer",
            "spec-reviewer",
        ]:
            with self.subTest(persona=persona):
                self.assertIn(f"`{persona}`", self.content)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_does_not_inline_full_content(self) -> None:
        """Persona section references but does not inline full persona files."""
        # The full grounding is ~4 sentences; the reference is condensed.
        # Check that the full behavioral anchors section is NOT inlined.
        self.assertNotIn("## Behavioral Anchors", self.content)
        self.assertNotIn("## Anti-patterns", self.content)

    @covers("REQ-0.0.12-07-02")
    def test_persona_references_survive_regeneration(self) -> None:
        """Template round-trip produces identical persona section."""
        content_a = render_template(
            "agents",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            skills_catalog="(none)",
            sync_date="2026-01-01",
            local_content="",
        )
        content_b = render_template(
            "agents",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            skills_catalog="(none)",
            sync_date="2026-01-01",
            local_content="",
        )
        # Extract persona section from both renders
        persona_a = content_a.split("## Persona")[1].split("## Prime Directive")[0]
        persona_b = content_b.split("## Persona")[1].split("## Prime Directive")[0]
        self.assertEqual(persona_a, persona_b)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_references_adr_0_0_12(self) -> None:
        """Persona reference section cites ADR-0.0.12."""
        self.assertIn("ADR-0.0.12", self.content)


class TestAdrPersonaSection(unittest.TestCase):
    """Verify the Persona placeholder in the ADR template."""

    @covers("REQ-0.0.11-04-02")
    def test_adr_template_has_persona_section(self) -> None:
        """ADR template contains ## Persona heading."""
        content = load_template("adr")
        self.assertIn("## Persona", content)

    @covers("REQ-0.0.11-04-02")
    def test_adr_persona_precedes_intent(self) -> None:
        """Persona section appears before Intent in ADR template."""
        content = load_template("adr")
        persona_pos = content.index("## Persona")
        intent_pos = content.index("## Intent")
        self.assertLess(persona_pos, intent_pos)


class TestPersonaSyncMirrors(unittest.TestCase):
    """Verify persona files are mirrored to vendor surfaces (OBPI-0.0.13-03).

    @covers ADR-0.0.13  OBPI-0.0.13-03 manifest-schema-persona-sync
    """

    _PERSONA_CONTENT = (
        "---\nname: implementer\ntraits:\n  - methodical\n"
        "anti-traits:\n  - scope-creep\ngrounding: I implement with care.\n---\n\n"
        "# Implementer\n"
    )

    def test_persona_sync_mirrors_to_claude(self) -> None:
        """REQ-0.0.13-03-02: Sync mirrors .gzkit/personas/ to .claude/personas/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "implementer.md").write_text(self._PERSONA_CONTENT, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            updated = sync_persona_mirrors(root, config)

            mirror = root / ".claude" / "personas" / "implementer.md"
            self.assertTrue(mirror.exists(), f"Expected {mirror} to exist")
            content = mirror.read_text(encoding="utf-8")
            self.assertIn("I implement with care", content)
            self.assertTrue(len(updated) > 0)

    def test_persona_sync_respects_vendor_enablement(self) -> None:
        """REQ-0.0.13-03-03: Disabled vendor gets no persona mirror."""
        _persona = (
            "---\nname: main-session\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: I stay on task.\n---\n\n"
            "# Main\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "main-session.md").write_text(_persona, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config, vendor_aware=True)

            # Copilot is disabled by default
            copilot_mirror = root / ".github" / "personas" / "main-session.md"
            self.assertFalse(copilot_mirror.exists(), "Disabled vendor should not get mirror")

            # Claude is enabled by default
            claude_mirror = root / ".claude" / "personas" / "main-session.md"
            self.assertTrue(claude_mirror.exists(), "Enabled vendor should get mirror")

    def test_persona_sync_skips_when_no_personas_dir(self) -> None:
        """Sync returns empty list when .gzkit/personas/ does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            updated = sync_persona_mirrors(root, config)
            self.assertEqual(updated, [])

    def test_persona_sync_updates_stale_mirror(self) -> None:
        """REQ-0.0.13-03-06: Re-running sync updates changed persona files."""
        _v1 = (
            "---\nname: implementer\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: Version one.\n---\n\n"
            "# V1\n"
        )
        _v2 = (
            "---\nname: implementer\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: Version two.\n---\n\n"
            "# V2\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "implementer.md").write_text(_v1, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config)

            # Update canonical file
            (personas_dir / "implementer.md").write_text(_v2, encoding="utf-8")
            updated = sync_persona_mirrors(root, config)

            mirror = root / ".claude" / "personas" / "implementer.md"
            content = mirror.read_text(encoding="utf-8")
            self.assertIn("Version two", content)
            self.assertTrue(len(updated) > 0)

    def test_persona_sync_does_not_modify_canonical(self) -> None:
        """REQ-0.0.13-03-06: Sync is one-directional — canonical files unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            canonical = personas_dir / "implementer.md"
            canonical.write_text(self._PERSONA_CONTENT, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config)

            self.assertEqual(canonical.read_text(encoding="utf-8"), self._PERSONA_CONTENT)


if __name__ == "__main__":
    unittest.main()
