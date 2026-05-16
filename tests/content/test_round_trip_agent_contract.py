"""Round-trip fidelity tests for AgentContract — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import AgentContract, Bullet
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripAgentContract(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal AgentContract."""
        model = AgentContract(name="Test", purpose="A purpose", tech_stack=[], rules=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "AgentContract")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for AgentContract with all fields populated."""
        model = AgentContract(
            name="My Agent",
            purpose="Does useful things",
            tech_stack=["Python 3.13+", "uv"],
            rules=[
                Bullet(text="Rule one", indent=0),
                Bullet(text="Sub rule", indent=1),
            ],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "AgentContract")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = AgentContract(
            name="My Agent",
            purpose="Does useful things",
            tech_stack=["Python 3.13+", "uv"],
            rules=[Bullet(text="Rule one", indent=0)],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "AgentContract")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
