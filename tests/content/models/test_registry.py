"""Tests for the content model registry (OBPI-0.0.34-01).

Covers:
  REQ-0.0.34-01-01 — all eight canonical models declare frozen=True, extra="forbid"
  REQ-0.0.34-01-02 — undeclared fields raise pydantic.ValidationError
  REQ-0.0.34-01-04 — registry enumerates all eight types, each importable from gzkit.content.models
"""

import unittest

from pydantic import ValidationError

from gzkit.content.models import CONTENT_MODELS
from gzkit.traceability import covers

_CANONICAL_EIGHT = {
    "AgentContract",
    "Rule",
    "Skill",
    "Chore",
    "Persona",
    "Handoff",
    "Scenario",
    "Bullet",
}


class TestContentModelsRegistry(unittest.TestCase):
    """Registry completeness and model-config constraint tests."""

    @covers("REQ-0.0.34-01-04")
    def test_canonical_eight_present(self) -> None:
        """All eight canonical content types must be present in CONTENT_MODELS."""
        self.assertEqual(set(CONTENT_MODELS.keys()), _CANONICAL_EIGHT)

    @covers("REQ-0.0.34-01-01")
    def test_all_models_frozen(self) -> None:
        """Every registered model must declare frozen=True in model_config."""
        for name, model_cls in CONTENT_MODELS.items():
            with self.subTest(model=name):
                self.assertTrue(
                    model_cls.model_config.get("frozen") is True,
                    f"{name}.model_config['frozen'] must be True",
                )

    @covers("REQ-0.0.34-01-01")
    def test_all_models_extra_forbid(self) -> None:
        """Every registered model must declare extra='forbid' in model_config."""
        for name, model_cls in CONTENT_MODELS.items():
            with self.subTest(model=name):
                self.assertEqual(
                    model_cls.model_config.get("extra"),
                    "forbid",
                    f"{name}.model_config['extra'] must be 'forbid'",
                )

    @covers("REQ-0.0.34-01-02")
    def test_extra_field_raises_validation_error(self) -> None:
        """Constructing any registered model with an undeclared field must raise ValidationError."""
        for name, model_cls in CONTENT_MODELS.items():
            with (
                self.subTest(model=name),
                self.assertRaises(
                    ValidationError,
                    msg=f"{name}: expected ValidationError for undeclared field",
                ),
            ):
                model_cls(**{"_undeclared_sentinel_field_xyz": "boom"})
