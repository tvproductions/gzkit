<!-- markdownlint-disable-file MD013 MD041 -->

ADR EVALUATION SCORECARD
========================

ADR: ADR-0.18.0 — Subagent-Driven Pipeline Execution
Evaluator: Claude Opus 4.6
Date: 2026-03-17
Revision: 2 (post-improvement pass)

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Problem quantified: "40-60% context consumption on 8+ task OBPIs." Before state is concrete (single-session inline). After state is testable (controller dispatches subagents, orchestrator stays lean). "So what?" links directly to ADR-0.12.0/0.13.0 investment being undermined by context exhaustion. |
| 2 | Decision Justification | 15% | 4 | 0.60 | Alternatives Considered table names and dismisses 5 specific alternatives (bigger context, parallel implementers, skip review for Lite, external CI, single reviewer) with concrete reasoning. Superpowers cited as community-validated precedent (92k+ stars). Local precedent cited (gz-plan Explore agents, gz-obpi-lock). |
| 3 | Feature Checklist | 15% | 4 | 0.60 | Checklist Item Necessity Table explicitly answers "if removed, what breaks?" for each of the 5 items. Every item has a concrete capability gap when removed. No padding — each OBPI is independently necessary and the set is sufficient. |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | Clean domain boundaries: taxonomy / dispatch / review / verification / integration. Dependency graph is acyclic with clear parallelization (3-stage critical path). Each OBPI is 1-3 day scope. Structural parity with ADR-0.14.0 exemplar noted. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | Every assignment justified with specific criteria. Heavy OBPIs (02, 05) change external contracts (pipeline behavior, CLI surface). Lite OBPIs (01, 03, 04) are internal data model and protocol. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Non-Goals section with 5 explicit exclusions. Scope Creep Guardrails subsection names 4 specific expansion scenarios and directs each to a new ADR. Scope boundaries are tested against plausible creep. |
| 7 | Evidence Requirements | 10% | 3 | 0.30 | Each OBPI has specific test files, quality gate commands, and completion checklists. Heavy OBPIs address Gate 3/4/5 obligations. Verification commands are concrete. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | Architectural Exemplar section references ADR-0.14.0 and names structural parity. Local precedent cited (gz-plan, gz-obpi-lock subagent usage). Integration points listed with module paths. Anti-pattern warning is specific. Guardrails prevent known scope expansion. |

**WEIGHTED TOTAL: 3.75/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Agent Role Taxonomy | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 02 — Implementer Dispatch | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 03 — Two-Stage Review | 3 | 3 | 3 | 4 | 3 | 3.2 |
| 04 — REQ Verification | 3 | 3 | 3 | 4 | 3 | 3.2 |
| 05 — Runtime Integration | 2 | 3 | 4 | 3 | 3 | 3.0 |

**OBPI THRESHOLD:** All averages >= 3.0. No OBPI scores 1 on any dimension.

**OBPI Notes:**

- OBPI-05 scores 2 on Independence because it integrates all prior OBPIs — inherent to its role as the integration OBPI. Not a defect, but a scheduling constraint.
- OBPI-03 scores 3 on Value (not 4) because the pipeline would still function without independent review — it would just be weaker. This is an enhancement, not a capability gap.

--- Overall Verdict ---

[x] **GO** — Ready for proposal/defense review.

Weighted total 3.75/4.0 clears the GO threshold comfortably. All dimensions at 3+, six dimensions at 4. All OBPI averages >= 3.0 with no dimension scoring 1.

**Improvement from revision 1:** +0.65 (3.10 → 3.75) via quantified problem statement, Alternatives Considered table, Checklist Necessity Table, Scope Creep Guardrails, and Architectural Exemplar reference.

**ACTION ITEMS:**

None — proceed to human review.
