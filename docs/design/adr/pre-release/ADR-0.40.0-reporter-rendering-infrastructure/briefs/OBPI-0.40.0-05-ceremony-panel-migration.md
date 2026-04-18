---
id: OBPI-0.40.0-05-ceremony-panel-migration
parent: ADR-0.40.0-reporter-rendering-infrastructure
status: pending
lane: heavy
semver: 0.40.0
sequence: 5
date: 2026-03-28
---

# OBPI-0.40.0-05: Ceremony Panel Migration

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md`
- OBPI Entry: `OBPI-0.40.0-05 — "Ceremony panel migration to reporter-generated Rich panels"`

## OBJECTIVE

Replace hand-padded Unicode box-drawing strings in ceremony skill templates with calls to `reporter.ceremony_panel()`. The closeout ceremony completion table, walkthrough headers, and gate summary panels are generated deterministically by code.

## LANE

Heavy — ceremony output appearance changes; skill templates reference reporter CLI or functions.

## ALLOWED PATHS

- `src/gzkit/reporter/panels.py`
- `src/gzkit/commands/ceremony.py` (new, if needed as CLI surface for panel rendering)
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- `tests/test_reporter.py`
- `features/reporter_rendering.feature`
- `docs/user/concepts/reporter-architecture.md`

## REQUIREMENTS

1. `ceremony_panel()` accepts title string and list of (step_label, check_status) tuples, returns Rich Panel with box.DOUBLE
2. Closeout ceremony skill template references `ceremony_panel()` output instead of hand-drawn box art
3. Panel width and alignment are computed by Rich — no manual padding
4. Check status renders as checkmark (green) or pending marker
5. Optional: `gz reporter ceremony-box` CLI command for skill templates to invoke

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.40.0-05-01: `ceremony_panel()` accepts title string and list of (step_label, check_status) tuples, returns Rich Panel with box.DOUBLE
- [x] REQ-0.40.0-05-02: Closeout ceremony skill template references `ceremony_panel()` output instead of hand-drawn box art
- [x] REQ-0.40.0-05-03: Panel width and alignment are computed by Rich — no manual padding
- [x] REQ-0.40.0-05-04: Check status renders as checkmark (green) or pending marker
- [x] REQ-0.40.0-05-05: Optional: `gz reporter ceremony-box` CLI command for skill templates to invoke


## NON-GOALS

- Changing ceremony workflow or attestation logic
- Modifying ceremony skill content beyond the output rendering
- Adding new ceremony types

## QUALITY GATES

- Gate 1 (ADR): This brief
- Gate 2 (TDD): Unit tests for ceremony_panel() with various step counts
- Gate 3 (Docs): Reporter architecture doc updated with ceremony panel section
- Gate 4 (BDD): Ceremony panel rendering scenario
