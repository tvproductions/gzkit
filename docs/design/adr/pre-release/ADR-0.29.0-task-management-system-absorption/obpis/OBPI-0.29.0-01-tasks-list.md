---
id: OBPI-0.29.0-01-tasks-list
parent: ADR-0.29.0-task-management-system-absorption
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-01: Tasks List

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-01 --- "Evaluate tasks list subcommand --- task enumeration and filtering"`

## OBJECTIVE

Evaluate opsdev's `tasks list` subcommand against gzkit's existing enumeration surfaces (`gz chores list`, `gz status --table`, `gz adr report`). Determine whether `tasks list` fills a genuine gap in gzkit's governance model or duplicates existing functionality. The evaluation must compare: what entities does `tasks list` enumerate, what filters does it support, and does gzkit already cover this with its chore/OBPI/ADR listing commands?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks list` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/chores.py` (`gz chores list`), `src/gzkit/commands/status.py` (`gz status`), `src/gzkit/commands/adr.py` (`gz adr report`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task enumeration may overlap with chore listing, OBPI enumeration, or ADR status
- If `tasks list` manages a different entity type (discrete work items vs governance artifacts), the gap is real
- If `tasks list` is essentially `gz chores list` under a different name, it should be excluded

## NON-GOALS

- Rewriting gzkit's existing listing commands to match opsdev's interface
- Absorbing the command without understanding what "task" means in opsdev's model
- Changing gzkit's governance entity model (ADR/OBPI/chore) without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks list` implementation completely
1. Map the entity it enumerates against gzkit's existing entities (ADRs, OBPIs, chores)
1. Document comparison: entity model, filters, output format, integration points
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing surfaces are sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.29.0-01-01: Read the `tasks list` implementation completely
- [x] REQ-0.29.0-01-02: Map the entity it enumerates against gzkit's existing entities (ADRs, OBPIs, chores)
- [x] REQ-0.29.0-01-03: Document comparison: entity model, filters, output format, integration points
- [x] REQ-0.29.0-01-04: Record decision with rationale: Absorb / Adapt / Exclude
- [x] REQ-0.29.0-01-05: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.29.0-01-06: If Exclude: document why gzkit's existing surfaces are sufficient


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
