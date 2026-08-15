ADR STRUCTURAL-COMPLETENESS SCORECARD
=====================================

ADR: ADR-0.37.0
Evaluator: gz adr eval (deterministic STRUCTURAL-COMPLETENESS lint)
Date: 2026-08-15

NOTE: This scorecard grades STRUCTURAL COMPLETENESS only — section
presence, depth, counts, and references. It is NOT a judgment of decision
SUBSTANCE or quality, and its verdict is NOT an authoritative quality GO.
Substance is graded only by recorded judge verdicts (see the Substance
channel below) or reported UNGRADED. Do NOT composite these scores with a
human substance review — they measure different things (GHI #624).

--- Structural Completeness (deterministic) ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| ontology-inverse-reach | 4 | 4 | 3 | 4 | 3 | 3.6 |
| airlock-seam-calibration | 4 | 4 | 4 | 4 | 3 | 3.8 |
| seam-accounting-predicate | 4 | 4 | 3 | 4 | 3 | 3.6 |
| transit-trailer-stamp | 4 | 4 | 3 | 4 | 3 | 3.6 |
| session-entry-door | 4 | 4 | 3 | 4 | 3 | 3.6 |
| transit-gate-flip | 4 | 4 | 3 | 4 | 3 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Substance (judge-graded; never derived from the scores above) ---

| Dimension | Grade | Source |
|-----------|-------|--------|
| Problem Substance | UNGRADED | no judge verdict recorded |
| Decision Substance | UNGRADED | no judge verdict recorded |

--- Persona Dispatch (mandated by the ceremony; never inferred) ---

| Persona | Independent input | Source |
|---------|-------------------|--------|
| spec-reviewer | NOT DISPATCHED | no dispatch receipt recorded |
| quality-reviewer | NOT DISPATCHED | no dispatch receipt recorded |
| narrator | NOT DISPATCHED | no dispatch receipt recorded |

DISPATCH MODE: SINGLE-DRIVER — 0 of 3 mandated personas produced receipted independent input.
This scorecard is NOT an independent review. A single driver scoring its
own scoring is the optimistic-bias defect `spec-reviewer`'s anti-traits
name, and it is why the ceremony mandates the dispatch (GHI #770).

--- Structural-Completeness Summary (NOT a quality/substance verdict) ---

[x] STRUCTURALLY COMPLETE
[ ] STRUCTURAL GAPS
[ ] STRUCTURALLY INCOMPLETE
