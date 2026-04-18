---
id: OBPI-0.0.17-01-schema-and-model
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.17-01-schema-and-model: kind field in ADR schema + Pydantic model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #1 — "Schema + Pydantic model + cross-validation test"

**Status:** Draft

## Objective

Extend `src/gzkit/schemas/adr.json` with a `kind` frontmatter field constrained to `enum: [foundation, feature]`. Extend `AdrFrontmatter` Pydantic model in `src/gzkit/core/models.py` with the matching `Literal["foundation", "feature"]` field. Cross-validation tests lock schema ↔ model alignment. Pool ADRs do NOT carry `kind:` in frontmatter — their kind is derived from the `ADR-pool.*` id prefix (see OBPI-04 for the validator's id-based pool detection).

## Lane

**Heavy** — schema and public data-model contract change.

## Allowed Paths

- `src/gzkit/schemas/adr.json`
- `src/gzkit/core/models.py`
- `src/gzkit/models/frontmatter.py` (re-exports only)
- `tests/test_schemas.py` (cross-validation)
- `tests/test_models.py` (Pydantic behavior)

## Denied Paths

- Any CLI command surface (OBPI-02, OBPI-03, OBPI-04)
- Any existing ADR frontmatter (OBPI-05 backfill)
- Documentation surfaces (OBPI-06)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/schemas/adr.json` frontmatter schema includes `kind` in `properties` with `enum: ["foundation", "feature"]` and a clear `description`.
2. REQUIREMENT: `kind` is listed in `required` for non-pool ADRs. Pool ADRs are out-of-scope for this schema — the pool schema (if any future work creates one) or the id-derived check in OBPI-04 handles pool detection. This brief NEVER adds `kind: pool` as a valid enum value.
3. REQUIREMENT: `AdrFrontmatter` in `src/gzkit/core/models.py` carries `kind: Literal["foundation", "feature"]` as a required field.
4. REQUIREMENT: `tests/test_schemas.py::TestFrontmatterSchemaAlignment` includes `kind` in `test_adr_required_fields_match` and `test_adr_enum_values_match` assertions (both derive from the schema via `_check_required_fields` / `_check_enum_fields` helpers — no new assertion shape needed, only the new field must pass under them).
5. REQUIREMENT: The Pydantic model rejects `kind: pool`, `kind: ""`, missing `kind`, and any non-enum string with a clear pattern/literal error message.
6. REQUIREMENT: `validate_frontmatter_model` correctly translates Pydantic `literal_error` on `kind` into a `ValidationError(type='frontmatter', field='kind', ...)` with the allowed-values list in the message.

## Verification

```bash
uv run gz arb step --name unittest -- uv run -m unittest tests.test_schemas tests.test_models -v
uv run gz arb ruff
uv run gz arb typecheck
```

All four tests in the expanded `test_schemas.py` must pass; `test_adr_required_fields_match` and `test_adr_enum_values_match` must cover `kind`.

## Evidence

- Schema/model alignment test output
- Pydantic rejection test output (invalid kind values produce ValidationError with the allowed-values list)
- ARB receipts (ruff, ty, unittest)

## REQ Coverage

- REQ-0.0.17-01-01 through REQ-0.0.17-01-06 (one per requirement above)
