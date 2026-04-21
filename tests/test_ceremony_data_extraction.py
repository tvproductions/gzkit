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
from gzkit.commands.ceremony_intent import (
    format_intent_pairing_table,
    pair_intent_with_obpis,
    parse_intent_items,
)
from gzkit.commands.ceremony_steps import render_step_2_summary
from gzkit.traceability import covers

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

    @covers("REQ-0.23.0-04-09")
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

    @covers("REQ-0.23.0-04-09")
    def test_titlecase_objective_heading_still_works(self) -> None:
        content = BRIEF_UPPERCASE_HEADINGS.replace("## OBJECTIVE", "## Objective")
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-title.md"
            brief_path.write_text(content, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)

        self.assertIn("Absorb the attestation pattern", meta["objective"])

    @covers("REQ-0.23.0-04-09")
    def test_mixedcase_objective_heading_is_captured(self) -> None:
        content = BRIEF_UPPERCASE_HEADINGS.replace("## OBJECTIVE", "## ObJeCtIvE")
        with tempfile.TemporaryDirectory() as temp_dir:
            brief_path = Path(temp_dir) / "OBPI-mixed.md"
            brief_path.write_text(content, encoding="utf-8")

            meta = extract_brief_metadata(brief_path)

        self.assertIn("Absorb the attestation pattern", meta["objective"])

    @covers("REQ-0.23.0-04-09")
    @covers("REQ-0.23.0-04-13")
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

    @covers("REQ-0.23.0-04-10")
    def test_intent_section_captured_from_canonical_adr(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR-0.25.0-core-infrastructure-pattern-absorption.md"
            adr_path.write_text(ADR_FIXTURE, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertIn("gzkit is the forward platform", intent)
        self.assertIn("one-time harvest", intent)
        self.assertIn("subtraction test", intent)

    @covers("REQ-0.23.0-04-10")
    def test_intent_section_excludes_preamble_and_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR.md"
            adr_path.write_text(ADR_FIXTURE, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertNotIn("Tidy First Plan", intent)
        self.assertNotIn("Role/Goals preamble", intent)
        self.assertNotIn("individual OBPI examination", intent)
        self.assertNotIn("Downstream consequences", intent)

    @covers("REQ-0.23.0-04-10")
    def test_intent_section_case_insensitive(self) -> None:
        content = ADR_FIXTURE.replace("## Intent", "## INTENT")
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path = Path(temp_dir) / "ADR.md"
            adr_path.write_text(content, encoding="utf-8")

            intent = extract_adr_intent(adr_path)

        self.assertIn("gzkit is the forward platform", intent)

    @covers("REQ-0.23.0-04-10")
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

    @covers("REQ-0.23.0-04-10")
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

    @covers("REQ-0.23.0-04-10")
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

    @covers("REQ-0.23.0-04-11")
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

    @covers("REQ-0.23.0-04-13")
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


ADR_INTENT_WITH_BULLETS = """\
---
id: ADR-0.0.18-adr-taxonomy-doctrine
semver: 0.0.18
lane: lite
---

# ADR-0.0.18

## Intent

ADR-0.0.17 closes the naming gap. Adopters still need guidance on:

1. **PRD → ADR derivation**. How does a PRD decompose into foundation vs feature?
2. **Pool curation**. When does an idea belong in the pool vs active?
3. **Epic grouping**. How are epics named, maintained, surfaced?
4. **Foundation-vs-feature decision guidance**. Worked examples, red flags.

**After this ADR**: `docs/user/concepts/adr-taxonomy.md` is canonical.

## Decision

Land doctrine.
"""


def _obpi_brief(obpi_id: str, title: str, objective: str) -> str:
    return (
        f"---\nid: {obpi_id}\nstatus: Completed\nlane: lite\n---\n\n"
        f"# {obpi_id}: {title}\n\n## Objective\n\n{objective}\n"
    )


class TestParseIntentItems(unittest.TestCase):
    """GHI #259: parse_intent_items extracts numbered/dash intent bullets."""

    @covers("REQ-0.23.0-04-10")
    def test_numbered_bold_prefix_items(self) -> None:
        text = (
            "Adopters still need guidance on:\n\n"
            "1. **PRD → ADR derivation**. How does a PRD decompose?\n"
            "2. **Pool curation**. When does an idea belong in the pool?\n"
        )
        items = parse_intent_items(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["heading"], "PRD → ADR derivation")
        self.assertIn("How does a PRD decompose", items[0]["body"])
        self.assertEqual(items[1]["heading"], "Pool curation")

    @covers("REQ-0.23.0-04-10")
    def test_dash_bold_prefix_items(self) -> None:
        text = "- **Foo**. First item body.\n- **Bar**. Second item body.\n"
        items = parse_intent_items(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["heading"], "Foo")
        self.assertEqual(items[1]["heading"], "Bar")

    @covers("REQ-0.23.0-04-10")
    def test_plain_numbered_items_without_bold(self) -> None:
        text = "1. First concern with prose body.\n2. Second concern with body.\n"
        items = parse_intent_items(text)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["heading"], "First concern with prose body.")

    @covers("REQ-0.23.0-04-10")
    def test_prose_only_returns_empty(self) -> None:
        text = "This is a prose-only intent section with no bullets at all.\n"
        items = parse_intent_items(text)
        self.assertEqual(items, [])


class TestPairIntentWithObpis(unittest.TestCase):
    """GHI #259: pair_intent_with_obpis matches intent headings to OBPIs."""

    @covers("REQ-0.23.0-04-10")
    def test_matches_by_slug_keyword(self) -> None:
        items = [{"heading": "PRD → ADR derivation", "body": ""}]
        briefs = [
            {
                "id": "OBPI-0.0.18-02-runbook-prd-to-adr",
                "title": "runbook prd to adr",
                "objective": "Expand runbook with PRD to ADR derivation heuristics.",
            }
        ]
        result = pair_intent_with_obpis(items, briefs)
        self.assertEqual(len(result), 1)
        self.assertIn("OBPI-0.0.18-02-runbook-prd-to-adr", result[0]["delivered_by"])

    @covers("REQ-0.23.0-04-10")
    def test_matches_by_objective_keyword(self) -> None:
        items = [{"heading": "Pool curation", "body": "When does pool membership apply?"}]
        briefs = [
            {
                "id": "OBPI-0.0.18-03-pool-curation-policy",
                "title": "pool curation policy",
                "objective": "Define pool curation policy with criteria and cadence.",
            }
        ]
        result = pair_intent_with_obpis(items, briefs)
        self.assertIn("OBPI-0.0.18-03-pool-curation-policy", result[0]["delivered_by"])

    @covers("REQ-0.23.0-04-10")
    def test_multiple_obpis_per_intent(self) -> None:
        items = [{"heading": "Foundation-vs-feature decision guidance", "body": ""}]
        briefs = [
            {
                "id": "OBPI-0.0.18-01-concepts-page",
                "title": "concepts page",
                "objective": "Author the foundation vs feature concepts page.",
            },
            {
                "id": "OBPI-0.0.18-05-skill-prompt-enrichment",
                "title": "skill prompt enrichment",
                "objective": ("Enrich skill prompts with foundation vs feature decision guidance."),
            },
        ]
        result = pair_intent_with_obpis(items, briefs)
        delivered = result[0]["delivered_by"]
        self.assertIn("OBPI-0.0.18-01-concepts-page", delivered)
        self.assertIn("OBPI-0.0.18-05-skill-prompt-enrichment", delivered)

    @covers("REQ-0.23.0-04-10")
    def test_no_match_returns_empty_delivered_by(self) -> None:
        items = [{"heading": "Completely unrelated topic xyzzy", "body": ""}]
        briefs = [
            {
                "id": "OBPI-0.0.18-01-concepts-page",
                "title": "concepts",
                "objective": "authoring work",
            }
        ]
        result = pair_intent_with_obpis(items, briefs)
        self.assertEqual(result[0]["delivered_by"], [])


class TestFormatIntentPairingTable(unittest.TestCase):
    """GHI #259: renderer produces 2-column table."""

    @covers("REQ-0.23.0-04-10")
    def test_renders_pairings_with_delivered_by(self) -> None:
        pairings = [
            {
                "heading": "PRD → ADR derivation",
                "body": "",
                "delivered_by": ["OBPI-0.0.18-02-runbook-prd-to-adr"],
            },
            {
                "heading": "Pool curation",
                "body": "",
                "delivered_by": ["OBPI-0.0.18-03-pool-curation-policy"],
            },
        ]
        out = format_intent_pairing_table(pairings)
        flat = " ".join(line.strip("│ ") for line in out.splitlines())
        self.assertIn("PRD → ADR derivation", flat)
        self.assertIn("02-runbook-prd-to-adr", flat)
        self.assertIn("Pool curation", flat)
        self.assertIn("03-pool-curation-policy", flat)

    @covers("REQ-0.23.0-04-10")
    def test_renders_review_bom_hint_when_no_match(self) -> None:
        pairings = [{"heading": "X", "body": "", "delivered_by": []}]
        out = format_intent_pairing_table(pairings)
        self.assertIn("(review BOM below)", out)


class TestRenderStep2WithPairingTable(unittest.TestCase):
    """GHI #259: Step 2 renders intent ↔ OBPI pairing table when bullets exist."""

    def _write_fixture(self, temp_dir: Path) -> tuple[Path, list[Path], Path]:
        project_root = temp_dir
        adr_dir = project_root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.18"
        adr_dir.mkdir(parents=True)
        adr_path = adr_dir / "ADR-0.0.18.md"
        adr_path.write_text(ADR_INTENT_WITH_BULLETS, encoding="utf-8")

        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir()

        obpis = [
            (
                "OBPI-0.0.18-01-concepts-page",
                "concepts page",
                "Author the foundation vs feature concepts page with decision guidance.",
            ),
            (
                "OBPI-0.0.18-02-runbook-prd-to-adr",
                "runbook prd to adr",
                "Expand runbook with PRD to ADR derivation heuristics.",
            ),
            (
                "OBPI-0.0.18-03-pool-curation-policy",
                "pool curation policy",
                "Define pool curation policy.",
            ),
            (
                "OBPI-0.0.18-04-epic-grouping",
                "epic grouping",
                "Document epic grouping naming convention.",
            ),
        ]
        paths: list[Path] = []
        for obpi_id, title, objective in obpis:
            p = obpi_dir / f"{obpi_id}.md"
            p.write_text(_obpi_brief(obpi_id, title, objective), encoding="utf-8")
            paths.append(p)

        return adr_path, paths, project_root

    @covers("REQ-0.23.0-04-10")
    def test_step2_contains_intent_pairing_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.0.18",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="lite",
                project_root=project_root,
            )
        flat = " ".join(line.strip("│ ") for line in rendered.splitlines())
        self.assertIn("ADR Intent", flat)
        self.assertIn("Delivered by", flat)
        self.assertIn("PRD → ADR derivation", flat)
        self.assertIn("Pool curation", flat)
        self.assertIn("Epic grouping", flat)

    @covers("REQ-0.23.0-04-10")
    def test_step2_pairs_intent_to_obpis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adr_path, obpi_files, project_root = self._write_fixture(Path(temp_dir))
            rendered = render_step_2_summary(
                adr_id="ADR-0.0.18",
                adr_file=adr_path,
                obpi_files=obpi_files,
                lane="lite",
                project_root=project_root,
            )
        flat = " ".join(line.strip("│ ") for line in rendered.splitlines())
        self.assertIn("02-runbook-prd-to-adr", flat)
        self.assertIn("03-pool-curation-policy", flat)
        self.assertIn("04-epic-grouping", flat)

    @covers("REQ-0.23.0-04-10")
    def test_step2_falls_back_to_prose_when_no_bullets(self) -> None:
        """An ADR with prose-only intent still renders prose (not an empty pairing table)."""
        content = ADR_INTENT_WITH_BULLETS.replace(
            "1. **PRD → ADR derivation**. How does a PRD decompose into foundation vs feature?\n"
            "2. **Pool curation**. When does an idea belong in the pool vs active?\n"
            "3. **Epic grouping**. How are epics named, maintained, surfaced?\n"
            "4. **Foundation-vs-feature decision guidance**. Worked examples, red flags.\n",
            "Just prose here, no bulleted items for the adopters to cross-reference.\n",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            adr_dir = project_root / "adr"
            adr_dir.mkdir()
            adr_path = adr_dir / "ADR.md"
            adr_path.write_text(content, encoding="utf-8")

            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir()
            obpi_path = obpi_dir / "OBPI-X.md"
            obpi_path.write_text(_obpi_brief("OBPI-X", "x", "Some objective."), encoding="utf-8")
            rendered = render_step_2_summary(
                adr_id="ADR",
                adr_file=adr_path,
                obpi_files=[obpi_path],
                lane="lite",
                project_root=project_root,
            )

        self.assertIn("Just prose here", rendered)


if __name__ == "__main__":
    unittest.main()
