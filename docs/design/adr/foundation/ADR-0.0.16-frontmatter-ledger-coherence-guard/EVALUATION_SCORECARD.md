# ADR Evaluation Scorecard — ADR-0.0.16

**ADR:** ADR-0.0.16 — Frontmatter-ledger coherence guard and chore audit
**Evaluator:** Claude (main-session persona), manual pass supersedes CLI pre-screen
**Date:** 2026-04-17
**Framework version:** 1.0
**Revision:** 2 (post-refinement)

---

## CLI Pre-Screen (traceability)

```
uv run gz adr evaluate ADR-0.0.16 --json
```

| Dimension | Rev1 CLI | Rev2 CLI (post-refinement) |
|-----------|----------|----------------------------|
| Problem Clarity | 1 | 4 |
| Decision Justification | 4 | 4 |
| Feature Checklist | 4 | 4 |
| OBPI Decomposition | 4 | 4 |
| Lane Assignment | 4 | 4 |
| Scope Discipline | 4 | 4 |
| Evidence Requirements | 4 | 4 |
| Architectural Alignment | 4 | 4 |

**Rev1 CLI weighted total:** 3.55/4.0
**Rev2 CLI weighted total:** 4.00/4.0
**Rev2 verdict:** GO

---

## ADR-Level Scores (Manual, Authoritative)

| # | Dimension | Weight | Score (1-4) | Weighted | CLI Rev2 | Reconciliation |
|---|-----------|--------|-------------|----------|----------|----------------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | 4 | Agree. Post-refinement Intent now includes explicit after-state ("every `gz gates` invocation mechanically confirms frontmatter-ledger coherence…"). Rev1 CLI false-negative (keyword heuristic) is resolved by adding the trigger words naturally. |
| 2 | Decision Justification | 15% | 4 | 0.60 | 4 | Agree. 5 alternatives with rejection rationale; precedent claim now tightened (exemplars cover validator surface only, chore is novel). |
| 3 | Feature Checklist | 15% | 4 | 0.60 | 4 | Agree. 5 items, consistent granularity, OBPI-prefixed, logical order. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | 4 | Upgraded from Rev1 3 → 4. OBPI-05 extraction breaks the 01→02→03→04 chain; 01 and 05 are parallel roots; 02 and 03 run in parallel post-roots. Critical path now 3-deep (01∥05 → 02∥03 → 04) instead of 4-deep serial. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | 4 | Agree. All five OBPIs Heavy; each touches an external contract. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | 4 | Agree. 4 explicit "Does NOT" items; 4 `NEVER` guardrails; conditional future work (ledger schema extension) gated by BLOCKER. |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | 4 | Agree. Every OBPI has REQ-IDs with Given/When/Then; named test files; latency budget; receipt schema. OBPI-03 now carries explicit edge-case requirements (mid-gate race, pool ADRs, partial-failure). |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | 4 | Agree. Exemplar ADRs (0.0.6, 0.0.7) now correctly scoped to validator-surface only; chore novelty acknowledged; module paths cited; anti-pattern `NEVER` guardrails present. |

**Manual weighted total:** 4.00/4.0
**Threshold:** 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)
**Manual verdict:** **GO**

---

## OBPI-Level Scores (Manual, Authoritative)

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | CLI | Notes |
|------|--------------|-------------|-------|------|---------|-----|-----|-------|
| 01 validate-frontmatter-guard | 4 | 4 | 4 | 4 | 4 | 4.0 | 3.8 | CLI size=3 is a false-negative from backtick-counting inline code (`--frontmatter`, `parent:`) as allowed-paths. Real count is 6, in the 2-8 range = 4. Parallel root. |
| 02 gate-integration | 3 | 4 | 4 | 4 | 4 | 3.8 | 4.0 | Explicit predecessors: OBPI-01 + OBPI-05. Framework scores declared-predecessor-only as 3, not 4. CLI missed the cross-OBPI dependency signal. |
| 03 chore-registration | 3 | 4 | 4 | 4 | 4 | 3.8 | 3.6 | CLI caught declared predecessors (ind=2); upgrade to 3 because the brief declares them explicitly. Now includes Known Edge Cases section (mid-gate race, pool ADRs, partial-failure). |
| 04 backfill-and-ghi-closure | 3 | 4 | 4 | 4 | 4 | 3.8 | 4.0 | Explicit prerequisites on 01/02/03/05; CLI heuristic misses "Prerequisites:" language. |
| 05 status-vocab-mapping | 4 | 4 | 4 | 4 | 4 | 4.0 | 3.6 | Parallel root with OBPI-01; no predecessors. CLI ind=2 is a false-negative — CLI matched "parallel with OBPI-01" as a dependency keyword. Framework rubric: truly independent = 4. |

