"""The scorecard's Summary roll-up is fenced against the rows it summarizes.

`docs/governance/advisory-rules-audit.md` carries a count table summarizing the
rows beneath it -- a derived view living inside its own source, with no
regenerator (Architectural Boundary 6). Nothing read it, so it drifted twice in
opposite directions:

* It was last hand-stamped 2026-05-26 describing 69 rows of a 91-row scorecard.
* A 2026-08-08 re-measurement reported "12 Promotable + 2 Ambiguous" by counting
  *mentions* rather than *rows*: `grep -c 'Ambiguous'` returns exactly 2 -- the
  legend row and the Summary row itself, neither of which is a rule. That figure
  reached an operator-ratified campaign amendment as the completion criterion of
  the Movement C family-closure box, so a wrong count retargeted real work.

These tests pin the counting *semantics*, not the current figures: each asserts a
way the count can be wrong while still looking right. The figures themselves live
in the fenced table and are asserted by `gz validate --advisory-scorecard`.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits import audit_advisory_scorecard
from gzkit.governance.trust_audits.release import (
    _scorecard_row_scores,
    _summary_drift_errors,
)

_RULE_BODY = """<!-- rule-version: 1.2.3 -->

> **Rule version:** `1.2.3` -- sample.

## Invariant

**Something binding.**
"""


def _scorecard(rows: str, summary: str = "") -> str:
    """Return a scorecard document carrying *rows* and an optional roll-up."""
    doc = (
        "# Advisory Rules Audit\n\n"
        "| Score | Meaning |\n|---|---|\n"
        "| **Mechanical** | Already has a fail-closed check. |\n"
        "| **Promotable** | Could become mechanical. |\n"
        "| **Judgment** | Requires judgment by its nature. |\n"
        "| **Ambiguous** | Scope is unclear. |\n\n"
        "## Coverage Ledger\n\n"
        "| Rule file | Scored at rule-version |\n|---|---|\n"
        "| `sample.md` | `1.2.3` |\n\n"
        "## Scorecard\n\n"
        "### Sample (`.gzkit/rules/sample.md`)\n\n"
        "| # | Rule | Score | Notes |\n|---|------|-------|-------|\n"
        f"{rows}\n"
    )
    if summary:
        doc += f"\n## Summary\n\n| Score | Rows | % |\n|---|---|---|\n{summary}\n"
    return doc


class ScorecardRowCounting(unittest.TestCase):
    """What counts as a scored rule row, and what only looks like one."""

    def test_legend_and_summary_rows_are_not_rules(self) -> None:
        """The phantom `Ambiguous` rules: a score's own definition is not a member.

        The legend defines all four scores and the roll-up restates them. Counting
        either as a rule invents members for a score that has none -- which is how
        two `Ambiguous` rules entered a ratified campaign criterion when the
        scorecard has never contained one.
        """
        text = _scorecard(
            "| 1 | Something binding | **Judgment** | prose |",
            "| **Ambiguous** | 0 | 0% |",
        )
        self.assertEqual(_scorecard_row_scores(text)["Ambiguous"], 0)

    def test_escaped_pipe_in_a_cell_is_not_a_column_break(self) -> None:
        """Rows 22, 27 and 52 carry ``\\|`` inside a code span.

        Splitting the line on every `|` shifts the Score column rightward for
        exactly those rows, dropping them from the count. A three-row undercount
        is indistinguishable from a correct answer unless something asserts it.
        """
        text = _scorecard("| 1 | Use `str \\| None` not `Optional[str]` | **Mechanical** | ruff |")
        self.assertEqual(_scorecard_row_scores(text)["Mechanical"], 1)

    def test_a_score_named_only_in_the_notes_column_does_not_count(self) -> None:
        """Row 53 recounts that it *was* Promotable while scoring Mechanical today.

        Reading the whole line rather than the Score cell turns the audit's own
        record of a past re-score into a present member of the score it left.
        """
        text = _scorecard(
            "| 1 | Closed enum | **Mechanical** | Scored **Promotable** until `0.4.0`. |"
        )
        counts = _scorecard_row_scores(text)
        self.assertEqual(counts["Promotable"], 0)
        self.assertEqual(counts["Mechanical"], 1)

    def test_a_row_scoring_two_halves_counts_toward_both(self) -> None:
        """Row 65 scores changelog structure Mechanical and curation Judgment.

        Collapsing it to one score would report a rule as fully witnessed when
        half of it is explicitly advisory -- the precise conflation the third
        state exists to surface.
        """
        text = _scorecard(
            "| 1 | Changelog and notes | **Mechanical** (structure) / **Judgment** (curation) | . |"
        )
        counts = _scorecard_row_scores(text)
        self.assertEqual(counts["Mechanical"], 1)
        self.assertEqual(counts["Judgment"], 1)

    def test_rows_outside_the_scorecard_section_are_not_scored_rules(self) -> None:
        """`## Recommended promotion order` is also a numbered table.

        A document-wide row scan counts its rows as rules and inflates the total,
        which then makes every percentage wrong in a way no reader can see.
        """
        text = _scorecard("| 1 | Something binding | **Judgment** | prose |")
        text += (
            "\n## Recommended promotion order\n\n"
            "| # | Rule(s) | GHI | Summary | Landed as |\n|---|---|---|---|---|\n"
            "| 1 | 28 | #202 | Every CLI verb has a skill | **Mechanical** |\n"
        )
        self.assertEqual(_scorecard_row_scores(text)["Mechanical"], 0)


class SummaryDriftReporting(unittest.TestCase):
    """When the roll-up disagrees with its rows, and when it is silent."""

    def test_absent_roll_up_is_clean(self) -> None:
        """The check fences a claim that was made; it never demands one.

        Deleting the roll-up is a valid disposition -- there is then no
        transcribed count to go stale.
        """
        text = _scorecard("| 1 | Something binding | **Judgment** | prose |")
        self.assertEqual(_summary_drift_errors(text), [])

    def test_an_accurate_roll_up_is_clean(self) -> None:
        text = _scorecard(
            "| 1 | Something binding | **Judgment** | prose |\n"
            "| 2 | Something tractable | **Promotable** | no reader |",
            "| **Judgment** | 1 | 50% |\n| **Promotable** | 1 | 50% |",
        )
        self.assertEqual(_summary_drift_errors(text), [])

    def test_drift_names_the_score_and_both_figures(self) -> None:
        """The recovery prose must say which score, claimed what, against what.

        A bare "counts are wrong" forces the reader to recount all four to find
        the one that moved (`.gzkit/rules/guardrail-feedback-prose.md`).
        """
        text = _scorecard(
            "| 1 | Something tractable | **Promotable** | no reader |",
            "| **Promotable** | 9 | 90% |",
        )
        errors = _summary_drift_errors(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("Promotable says 9, rows show 1", errors[0].message)

    def test_a_score_the_roll_up_omits_is_not_invented(self) -> None:
        """Omitting a score from the roll-up is not the same as claiming zero.

        Only transcribed claims are checked, so a partial roll-up is judged on
        what it actually asserts.
        """
        text = _scorecard(
            "| 1 | Something binding | **Judgment** | prose |",
            "| **Promotable** | 0 | 0% |",
        )
        self.assertEqual(_summary_drift_errors(text), [])


class SummaryDriftThroughTheAudit(unittest.TestCase):
    """The drift arm reaches `gz validate --advisory-scorecard`, not just the helper."""

    def _run(self, summary: str) -> list[str]:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".gzkit" / "rules"
            rules.mkdir(parents=True)
            (rules / "sample.md").write_text(_RULE_BODY, encoding="utf-8")
            doc = root / "docs" / "governance"
            doc.mkdir(parents=True)
            (doc / "advisory-rules-audit.md").write_text(
                _scorecard("| 1 | Something binding | **Judgment** | prose |", summary),
                encoding="utf-8",
            )
            return [e.message for e in audit_advisory_scorecard(root)]

    def test_the_audit_reports_a_drifted_roll_up(self) -> None:
        messages = self._run("| **Judgment** | 42 | 100% |")
        self.assertTrue(any("Summary roll-up" in m for m in messages), messages)

    def test_the_audit_is_clean_on_an_accurate_roll_up(self) -> None:
        self.assertEqual(self._run("| **Judgment** | 1 | 100% |"), [])


if __name__ == "__main__":
    unittest.main()
