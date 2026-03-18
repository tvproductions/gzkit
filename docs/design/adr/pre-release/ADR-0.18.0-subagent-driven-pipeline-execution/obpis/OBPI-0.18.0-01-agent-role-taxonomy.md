---
id: OBPI-0.18.0-01-agent-role-taxonomy
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 1
lane: Lite
status: Accepted
---

# OBPI-0.18.0-01: Agent Role Taxonomy and Handoff Protocols

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #1 — "Agent role taxonomy: four roles, handoff protocols, conflict resolution (subsumes ADR-pool.agent-role-specialization)"

**Status:** Accepted

## Objective

Define four universal agent roles — Planner, Implementer, Reviewer, Narrator — with explicit
boundaries, handoff artifacts, and conflict resolution rules. This OBPI subsumes the intent of
`ADR-pool.agent-role-specialization` by implementing its target scope within the pipeline context.

Roles are project-level abstractions. Vendor assignment (which model fills which role) is a
session-level decision made by the pipeline orchestrator.

## Lane

**Lite** — Internal taxonomy definition; no external CLI/API/schema contract changes in this OBPI.
The `gz roles` CLI surface ships in OBPI-05.

## Allowed Paths

- `src/gzkit/roles.py` — role taxonomy data model and handoff contracts
- `tests/test_roles.py` — role taxonomy validation and handoff protocol tests
- `docs/design/adr/pool/ADR-pool.agent-role-specialization.md` — mark as Superseded

## Denied Paths

- `src/gzkit/pipeline_runtime.py` — runtime integration belongs to OBPI-05
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — skill updates belong to OBPI-05
- `src/gzkit/commands/` — CLI surface belongs to OBPI-05
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Define exactly four roles: Planner, Implementer, Reviewer, Narrator.
1. REQUIREMENT: Each role MUST specify what artifacts it produces and what artifacts it consumes.
1. REQUIREMENT: Handoff protocol MUST define the structured result format between roles (e.g., implementer returns `DONE`/`BLOCKED`/`NEEDS_CONTEXT`/`DONE_WITH_CONCERNS`).
1. REQUIREMENT: Conflict resolution MUST specify precedence when two agents touch the same file.
1. NEVER: Allow roles to be vendor-specific — roles are abstract; vendor binding is deployment.
1. ALWAYS: A single agent session CAN fill multiple roles sequentially.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Role Definitions (Design Input)

### Planner

- **Produces:** ADR documents, OBPI briefs, implementation plans, dependency graphs
- **Consumes:** User intent, codebase state, governance constraints
- **Pipeline mapping:** Pre-pipeline (plan mode), Stage 1 context loading

### Implementer

- **Produces:** Code changes, tests, commit-ready file sets, structured result status
- **Consumes:** Plan task with scoped context (allowed files, test expectations, brief requirements)
- **Pipeline mapping:** Stage 2 (dispatched per task)
- **Result contract:** `{status: DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED, files_changed: [...], tests_added: [...], concerns: [...]}`

### Reviewer

- **Produces:** Review verdicts (PASS/FAIL/CONCERNS), specific findings with severity
- **Consumes:** Code changes from implementer, plan/brief requirements, quality criteria
- **Pipeline mapping:** Stage 2 (post-task review), Stage 3 (REQ verification)
- **Two sub-roles:**
  - **Spec Compliance Reviewer:** Verifies code matches plan/brief requirements line-by-line
  - **Code Quality Reviewer:** Evaluates architecture, SOLID, test coverage, maintainability

### Narrator

- **Produces:** Evidence presentations, ceremony artifacts, documentation updates
- **Consumes:** Implementation results, verification outputs, attestation records
- **Pipeline mapping:** Stage 4 (ceremony presentation), Stage 5 (documentation sync)

## Edge Cases

- A single agent fills Implementer + Reviewer sequentially (allowed but reviewer MUST re-read code independently, not trust implementer's report)
- Two implementer subagents dispatched for tasks that unexpectedly overlap files (conflict resolution: first-to-commit wins; second must rebase)
- Reviewer finds critical issue but implementer subagent is already terminated (orchestrator dispatches new implementer with reviewer feedback)

## Quality Gates (Lite)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 2: TDD

- [ ] Unit tests validate role taxonomy data model
- [ ] Unit tests validate handoff result contract serialization
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Coverage:** Coverage >= 40% maintained
- [ ] **Pool ADR:** `ADR-pool.agent-role-specialization` marked Superseded
- [ ] **OBPI Completion:** Record evidence in brief
