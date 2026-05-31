"""Tests for content model field type constraints (OBPI-0.0.34-01).

Covers:
  REQ-0.0.34-01-03 — no field resolves to typing.Any or untyped plain dict
"""

import typing
import unittest

from pydantic import ValidationError

from gzkit.content.models import (
    CONTENT_MODELS,
    Chore,
    Handoff,
    Persona,
    Rule,
    Skill,
)
from gzkit.traceability import covers


def _annotation_is_any(annotation: object) -> bool:
    """Return True if the annotation is typing.Any or the bare Any singleton."""
    return annotation is typing.Any


def _annotation_is_untyped_dict(annotation: object) -> bool:
    """Return True if the annotation is a bare dict with no type arguments."""
    # dict without args (e.g. `dict` or `Dict` without subscript)
    if annotation is dict:
        return True
    origin = getattr(annotation, "__origin__", None)
    if origin is dict:
        args = getattr(annotation, "__args__", None)
        # dict[Any, Any] also counts as untyped
        if args and all(_annotation_is_any(a) for a in args):
            return True
    return False


class TestContentModelFieldTypes(unittest.TestCase):
    """Field annotation quality tests for all registered content models."""

    @covers("REQ-0.0.34-01-03")
    def test_no_any_typed_fields(self) -> None:
        """No field in any registered model may be annotated as typing.Any or bare dict."""
        for model_name, model_cls in CONTENT_MODELS.items():
            for field_name, field_info in model_cls.model_fields.items():
                annotation = field_info.annotation
                with self.subTest(model=model_name, field=field_name):
                    self.assertFalse(
                        _annotation_is_any(annotation),
                        f"{model_name}.{field_name} must not be typed as Any",
                    )
                    self.assertFalse(
                        _annotation_is_untyped_dict(annotation),
                        f"{model_name}.{field_name} must not be a bare/untyped dict",
                    )

    @covers("REQ-0.0.34-01-03")
    def test_json_schema_no_any(self) -> None:
        """JSON schema for each registered model must not contain unconstrained objects."""
        for model_name, model_cls in CONTENT_MODELS.items():
            schema = model_cls.model_json_schema()
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                with self.subTest(model=model_name, property=prop_name):
                    # A bare {"type": "object"} with no further constraints signals Any/untyped dict
                    is_bare_object = (
                        prop_schema.get("type") == "object"
                        and "properties" not in prop_schema
                        and "additionalProperties" not in prop_schema
                        and "anyOf" not in prop_schema
                        and "$ref" not in prop_schema
                    )
                    self.assertFalse(
                        is_bare_object,
                        f"{model_name}.{prop_name} schema is an unconstrained object"
                        " (Any/untyped dict)",
                    )


