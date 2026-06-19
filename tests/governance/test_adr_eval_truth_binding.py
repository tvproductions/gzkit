"""Evaluator truth-binding: structural completeness, never substance (OBPI-0.0.73-07).

The repudiated GHI #624 "fix" CLAIMED `gz adr evaluate` dim-1 (Problem Clarity)
and dim-2 (Decision Justification) graded decision SUBSTANCE — while the bodies
graded shape (word-count, keyword regex). The honest contract pinned here: these
deterministic dimensions grade STRUCTURAL COMPLETENESS only (section presence and
depth). They make NO substance claim; substance is graded solely by the separate
judge channel (`gzkit.adr_eval_substance`) or reported UNGRADED — never derived
from the prose. See `tests/test_adr_eval_substance.py` for the substance-channel
contract; this file pins that the structural scorers stay honestly structural.

Each ADR fixture isolates STRUCTURAL completeness:
- RIGOROUS_NO_KEYWORDS  — structurally complete: deep sections, concrete
  references, an Alternatives section naming rejections, a Negative-consequences
  subsection. Scores high on structural completeness (honestly — it IS complete).
- HOLLOW_KEYWORD_STUFFED — structurally incomplete: one-sentence sections, no
  references, no Alternatives/Consequences sections. Keyword stuffing does not
  manufacture the missing structure, so it scores low — and neither score is a
  substance verdict.
"""

from __future__ import annotations

import unittest

# Import the package entry point first: it resolves the adr_eval <-> adr_eval_scoring
# import cycle (production code always enters via adr_eval, never adr_eval_scoring).
import gzkit.adr_eval  # noqa: F401
from gzkit.adr_eval_scoring import (
    _score_decision_justification,
    _score_problem_clarity,
)
from gzkit.governance.trust_audits.qc_binding import (
    THEATER_SIGNATURES,
    _check_theater_signatures,
)
from gzkit.qc_binding import QCStep, build_qc_registry
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# ADR fixtures
# ---------------------------------------------------------------------------

# Rigorous: deep, concretely grounded (paths, `code`, GHI ref), two articulated
# states, weighed-and-rejected alternatives, honest negative consequences. Phrased
# WITHOUT "before"/"after"/"because"; Decision uses bold-numbered parts, NOT a
# markdown numbered list (no leading "1." line).
RIGOROUS_NO_KEYWORDS = """\
---
id: ADR-9.9.9-rigorous-keyword-free
lane: heavy
---

# ADR-9.9.9-rigorous-keyword-free: Rigorous Keyword Free

## Intent

The reconciliation cache in `src/gzkit/reconcile.py` recomputes every artifact
relationship on each invocation, so a 400-artifact tree spends nine seconds
walking the graph that GHI #511 already proved is stable between commits. Operators
running `gz state` in a tight loop pay that cost repeatedly with no benefit, and the
cache file `.gzkit/state-cache.json` is written but never read. The target state
makes `gz state` read the committed cache when the tree hash matches and recompute
only on a genuine change, so the common path is a single hash comparison rather than
a full graph walk. This shifts the dominant cost from O(artifacts) to O(1) for the
unchanged-tree case, which is the case operators hit most.

## Decision

**Part one** — `gz state` computes a content hash of the artifact tree and compares
it against the hash stored alongside `.gzkit/state-cache.json`; a match short-circuits
to the cached relationship graph. **Part two** — a cache miss recomputes the graph and
rewrites both the cache and its hash within a single atomic write in `reconcile.py`,
so a crash mid-write cannot leave a torn cache. The hash covers artifact paths and
their frontmatter, the inputs the relationship graph actually depends on, drawn from
the dependency surface `gz state` already reads today.

## Alternatives Considered

1. **(a) mtime-based invalidation.** Rejected: mtime is unreliable across `git`
   checkouts and clones, which reset timestamps and would silently serve a stale graph.
2. **(b) an in-memory LRU instead of a committed cache.** Rejected: it discards the
   speedup across process boundaries, and `gz state` is invoked fresh per command, so
   an in-memory cache never survives to the next call.

## Consequences

### Positive

1. The unchanged-tree path collapses to a single hash comparison.

### Negative

1. A hash-collision or a bug in the tree-hash function serves a stale graph; the
   mitigation is a `--no-cache` escape hatch and a hash that covers all graph inputs.
"""

