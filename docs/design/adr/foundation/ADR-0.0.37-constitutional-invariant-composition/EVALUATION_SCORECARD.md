ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.37-constitutional-invariant-composition
Evaluator: gz adr eval (deterministic)
Date: 2026-05-06

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.60/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| invariant-schema-and-registry | 4 | 4 | 4 | 4 | 3 | 3.8 |
| composition-renderer | 4 | 4 | 3 | 4 | 3 | 3.6 |
| composition-drift-validator | 4 | 4 | 3 | 4 | 3 | 3.6 |
| brief-structural-schema | 4 | 4 | 4 | 4 | 3 | 3.8 |
| brief-reconcile-engine | 4 | 4 | 3 | 4 | 3 | 3.6 |
| brief-reconcile-cli | 4 | 4 | 3 | 4 | 3 | 3.6 |
| pipeline-stage1-gate | 4 | 4 | 3 | 4 | 3 | 3.6 |
| obpi-complete-gate | 4 | 4 | 4 | 4 | 3 | 3.8 |
| agents-md-migration | 4 | 4 | 3 | 4 | 4 | 3.8 |
| doctrine-refresh | 4 | 4 | 3 | 4 | 3 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
