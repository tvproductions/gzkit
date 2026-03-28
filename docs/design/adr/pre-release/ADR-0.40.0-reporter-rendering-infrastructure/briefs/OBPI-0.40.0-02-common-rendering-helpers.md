---
id: OBPI-0.40.0-02-common-rendering-helpers
parent: ADR-0.40.0-reporter-rendering-infrastructure
status: Accepted
lane: lite
semver: 0.40.0
sequence: 2
date: 2026-03-28
---

# OBPI-0.40.0-02: Common Rendering Helpers

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md`
- OBPI Entry: `OBPI-0.40.0-02 — "Common rendering helpers from airlineops patterns"`

## OBJECTIVE

Appropriate portable helper functions from airlineops `rich_renderers_common.py` into `src/gzkit/reporter/helpers.py`. These are domain-agnostic formatting utilities: value formatting, format negotiation, and Rich-with-fallback rendering.

## LANE

Lite — internal helpers with no external contract change.

## ALLOWED PATHS

- `src/gzkit/reporter/helpers.py`
- `tests/test_reporter.py`

## REQUIREMENTS

1. `fmt_value()` — humanize numeric values (thousand separators, percentage formatting)
2. `render_with_fallback()` — render Rich renderable to console with plain-text fallback on error
3. `format_output()` — dispatch between JSON serialization and Rich console rendering based on mode
4. All helpers are pure functions or thin wrappers — no business logic, no governance awareness

## NON-GOALS

- Airlineops-specific helpers (report packages, eligibility gates, dataset renderers)
- Modifying OutputFormatter (it stays as-is; helpers complement it)

## QUALITY GATES

- Gate 1 (ADR): This brief
- Gate 2 (TDD): Unit tests for each helper function
