---
id: OBPI-0.29.0-03-tasks-sync
parent_adr: ADR-0.29.0-task-management-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-03: Tasks Sync

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-03 --- "Evaluate tasks sync subcommand --- task state synchronization"`

## OBJECTIVE

Evaluate opsdev's `tasks sync` subcommand against gzkit's existing synchronization surfaces (`gz implement`, `gz git-sync`). Determine whether `tasks sync` provides state synchronization capabilities that gzkit lacks. The evaluation must compare: what state does `tasks sync` synchronize, between which systems, and does gzkit already cover this through its implementation tracking or git-sync workflows?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks sync` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/implement.py` (`gz implement`), `src/gzkit/commands/git_sync.py` (`gz git-sync`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task synchronization may overlap with `gz implement` (ADR/OBPI state tracking) or `gz git-sync` (file synchronization)
- If `tasks sync` bridges task state with an external system (e.g., superpowers), it may be project-specific
- If `tasks sync` provides governance-generic state reconciliation, the gap is real

## NON-GOALS

- Rewriting gzkit's existing sync commands to match opsdev's interface
- Absorbing external-system integrations that are project-specific
- Changing gzkit's state management model without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks sync` implementation completely
1. Map the synchronization targets against gzkit's existing sync surfaces
1. Document comparison: state model, sync direction, conflict resolution, idempotency
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing sync surfaces are sufficient

## ALLOWED PATHS

- `src/gzkit/commands/` --- target for absorbed commands
- `tests/` --- tests for absorbed commands
- `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/` --- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
