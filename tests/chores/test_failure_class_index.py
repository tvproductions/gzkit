"""Tests for the failure-class index (chore: failure-class-index).

Assertions derive from what the index is FOR — surfacing a recurrence chain
before the next instance is authored — not from a run of the code. The corpus
shapes exercised here are taken from real GHI class statements (#505, #554,
#537) so a change in extraction semantics fails rather than merely differs.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.insights.failure_classes import (
    build_index,
    extract_class_statement,
    load_snapshot,
    parse_entry,
    render_report,
    resolve_chains,
    summarize,
)

BODY = """## Observed

Something broke.

## Class of failure

Same bare-id class as GHIs #279 -> #305 -> #344. Any future emission path
reproduces it.

## Related

- nothing
"""


def _record(number: int, body: str, title: str = "t") -> dict[str, object]:
    return {"number": number, "title": title, "body": body}


class TestExtraction(unittest.TestCase):
    """The section is the author's diagnosis; extraction must not distort it."""

    def test_statement_stops_at_the_next_section(self):
        text = extract_class_statement(BODY)
        self.assertIsNotNone(text)
        assert text is not None
        self.assertIn("Same bare-id class", text)
        self.assertNotIn("Related", text)
        self.assertNotIn("Something broke", text)

    def test_absent_section_yields_none_not_empty_string(self):
        # A GHI with no diagnosis must be distinguishable from one whose
        # diagnosis is blank — 45 of 333 in the real corpus carry no section.
        self.assertIsNone(extract_class_statement("## Observed\n\nno diagnosis\n"))

    def test_missing_body_is_tolerated(self):
        self.assertIsNone(extract_class_statement(None))

    def test_markup_is_normalized_so_phrasing_matches_regardless_of_emphasis(self):
        body = "## Class of failure\n\n**Same class** as GHI #501.\n"
        text = extract_class_statement(body)
        assert text is not None
        self.assertIn("Same class as GHI #501", text)


class TestRecurrenceDetection(unittest.TestCase):
    """A declared recurrence is the signal; missing one defeats the surface."""

    def test_same_class_phrasing_declares_recurrence(self):
        entry = parse_entry(_record(505, BODY))
        assert entry is not None
        self.assertTrue(entry.declares_recurrence)
        self.assertEqual(entry.cites, (279, 305, 344))

    def test_ordinal_instance_phrasing_declares_recurrence(self):
        # Real shape from #554: "This is the 5th instance in 4 weeks".
        body = "## Class of failure\n\nThis is the 5th instance in 4 weeks: #358, #371.\n"
        entry = parse_entry(_record(554, body))
        assert entry is not None
        self.assertTrue(entry.declares_recurrence)

    def test_novel_defect_does_not_declare_recurrence(self):
        body = "## Class of failure\n\nA writer emits into a path with no declared owner.\n"
        entry = parse_entry(_record(769, body))
        assert entry is not None
        self.assertFalse(entry.declares_recurrence)
        self.assertEqual(entry.cites, ())

    def test_self_citation_is_not_a_link_to_itself(self):
        body = "## Class of failure\n\nSame class as GHI #600 and this issue #601.\n"
        entry = parse_entry(_record(601, body))
        assert entry is not None
        self.assertNotIn(601, entry.cites)

    def test_short_numbers_are_not_read_as_citations(self):
        body = "## Class of failure\n\nSame class; the #1 cause is drift across #512.\n"
        entry = parse_entry(_record(700, body))
        assert entry is not None
        self.assertEqual(entry.cites, (512,))


