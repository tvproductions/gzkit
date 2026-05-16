ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.48-gz-adr-pool-triage
Evaluator: gz adr eval (deterministic)
Date: 2026-05-16

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 3 | 0.45 | No rationale language in Decision |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 3 | 0.30 | OBPI lane exceeds parent ADR lane |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.60/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| triage-prepass-contract | 4 | 4 | 2 | 4 | 3 | 3.4 |
| candidate-cognitive-pass | 4 | 4 | 2 | 4 | 3 | 3.4 |
| deterministic-renderer | 4 | 4 | 2 | 4 | 3 | 3.4 |
| blocked-foundation-filter | 4 | 4 | 2 | 4 | 3 | 3.4 |
| skill-surface-sync | 4 | 4 | 2 | 4 | 3 | 3.4 |
| docs-validation-fixtures | 4 | 4 | 2 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
