"""Round-trip fidelity tests for Skill — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Bullet, Skill
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripSkill(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Skill."""
        model = Skill(slug="test-skill", title="Test Skill", purpose="A purpose", steps=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Skill")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Skill with all fields populated."""
        model = Skill(
            slug="gz-check",
            title="GZ Check",
            purpose="Run all quality checks",
            steps=[
                Bullet(text="Run lint", indent=0),
                Bullet(text="Run tests", indent=0),
            ],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Skill")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Skill(
            slug="gz-check",
            title="GZ Check",
            purpose="Run all quality checks",
            steps=[Bullet(text="Run lint", indent=0)],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Skill")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
