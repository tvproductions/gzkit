---
id: OBPI-0.28.0-18-chores-models
parent: ADR-0.28.0-chores-system-maturity-absorption
item: 18
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.28.0-18: Chores Models

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.28.0-chores-system-maturity-absorption/ADR-0.28.0-chores-system-maturity-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.28.0-18 — "Evaluate and absorb chores_tools/models.py (56 lines) — chores data models"`

## OBJECTIVE

Evaluate `opsdev/src/opsdev/chores_tools/models.py` (56 lines) against gzkit's data models in `commands/chores.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides dedicated Pydantic data models for chore definitions, execution results, plan state, and recommendations. gzkit's data modeling for chores is inline — likely using dicts or ad-hoc classes rather than proper Pydantic models per the data model policy.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/chores_tools/models.py` (56 lines)
- **gzkit equivalent:** Inline data handling in `src/gzkit/commands/chores.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not opsdev-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic BaseModel, ConfigDict(frozen=True, extra="forbid"), Field with descriptions)
- Dedicated Pydantic models align with gzkit's data model policy — this is likely a straightforward Absorb
- These models are consumed by nearly every other module in the chores system

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Migrating all existing gzkit chores data handling in this OBPI — focus on the model definitions

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

- [x] REQ-0.28.0-18-01: Read both implementations completely
- [x] REQ-0.28.0-18-02: Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
- [x] REQ-0.28.0-18-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.28.0-18-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.28.0-18-05: If Confirm: document why gzkit's implementation is sufficient
- [x] REQ-0.28.0-18-06: If Exclude: document why the module is domain-specific


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
