ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.66-deterministic-steering-substrate
Evaluator: gz adr eval (deterministic)
Date: 2026-05-31

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.40/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| tdd-receipt-stream-hub | 4 | 4 | 4 | 4 | 3 | 3.8 |
| gz-next-cap22-and-cap08-mode | 4 | 4 | 4 | 3 | 3 | 3.6 |
| gz-metrics-read-view | 4 | 4 | 4 | 4 | 3 | 3.8 |
| queryability-search-and-insights-query | 4 | 4 | 4 | 4 | 3 | 3.8 |
| solved-problem-pattern-corpus-read-surface | 4 | 4 | 4 | 4 | 3 | 3.8 |
| subsume-pool-management-into-gz-next | 4 | 4 | 4 | 4 | 3 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO

--- Manual Review (supersedes CLI pre-screen; gz-adr-evaluate Step 2-3) ---

Evaluator: main-session (authoring agent), 2026-05-31. CLI pre-screen recorded
above for traceability; manual reconciliation of each flagged dimension:

| # | CLI score | CLI finding | Manual score | Heuristic-mismatch rationale |
|---|-----------|-------------|--------------|------------------------------|
| 1 Problem Clarity | 3 | "No after/target-state language in Intent" | 3 (confirm) | False-negative on the keyword scan, but the target-state IS distributed: Intent names the before-state (scattered across ~9 dormant ADRs; agents under-consult state) and the after-state (one coherent deterministic read-substrate; orientation sibling of the enforcement spine). The score-3 stands — Intent is dense but the before/after split could be one sentence sharper; not a revision blocker. |
| 2 Decision Justification | 3 | "Decision section has no numbered items" | 3 (confirm) | False-negative: the Decision IS decomposed (1)-(6) inline and the six Checklist items carry the numbered decomposition; the CLI looks for a leading-digit list shape in the Decision body specifically. Justification is distributed across Decision + Alternatives Considered (six rejected alternatives) + Stress-test forcing functions. Score-3 stands. |
| 3 Feature Checklist | 3 | "Checklist items not prefixed with OBPI-" | 3 (confirm) | False-negative on format: the practiced 0.0.64 ADR prefixes checklist items `OBPI-0.0.64-NN:`; this ADR uses `<slug>:` form. The 1:1 checklist<->OBPI mapping is intact and verified (`gz obpi validate --authored` 6/6 PASS). Cosmetic format divergence from the heuristic's expected prefix; not a completeness defect. |
| 4 OBPI Decomposition | 3 | "OBPI allowed paths overlap significantly" | 3 (confirm) | Partially true and intentional: all six OBPIs share `src/gzkit/` and `src/gzkit/cli/` because they are one substrate's verbs; the briefs disambiguate via explicit Denied Paths (each names the sibling-OBPI surfaces it must not touch) and leaf-first STOP-on-BLOCKERS sequencing. Overlap is real at the directory grain, bounded at the brief grain. Score-3 stands. |
| 8 Architectural Alignment | 1 -> 4 | "No source file path references; no exemplar/precedent language" | 4 | REVISED. The CLI flagged a genuine gap: the ADR body cited doctrines but no concrete `src/...` integration points or named precedent. Fixed by adding the `## Architectural Alignment` section (source-file integration points + exemplar/precedent reuse: ARB corpus, decision-table-over-ledger, stdlib FTS5, read-vs-compute boundary). Re-scored 4 by the CLI after the edit; weighted total 3.10 -> 3.40. |

No dimension scores 1 after the dimension-8 revision. All six OBPIs average
3.6-3.8 with no dimension scoring 1. Manual verdict: GO (concurs with CLI).
Ready for human proposal/defense review.

