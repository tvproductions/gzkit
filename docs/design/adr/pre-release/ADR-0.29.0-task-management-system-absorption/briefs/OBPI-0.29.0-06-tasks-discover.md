---
id: OBPI-0.29.0-06-tasks-discover
parent_adr: ADR-0.29.0-task-management-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-06: Tasks Discover

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-06 --- "Evaluate tasks discover subcommand --- task discovery and cataloging"`

## OBJECTIVE

Evaluate opsdev's `tasks discover` subcommand against gzkit's existing discovery surfaces (`gz chores list`, `gz state --json`, brief scanning). Determine whether `tasks discover` provides task discovery capabilities that gzkit lacks. The evaluation must compare: how does `tasks discover` find tasks, what sources does it scan, and does gzkit already discover equivalent work items through its OBPI/chore/ADR scanning?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks discover` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/chores.py` (`gz chores list`), `src/gzkit/commands/state.py` (`gz state`), brief scanning logic

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task discovery may overlap with chore discovery or OBPI brief enumeration
- If `tasks discover` scans sources that gzkit does not (e.g., TODO comments, issue trackers, external systems), the gap may be real
- If `tasks discover` scans the same brief/config files that gzkit already reads, it should be excluded

## NON-GOALS

- Rewriting gzkit's existing discovery mechanisms
- Absorbing project-specific discovery sources
- Changing gzkit's entity model to add a "task" type without deliberate design

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks discover` implementation completely
1. Map the discovery sources against gzkit's existing discovery surfaces
1. Document comparison: sources scanned, entity types discovered, output format
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing discovery is sufficient

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