# Hollow: thin, ungrounded — no paths, no `code`, no issue refs, one short sentence
# per section, no real alternatives, no consequences. BUT stuffs the dim-1 keywords
# (before/after) and dim-2 keyword (because) and a markdown numbered list in Decision.
HOLLOW_KEYWORD_STUFFED = """\
---
id: ADR-9.9.8-hollow-keyword-stuffed
lane: heavy
---

# ADR-9.9.8-hollow-keyword-stuffed: Hollow Keyword Stuffed

## Intent

Before this change the current existing thing was bad and after this change the
target outcome will be good because it should be better.

## Decision

1. We will do the thing because the rationale is that the reason is good.

## Alternatives Considered

None.

## Consequences

It will be fine.
"""


class TestStructuralCompletenessNotSubstance(unittest.TestCase):
    """REQ-0.0.73-07-01 / REQ-0.0.73-07-02: dim-1/dim-2 grade structural completeness.

    These dimensions are honest STRUCTURAL-COMPLETENESS signals — they reward a
    section that is present, deep, and carries the expected sub-structure. They
    are NOT substance verdicts: a high score means "structurally complete," never
    "the problem is clearly understood" or "the decision is well justified." That
    the score tracks structure (not keyword presence) is the property pinned here;
    the guarantee that shape never produces a SUBSTANCE grade lives in
    tests/test_adr_eval_substance.py.
    """

    @covers("REQ-0.0.73-07-01")
    def test_structurally_complete_intent_scores_high(self) -> None:
        # A deep Intent with concrete references and multiple substantive sentences
        # is structurally complete — it scores high on the completeness signal.
        score, findings = _score_problem_clarity(RIGOROUS_NO_KEYWORDS)
        self.assertGreaterEqual(
            score, 3, f"Structurally-complete Intent scored {score}; findings={findings}"
        )

    @covers("REQ-0.0.73-07-01")
    def test_structurally_complete_decision_scores_high(self) -> None:
        # A deep Decision with an Alternatives section naming rejections and a
        # Negative-consequences subsection is structurally complete.
        score, findings = _score_decision_justification(RIGOROUS_NO_KEYWORDS)
        self.assertGreaterEqual(
            score, 3, f"Structurally-complete Decision scored {score}; findings={findings}"
        )

    @covers("REQ-0.0.73-07-02")
    def test_keyword_stuffing_does_not_manufacture_structure_dim1(self) -> None:
        # A one-sentence Intent with no references is structurally incomplete;
        # stuffing before/after keywords does not manufacture the missing depth.
        score, _ = _score_problem_clarity(HOLLOW_KEYWORD_STUFFED)
        self.assertLess(score, 3, f"Keyword stuffing manufactured structure: dim-1 scored {score}")

    @covers("REQ-0.0.73-07-02")
    def test_keyword_stuffing_does_not_manufacture_structure_dim2(self) -> None:
        # A thin Decision with no Alternatives/Consequences sections is structurally
        # incomplete; "because" + a numbered list does not supply the missing sections.
        score, _ = _score_decision_justification(HOLLOW_KEYWORD_STUFFED)
        self.assertLess(
            score, 3, f"Keyword/format stuffing manufactured structure: dim-2 scored {score}"
        )

    @covers("REQ-0.0.73-07-02")
    def test_structural_score_tracks_structure_not_keywords(self) -> None:
        # The discriminator is STRUCTURE, not keyword presence: the structurally
        # complete ADR outscores the structurally incomplete one — and this is a
        # completeness claim, NOT a substance verdict (substance stays UNGRADED).
        self.assertGreater(
            _score_problem_clarity(RIGOROUS_NO_KEYWORDS)[0],
            _score_problem_clarity(HOLLOW_KEYWORD_STUFFED)[0],
        )
        self.assertGreater(
            _score_decision_justification(RIGOROUS_NO_KEYWORDS)[0],
            _score_decision_justification(HOLLOW_KEYWORD_STUFFED)[0],
        )


