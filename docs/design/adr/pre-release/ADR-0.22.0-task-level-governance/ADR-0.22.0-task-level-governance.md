---
id: ADR-0.22.0-task-level-governance
status: Proposed
semver: 0.22.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-20
promoted_from: ADR-pool.task-level-governance
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.22.0: Task-Level Governance

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit existing plan-file task formats — catalog how tasks appear in `.claude/plans/` files today (numbered lists, checkboxes, etc.) to understand what the TASK entity must absorb.
  1. Catalog existing ledger event types in `src/gzkit/events.py` — understand the event model patterns for adding TASK events.
  1. Review ADR-0.20.0 and ADR-0.21.0 to understand the REQ entity model and traceability chain this ADR extends.

**Date Added:** 2026-03-20
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.22.0
**Area:** Governance Hierarchy — Fourth Tier

## Agent Context Frame — MANDATORY

**Role:** Governance architect completing the four-tier hierarchy by formalizing TASK as a first-class entity.

**Purpose:** When this ADR is complete, gzkit's governance model has four typed tiers: ADR → OBPI → REQ → TASK. TASKs are the execution leaf — individually traced in the ledger, linked to parent REQs, and referenceable in git commits. The subagent dispatch model (ADR-0.18.0) can dispatch implementers per typed TASK entity instead of per informal plan-file step.

**Goals:**

- TASK entity has a Pydantic model with identifier scheme and lifecycle states
- TASK ledger events track start, completion, blocking, and escalation
- Git commit messages reference TASK IDs for four-tier traceability
- `gz task` CLI manages task lifecycle within pipeline execution
- TASK status integrates into `gz status` and `gz state` reporting

**Critical Constraint:** TASK-level tracing is advisory for Lite lane and required for Heavy lane. This preserves the principle that Lite work has lower ceremony overhead. TASKs must work with both formal plans (Claude Code plan mode) and informal checklists.

**Anti-Pattern Warning:** A failed implementation looks like: TASKs that add ceremony without value — requiring agents to manually create TASK entities before doing work, when the plan file already captures the same information. TASKs must be derivable from existing plan artifacts, not a parallel bookkeeping burden.

**Integration Points:**

- `src/gzkit/tasks.py` — TASK entity model and lifecycle
- `src/gzkit/events.py` — TASK ledger event types
- `src/gzkit/commands/task.py` — CLI surface
- `src/gzkit/pipeline_runtime.py` — pipeline integration (Stage 2 dispatch)
- ADR-0.20.0 REQ entity — TASK→REQ linkage
- ADR-0.18.0 subagent dispatch — consumer of TASK entities

---

## Feature Checklist — Appraisal of Completeness

1. **OBPI-0.22.0-01:** TASK entity model with identifier scheme, lifecycle
   states, valid transitions, and plan-derived creation
2. **OBPI-0.22.0-02:** TASK ledger events for start, resume, complete, block,
   and escalate semantics using the existing event model patterns
3. **OBPI-0.22.0-03:** Git commit linkage contract for TASK ID trailers and
   four-tier chain resolution
4. **OBPI-0.22.0-04:** `gz task` CLI with list, start, complete, block, and
   escalate lifecycle commands
5. **OBPI-0.22.0-05:** Status and state integration with task-level reporting,
   escalated visibility, and lane-sensitive advisory/required policy surfacing

Support obligations for the checklist above:

- External contract changed (Heavy lane): new `gz task` CLI command and
  changes to `gz status` / `gz state` output
- stdlib unittest guards TASK model, ledger events, commit linkage, and
  lifecycle transitions
- BDD scenarios cover `gz task` CLI and task-aware reporting surfaces
- Docs updated in `docs/user/commands/task.md`,
  `docs/user/commands/status.md`, `docs/user/commands/state.md`, and
  `docs/user/concepts/four-tier-hierarchy.md`
- Each numbered ADR checklist item maps to one brief and one concrete
  verification-command set

## Intent

gzkit governs work at three typed tiers: ADR (architectural intent), OBPI (implementation increment), and REQ (acceptance criterion). The fourth tier — TASK (execution step) — exists informally as plan-file steps and checklist items but has no typed model, no ledger events, and no traceability back to REQs.

This matters because ADR-0.18.0 (subagent-driven pipeline execution) dispatches implementer subagents "per task." Without a formal TASK entity, dispatch operates on untyped plan-file text, and there's no ledger trail from a completed task back through REQ → OBPI → ADR. The four-tier hierarchy is incomplete.

