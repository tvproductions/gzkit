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


_PYPROJECT = """[tool.ruff.lint]
select = ["E", "F", "BLE"]
ignore = ["D203"]
"""


class MechanicalRowsCitingRuffCodes(unittest.TestCase):
    """A **Mechanical** row naming a ruff code must name one that actually runs.

    The Movement C rules arm found four rows asserting enforcement that did not
    exist, and named the class: *a false Mechanical row is strictly worse than a
    Promotable one*. Promotable is honest -- it says no witness yet. A Mechanical
    row naming a lint rule that is not enabled reports green while blind, and the
    family-closure criterion counts only Promotable, so driving that count to zero
    leaves every false row untouched and makes the number look better.

    Row 18 claimed "ruff BLE001 enforces" with `BLE` absent from
    `[tool.ruff.lint] select`; six live violations sat unreported, one behind a
    `# noqa: BLE0001` typo that suppressed nothing and *could not be noticed while
    the rule was off*. All six wrong rows were found by opening the enforcement
    surface by hand, because nothing in gzkit compares a row's claim against the
    thing it names.

    This is the narrow tractable arm of that gap: a row cannot claim a ruff code
    that ruff would not run. It clears the § Recommended promotion order freeze on
    named observed drift, not on a backlog.
    """

    def _run(self, row: str, *, pyproject: str | None = _PYPROJECT) -> list[str]:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".gzkit" / "rules"
            rules.mkdir(parents=True)
            (rules / "sample.md").write_text(_RULE_BODY, encoding="utf-8")
            doc = root / "docs" / "governance"
            doc.mkdir(parents=True)
            (doc / "advisory-rules-audit.md").write_text(_scorecard(row), encoding="utf-8")
            if pyproject is not None:
                (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
            return [e.message for e in audit_advisory_scorecard(root)]

    def test_a_mechanical_row_citing_an_unselected_code_fails(self) -> None:
        """Row 18's exact shape, before `BLE` was added to the select list."""
        messages = self._run("| 1 | No bare except | **Mechanical** | ruff PLC0415 enforces |")
        self.assertTrue(any("PLC0415" in m for m in messages), messages)

    def test_a_mechanical_row_citing_a_selected_code_is_clean(self) -> None:
        self.assertEqual(
            self._run("| 1 | No bare except | **Mechanical** | ruff BLE001 enforces |"),
            [],
        )

    def test_a_selected_code_that_is_then_ignored_is_not_reachable(self) -> None:
        """`select = ["D"]` plus `ignore = ["D203"]` means D203 does not run.

        Reachability is the conjunction, not the select list alone. A row could
        otherwise cite a code whose family is selected while the code itself is
        switched off one table down -- the same report-green-while-blind state,
        arrived at from the other direction.
        """
        messages = self._run("| 1 | Docstring shape | **Mechanical** | ruff D203 enforces |")
        self.assertTrue(any("D203" in m for m in messages), messages)

    def test_a_judgment_row_may_name_a_disabled_code(self) -> None:
        """Naming a code you are NOT claiming to enforce is the honest posture.

        `.gzkit/rules/pythonic.md` § Imports records "PLC0415 is not enabled" with
        its 138-violation measurement, and scorecard row 23 carries that as
        **Judgment**. Flagging it would punish the disclosure this whole family
        exists to produce -- the check must fire on the CLAIM, never on the code.
        """
        self.assertEqual(
            self._run("| 1 | No lazy imports | **Judgment** | ruff PLC0415 is not enabled |"),
            [],
        )

    def test_a_non_ruff_code_shape_is_not_read_as_a_ruff_code(self) -> None:
        """`MD013` is markdownlint. Without the ruff anchor it is not this scope's.

        Extraction is anchored on the row mentioning ruff at all, because the
        bare code shape (`[A-Z]{1,4}` + digits) is shared by markdownlint,
        pydocstyle and others. An unanchored scan would invent findings against
        tools this project configures elsewhere.
        """
        self.assertEqual(
            self._run("| 1 | Line length | **Mechanical** | markdownlint MD013 configured |"),
            [],
        )

    def test_an_unreadable_ruff_config_reports_nothing(self) -> None:
        """No pyproject means no reachability answer -- and no invented one.

        Silence here is correct rather than lenient: the check's whole subject is
        whether a claim matches the config, so with no config there is no
        disagreement to report. `--distribution` covers a missing pyproject.
        """
        self.assertEqual(
            self._run(
                "| 1 | No bare except | **Mechanical** | ruff PLC0415 enforces |",
                pyproject=None,
            ),
            [],
        )


class PromotableAssignedInProse(unittest.TestCase):
    """A clause's score is assigned in a Scorecard ROW, never in prose about it.

    The rules arm drove the Scorecard's Promotable column to zero and the Summary
    roll-up is fenced against those rows. Three prose sites survived both, still
    asserting a live Promotable band the fenced table denies:

    * `**Invariant #10a**` ("When a skill step names a tool, invoke it in the same
      turn") declared **promotable** with no scorecard row at ALL -- a *skill*
      mandate in the forbidden third state, invisible to the criterion because it
      was never a row to count.
    * "The remaining Promotable band (Invariants 2/3 of the tool-skill-runbook
      rule, lazy imports, ...)" -- rows 29, 30 and 23 all read **Judgment**.
    * "Invariants 2 and 3 ... (rows 29/30 above) remain Promotable" -- naming the
      very rows that contradict it.

    This is Architectural Boundary 6 one surface over from the Summary table: a
    second, unfenced authority on scores. Fencing the roll-up while leaving prose
    free to assign scores would have moved the defect rather than closed it.

    Scoped to **Promotable** deliberately. It is the third state the family-closure
    criterion counts, and a Mechanical/Judgment narration (the promotion-wave
    paragraph cites a dozen) is history, not a live classification.
    """

    def _run(self, extra: str) -> list[str]:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".gzkit" / "rules"
            rules.mkdir(parents=True)
            (rules / "sample.md").write_text(_RULE_BODY, encoding="utf-8")
            doc = root / "docs" / "governance"
            doc.mkdir(parents=True)
            body = _scorecard("| 1 | Something binding | **Judgment** | prose |")
            (doc / "advisory-rules-audit.md").write_text(f"{body}\n{extra}\n", encoding="utf-8")
            return [e.message for e in audit_advisory_scorecard(root)]

    def test_prose_scoring_a_named_invariant_is_refused(self) -> None:
        """Line 210's exact shape: a named clause given a score outside any row."""
        messages = self._run(
            "**Invariant #10a** (skill-tool-invoke-same-turn) is **promotable** -- "
            "could be detected via hook analysis."
        )
        self.assertTrue(any("Invariant #10a" in m or "Promotable" in m for m in messages), messages)

    def test_prose_naming_rows_that_contradict_it_is_refused(self) -> None:
        """Line 421's shape: prose citing the very rows that disagree with it."""
        messages = self._run(
            "Invariants 2 and 3 of the tool-skill-runbook rule (rows 29/30 above) "
            "remain Promotable."
        )
        self.assertTrue(messages, "prose asserting a live Promotable band must be refused")

    def test_prose_about_the_score_itself_is_not_a_score_assignment(self) -> None:
        """The fenced Summary's own conditional must survive.

        "A row returning to **Promotable** means a clause was found declaring a
        discipline with neither a witness nor an admission" explains what the
        score MEANS. It assigns it to nothing, and it is the sentence that makes
        the empty third state legible. A fence that cost this sentence would be
        trading the explanation for the enforcement.
        """
        self.assertEqual(
            self._run(
                "A row returning to **Promotable** means a clause was found declaring "
                "a discipline with neither a witness nor an admission."
            ),
            [],
        )

    def test_a_scorecard_row_may_narrate_its_own_promotable_history(self) -> None:
        """Inside the Scorecard, "Scored **Promotable** until `0.4.0`" is the record.

        Rows 53, 60a, 61 and 62 each recount the score they used to carry and why
        it moved. That narration is how a reader tells a corrected row from one
        that was always right, so the fence stops at the Scorecard boundary.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".gzkit" / "rules"
            rules.mkdir(parents=True)
            (rules / "sample.md").write_text(_RULE_BODY, encoding="utf-8")
            doc = root / "docs" / "governance"
            doc.mkdir(parents=True)
            (doc / "advisory-rules-audit.md").write_text(
                _scorecard(
                    "| 53 | Abandon categories are closed | **Mechanical** | "
                    "Scored **Promotable** until `0.4.0`; row 53 was corrected when "
                    "OBPI-0.0.41-02 landed. |"
                ),
                encoding="utf-8",
            )
            self.assertEqual([e.message for e in audit_advisory_scorecard(root)], [])


if __name__ == "__main__":
    unittest.main()
