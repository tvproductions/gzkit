"""Tests for core domain models (extracted from models/frontmatter.py)."""

import unittest

from gzkit.core.models import (
    AdrFrontmatter,
    ObpiFrontmatter,
    PrdFrontmatter,
    validate_frontmatter_model,
)
from gzkit.traceability import covers


class TestCoreAdrFrontmatter(unittest.TestCase):
    """Verify AdrFrontmatter is importable from core."""

    @covers("REQ-0.0.3-02-04")
    def test_valid_adr_frontmatter(self) -> None:
        fm = AdrFrontmatter(
            id="ADR-0.1.0",
            status="Draft",
            semver="0.1.0",
            lane="heavy",
            parent="",
            date="2026-01-01",
        )
        self.assertEqual(fm.id, "ADR-0.1.0")
        self.assertEqual(fm.lane, "heavy")


class TestCoreObpiFrontmatter(unittest.TestCase):
    """Verify ObpiFrontmatter is importable from core."""

    @covers("REQ-0.0.3-02-04")
    def test_valid_obpi_frontmatter(self) -> None:
        fm = ObpiFrontmatter(
            id="OBPI-0.1.0-01",
            parent="ADR-0.1.0",
            item=1,
            lane="Heavy",
            status="Draft",
        )
        self.assertEqual(fm.parent, "ADR-0.1.0")


class TestCorePrdFrontmatter(unittest.TestCase):
    """Verify PrdFrontmatter is importable from core."""

    @covers("REQ-0.0.3-02-04")
    def test_valid_prd_frontmatter(self) -> None:
        fm = PrdFrontmatter(
            id="PRD-AI-0.1.0",
            status="Draft",
            semver="0.1.0",
            date="2026-01-01",
        )
        self.assertEqual(fm.status, "Draft")


class TestCoreValidateFrontmatterModel(unittest.TestCase):
    """Verify validate_frontmatter_model from core."""

    @covers("REQ-0.0.3-02-04")
    def test_returns_none_for_unknown_schema(self) -> None:
        result = validate_frontmatter_model({}, {"$id": "unknown"}, "test.md")
        self.assertIsNone(result)


class TestCoreReExports(unittest.TestCase):
    """Verify original module re-exports work (backward compat)."""

    @covers("REQ-0.0.3-02-05")
    def test_models_reexports_adr(self) -> None:
        from gzkit.models import AdrFrontmatter as orig

        self.assertIs(orig, AdrFrontmatter)

    @covers("REQ-0.0.3-02-05")
    def test_models_frontmatter_reexports(self) -> None:
        from gzkit.models.frontmatter import ObpiFrontmatter as orig

        self.assertIs(orig, ObpiFrontmatter)


if __name__ == "__main__":
    unittest.main()
