"""Tests for vendor-neutral persona loading adapters (OBPI-0.0.13-04)."""

import unittest

from gzkit.models.persona import PersonaFrontmatter
from gzkit.personas import (
    VENDOR_ADAPTERS,
    render_persona_claude,
    render_persona_codex,
    render_persona_copilot,
    render_persona_for_vendor,
)
from gzkit.traceability import covers

# Shared test fixture — reused across all adapter tests.
_FM = PersonaFrontmatter(
    name="tester",
    traits=["methodical", "test-first"],
    anti_traits=["shallow-compliance", "scope-creep"],
    grounding="I verify every claim with evidence.",
)

_BODY = """\
# Tester Persona

## Behavioral Anchors

- **Methodical**: Plans before acting, traces every change to intent.
- **Test-first**: Writes tests before implementation code.

## Anti-patterns

- **Shallow-compliance**: Checking boxes without verifying substance.
- **Scope-creep**: Adding work outside the brief boundary.
"""


class TestRenderPersonaClaude(unittest.TestCase):
    """Claude adapter produces system prompt fragments."""

    @covers("REQ-0.0.13-04-01")
    def test_contains_traits_as_behavioral_instructions(self) -> None:
        """Claude output includes traits as 'You are X' instructions."""
        result = render_persona_claude(_FM, _BODY)
        self.assertIn("You are methodical:", result)
        self.assertIn("You are test-first:", result)

    @covers("REQ-0.0.13-04-01")
    def test_contains_grounding(self) -> None:
        """Claude output opens with the grounding text."""
        result = render_persona_claude(_FM, _BODY)
        self.assertTrue(result.startswith("I verify every claim with evidence."))

    @covers("REQ-0.0.13-04-01")
    def test_contains_anti_traits_as_constraints(self) -> None:
        """Claude output includes anti-traits in a suppression section."""
        result = render_persona_claude(_FM, _BODY)
        self.assertIn("What this persona does NOT do:", result)
        self.assertIn("shallow-compliance:", result)
        self.assertIn("scope-creep:", result)

    @covers("REQ-0.0.13-04-01")
    def test_without_body_uses_bare_traits(self) -> None:
        """Claude adapter works without body text (no descriptions)."""
        result = render_persona_claude(_FM)
        self.assertIn("You are methodical.", result)
        self.assertIn("You are test-first.", result)


class TestRenderPersonaCodex(unittest.TestCase):
    """Codex adapter produces AGENTS.md instruction blocks."""

    @covers("REQ-0.0.13-04-02")
    def test_produces_agents_md_heading(self) -> None:
        """Codex output starts with a markdown heading."""
        result = render_persona_codex(_FM, _BODY)
        self.assertIn("# Persona: tester", result)

    @covers("REQ-0.0.13-04-02")
    def test_contains_grounding(self) -> None:
        """Codex output includes the grounding text."""
        result = render_persona_codex(_FM, _BODY)
        self.assertIn("I verify every claim with evidence.", result)

    @covers("REQ-0.0.13-04-02")
    def test_contains_behavioral_traits_section(self) -> None:
        """Codex output includes a Behavioral Traits section with descriptions."""
        result = render_persona_codex(_FM, _BODY)
        self.assertIn("## Behavioral Traits", result)
        self.assertIn("- methodical: Plans before acting", result)
        self.assertIn("- test-first: Writes tests before implementation", result)

    @covers("REQ-0.0.13-04-02")
    def test_contains_anti_patterns_section(self) -> None:
        """Codex output includes an Anti-Patterns section."""
        result = render_persona_codex(_FM, _BODY)
        self.assertIn("## Anti-Patterns", result)
        self.assertIn("- shallow-compliance:", result)
        self.assertIn("- scope-creep:", result)

    @covers("REQ-0.0.13-04-02")
    def test_without_body_uses_bare_names(self) -> None:
        """Codex adapter uses bare trait names when no body is provided."""
        result = render_persona_codex(_FM)
        self.assertIn("- methodical", result)
        self.assertNotIn("- methodical:", result)


