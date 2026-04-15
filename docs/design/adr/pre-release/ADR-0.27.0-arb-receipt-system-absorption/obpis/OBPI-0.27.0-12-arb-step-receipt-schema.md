---
id: OBPI-0.27.0-12-arb-step-receipt-schema
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 12
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

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-12-01: Read the schema completely
- [x] REQ-0.27.0-12-02: Document: field coverage, required vs optional fields, validation constraints, interoperability value
- [x] REQ-0.27.0-12-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-12-04: If Absorb: copy schema to gzkit's `data/schemas/` and validate it
- [x] REQ-0.27.0-12-05: If Confirm: document why gzkit's existing approach is sufficient
- [x] REQ-0.27.0-12-06: If Exclude: document why the schema is environment-specific


## ALLOWED PATHS

- `data/schemas/` — target for absorbed schemas
- `tests/` — tests for schema validation
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Decision: Absorb (executed under OBPI-0.25.0-33)

**Decision:** Absorb.

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (closed 2026-04-14). Cross-referenced to preserve per-module audit trail.

**Gzkit implementation:**

- `data/schemas/arb_step_receipt.schema.json` — port of `airlineops/data/schemas/arb_step_receipt.schema.json`. Renamed `$id` to `gzkit.arb.step_receipt.schema.json` and `properties.schema.const` to `gzkit.arb.step_receipt.v1`. Draft 2020-12, `additionalProperties: false`, required fields `[schema, step, run_id, timestamp_utc, git, exit_status, duration_ms, stdout_tail, stderr_tail, stdout_truncated, stderr_truncated]`. The `step` subobject requires `[name, command]` where `command` is a `minItems: 1` array of strings (matches Python argv convention).
- `tests/arb/test_schemas.py` — schema meta-validation test covers both lint and step schemas; well-formed step receipt validation test asserts the step-receipt shape loads and validates cleanly.

**Brief-framing correction:** Same pattern as OBPI-0.27.0-11 — the brief assumed the schema might exist; the absorption discovered the rule referenced a non-existent path and produced the real artifact.

**Dependency note:** The brief correctly noted "consumed by validate (OBPI-03) and step_reporter (OBPI-02)." All three were absorbed atomically in the OBPI-0.25.0-33 implementation pass.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
