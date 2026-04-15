---
id: OBPI-0.27.0-03-arb-validate
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 3
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

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-03-01: Read both implementations completely
- [x] REQ-0.27.0-03-02: Document comparison: validation depth, error reporting, schema coupling, integrity checks
- [x] REQ-0.27.0-03-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-03-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-03-05: If Confirm: document why gzkit's existing validation is sufficient
- [x] REQ-0.27.0-03-06: If Exclude: document why the module is environment-specific


## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
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

- `src/gzkit/arb/validator.py` — port of `opsdev/arb/validate.py` (154L source). Converts airlineops's `@dataclass(frozen=True) ArbReceiptValidationResult` to Pydantic `BaseModel(frozen=True, extra="forbid")` with `Field(..., description=...)` per `.gzkit/rules/models.md`. Uses `gzkit.commands.common.get_project_root()` for project root resolution instead of `Path(__file__).parents[N]` (which the gzkit ADR path contract check rejects). Loads schemas from `data/schemas/arb_lint_receipt.schema.json` and `data/schemas/arb_step_receipt.schema.json` via `jsonschema.Draft202012Validator`. Handles JSON decode errors, schema-id lookup misses, and unknown-schema cases distinctly.
- `tests/arb/test_validator.py` — 7 Red→Green tests: all-valid case, malformed-counts-invalid, unknown schema, missing schema field, empty directory, limit honored, result-is-frozen-pydantic.

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence — "Receipt validation — `validate.py:59-128` — Draft 2020-12 validator, schema ID lookup, counts valid/invalid/unknown" against gzkit pre-absorption "None — `validate_pkg/ledger_check.py` validates governance ledger events (Pydantic `ObpiReceiptEvidence`), not lint/step receipts."

**Dog-fooding proof:** `uv run gz arb validate --limit 20` run against the 4 dog-food receipts reports `Receipts scanned: 4, Valid: 4, Invalid: 0`. The `arb validate` command is the user-visible entry point and returns exit 0 when invalid==0, exit 1 when invalid>0, exit 2 on ARB internal error (per `.gzkit/rules/arb.md`).

**Dependency note:** This brief correctly noted dependency on OBPI-0.27.0-11 (lint schema) and OBPI-0.27.0-12 (step schema). Both schemas were absorbed under OBPI-0.25.0-33 in the same implementation pass, so the dependency chain resolved atomically.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
