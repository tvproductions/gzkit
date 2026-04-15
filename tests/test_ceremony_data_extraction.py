"""GHI-153: extract_brief_metadata must tolerate section heading case drift.

The canonical OBPI template uses ``## Objective`` (title case), but many briefs
across ADR-0.25.0, ADR-0.27.0, ADR-0.35.0, ADR-0.37.0, and foundation ADRs
have drifted to ``## OBJECTIVE`` (uppercase). The closeout ceremony's
Bill-of-Materials table silently rendered an empty Objective column for every
drifted brief because ``_extract_section`` matched heading text literally.

This test exercises the full ``extract_brief_metadata`` pathway against a
temp brief written with uppercase headings and asserts the objective text is
captured. The failure mode is silent data loss in ceremony Step 2, so the
test verifies the field is non-empty and contains the expected prose.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.ceremony_data import extract_brief_metadata, format_summary_table

BRIEF_UPPERCASE_HEADINGS = """\
---
id: OBPI-0.25.0-01-attestation-pattern
status: Completed
lane: heavy
---

# OBPI-0.25.0-01: Attestation Pattern

## ADR ITEM — Level 1 WBS Reference

Parent: ADR-0.25.0

## OBJECTIVE

Absorb the attestation pattern from the canonical reference, preserving
ledger-backed human decisions across the governance lifecycle.

## SOURCE MATERIAL

Reference implementation at ../airlineops.

## Acceptance Criteria

- [ ] Pattern absorbed with test coverage
- [ ] CLI wiring complete
"""


class TestExtractBriefMetadataHeadingCase(unittest.TestCase):
    """extract_brief_metadata captures Objective regardless of heading case."""

    def test_uppercase_objective_heading_is_captured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-0.25.0-01-attestation-pattern.md"
            brief_path.write_text(BRIEF_UPPERCASE_HEADINGS, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)

        self.assertNotEqual(
            meta["objective"],
            "",
            "Objective must be captured when brief uses '## OBJECTIVE' (uppercase).",
        )
        self.assertIn("Absorb the attestation pattern", meta["objective"])
        self.assertIn("ledger-backed human decisions", meta["objective"])

    def test_titlecase_objective_heading_still_works(self) -> None:
        content = BRIEF_UPPERCASE_HEADINGS.replace("## OBJECTIVE", "## Objective")
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-title.md"
            brief_path.write_text(content, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)

        self.assertIn("Absorb the attestation pattern", meta["objective"])

    def test_mixedcase_objective_heading_is_captured(self) -> None:
        content = BRIEF_UPPERCASE_HEADINGS.replace("## OBJECTIVE", "## ObJeCtIvE")
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-mixed.md"
            brief_path.write_text(content, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)

        self.assertIn("Absorb the attestation pattern", meta["objective"])

    def test_bom_table_populates_objective_for_uppercase_brief(self) -> None:
        """End-to-end: brief with uppercase heading → BOM table shows objective."""
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-0.25.0-01-attestation-pattern.md"
            brief_path.write_text(BRIEF_UPPERCASE_HEADINGS, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)
            rendered = format_summary_table([meta], title="Test BOM")

        flat = " ".join(line.strip("│ ") for line in rendered.splitlines())
        self.assertIn("Absorb the attestation pattern", flat)


if __name__ == "__main__":
    unittest.main()
