---
id: OBPI-0.27.0-03-arb-validate
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-03: ARB Validate

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-03 — "Evaluate and absorb arb/validate.py (154 lines) — receipt schema validation and integrity checks"`

## OBJECTIVE

Evaluate `opsdev/arb/validate.py` (154 lines) against gzkit's current approach to QA evidence validation and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing validation is sufficient), or Exclude (environment-specific). The opsdev module validates receipt JSON files against JSON schemas, checks structural integrity, reports validation errors, and provides summary statistics. gzkit currently has schema validation in other contexts but no receipt-specific validation. The comparison must determine whether receipt validation adds governance rigor beyond what gzkit's existing validation patterns provide.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/validate.py` (154 lines)
- **gzkit equivalent:** Schema validation patterns in `src/gzkit/schema.py` (not receipt-specific)

## ASSUMPTIONS

- The governance value question governs: does receipt-specific validation add rigor beyond general schema validation?
- opsdev wins where receipt validation catches integrity issues that general validation misses
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module likely depends on receipt schemas (OBPI-11, OBPI-12) — evaluation should note the dependency

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Duplicating gzkit's existing schema validation infrastructure for receipts

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: validation depth, error reporting, schema coupling, integrity checks
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's existing validation is sufficient
1. If Exclude: document why the module is environment-specific

## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
