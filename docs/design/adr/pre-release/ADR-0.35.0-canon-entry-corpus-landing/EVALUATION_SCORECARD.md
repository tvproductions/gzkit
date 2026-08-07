ADR STRUCTURAL-COMPLETENESS SCORECARD
=====================================

ADR: ADR-0.35.0-canon-entry-corpus-landing
Evaluator: gz adr eval (deterministic STRUCTURAL-COMPLETENESS lint)
Date: 2026-08-07

NOTE: This scorecard grades STRUCTURAL COMPLETENESS only — section
presence, depth, counts, and references. It is NOT a judgment of decision
SUBSTANCE or quality, and its verdict is NOT an authoritative quality GO.
Substance is graded only by recorded judge verdicts (see the Substance
channel below) or reported UNGRADED. Do NOT composite these scores with a
human substance review — they measure different things (GHI #624).

--- Structural Completeness (deterministic) ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 1 | 0.15 | Checklist items not prefixed with OBPI-; Checklist items have inconsistent granularity |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.55/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| corpus-tombstone-schema-and-fold | 4 | 4 | 4 | 4 | 4 | 4.0 |
| content-withdraw-verb | 4 | 4 | 4 | 2 | 4 | 3.6 |
| retire-duplicate-invariant-entries | 4 | 4 | 4 | 4 | 3 | 3.8 |
| section-ownership-and-ratchet | 4 | 4 | 4 | 3 | 4 | 3.8 |
| corpus-candidate-generator | 4 | 4 | 4 | 2 | 4 | 3.6 |
| validate-rendition-lineage | 4 | 4 | 4 | 3 | 4 | 3.8 |
| content-land-orchestrator | 4 | 4 | 4 | 2 | 4 | 3.6 |
| remember-post-append-advisory | 4 | 4 | 4 | 4 | 4 | 4.0 |
| codex-playback-wiring | 4 | 4 | 4 | 3 | 4 | 3.8 |
| classification-reader-and-ownership | 4 | 4 | 4 | 3 | 4 | 3.8 |

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
