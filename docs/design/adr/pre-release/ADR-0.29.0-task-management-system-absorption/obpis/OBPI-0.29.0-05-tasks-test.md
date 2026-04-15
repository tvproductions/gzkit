---
id: OBPI-0.29.0-05-tasks-test
parent: ADR-0.29.0-task-management-system-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.29.0-05: Tasks Test

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.29.0-task-management-system-absorption/ADR-0.29.0-task-management-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.29.0-05 --- "Evaluate tasks test subcommand --- task-scoped test execution"`

## OBJECTIVE

Evaluate opsdev's `tasks test` subcommand against gzkit's existing test execution surfaces (`gz test`, ARB step wrapping). Determine whether `tasks test` provides task-scoped test execution capabilities that gzkit lacks. The evaluation must compare: does `tasks test` run tests scoped to a specific task/OBPI, does it provide selective test filtering that `gz test` does not, and is task-scoped testing a governance-generic need?

## SOURCE MATERIAL

- **opsdev:** `tasks.py` --- `tasks test` subcommand implementation
- **gzkit equivalents:** `src/gzkit/commands/test.py` (`gz test`), ARB step wrapping (`gz arb step`)

## ASSUMPTIONS

- The subtraction test governs: if it's not project-specific, it belongs in gzkit
- Task-scoped test execution may overlap with `gz test` or ARB step wrapping
- If `tasks test` provides intelligent test selection based on task scope (e.g., only tests affected by a task's file changes), this is a real capability gap
- If `tasks test` is essentially `uv run -m unittest` with a filter, it may not warrant absorption

## NON-GOALS

- Rewriting gzkit's existing test runner to match opsdev's interface
- Absorbing project-specific test configurations
- Replacing `gz test` or ARB --- evaluating complementary value only

## REQUIREMENTS (FAIL-CLOSED)

1. Read the `tasks test` implementation completely
1. Map the test selection logic against gzkit's existing test execution surfaces
1. Document comparison: scope selection, test filtering, result reporting
1. Record decision with rationale: Absorb / Adapt / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why gzkit's existing test execution is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.29.0-05-01: Read the `tasks test` implementation completely
- [x] REQ-0.29.0-05-02: Map the test selection logic against gzkit's existing test execution surfaces
- [x] REQ-0.29.0-05-03: Document comparison: scope selection, test filtering, result reporting
- [x] REQ-0.29.0-05-04: Record decision with rationale: Absorb / Adapt / Exclude
- [x] REQ-0.29.0-05-05: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.29.0-05-06: If Exclude: document why gzkit's existing test execution is sufficient


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
