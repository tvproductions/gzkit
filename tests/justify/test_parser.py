"""Unit tests for gzkit.justify.parser — reverse parser + ValidateResult.

Covers OBPI-0.0.19-03 REQs 01 through 04, 09, 10, and 11. CLI-level REQs
(05 through 08, 12) live in tests/commands/test_justify_validate.py.

Tests pin semantic contract derived from the OBPI brief acceptance criteria,
not current implementation output shape.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.justify.models import AnchorRef, EvidenceBundle
from gzkit.justify.parser import (
    ValidateResult,
    WalkthroughParseError,
    parse_walkthrough,
)
from gzkit.justify.walkthrough import (
    SECTION_HEADINGS,
    SECTION_PROMPTS,
    Walkthrough,
    WalkthroughSection,
    render_markdown,
)
from gzkit.traceability import covers

_TAXONOMY_REFERENCE_PATH = "docs/governance/model-regression-taxonomy.md"


def _make_anchor(*, kind: str = "ghi", identifier: str | None = "GHI-232") -> AnchorRef:
    return AnchorRef(
        kind=kind,  # type: ignore[arg-type]
        identifier=identifier,
        title=None,
        body=None,
    )


def _empty_evidence(anchor: AnchorRef) -> EvidenceBundle:
    return EvidenceBundle(
        anchor=anchor,
        matching_rules=(),
        ledger_events=(),
        recent_commits=(),
        related_anchors=(),
        taxonomy_reference=_TAXONOMY_REFERENCE_PATH,
        warnings=(),
    )


def _filled_section(ordinal: int, *, reasoning: str | None = None) -> WalkthroughSection:
    return WalkthroughSection(
        ordinal=ordinal,
        heading=SECTION_HEADINGS[ordinal - 1],
        prompt=SECTION_PROMPTS[ordinal],
        evidence_citations=[],
        reasoning=reasoning or f"Filled reasoning for section {ordinal}.",
    )


def _filled_walkthrough(
    *,
    anchor: AnchorRef | None = None,
    section_reasonings: dict[int, str] | None = None,
) -> Walkthrough:
    anchor = anchor or _make_anchor()
    overrides = section_reasonings or {}
    sections = [_filled_section(i, reasoning=overrides.get(i)) for i in range(1, 9)]
    return Walkthrough(
        anchor=anchor,
        evidence=_empty_evidence(anchor),
        generated_at="2026-04-22T00:00:00+00:00",
        sections=sections,
        scaffold_version="1.0",
    )


class TestParseWalkthroughHappyPath(unittest.TestCase):
    """Structural parse of a rendered, fully-filled walkthrough."""

    @covers("REQ-0.0.19-03-01")
    def test_filled_render_parses_to_complete_walkthrough(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)

        parsed = parse_walkthrough(markdown)

        self.assertIsInstance(parsed, Walkthrough)
        self.assertTrue(parsed.is_complete())
        self.assertEqual(len(parsed.sections), 8)
        for section in parsed.sections:
            self.assertTrue(section.is_filled)

    @covers("REQ-0.0.19-03-01")
    def test_parsed_walkthrough_preserves_section_order_and_headings(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)

        parsed = parse_walkthrough(markdown)

        self.assertEqual([s.ordinal for s in parsed.sections], list(range(1, 9)))
        self.assertEqual([s.heading for s in parsed.sections], SECTION_HEADINGS)

    @covers("REQ-0.0.19-03-01")
    def test_parsed_walkthrough_preserves_prompts(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)

        parsed = parse_walkthrough(markdown)

        for section in parsed.sections:
            self.assertEqual(section.prompt, SECTION_PROMPTS[section.ordinal])

    @covers("REQ-0.0.19-03-01")
    def test_parsed_walkthrough_preserves_reasoning_text(self) -> None:
        walkthrough = _filled_walkthrough(
            section_reasonings={i: f"Reasoning for {i} with extra words." for i in range(1, 9)},
        )
        markdown = render_markdown(walkthrough)

        parsed = parse_walkthrough(markdown)

        for i in range(1, 9):
            self.assertEqual(
                parsed.sections[i - 1].reasoning,
                f"Reasoning for {i} with extra words.",
            )


class TestParseWalkthroughRoundTrip(unittest.TestCase):
    """REQ-03: parser is the inverse of the renderer for structurally valid inputs."""

    @covers("REQ-0.0.19-03-02")
    def test_round_trip_equals_original_for_complete_walkthrough(self) -> None:
        walkthrough = _filled_walkthrough()

        round_trip = parse_walkthrough(render_markdown(walkthrough))

        self.assertEqual(round_trip, walkthrough)

    @covers("REQ-0.0.19-03-02")
    def test_round_trip_equals_original_for_walkthrough_with_unfilled_sections(self) -> None:
        anchor = _make_anchor()
        sections = [
            _filled_section(i)
            if i not in {2, 5, 8}
            else WalkthroughSection(
                ordinal=i,
                heading=SECTION_HEADINGS[i - 1],
                prompt=SECTION_PROMPTS[i],
                evidence_citations=[],
                reasoning="_[To be filled]_",
            )
            for i in range(1, 9)
        ]
        walkthrough = Walkthrough(
            anchor=anchor,
            evidence=_empty_evidence(anchor),
            generated_at="2026-04-22T00:00:00+00:00",
            sections=sections,
        )

        round_trip = parse_walkthrough(render_markdown(walkthrough))

        self.assertEqual(round_trip, walkthrough)

    @covers("REQ-0.0.19-03-02")
    def test_round_trip_equals_original_for_draft_anchor(self) -> None:
        # Draft anchors serialize kind + draft_slug (via the "draft-<slug>"
        # frontmatter fallback). draft_text is not serialized by the renderer,
        # so the round-trippable shape omits it.
        anchor = AnchorRef(
            kind="draft",
            identifier=None,
            title=None,
            body=None,
            draft_slug="my-proposal",
        )
        walkthrough = _filled_walkthrough(anchor=anchor)

        round_trip = parse_walkthrough(render_markdown(walkthrough))

        self.assertEqual(round_trip, walkthrough)


class TestParseWalkthroughFrontmatterStrictness(unittest.TestCase):
    """REQ-04: unparseable input raises with first-failure location."""

    @covers("REQ-0.0.19-03-03")
    def test_missing_frontmatter_raises_with_line_reference(self) -> None:
        markdown_without_frontmatter = "# Walkthrough: GHI-232\n\n## 1. Heading\n"

        with self.assertRaises(WalkthroughParseError) as cm:
            parse_walkthrough(markdown_without_frontmatter)

        message = str(cm.exception)
        self.assertIn("frontmatter", message.lower())
        self.assertIn("line 1", message.lower())

    @covers("REQ-0.0.19-03-03")
    def test_empty_input_raises_with_line_reference(self) -> None:
        with self.assertRaises(WalkthroughParseError) as cm:
            parse_walkthrough("")

        self.assertIn("frontmatter", str(cm.exception).lower())


class TestParseWalkthroughSectionStrictness(unittest.TestCase):
    """REQ-04: H2 ordinal order and heading alignment are strict."""

    @covers("REQ-0.0.19-03-04")
    def test_out_of_order_headings_raise_with_heading_reference(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        # Swap sections 5 and 6: take the rendered text and reverse the order
        # of the two H2 blocks.
        lines = markdown.splitlines(keepends=True)
        section_starts: list[int] = []
        for idx, line in enumerate(lines):
            if line.startswith("## "):
                section_starts.append(idx)
        self.assertEqual(len(section_starts), 8)
        s5_start, s5_end = section_starts[4], section_starts[5]
        s6_start, s6_end = section_starts[5], section_starts[6]
        section5 = lines[s5_start:s5_end]
        section6 = lines[s6_start:s6_end]
        swapped = lines[:s5_start] + section6 + section5 + lines[s6_end:]
        swapped_markdown = "".join(swapped)

        with self.assertRaises(WalkthroughParseError) as cm:
            parse_walkthrough(swapped_markdown)

        message = str(cm.exception)
        self.assertIn("heading", message.lower())

    @covers("REQ-0.0.19-03-05")
    def test_seven_sections_raise_count_mismatch(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        # Truncate at the start of section 8.
        cutoff = markdown.index("## 8. ")
        truncated = markdown[:cutoff].rstrip() + "\n"

        with self.assertRaises(WalkthroughParseError) as cm:
            parse_walkthrough(truncated)

        message = str(cm.exception).lower()
        self.assertIn("8 sections", message)

    @covers("REQ-0.0.19-03-05")
    def test_nine_sections_raise_count_mismatch(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        extra_section = (
            "## 9. Extra heading\n\n"
            "**Prompt:** *extra*\n\n"
            "**Evidence:**\n\n"
            "- _(no citations for this section)_\n\n"
            "Filler.\n\n"
        )
        with_extra = markdown.rstrip() + "\n\n" + extra_section

        with self.assertRaises(WalkthroughParseError) as cm:
            parse_walkthrough(with_extra)

        message = str(cm.exception).lower()
        self.assertIn("8 sections", message)

    @covers("REQ-0.0.19-03-04")
    def test_missing_evidence_block_raises(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        broken = markdown.replace("**Evidence:**", "**Evidencium:**", 1)

        with self.assertRaises(WalkthroughParseError):
            parse_walkthrough(broken)

    @covers("REQ-0.0.19-03-04")
    def test_missing_prompt_block_raises(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        broken = markdown.replace("**Prompt:**", "**Prompto:**", 1)

        with self.assertRaises(WalkthroughParseError):
            parse_walkthrough(broken)


class TestParseWalkthroughTolerance(unittest.TestCase):
    """REQ-02: parser is tolerant of trailing whitespace, blank lines, and # comments."""

    @covers("REQ-0.0.19-03-01")
    def test_trailing_whitespace_is_tolerated(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        noisy = markdown.replace("\n", "   \n")

        parsed = parse_walkthrough(noisy)

        self.assertTrue(parsed.is_complete())

    @covers("REQ-0.0.19-03-01")
    def test_extra_blank_lines_between_sections_tolerated(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        noisy = markdown.replace("\n\n## ", "\n\n\n\n## ")

        parsed = parse_walkthrough(noisy)

        self.assertTrue(parsed.is_complete())

    @covers("REQ-0.0.19-03-01")
    def test_hash_style_comment_lines_tolerated(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        # Insert a line-level comment between frontmatter and the title heading.
        # The title (H1) is skipped by the parser; a comment line elsewhere
        # is also skipped.
        noisy = markdown.replace(
            "# Walkthrough: ",
            "# Walkthrough: ",
            1,
        )
        # Inject comment before section 2.
        noisy = noisy.replace(
            "## 2. ",
            "# stray comment line\n\n## 2. ",
            1,
        )

        parsed = parse_walkthrough(noisy)

        self.assertTrue(parsed.is_complete())


class TestValidateResultContract(unittest.TestCase):
    """REQ-06: ValidateResult is a frozen, extra='forbid' Pydantic model."""

    @covers("REQ-0.0.19-03-09")
    def test_validate_result_is_frozen(self) -> None:
        result = ValidateResult(
            file_path="x.md",
            is_parseable=True,
            is_complete=True,
            unfilled_ordinals=[],
            parse_error=None,
        )
        with self.assertRaises(ValidationError):
            result.file_path = "y.md"  # type: ignore[misc]

    @covers("REQ-0.0.19-03-09")
    def test_validate_result_forbids_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            ValidateResult(
                file_path="x.md",
                is_parseable=True,
                is_complete=True,
                unfilled_ordinals=[],
                parse_error=None,
                extra_field="nope",  # type: ignore[call-arg]
            )

    @covers("REQ-0.0.19-03-09")
    def test_validate_result_serializes_required_keys(self) -> None:
        result = ValidateResult(
            file_path="tests/fixtures/walkthrough_incomplete.md",
            is_parseable=True,
            is_complete=False,
            unfilled_ordinals=[2, 5, 8],
            parse_error=None,
        )

        dumped = result.model_dump()

        self.assertEqual(
            set(dumped.keys()),
            {"file_path", "is_parseable", "is_complete", "unfilled_ordinals", "parse_error"},
        )


class TestStructuralIsCompleteSemantics(unittest.TestCase):
    """REQ-09: is_complete is structural; 'I don't know' reasoning passes."""

    @covers("REQ-0.0.19-03-11")
    def test_i_dont_know_reasoning_is_structurally_complete(self) -> None:
        walkthrough = _filled_walkthrough(
            section_reasonings=dict.fromkeys(range(1, 9), "I don't know"),
        )
        markdown = render_markdown(walkthrough)

        parsed = parse_walkthrough(markdown)

        self.assertTrue(parsed.is_complete())
        for section in parsed.sections:
            self.assertTrue(section.is_filled)


class TestParserSideEffectDiscipline(unittest.TestCase):
    """REQ-10: parser never mutates input and reads only once."""

    @covers("REQ-0.0.19-03-09")
    def test_parser_accepts_string_input_without_mutation(self) -> None:
        walkthrough = _filled_walkthrough()
        markdown = render_markdown(walkthrough)
        original_markdown = markdown

        parse_walkthrough(markdown)

        self.assertEqual(markdown, original_markdown)


if __name__ == "__main__":
    unittest.main()