class TestSemanticStructureValidators(unittest.TestCase):
    """REQ-03 second clause: semantic-structure string fields carry validators.

    Brief enumerates "paths, identifiers, semver" as the categories required
    to carry pydantic validators that reject malformed input.
    """

    @covers("REQ-0.0.34-01-03")
    def test_rule_paths_rejects_absolute_path(self) -> None:
        with self.assertRaises(ValidationError):
            Rule(title="t", version="1.0.0", paths=["/abs/path"])

    @covers("REQ-0.0.34-01-03")
    def test_rule_paths_rejects_windows_drive_path(self) -> None:
        with self.assertRaises(ValidationError):
            Rule(title="t", version="1.0.0", paths=["C:/abs/path"])

    @covers("REQ-0.0.34-01-03")
    def test_rule_paths_rejects_parent_traversal(self) -> None:
        with self.assertRaises(ValidationError):
            Rule(title="t", version="1.0.0", paths=["../escape"])

    @covers("REQ-0.0.34-01-03")
    def test_rule_paths_rejects_empty_element(self) -> None:
        with self.assertRaises(ValidationError):
            Rule(title="t", version="1.0.0", paths=[""])

    @covers("REQ-0.0.34-01-03")
    def test_rule_version_rejects_non_semver(self) -> None:
        with self.assertRaises(ValidationError):
            Rule(title="t", version="not-semver")

    @covers("REQ-0.0.34-01-03")
    def test_skill_slug_rejects_non_kebab(self) -> None:
        with self.assertRaises(ValidationError):
            Skill(slug="Bad_Slug", title="t", purpose="p")

    @covers("REQ-0.0.34-01-03")
    def test_chore_slug_rejects_non_kebab(self) -> None:
        with self.assertRaises(ValidationError):
            Chore(slug="Bad_Slug", title="t")

    @covers("REQ-0.0.34-01-03")
    def test_persona_slug_rejects_non_kebab(self) -> None:
        with self.assertRaises(ValidationError):
            Persona(slug="Bad_Slug", role="r")

    @covers("REQ-0.0.34-01-03")
    def test_handoff_session_id_rejects_empty(self) -> None:
        with self.assertRaises(ValidationError):
            Handoff(session_id="", state_summary="s")

    @covers("REQ-0.0.34-01-03")
    def test_handoff_session_id_rejects_whitespace(self) -> None:
        with self.assertRaises(ValidationError):
            Handoff(session_id="bad space", state_summary="s")

    @covers("REQ-0.0.34-01-03")
    def test_good_values_construct_successfully(self) -> None:
        Rule(title="t", version="1.2.3", paths=["foo.md", "bar/*.txt"])
        Skill(slug="my-skill", title="t", purpose="p")
        Chore(slug="my-chore", title="t")
        Persona(slug="my-persona", role="r")
        Handoff(session_id="abc-123", state_summary="s")


class TestDensityBulletFields(unittest.TestCase):
    @covers("REQ-0.0.37-11-01")
    def test_bullet_accepts_classification_enum_values(self) -> None:
        from gzkit.content.models import Bullet

        for cls in ("Mechanical", "Promotable", "Judgment", "Ambiguous"):
            b = Bullet(text="x", classification=cls)
            self.assertEqual(b.classification, cls)

    @covers("REQ-0.0.37-11-01")
    def test_bullet_rejects_invalid_classification(self) -> None:
        from gzkit.content.models import Bullet

        with self.assertRaises(ValidationError):
            Bullet(text="x", classification="Invalid")

    @covers("REQ-0.0.37-11-01")
    def test_bullet_accepts_witness_and_rationale_ref(self) -> None:
        from gzkit.content.models import Bullet

        b = Bullet(text="x", witness="gz validate --foo", rationale_ref="docs/foo.md")
        self.assertEqual(b.witness, "gz validate --foo")
        self.assertEqual(b.rationale_ref, "docs/foo.md")

    @covers("REQ-0.0.37-11-01")
    def test_bullet_new_fields_default_to_none(self) -> None:
        from gzkit.content.models import Bullet

        b = Bullet(text="x")
        self.assertIsNone(b.classification)
        self.assertIsNone(b.witness)
        self.assertIsNone(b.rationale_ref)
        self.assertIsNone(b.density_min)

    @covers("REQ-0.0.37-11-03")
    def test_judgment_bullet_density_min_auto_set_to_lite(self) -> None:
        from gzkit.content.models import Bullet

        b = Bullet(text="x", classification="Judgment")
        self.assertEqual(b.density_min, "lite")

    @covers("REQ-0.0.37-11-03")
    def test_judgment_bullet_rejects_density_min_above_lite(self) -> None:
        from gzkit.content.models import Bullet

        with self.assertRaises(ValidationError):
            Bullet(text="x", classification="Judgment", density_min="heavy")

    @covers("REQ-0.0.37-11-01")
    def test_density_min_accepts_valid_temperatures(self) -> None:
        from gzkit.content.models import Bullet

        for temp in ("lite", "medium", "heavy"):
            b = Bullet(text="x", density_min=temp)
            self.assertEqual(b.density_min, temp)

    @covers("REQ-0.0.37-11-01")
    def test_density_min_rejects_invalid_temperature(self) -> None:
        from gzkit.content.models import Bullet

        with self.assertRaises(ValidationError):
            Bullet(text="x", density_min="ultra")


