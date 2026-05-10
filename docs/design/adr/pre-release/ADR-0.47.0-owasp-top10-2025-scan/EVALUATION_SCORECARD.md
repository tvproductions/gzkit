ADR EVALUATION SCORECARD
========================

ADR: ADR-0.47.0
Evaluator: gz adr eval (deterministic)
Date: 2026-05-10

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist count (5) != OBPI file count (0) |
| 4 | OBPI Decomposition | 15% | 1 | 0.15 | No OBPI brief files found; OBPI numbering has gaps |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 1 | 0.10 | No OBPI briefs to evaluate |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No exemplar/precedent language |

WEIGHTED TOTAL: 2.70/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[ ] GO
[x] CONDITIONAL GO
[ ] NO GO

ACTION ITEMS:
1. ADR weighted total 2.70 < 3.0 (GO threshold)
