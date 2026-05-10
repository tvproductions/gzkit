ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.31-distribution-invariant-doctrine
Evaluator: main-session (manual) + gz adr eval (CLI pre-screen)
Date: 2026-05-10 (post-polish)

--- CLI Pre-Screen (post-polish, for traceability) ---

Weighted total: 3.75/4.0 — CLI verdict: NO GO (still firing on OBPI Clarity heuristic)
OBPI scores: author-t0-doctrine 3.4 | register-t0-scorecard 3.2 | t0-failure-mode-catalog 2.8

CLI dimension shifts after polish:
- Dim 1 Problem Clarity: 3 → 4 (target-state paragraph now in Intent)
- Dim 8 Architectural Alignment: 1 → 3 (ADR-0.0.18↔ADR-0.0.17 precedent now surfaced at top of Decision)
- Dim 2 Decision Justification: still 3 (CLI heuristic misfire unchanged — see reconciliation below)

The CLI's NO GO verdict still fires on OBPI Clarity = 1 across all three OBPIs.
This is a documented false-negative from the CLI's Implementation-Summary heuristic
on Draft briefs (see OBPI-level reconciliation below).

--- ADR-Level Scores (Manual, post-polish) ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Polish landed: target-state paragraph in Intent now names byte-equivalent-on-fresh-install as the testable after-state. Before-state (GHI #318 evidence) and after-state both concrete; "so what?" is immediate. CLI agrees (3→4). |
| 2 | Decision Justification | 15% | 4 | 0.60 | Three alternatives dismissed with specific rejection rationale; ADR-0.0.18↔ADR-0.0.17 precedent named twice (now also at top of Decision). CLI scored 3 ("no rationale language in Decision") — heuristic looks for keywords in Decision section header; rationale flows through Alternatives Considered + the explicit precedent paragraph at top of Decision. Manual overrides to 4. |
| 3 | Feature Checklist | 15% | 4 | 0.60 | Three items, each independently valuable with named removal-impact. Granularity consistent. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | Clean acyclic graph; OBPI-01 → -02 and -03 (parallelizable after -01). Domain-driven boundaries. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | All Lite; foundation-kind brief-level Gate 5 correctly acknowledged in every OBPI. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Six explicit "What this ADR does NOT author" exclusions; Denied Paths cross-checked across OBPIs. |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | Every OBPI has runnable grep + validate + mkdocs verification commands. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | Polish landed: ADR-0.0.18↔ADR-0.0.17 precedent now surfaced at top of Decision rather than buried in Alternatives. Integration points named (`docs/governance/trust-doctrine.md`, `docs/governance/advisory-rules-audit.md`). Anti-pattern quoted verbatim. CLI agrees (1→3). Score 3 rather than 4 because the ADR has no dedicated "Integration Points" section heading — the precedent and integration points live in narrative form within Decision. Acceptable for a doctrine ADR; would need a structural section to reach 4. |

WEIGHTED TOTAL (MANUAL): 3.90/4.0
CLI WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores (Manual, post-polish) ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 author-t0-doctrine | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 02 register-t0-scorecard | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 03 t0-failure-mode-catalog | 3 | 4 | 4 | 3 | 3 | 3.4 |

OBPI-02 Clarity lifted 3 → 4 after polish: the representative Promotable row (row 53,
lock-handoff-coupling) is now quoted inline with extracted column schema, removing
the interpretation flexibility that previously held the score at 3.

All OBPIs pass. No dimension scores 1 in the manual evaluation.

--- CLI vs Manual OBPI Reconciliation ---

CLI Clarity scores (all three OBPIs): 1
Root cause: CLI heuristic checks Implementation Summary content for completion evidence.
All three briefs are in Draft status with empty Implementation Summary sections (the
"## Implementation Summary" section is part of the Evidence template and is filled
post-implementation). The heuristic cannot distinguish "well-specified Draft awaiting
implementation" from "vague Draft." Specification clarity is assessed from the
Requirements, Acceptance Criteria, Verification, and Key Proof sections — all of which
are substantive in this ADR's OBPIs.

CLI OBPI-03 Independence score: 2 ("has undeclared dependencies")
Root cause: CLI didn't recognize STOP-on-BLOCKER conditions as declared dependency
declarations. OBPI-03 explicitly names OBPI-01, ADR-0.0.32, GHI #318, and ADR-0.0.21
as prerequisites with STOP-on-BLOCKER conditions — these are declared predecessors.
Manual score: 3.

--- Polish Diff (this round) ---

1. ADR Intent — added "Target state (testable)" paragraph naming byte-equivalent-on-
   fresh-install as the testable after-state. Lifts Dim 1 to 4 (CLI-confirmed).

2. ADR Decision — added "Architectural precedent" paragraph at the top surfacing the
   ADR-0.0.18↔ADR-0.0.17 doctrine/mechanics split as the proven precedent. Lifts
   Dim 8 to 3 (CLI-confirmed).

3. OBPI-0.0.31-02 — added a representative Promotable row (row 53, lock-handoff-
   coupling) inline with extracted four-column schema. Lifts OBPI-02 Clarity to 4.

--- Overall Verdict ---

[x] GO ← manual verdict (ADR weighted total 3.90, all OBPI averages >= 3.4, no dimension scores 1)
[ ] CONDITIONAL GO
[ ] NO GO

NOTE: The CLI's standing NO GO verdict reflects the OBPI Clarity heuristic firing on
empty Implementation Summary sections in Draft briefs — a known false-negative
(documented above). The manual evaluation overrides to GO.

No outstanding action items. ADR is ready for proposal/defense review.
