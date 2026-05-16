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
