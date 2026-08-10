"""Pydantic model tests for SecuritySurfaceEntry (ADR-0.0.22, OBPI-0.0.22-02).

Covers REQ-0.0.22-02-03 (malformed entries are rejected with typed errors) and
REQ-0.0.22-02-04 (model declares frozen=True + extra='forbid' per
.claude/rules/models.md).

@covers REQ-0.0.22-02-03
@covers REQ-0.0.22-02-04
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.models.security_surfaces import (
    CANONICAL_CATEGORIES,
    SecuritySurfaceEntry,
)
from gzkit.traceability import covers  # noqa: F401


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "category": "credential_handling",
        "globs": ("src/gzkit/**/credentials.py",),
        "rationale": "Credential helpers handle secrets; review for leakage and storage.",
    }
    base.update(overrides)
    return base


class TestSecuritySurfaceEntryConfig(unittest.TestCase):
    """REQ-0.0.22-02-04: model_config declares frozen + extra='forbid'."""

    def test_model_config_frozen(self) -> None:
        self.assertTrue(SecuritySurfaceEntry.model_config.get("frozen"))

    def test_model_config_extra_forbid(self) -> None:
        self.assertEqual(SecuritySurfaceEntry.model_config.get("extra"), "forbid")

    def test_assignment_after_construction_raises(self) -> None:
        entry = SecuritySurfaceEntry(**_valid_kwargs())
        with self.assertRaises(ValidationError):
            entry.rationale = "altered"  # ty: ignore[invalid-assignment]


class TestSecuritySurfaceEntryRejection(unittest.TestCase):
    """REQ-0.0.22-02-03: malformed entries fail Pydantic construction."""

    def test_unknown_category_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**_valid_kwargs(category="cosmic_radiation"))

    def test_extra_key_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**_valid_kwargs(severity="critical"))

    def test_empty_globs_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**_valid_kwargs(globs=()))

    def test_empty_glob_string_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**_valid_kwargs(globs=("",)))

    def test_empty_rationale_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**_valid_kwargs(rationale=""))

    def test_missing_category_rejected(self) -> None:
        kwargs = _valid_kwargs()
        del kwargs["category"]
        with self.assertRaises(ValidationError):
            SecuritySurfaceEntry(**kwargs)


class TestCanonicalCategories(unittest.TestCase):
    """REQ-0.0.22-02-02: canonical category set is the nine names from the parent ADR."""

    def test_canonical_categories_are_the_nine_named(self) -> None:
        expected = (
            "credential_handling",
            "subprocess_user_input",
            "crypto_primitives",
            "auth_boundaries",
            "external_api_surfaces",
            "ledger_integrity",
            "arb_receipt_chain",
            "secret_handling",
            "deserialization_user_input",
        )
        self.assertEqual(set(CANONICAL_CATEGORIES), set(expected))
        self.assertEqual(len(CANONICAL_CATEGORIES), 9)

    def test_each_canonical_category_constructs(self) -> None:
        for category in CANONICAL_CATEGORIES:
            entry = SecuritySurfaceEntry(
                category=category,
                globs=("src/example.py",),
                rationale="test rationale",
            )
            self.assertEqual(entry.category, category)


if __name__ == "__main__":
    unittest.main()
