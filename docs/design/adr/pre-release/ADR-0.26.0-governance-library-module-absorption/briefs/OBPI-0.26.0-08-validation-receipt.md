---
id: OBPI-0.26.0-08-validation-receipt
parent_adr: ADR-0.26.0-governance-library-module-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.26.0-08: Validation Receipt

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-08 — "Evaluate and absorb lib/validation_receipt.py (274 lines) — structured validation receipt generation"`

## OBJECTIVE

Evaluate `opsdev/lib/validation_receipt.py` (274 lines) against gzkit's partial validation in `validate.py` and determine: Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The opsdev module provides 274 lines of dedicated validation receipt generation — creating structured, schema-validated receipts that record what was validated, when, by whom, and with what result. gzkit has partial coverage in validate.py, but the comparison must determine whether gzkit's validation approach produces receipts with the same structural rigor and auditability as opsdev's dedicated module.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/lib/validation_receipt.py` (274 lines)
- **gzkit equivalent:** Partial in `src/gzkit/validate.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Structured validation receipts are a governance primitive that aligns with gzkit's ARB (Agent Self-Reporting) middleware
- gzkit's validate.py may perform validation but may lack receipt generation depth

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing validation infrastructure — the goal is enriching receipt capabilities

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
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