class TestEvaluatorSelfRegistration(unittest.TestCase):
    """REQ-0.0.73-07-03: gz adr evaluate self-registers as an advisory QC step."""

    @covers("REQ-0.0.73-07-03")
    def test_adr_evaluate_registered_as_advisory(self) -> None:
        registry = build_qc_registry()
        evaluate_steps = [s for s in registry if s.wired_into == ["gz adr evaluate"]]
        self.assertEqual(
            len(evaluate_steps),
            1,
            f"Expected exactly one self-registered gz-adr-evaluate QC step, "
            f"found {len(evaluate_steps)}",
        )
        step = evaluate_steps[0]
        self.assertEqual(step.binding, "advisory")

    @covers("REQ-0.0.73-07-03")
    def test_advisory_evaluator_is_binding_honest(self) -> None:
        # An advisory step is not required to fail a negative control; the qc-binding
        # audit must NOT flag it as a binding-mismatch (it carries no theater flags
        # and does not claim `bound` enforcement it cannot deliver).
        registry = build_qc_registry()
        step = next(s for s in registry if s.wired_into == ["gz adr evaluate"])
        self.assertEqual(_check_theater_signatures(step), [])


class TestEvaluatorOutputNeverPresentsShapeAsSubstance(unittest.TestCase):
    """REQ-0.0.73-07-03 / REQ-0.0.73-07-06: self-binding regression guard.

    Pins the eradication: a rendered scorecard must declare structural-completeness
    scope, carry the do-not-composite disclaimer, render a distinct Substance channel,
    and never present an authoritative quality 'GO'. A revert to the facade framing
    fails here, in gz check.
    """

    def _render(self) -> str:
        from gzkit.adr_eval import (
            AdrEvalResult,
            DimensionScore,
            EvalVerdict,
            ObpiDimensionScores,
            render_scorecard_markdown,
        )
        from gzkit.adr_eval_substance import ungraded

        result = AdrEvalResult(
            adr_id="ADR-9.9.9-guard",
            adr_dimensions=[
                DimensionScore(dimension="Problem Clarity", weight=0.15, score=4, weighted=0.6)
            ],
            adr_weighted_total=3.55,
            obpi_scores=[
                ObpiDimensionScores(
                    obpi_id="OBPI-9.9.9-01",
                    independence=4,
                    testability=4,
                    value=4,
                    size=4,
                    clarity=4,
                    average=4.0,
                )
            ],
            verdict=EvalVerdict.GO,
            action_items=[],
            timestamp="2026-06-19T00:00:00+00:00",
            substance=[ungraded("Problem Substance"), ungraded("Decision Substance")],
        )
        return render_scorecard_markdown(result)

    @covers("REQ-0.0.73-07-03")
    def test_scorecard_declares_structural_scope_and_disclaimer(self) -> None:
        md = self._render()
        self.assertIn("STRUCTURAL-COMPLETENESS", md)
        self.assertIn("NOT a judgment of decision", md)
        self.assertIn("Substance", md)
        # The honest verdict label, never a bare authoritative quality GO.
        self.assertIn("STRUCTURALLY COMPLETE", md)

    @covers("REQ-0.0.73-07-06")
    def test_scorecard_substance_is_ungraded_not_derived_from_score(self) -> None:
        md = self._render()
        # A 3.55 structural score must NOT manufacture a substance grade.
        self.assertIn("UNGRADED", md)
        self.assertNotIn("[x] GO\n", md)


class TestShapeGradedTheaterSignature(unittest.TestCase):
    """REQ-0.0.73-07-04: the seventh theater signature is detected, not silently passed."""

    @covers("REQ-0.0.73-07-04")
    def test_shape_graded_not_substance_is_a_canonical_signature(self) -> None:
        self.assertIn("shape-graded-not-substance", THEATER_SIGNATURES)

    @covers("REQ-0.0.73-07-04")
    def test_shape_graded_step_is_detected(self) -> None:
        planted = QCStep(
            id="shape-graded-evaluate-check",
            name="Shape Graded Evaluate Check",
            kind="audit",
            subject="docs/",
            binding="advisory",
            wired_into=["gz adr evaluate"],
            theater_flags=["shape-graded-not-substance"],
            enforcement_locus="python_function",
        )
        errors = _check_theater_signatures(planted)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("shape-graded-not-substance" in e.message for e in errors),
            f"Expected shape-graded-not-substance detected, got: {[e.message for e in errors]}",
        )


if __name__ == "__main__":
    unittest.main()
