"""Validate the OBPI brief template enforces Closing Argument structure."""

import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "skills"
    / "gz-obpi-specify"
    / "assets"
    / "OBPI_BRIEF-template.md"
)

# Planning-phase placeholder patterns that should NOT appear in a completed
# Closing Argument section (used by test_no_planning_phase_placeholders).
PLANNING_PLACEHOLDERS = [
    "TBD",
    "TODO",
    "FIXME",
    "fill in later",
    "to be determined",
]


class TestOBPIBriefTemplate(unittest.TestCase):
    """Ensure the OBPI brief template includes Closing Argument guidance."""

    @classmethod
    def setUpClass(cls):
        cls.template_text = TEMPLATE_PATH.read_text(encoding="utf-8")

    @covers("REQ-0.23.0-01-01")
    def test_closing_argument_section_exists(self):
        """Template must contain at least one '### Closing Argument' heading."""
        matches = re.findall(r"^### Closing Argument", self.template_text, re.MULTILINE)
        self.assertGreaterEqual(
            len(matches), 1, "Template must have a '### Closing Argument' section"
        )

    @covers("REQ-0.23.0-01-01")
    def test_no_value_narrative_heading(self):
        """Template must not contain a standalone '### Value Narrative' heading."""
        matches = re.findall(r"^### Value Narrative\b", self.template_text, re.MULTILINE)
        self.assertEqual(
            len(matches),
            0,
            "Template must not have '### Value Narrative' — use '### Closing Argument' instead",
        )

    @covers("REQ-0.23.0-01-02")
    def test_authored_at_completion_guidance(self):
        """Template must include guidance that the section is authored at COMPLETION."""
        self.assertIn(
            "authored at COMPLETION",
            self.template_text,
            "Template must include 'authored at COMPLETION' guidance text",
        )

    @covers("REQ-0.23.0-01-03")
    @covers("REQ-0.23.0-01-04")
    @covers("REQ-0.23.0-01-05")
    def test_three_required_elements(self):
        """Template must require: what was built, what it enables, why it matters."""
        self.assertIn("What was built", self.template_text)
        self.assertIn("What it enables", self.template_text)
        self.assertIn("Why it matters", self.template_text)

    @covers("REQ-0.23.0-01-01")
    def test_closing_argument_in_both_lanes(self):
        """Both Lite and Heavy lane templates must have Closing Argument sections."""
        self.assertIn("### Closing Argument (Lite)", self.template_text)
        self.assertIn("### Closing Argument (Heavy)", self.template_text)

    @covers("REQ-0.23.0-01-07")
    def test_no_planning_phase_placeholders_in_closing_argument(self):
        """Closing Argument sections in the template must not contain planning placeholders.

        The template's own guidance text and HTML comments are excluded —
        this checks that no planning-phase filler leaked into the required-elements
        area or example blocks.
        """
        # Extract each Closing Argument section body (between heading and next ###)
        sections = re.findall(
            r"^### Closing Argument.*?\n(.*?)(?=^### |\Z)",
            self.template_text,
            re.MULTILINE | re.DOTALL,
        )
        self.assertTrue(sections, "Could not extract Closing Argument section bodies")

        for section_body in sections:
            # Strip HTML comments before checking for placeholders
            stripped = re.sub(r"<!--.*?-->", "", section_body, flags=re.DOTALL)
            for placeholder in PLANNING_PLACEHOLDERS:
                self.assertNotIn(
                    placeholder,
                    stripped,
                    f"Closing Argument section contains planning placeholder: {placeholder!r}",
                )


if __name__ == "__main__":
    unittest.main()
