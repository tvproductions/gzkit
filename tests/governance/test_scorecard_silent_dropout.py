"""A scorecard row that looks scored must actually be scored.

`_scorecard_row_scores` counts a row by finding `**Mechanical**` (or a sibling)
in its Score cell. A row whose Score cell is malformed is not counted -- and it
stays on the page looking scored. Every per-score check and every total then
describes a corpus one row smaller than the one a reader sees.

The scorecard has already been bitten by exactly this: rows 22, 27 and 52 carry
`\\|` inside code spans, and before `_CELL_SPLIT_RE` existed a naive `split("|")`
read those as column breaks and dropped all three. `_CELL_SPLIT_RE`'s own comment
names the shape -- *"a three-row undercount that looks exactly like a correct
answer"*.

`_summary_drift_errors` does NOT cover this. It compares the roll-up against the
parsed rows, so a dropout moves both numbers as soon as someone corrects the
Summary to match: fence and defect agree, and the row is silently gone. The
dropout witness asserts the prior property -- that the parse saw everything the
page presents.

These tests are the reason the classification cells were NOT migrated to JSON
(operator ruling 2026-08-16, after measurement): the residual risk was silent
dropout, so the proportionate answer is to witness dropout, leaving each verdict
welded to the rationale that justifies it.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.governance.trust_audits.release import (
    _scorecard_row_scores,
    _silent_dropout_errors,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCORECARD = REPO_ROOT / "docs" / "governance" / "advisory-rules-audit.md"

_HEAD = "\n## Scorecard\n\n| # | Rule | Score | Notes |\n|---|---|---|---|\n"


def _doc(*rows: str) -> str:
    return _HEAD + "\n".join(rows) + "\n\n## Next section\n"


class TheLiveScorecardHasNoDropouts(unittest.TestCase):
    """The corpus itself, which is what the check is deployed to protect."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SCORECARD.read_text(encoding="utf-8")

    def test_no_row_is_presented_as_scored_without_a_score(self) -> None:
        self.assertEqual(_silent_dropout_errors(self.text), [])

    def test_the_parse_sees_the_rows_the_page_presents(self) -> None:
        """A total of zero would satisfy the check above vacuously.

        Pins that the corpus is genuinely being counted, so the dropout witness
        is guarding a live parse rather than an empty one.
        """
        self.assertGreater(sum(_scorecard_row_scores(self.text).values()), 100)


class MalformedScoreCellsAreCaught(unittest.TestCase):
    """Each shape that silently removes a row from the count."""

    def test_a_row_with_no_score_at_all_is_flagged(self) -> None:
        errors = _silent_dropout_errors(_doc("| 1 | some rule | | notes |"))
        self.assertEqual(len(errors), 1)
        self.assertIn("1", errors[0].message)

    def test_an_unbolded_score_is_flagged(self) -> None:
        """`Mechanical` and `**Mechanical**` read identically to a human."""
        self.assertEqual(len(_silent_dropout_errors(_doc("| 2 | r | Mechanical | n |"))), 1)

    def test_a_misspelled_score_is_flagged(self) -> None:
        self.assertEqual(len(_silent_dropout_errors(_doc("| 3 | r | **Mechnical** | n |"))), 1)

    def test_an_unescaped_pipe_shifting_the_columns_is_flagged(self) -> None:
        """The observed historical defect (rows 22, 27, 52), reproduced.

        A literal `|` inside a code span in an earlier cell shifts the Score
        cell rightward. The row still renders as a scorecard row, and vanishes
        from every count.
        """
        row = "| 4 | takes `str | None` | **Mechanical** | notes |"
        self.assertEqual(len(_silent_dropout_errors(_doc(row))), 1)

    def test_the_same_row_with_the_pipe_escaped_is_clean(self) -> None:
        """The negative pole: escaping is the fix the message prescribes."""
        row = r"| 4 | takes `str \| None` | **Mechanical** | notes |"
        self.assertEqual(_silent_dropout_errors(_doc(row)), [])

    def test_every_dropout_is_named_not_just_counted(self) -> None:
        """An operator cannot fix rows the message will not identify."""
        errors = _silent_dropout_errors(
            _doc("| 7 | a | | n |", "| 9 | b | **Judgment** | n |", "| 11 | c | Judgment | n |")
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("7", errors[0].message)
        self.assertIn("11", errors[0].message)


class WellFormedRowsAreNotFlagged(unittest.TestCase):
    """The check must not fire on the shapes the scorecard legitimately uses."""

    def test_each_of_the_four_scores_is_recognised(self) -> None:
        for score in ("Mechanical", "Promotable", "Judgment", "Ambiguous"):
            with self.subTest(score=score):
                self.assertEqual(_silent_dropout_errors(_doc(f"| 1 | r | **{score}** | n |")), [])

    def test_a_lettered_row_id_is_recognised(self) -> None:
        """Ids carry suffixes (`6a`, `17h`, `60a`) and must not read as unscored."""
        self.assertEqual(_silent_dropout_errors(_doc("| 17h | r | **Promotable** | n |")), [])

    def test_a_row_scoring_two_halves_is_clean(self) -> None:
        """Row 65 scores its halves separately; both live in one Score cell."""
        row = "| 65 | changelog + notes | **Mechanical** / **Judgment** | n |"
        self.assertEqual(_silent_dropout_errors(_doc(row)), [])

    def test_rows_outside_the_scorecard_section_are_not_inspected(self) -> None:
        """`## Recommended promotion order` is also a numbered table.

        Scanning document-wide would report its rows as unscored rules, which is
        the slicing bug `_scorecard_section` exists to prevent.
        """
        text = _doc("| 1 | r | **Judgment** | n |") + "\n| 1 | promotion candidate | high |\n"
        self.assertEqual(_silent_dropout_errors(text), [])


if __name__ == "__main__":
    unittest.main()
