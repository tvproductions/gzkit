"""Pydantic frontmatter tests for the `sensitivity` field (ADR-0.0.22, OBPI-0.0.22-01).

Covers REQ-0.0.22-01-04: Pydantic ADR/OBPI frontmatter models expose `sensitivity`
as a typed optional Literal["security"] | None field; the value is preserved on
the immutable model when supplied; absent input produces None; unknown values
are rejected.

@covers REQ-0.0.22-01-04
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.models.frontmatter import AdrFrontmatter, ObpiFrontmatter
from gzkit.traceability import covers  # noqa: F401


def _adr_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "ADR-0.0.99-test-only",
        "status": "Draft",
        "semver": "0.0.99",
        "lane": "lite",
        "kind": "foundation",
        "parent": "PRD-GZKIT-1.0.0",
        "date": "2026-04-29",
    }
    base.update(overrides)
    return base


def _obpi_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "OBPI-0.0.99-01-test-only",
        "parent": "ADR-0.0.99-test-only",
        "item": 1,
        "lane": "lite",
        "status": "Draft",
    }
    base.update(overrides)
    return base


class TestAdrFrontmatterSensitivity(unittest.TestCase):
    def test_accepts_sensitivity_security(self) -> None:
        model = AdrFrontmatter(**_adr_kwargs(sensitivity="security"))
        self.assertEqual(model.sensitivity, "security")

    def test_defaults_to_none_when_absent(self) -> None:
        model = AdrFrontmatter(**_adr_kwargs())
        self.assertIsNone(model.sensitivity)

    def test_rejects_unknown_value(self) -> None:
        with self.assertRaises(ValidationError):
            AdrFrontmatter(**_adr_kwargs(sensitivity="confidential"))

    def test_field_is_immutable(self) -> None:
        model = AdrFrontmatter(**_adr_kwargs(sensitivity="security"))
        with self.assertRaises(ValidationError):
            model.sensitivity = None  # type: ignore[misc]


class TestObpiFrontmatterSensitivity(unittest.TestCase):
    def test_accepts_sensitivity_security(self) -> None:
        model = ObpiFrontmatter(**_obpi_kwargs(sensitivity="security"))
        self.assertEqual(model.sensitivity, "security")

    def test_defaults_to_none_when_absent(self) -> None:
        model = ObpiFrontmatter(**_obpi_kwargs())
        self.assertIsNone(model.sensitivity)

    def test_rejects_unknown_value(self) -> None:
        with self.assertRaises(ValidationError):
            ObpiFrontmatter(**_obpi_kwargs(sensitivity="confidential"))

    def test_field_is_immutable(self) -> None:
        model = ObpiFrontmatter(**_obpi_kwargs(sensitivity="security"))
        with self.assertRaises(ValidationError):
            model.sensitivity = None  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