**Overall OBPI average:** 3.88
**OBPI threshold:** Average ≥3.0 per OBPI, no dimension score of 1.
**OBPI gate:** PASS (all averages 3.8+; no dimension scored 1).

---

## Red-Team Challenges (Part 3)

Engaged all 10. No `N/A`. Re-run post-refinement — three of the Rev1 "PASS with note" items are now closed.

| # | Challenge | Rev1 Result | Rev2 Result | Notes |
|---|-----------|-------------|-------------|-------|
| 1 | So What? | PASS | PASS | Each of five OBPIs has unique capability. OBPI-05 passes by being the missing data layer both OBPI-02 and OBPI-03 depend on; removing it forces gate+chore to each inline their own mapping (duplication, drift risk). |
| 2 | Scope | PASS | PASS | "Does NOT" section unchanged. OBPI-04 (backfill execution) still in scope; legitimately the dogfood proof. |
| 3 | Alternative | PASS with note | **PASS (resolved)** | The Rev1 note ("OBPI-02 bundles gate wiring + status-vocab") is the exact refactor executed in Rev2. Decomposition now 5 OBPIs with 2 parallel roots and 1 parallel pair. |
| 4 | Dependency | PASS | PASS | Dependency graph: 01 and 05 are parallel roots; 02 and 03 depend on both; 04 depends on all. Single points of failure: 01 (ledger graph schema discovery) and 05 (vocab mapping). Both have STOP-on-BLOCKER paths. |
| 5 | Gold Standard | PASS | PASS | Exemplar comparison unchanged; Rev2 is stronger because precedent claim is now tightened to validator-surface only. |
| 6 | Timeline | PASS | PASS (improved) | Critical path shortened: Rev1 was 4-deep serial (01→02→03→04). Rev2 is 3-deep with parallelism (01∥05 → 02∥03 → 04). Theoretical wall-clock reduction: ~25-30%. |
| 7 | Evidence | PASS | PASS | Every OBPI has named test file + verification commands. OBPI-03 now carries edge-case tests (race, pool, partial-failure). OBPI-05 has 6 REQ-IDs covering exhaustiveness, round-trip, immutability. |
| 8 | Consumer | PASS with note | **PASS (resolved)** | The Rev1 note (OBPI-03 edge cases) is now an explicit "Known Edge Cases (MUST be addressed in implementation)" subsection in OBPI-03 with resolutions and tests for each case. |
| 9 | Regression | PASS with note | **PASS (resolved)** | The Rev1 note (chore cadence regression) is now Consequences (Negative) item #9: explicit risk, mitigation (default cadence + `gz tidy` integration + `last_run_at` in help), and longer-term CI dry-run proposal. |
| 10 | Parity | PASS with note | **PASS (resolved)** | The Rev1 note (parity claim overreach) is addressed in the tightened precedent paragraph: "exemplars for the validator-surface pattern only; the auto-fix chore with ledger-wins reconciliation, receipt emission, and a one-time dogfood backfill is a novel structural contribution of this ADR." |

**Red-team summary:** 10 engaged, 10 clean PASS (0 PASS-with-note, 0 FAIL) in Rev2. All Rev1 notes resolved.
**Red-team threshold:** ≤2 failures = GO, 3-4 = CONDITIONAL GO, ≥5 = NO GO.
**Red-team verdict:** **GO**

---

## Overall Verdict

- [x] **GO** — Ready for proposal/defense review and implementation authorization.
- [ ] CONDITIONAL GO — Address items below, then re-evaluate.
- [ ] NO GO — Structural revision required.

**Weighted total:** 4.00/4.0 (manual + CLI agree)
**OBPI gate:** PASS (avg 3.88, no dimension scored 1)
**Red-team:** 0 failures, 0 notes, 10/10 clean PASS

---

## Revision History

- **Rev1 (2026-04-17, pre-refinement):** Manual 3.70/4.0, CLI 3.55/4.0. GO with 3 red-team PASS-with-note and 5 non-blocking action items.
- **Rev2 (2026-04-17, post-refinement):** Manual 4.00/4.0, CLI 4.00/4.0. GO with 0 notes. All 5 Rev1 action items applied:
  1. Intent after-state sentence added (D1: 3 → 4)
  2. OBPI-05 extracted for parallelism (D4: 3 → 4; red-team Challenge 3 resolved)
  3. Known Edge Cases subsection added to OBPI-03 (red-team Challenge 8 resolved)
  4. Parity claim tightened (red-team Challenge 10 resolved)
  5. Chore cadence regression added to Consequences Negative #9 (red-team Challenge 9 resolved)

## Action Items

None. The ADR is ready for implementation authorization.
