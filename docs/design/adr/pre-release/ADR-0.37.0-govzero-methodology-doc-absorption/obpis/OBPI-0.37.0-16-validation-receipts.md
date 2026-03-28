---
id: OBPI-0.37.0-16-validation-receipts
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 16
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-16: validation-receipts

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-16 — "Compare and absorb validation-receipts.md — receipt schema and lifecycle"`

## OBJECTIVE

Compare `docs/governance/GovZero/validation-receipts.md` between airlineops and gzkit. This document defines the validation receipt schema, lifecycle, and storage conventions — how QA evidence is captured and persisted. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/validation-receipts.md`
- **gzkit:** `docs/governance/GovZero/validation-receipts.md`

## ASSUMPTIONS

- Receipt documentation must match the ARB receipt schema and storage patterns
- gzkit implements the receipt system; its documentation should be authoritative
- airlineops may have additional receipt patterns from operational QA experience

## NON-GOALS

- Changing the receipt schema
- Adding domain-specific receipt types

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in receipt schema, lifecycle, storage conventions
1. Evaluate which version is more complete and matches the implementation
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/validation-receipts.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
