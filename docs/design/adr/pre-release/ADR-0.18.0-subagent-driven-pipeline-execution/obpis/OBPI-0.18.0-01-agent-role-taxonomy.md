---
id: OBPI-0.18.0-01-agent-role-taxonomy
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 1
lane: Lite
status: Completed
---

# OBPI-0.18.0-01: Agent Role Taxonomy and Handoff Protocols

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #1 — "Agent role taxonomy: four roles, handoff protocols, conflict resolution (subsumes ADR-pool.agent-role-specialization)"

**Status:** Completed

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
- `.claude/agents/implementer.md` — implementer agent file definition
- `.claude/agents/spec-reviewer.md` — spec compliance reviewer agent file definition
- `.claude/agents/quality-reviewer.md` — code quality reviewer agent file definition
- `.claude/agents/narrator.md` — narrator agent file definition

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
1. REQUIREMENT: Each role MUST be delivered as a `.claude/agents/{role}.md` file with YAML frontmatter specifying `tools`, `model`, `permissionMode`, `maxTurns`, and `skills` — the Claude Code primitives that enforce role boundaries at dispatch time.
1. REQUIREMENT: Tool allowlists MUST enforce role boundaries structurally (not just via prompt instruction). Reviewers MUST NOT have Edit/Write tools. Implementers MUST have full write access.
1. NEVER: Allow roles to be vendor-specific — roles are abstract; vendor binding is deployment.
1. ALWAYS: A single agent session CAN fill multiple roles sequentially.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.18.0-01-01: REQUIREMENT: Define exactly four roles: Planner, Implementer, Reviewer, Narrator.
- [x] REQ-0.18.0-01-02: REQUIREMENT: Each role MUST specify what artifacts it produces and what artifacts it consumes.
- [x] REQ-0.18.0-01-03: REQUIREMENT: Handoff protocol MUST define the structured result format between roles (e.g., implementer returns `DONE`/`BLOCKED`/`NEEDS_CONTEXT`/`DONE_WITH_CONCERNS`).
- [x] REQ-0.18.0-01-04: REQUIREMENT: Conflict resolution MUST specify precedence when two agents touch the same file.
- [x] REQ-0.18.0-01-05: REQUIREMENT: Each role MUST be delivered as a `.claude/agents/{role}.md` file with YAML frontmatter specifying `tools`, `model`, `permissionMode`, `maxTurns`, and `skills` — the Claude Code primitives that enforce role boundaries at dispatch time.
- [x] REQ-0.18.0-01-06: REQUIREMENT: Tool allowlists MUST enforce role boundaries structurally (not just via prompt instruction). Reviewers MUST NOT have Edit/Write tools. Implementers MUST have full write access.
- [x] REQ-0.18.0-01-07: NEVER: Allow roles to be vendor-specific — roles are abstract; vendor binding is deployment.
- [x] REQ-0.18.0-01-08: ALWAYS: A single agent session CAN fill multiple roles sequentially.


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
- **Agent file primitives:**
  - `tools: Read, Edit, Write, Glob, Grep, Bash` — full write access
  - `permissionMode: acceptEdits` — non-blocking file modifications
  - `maxTurns: 25` — bounded loop to prevent runaway implementation
  - `skills: [superpowers-tdd]` — TDD discipline injected into context
  - `hooks.PreToolUse` on Edit/Write — validates file paths against brief allowlist

### Reviewer

- **Produces:** Review verdicts (PASS/FAIL/CONCERNS), specific findings with severity
- **Consumes:** Code changes from implementer, plan/brief requirements, quality criteria
- **Pipeline mapping:** Stage 2 (post-task review), Stage 3 (REQ verification)
- **Two sub-roles:**
  - **Spec Compliance Reviewer:** Verifies code matches plan/brief requirements line-by-line
  - **Code Quality Reviewer:** Evaluates architecture, SOLID, test coverage, maintainability
