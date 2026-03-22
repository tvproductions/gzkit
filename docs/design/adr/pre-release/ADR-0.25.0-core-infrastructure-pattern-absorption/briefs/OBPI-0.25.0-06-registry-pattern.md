---
id: OBPI-0.25.0-06-registry-pattern
parent_adr: ADR-0.25.0-core-infrastructure-pattern-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-06: Registry Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-06 — "Evaluate and absorb core/registry.py (86 lines) — registry pattern implementation"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/registry.py` (86 lines) against gzkit's `registry.py` (217 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides a registry pattern with lookup facades. gzkit's equivalent is already 2.5x larger, suggesting gzkit may be more sophisticated — but the comparison must verify this.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/registry.py` (86 lines)
- **gzkit equivalent:** `src/gzkit/registry.py` (217 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's larger implementation may already subsume airlineops's capabilities

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Merging registry patterns if they serve fundamentally different purposes

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
