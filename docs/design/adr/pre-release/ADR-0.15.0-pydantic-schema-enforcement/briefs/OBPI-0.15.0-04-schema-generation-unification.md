---
id: OBPI-0.15.0-04-schema-generation-unification
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 4
lane: Lite
status: Draft
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

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` — all tests pass
- [ ] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
