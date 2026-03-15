---
id: ADR-pool.task-level-governance
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.spec-triangle-sync
inspired_by: https://github.com/obra/superpowers
---

# ADR-pool.task-level-governance: Task-Level Governance

## Status

Proposed

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Four-tier governance hierarchy

---

## Intent

Formalize TASK as the fourth tier of gzkit's governance hierarchy: ADR → OBPI → REQ → TASK. Every tier is both ledger-traceable and git-commit traceable.

Today, gzkit governs work at the ADR and OBPI levels. The `spec-triangle-sync` and `tests-for-spec` pool ADRs define the REQ level (named requirements with test linkage). This ADR completes the hierarchy by adding the TASK level — execution steps that are individually traced, behaviorally defended with anti-rationalization patterns, and intermeshed with the superpowers behavioral methodology.

Superpowers provides excellent execution-step discipline (TDD, debugging, verification, circuit breakers) but treats tasks as ephemeral checklist items with no governance trail. gzkit makes them first-class governance artifacts: ledger-recorded, git-commit-linked, and auditable.

---

## Target Scope

- Define TASK entity format and identifier scheme (e.g., `TASK-<semver>-<obpi>-<req>-<seq>`).
- Define TASK-level ledger events (`task_started`, `task_completed`, `task_blocked`, `task_escalated`).
- Define git commit linkage contract (TASK ID in commit message → traceable to REQ → OBPI → ADR).
- Define the intermeshing contract with superpowers: how superpowers behavioral methodology (anti-rationalization, RED-GREEN-REFACTOR, circuit breakers) maps to TASK-level governance events.
- Add CLI surfaces for TASK lifecycle management within OBPI pipeline execution.
- Integrate TASK status with existing `gz status` and `gz state` reporting.

---

## Non-Goals

- No replacement of superpowers behavioral methodology at the execution level. Superpowers skills remain the behavioral discipline source; gzkit adds the governance wrapper.
- No mandatory adoption — TASK-level tracing is opt-in per lane (advisory for lite, required for heavy).
- No changes to ADR or OBPI governance tiers.
- No cloud or external storage requirements. TASK state derives from the ledger.

---

## Dependencies

- **Blocks on**: ADR-pool.spec-triangle-sync (REQ level must exist before TASK level can reference it).
- **Blocks on**: ADR-pool.tests-for-spec (REQ identifiers must be defined for TASK→REQ linkage).
- **Related**: ADR-pool.skill-behavioral-hardening (behavioral patterns that TASK-level governance will formalize).
- **Related**: ADR-pool.execution-memory-graph (TASK events feed the execution memory graph).

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. ADR-pool.spec-triangle-sync is promoted and the REQ identifier scheme is ratified.
2. TASK identifier format and ledger event schema are approved.
3. Git commit linkage contract is defined (what goes in commit messages, how it is parsed).
4. Superpowers intermeshing contract is defined (which superpowers skills generate which TASK events).
5. Advisory vs. required enforcement model is agreed per lane.

---

## Notes

- The four-tier hierarchy (ADR → OBPI → REQ → TASK) is unique to gzkit. No other project combines governance traceability at all four levels with AI agent behavioral methodology.
- Superpowers (github.com/obra/superpowers) provides behavioral discipline at the TASK level. gzkit provides governance infrastructure (ledger, git tracing, evidence requirements) at ALL four levels. The intermeshing is complementary, not competitive.
- TASK-level governance events enable new capabilities: execution velocity metrics, rationalization frequency tracking, circuit breaker activation rates, and per-agent performance auditing.
- This ADR intentionally depends on spec-triangle-sync to avoid defining the REQ level twice. The dependency chain is: spec-triangle-sync → tests-for-spec → task-level-governance.
