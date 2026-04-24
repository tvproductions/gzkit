ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.21
Evaluator: gz adr eval (deterministic)
Date: 2026-04-24

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
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 4.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| physical-migration | 4 | 4 | 4 | 4 | 3 | 3.8 |
| config-schema-paths-chores | 4 | 4 | 4 | 4 | 3 | 3.8 |
| wheel-packaging-chores-data | 4 | 4 | 4 | 4 | 3 | 3.8 |
| resolver-with-fallback | 4 | 4 | 4 | 4 | 3 | 3.8 |
| scaffold-core-chores | 4 | 4 | 4 | 3 | 3 | 3.6 |
| rule-and-doc-updates | 4 | 4 | 4 | 2 | 3 | 3.4 |
| bdd-chores-distribution | 4 | 4 | 4 | 4 | 4 | 4.0 |
| layout-validator | 4 | 4 | 4 | 3 | 3 | 3.6 |
| chores-doctor-command | 4 | 4 | 4 | 3 | 3 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
