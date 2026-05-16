"""Round-trip fidelity tests for Persona — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Persona
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripPersona(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Persona."""
        model = Persona(slug="main-session", role="Primary operator", traits=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Persona")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Persona with all fields populated."""
        model = Persona(
            slug="implementer",
            role="Task implementer",
            traits=["methodical", "test-first", "atomic-edits"],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Persona")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Persona(
            slug="implementer",
            role="Task implementer",
            traits=["methodical", "test-first", "atomic-edits"],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Persona")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
