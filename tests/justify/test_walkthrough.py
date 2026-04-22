"""Tests for gzkit.justify.walkthrough — models, rendering, scaffold entry point.

Covers OBPI-0.0.19-02 REQ-01 through REQ-05 (CLI REQs 06-12 live in
tests/commands/test_justify_cmd.py). REQ assertions pin semantic contract
derived from the OBPI brief, not current output shape.
"""

from __future__ import annotations

import re
import unittest
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from gzkit.justify.models import AnchorRef, CommitRef, EvidenceBundle, LedgerEvent, RuleCitation
from gzkit.justify.walkthrough import (
    SECTION_HEADINGS,
    SECTION_PROMPTS,
    Walkthrough,
    WalkthroughSection,
    render_markdown,
    render_scaffold,
)
from gzkit.traceability import covers

CANONICAL_HEADINGS = [
    "What I see (the problem)",
    "Per-instance severity",
    "Why this scope",
    "What it proposes",
    "Routing decision",
    "Why this design is right-sized",
    "What convinces me (evidence)",
    "Residual uncertainty",
]


def _section(
    ordinal: int, *, reasoning: str = "_[To be filled]_", citations: list[str] | None = None
) -> WalkthroughSection:
    return WalkthroughSection(
        ordinal=ordinal,
        heading=CANONICAL_HEADINGS[ordinal - 1],
        prompt=SECTION_PROMPTS[ordinal],
        evidence_citations=citations or [],
        reasoning=reasoning,
    )


def _eight_sections(reasoning: str = "_[To be filled]_") -> list[WalkthroughSection]:
    return [_section(i, reasoning=reasoning) for i in range(1, 9)]


def _make_anchor(body: str | None = None) -> AnchorRef:
    return AnchorRef(
        kind="ghi",
        identifier="GHI-232",
        title="Example anchor",
        body=body,
        labels=(),
        author="octocat",
    )


def _make_evidence(
    anchor: AnchorRef, *, rules: bool = False, events: bool = False, commits: bool = False
) -> EvidenceBundle:
    return EvidenceBundle(
        anchor=anchor,
        matching_rules=(
            (
                RuleCitation(
                    rule_id="rules.cli.md",
                    path=".gzkit/rules/cli.md",
                    description="CLI contract",
                    paths_globs=("src/gzkit/commands/**",),
                ),
            )
            if rules
            else ()
        ),
        ledger_events=(
            (
                LedgerEvent(
                    event="adr_created",
                    id="ADR-0.0.19",
                    ts="2026-04-20T00:00:00+00:00",
                    parent=None,
                    extra={},
                ),
            )
            if events
            else ()
        ),
        recent_commits=(
            (CommitRef(sha="abcdef1234567890", subject="feat(justify): anchor"),) if commits else ()
        ),
        related_anchors=(),
        taxonomy_reference="docs/governance/model-regression-taxonomy.md",
        warnings=(),
    )


class TestSectionHeadings(unittest.TestCase):
    @covers("REQ-0.0.19-02-01")
    def test_section_headings_match_canonical_order(self) -> None:
        self.assertEqual(SECTION_HEADINGS, CANONICAL_HEADINGS)
        self.assertEqual(len(SECTION_HEADINGS), 8)

    @covers("REQ-0.0.19-02-01")
    def test_section_prompts_cover_all_eight_ordinals(self) -> None:
        self.assertEqual(sorted(SECTION_PROMPTS.keys()), list(range(1, 9)))
        for prompt in SECTION_PROMPTS.values():
            self.assertTrue(prompt.strip(), "each section prompt must be non-empty")


class TestWalkthroughSection(unittest.TestCase):
    @covers("REQ-0.0.19-02-02")
    def test_is_filled_false_on_placeholder(self) -> None:
        section = _section(1, reasoning="_[To be filled]_")
        self.assertFalse(section.is_filled)

    @covers("REQ-0.0.19-02-02")
    def test_is_filled_false_on_empty_whitespace(self) -> None:
        section = _section(1, reasoning="   \n\t  ")
        self.assertFalse(section.is_filled)

    @covers("REQ-0.0.19-02-02")
    def test_is_filled_true_on_actual_reasoning(self) -> None:
        section = _section(1, reasoning="Because the brief requires it.")
        self.assertTrue(section.is_filled)

    @covers("REQ-0.0.19-02-02")
    def test_is_filled_false_when_placeholder_embedded(self) -> None:
        section = _section(1, reasoning="Intro text _[To be filled]_ trailing")
        self.assertFalse(section.is_filled)

    @covers("REQ-0.0.19-02-01")
    def test_section_rejects_ordinal_below_range(self) -> None:
        with self.assertRaises(ValidationError):
            WalkthroughSection(
                ordinal=0,
                heading="Anything",
                prompt="prompt",
                evidence_citations=[],
                reasoning="_[To be filled]_",
            )

    @covers("REQ-0.0.19-02-01")
    def test_section_rejects_ordinal_above_range(self) -> None:
        with self.assertRaises(ValidationError):
            WalkthroughSection(
                ordinal=9,
                heading="Anything",
                prompt="prompt",
                evidence_citations=[],
                reasoning="_[To be filled]_",
            )

    @covers("REQ-0.0.19-02-01")
    def test_section_is_frozen(self) -> None:
        section = _section(1)
        with self.assertRaises(ValidationError):
            section.reasoning = "mutated"  # type: ignore[misc]


