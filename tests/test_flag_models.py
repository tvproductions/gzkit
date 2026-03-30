"""Tests for feature flag models (OBPI-0.0.8-01)."""

import unittest
from datetime import date

from pydantic import ValidationError

from gzkit.flags.models import (
    FlagCategory,
    FlagError,
    FlagEvaluation,
    FlagSpec,
    InvalidFlagValueError,
    UnknownFlagError,
)
from gzkit.traceability import covers


def _base_spec(**overrides: object) -> dict[str, object]:
    """Return minimal valid FlagSpec kwargs, merged with overrides."""
    base: dict[str, object] = {
        "key": "ops.test_flag",
        "category": "ops",
        "default": True,
        "description": "A test flag",
        "owner": "test-team",
        "introduced_on": "2026-03-29",
        "review_by": "2026-06-29",
    }
    base.update(overrides)
    return base


class TestFlagCategory(unittest.TestCase):
    """FlagCategory enum membership tests."""

    def test_members(self) -> None:
        self.assertEqual(set(FlagCategory), {"release", "ops", "migration", "development"})

    def test_str_enum_values(self) -> None:
        self.assertEqual(FlagCategory.release, "release")
        self.assertEqual(FlagCategory.ops, "ops")
        self.assertEqual(FlagCategory.migration, "migration")
        self.assertEqual(FlagCategory.development, "development")

    def test_invalid_category_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            FlagSpec.model_validate(_base_spec(category="experiment"))


class TestFlagSpecCreation(unittest.TestCase):
    """FlagSpec construction and field validation."""

    @covers("REQ-0.0.8-01-01")
    def test_valid_ops_flag(self) -> None:
        spec = FlagSpec.model_validate(_base_spec())
        self.assertEqual(spec.key, "ops.test_flag")
        self.assertEqual(spec.category, FlagCategory.ops)
        self.assertTrue(spec.default)
        self.assertEqual(spec.review_by, date(2026, 6, 29))

    def test_frozen_model(self) -> None:
        spec = FlagSpec.model_validate(_base_spec())
        with self.assertRaises(ValidationError):
            spec.key = "changed"  # type: ignore[misc]

    def test_extra_fields_forbidden(self) -> None:
        with self.assertRaises(ValidationError):
            FlagSpec.model_validate(_base_spec(unexpected_field="bad"))

    def test_all_adr_fields_present(self) -> None:
        """All ADR Section 6.5 fields are accepted."""
        spec = FlagSpec.model_validate(
            _base_spec(
                key="migration.full_spec",
                category="migration",
                remove_by="2026-05-01",
                review_by=None,
                linked_adr="ADR-0.0.8",
                linked_issue="GHI-49",
            )
        )
        self.assertEqual(spec.linked_adr, "ADR-0.0.8")
        self.assertEqual(spec.linked_issue, "GHI-49")
        self.assertEqual(spec.remove_by, date(2026, 5, 1))

    def test_optional_fields_default_to_none(self) -> None:
        spec = FlagSpec.model_validate(_base_spec())
        self.assertIsNone(spec.remove_by)
        self.assertIsNone(spec.linked_adr)
        self.assertIsNone(spec.linked_issue)


class TestCategoryValidationRules(unittest.TestCase):
    """Category-specific validation per ADR-0.0.8 Section 6.5."""

    @covers("REQ-0.0.8-01-02")
    def test_release_without_remove_by_rejected(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            FlagSpec.model_validate(
                _base_spec(key="release.new_feature", category="release", remove_by=None)
            )
        self.assertIn("remove_by", str(ctx.exception))

    def test_release_with_remove_by_accepted(self) -> None:
        spec = FlagSpec.model_validate(
            _base_spec(
                key="release.new_feature",
                category="release",
                remove_by="2026-05-01",
                review_by=None,
            )
        )
        self.assertEqual(spec.category, FlagCategory.release)

    def test_migration_without_remove_by_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            FlagSpec.model_validate(
                _base_spec(key="migration.old_path", category="migration", remove_by=None)
            )

    def test_migration_with_remove_by_accepted(self) -> None:
        spec = FlagSpec.model_validate(
            _base_spec(
                key="migration.old_path",
                category="migration",
                remove_by="2026-05-01",
                review_by=None,
            )
        )
        self.assertEqual(spec.category, FlagCategory.migration)

    def test_ops_without_review_by_rejected(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            FlagSpec.model_validate(_base_spec(review_by=None))
        self.assertIn("review_by", str(ctx.exception))

    def test_ops_with_review_by_accepted(self) -> None:
        spec = FlagSpec.model_validate(_base_spec())
        self.assertEqual(spec.category, FlagCategory.ops)

    @covers("REQ-0.0.8-01-03")
    def test_development_with_default_true_rejected(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            FlagSpec.model_validate(
                _base_spec(
                    key="development.wip",
                    category="development",
                    default=True,
                    remove_by="2026-05-01",
                    review_by=None,
                )
            )
        self.assertIn("false", str(ctx.exception).lower())

    def test_development_without_remove_by_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            FlagSpec.model_validate(
                _base_spec(
                    key="development.wip",
                    category="development",
                    default=False,
                    remove_by=None,
                    review_by=None,
                )
            )

    def test_development_valid(self) -> None:
        spec = FlagSpec.model_validate(
            _base_spec(
                key="development.wip",
                category="development",
                default=False,
                remove_by="2026-05-01",
                review_by=None,
            )
        )
        self.assertFalse(spec.default)


class TestFlagEvaluation(unittest.TestCase):
    """FlagEvaluation roundtrip tests."""

    def test_create_evaluation(self) -> None:
        ev = FlagEvaluation(key="ops.test", value=True, source="registry_default")
        self.assertEqual(ev.key, "ops.test")
        self.assertTrue(ev.value)
        self.assertEqual(ev.source, "registry_default")

    def test_frozen(self) -> None:
        ev = FlagEvaluation(key="ops.test", value=False, source="env")
        with self.assertRaises(ValidationError):
            ev.value = True  # type: ignore[misc]

    def test_extra_forbidden(self) -> None:
        with self.assertRaises(ValidationError):
            FlagEvaluation(key="ops.test", value=True, source="env", extra="bad")  # type: ignore[call-arg]

    def test_roundtrip_json(self) -> None:
        ev = FlagEvaluation(key="ops.test", value=True, source="config")
        dumped = ev.model_dump()
        restored = FlagEvaluation.model_validate(dumped)
        self.assertEqual(ev, restored)


class TestErrorHierarchy(unittest.TestCase):
    """Error type hierarchy tests."""

    def test_flag_error_is_gzkit_error(self) -> None:
        from gzkit.core.exceptions import GzkitError

        self.assertTrue(issubclass(FlagError, GzkitError))

    def test_unknown_flag_error_is_flag_error(self) -> None:
        self.assertTrue(issubclass(UnknownFlagError, FlagError))

    def test_invalid_value_error_is_flag_error(self) -> None:
        self.assertTrue(issubclass(InvalidFlagValueError, FlagError))

    def test_flag_error_exit_code(self) -> None:
        self.assertEqual(FlagError("test").exit_code, 1)

    def test_unknown_flag_error_message(self) -> None:
        err = UnknownFlagError("ops.nonexistent")
        self.assertEqual(str(err), "ops.nonexistent")

    def test_invalid_value_error_message(self) -> None:
        err = InvalidFlagValueError("bad value")
        self.assertEqual(str(err), "bad value")


if __name__ == "__main__":
    unittest.main()
