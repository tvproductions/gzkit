---
id: OBPI-0.27.0-11-arb-lint-receipt-schema
parent_adr: ADR-0.27.0-arb-receipt-system-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-11: ARB Lint Receipt Schema

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-11 — "Evaluate and absorb arb_lint_receipt.schema.json — JSON schema for lint receipt validation"`

## OBJECTIVE

Evaluate `data/schemas/arb_lint_receipt.schema.json` from opsdev against gzkit's current schema patterns and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev schema defines the JSON structure for lint receipts: metadata fields (timestamp, tool, version), findings array (rule, file, line, column, severity, message), and summary statistics. gzkit currently has `data/schemas/arb_lint_receipt.schema.json` referenced in its ARB rule documentation but the evaluation must verify whether the schema exists and is complete. The comparison must determine whether a formal JSON schema for lint receipts adds validation rigor beyond Pydantic model validation.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/data/schemas/arb_lint_receipt.schema.json`
- **gzkit equivalent:** `data/schemas/arb_lint_receipt.schema.json` (referenced in ARB docs — verify existence)

## ASSUMPTIONS

- JSON schemas provide language-agnostic validation that Pydantic models cannot (external tools, CI pipelines)
- If the receipt system is adopted, schemas are essential for interoperability
- Absorbed schemas must be validated with a JSON schema validator
- This schema is consumed by validate (OBPI-03) — tight coupling expected

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
