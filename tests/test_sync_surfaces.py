"""Regression tests for sync-generated surfaces.

@covers ADR-0.0.11  OBPI-0.0.11-04 agents-md-persona-section
"""

import unittest

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


if __name__ == "__main__":
    unittest.main()
