---
id: OBPI-0.29.0-07-tasks-tidy
parent: ADR-0.29.0-task-management-system-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-07: Tasks Tidy

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-07 --- "Evaluate tasks tidy subcommand --- task cleanup and maintenance"`

## OBJECTIVE

Evaluate opsdev's `tasks tidy` subcommand against gzkit's existing cleanup surfaces (`gz closeout`, `gz adr audit-check`). Determine whether `tasks tidy` provides task cleanup capabilities that gzkit lacks. The evaluation must compare: what does `tasks tidy` clean up, what state transitions does it manage, and does gzkit already cover this through its closeout or audit workflows?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks tidy` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/closeout.py` (`gz closeout`), `src/gzkit/commands/adr.py` (`gz adr audit-check`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task tidying may overlap with ADR closeout or audit cleanup
- If `tasks tidy` manages task-level cleanup distinct from ADR/OBPI lifecycle, the gap may be real
- If `tasks tidy` is essentially "archive completed tasks," it may map to existing closeout patterns

## NON-GOALS

- Rewriting gzkit's existing cleanup workflows to match opsdev's interface
- Absorbing project-specific cleanup logic
- Changing gzkit's lifecycle state machine without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks tidy` implementation completely
1. Map the cleanup operations against gzkit's existing cleanup surfaces
1. Document comparison: what is cleaned, state transitions, idempotency, safety checks
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing cleanup surfaces are sufficient

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
