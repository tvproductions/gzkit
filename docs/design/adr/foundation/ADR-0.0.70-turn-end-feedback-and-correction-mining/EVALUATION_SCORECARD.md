ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.70
Evaluator: gz adr eval (deterministic)
Date: 2026-06-12

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.45/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| stop-hook-turn-end-feedback | 4 | 4 | 4 | 3 | 4 | 3.8 |
| session-correction-mining | 4 | 4 | 4 | 4 | 4 | 4.0 |
| guardrail-feedback-prose-rule | 4 | 4 | 4 | 4 | 4 | 4.0 |
| fourth-source-triangulation | 4 | 4 | 4 | 4 | 3 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO



---

## Manual Evaluation (authoritative — supersedes CLI pre-screen)

Evaluated 2026-06-12 per gz-adr-evaluate v6 with persona dispatch: `spec-reviewer`
(dimensions 1, 3, 4, 7 + OBPI Independence/Testability/Clarity) and
`quality-reviewer` (dimensions 2, 5, 6, 8 + OBPI Value/Size) ran as independent
subagents; the driver synthesized. Manual scores supersede the CLI pre-screen;
every divergence names the misfired heuristic.

### Part 1 — ADR dimensions (1-4)

| # | Dimension | Weight | CLI | Manual | Reconciliation |
|---|-----------|--------|-----|--------|----------------|
| 1 | Problem Clarity | 15% | 3 | 3 | Concur. No quantified baseline; after-state lives in Decision. |
| 2 | Decision Justification | 15% | 3 | 4 | CLI numbered-item regex missed bold-prefix numbering (**1.**–**4.**); 7 alternatives each rejected with named reasons. |
| 3 | Feature Checklist Completeness | 15% | 3 | 3 | Concur on score; CLI's prefix-format finding is noise — real blocker was the item-1/item-3 coupled proof boundary (fixed: shared path now declared in both briefs). |
| 4 | OBPI Decomposition Quality | 15% | 4 | 3 | Diverge down: CLI cannot compute cross-brief allowed-path closure over REQ proof artifacts (OBPI-03's @covers file lived outside its scope; fixed at authoring). |
| 5 | Lane Assignment Correctness | 10% | 4 | 3 | Diverge down: per-brief lane rationale was template boilerplate; lite confirmed correct under stress-test (fail-open + single-block + off-switch bounds; Gate 5 universal). OBPI-01 lane rationale now specific. |
| 6 | Scope Discipline | 10% | 4 | 4 | Concur. Five non-goals each with exclusion reasoning; mechanical fences via structural-fence REQs. |
| 7 | Evidence Requirements | 10% | 4 | 3 | Diverge down: Demo flags lacked covering REQs (fixed: REQ-01-08, REQ-02-08); telemetry cap unspecified (fixed: 1 MiB / newest 500 lines); REQ-04-02 proof not command-shaped (fixed). |
| 8 | Architectural Alignment | 10% | 3 | 3 | Same score, different reason: CLI's 'no anti-pattern guidance' misfires against the repo-wide Do-Not heading rename; manual 3 rested on the unjustified `.gzkit/sensors/` home (now justified in Decision §1). |

**Weighted total (manual): 3.25 / 4.0 → GO** (CLI pre-screen: 3.45).

### Part 2 — OBPI dimensions (1-4)

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|--------------|-------------|-------|------|---------|-----|
| 01 stop-hook-turn-end-feedback | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 02 session-correction-mining | 4 | 4 | 4 | 3 | 3 | 3.6 |
| 03 guardrail-feedback-prose-rule | 3 | 4 | 3 | 3 | 3 | 3.2 |
| 04 fourth-source-triangulation | 3 | 3 | 3 | 3 | 3 | 3.0 |

All OBPIs >= 3.0; no dimension scored 1; no revision forced.

### Findings applied at authoring time (pre-implementation)

1. MAJOR — OBPI-03's REQ-03-02 proof artifact (`tests/hooks/test_stop_turn_feedback.py`)
   was outside its own Allowed Paths → declared as SHARED proof surface in OBPI-03.
2. ADR Intent's past-tense "recorded as item B.0" claim → corrected to "lands as
   item B.0 via OBPI-0.0.70-04".
3. REQ-0.0.70-01-05 telemetry cap unspecified → pinned (1 MiB; rewrite keeping
   newest 500 lines).
4. `--demo` / `--dry-run` demos uncovered by REQs → REQ-0.0.70-01-08 and
   REQ-0.0.70-02-08 added.
5. REQ-0.0.70-04-02 proof not command-shaped → rg-based proof command pinned.
6. `.gzkit/sensors/` novel runtime-state home unjustified → justification added
   to Decision §1.
7. OBPI-02 corrective-marker lexicon unspecified → initial lexicon pinned as a
   module-level constant requirement.
8. OBPI-01 lane rationale boilerplate → counterargument named and defeated in
   the brief's Lane section.

**Verdict: GO** — ready for implementation; all findings remediated and
`gz obpi validate --adr ADR-0.0.70 --authored` passes 4/4.