- **Agent file primitives (both sub-roles):**
  - `tools: Read, Glob, Grep` — **read-only enforced structurally** (no Edit/Write/Bash)
  - `maxTurns: 15` — reviews are bounded; escalate rather than loop
  - Spec reviewer `skills: [brief-requirements]` — brief requirements injected for line-by-line verification
  - Quality reviewer `skills: [code-quality-criteria]` — SOLID, maintainability criteria injected

### Narrator

- **Produces:** Evidence presentations, ceremony artifacts, documentation updates
- **Consumes:** Implementation results, verification outputs, attestation records
- **Pipeline mapping:** Stage 4 (ceremony presentation), Stage 5 (documentation sync)
- **Agent file primitives:**
  - `tools: Read, Glob, Grep, Bash` — reads evidence, runs presentation/sync commands
  - `maxTurns: 10` — ceremony and sync are bounded operations

## Agent File Templates (Design Input)

Each role is delivered as a `.claude/agents/` Markdown file. The controller overrides `model` per-dispatch based on task complexity (OBPI-05).

**`.claude/agents/implementer.md`:**
```yaml
---
name: implementer
description: Implements plan tasks with TDD discipline. Dispatched per-task by the pipeline controller.
tools: Read, Edit, Write, Glob, Grep, Bash
model: inherit
permissionMode: acceptEdits
maxTurns: 25
---
```

**`.claude/agents/spec-reviewer.md`:**
```yaml
---
name: spec-reviewer
description: Verifies implementation matches plan/brief requirements. Read-only independent review.
tools: Read, Glob, Grep
model: inherit
maxTurns: 15
---
```

**`.claude/agents/quality-reviewer.md`:**
```yaml
---
name: quality-reviewer
description: Evaluates code architecture, SOLID, test coverage, maintainability. Read-only independent review.
tools: Read, Glob, Grep
model: inherit
maxTurns: 15
---
```

**`.claude/agents/narrator.md`:**
```yaml
---
name: narrator
description: Presents evidence for ceremony and documentation sync. Reads implementation and verification outputs.
tools: Read, Glob, Grep, Bash
model: inherit
maxTurns: 10
---
```

## Edge Cases

- A single agent fills Implementer + Reviewer sequentially (allowed but reviewer MUST re-read code independently, not trust implementer's report)
- Two implementer subagents dispatched for tasks that unexpectedly overlap files (conflict resolution: first-to-commit wins; second must rebase)
- Reviewer finds critical issue but implementer subagent is already terminated (orchestrator dispatches new implementer with reviewer feedback)
- Agent file `maxTurns` exceeded before task completion — treat as BLOCKED, escalate to controller

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

### Implementation Summary

- Module: `src/gzkit/roles.py` — four roles (Planner, Implementer, Reviewer, Narrator) as Pydantic models with artifact contracts, tool boundary validation, and conflict resolution
- Tests: `tests/test_roles.py` — 33 unit tests across 7 test classes (TestRoleTaxonomy, TestToolBoundaries, TestConflictResolution, TestHandoffProtocol, TestReviewResult, TestModelImmutability, TestStageMapping)
- Agent files: `.claude/agents/{implementer,spec-reviewer,quality-reviewer,narrator}.md` — YAML frontmatter with tools, model, permissionMode, maxTurns
- Pool ADR: `ADR-pool.agent-role-specialization` marked Superseded
- Coverage: 99% on `src/gzkit/roles.py`

### Key Proof

```bash
$ uv run -m unittest tests.test_roles -v
test_exactly_four_roles_defined ... ok
test_reviewer_has_no_write_tools ... ok
test_validate_tool_boundaries_all_roles_clean ... ok
test_precedence_order ... ok
test_handoff_result_roundtrip ... ok
...
Ran 33 tests in 0.001s
OK
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained (99%)
- [x] **Pool ADR:** `ADR-pool.agent-role-specialization` marked Superseded
- [x] **OBPI Completion:** Record evidence in brief
