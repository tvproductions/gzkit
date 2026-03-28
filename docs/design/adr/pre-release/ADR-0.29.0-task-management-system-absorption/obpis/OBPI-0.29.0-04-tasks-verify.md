---
id: OBPI-0.29.0-04-tasks-verify
parent: ADR-0.29.0-task-management-system-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-04: Tasks Verify

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-04 --- "Evaluate tasks verify subcommand --- task verification and validation"`

## OBJECTIVE

Evaluate opsdev's `tasks verify` subcommand against gzkit's existing verification surfaces (`gz gates`, `gz validate`, `gz adr audit-check`). Determine whether `tasks verify` provides verification capabilities that gzkit lacks. The evaluation must compare: what does `tasks verify` validate, what evidence does it produce, and does gzkit already cover this through its gate verification or audit-check workflows?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks verify` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/gates.py` (`gz gates`), `src/gzkit/commands/validate.py` (`gz validate`), `src/gzkit/commands/adr.py` (`gz adr audit-check`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task verification may overlap with gate verification or audit-check
- If `tasks verify` checks task-level completion criteria that differ from OBPI gates, the gap is real
- If `tasks verify` is essentially `gz gates` scoped to tasks, it may be redundant

## NON-GOALS

- Rewriting gzkit's existing verification commands to match opsdev's interface
- Absorbing project-specific verification criteria
- Changing gzkit's gate model without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks verify` implementation completely
1. Map the verification criteria against gzkit's existing verification surfaces
1. Document comparison: what is verified, evidence produced, pass/fail semantics
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing verification is sufficient

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
