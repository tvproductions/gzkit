---
id: OBPI-0.28.0-17-chores-parser
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 17
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-17: Chores Parser

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-17 — "Evaluate and absorb chores_tools/parser.py (302 lines) — chore definition parsing and validation"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/parser.py` (302 lines) against gzkit's parsing logic in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides dedicated chore definition parsing with schema validation, config file loading, chore metadata extraction, and validation error reporting. gzkit's parsing is embedded in the monolith without the same depth of validation and error reporting.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/parser.py` (302 lines)
- **gzkit equivalent:** Parsing logic in `src/gzkit/commands/chores.py` (embedded)

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 302 lines with schema validation and error reporting, the parser likely provides stricter validation than gzkit's inline parsing
- The parser produces models consumed by the planner (OBPI-0.28.0-16) and executor (OBPI-0.28.0-10)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Creating a general-purpose config parser — this is chore definition parsing

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

- [x] REQ-0.28.0-17-01: Read both implementations completely
- [x] REQ-0.28.0-17-02: Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
- [x] REQ-0.28.0-17-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.28.0-17-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.28.0-17-05: If Confirm: document why gzkit's implementation is sufficient
- [x] REQ-0.28.0-17-06: If Exclude: document why the module is domain-specific


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