class TestChains(unittest.TestCase):
    """Chain depth is what makes a family visible before instance N+1."""

    def test_transitive_citations_form_one_chain(self):
        records = [
            _record(305, "## Class of failure\n\nSame class as GHI #279.\n"),
            _record(344, "## Class of failure\n\nSame class as GHI #305.\n"),
            _record(494, "## Class of failure\n\nSame class as GHI #344.\n"),
        ]
        chains = resolve_chains(build_index(records))
        self.assertEqual(len(chains), 1)
        self.assertEqual(chains[0].members, (279, 305, 344, 494))
        self.assertEqual(chains[0].depth, 4)

    def test_only_declaring_entries_contribute_edges(self):
        # A passing mention must not merge two unrelated families. This is the
        # over-merge the throwaway analysis hit; the contract is that the
        # author's recurrence phrasing makes the link, not any citation.
        records = [
            _record(600, "## Class of failure\n\nSame class as GHI #500.\n"),
            _record(601, "## Class of failure\n\nUnrelated cause; see #600 for context.\n"),
        ]
        chains = resolve_chains(build_index(records))
        self.assertEqual([c.members for c in chains], [(500, 600)])

    def test_declared_members_are_distinguished_from_cited_ancestors(self):
        records = [_record(505, BODY)]
        chain = resolve_chains(build_index(records))[0]
        self.assertEqual(chain.declared, (505,))
        self.assertIn(279, chain.members)

    def test_chains_are_ordered_deepest_first(self):
        records = [
            _record(300, "## Class of failure\n\nSame class as GHI #200.\n"),
            _record(401, "## Class of failure\n\nSame class as GHI #400.\n"),
            _record(402, "## Class of failure\n\nSame class as GHI #401.\n"),
        ]
        chains = resolve_chains(build_index(records))
        self.assertEqual(chains[0].depth, 3)
        self.assertEqual(chains[-1].depth, 2)


class TestSummary(unittest.TestCase):
    """The recurrence rate is the number a campaign box would be written against."""

    def test_rate_is_declaring_over_indexed_not_over_all_records(self):
        records = [
            _record(1, "## Class of failure\n\nSame class as GHI #900.\n"),
            _record(2, "## Class of failure\n\nA novel cause.\n"),
            _record(3, "## Observed\n\nno diagnosis section at all\n"),
        ]
        entries = build_index(records)
        stats = summarize(entries, resolve_chains(entries))
        self.assertEqual(stats["entries"], 2)
        self.assertEqual(stats["declaring_recurrence"], 1)
        self.assertEqual(stats["recurrence_rate"], 0.5)

    def test_empty_corpus_reports_zero_rather_than_dividing_by_zero(self):
        stats = summarize((), ())
        self.assertEqual(stats["entries"], 0)
        self.assertEqual(stats["recurrence_rate"], 0.0)


class TestFailSoft(unittest.TestCase):
    """A maintenance run reports 'nothing indexed'; it never crashes the chore."""

    def test_absent_snapshot_yields_empty_corpus(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(load_snapshot(Path(tmp) / "missing.json"), [])

    def test_malformed_snapshot_yields_empty_corpus(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertEqual(load_snapshot(path), [])

    def test_non_list_snapshot_yields_empty_corpus(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "obj.json"
            path.write_text(json.dumps({"number": 1}), encoding="utf-8")
            self.assertEqual(load_snapshot(path), [])


class TestReport(unittest.TestCase):
    """The report is what an operator reads before writing a campaign box."""

    def test_report_names_chain_members_and_marks_the_declarer(self):
        records = [_record(505, BODY, title="interview adr: bare adr_created")]
        entries = build_index(records)
        text = render_report(entries, resolve_chains(entries), min_depth=3)
        self.assertIn("#505", text)
        self.assertIn("#279", text)
        self.assertIn("interview adr", text)
        self.assertIn("depth 4", text)

    def test_report_states_absence_rather_than_rendering_an_empty_section(self):
        records = [_record(1, "## Class of failure\n\nA novel cause.\n")]
        entries = build_index(records)
        text = render_report(entries, resolve_chains(entries), min_depth=3)
        self.assertIn("_None._", text)


if __name__ == "__main__":
    unittest.main()
