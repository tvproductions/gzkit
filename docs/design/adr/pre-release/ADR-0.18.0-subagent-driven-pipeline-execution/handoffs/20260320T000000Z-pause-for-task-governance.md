---
mode: CREATE
adr_id: ADR-0.18.0
branch: main
timestamp: "2026-03-20T00:00:00Z"
agent: claude-code
obpi_id: OBPI-0.18.0-01
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.18.0 — created by claude-code at 2026-03-20T00:00:00Z -->

## Current State Summary

OBPI-0.18.0-01 (Agent Role Taxonomy) pipeline was paused at Stage 4 (ceremony, awaiting attestation). All implementation and verification is complete — 33/33 tests pass, lint clean, typecheck clean, 727 full suite tests pass.

The pipeline was paused because the human identified a dependency ordering issue: ADR-0.18.0's dispatch model dispatches "per task" but TASK is not yet a formal entity. `ADR-pool.task-level-governance` should be promoted first to formalize the TASK entity before building dispatch on top of it.

Implementation artifacts remain on disk and are valid. No attestation was given.

## Important Context

- The four-tier governance hierarchy is ADR -> OBPI -> REQ -> TASK. TASK is the missing leaf — currently informal (plan-file steps).
- OBPI-02 through OBPI-05 of ADR-0.18.0 all dispatch "per task" — they depend on a clear TASK definition.
- `ADR-pool.task-level-governance` is the pool ADR that formalizes TASK as a Pydantic model with schema and ledger events.
- The pool ADR's promotion should define the TASK entity that ADR-0.18.0 OBPIs 02-05 consume.
- OBPI-01 (this one) is purely the role taxonomy — it does NOT depend on TASK directly, but was paused as part of the broader sequencing decision.

## Decisions Made

- **Decision:** Pause OBPI-0.18.0-01 pipeline before attestation to promote ADR-pool.task-level-governance first.
  **Rationale:** The dispatch model's fundamental unit of work is the task. Building dispatch on an informal/undefined entity means retrofitting later. Completing the governance model (TASK formalization) before execution machinery is architecturally cleaner.
  **Alternatives rejected:** (1) Continue with informal tasks and retrofit later — creates technical debt. (2) Define TASK inline within ADR-0.18.0 — violates scope, that's pool ADR territory.

## Immediate Next Steps

1. Promote `ADR-pool.task-level-governance` to a versioned ADR (e.g., ADR-0.19.0 or next available semver) via `/gz-adr-promote`
2. Implement the TASK entity: Pydantic model, schema, ledger event types
3. After TASK ADR is completed, resume OBPI-0.18.0-01 pipeline with `--from=ceremony` (implementation and verification are done)
4. Update ADR-0.18.0 dependency graph to show TASK formalization as a prerequisite
5. Consider whether OBPI-0.18.0-01's `HandoffResult` should reference a formal TASK ID

## Pending Work / Open Loops

- OBPI-0.18.0-01 needs attestation and Stage 5 sync (resume with `--from=ceremony`)
- OBPIs 02-05 are blocked on both OBPI-01 completion and TASK formalization
- `ADR-pool.agent-role-specialization` is already marked Superseded — no action needed
- The four `.claude/agents/` files are created but not yet governance-synced

## Verification Checklist

- [x] `uv run gz test` passes (727 tests)
- [x] `uv run gz lint` clean
- [x] `uv run gz typecheck` clean
- [x] `uv run -m unittest tests.test_roles -v` passes (33/33)
- [ ] Branch matches: `git branch --show-current` -> main
- [ ] No pipeline markers active (cleaned up)
- [ ] No OBPI locks active (released)

## Evidence / Artifacts

- `src/gzkit/roles.py` — role taxonomy data model (four roles, handoff contracts, conflict resolution, tool boundary validation)
- `tests/test_roles.py` — 33 unit tests across 7 test classes
- `.claude/agents/implementer.md` — implementer agent file (write tools, acceptEdits, maxTurns=25)
- `.claude/agents/spec-reviewer.md` — spec compliance reviewer (read-only, maxTurns=15)
- `.claude/agents/quality-reviewer.md` — code quality reviewer (read-only, maxTurns=15)
- `.claude/agents/narrator.md` — narrator agent file (read+bash, maxTurns=10)