class TestWalkthroughModel(unittest.TestCase):
    @covers("REQ-0.0.19-02-01")
    def test_accepts_canonical_eight_sections(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        walkthrough = Walkthrough(
            anchor=anchor,
            evidence=evidence,
            generated_at="2026-04-22T00:00:00+00:00",
            sections=_eight_sections(),
        )
        self.assertEqual([s.ordinal for s in walkthrough.sections], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(walkthrough.scaffold_version, "1.0")

    @covers("REQ-0.0.19-02-01")
    def test_rejects_missing_ordinal(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        seven = _eight_sections()[:7]
        with self.assertRaises(ValidationError):
            Walkthrough(
                anchor=anchor,
                evidence=evidence,
                generated_at="2026-04-22T00:00:00+00:00",
                sections=seven,
            )

    @covers("REQ-0.0.19-02-01")
    def test_rejects_duplicate_ordinal(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        sections = _eight_sections()
        sections[2] = _section(3)  # duplicate ordinal 3
        with self.assertRaises(ValidationError):
            Walkthrough(
                anchor=anchor,
                evidence=evidence,
                generated_at="2026-04-22T00:00:00+00:00",
                sections=sections[:-1] + [sections[2]],
            )

    @covers("REQ-0.0.19-02-01")
    def test_rejects_permuted_ordinals(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        sections = _eight_sections()
        sections[1], sections[2] = sections[2], sections[1]  # swap 2 and 3
        with self.assertRaises(ValidationError):
            Walkthrough(
                anchor=anchor,
                evidence=evidence,
                generated_at="2026-04-22T00:00:00+00:00",
                sections=sections,
            )

    @covers("REQ-0.0.19-02-01")
    def test_rejects_heading_drift(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        sections = _eight_sections()
        sections[0] = WalkthroughSection(
            ordinal=1,
            heading="Wrong heading text",
            prompt=SECTION_PROMPTS[1],
            evidence_citations=[],
            reasoning="_[To be filled]_",
        )
        with self.assertRaises(ValidationError):
            Walkthrough(
                anchor=anchor,
                evidence=evidence,
                generated_at="2026-04-22T00:00:00+00:00",
                sections=sections,
            )

    @covers("REQ-0.0.19-02-03")
    def test_is_complete_true_when_all_sections_filled(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        walkthrough = Walkthrough(
            anchor=anchor,
            evidence=evidence,
            generated_at="2026-04-22T00:00:00+00:00",
            sections=_eight_sections(reasoning="Actual reasoning."),
        )
        self.assertTrue(walkthrough.is_complete())

    @covers("REQ-0.0.19-02-03")
    def test_is_complete_false_when_any_section_placeholder(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        sections = _eight_sections(reasoning="Actual reasoning.")
        sections[4] = _section(5, reasoning="_[To be filled]_")
        walkthrough = Walkthrough(
            anchor=anchor,
            evidence=evidence,
            generated_at="2026-04-22T00:00:00+00:00",
            sections=sections,
        )
        self.assertFalse(walkthrough.is_complete())


class TestRenderScaffold(unittest.TestCase):
    @covers("REQ-0.0.19-02-05")
    def test_builds_eight_sections_with_placeholders(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        walkthrough = render_scaffold(anchor, evidence, now=datetime(2026, 1, 1, tzinfo=UTC))
        self.assertEqual(len(walkthrough.sections), 8)
        for section in walkthrough.sections:
            self.assertEqual(section.reasoning, "_[To be filled]_")
            self.assertFalse(section.is_filled)

    @covers("REQ-0.0.19-02-05")
    def test_section_one_extracts_anchor_body_citations(self) -> None:
        body = "See GHI-232 and also GHI-233. Related: OBPI-0.0.19-01 and ADR-0.0.19."
        anchor = _make_anchor(body=body)
        evidence = _make_evidence(anchor)
        walkthrough = render_scaffold(anchor, evidence, now=datetime(2026, 1, 1, tzinfo=UTC))
        citations = walkthrough.sections[0].evidence_citations
        self.assertIn("GHI-232", citations)
        self.assertIn("GHI-233", citations)
        self.assertIn("OBPI-0.0.19-01", citations)
        self.assertIn("ADR-0.0.19", citations)

    @covers("REQ-0.0.19-02-05")
    def test_section_one_empty_when_body_is_none(self) -> None:
        anchor = _make_anchor(body=None)
        evidence = _make_evidence(anchor)
        walkthrough = render_scaffold(anchor, evidence, now=datetime(2026, 1, 1, tzinfo=UTC))
        self.assertEqual(walkthrough.sections[0].evidence_citations, [])

    @covers("REQ-0.0.19-02-05")
    def test_section_seven_pulls_all_three_evidence_sources(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor, rules=True, events=True, commits=True)
        walkthrough = render_scaffold(anchor, evidence, now=datetime(2026, 1, 1, tzinfo=UTC))
        section7 = walkthrough.sections[6]
        self.assertEqual(len(section7.evidence_citations), 3)
        combined = " | ".join(section7.evidence_citations)
        self.assertIn("rules.cli.md", combined)
        self.assertIn("ADR-0.0.19", combined)
        self.assertIn("abcdef1", combined)

    @covers("REQ-0.0.19-02-05")
    def test_non_populated_sections_have_empty_citations(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor, rules=True, events=True, commits=True)
        walkthrough = render_scaffold(anchor, evidence, now=datetime(2026, 1, 1, tzinfo=UTC))
        for ordinal in (2, 3, 4, 5, 6, 8):
            self.assertEqual(
                walkthrough.sections[ordinal - 1].evidence_citations,
                [],
                f"section {ordinal} must be empty for scaffold",
            )

    @covers("REQ-0.0.19-02-04")
    def test_generated_at_uses_injected_now(self) -> None:
        anchor = _make_anchor()
        evidence = _make_evidence(anchor)
        fixed = datetime(2026, 4, 22, 12, 34, 56, tzinfo=UTC)
        walkthrough = render_scaffold(anchor, evidence, now=fixed)
        self.assertEqual(walkthrough.generated_at, fixed.isoformat())


class TestRenderMarkdown(unittest.TestCase):
    def _render(self) -> str:
        anchor = _make_anchor(body="See GHI-232 for context.")
        evidence = _make_evidence(anchor, rules=True, events=True, commits=True)
        walkthrough = render_scaffold(
            anchor, evidence, now=datetime(2026, 4, 22, 0, 0, 0, tzinfo=UTC)
        )
        return render_markdown(walkthrough)

    @covers("REQ-0.0.19-02-04")
    def test_rendered_markdown_byte_stable_across_invocations(self) -> None:
        first = self._render()
        second = self._render()
        self.assertEqual(first, second)

    @covers("REQ-0.0.19-02-05")
    def test_rendered_markdown_has_yaml_frontmatter(self) -> None:
        rendered = self._render()
        self.assertTrue(rendered.startswith("---\n"))
        frontmatter_end = rendered.index("\n---\n", 4)
        frontmatter = rendered[4:frontmatter_end]
        self.assertIn("anchor_id:", frontmatter)
        self.assertIn("anchor_kind:", frontmatter)
        self.assertIn("generated_at:", frontmatter)
        self.assertIn("scaffold_version:", frontmatter)

    @covers("REQ-0.0.19-02-05")
    def test_rendered_markdown_has_exactly_eight_h2_sections(self) -> None:
        rendered = self._render()
        matches = re.findall(r"^## \d+\. ", rendered, flags=re.MULTILINE)
        self.assertEqual(len(matches), 8)

    @covers("REQ-0.0.19-02-05")
    def test_each_section_has_evidence_prompt_reasoning(self) -> None:
        rendered = self._render()
        for ordinal, heading in enumerate(CANONICAL_HEADINGS, start=1):
            marker = f"## {ordinal}. {heading}"
            self.assertIn(marker, rendered, f"missing section {ordinal}")
        self.assertEqual(rendered.count("**Evidence:**"), 8)
        self.assertEqual(rendered.count("**Prompt:**"), 8)
        self.assertEqual(rendered.count("_[To be filled]_"), 8)

    @covers("REQ-0.0.19-02-04")
    def test_rendered_markdown_matches_golden_fixture(self) -> None:
        rendered = self._render()
        fixture_path = Path(__file__).parent / "fixtures" / "walkthrough_expected.md"
        expected = fixture_path.read_text(encoding="utf-8")
        self.assertEqual(rendered, expected)


if __name__ == "__main__":
    unittest.main()
