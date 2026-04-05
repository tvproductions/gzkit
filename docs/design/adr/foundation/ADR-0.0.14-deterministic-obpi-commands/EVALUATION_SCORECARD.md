ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.14
Evaluator: gz adr eval (deterministic)
Date: 2026-04-05

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist count (8) != OBPI file count (3) |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 3 | 0.30 | No lane in ADR frontmatter |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No exemplar/precedent language |

WEIGHTED TOTAL: 3.50/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| obpi-lock-command | 4 | 4 | 3 | 3 | 3 | 3.4 |
| obpi-complete-command | 4 | 4 | 4 | 3 | 3 | 3.6 |
| pipeline-skill-migration | 4 | 4 | 4 | 4 | 3 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO

