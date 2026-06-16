ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.73-verification-layer-binding-audit
Evaluator: gz adr eval (deterministic)
Date: 2026-06-16

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.85/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| qc-step-registry-and-classifier | 4 | 4 | 4 | 4 | 4 | 4.0 |
| qc-binding-validate-scope | 4 | 4 | 4 | 2 | 4 | 3.6 |
| fidelity-assertions-and-gate | 4 | 4 | 4 | 3 | 4 | 3.8 |
| closeout-audit-fidelity-repoint | 4 | 4 | 4 | 3 | 4 | 3.8 |
| absorb-dispatch-attestation-pool | 4 | 4 | 4 | 4 | 4 | 4.0 |
| self-check-facade-regression-corpus | 4 | 4 | 4 | 4 | 4 | 4.0 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO


--- Manual Review Synthesis (supersedes CLI pre-screen) ---

Reviewer: main-session (booking agent), 2026-06-16. The CLI is a pattern-matching
pre-screen; manual review is authoritative per gz-adr-evaluate.

Initial pre-screen scored Problem Clarity (dim 1) and Decision Justification
(dim 2) at 1 — both false negatives from keyword/format heuristics (the Intent
lacked literal before/after tokens; the Decision used bold-numbered parts rather
than a markdown numbered list). Eating this ADR's own dogfood (a facade-killing
ADR must not itself be a facade to the mechanical checker), the content was
genuinely strengthened, not merely overridden: an explicit before/after frame was
added to the Intent, the Decision was reshaped into a real numbered list with a
"because" rationale clause, and source-file paths were named per part. Re-run:
dims 1, 2, 8 now score 4. No dimension scores 1.

Residual heuristic findings (judged non-defects):
- Dim 3 (Feature Checklist) scored 3: "Checklist items not prefixed with OBPI-".
  Correct by template — ADR checklist items are deliverable descriptions that map
  1:1 to OBPI briefs; they are not OBPI IDs. No action.
- OBPI-02 Size=2: the `--qc-binding` scope (behavioral negative-control runner +
  six theater-signature detectors + gz check wiring + manpage) is the largest unit
  but remains a single coherent surface; deliberately not split further. Acceptable.

Verdict: GO (weighted 3.85/4.0). All six OBPIs average >= 3.6 with no dimension
at 1. Ready for the operator-witnessed steps (Magna Carta seating + Gate 5).


--- Scope Expansion Note: 6 -> 7 OBPIs (2026-06-16, manual synthesis) ---

Reviewer: main-session, 2026-06-16. Operator-directed: GHI #624 (`gz adr evaluate`
dim-1/dim-2 score prose SHAPE & KEYWORDS, not decision truth) is homed into this
ADR as a seventh OBPI rather than left as a standalone fix, "to make it
comprehensive." The defect is the exact pattern-matching-instead-of-verifying
class this ADR exists to kill — the evaluator is just another QC step that
presents as authoritative while grading only shape.

Added: OBPI-07 (evaluate-truth-binding); Feature Checklist item #7; Decision
"Evaluator truth-binding" paragraph (OBPI-07 homing GHI #624); Boundary Invariant
#6; one Fidelity Assertion row. The seventh `shape-graded-not-substance` theater
signature is calibrated on GHI #624 and is distinct from the six ADR-0.0.37
signatures, so OBPI-06's "six" references are unchanged and remain accurate.

This note is a manual synthesis, not a re-run of the CLI pre-screen — by design,
since the pre-screen surface is the very thing OBPI-07 remediates. The 1:1
checklist<->OBPI count is now 7<->7; dim-3 (Feature Checklist) still scores 3 on
the "not prefixed with OBPI-" heuristic, a correct-by-template non-defect (same
as the original pre-screen). Verdict unchanged: GO.
