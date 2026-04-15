---
id: OBPI-0.29.0-02-tasks-show
parent: ADR-0.29.0-task-management-system-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-02: Tasks Show

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-02 --- "Evaluate tasks show subcommand --- detailed task display"`

## OBJECTIVE

Evaluate opsdev's `tasks show` subcommand against gzkit's existing detail-display surfaces (`gz chores show`, `gz adr report`). Determine whether `tasks show` provides task-detail capabilities that gzkit lacks. The evaluation must compare: what detail does `tasks show` render, what metadata does it surface, and does gzkit already provide equivalent detail through its chore/OBPI/ADR detail views?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks show` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/chores.py` (`gz chores show`), `src/gzkit/commands/adr.py` (`gz adr report`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task detail display may overlap with chore detail or OBPI brief rendering
- If `tasks show` renders metadata that gzkit's existing detail views do not surface, the gap is real
- If `tasks show` is essentially `gz chores show` under a different name, it should be excluded

## NON-GOALS

- Rewriting gzkit's existing detail views to match opsdev's interface
- Absorbing the command without understanding what metadata it surfaces
- Changing gzkit's output format conventions without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks show` implementation completely
1. Map the metadata it surfaces against gzkit's existing detail views
1. Document comparison: metadata coverage, output format, user experience
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing detail views are sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.29.0-02-01: Read the `tasks show` implementation completely
- [x] REQ-0.29.0-02-02: Map the metadata it surfaces against gzkit's existing detail views
- [x] REQ-0.29.0-02-03: Document comparison: metadata coverage, output format, user experience
- [x] REQ-0.29.0-02-04: Record decision with rationale: Absorb / Adapt / Exclude
- [x] REQ-0.29.0-02-05: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.29.0-02-06: If Exclude: document why gzkit's existing detail views are sufficient


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
