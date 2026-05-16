"""Round-trip fidelity tests for Rule — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Bullet, Rule
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripRule(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Rule."""
        model = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Rule")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Rule with all fields populated."""
        model = Rule(
            title="Cross-Platform Policy",
            version="0.3.0",
            paths=["src/**/*.py", "tests/**/*.py"],
            body=[
                Bullet(text="Use pathlib.Path", indent=0),
                Bullet(text="Specify encoding=utf-8", indent=0),
            ],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Rule")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Rule(
            title="Cross-Platform Policy",
            version="0.3.0",
            paths=["src/**/*.py", "tests/**/*.py"],
            body=[Bullet(text="Use pathlib.Path", indent=0)],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Rule")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
