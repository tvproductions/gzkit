---
id: OBPI-0.40.0-01-reporter-module-scaffold
parent: ADR-0.40.0-reporter-rendering-infrastructure
status: in_progress
lane: heavy
semver: 0.40.0
sequence: 1
date: 2026-03-28
---

# OBPI-0.40.0-01: Reporter Module Scaffold

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md`
- OBPI Entry: `OBPI-0.40.0-01 — "Reporter module scaffold with four style presets"`

## OBJECTIVE

Create `src/gzkit/reporter/` module with four named style presets (status_table, kv_table, ceremony_panel, list_table) implemented as Rich-based rendering functions. Each preset returns a Rich renderable given a data dict.

## LANE

Heavy — new module introduces rendering contract consumed by all CLI commands.

## ALLOWED PATHS

- `src/gzkit/reporter/__init__.py`
- `src/gzkit/reporter/presets.py`
- `src/gzkit/reporter/panels.py`
- `tests/test_reporter.py`
- `features/reporter_rendering.feature`
- `features/steps/reporter_steps.py`
- `docs/user/concepts/reporter-architecture.md`

## REQUIREMENTS

1. `src/gzkit/reporter/presets.py` exports `status_table()`, `kv_table()`, `ceremony_panel()`, `list_table()` — each accepts a data dict and returns a Rich renderable
2. `status_table()` uses `box.ROUNDED`, supports column definitions, row striping, and title
3. `kv_table()` renders two-column label/value pairs with `box.ROUNDED`
4. `ceremony_panel()` uses `box.DOUBLE`, accepts title and list of (label, status) tuples
5. `list_table()` uses `box.ROUNDED`, minimal columns, supports empty-state message
6. All presets are stateless pure functions — no IO, no ledger reads, no business logic

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.40.0-01-01: `src/gzkit/reporter/presets.py` exports `status_table()`, `kv_table()`, `ceremony_panel()`, `list_table()` — each accepts a data dict and returns a Rich renderable
- [x] REQ-0.40.0-01-02: `status_table()` uses `box.ROUNDED`, supports column definitions, row striping, and title
- [x] REQ-0.40.0-01-03: `kv_table()` renders two-column label/value pairs with `box.ROUNDED`
- [x] REQ-0.40.0-01-04: `ceremony_panel()` uses `box.DOUBLE`, accepts title and list of (label, status) tuples
- [x] REQ-0.40.0-01-05: `list_table()` uses `box.ROUNDED`, minimal columns, supports empty-state message
- [x] REQ-0.40.0-01-06: All presets are stateless pure functions — no IO, no ledger reads, no business logic


## NON-GOALS

- Migrating existing commands (OBPI-03, OBPI-04, OBPI-05)
- Format negotiation helpers (OBPI-02)
- JSON/plain output modes (handled by OutputFormatter)

## QUALITY GATES

- Gate 1 (ADR): This brief
- Gate 2 (TDD): Unit tests for all four presets
- Gate 3 (Docs): `docs/user/concepts/reporter-architecture.md`
- Gate 4 (BDD): Reporter rendering feature scenarios

### Implementation Summary

Created `src/gzkit/reporter/` module with four deterministic rendering presets (status_table, kv_table, list_table, ceremony_panel) backed by Pydantic ColumnDef model. All presets are stateless pure functions returning Rich renderables.

### Key Proof

20/20 unit tests pass, 6/6 BDD scenarios pass, all quality gates green. `uv run -m unittest tests/test_reporter.py -v`
