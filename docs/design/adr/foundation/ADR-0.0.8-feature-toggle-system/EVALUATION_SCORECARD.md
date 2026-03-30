<!-- markdownlint-disable-file MD013 MD033 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.0.8 — Feature Flag System for GZKit
**Evaluator:** Claude Opus 4.6
**Date:** 2026-03-30
**Revision:** 2 (post-remediation)

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Problem quantified (GHI #49, 25 blocked ADRs). Before/after concrete. "Every improvement is a breaking change" is immediately compelling. "What GZKit Is Not" preempts misframing. |
| 2 | Decision Justification | 15% | 4 | 0.60 | Three options assessed with evidence. Option A's structural weaknesses itemized (no registry, no categories, no metadata, silent defaults). Option B dismissed for architectural mismatch, not cost. Fowler's three-layer prescription cited with GZKit-specific application. |
| 3 | Feature Checklist | 15% | 4 | 0.60 | Feature Checklist table added with 11 capabilities. Each item names the capability, what is lost if removed, and which OBPI delivers it. All items are independently valuable and testable. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | 8 OBPIs follow domain boundaries. Dependency graph now explicit with 6 stages, critical path declared, parallelization opportunities identified (Stage 3: OBPI-03 ∥ OBPI-04; Stage 4: OBPI-05 ∥ OBPI-06). Each brief declares upstream/downstream dependencies. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OBPI-07 promoted to Heavy (`.gzkit.json` schema change is operator-facing). All Heavy OBPIs touch external contracts. OBPI-06 remains Lite (internal behavior routing with no external contract change). |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Non-goals are specific and strongly argued. Experiment and permissioning toggles dismissed as structurally inappropriate, not merely deferred. Section 6.3 lists governance invariants that flags cannot touch. Section 7 adds further explicit exclusions. |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | All 8 OBPI briefs now include: concrete verification commands, GWT acceptance criteria with REQ identifiers, allowed/denied paths, FAIL-CLOSED requirements, and evidence stub sections. Per-OBPI "done" is operationally defined. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | Module layout references existing structure. Integration points named with paths. Anti-patterns named explicitly (Section 6.3 forbidden locations, existing config.gates problems). Example code shows real integration. |

**WEIGHTED TOTAL: 4.00 / 4.0**

**THRESHOLD:** >= 3.0 = GO | 2.5-3.0 = CONDITIONAL GO | < 2.5 = NO GO

**ADR-LEVEL VERDICT: GO**

---

## OBPI-Level Scores

Scored from OBPI brief files in `obpis/OBPI-0.0.8-*.md`.

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Flag Models & Registry | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 — Flag Service | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 03 — Feature Decisions | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 04 — Diagnostics & Staleness | 3 | 4 | 3 | 3 | 4 | 3.4 |
| 05 — CLI Surface | 3 | 4 | 3 | 3 | 4 | 3.4 |
| 06 — Closeout Migration | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 07 — Config Gates Removal | 3 | 4 | 3 | 4 | 4 | 3.6 |
| 08 — Operator Docs | 3 | 3 | 3 | 3 | 4 | 3.2 |

**OBPI THRESHOLD:** Average >= 3.0 per OBPI. Any OBPI scoring 1 on any dimension must be revised.

**All OBPIs meet threshold (>= 3.0). No OBPI scores 1 on any dimension.**

### Score Changes from Revision 1

| OBPI | Rev 1 Avg | Rev 2 Avg | Change | Reason |
|------|-----------|-----------|--------|--------|
| 01 | 3.4 | 3.8 | +0.4 | Testability 3→4 (concrete verification commands in brief), Clarity 3→4 (full requirements and acceptance criteria) |
| 02 | 3.2 | 3.6 | +0.4 | Testability 3→4 (7 acceptance criteria with GWT format), Clarity 3→4 (11 FAIL-CLOSED requirements) |
| 03 | 3.6 | 3.8 | +0.2 | Size 3→4 (brief confirms surgical scope: one class, one module-level function) |
| 04 | 3.0 | 3.4 | +0.4 | Testability 3→4 (standalone time-bomb test file, gz check integration), Clarity 3→4 (8 requirements) |
| 05 | 2.8 | 3.4 | +0.6 | Independence 2→3 (brief declares explicit dependencies, stub/mock approach viable), Testability 3→4 (CLI smoke tests with expected exit codes), Clarity 3→4 (9 requirements with CLI Doctrine alignment) |
| 06 | 3.4 | 3.8 | +0.4 | Testability 3→4 (behavioral parity tests: flag ON blocks, flag OFF warns), Clarity 3→4 (grep-verifiable migration completeness) |
| 07 | 3.2 | 3.6 | +0.4 | Testability 3→4 (grep-based verification of complete removal), Clarity 3→4 (8 requirements including deprecation warning) |
| 08 | 2.8 | 3.2 | +0.4 | Independence 2→3 (brief acknowledges sequencing but scope is self-contained: 5 doc files), Clarity 3→4 (6 acceptance criteria with mkdocs --strict verification) |

---

## Remediation Summary

All three action items from Revision 1 have been addressed:

### 1. OBPI Brief Files Created

8 briefs written to `obpis/OBPI-0.0.8-*.md` with standard format:
- YAML frontmatter (id, parent, item, lane, status)
- ADR item reference with checklist item linkage
- Objective, Lane rationale, Dependencies (upstream/downstream/parallel)
- Allowed/Denied paths
- FAIL-CLOSED requirements (6-12 per brief)
- Quality gates with per-gate checklists
- GWT acceptance criteria with REQ identifiers (4-7 per brief)
- Concrete verification commands with expected outputs
- Evidence stub sections for completion

### 2. Dependency Graph Declared

ADR updated with explicit dependency graph (ASCII art), 6 stages, critical path
(01→02→03→06→07→08), and parallelization opportunities. Each brief also
declares its own upstream/downstream/parallel dependencies.

### 3. OBPI-07 Promoted to Heavy

Lane changed from Lite to Heavy. Rationale: removing the `.gzkit.json` `gates`
key is an operator-facing schema change. Brief includes deprecation warning
requirement for operators with existing `gates` configuration.

---

## Overall Verdict

- [x] **GO** — Ready for proposal/defense review

ADR scores 4.00/4.0. All 8 OBPIs meet the >= 3.0 threshold (range: 3.2-3.8).
No dimension scores 1. The ADR package is structurally complete with explicit
dependency graph, itemized feature checklist, per-OBPI acceptance criteria,
and concrete verification commands.

### Remaining Observations (non-blocking)

1. **OBPI-08 is the weakest brief (3.2)** — inherent to docs-last ordering. Testability is 3 because `mkdocs build --strict` is the primary verification, and content quality requires human review. This is expected for documentation OBPIs.

2. **Red-team protocol was not run.** If adversarial review is desired before proposal/defense, invoke with `--red-team`.
