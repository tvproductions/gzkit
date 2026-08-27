"""Unit tests for scripts/adherence_probe.py.

The probe measures whether a rendered per-turn contract surface is actually
RECALLABLE by a model, section by section, against each section's byte offset.
Published long-context research measures retrieval, never instruction
adherence, so the curve this produces exists nowhere else (Chroma "Context
Rot", 2025; lost-in-the-middle). These tests pin the properties that decide
whether a measurement is trustworthy:

- The question addresses a section by IDENTITY, never by content. A probe that
  carries its own expected answer cannot fail — the hollow-test family
  ``.gzkit/rules/tests.md`` names — so ``build_probe`` must not leak the
  anchor, and that is asserted directly rather than by inspection.
- Scoring is anchored on DISTINCTIVE tokens, so a plausible-sounding
  confabulation does not score as recall.
- A negative control probes a section that does not exist. A model that
  "recalls" it is confabulating, which invalidates the whole run rather than
  costing one row — the discipline ``_qc_negative_controls`` already applies
  to enforcement claims.
- Byte offsets come from the rendered surface, never from a stored constant:
  a frozen measurement in a declaration is a derived view masquerading as
  source-of-truth (Architectural Boundary 6).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "adherence_probe.py"
_spec = importlib.util.spec_from_file_location("adherence_probe", _MODULE_PATH)
assert _spec and _spec.loader
probe = importlib.util.module_from_spec(_spec)
# Registered before exec: @dataclass resolves annotations through
# sys.modules[cls.__module__], which is None for an unregistered spec-loaded
# module. Same pattern as tests/scripts/test_session_orientation.py.
sys.modules["adherence_probe"] = probe
_spec.loader.exec_module(probe)


SURFACE = """\
# Contract

Intro line that belongs to no section.

## First Section

The first rule is that agents own the work completely.
A second sentence that should not be the anchor.

## Second Section

Attestation carries the operator's verbatim words unchanged.

## Third Section

