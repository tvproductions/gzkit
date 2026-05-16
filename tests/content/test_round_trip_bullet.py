"""Round-trip fidelity tests for Bullet — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Bullet
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripBullet(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Bullet (indent=0)."""
        model = Bullet(text="An item", indent=0)
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Bullet")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Bullet with deep indent."""
        model = Bullet(text="Indented item", indent=2)
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Bullet")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_indent_one(self) -> None:
        """parse(render(model)) == model for Bullet with indent=1 (2 leading spaces)."""
        model = Bullet(text="Indent one item", indent=1)
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Bullet")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Bullet(text="Indented item", indent=2)
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Bullet")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
