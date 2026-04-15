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

from gzkit.commands.ceremony_data import (
    extract_adr_intent,
    extract_brief_metadata,
    format_summary_table,
)
from gzkit.commands.ceremony_steps import render_step_2_summary

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


ADR_FIXTURE = """\
---
id: ADR-0.25.0-core-infrastructure-pattern-absorption
status: Proposed
semver: 0.25.0
lane: heavy
---

# ADR-0.25.0: Core Infrastructure Pattern Absorption

## Tidy First Plan

Preamble content that must not leak into the intent extraction.

## Agent Context Frame

Role/Goals preamble that also must not leak into intent extraction.

## Intent

gzkit is the forward platform — it will serve as the governance and
infrastructure foundation for airlineops and future projects. This ADR
governs a one-time harvest of every reusable core infrastructure pattern
from airlineops into gzkit.

**Phase 1** examines airlineops's core/common packages (17 modules).
**Phase 2** examines airlineops's opsdev packages (16 modules).

After absorption, the subtraction test holds: the only thing left in
airlineops that isn't from gzkit is pure airline domain code.

## Decision

- Each of the 33 airlineops modules gets individual OBPI examination
- Three outcomes per module: Absorb, Confirm, or Exclude

## Consequences

Downstream consequences text.
"""


class TestExtractAdrIntent(unittest.TestCase):
    """GHI-155: extract_adr_intent pulls the ## Intent section for Step 2 framing."""

    def test_intent_section_captured_from_canonical_adr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR-0.25.0-core-infrastructure-pattern-absorption.md"
            adr_path.write_text(ADR_FIXTURE, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertIn("gzkit is the forward platform", intent)
        self.assertIn("one-time harvest", intent)
        self.assertIn("subtraction test", intent)

    def test_intent_section_excludes_preamble_and_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR.md"
            adr_path.write_text(ADR_FIXTURE, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertNotIn("Tidy First Plan", intent)
        self.assertNotIn("Role/Goals preamble", intent)
        self.assertNotIn("individual OBPI examination", intent)
        self.assertNotIn("Downstream consequences", intent)

    def test_intent_section_case_insensitive(self) -> None:
        content = ADR_FIXTURE.replace("## Intent", "## INTENT")
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR.md"
            adr_path.write_text(content, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertIn("gzkit is the forward platform", intent)

    def test_intent_missing_returns_empty_string(self) -> None:
        content = "# ADR\n\n## Decision\n\nNo intent section here.\n"
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR.md"
            adr_path.write_text(content, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertEqual(intent, "")


class TestRenderStep2ScopeReview(unittest.TestCase):
    """GHI-155: Step 2 must frame the scope review with ADR intent, not generic QA."""

    def _write_ceremony_fixture(self, temp_dir: Path) -> tuple[Path, list[Path], Path]:
        project_root = temp_dir
        adr_dir = project_root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.25.0"
        adr_dir.mkdir(parents=True)
        adr_path = adr_dir / "ADR-0.25.0-core-infrastructure-pattern-absorption.md"
        adr_path.write_text(ADR_FIXTURE, encoding="utf-8")

        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir()
        obpi_path = obpi_dir / "OBPI-0.25.0-01-attestation-pattern.md"
        obpi_path.write_text(BRIEF_UPPERCASE_HEADINGS, encoding="utf-8")

        return adr_path, [obpi_path], project_root

    def test_step_2_contains_adr_intent_framing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_ceremony_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.25.0-core-infrastructure-pattern-absorption",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="heavy",
                project_root=project_root,
            )

        self.assertIn("gzkit is the forward platform", rendered)
        self.assertIn("one-time harvest", rendered)

    def test_step_2_contains_scope_review_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_ceremony_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.25.0-core-infrastructure-pattern-absorption",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="heavy",
                project_root=project_root,
            )

        lower = rendered.lower()
        self.assertIn("scope review", lower)
        self.assertTrue(
            any(phrase in lower for phrase in ("match the", "matches the", "scope match"))
            and "intent" in lower,
            "Step 2 must frame the scope-vs-intent question explicitly",
        )

    def test_step_2_omits_generic_qa_command_block(self) -> None:
        """Generic QA commands belong to Steps 4-5 walkthrough, not Step 2."""
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_ceremony_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.25.0-core-infrastructure-pattern-absorption",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="heavy",
                project_root=project_root,
            )

        self.assertNotIn("uv run gz test", rendered)
        self.assertNotIn("uv run gz lint", rendered)
        self.assertNotIn("uv run gz typecheck", rendered)
        self.assertNotIn("uv run mkdocs build", rendered)
        self.assertNotIn("uv run -m behave", rendered)
        self.assertNotIn("for your direct observation", rendered)

    def test_step_2_still_contains_bom_table_objective(self) -> None:
        """The BOM table must still render the OBPI objective alongside the new framing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_ceremony_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.25.0-core-infrastructure-pattern-absorption",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="heavy",
                project_root=project_root,
            )

        flat = " ".join(line.strip("│ ") for line in rendered.splitlines())
        self.assertIn("Absorb the attestation pattern", flat)


if __name__ == "__main__":
    unittest.main()