class TestRenderPersonaCopilot(unittest.TestCase):
    """Copilot adapter produces copilot-instructions.md fragments."""

    @covers("REQ-0.0.13-04-03")
    def test_produces_h2_heading(self) -> None:
        """Copilot output uses a ## heading (embeddable in instructions file)."""
        result = render_persona_copilot(_FM)
        self.assertIn("## Persona: tester", result)

    @covers("REQ-0.0.13-04-03")
    def test_contains_grounding(self) -> None:
        """Copilot output includes the grounding text."""
        result = render_persona_copilot(_FM)
        self.assertIn("I verify every claim with evidence.", result)

    @covers("REQ-0.0.13-04-03")
    def test_contains_inline_traits(self) -> None:
        """Copilot output lists traits inline."""
        result = render_persona_copilot(_FM)
        self.assertIn("Behavioral traits: methodical, test-first", result)

    @covers("REQ-0.0.13-04-03")
    def test_contains_inline_anti_traits(self) -> None:
        """Copilot output lists anti-traits inline."""
        result = render_persona_copilot(_FM)
        self.assertIn("Behaviors to avoid: shallow-compliance, scope-creep", result)


class TestVendorFallback(unittest.TestCase):
    """Unknown vendor falls back to raw canonical markdown."""

    @covers("REQ-0.0.13-04-04")
    def test_unknown_vendor_returns_raw_markdown(self) -> None:
        """Unregistered vendor gets canonical markdown with frontmatter."""
        result = render_persona_for_vendor("opencode", _FM, _BODY)
        self.assertIn("---", result)
        self.assertIn("name: tester", result)
        self.assertIn("traits:", result)
        self.assertIn("# Tester Persona", result)

    @covers("REQ-0.0.13-04-04")
    def test_known_vendor_uses_adapter(self) -> None:
        """Known vendor uses adapter instead of raw fallback."""
        result = render_persona_for_vendor("claude", _FM, _BODY)
        # Claude adapter output starts with grounding, not frontmatter
        self.assertFalse(result.startswith("---"))
        self.assertTrue(result.startswith("I verify every claim"))


class TestAdapterDeterminism(unittest.TestCase):
    """Adapter functions are pure and deterministic."""

    @covers("REQ-0.0.13-04-05")
    def test_claude_deterministic(self) -> None:
        """Claude adapter produces identical output on repeated calls."""
        a = render_persona_claude(_FM, _BODY)
        b = render_persona_claude(_FM, _BODY)
        self.assertEqual(a, b)

    @covers("REQ-0.0.13-04-05")
    def test_codex_deterministic(self) -> None:
        """Codex adapter produces identical output on repeated calls."""
        a = render_persona_codex(_FM, _BODY)
        b = render_persona_codex(_FM, _BODY)
        self.assertEqual(a, b)

    @covers("REQ-0.0.13-04-05")
    def test_copilot_deterministic(self) -> None:
        """Copilot adapter produces identical output on repeated calls."""
        a = render_persona_copilot(_FM, _BODY)
        b = render_persona_copilot(_FM, _BODY)
        self.assertEqual(a, b)

    @covers("REQ-0.0.13-04-05")
    def test_fallback_deterministic(self) -> None:
        """Fallback rendering produces identical output on repeated calls."""
        a = render_persona_for_vendor("opencode", _FM, _BODY)
        b = render_persona_for_vendor("opencode", _FM, _BODY)
        self.assertEqual(a, b)


class TestVendorRegistry(unittest.TestCase):
    """VENDOR_ADAPTERS registry is complete and consistent."""

    def test_registry_has_three_vendors(self) -> None:
        """Registry contains exactly claude, codex, copilot."""
        self.assertEqual(set(VENDOR_ADAPTERS.keys()), {"claude", "codex", "copilot"})

    def test_all_adapters_callable(self) -> None:
        """Every registered adapter is callable."""
        for name, adapter in VENDOR_ADAPTERS.items():
            self.assertTrue(callable(adapter), f"{name} adapter is not callable")


if __name__ == "__main__":
    unittest.main()
