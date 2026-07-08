ADR STRUCTURAL-COMPLETENESS SCORECARD
=====================================

ADR: ADR-0.33.0-airlock-membrane
Evaluator: gz aADR structural completeness: ADR-0.33.0-airlock-membrane -- STRUCTURALLY
COMPLETE
  Structural-completeness score: 3.40/4.0
  OBPIs scored: 6
  Substance: 0 graded, 2 UNGRADED (substance is judge-graded, never derived from
the above)
```
 its verdict is NOT an authoritative quality GO.
Substance is graded only by recorded judge verdicts (see the Substance
channel below) or reported UNGRADED. Do NOT composite these scores with a
human substance review — they measure different things (GHI #624).

--- Structural Completeness (deterministic) ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | Intent contains no concrete references (code, path, or issue) |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 1 | 0.15 | Checklist items not prefixed with OBPI-; Checklist items have inconsistent granularity |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.40/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| airlock-data-model-and-events | 4 | 4 | 4 | 2 | 4 | 3.6 |
| airlock-in-pipeline-tracer | 4 | 4 | 4 | 2 | 4 | 3.6 |
| airlock-out-pipeline-tracer | 2 | 4 | 4 | 2 | 4 | 3.2 |
| airlock-mx-door | 4 | 4 | 4 | 2 | 3 | 3.4 |
| airlock-permitted-entry-door | 4 | 4 | 4 | 2 | 4 | 3.6 |
| airlock-doctrine-lawful | 4 | 4 | 4 | 3 | 4 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Substance (judge-graded; never derived from the scores above) ---

| Dimension | Grade | Source |
|-----------|-------|--------|
| Problem Substance | UNGRADED | no judge verdict recorded |
| Decision Substance | UNGRADED | no judge verdict recorded |

--- Structural-Completeness Summary (NOT a quality/substance verdict) ---

[x] STRUCTURALLY COMPLETE
[ ] STRUCTURAL GAPS
[ ] STRUCTURALLY INCOMPLETE
