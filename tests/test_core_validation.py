"""Tests for core validation rules (extracted from validate.py)."""

import unittest

from gzkit.core.validation_rules import (
    ValidationError,
    ValidationResult,
    extract_headers,
    parse_frontmatter,
)


class TestCoreParseFrontmatter(unittest.TestCase):
    """Verify parse_frontmatter is importable and works from core."""

    def test_parses_yaml_frontmatter(self) -> None:
        content = "---\nid: ADR-0.1.0\nstatus: Draft\n---\n# Title\nBody\n"
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["id"], "ADR-0.1.0")
        self.assertEqual(fm["status"], "Draft")
        self.assertIn("# Title", body)

    def test_no_frontmatter(self) -> None:
        content = "# Just a title\nBody text\n"
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm, {})
        self.assertEqual(body, content)


class TestCoreExtractHeaders(unittest.TestCase):
    """Verify extract_headers works from core."""

    def test_extracts_h2_headers(self) -> None:
        content = "## Intent\nfoo\n## Decision\nbar\n"
        headers = extract_headers(content)
        self.assertEqual(headers, ["Intent", "Decision"])


class TestCoreValidationModels(unittest.TestCase):
    """Verify validation models from core."""

    def test_validation_error_model(self) -> None:
        err = ValidationError(
            type="frontmatter",
            artifact="test.md",
            message="Missing field",
            field="id",
        )
        self.assertEqual(err.type, "frontmatter")
        self.assertEqual(err.field, "id")

    def test_validation_result_model(self) -> None:
        result = ValidationResult(valid=True, errors=[])
        self.assertTrue(result.valid)


class TestCoreReExports(unittest.TestCase):
    """Verify original module re-exports work (backward compat)."""

    def test_validate_reexports_parse_frontmatter(self) -> None:
        from gzkit.validate import parse_frontmatter as orig

        self.assertIs(orig, parse_frontmatter)

    def test_validate_reexports_validation_error(self) -> None:
        from gzkit.validate import ValidationError as orig

        self.assertIs(orig, ValidationError)


if __name__ == "__main__":
    unittest.main()
