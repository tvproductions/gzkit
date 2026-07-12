ADR STRUCTURAL-COMPLETENESS SCORECARD
=====================================

ADR: ADR-0.34.0
Evaluator: gz adr eval (deterministic STRUCTURAL-COMPLETENESS lint)
Date: 2026-07-12

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
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| grandfather-manifest-and-closed-kind-assertion | 4 | 4 | 4 | 2 | 4 | 3.6 |
| authoring-time-kind-rejection | 4 | 4 | 4 | 3 | 4 | 3.8 |
| terminal-partition-gate-and-doctrine-retirement | 2 | 4 | 4 | 2 | 4 | 3.2 |
| execute-migration-populate-and-resense | 2 | 4 | 4 | 2 | 3 | 3.0 |
| activate-standing-taxonomy-gate | 1 | 4 | 4 | 2 | 3 | 2.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Substance (judge-graded; never derived from the scores above) ---

| Dimension | Grade | Source |
|-----------|-------|--------|
| Problem Substance | UNGRADED | no judge verdict recorded |
| Decision Substance | UNGRADED | no judge verdict recorded |

--- Structural-Completeness Summary (NOT a quality/substance verdict) ---

[ ] STRUCTURALLY COMPLETE
[ ] STRUCTURAL GAPS
[x] STRUCTURALLY INCOMPLETE

STRUCTURAL ACTION ITEMS:
1. OBPI-0.34.0-05-activate-standing-taxonomy-gate: average 2.8 < 3.0
2. OBPI-0.34.0-05-activate-standing-taxonomy-gate: independence scored 1 (structural defect)

--- Operator disposition (2026-07-12, g0-ratified) ---

Action items 1 & 2 (OBPI-05 independence=1, avg 2.8) are ACCEPTED as an inherent
property of a sequential migration, NOT gamed away. The Foundation Sunset is
build-mechanism (01/02/03) -> migrate-data (04) -> activate-gate (05); the
anti-staging-flag doctrine requires the --taxonomy gate to wire into gz check as
the LAST act over a terminal tree, so some OBPI MUST be the dependent tail. A prior
4->5 split (to clear OBPI-04's original independence=1) relocated the flag to OBPI-05
rather than eliminating it, confirming no decomposition removes the sequential tail
-- it only chooses which OBPI carries it; the split still improved structure (the
flag now sits on a small 2-action activation step, not the original 6-action blob).
Per gz-adr-create §9 ("the CLI scorer is a pattern-matching pre-screen, not a truth
oracle ... do NOT reword solely to feed the matcher"), the score is a false-negative
on legitimate sequencing. Rationale documented in OBPI-05 § Sequencing.

Two score-3 dimensions left as-is (non-blocking, optional polish): Feature Checklist
(items keyed by slug, not OBPI- prefix) and Architectural Alignment (no explicit
anti-pattern guidance section).
