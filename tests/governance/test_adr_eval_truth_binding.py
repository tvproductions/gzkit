"""Evaluator truth-binding: substance over shape (OBPI-0.0.73-07, GHI #624).

`gz adr evaluate` dim-1 (Problem Clarity) and dim-2 (Decision Justification)
formerly graded prose SHAPE and KEYWORDS — `_has_keywords` substring membership
(before/after/because) plus a numbered-list regex. A facade ADR that stuffed the
keywords scored high; a rigorous ADR phrased without them was floored to 1. These
tests pin the truth-binding fix: scores reflect decision SUBSTANCE, never keyword
or format presence alone.

Each ADR fixture is authored to isolate the property under test:
- RIGOROUS_NO_KEYWORDS  — substantive, concretely grounded, BUT deliberately avoids
  the literal keywords "before"/"after"/"because" and uses no markdown numbered
  list in its Decision. A shape-grading scorer floors it; a substance-grading
  scorer does not.
- HOLLOW_KEYWORD_STUFFED — thin and ungrounded, BUT stuffs the keywords and a
  markdown numbered list. A shape-grading scorer lifts it; a substance-grading
  scorer does not.
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


class TestSubstanceNotShape(unittest.TestCase):
    """REQ-0.0.73-07-01 / REQ-0.0.73-07-02: dim-1/dim-2 grade decision substance."""

    @covers("REQ-0.0.73-07-01")
    def test_rigorous_keyword_free_adr_not_floored_dim1(self) -> None:
        # A rigorous, concretely-grounded Intent phrased without before/after
        # keywords must reflect its substance — not be floored to 1.
        score, findings = _score_problem_clarity(RIGOROUS_NO_KEYWORDS)
        self.assertGreaterEqual(
            score,
            3,
            f"Rigorous keyword-free Intent floored to {score}; findings={findings}",
        )

    @covers("REQ-0.0.73-07-01")
    def test_rigorous_keyword_free_adr_not_floored_dim2(self) -> None:
        # A deep Decision with weighed-and-rejected alternatives and honest negative
        # consequences, phrased without "because" and without a markdown numbered
        # list, must not be floored.
        score, findings = _score_decision_justification(RIGOROUS_NO_KEYWORDS)
        self.assertGreaterEqual(
            score,
            3,
            f"Rigorous keyword-free Decision floored to {score}; findings={findings}",
        )

    @covers("REQ-0.0.73-07-02")
    def test_keyword_stuffing_alone_does_not_lift_dim1(self) -> None:
        # Stuffing before/after keywords into a thin, ungrounded Intent must NOT
        # lift dim-1 to a passing score — keyword presence alone is not substance.
        score, _ = _score_problem_clarity(HOLLOW_KEYWORD_STUFFED)
        self.assertLess(
            score,
            3,
            f"Keyword stuffing alone lifted dim-1 to {score} (should stay < 3)",
        )

    @covers("REQ-0.0.73-07-02")
    def test_keyword_and_format_stuffing_alone_does_not_lift_dim2(self) -> None:
        # Stuffing "because" + a markdown numbered list into a thin Decision with no
        # real alternatives or consequences must NOT lift dim-2 to a passing score.
        score, _ = _score_decision_justification(HOLLOW_KEYWORD_STUFFED)
        self.assertLess(
            score,
            3,
            f"Keyword/format stuffing alone lifted dim-2 to {score} (should stay < 3)",
        )

    @covers("REQ-0.0.73-07-02")
    def test_rigorous_outscores_hollow_on_both_dims(self) -> None:
        # The discriminating property: substance beats shape. The rigorous ADR must
        # outscore the keyword-stuffed hollow one on both dimensions.
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
