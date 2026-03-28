---
id: OBPI-0.40.0-03-status-report-table-migration
parent: ADR-0.40.0-reporter-rendering-infrastructure
status: Accepted
lane: heavy
semver: 0.40.0
sequence: 3
date: 2026-03-28
---

# OBPI-0.40.0-03: Status and Report Table Migration

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md`
- OBPI Entry: `OBPI-0.40.0-03 — "Status/report table migration to reporter presets"`

## OBJECTIVE

Migrate `gz status`, `gz adr report`, and `gz state` table rendering from ad-hoc Rich Table construction to reporter `status_table()` and `kv_table()` presets. Commands produce data dicts; reporter renders them.

## LANE

Heavy — external output appearance changes for primary governance commands.

## ALLOWED PATHS

- `src/gzkit/commands/status.py`
- `src/gzkit/commands/state.py`
- `src/gzkit/reporter/presets.py` (if preset adjustments needed)
- `tests/test_reporter.py`
- `tests/test_status.py` (if exists)
- `features/reporter_rendering.feature`
- `docs/user/commands/status.md`
- `docs/user/commands/state.md`

## REQUIREMENTS

1. `gz status --table` renders via `reporter.status_table()` — same columns, same data, consistent box.ROUNDED style
2. `gz adr report` renders overview and OBPI tables via reporter presets
3. `gz state` detail output uses `reporter.kv_table()` for key-value sections
4. JSON mode (`--json`) continues to work through OutputFormatter — reporter is only consulted for human-readable output
5. No behavioral change — same data, same columns, deterministic styling

## NON-GOALS

- Changing what data is displayed (only how it's rendered)
- Modifying JSON output format
- Adding new columns or table features

## QUALITY GATES

- Gate 1 (ADR): This brief
- Gate 2 (TDD): Unit tests verify rendered output matches expected structure
- Gate 3 (Docs): Command docs updated if output examples change
- Gate 4 (BDD): Existing BDD scenarios still pass with new rendering
