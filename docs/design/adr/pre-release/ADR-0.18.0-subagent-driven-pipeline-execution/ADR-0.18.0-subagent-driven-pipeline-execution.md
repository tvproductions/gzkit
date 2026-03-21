---
id: ADR-0.18.0-subagent-driven-pipeline-execution
status: Proposed
semver: 0.18.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-17
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.18.0: Subagent-Driven Pipeline Execution

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit current Stage 2 implementation flow in `gz-obpi-pipeline` SKILL.md — identify all inline implementation steps that could become subagent dispatch points.
  1. Extract role-like concepts already implicit in the pipeline (implementer = Stage 2, reviewer = Stage 3) into explicit named roles for reference.
  1. Catalog existing subagent usage patterns in gzkit skills (Explore agents in gz-plan, etc.) as precedent.

Separate prep from change via distinct commits. STOP if current pipeline skill has undocumented behavioral contracts not captured in SKILL.md or pipeline_runtime.py.

**Date Added:** 2026-03-17
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.18.0
**Area:** Pipeline Execution Architecture

## Agent Context Frame — MANDATORY

**Role:** Pipeline architect evolving gz-obpi-pipeline from single-session to multi-agent orchestration.

**Purpose:** When this ADR is complete, the gz-obpi-pipeline dispatches fresh subagents for TASK-level implementation and REQ-level verification, keeping the main session lean as a governance orchestrator. Agent roles (Planner, Implementer, Reviewer, Narrator) have formal definitions, handoff protocols, and conflict resolution rules.

**Goals:**

- Pipeline Stage 2 dispatches implementer subagents per plan task instead of executing inline
- Two-stage review (spec compliance + code quality) runs via independent reviewer subagents after each task
- Stage 3 dispatches parallel verification subagents for non-overlapping REQ paths
- Agent role taxonomy is defined with handoff contracts and conflict resolution
- Pipeline runtime tracks subagent dispatch, status, and result aggregation

**Critical Constraint:** Implementations MUST preserve the Iron Law — the pipeline still runs all 5 stages to completion. Subagent dispatch is an execution strategy within stages, not a license to skip governance stages or stop early.

**Anti-Pattern Warning:** A failed implementation looks like: subagents complete their tasks but the orchestrator treats task completion as pipeline completion. The pipeline stops after Stage 2 because "all tasks are done" without running verification (Stage 3), ceremony (Stage 4), or sync (Stage 5). Subagent dispatch adds complexity to Stage 2 but does NOT change the stage contract.

**Integration Points:**

- `src/gzkit/pipeline_runtime.py` — canonical shared runtime for pipeline stages
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — pipeline skill definition
- `.claude/skills/gz-obpi-lock/SKILL.md` — lock coordination for multi-agent work
- `.claude/agents/` — agent file definitions (Markdown + YAML frontmatter) for each pipeline role
- Claude Code Agent tool — subagent dispatch mechanism (supports `model`, `isolation`, `run_in_background`)
- Claude Code TaskCreate/TaskUpdate — task tracking within sessions

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract changed (Heavy lane): pipeline execution model, runtime command behavior, skill definition
- Tests
  - stdlib unittest guards role taxonomy, dispatch contracts, and result aggregation
  - BDD scenarios for pipeline subagent dispatch lifecycle
- Docs
  - Pipeline skill SKILL.md updated with subagent dispatch architecture
  - Runbook updated with subagent-aware pipeline operation
- OBPI mapping
  - Each numbered ADR checklist item maps to one brief; acceptance recorded in the brief

## Intent

The gz-obpi-pipeline today executes all five governance stages — including all implementation code — in a single agent session. On complex OBPIs with 8+ plan tasks, Stage 2 alone can consume 40-60% of the session's context window, leaving Stages 3-5 (verification, ceremony, sync) operating in compressed or degraded context. The same session that writes code also reviews it, and every task — from a one-line rename to a cross-module refactor — runs on the same model at the same cost.