class TestPillarFields(unittest.TestCase):
    @covers("REQ-0.0.37-11-02")
    def test_pillar_constructs_with_minimal_required_fields(self) -> None:
        from gzkit.content.models.agent_contract import Pillar

        p = Pillar(id="behavior-rules", title="Behavior Rules", order=1)
        self.assertEqual(p.order, 1)
        self.assertTrue(p.enabled)  # default True
        self.assertEqual(p.tier, "lite")  # default "lite"
        self.assertEqual(p.bullets, [])  # default empty

    @covers("REQ-0.0.37-11-02")
    def test_pillar_enabled_stores_false(self) -> None:
        from gzkit.content.models.agent_contract import Pillar

        p = Pillar(id="x", title="X", order=1, enabled=False)
        self.assertFalse(p.enabled)

    @covers("REQ-0.0.37-11-02")
    def test_pillar_tier_controls_lowest_temperature(self) -> None:
        from gzkit.content.models.agent_contract import Pillar

        for tier in ("lite", "medium", "heavy"):
            p = Pillar(id="x", title="X", order=1, tier=tier)
            self.assertEqual(p.tier, tier)

    @covers("REQ-0.0.37-11-02")
    def test_pillar_tier_rejects_invalid_value(self) -> None:
        from gzkit.content.models.agent_contract import Pillar

        with self.assertRaises(ValidationError):
            Pillar(id="x", title="X", order=1, tier="ultra")

    @covers("REQ-0.0.37-11-02")
    def test_pillar_carries_bullets(self) -> None:
        from gzkit.content.models import Bullet
        from gzkit.content.models.agent_contract import Pillar

        p = Pillar(
            id="x", title="X", order=1, bullets=[Bullet(text="rule one"), Bullet(text="rule two")]
        )
        self.assertEqual(len(p.bullets), 2)

    @covers("REQ-0.0.37-11-02")
    def test_agent_contract_accepts_pillars(self) -> None:
        from gzkit.content.models import AgentContract
        from gzkit.content.models.agent_contract import Pillar

        p = Pillar(id="x", title="X", order=1)
        ac = AgentContract(name="A", purpose="P", pillars=[p])
        self.assertEqual(len(ac.pillars), 1)

    @covers("REQ-0.0.37-11-02")
    def test_agent_contract_pillars_defaults_to_empty(self) -> None:
        from gzkit.content.models import AgentContract

        ac = AgentContract(name="A", purpose="P")
        self.assertEqual(ac.pillars, [])

    @covers("REQ-0.0.37-11-02")
    def test_pillar_frozen_and_extra_forbid(self) -> None:
        """Pillar inherits frozen=True and extra='forbid' from BaseContentModel."""
        from pydantic import ValidationError

        from gzkit.content.models.agent_contract import Pillar

        self.assertTrue(Pillar.model_config.get("frozen") is True)
        self.assertEqual(Pillar.model_config.get("extra"), "forbid")
        with self.assertRaises(ValidationError):
            Pillar(id="x", title="X", order=1, _undeclared_field_xyz="boom")

    @covers("REQ-0.0.37-11-02")
    def test_pillar_no_untyped_fields(self) -> None:
        """Pillar schema must not contain unconstrained Any/untyped dict fields."""
        import typing

        from gzkit.content.models.agent_contract import Pillar

        for field_name, field_info in Pillar.model_fields.items():
            annotation = field_info.annotation
            with self.subTest(field=field_name):
                self.assertIsNot(annotation, typing.Any, f"Pillar.{field_name} must not be Any")
