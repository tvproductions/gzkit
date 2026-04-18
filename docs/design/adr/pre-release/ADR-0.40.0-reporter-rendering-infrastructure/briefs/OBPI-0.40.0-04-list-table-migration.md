---
id: OBPI-0.40.0-04-list-table-migration
parent: ADR-0.40.0-reporter-rendering-infrastructure
status: pending
lane: heavy
semver: 0.40.0
sequence: 4
date: 2026-03-28
---

# OBPI-0.40.0-04: List Table Migration

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md`
- OBPI Entry: `OBPI-0.40.0-04 — "List table migration to reporter list presets"`

## OBJECTIVE

Migrate `gz task list`, `gz chores list`, `gz roles`, and `gz skill list` from ad-hoc Rich Table construction to reporter `list_table()` preset. Consistent styling across all list-style command output.

## LANE

Heavy — external output appearance changes for list commands.

## ALLOWED PATHS

- `src/gzkit/commands/task.py`
- `src/gzkit/commands/chores.py`
- `src/gzkit/commands/roles.py`
- `src/gzkit/commands/skills_cmd.py`
- `src/gzkit/reporter/presets.py` (if preset adjustments needed)
- `tests/test_reporter.py`
- `features/reporter_rendering.feature`
- `docs/user/commands/task-list.md`

## REQUIREMENTS

1. All list commands render via `reporter.list_table()` with consistent box.ROUNDED style
2. Empty-state messages ("No tasks found", etc.) render through the preset's empty-state handler
3. JSON mode continues to bypass reporter (OutputFormatter handles)
4. Column definitions passed as data — no hard-coded columns in reporter

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.40.0-04-01: All list commands render via `reporter.list_table()` with consistent box.ROUNDED style
- [x] REQ-0.40.0-04-02: Empty-state messages ("No tasks found", etc.) render through the preset's empty-state handler
- [x] REQ-0.40.0-04-03: JSON mode continues to bypass reporter (OutputFormatter handles)
- [x] REQ-0.40.0-04-04: Column definitions passed as data — no hard-coded columns in reporter


## NON-GOALS

- Adding new list commands
- Changing list data content
- Modifying JSON output schemas

## QUALITY GATES

- Gate 1 (ADR): This brief
- Gate 2 (TDD): Unit tests for list table rendering
- Gate 3 (Docs): Command docs updated if output examples change
- Gate 4 (BDD): Existing BDD scenarios pass, new scenarios for consistent list rendering
