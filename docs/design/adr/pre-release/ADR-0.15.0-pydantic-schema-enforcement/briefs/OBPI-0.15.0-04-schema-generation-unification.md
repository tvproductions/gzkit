---
id: OBPI-0.15.0-04-schema-generation-unification
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 4
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.15.0-04 — schema-generation-unification

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- OBPI Entry: `OBPI-0.15.0-04 — "Verify/generate JSON Schema from Pydantic models; decide single-source direction"`

## OBJECTIVE (Lite)

Determine the single-source-of-truth direction for JSON Schema:

- **Option A:** Generate JSON Schema from Pydantic models using `model_json_schema()`.
  Hand-authored schemas in `src/gzkit/schemas/` are replaced by a generation step.
- **Option B:** Keep hand-authored schemas but add a cross-validation test that verifies
  Pydantic models produce equivalent schemas.

Implement the chosen option. Either way, the invariant is: Pydantic models and JSON
schemas never drift from each other.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `src/gzkit/schemas/` (modify or replace schema files)
- `src/gzkit/schemas/__init__.py` (update schema loading if generation chosen)
- `tests/test_schemas.py` (new: cross-validation or generation tests)
- `scripts/generate_schemas.py` (new: if generation chosen)

## DENIED PATHS (Lite)

- CI files, lockfiles
- `.gzkit/governance/ontology.schema.json` (separate concern)

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. Decision documented: Option A (generate) or Option B (cross-validate)
1. If Option A: generation script produces schemas identical to current hand-authored ones (diff-verified before replacing)
1. If Option B: test asserts `model_json_schema()` output matches hand-authored schema for every content type
1. No JSON Schema consumed by external tools changes shape (backward compatibility)
1. `load_schema()` and `get_schema_path()` continue to work identically
1. Invariant enforced by test: Pydantic models and JSON schemas cannot drift

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — 588 tests pass
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_schemas -v
Ran 17 tests in 0.002s — OK
schemas/__init__.py coverage: 100.0%
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

**Decision: Option B (cross-validate).** Hand-authored schemas are kept; Pydantic models
are validated against them by 17 cross-validation tests in `tests/test_schemas.py`.

Rationale for Option B over Option A:
- `ledger.json` uses a custom format (not standard JSON Schema) — `model_json_schema()` would produce incompatible output
- `manifest.json` and `agents.json` have no Pydantic model equivalents
- Frontmatter schemas include `required_headers`/`optional_headers` (markdown concerns outside Pydantic)
- Replacing schemas risks breaking external tool consumers

Created `tests/test_schemas.py` with three test classes:
- `TestFrontmatterSchemaAlignment` — 9 tests: required fields, enum values, and regex patterns match between ADR/OBPI/PRD Pydantic models and their JSON schemas
- `TestLedgerSchemaAlignment` — 5 tests: bidirectional event coverage, required fields per event, properties per event, base required fields across all 12 typed event models
- `TestSchemaLoading` — 3 tests: `load_schema()` and `get_schema_path()` regression for all 6 schemas

### Key Proof

```bash
uv run -m unittest tests.test_schemas -v
# 17/17 pass — models and schemas aligned, no drift detected
```

## Human Attestation

- Attestor: `human:jeff`
- Attestation: `attest completed`
- Date: `2026-03-18`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
