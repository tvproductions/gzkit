ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.50
Evaluator: gz adr eval (deterministic)
Date: 2026-05-18

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No exemplar/precedent language |

WEIGHTED TOTAL: 3.45/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| validation-pipeline-orchestrator-skill | 4 | 4 | 3 | 4 | 4 | 3.8 |
| redteam-verifier-persona-and-dispatch | 4 | 4 | 3 | 4 | 3 | 3.6 |
| redteam-receipt-schema-and-goal-convergence | 4 | 4 | 3 | 4 | 3 | 3.6 |
| validation-pipeline-validators-fail-closed | 4 | 4 | 3 | 4 | 3 | 3.6 |
| gz-status-next-action-and-doctrine | 4 | 4 | 3 | 4 | 3 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
