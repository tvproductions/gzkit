<!-- markdownlint-disable-file MD013 MD041 -->

ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.10 — Storage Tiers and Simplicity Profile
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
| 03 | 4 | 3 | 3 | 3 | 4 | 3.4 |
| 04 | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 05 | 3 | 4 | 3 | 3 | 3 | 3.2 |
| 06 | 4 | 4 | 3 | 4 | 4 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. All OBPIs pass. No dimension scores 1.

--- Notes ---

Dimension 6 (Scope Discipline) scored 3 after adding explicit Non-Goals section
with four scope boundaries (no SQLite, no Tier B manifest, no Tier C introduction,
no identity model implementation).

ADR-0.0.10 promotes pool ADR storage-simplicity-profile. The pool ADR provides
strong prior art, strengthening Decision Justification. All six OBPIs are Lite
lane (no external contract changes), which is correct — this ADR documents and
enforces tier rules, it does not add CLI surfaces.

--- Overall Verdict ---

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

ACTION ITEMS:
1. (Addressed) Non-goals section added to improve scope discipline
2. OBPI-02 (identity surfaces) may have tension with Entity Hierarchy ADR
   scope — clarify which ADR owns Pydantic model authoring for REQ/TASK/EV
3. Consider adding pool ADR text comparison to show what was added vs promoted
   verbatim, strengthening Decision Justification toward a 4