This ADR completes the hierarchy by defining TASK as a first-class Pydantic entity with:
- An identifier scheme linking to parent REQ (`TASK-<semver>-<obpi>-<req>-<seq>`)
- Lifecycle states (pending, in_progress, completed, blocked, escalated)
- Ledger events for start/resume, completion, blocking, and escalation
- Git commit linkage for full traceability
- CLI surfaces for lifecycle management

## Decision

- Define TASK entity as a Pydantic BaseModel with identifier scheme `TASK-<semver>-<obpi>-<req>-<seq>` and lifecycle states {pending, in_progress, completed, blocked, escalated}. Follow the `ReqId`/`ReqEntity` pattern in `src/gzkit/triangle.py`: frozen `ConfigDict`, regex-based `parse()` classmethod, `__str__` round-trip, and `Field(...)` with descriptions.
- Define TASK ledger events: `task_started`, `task_completed`,
  `task_blocked`, `task_escalated` — following the existing event model
  patterns in `events.py`. `task_started` is emitted both for initial
  `pending -> in_progress` starts and `blocked -> in_progress` resumes; no
  separate resume event is introduced in this ADR.
- Define git commit linkage contract: TASK ID in commit message trailers (e.g., `Task: TASK-0.20.0-01-01-01`), parseable for four-tier traceability.
- Build `gz task` CLI for lifecycle management: `gz task list`,
  `gz task start`, `gz task complete`, `gz task block`, `gz task escalate`.
- Integrate TASK status into `gz status` and `gz state` reporting, including
  escalated-task visibility and lane-sensitive advisory/required semantics.
- TASK-level tracing is advisory for Lite lane, required for Heavy lane, and
  this policy must be visible in reporting/output rather than remaining an
  ADR-only rule.
- TASKs are derivable from plan files — agents can auto-create TASKs from plan steps, not manually author them.

### Boundary with ADR-0.18.0

| Owned by 0.22.0 | Owned by 0.18.0 |
|------------------|-----------------|
| TASK entity model | Subagent dispatch logic |
| TASK ledger events | Implementer/Reviewer role definitions |
| TASK lifecycle states | HandoffResult contract |
| `gz task` CLI | `gz roles` CLI |
| Git commit linkage | Pipeline runtime integration |

ADR-0.18.0 is a **consumer** of the TASK entity. It dispatches implementers per TASK and records HandoffResults against TASK IDs. But the TASK entity definition, ledger events, and CLI are owned here.

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Keep tasks informal** | Dispatch operates on untyped text. No ledger trail, no audit, no traceability. The four-tier hierarchy remains incomplete. |
| **Merge TASK into REQ** | REQs are acceptance criteria (what must be true); TASKs are execution steps (what work to do). Conflating them loses the distinction between specification and execution. |
| **Complex TASK workflow engine** | gzkit is a governance CMS, not a project management tool. TASK lifecycle is simple (5 states, 5 valid transitions, 4 event kinds with `task_started` reused for resume). Over-engineering the state machine adds complexity without value. |
| **External task tracker integration** | Would require API dependencies. gzkit's principle is local, ledger-first governance. TASKs derive from the same JSONL ledger as everything else. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | TASK entity model | No typed representation of execution steps. Dispatch operates on strings. |
| 2 | TASK ledger events | TASKs exist but start, resume, block, completion, and escalation state changes aren't recorded coherently. No audit trail for execution. |
| 3 | Git commit linkage | TASKs are ledger-tracked but commits don't reference them. Four-tier traceability breaks at the TASK↔commit boundary. |
| 4 | gz task CLI | TASK entity exists but operators can't manage lifecycle transitions, including escalation. No external surface. |
| 5 | Status and state integration | TASKs are managed but invisible in standard reporting, and operators can't tell whether task tracing is advisory or required for the active lane. |

## Interfaces

- **CLI (external contract):** `uv run gz task list|start|complete|block|escalate` — new commands
- **CLI (external contract):** `uv run gz status` — gains task-level section
- **Ledger (internal):** New event types: `task_started`, `task_completed`, `task_blocked`, `task_escalated`
- **Internal:** `src/gzkit/tasks.py` — TASK entity model

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.22.0-01 | TASK entity model: Pydantic model, identifier scheme, lifecycle states | Lite | Pending |
| 2 | OBPI-0.22.0-02 | TASK ledger events: start/resume, completed, blocked, escalated | Lite | Pending |
| 3 | OBPI-0.22.0-03 | Git commit linkage: TASK ID in commit trailers, parsing for traceability | Lite | Pending |
| 4 | OBPI-0.22.0-04 | `gz task` CLI: list, start, complete, block, escalate lifecycle commands | Heavy | Pending |
| 5 | OBPI-0.22.0-05 | Status and state integration: TASK data in `gz status` and `gz state`, including escalated counts and lane-policy surfacing | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.22.0-*.md`

**Dependency Graph:**

```text
OBPI-01 (entity model)
  ├──► OBPI-02 (ledger events)
  ├──► OBPI-03 (git linkage)
  └──► OBPI-04 (CLI)
