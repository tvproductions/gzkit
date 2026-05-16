"""Byte-stability tests for the Jinja2 render pipeline (OBPI-0.0.34-02).

These tests are in EXPECTED RED state until Task 2 delivers the Jinja2
templates under src/gzkit/content/templates/<content-type>/<vendor>.md.j2.
They will transition to GREEN automatically when those templates land.

Covers:
  REQ-0.0.34-02-01 — render(model, vendor) invoked twice produces byte-equal output
  REQ-0.0.34-02-02 — each (content_type, vendor) pair has a template that renders non-empty
"""

import unittest

from gzkit.content.models import (
    CONTENT_MODELS,
    AgentContract,
    Bullet,
    Chore,
    Handoff,
    Persona,
    Rule,
    Scenario,
    Skill,
)
from gzkit.content.render import render
from gzkit.content.render.pipeline import _VENDOR_ROUTING
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Minimal stub instances — one per content type with the minimal required fields.
# These are used by both byte-stability tests and the routing-coverage test.
# ---------------------------------------------------------------------------

_STUB_RULE = Rule(title="Stability Test Rule", version="1.0.0", paths=[], body=[])
_STUB_SKILL = Skill(slug="test-skill", title="Test Skill", purpose="Stability testing")
_STUB_AGENT_CONTRACT = AgentContract(name="test-agent", purpose="Stability testing")
_STUB_CHORE = Chore(slug="test-chore", title="Test Chore")
_STUB_PERSONA = Persona(slug="test-persona", role="Stability tester")
_STUB_HANDOFF = Handoff(session_id="session-01", state_summary="Test handoff state")
_STUB_SCENARIO = Scenario(feature="Stability", scenario="Render is byte-stable")
_STUB_BULLET = Bullet(text="Stability bullet item")

# Map content type name → stub instance for parametric tests.
_STUB_BY_TYPE: dict[str, object] = {
    "AgentContract": _STUB_AGENT_CONTRACT,
    "Rule": _STUB_RULE,
    "Skill": _STUB_SKILL,
    "Chore": _STUB_CHORE,
    "Persona": _STUB_PERSONA,
    "Handoff": _STUB_HANDOFF,
    "Scenario": _STUB_SCENARIO,
    "Bullet": _STUB_BULLET,
}


class TestByteStability(unittest.TestCase):
    """Byte-stability tests — RED until templates land (Task 2)."""

    @covers("REQ-0.0.34-02-01")
    def test_render_twice_byte_equal_rule(self) -> None:
        """render(Rule, 'claude') invoked twice MUST produce identical bytes."""
        first = render(_STUB_RULE, "claude")
        second = render(_STUB_RULE, "claude")
        self.assertEqual(first, second)
        self.assertIsInstance(first, bytes)

    @covers("REQ-0.0.34-02-01")
    def test_render_twice_byte_equal_skill(self) -> None:
        """render(Skill, 'claude') invoked twice MUST produce identical bytes."""
        first = render(_STUB_SKILL, "claude")
        second = render(_STUB_SKILL, "claude")
        self.assertEqual(first, second)
        self.assertIsInstance(first, bytes)

    @covers("REQ-0.0.34-02-01")
    def test_render_twice_byte_equal_all_types(self) -> None:
        """render() twice on any registered content type MUST produce identical bytes."""
        for content_type_name, stub in _STUB_BY_TYPE.items():
            with self.subTest(content_type=content_type_name):
                from gzkit.content.models.base import BaseContentModel

                assert isinstance(stub, BaseContentModel)
                first = render(stub, "claude")
                second = render(stub, "claude")
                self.assertEqual(
                    first,
                    second,
                    f"render() not byte-stable for content_type={content_type_name!r}",
                )

    @covers("REQ-0.0.34-02-02")
    def test_all_registered_pairs_render_nonempty(self) -> None:
        """Every (content_type, vendor) pair in the routing table renders non-empty output."""
        for content_type_name, vendor in sorted(_VENDOR_ROUTING):
            with self.subTest(content_type=content_type_name, vendor=vendor):
                stub = _STUB_BY_TYPE.get(content_type_name)
                self.assertIsNotNone(
                    stub,
                    f"No stub instance for content_type={content_type_name!r} — "
                    f"update _STUB_BY_TYPE in this test file.",
                )
                from gzkit.content.models.base import BaseContentModel

                assert isinstance(stub, BaseContentModel)
                result = render(stub, vendor)
                self.assertIsInstance(result, bytes)
                self.assertGreater(
                    len(result),
                    0,
                    f"render() returned empty bytes for ({content_type_name!r}, {vendor!r})",
                )

    @covers("REQ-0.0.34-02-02")
    def test_routing_table_covers_all_canonical_models(self) -> None:
        """The routing table must include an entry for every canonical content type."""
        routed_types = {ct for ct, _ in _VENDOR_ROUTING}
        canonical_types = set(CONTENT_MODELS.keys())
        missing = canonical_types - routed_types
        self.assertEqual(
            missing,
            set(),
            f"Canonical types not in routing table: {missing}",
        )

    @covers("REQ-0.0.34-02-04")
    def test_render_pipeline_does_not_regress_content_model_imports(self) -> None:
        """Render pipeline must not break existing content-model registry."""
        from gzkit.content.models import CONTENT_MODELS as registry  # noqa: PLC0415

        self.assertGreaterEqual(
            len(registry), 8, "CONTENT_MODELS registry must have ≥8 entries post-OBPI"
        )
        for name in (
            "AgentContract",
            "Rule",
            "Skill",
            "Chore",
            "Persona",
            "Handoff",
            "Scenario",
            "Bullet",
        ):
            self.assertIn(
                name,
                registry,
                f"{name} must still be in CONTENT_MODELS after render pipeline lands",
            )
        for content_type_name, vendor in sorted(_VENDOR_ROUTING):
            stub = _STUB_BY_TYPE.get(content_type_name)
            self.assertIsNotNone(stub, f"No stub for {content_type_name!r}")
            from gzkit.content.models.base import BaseContentModel  # noqa: PLC0415

            assert isinstance(stub, BaseContentModel)
            result = render(stub, vendor)
            self.assertIsInstance(result, bytes)
            self.assertGreater(len(result), 0)
