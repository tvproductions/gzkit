<!-- markdownlint-disable-file MD013 MD041 -->

ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy
Evaluator: Claude Opus 4.6 (1M context)
Date: 2026-03-29

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

WEIGHTED TOTAL: 3.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 3 | 3 | 3 | 4 | 3.4 |
| 02 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 03 | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 04 | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 05 | 3 | 4 | 3 | 3 | 4 | 3.4 |
| 06 | 4 | 3 | 3 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. All OBPIs pass. No dimension scores 1.

--- Notes ---

Dimension 6 (Scope Discipline) was initially scored 2 due to missing non-goals.
A Non-Goals section was added to the ADR with four explicit scope boundaries,
raising the score to 3. Revised weighted total: 3.00.

--- Overall Verdict ---

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

ACTION ITEMS:
1. (Addressed) Non-goals section added to improve scope discipline
2. Consider adding quantification to Problem Clarity (count of commands that
   read status from different layers) to strengthen Dimension 1 toward a 4
3. Consider naming alternatives explicitly in Decision section (e.g.,
   "frontmatter-first" as rejected alternative) to strengthen Dimension 2
