"""Round-trip fidelity tests for Scenario — OBPI-0.0.34-03."""

from __future__ import annotations

import unittest

from gzkit.content.models import Scenario
from gzkit.content.parse import parse
from gzkit.content.render import render
from gzkit.traceability import covers


class TestRoundTripScenario(unittest.TestCase):
    """Round-trip fidelity: parse(render(model)) == model and render is idempotent."""

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_minimal(self) -> None:
        """parse(render(model)) == model for minimal Scenario."""
        model = Scenario(feature="Feature", scenario="Scenario", given=[], when=[], then=[])
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Scenario")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_model_identity_with_data(self) -> None:
        """parse(render(model)) == model for Scenario with all fields populated."""
        model = Scenario(
            feature="Content Import",
            scenario="Import a rule file",
            given=["a valid rule file exists"],
            when=["gz content import is run"],
            then=["exit code is 0", "JSON is emitted to stdout"],
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "Scenario")
        self.assertEqual(parsed, model)

    @covers("REQ-0.0.34-03-02")
    def test_render_idempotency(self) -> None:
        """render(parse(render(model))) == render(model) — byte-stable."""
        model = Scenario(
            feature="Content Import",
            scenario="Import a rule file",
            given=["a valid rule file exists"],
            when=["gz content import is run"],
            then=["exit code is 0", "JSON is emitted to stdout"],
        )
        once = render(model, "claude")
        parsed = parse(once.decode("utf-8"), "Scenario")
        twice = render(parsed, "claude")
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