This ADR evolves the pipeline to a controller/worker architecture: the main session orchestrates governance stages and dispatches fresh subagents for TASK-level implementation and REQ-level verification. Each subagent starts with a clean context scoped to its task, returns a structured result, and is discarded. The orchestrator stays lean for the governance stages that follow.

This pattern is proven at scale by the [superpowers](https://github.com/obra/superpowers) methodology (92k+ stars), which dispatches a fresh implementer subagent per task with two-stage independent review. gzkit's contribution is wrapping this execution pattern in governance infrastructure: ledger-aware dispatch, role-based handoff contracts, and auditable result aggregation within the existing five-stage pipeline lifecycle.

This ADR subsumes `ADR-pool.agent-role-specialization` by defining the role taxonomy as a foundational OBPI. It references but does not depend on `ADR-pool.task-level-governance` — the subagent dispatch pattern works with the pipeline's existing task lists and will naturally consume formal TASK entities when that pool ADR is promoted.

## Decision

- Pipeline Stage 2 (Implement) becomes a controller loop: for each plan task, dispatch a fresh implementer subagent with scoped context (task description, allowed files, test expectations), receive a structured result (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, `BLOCKED`), and advance.
- After each implementer subagent completes, dispatch two independent reviewer subagents: a spec compliance reviewer (verifies code matches the plan/brief requirements) and a code quality reviewer (evaluates architecture, test coverage, maintainability).
- Stage 3 (Verify) dispatches parallel verification subagents for REQ-level checks when requirements have non-overlapping test paths, reducing verification wall-clock time.
- Define four agent roles — Planner, Implementer, Reviewer, Narrator — with explicit handoff contracts (what each role produces for downstream consumption) and conflict resolution rules.
- Model-aware dispatch: simple tasks (1-2 files, mechanical changes) route to economical models; integration tasks and reviews route to capable models.
- Subagent dispatch is an execution strategy within pipeline stages, not a new stage. The Iron Law (all 5 stages to completion) is unchanged.
- The pipeline runtime (`pipeline_runtime.py`) gains subagent dispatch tracking, result aggregation, and status reporting.
- The pipeline skill (`SKILL.md`) is updated with controller/worker architecture documentation.
- Each pipeline role is defined as a reusable `.claude/agents/` Markdown file with YAML frontmatter specifying tool restrictions, model defaults, permission modes, and skill injections — the concrete Claude Code primitives that enforce role boundaries at dispatch time.

### Claude Code Subagent Primitive Mapping

The abstract role and dispatch concepts in this ADR map to concrete Claude Code agent primitives:

| Concept | Claude Code Primitive | Where Defined |
|---------|----------------------|---------------|
| Role boundary enforcement | `tools` allowlist in agent frontmatter | `.claude/agents/{role}.md` |
| Model-aware routing | `model` field in agent frontmatter + per-dispatch override | OBPI-05 model routing config |
| Write permission for implementers | `permissionMode: acceptEdits` | `.claude/agents/implementer.md` |
| Read-only reviewers | `tools: Read, Glob, Grep` (no Edit/Write) | `.claude/agents/spec-reviewer.md`, `quality-reviewer.md` |
| Parallel verification isolation | `isolation: worktree` on Agent tool dispatch | OBPI-04 dispatch logic |
| Concurrent verification | `run_in_background: true` on Agent tool dispatch | OBPI-04 dispatch logic |
| File path enforcement | `hooks.PreToolUse` in agent frontmatter | `.claude/agents/implementer.md` |
| Domain knowledge injection | `skills` field in agent frontmatter | Per-role agent files |
| Agent loop bounds | `maxTurns` field in agent frontmatter | Per-role agent files |

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Bigger context windows** | Treats the symptom (context exhaustion) not the cause (single-session conflation of implementation and governance). Does not address independent review or model optimization. Context windows grow but so does implementation complexity. |
| **Parallel implementer subagents** | File conflicts between concurrent tasks are expensive to resolve. Superpowers explicitly prohibits parallel implementers — sequential dispatch with fresh context is strictly safer. Parallel dispatch is reserved for Stage 3 verification where `isolation: worktree` provides safe concurrent execution. |
| **Skip review for Lite OBPIs** | Lite lane reduces *governance gates* (no BDD/docs/attestation), not *code quality*. Independent review catches bugs regardless of lane. The review protocol is internal and low-overhead. |
| **External CI-based dispatch** | Would require infrastructure beyond the repository. gzkit's principle is that governance runs locally with `uv run gz`. Subagent dispatch via the Agent tool is local, auditable, and requires no external services. |
| **Single-reviewer (not two-stage)** | Superpowers found that spec compliance and code quality are orthogonal concerns — reviewers optimizing for "does it match the spec?" systematically overlook architectural issues, and vice versa. Two reviewers with distinct briefs outperform one reviewer with a combined brief. |
| **Prompt-only role enforcement** | Relying solely on prompt instructions for role boundaries (e.g., "do not modify files") is weaker than Claude Code's `tools` allowlist, which structurally prevents unauthorized tool use. Prompt instructions are best-effort; tool restrictions are enforced. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | Agent Role Taxonomy | No dispatch boundaries — subagents have no defined handoff contracts, conflict resolution, or result formats. Dispatch becomes ad-hoc. |
| 2 | Implementer Dispatch | Stage 2 remains single-session inline. No context isolation, no model-aware routing. The core problem this ADR exists to solve is unaddressed. |
| 3 | Two-Stage Review | No independent review — implementer self-reviews. Quality regressions caught later in Stage 3 or (worse) by the human in Stage 4. |
| 4 | REQ Verification | Stage 3 runs sequentially on all requirements. No wall-clock improvement on OBPIs with many non-overlapping requirements. |
| 5 | Runtime Integration | Dispatch patterns exist but nothing is wired together. No CLI surface, no state tracking, no SKILL.md documentation. Pipeline cannot actually use subagents. |
| 6 | Wire Implementer Dispatch | Stage 2 has dispatch machinery but SKILL.md still executes inline. The core value proposition — fresh subagents per task — is unrealized. |
| 7 | Wire Two-Stage Review | Implementer tasks complete without independent review. Quality regressions caught late or missed entirely. |
| 8 | Wire REQ Verification | Stage 3 verification runs sequentially. No wall-clock improvement from parallel dispatch on multi-REQ briefs. |

## Interfaces

- **CLI (external contract):** `uv run gz obpi pipeline {OBPI-ID}` — execution model changes but command interface is unchanged
- **Skill (external contract):** `/gz-obpi-pipeline` — updated Stage 2/3 dispatch behavior
- **Runtime (internal):** `pipeline_runtime.py` gains subagent dispatch state tracking
- **New CLI surface:** `uv run gz roles` — query role taxonomy and detect unassigned work

## OBPI Decomposition — Work Breakdown Structure (Level 1)

> **OBPI Etymology:** "One Brief Per Item" — where the "Item" is the OBPI entry itself (recursive).
> The OBPI table defines what work exists; each brief (Level 2 WBS) elaborates how to deliver it.

Each OBPI elaborates intent, specifies acceptance criteria, and tracks execution.
The Completion Checklist is substantiated by OBPI fulfillment.

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.18.0-01 | Agent role taxonomy: four roles, handoff protocols, conflict resolution (subsumes ADR-pool.agent-role-specialization) | Lite | Pending |
| 2 | OBPI-0.18.0-02 | Controller/worker Stage 2: dispatch fresh implementer subagents per plan task | Heavy | Pending |
| 3 | OBPI-0.18.0-03 | Two-stage review protocol: spec compliance + code quality reviewer subagents | Lite | Pending |
| 4 | OBPI-0.18.0-04 | REQ-level parallel verification dispatch in Stage 3 | Lite | Pending |
| 5 | OBPI-0.18.0-05 | Pipeline runtime and skill integration: dispatch tracking, result aggregation, model routing | Heavy | Pending |
| 6 | OBPI-0.18.0-06 | Wire implementer dispatch into Stage 2 of the pipeline skill | Heavy | Pending |
| 7 | OBPI-0.18.0-07 | Wire two-stage review into the pipeline flow after each implementation task | Heavy | Pending |
| 8 | OBPI-0.18.0-08 | Wire REQ verification dispatch into Stage 3 | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.18.0-*.md` (each brief is a **Level 2 WBS** element)

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

## Non-Goals

- No replacement of superpowers behavioral methodology at the execution level. Superpowers skills remain the behavioral discipline source (TDD, anti-rationalization, circuit breakers); this ADR adds governance-aware orchestration around that methodology.
- No formal TASK entity definition or ledger events. That is `ADR-pool.task-level-governance` scope. This ADR works with the pipeline's existing task lists and will naturally consume formal TASK entities when that pool ADR is promoted.
- No vendor-specific subagent implementations. The dispatch pattern uses Claude Code's Agent tool today but roles and contracts are vendor-neutral abstractions.
- No changes to Stages 1, 4, or 5 governance logic. Subagent dispatch is scoped to Stages 2 and 3 execution strategy only.
- No mandatory subagent dispatch. A `--no-subagents` fallback preserves current inline execution for debugging and environments without subagent support.

### Scope Creep Guardrails

If any of these emerge during implementation, create a new ADR rather than expanding this one:

- TASK-level ledger events or formal TASK entity schema → `ADR-pool.task-level-governance`
- Cross-ADR subagent coordination (multiple ADRs sharing subagents) → new pool ADR
- Persistent subagent sessions (agents that survive across pipeline runs) → new pool ADR
- Subagent dispatch for Stages 1, 4, or 5 → new pool ADR (this ADR scopes to Stages 2-3 only)

## Dependency Graph and Parallelization

```text
OBPI-01 (role taxonomy)
  ├──► OBPI-02 (implementer dispatch)   ─┐
  ├──► OBPI-03 (reviewer protocol)       ├──► OBPI-05 (runtime integration)
  └──► OBPI-04 (REQ verification)       ─┘
                                           │
                                           ├──► OBPI-06 (wire implementer → Stage 2)
                                           │      └──► OBPI-07 (wire review → after each task)
                                           └──► OBPI-08 (wire REQ verification → Stage 3)
```

**Critical path:** OBPI-01 → OBPI-02 → OBPI-05 → OBPI-06 → OBPI-07

**Parallelization:** After OBPI-01 completes, OBPIs 02, 03, and 04 can run concurrently. OBPI-05 sequences after 02, 03, 04. After OBPI-05, OBPI-06 and OBPI-08 can run concurrently. OBPI-07 sequences after OBPI-06 (review wiring depends on implementer dispatch being wired).

**Theoretical minimum stages:** 5 (01 → 02+03+04 → 05 → 06+08 → 07)

---

## Rationale

The gz-obpi-pipeline currently executes all implementation work in the main session. This creates three measured problems:

1. **Context pollution** — implementation details from Stage 2 consume 40-60% of the session's context window on complex OBPIs (8+ plan tasks). Stages 3-5 then operate in compressed context, increasing the risk of governance step omission — the exact anti-pattern the pipeline was built to prevent. ADR-0.12.0 (enforcement parity) and ADR-0.13.0 (runtime surface) invested heavily in ensuring all 5 stages complete; context exhaustion undermines that investment.

2. **No independent review** — the same session that writes code also verifies it. Self-review is inherently weaker than independent review. The superpowers methodology addresses this with a two-stage review protocol where the reviewer subagent is explicitly told "the implementer may be optimistic — verify everything independently." This separation has demonstrated measurable quality improvement across the superpowers community.

3. **No model optimization** — every task runs on the same model regardless of complexity. A one-line config rename and a cross-module refactor both consume the same model tier. Model-aware routing — matching task complexity to model capability — reduces cost on trivial tasks and ensures complex tasks get the reasoning power they need.

The [superpowers](https://github.com/obra/superpowers) methodology (92k+ stars) has validated the controller/worker pattern across a large community of real development sessions. The key patterns — fresh subagent per task, sequential dispatch, two-stage review, structured result contracts — are directly adopted here. gzkit's contribution is wrapping this execution pattern in governance infrastructure: ledger-aware dispatch, role-based handoff contracts, and auditable result aggregation within the existing five-stage pipeline lifecycle.

**Local precedent:** gzkit already uses subagent dispatch in `gz-plan` (Explore subagents for codebase research) and `gz-obpi-lock` (agent identity resolution). This ADR extends the same pattern to pipeline execution — the highest-value dispatch point.

## Consequences

- Pipeline execution model changes from single-session to multi-agent orchestration
- `ADR-pool.agent-role-specialization` is superseded (subsumed into OBPI-0.18.0-01)
- `ADR-pool.task-level-governance` remains in pool — this ADR builds the execution layer that task-level governance will formalize
- Pipeline runtime gains new state tracking for subagent dispatch and results
- `gz roles` becomes a new CLI surface for role queries
- Pipeline skill SKILL.md grows significantly with controller/worker documentation

## Architectural Exemplar

This ADR follows the structural pattern of [ADR-0.14.0](../ADR-0.14.0-multi-agent-instruction-architecture-unification/ADR-0.14.0-multi-agent-instruction-architecture-unification.md) (Multi-Agent Instruction Architecture Unification):

- Same decomposition style: foundational OBPI (01) → parallel implementation OBPIs (02-04) → integration OBPI (05)
- Same dependency graph shape: fan-out after foundation, fan-in at integration
- Same lane mix: Heavy for external contract changes, Lite for internal protocol
- Improvement over 0.14.0: explicit Alternatives Considered table, checklist necessity table, and scope creep guardrails

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_roles.py`, `tests/test_pipeline_dispatch.py`
- **BDD (external contract changed):** `features/subagent_pipeline.feature`, `features/steps/subagent_pipeline_steps.py`
- **Docs:** `docs/user/concepts/subagent-pipeline.md`, updated `docs/user/runbook.md`

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once Four Gates are green.
- Include the exact command to reproduce the observed behavior, if applicable:

`uv run gz obpi pipeline OBPI-0.18.0-XX`

---

## Evidence Ledger (authoritative summary)

> List **every artifact created or modified** to deliver and accept this ADR. If it wasn't listed here, it didn't happen.

### Provenance

- **Git tag:** `adr-0.18.0`
- **Related issues:** Subsumes `ADR-pool.agent-role-specialization`; references `ADR-pool.task-level-governance`

### Source & Contracts

- CLI / contracts: `src/gzkit/commands/roles.py`
- Core modules: `src/gzkit/pipeline_runtime.py`, `src/gzkit/roles.py`
- Skills: `.claude/skills/gz-obpi-pipeline/SKILL.md`
- Agent files: `.claude/agents/implementer.md`, `.claude/agents/spec-reviewer.md`, `.claude/agents/quality-reviewer.md`, `.claude/agents/narrator.md`

### Tests

- Unit: `tests/test_roles.py`, `tests/test_pipeline_dispatch.py`
- BDD: `features/subagent_pipeline.feature`, `features/steps/subagent_pipeline_steps.py`

### Docs

- Concepts: `docs/user/concepts/subagent-pipeline.md`
- Runbook: `docs/user/runbook.md` (updated)

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: To be completed during implementation

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors (observable, reproducible) | Evidence (link/snippet/hash) | Notes |
|---|---|---|---|---|
| src/gzkit/roles.py | P | Role taxonomy queryable via `gz roles` | Test output | |
| src/gzkit/pipeline_runtime.py | M | Subagent dispatch state tracked | Test output | |
| .claude/skills/gz-obpi-pipeline/SKILL.md | M | Controller/worker architecture documented | File review | |
| docs/user/concepts/subagent-pipeline.md | P | Subagent pipeline concept explained | Rendered docs | |
| docs/user/runbook.md | M | Subagent pipeline operation documented | Rendered docs | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. ...

1. ...

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.18.0 | Completed | Jeffry Babb | 2026-03-21 | completed |
