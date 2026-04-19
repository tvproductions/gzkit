ADR EVALUATION SCORECARD
========================

ADR: ADR-0.42.0-gz-preflight-health-orchestration
Evaluator: gz adr eval (deterministic)
Date: 2026-04-19

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 1 | 0.15 | Intent section is thin (<100 words); No before/current-state language in Intent; No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 1 | 0.15 | Decision section has no numbered items; No rationale language in Decision; Missing or thin Alternatives Considered section |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 1 | 0.10 | No source file path references in ADR; No exemplar/precedent language |

WEIGHTED TOTAL: 2.65/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| check-pipeline | 4 | 4 | 2 | 4 | 3 | 3.4 |
| auto-repair-tier | 4 | 4 | 2 | 4 | 3 | 3.4 |
| cli-surface | 4 | 4 | 2 | 4 | 3 | 3.4 |
| receipt-artifact | 4 | 4 | 2 | 4 | 3 | 3.4 |
| advisory-gate | 4 | 4 | 2 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[ ] GO
[x] CONDITIONAL GO
[ ] NO GO

ACTION ITEMS:
1. ADR weighted total 2.65 < 3.0 (GO threshold)
