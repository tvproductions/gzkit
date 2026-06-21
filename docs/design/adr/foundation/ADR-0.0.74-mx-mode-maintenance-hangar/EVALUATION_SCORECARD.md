ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.74 — MX Mode (Maintenance Hangar) + leveled GZ_<LEVEL> substrate
Date: 2026-06-21
Channels: STRUCTURAL (deterministic CLI pre-screen) + SUBSTANCE (independent
persona-dispatched review). Kept SEPARATE per GHI #624 — never composited.

================================================================
CHANNEL A — STRUCTURAL COMPLETENESS (deterministic; gz adr evaluate)
================================================================

NOTE: grades STRUCTURAL COMPLETENESS only — section presence, depth, counts,
references. NOT a substance/quality verdict.

| # | Dimension | Weight | Score | Weighted | Findings |
|---|-----------|--------|-------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

STRUCTURAL WEIGHTED TOTAL: 3.85/4.0 — STRUCTURALLY COMPLETE
OBPIs: 14 scored, all averages >= 3.6, no dimension = 1.

================================================================
CHANNEL B — SUBSTANCE (independent persona-dispatched review)
================================================================

Judges: quality-reviewer (architectural dims) + spec-reviewer (spec dims + the
7 Phase-B OBPIs), dispatched independently per the gz-adr-evaluate persona
contract (the driver authored the briefs, so self-scoring is excluded). Scores
below are POST-FIX (three findings surfaced and resolved this pass — see
ACTION ITEMS).

--- ADR substance (8 dimensions) ---

| # | Dimension | Weight | Score | Weighted |
|---|-----------|--------|-------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 4 | 0.40 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 4 | 0.40 |

SUBSTANCE WEIGHTED TOTAL: 3.35/4.0  (>= 3.0 = GO)

--- OBPI substance (7 Phase-B briefs; post-fix) ---

| OBPI | Ind | Test | Val | Size | Clar | Avg |
|------|-----|------|-----|------|------|-----|
| 03 mx-gate5-invariants | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 05 mx-exit-hard-gate | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 09 mx-retire-staging-flags | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 11 mx-gz-level-vocabulary | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 12 mx-gates-as-sensors | 4 | 4 | 4 | 4 | 3 | 3.8 |
| 13 mx-proxy-reality-detector | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 14 mx-hardening | 4 | 4 | 4 | 3 | 3 | 3.6 |

OBPI THRESHOLD: every average >= 3.0, no dimension = 1. PASS.
(OBPIs 01/02/04/06/07/08 unchanged this pass — inherit prior structural scores.)

ACTION ITEMS (surfaced by review, resolved before commit):
1. ADR Consequences leaked the withdrawn item-10 doc-type taxonomy — Positive #6
   rewritten to the leveled-substrate benefit; Negative #3's "one-word alignment"
   / "lexical-alignment guard" clauses removed. (Coupled-surface coherence.)
2. OBPI-14 REQ-14-02 "blocks a normal release" was unwired — added
   src/gzkit/commands/patch_release.py + closeout.py to Allowed Paths and rewrote
   the REQ to consult hardening.normal_release_blocked() at the real release site
   (gz patch release / gz closeout). Raised Testability 3->4, Clarity 2->3.
3. OBPI-05 reshape left Discovery Context/Prerequisites as scaffold — declared the
   hard predecessors OBPI-04 (enter-scope) / 01 / 02 / 11 / 12. Raised
   Independence 2->3.

================================================================
OVERALL VERDICT: GO
================================================================

[x] GO — both channels pass (structural 3.85, substance 3.35), every OBPI
        average >= 3.0, no dimension scored 1. Ready for proposal/defense review.
[ ] CONDITIONAL GO
[ ] NO GO

Red-team (Part 3, 10-challenge): not run this pass (not requested; standard
8+5 dimension evaluation with independent dispatch performed instead).