Never bypass Gate 5 human attestation.
"""


class TestSectionExtraction(unittest.TestCase):
    """Sections and their byte offsets are read from the surface itself."""

    def test_sections_are_returned_in_document_order_with_byte_offsets(self):
        sections = probe.parse_sections(SURFACE)
        self.assertEqual(
            [s.section_id for s in sections],
            ["first-section", "second-section", "third-section"],
        )
        offsets = [s.offset for s in sections]
        self.assertEqual(offsets, sorted(offsets))

    def test_offset_is_the_byte_index_of_the_heading(self):
        sections = probe.parse_sections(SURFACE)
        raw = SURFACE.encode("utf-8")
        for section in sections:
            self.assertTrue(
                raw[section.offset :].startswith(b"## "),
                f"{section.section_id} offset does not land on its heading",
            )

    def test_offsets_are_measured_not_stored(self):
        """Growing an earlier section moves every later offset."""
        grown = SURFACE.replace(
            "A second sentence that should not be the anchor.",
            "A second sentence that should not be the anchor. " + ("pad " * 200),
        )
        before = {s.section_id: s.offset for s in probe.parse_sections(SURFACE)}
        after = {s.section_id: s.offset for s in probe.parse_sections(grown)}
        self.assertGreater(after["third-section"], before["third-section"])

    def test_anchor_is_the_first_body_sentence_not_the_heading(self):
        sections = {s.section_id: s for s in probe.parse_sections(SURFACE)}
        self.assertEqual(
            sections["first-section"].anchor,
            "The first rule is that agents own the work completely.",
        )

    def test_bold_lead_paragraph_is_prose_not_a_list_bullet(self):
        """``**Pattern:** ...`` opens with ``*`` but is a sentence, not a bullet.

        Measured against the real AGENTS.md: ``## Attestation`` leads with
        ``**Pattern:** ...`` and the first cut skipped it as a bullet, anchoring
        on a later sentence. The model then quoted the real lead and scored
        ``confabulated`` for being correct.
        """
        surface = "## Bold Lead\n\n**Pattern:** operators supply verbatim tokens.\n"
        self.assertEqual(
            probe.parse_sections(surface)[0].anchor,
            "**Pattern:** operators supply verbatim tokens.",
        )

    def test_a_table_led_section_yields_no_anchor(self):
        """No fair probe exists when the body opens with a table.

        Asking "quote its first sentence" of a section whose first line is a
        table row, then scoring against a prose sentence further down, marks a
        correct answer wrong. Such a section is EXCLUDED rather than scored —
        an unfair probe is worse than a missing row, because it produces a
        number that looks like evidence.
        """
        surface = "## Table Led\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\nProse arrives later here.\n"
        self.assertEqual(probe.parse_sections(surface)[0].anchor, "")

    def test_probe_is_skipped_when_there_is_no_anchor(self):
        surface = "## Table Led\n\n| a | b |\n|---|---|\n\nProse arrives later.\n"
        section = probe.parse_sections(surface)[0]
        self.assertFalse(probe.is_probeable(section))

    def test_probe_is_kept_when_the_body_leads_with_prose(self):
        section = probe.parse_sections(SURFACE)[0]
        self.assertTrue(probe.is_probeable(section))


class TestProbeDoesNotLeakTheAnswer(unittest.TestCase):
    """A probe carrying its own answer cannot fail. Assert it does not."""

    def test_question_never_contains_the_anchor_text(self):
        for section in probe.parse_sections(SURFACE):
            question = probe.build_probe(section)
            self.assertNotIn(
                section.anchor,
                question,
                f"probe for {section.section_id} leaks its expected answer",
            )

    def test_question_never_contains_any_answer_token(self):
        """Even a partial leak lets the model echo rather than recall.

        Scored against ``answer_tokens``, not every distinctive anchor token:
        the probe MUST name the heading to address the section, so a word the
        heading and the body share ("First" in ``## First Section`` above) is
        handed to the model for free and is therefore not evidence of recall.
        Excluding heading tokens is what keeps a model that merely echoes the
        question from scoring as recall.
        """
        for section in probe.parse_sections(SURFACE):
            question = probe.build_probe(section).lower()
            for token in probe.answer_tokens(section):
                self.assertNotIn(
                    token,
                    question,
                    f"probe for {section.section_id} leaks token {token!r}",
                )

    def test_answer_tokens_exclude_words_the_heading_gives_away(self):
        section = probe.parse_sections(SURFACE)[0]
        self.assertIn("first", probe.distinctive_tokens(section.anchor))
        self.assertNotIn("first", probe.answer_tokens(section))
        self.assertIn("agents", probe.answer_tokens(section))

    def test_echoing_the_heading_back_does_not_score_as_recall(self):
        section = probe.parse_sections(SURFACE)[0]
        self.assertEqual(probe.score(section, "The First Section section."), probe.CONFABULATED)

    def test_question_addresses_the_section_by_heading(self):
        section = probe.parse_sections(SURFACE)[0]
        self.assertIn("First Section", probe.build_probe(section))

    def test_question_offers_the_missing_escape(self):
        section = probe.parse_sections(SURFACE)[0]
        self.assertIn(probe.MISSING_TOKEN, probe.build_probe(section))


class TestScoring(unittest.TestCase):
    """Recall is scored on distinctive tokens, not on plausibility."""

    def setUp(self):
        self.section = probe.parse_sections(SURFACE)[0]

    def test_verbatim_answer_scores_recalled(self):
        verdict = probe.score(self.section, self.section.anchor)
        self.assertEqual(verdict, probe.RECALLED)

    def test_missing_token_scores_absent(self):
        verdict = probe.score(self.section, f"  {probe.MISSING_TOKEN}  ")
        self.assertEqual(verdict, probe.ABSENT)

    def test_plausible_confabulation_scores_confabulated(self):
        """Right topic, none of the distinctive tokens — not recall."""
        verdict = probe.score(self.section, "Agents should always finish their tasks.")
        self.assertEqual(verdict, probe.CONFABULATED)

    def test_partial_quote_with_enough_distinctive_tokens_scores_recalled(self):
        verdict = probe.score(self.section, "agents own the work completely")
        self.assertEqual(verdict, probe.RECALLED)

    def test_scoring_ignores_case_and_smart_punctuation(self):
        noisy = "“THE FIRST RULE IS THAT AGENTS OWN THE WORK COMPLETELY.”"
        self.assertEqual(probe.score(self.section, noisy), probe.RECALLED)

    def test_distinctive_tokens_exclude_stopwords(self):
        tokens = probe.distinctive_tokens("The first rule is that agents own the work")
        self.assertNotIn("the", tokens)
        self.assertNotIn("is", tokens)
        self.assertIn("agents", tokens)


class TestNegativeControl(unittest.TestCase):
    """A model that recalls a section that does not exist invalidates the run."""

    def test_control_section_is_not_present_in_the_surface(self):
        control = probe.negative_control(SURFACE)
        self.assertNotIn(control.title.lower(), SURFACE.lower())

    def test_control_is_stable_for_a_given_surface(self):
        self.assertEqual(
            probe.negative_control(SURFACE).title,
            probe.negative_control(SURFACE).title,
        )

    def test_absent_answer_on_the_control_keeps_the_run_valid(self):
        self.assertTrue(probe.control_passed(probe.ABSENT))

    def test_any_recall_on_the_control_invalidates_the_run(self):
        self.assertFalse(probe.control_passed(probe.RECALLED))
        self.assertFalse(probe.control_passed(probe.CONFABULATED))


class TestReport(unittest.TestCase):
    """The report is the deliverable: recall against byte position."""

    def _results(self):
        sections = probe.parse_sections(SURFACE)
        verdicts = [probe.RECALLED, probe.RECALLED, probe.ABSENT]
        return [
            probe.Result(section=s, verdict=v, answer="")
            for s, v in zip(sections, verdicts, strict=True)
        ]

    def test_report_orders_rows_by_byte_offset(self):
        rows = probe.build_report(self._results(), cap=None, control_ok=True)["rows"]
        self.assertEqual([r["offset"] for r in rows], sorted(r["offset"] for r in rows))

    def test_report_carries_the_recall_rate(self):
        report = probe.build_report(self._results(), cap=None, control_ok=True)
        self.assertAlmostEqual(report["recall_rate"], 2 / 3)

    def test_report_marks_rows_past_the_delivery_cap(self):
        results = self._results()
        cap = results[-1].section.offset - 1
        rows = probe.build_report(results, cap=cap, control_ok=True)["rows"]
        self.assertTrue(rows[-1]["past_cap"])
        self.assertFalse(rows[0]["past_cap"])

    def test_failed_control_marks_the_whole_run_invalid(self):
        report = probe.build_report(self._results(), cap=None, control_ok=False)
        self.assertFalse(report["valid"])

    def test_valid_run_reports_valid(self):
        report = probe.build_report(self._results(), cap=None, control_ok=True)
        self.assertTrue(report["valid"])

    def test_recall_rate_is_reported_separately_above_and_below_the_cap(self):
        results = self._results()
        cap = results[-1].section.offset - 1
        report = probe.build_report(results, cap=cap, control_ok=True)
        self.assertAlmostEqual(report["recall_rate_within_cap"], 1.0)
        self.assertAlmostEqual(report["recall_rate_past_cap"], 0.0)


if __name__ == "__main__":
    unittest.main()
