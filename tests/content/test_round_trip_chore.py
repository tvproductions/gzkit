"""Round-trip fidelity tests for Chore — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Bullet, Chore
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripChore(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Chore."""
        model = Chore(slug="test-chore", title="Test Chore", steps=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Chore")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Chore with all fields populated."""
        model = Chore(
            slug="dep-audit",
            title="Dependency Audit",
            cadence="monthly",
            steps=[Bullet(text="Run uv pip check", indent=0)],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Chore")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Chore(
            slug="dep-audit",
            title="Dependency Audit",
            cadence="monthly",
            steps=[Bullet(text="Run uv pip check", indent=0)],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Chore")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
