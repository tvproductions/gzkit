"""Tests for gzkit template system."""

import unittest
from pathlib import Path

from gzkit.templates import list_templates, load_template, render_template


class TestLoadTemplate(unittest.TestCase):
    """Tests for template loading."""

    def test_load_prd_template(self) -> None:
        """Can load PRD template."""
        content = load_template("prd")
        self.assertIn("{id}", content)
        self.assertIn("Problem Statement", content)

    def test_load_adr_template(self) -> None:
        """Can load ADR template."""
        content = load_template("adr")
        self.assertIn("{id}", content)
        self.assertIn("Intent", content)
        self.assertIn("Decision", content)

    def test_load_obpi_template(self) -> None:
        """Can load OBPI template."""
        content = load_template("obpi")
        self.assertIn("{id}", content)
        self.assertIn("Objective", content)
        self.assertIn("Requirements (FAIL-CLOSED)", content)
        self.assertIn("Discovery Checklist", content)

    def test_load_nonexistent_template(self) -> None:
        """Loading nonexistent template raises error."""
        with self.assertRaises(FileNotFoundError):
            load_template("nonexistent")


class TestRenderTemplate(unittest.TestCase):
    """Tests for template rendering."""

    def test_render_substitutes_values(self) -> None:
        """Render substitutes provided values."""
        content = render_template(
            "prd",
            id="PRD-TEST-1.0.0",
            title="Test PRD",
            semver="1.0.0",
        )
        self.assertIn("PRD-TEST-1.0.0", content)
        self.assertIn("Test PRD", content)

    def test_render_uses_defaults(self) -> None:
        """Render uses default values for missing keys."""
        content = render_template(
            "adr",
            id="ADR-0.1.0",
            title="Test ADR",
        )
        # date should be filled with today's date
        self.assertIn("ADR-0.1.0", content)
        # status should default to "Draft"
        self.assertIn("Draft", content)

    def test_render_preserves_unknown_placeholders(self) -> None:
        """Render preserves placeholders for unknown keys."""
        content = render_template(
            "obpi",
            id="OBPI-0.1.0-01-test",
            title="Test OBPI",
            # parent_adr not provided
        )
        # Unknown placeholders preserved
        self.assertIn("{parent_adr}", content)


class TestListTemplates(unittest.TestCase):
    """Tests for listing templates."""

    def test_lists_core_templates(self) -> None:
        """Lists all core templates."""
        templates = list_templates()
        names = {Path(template).stem for template in templates}
        self.assertIn("prd", names)
        self.assertIn("adr", names)
        self.assertIn("obpi", names)
        self.assertIn("constitution", names)
        self.assertIn("agents", names)


if __name__ == "__main__":
    unittest.main()
