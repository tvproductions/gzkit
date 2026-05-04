ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.26
Evaluator: gz adr eval (deterministic)
Date: 2026-05-04

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 1 | 0.10 | No source file path references in ADR; No exemplar/precedent language |

WEIGHTED TOTAL: 3.70/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| persist-evaluation-events | 4 | 4 | 2 | 3 | 4 | 3.4 |
| justify-binding-gate | 4 | 4 | 4 | 3 | 4 | 3.8 |
| clustering-chore | 4 | 4 | 4 | 4 | 4 | 4.0 |
| ghi-promotion-and-trailer | 4 | 4 | 4 | 2 | 4 | 3.6 |
| bdd-coverage | 4 | 4 | 3 | 3 | 4 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO

