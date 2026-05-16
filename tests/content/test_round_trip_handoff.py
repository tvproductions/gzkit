"""Round-trip fidelity tests for Handoff — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Bullet, Handoff
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripHandoff(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Handoff with empty resume_point."""
        model = Handoff(
            session_id="session-01",
            state_summary="Session state",
            open_items=[],
            resume_point="",
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Handoff")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Handoff with all fields populated."""
        model = Handoff(
            session_id="session-42",
            state_summary="Halfway through OBPI",
            open_items=[Bullet(text="Fix lint error", indent=0)],
            resume_point="Start from Stage 3",
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Handoff")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency_empty_resume(self) -> None:
        """render(parse(render(model))) == render(model) — empty resume_point."""
        model = Handoff(
            session_id="session-01",
            state_summary="Session state",
            open_items=[],
            resume_point="",
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Handoff")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency_with_resume(self) -> None:
        """render(parse(render(model))) == render(model) — non-empty resume_point."""
        model = Handoff(
            session_id="session-42",
            state_summary="Halfway through OBPI",
            open_items=[Bullet(text="Fix lint error", indent=0)],
            resume_point="Start from Stage 3",
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Handoff")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
