"""Tests for gzkit.personas — trait composition model."""

import unittest
from pathlib import Path

from gzkit.models.persona import PersonaFrontmatter, parse_persona_file
from gzkit.personas import compose_persona_frame
from gzkit.traceability import covers


class TestComposePersonaFrame(unittest.TestCase):
    """compose_persona_frame() unit tests."""

    @covers("REQ-0.0.11-03-01")
    def test_multi_trait_composition_order(self) -> None:
        """Traits compose in declaration order with grounding first."""
        fm = PersonaFrontmatter(
            name="tester",
            traits=["methodical", "thorough"],
            anti_traits=["shallow-compliance"],
            grounding="I verify every claim with evidence.",
        )
        frame = compose_persona_frame(fm)
        lines = frame.split("\n")
        # Grounding is the opening anchor
        self.assertEqual(lines[0], "I verify every claim with evidence.")
        # Traits follow grounding (after blank line)
        self.assertIn("You are methodical.", frame)
        self.assertIn("You are thorough.", frame)
        # Trait order matches declaration order
        idx_methodical = frame.index("You are methodical.")
        idx_thorough = frame.index("You are thorough.")
        self.assertLess(idx_methodical, idx_thorough)

    @covers("REQ-0.0.11-03-02")
    def test_anti_traits_in_suppression_section(self) -> None:
        """Anti-traits appear in a dedicated suppression section."""
        fm = PersonaFrontmatter(
            name="tester",
            traits=["methodical"],
            anti_traits=["shallow-compliance", "token-minimizer"],
            grounding="I verify every claim.",
        )
        frame = compose_persona_frame(fm)
        self.assertIn("What this persona does NOT do:", frame)
        self.assertIn("- shallow-compliance", frame)
        self.assertIn("- token-minimizer", frame)
        # Suppression section comes after traits
        idx_trait = frame.index("You are methodical.")
        idx_suppression = frame.index("What this persona does NOT do:")
        self.assertLess(idx_trait, idx_suppression)

    @covers("REQ-0.0.11-03-03")
    def test_deterministic_output(self) -> None:
        """Same input produces identical output across calls."""
        fm = PersonaFrontmatter(
            name="tester",
            traits=["methodical", "thorough"],
            anti_traits=["shallow-compliance"],
            grounding="I verify every claim with evidence.",
        )
        frame1 = compose_persona_frame(fm)
        frame2 = compose_persona_frame(fm)
        self.assertEqual(frame1, frame2)

    @covers("REQ-0.0.11-03-01")
    def test_body_enriches_trait_descriptions(self) -> None:
        """Body behavioral anchors enrich trait lines with descriptions."""
        fm = PersonaFrontmatter(
            name="tester",
            traits=["methodical", "thorough"],
            anti_traits=["shallow-compliance"],
            grounding="I verify every claim.",
        )
        body = (
            "# Tester Persona\n\n"
            "## Behavioral Anchors\n\n"
            "- **Methodical**: Follow the plan step by step.\n"
            "- **Thorough**: Check every edge case.\n\n"
            "## Anti-patterns\n\n"
            "- **Shallow-compliance**: Producing the minimum to pass.\n"
        )
        frame = compose_persona_frame(fm, body)
        self.assertIn("You are methodical: Follow the plan step by step.", frame)
        self.assertIn("You are thorough: Check every edge case.", frame)
        self.assertIn("- shallow-compliance: Producing the minimum to pass.", frame)

    @covers("REQ-0.0.11-03-01")
    def test_fallback_without_body(self) -> None:
        """Without body, traits use name-only format."""
        fm = PersonaFrontmatter(
            name="minimal",
            traits=["careful"],
            anti_traits=["hasty"],
            grounding="I take my time.",
        )
        frame = compose_persona_frame(fm)
        self.assertIn("You are careful.", frame)
        self.assertIn("- hasty", frame)
        self.assertNotIn(":", frame.split("You are careful.")[1].split("\n")[0])

    @covers("REQ-0.0.11-03-02")
    def test_empty_anti_traits_omits_section(self) -> None:
        """No anti-traits means no suppression section."""
        fm = PersonaFrontmatter(
            name="simple",
            traits=["focused"],
            anti_traits=[],
            grounding="I do one thing well.",
        )
        frame = compose_persona_frame(fm)
        self.assertNotIn("What this persona does NOT do:", frame)


class TestExemplarComposition(unittest.TestCase):
    """Integration: compose the shipped implementer persona."""

    @covers("REQ-0.0.11-03-03")
    def test_implementer_exemplar_composes_deterministically(self) -> None:
        """The shipped implementer.md produces a deterministic frame."""
        exemplar = Path(".gzkit/personas/implementer.md")
        if not exemplar.is_file():
            self.skipTest("exemplar not present")
        fm, body = parse_persona_file(exemplar)
        frame1 = compose_persona_frame(fm, body)
        frame2 = compose_persona_frame(fm, body)
        self.assertEqual(frame1, frame2)
        # Verify structural elements
        self.assertIn(fm.grounding, frame1)
        for trait in fm.traits:
            self.assertIn(f"You are {trait}", frame1)
        self.assertIn("What this persona does NOT do:", frame1)
        for at in fm.anti_traits:
            self.assertIn(at, frame1)

    @covers("REQ-0.0.11-03-01")
    def test_implementer_traits_enriched_from_body(self) -> None:
        """Implementer body enriches trait lines with descriptions."""
        exemplar = Path(".gzkit/personas/implementer.md")
        if not exemplar.is_file():
            self.skipTest("exemplar not present")
        fm, body = parse_persona_file(exemplar)
        frame = compose_persona_frame(fm, body)
        # Implementer body has behavioral anchors with descriptions
        self.assertIn("You are methodical:", frame)
        self.assertIn("You are test-first:", frame)
