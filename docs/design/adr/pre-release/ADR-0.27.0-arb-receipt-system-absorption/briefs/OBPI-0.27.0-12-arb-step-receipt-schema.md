---
id: OBPI-0.27.0-12-arb-step-receipt-schema
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-12: ARB Step Receipt Schema

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-12 — "Evaluate and absorb arb_step_receipt.schema.json — JSON schema for step receipt validation"`

## OBJECTIVE

Evaluate `data/schemas/arb_step_receipt.schema.json` from opsdev against gzkit's current schema patterns and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev schema defines the JSON structure for generic QA step receipts: execution metadata (command, arguments, exit code, duration), output capture (stdout, stderr), environment context, and status classification. gzkit currently has no step receipt schema. The comparison must determine whether a formal JSON schema for step receipts adds validation rigor beyond Pydantic model validation.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/data/schemas/arb_step_receipt.schema.json`
- **gzkit equivalent:** No direct equivalent — no step receipt schema exists

## ASSUMPTIONS

- JSON schemas provide language-agnostic validation that Pydantic models cannot (external tools, CI pipelines)
- If the receipt system is adopted, schemas are essential for interoperability
- Absorbed schemas must be validated with a JSON schema validator
- This schema is consumed by validate (OBPI-03) and step_reporter (OBPI-02) — tight coupling expected

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Designing a schema registry — scope is evaluating this specific schema

## REQUIREMENTS (FAIL-CLOSED)

1. Read the schema completely
1. Document: field coverage, required vs optional fields, validation constraints, interoperability value
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: copy schema to gzkit's `data/schemas/` and validate it
1. If Confirm: document why gzkit's existing approach is sufficient
1. If Exclude: document why the schema is environment-specific

## ALLOWED PATHS

- `data/schemas/` — target for absorbed schemas
- `tests/` — tests for schema validation
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
