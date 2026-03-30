<!-- markdownlint-disable-file MD013 MD033 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.0.8 — Feature Flag System for GZKit
**Evaluator:** Claude Opus 4.6
**Date:** 2026-03-30

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Problem quantified (GHI #49, 25 blocked ADRs). Before/after concrete. "Every improvement is a breaking change" is immediately compelling. "What GZKit Is Not" preempts misframing. |
| 2 | Decision Justification | 15% | 4 | 0.60 | Three options assessed with evidence. Option A's structural weaknesses itemized (no registry, no categories, no metadata, silent defaults). Option B dismissed for architectural mismatch, not cost. Fowler's three-layer prescription cited with GZKit-specific application. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | v1 Scope (Section 9) is comprehensive and well-bounded. Items are concrete and testable. Loses a point because the scope list is formatted as in-scope/out-of-scope prose rather than a strictly itemized checklist where each item's independent value is stated. |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | 8 OBPIs follow domain boundaries (models → service → decisions → diagnostics → CLI → migration → docs). Dependency chain is implicit but clear. Loses a point because the dependency graph is not explicitly declared and parallelization stages are not stated. |
| 5 | Lane Assignment | 10% | 3 | 0.30 | Heavy assignments are defensible — OBPIs 01-05 and 08 touch external contracts (new subpackage, CLI commands, operator docs). Lite for 06-07 is defensible (internal routing). Minor concern: OBPI-07 removes the `.gzkit.json` `gates` key, which is an operator-facing schema change — arguably Heavy. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Non-goals are specific and strongly argued. Experiment and permissioning toggles dismissed as structurally inappropriate, not merely deferred. Section 6.3 lists governance invariants that flags cannot touch. Section 7 adds further explicit exclusions. |
| 7 | Evidence Requirements | 10% | 2 | 0.20 | Testing strategy (Section 10) is thorough at the system level (9 test categories from Fowler). But per-OBPI verification commands are absent. No OBPI brief files exist yet. The WBS table lists specification summaries but not acceptance criteria or evidence commands per OBPI. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | Module layout references existing structure. Integration points named with paths (`core/lifecycle.py`, `commands/closeout.py`, `commands/gates.py`). Anti-patterns named explicitly (Section 6.3 forbidden locations, existing config.gates problems). Example code shows real integration. |

**WEIGHTED TOTAL: 3.40 / 4.0**

**THRESHOLD:** >= 3.0 = GO | 2.5-3.0 = CONDITIONAL GO | < 2.5 = NO GO

**ADR-LEVEL VERDICT: GO**

---

## OBPI-Level Scores

Scored from WBS descriptions in the ADR (no brief files exist yet).

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Flag Models & Registry | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 02 — Flag Service | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 03 — Feature Decisions | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 04 — Diagnostics & Staleness | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 05 — CLI Surface | 2 | 3 | 3 | 3 | 3 | **2.8** |
| 06 — Closeout Migration | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 07 — Config Gates Removal | 3 | 3 | 3 | 4 | 3 | 3.2 |
| 08 — Operator Docs | 2 | 3 | 3 | 3 | 3 | **2.8** |

**OBPI THRESHOLD:** Average >= 3.0 per OBPI. Any OBPI scoring 1 on any dimension must be revised.

**Findings:**

- No OBPI scores 1 on any dimension (revision threshold passes).
- OBPI-05 (CLI Surface) averages 2.8 — Independence is 2 because it depends on 01, 02, and 04 before it can be meaningfully built. Consider whether a stub/mock approach could raise independence.
- OBPI-08 (Operator Docs) averages 2.8 — Independence is 2 because docs require all implementation OBPIs complete. This is inherent to docs-last ordering but could be mitigated by writing docs incrementally with each OBPI.

---

## Dimension-Level Commentary

### Strengths

1. **Problem framing is exemplary.** The GHI #49 incident is a concrete, quantified trigger. The "What GZKit Is Not" section preempts the most likely misframing (SaaS feature flags). The six problem statements in Section 2 each name a specific capability gap.

2. **Toggle taxonomy is rigorous.** Section 4 doesn't just list the Fowler categories — it evaluates each against GZKit's actual domain and gives a specific fit verdict. The "structurally inappropriate, not merely deferred" framing for experiment and permissioning toggles is strong scope defense.

3. **Architecture is well-reasoned.** The three-layer separation (router → decisions → toggle points) follows Fowler's prescription and is justified with GZKit-specific examples. The "where toggle points are forbidden" section (6.3) is unusually strong — most ADRs define what the system does, not what it must never do.

4. **Lifecycle discipline is concrete.** The removal strategy (Section 10) names 7 specific steps. The time-bomb test is a forcing function that makes leaving stale flags harder than removing them. The ON/OFF convention ensures "all flags OFF" is always valid.

### Weaknesses

1. **Per-OBPI evidence criteria are missing.** The testing strategy is system-level. Individual OBPIs don't declare what commands prove they're done. This will cause ambiguity at closeout.

2. **Dependency graph is implicit.** The natural chain (01→02→03, then 04/05/06 branch) is inferrable but not stated. Parallelization stages are not declared. An implementer must reconstruct the graph from context.

3. **OBPI-07 lane assignment is borderline.** Removing the `gates` key from `.gzkit.json` changes an operator-facing schema. If any operator has `gates` in their config, removal is a breaking change. This could warrant Heavy lane or at minimum a migration note.

4. **No OBPI brief files exist.** The WBS table provides summaries but briefs with full acceptance criteria, constraints, and evidence stubs are absent. Evaluation of OBPI quality is therefore based on summary descriptions only.

---

## Overall Verdict

- [x] **CONDITIONAL GO** — Address items below, then re-evaluate

The ADR itself scores 3.40/4.0 (GO). However, two OBPIs (05, 08) fall below the 3.0 average threshold, and no OBPI brief files exist. The ADR is structurally sound and ready for implementation planning, but brief creation should address the identified weaknesses.

### Action Items

1. **Create OBPI brief files** with per-OBPI acceptance criteria, verification commands, and dependency declarations. The ADR provides enough specification — the briefs are the missing delivery vehicle.

2. **Declare the dependency graph explicitly** in briefs or ADR. State which OBPIs can run in parallel and which have sequential dependencies. Suggested stages:
   - Stage 1: OBPI-01 (models/registry — foundation)
   - Stage 2: OBPI-02 (service — depends on 01)
   - Stage 3: OBPI-03 (decisions — depends on 02), OBPI-04 (diagnostics — depends on 01/02) [parallel]
   - Stage 4: OBPI-05 (CLI — depends on 01/02/04), OBPI-06 (closeout migration — depends on 03) [parallel]
   - Stage 5: OBPI-07 (gates removal — depends on 06)
   - Stage 6: OBPI-08 (docs — depends on all)

3. **Reconsider OBPI-07 lane.** If `.gzkit.json` `gates` key removal is operator-visible, it should be Heavy with a migration note. If no operators currently use `gates`, document that finding as evidence and keep Lite.
