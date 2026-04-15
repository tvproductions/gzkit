---
id: OBPI-0.28.0-16-chores-planner
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 16
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-16: Chores Planner

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-16 — "Evaluate and absorb chores_tools/planner.py (617 lines) — chore planning and dependency resolution"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/planner.py` (617 lines) against gzkit's planning logic in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides sophisticated chore planning with dependency resolution, config-driven lane selection, execution ordering, plan persistence, and plan diffing (via `--replace`). At 617 lines, this is the second largest module in the system. gzkit's planning logic is embedded in the monolith and lacks the depth of dependency resolution and config-driven behavior.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/planner.py` (617 lines)
- **gzkit equivalent:** Planning logic in `src/gzkit/commands/chores.py` (embedded)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 617 lines with dependency resolution and config-driven lane selection, the planner likely represents significant capabilities gzkit is missing
- The planner depends on models (OBPI-0.28.0-18), parser (OBPI-0.28.0-17), and config (OBPI-0.28.0-19)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Creating a general-purpose task scheduler — this is chore planning specifically

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.28.0-16-01: Read both implementations completely
- [x] REQ-0.28.0-16-02: Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
- [x] REQ-0.28.0-16-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.28.0-16-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.28.0-16-05: If Confirm: document why gzkit's implementation is sufficient
- [x] REQ-0.28.0-16-06: If Exclude: document why the module is domain-specific


## ALLOWED PATHS

- `src/gzkit/chores_tools/` — target for absorbed modules
- `src/gzkit/commands/chores.py` — existing monolith (may be refactored)
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
