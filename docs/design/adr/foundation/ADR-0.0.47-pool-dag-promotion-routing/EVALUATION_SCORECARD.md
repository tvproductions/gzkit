ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.47-pool-dag-promotion-routing
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
| relationship-frontmatter-schema | 4 | 4 | 2 | 4 | 3 | 3.4 |
| pool-graph-builder | 4 | 4 | 2 | 4 | 3 | 3.4 |
| pool-graph-cli | 4 | 4 | 2 | 4 | 3 | 3.4 |
| promote-dependency-guard | 4 | 4 | 3 | 4 | 3 | 3.6 |
| pool-backfill-migration | 4 | 4 | 2 | 4 | 3 | 3.4 |
| next-pool-recommendation | 4 | 4 | 2 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
