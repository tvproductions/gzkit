"""Tests for the content type registry.

@covers ADR-0.16.0  OBPI-0.16.0-01 content-type-registry
"""

import unittest

from pydantic import ValidationError

from gzkit.models.frontmatter import AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter
from gzkit.registry import REGISTRY, ContentType, ContentTypeRegistry


class TestContentTypeModel(unittest.TestCase):
    """ContentType Pydantic model constraints."""

    def test_valid_content_type(self) -> None:
        ct = ContentType(
            name="Test",
            schema_name="test",
            lifecycle_states=["Draft", "Active"],
            canonical_path_pattern="test/**/*.md",
        )
        self.assertEqual(ct.name, "Test")
        self.assertEqual(ct.schema_name, "test")
        self.assertEqual(ct.lifecycle_states, ["Draft", "Active"])

    def test_frozen(self) -> None:
        ct = ContentType(
            name="Test",
            canonical_path_pattern="test/**/*.md",
        )
        with self.assertRaises(ValidationError):
            ct.name = "Changed"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            ContentType(
                name="Test",
                canonical_path_pattern="test/**/*.md",
                bogus_field="x",  # type: ignore[call-arg]
            )

    def test_optional_fields_default_none(self) -> None:
        ct = ContentType(
            name="Test",
            canonical_path_pattern="test/**/*.md",
        )
        self.assertIsNone(ct.schema_name)
        self.assertIsNone(ct.frontmatter_model)
        self.assertEqual(ct.lifecycle_states, [])
        self.assertEqual(ct.vendor_rendering_rules, {})


class TestContentTypeRegistry(unittest.TestCase):
    """ContentTypeRegistry register/get/list_all behavior."""

    def setUp(self) -> None:
        self.reg = ContentTypeRegistry()

    def test_register_and_get(self) -> None:
        ct = ContentType(name="Foo", canonical_path_pattern="foo/*.md")
        self.reg.register(ct)
        self.assertIs(self.reg.get("Foo"), ct)

    def test_get_unknown_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.reg.get("NoSuchType")

    def test_duplicate_register_raises_value_error(self) -> None:
        ct = ContentType(name="Dup", canonical_path_pattern="dup/*.md")
        self.reg.register(ct)
        with self.assertRaises(ValueError):
            self.reg.register(ct)

    def test_list_all_preserves_order(self) -> None:
        names = ["Alpha", "Beta", "Gamma"]
        for name in names:
            self.reg.register(ContentType(name=name, canonical_path_pattern=f"{name}/*.md"))
        self.assertEqual([ct.name for ct in self.reg.list_all()], names)

    def test_list_all_empty(self) -> None:
        self.assertEqual(self.reg.list_all(), [])


class TestValidateArtifact(unittest.TestCase):
    """ContentTypeRegistry.validate_artifact() behavior."""

    def setUp(self) -> None:
        self.reg = ContentTypeRegistry()
        self.reg.register(
            ContentType(
                name="ADR",
                schema_name="adr",
                frontmatter_model=AdrFrontmatter,
                lifecycle_states=["Draft"],
                canonical_path_pattern="docs/**/*.md",
            )
        )
        self.reg.register(
            ContentType(
                name="NoModel",
                canonical_path_pattern="no/*.md",
            )
        )

    def test_valid_frontmatter_returns_empty(self) -> None:
        fm = {
            "id": "ADR-0.1.0",
            "status": "Draft",
            "semver": "0.1.0",
            "lane": "lite",
            "parent": "root",
            "date": "2026-01-01",
        }
        errors = self.reg.validate_artifact("ADR", fm, "test.md")
        self.assertEqual(errors, [])

    def test_invalid_frontmatter_returns_errors(self) -> None:
        fm = {"id": "bad-id"}
        errors = self.reg.validate_artifact("ADR", fm, "test.md")
        self.assertGreater(len(errors), 0)
        self.assertTrue(all(e["type"] == "frontmatter" for e in errors))
        self.assertTrue(all(e["artifact"] == "test.md" for e in errors))

    def test_unknown_type_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.reg.validate_artifact("Ghost", {}, "x.md")

    def test_no_model_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.reg.validate_artifact("NoModel", {}, "x.md")


class TestGlobalRegistry(unittest.TestCase):
    """The singleton REGISTRY is populated at import time."""

    def test_all_eight_types_registered(self) -> None:
        names = {ct.name for ct in REGISTRY.list_all()}
        expected = {
            "ADR",
            "OBPI",
            "PRD",
            "Constitution",
            "Rule",
            "Skill",
            "Attestation",
            "LedgerEvent",
        }
        self.assertEqual(names, expected)

    def test_adr_has_correct_model(self) -> None:
        self.assertIs(REGISTRY.get("ADR").frontmatter_model, AdrFrontmatter)

    def test_obpi_has_correct_model(self) -> None:
        self.assertIs(REGISTRY.get("OBPI").frontmatter_model, ObpiFrontmatter)

    def test_prd_has_correct_model(self) -> None:
        self.assertIs(REGISTRY.get("PRD").frontmatter_model, PrdFrontmatter)

    def test_unschematized_types_have_no_model(self) -> None:
        for name in ("Constitution", "Skill", "Attestation"):
            with self.subTest(name=name):
                self.assertIsNone(REGISTRY.get(name).frontmatter_model)

    def test_rule_has_frontmatter_model(self) -> None:
        from gzkit.rules import RuleFrontmatter

        self.assertIs(REGISTRY.get("Rule").frontmatter_model, RuleFrontmatter)

    def test_ledger_event_has_schema_but_no_frontmatter_model(self) -> None:
        le = REGISTRY.get("LedgerEvent")
        self.assertEqual(le.schema_name, "ledger")
        self.assertIsNone(le.frontmatter_model)

    def test_each_type_has_canonical_path_pattern(self) -> None:
        for ct in REGISTRY.list_all():
            with self.subTest(name=ct.name):
                self.assertTrue(len(ct.canonical_path_pattern) > 0)

    def test_each_type_has_lifecycle_states(self) -> None:
        for ct in REGISTRY.list_all():
            with self.subTest(name=ct.name):
                self.assertGreater(len(ct.lifecycle_states), 0)

    def test_validate_artifact_adr_valid(self) -> None:
        fm = {
            "id": "ADR-0.1.0",
            "status": "Draft",
            "semver": "0.1.0",
            "lane": "lite",
            "parent": "root",
            "date": "2026-01-01",
        }
        errors = REGISTRY.validate_artifact("ADR", fm, "test.md")
        self.assertEqual(errors, [])

    def test_validate_artifact_obpi_valid(self) -> None:
        fm = {
            "id": "OBPI-0.1.0-01-demo",
            "parent": "ADR-0.1.0",
            "item": 1,
            "lane": "Lite",
            "status": "Draft",
        }
        errors = REGISTRY.validate_artifact("OBPI", fm, "test.md")
        self.assertEqual(errors, [])

    def test_validate_artifact_prd_valid(self) -> None:
        fm = {
            "id": "PRD-GZKIT-0.1.0",
            "status": "Draft",
            "semver": "0.1.0",
            "date": "2026-01-01",
        }
        errors = REGISTRY.validate_artifact("PRD", fm, "test.md")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