OBPI-02 (ledger events)
  └──► OBPI-04 (CLI) ──► OBPI-05 (status integration)
```

**Critical path:** OBPI-01 → OBPI-02 → OBPI-04 → OBPI-05

**Parallelization:** After OBPI-01, OBPIs 02 and 03 can run concurrently.
OBPI-04 depends on OBPI-02 for event emission semantics. OBPI-05 needs OBPI-04.

**Verification spine:**

- OBPI-01: `uv run -m unittest tests.test_tasks -v`
- OBPI-02: `uv run -m unittest tests.test_tasks -v`
- OBPI-03: `uv run -m unittest tests.test_tasks -v`
- OBPI-04: `uv run gz task --help`,
  `uv run -m behave features/task_governance.feature`
- OBPI-05: `uv run gz status`, `uv run gz state --json`,
  `uv run mkdocs build --strict`

## Non-Goals

- No replacement of superpowers behavioral methodology at the execution level.
- No mandatory TASK tracing for Lite lane — advisory only.
- No changes to ADR or OBPI governance tiers.
- No cloud or external storage requirements. TASK state derives from the ledger.
- No complex workflow engine or state machine beyond 5 states, 5 valid
  transitions, and 4 event kinds.

### Scope Creep Guardrails

- Subagent dispatch per TASK → ADR-0.18.0
- Superpowers behavioral pattern mapping → future ADR (after dispatch is proven)
- Execution memory graph from TASK events → `ADR-pool.execution-memory-graph`
- TASK-level metrics and velocity tracking → `ADR-pool.session-productivity-metrics`

## Rationale

The four-tier governance hierarchy (ADR → OBPI → REQ → TASK) is gzkit's distinguishing architecture. Three tiers are formalized; one is not. This creates a traceability gap at the execution level — the most granular and most frequent governance activity has no typed representation.

ADR-0.18.0 exposes this gap directly: its subagent dispatch model dispatches "per task" but the dispatch boundary is an informal plan-file step. Formalizing TASK gives the dispatch model a typed input, gives the ledger execution-level events, and gives operators visibility into task-level progress through standard reporting surfaces.

The design is deliberately simple: 5 lifecycle states, 5 valid transitions,
4 ledger event kinds, and identifier-based linkage. `task_started` covers both
initial start and resume from blocked state so the event taxonomy stays small.
gzkit is a governance CMS, not a project management tool. TASK captures what
happened during execution with enough structure for traceability, not enough to
become a workflow engine.

## Consequences

- Four-tier hierarchy is complete: ADR → OBPI → REQ → TASK
- ADR-0.18.0 (subagent dispatch) gains typed TASK input for dispatch
- Ledger gains execution-level events for audit and metrics
- `gz status` gains task-level visibility
- Git commits gain four-tier traceability via TASK ID trailers

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_tasks.py`
- **BDD (external contract changed):** `features/task_governance.feature`
- **Docs:** `docs/user/commands/task.md`, `docs/user/concepts/four-tier-hierarchy.md`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.22.0`
- **Promoted from:** `ADR-pool.task-level-governance`
- **Depends on:** ADR-0.20.0 (REQ entity, triangle model), ADR-0.21.0 (test traceability)
- **Consumed by:** ADR-0.18.0 (subagent dispatch)

### Source & Contracts

- Core modules: `src/gzkit/tasks.py`
- Events: `src/gzkit/events.py` (extended)
- CLI: `src/gzkit/commands/task.py`

### Tests

- Unit: `tests/test_tasks.py`
- BDD: `features/task_governance.feature`

### Docs

- Commands: `docs/user/commands/task.md`
- Concepts: `docs/user/concepts/four-tier-hierarchy.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| src/gzkit/tasks.py | P | TASK model, lifecycle | Test output | |
| src/gzkit/events.py | M | TASK ledger events | Test output | |
| src/gzkit/commands/task.py | P | `gz task` CLI | Test output | |
| docs/user/commands/task.md | P | Command docs | Rendered docs | |

### SIGN-OFF

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.22.0 | Pending | | | |
