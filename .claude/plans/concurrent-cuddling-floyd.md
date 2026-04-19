# OBPI-0.0.17-01 — Schema + Pydantic Model: `kind` Field

## Context

ADR-0.0.17 (Heavy) introduces a mechanical `kind` taxonomy for ADRs: `foundation` (semver `0.0.x`) vs `feature` (everything else). Pool ADRs carry no `kind:` in frontmatter — their kind is derived from the `ADR-pool.*` id prefix by a later OBPI's validator.

**This OBPI owns the foundation step:** extend the schema and the Pydantic model to recognize `kind` as a required enum field (`foundation | feature`) on non-pool ADRs. Every downstream OBPI (plan create, adr promote, validate taxonomy, backfill, docs) depends on this alignment being locked and cross-checked.

**Boundary discipline (confirmed by exploration):**
- OBPI-01 (this brief) — schema + model: `kind: {foundation, feature}` enum. Rejects `kind: pool` at the schema level.
- OBPI-04 — id-prefix pool detection in the validator (defense-in-depth, not our scope).
- OBPI-05 — backfill existing ADR files.

Lane: **Heavy**. Gate 4 BDD is deferred to OBPIs that expose CLI surfaces (02, 03, 04); this OBPI's verification is unittest-only per the brief.

## Approach

Extend `src/gzkit/schemas/adr.json` and `src/gzkit/core/models.py` in lockstep, then prove lockstep alignment via the existing `TestFrontmatterSchemaAlignment` helpers. Add Pydantic-level rejection tests and one `validate_frontmatter_model` translation test. Update existing `AdrFrontmatter(...)` fixtures in `tests/test_models.py` to carry `kind` (newly required).

**Mechanical insight from exploration:** `tests/test_schemas.py::TestFrontmatterSchemaAlignment` already auto-discovers required/enum fields via `_check_required_fields` and `_check_enum_fields` (`tests/test_schemas.py:80-117`). Adding `kind` to both surfaces makes the alignment tests pass without new assertion shapes — REQ-04 is satisfied by the field landing on both sides.

## Files to modify

| File | Change |
|------|--------|
| `src/gzkit/schemas/adr.json` | Add `kind` to `properties.frontmatter.properties` (enum `["foundation", "feature"]`, type string, description). Add `"kind"` to `properties.frontmatter.required`. |
| `src/gzkit/core/models.py` | Add `kind: Literal["foundation", "feature"]` on `AdrFrontmatter` (after `lane`, line 27), bare Literal pattern matching `status`/`lane`. |
| `tests/test_schemas.py` | No structural change — existing helpers cover the new field. Verify alignment tests pass. |
| `tests/test_models.py` | (1) Update all `AdrFrontmatter(...)` fixtures to include `kind="foundation"`. (2) Add `test_invalid_kind_enum` (mirror of `test_invalid_status_enum` at line 67), asserting rejection of `"pool"`, `""`, and arbitrary strings with `literal_error`. (3) Add `test_missing_kind` (mirror of `test_missing_required_field`). (4) Add `test_validate_frontmatter_model_translates_kind_literal_error` asserting `validate_frontmatter_model` returns a `ValidationError` dict with `type='frontmatter'`, `field='kind'`, and the allowed-values list `['foundation', 'feature']` in the message. |
| `src/gzkit/models/frontmatter.py` | No change — pure re-export shim. |

## REQ → Test Mapping

All new / updated tests carry `@covers("REQ-0.0.17-01-NN")` decorators from `gzkit.traceability` (`src/gzkit/traceability.py:119`).

| REQ | Mechanism | Test |
|-----|-----------|------|
| REQ-0.0.17-01-01 | Schema `properties.kind.enum == ["foundation", "feature"]` with description | `test_schemas.py::TestFrontmatterSchemaAlignment::test_adr_enum_values_match` (existing, auto-discovers) |
| REQ-0.0.17-01-02 | `"kind"` in `properties.frontmatter.required` | `test_schemas.py::TestFrontmatterSchemaAlignment::test_adr_required_fields_match` (existing, auto-discovers) |
| REQ-0.0.17-01-03 | `AdrFrontmatter.kind: Literal["foundation", "feature"]` | `test_models.py::TestAdrFrontmatter::test_valid_adr` (updated fixture) |
| REQ-0.0.17-01-04 | Cross-validation alignment schema ↔ model | `test_schemas.py::TestFrontmatterSchemaAlignment::test_adr_required_fields_match` AND `test_adr_enum_values_match` (both auto-cover via `_check_required_fields` / `_check_enum_fields`) |
| REQ-0.0.17-01-05 | Pydantic rejects `kind: pool`, `kind: ""`, missing, non-enum | `test_models.py::test_invalid_kind_enum` (new) + `test_missing_kind` (new) |
| REQ-0.0.17-01-06 | `validate_frontmatter_model` translates Pydantic `literal_error` on kind → `ValidationError(type='frontmatter', field='kind', message="… must be one of ['foundation', 'feature'], got '…'")` | `test_models.py::test_validate_frontmatter_model_translates_kind_literal_error` (new) |

## TDD Sequence (Red → Green, per-increment)

1. **Red 1:** Add `test_invalid_kind_enum` + `test_missing_kind` to `tests/test_models.py`. Run — they fail (no `kind` field on model yet).
2. **Green 1:** Add `kind: Literal["foundation", "feature"]` to `AdrFrontmatter`. Update the 9 existing fixture constructions in `test_models.py` to pass `kind="foundation"`. Re-run — new rejection tests pass, all existing tests pass.
3. **Red 2:** Run `test_schemas.py::test_adr_required_fields_match` — fails (schema lacks `kind` in required).
4. **Green 2:** Add `kind` property and `"kind"` to required in `src/gzkit/schemas/adr.json`. Re-run — schema alignment tests pass.
5. **Red 3:** Add `test_validate_frontmatter_model_translates_kind_literal_error`. Run — passes immediately if existing `_translate_pydantic_errors` + `_literal_values` handle the Literal correctly (they should, since they already handle `status` and `lane`). If it fails, the failure is diagnostic — fix the translator.
6. **Refactor:** Scan diff for dead code / inconsistent field ordering / missing `@covers` — none expected given the mechanical nature of the change.

## Verification

Per the OBPI brief's Verification section (unittest + ARB):

```bash
uv run gz arb step --name unittest -- uv run -m unittest tests.test_schemas tests.test_models -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz covers OBPI-0.0.17-01-schema-and-model --json
```

Acceptance:
- All tests in `test_schemas.py` and `test_models.py` pass.
- `test_adr_required_fields_match` and `test_adr_enum_values_match` both include `kind` in their assertions (mechanical — auto-discovered via existing helpers).
- `gz covers` reports `uncovered_reqs == 0` for REQ-0.0.17-01-01 through REQ-0.0.17-01-06.
- Coverage ≥ 40.00%; ruff + ty clean; ARB receipts written.

## Out of Scope (confirmed boundaries)

- No CLI surface changes — those land in OBPI-02 (`gz plan create --kind`) and OBPI-03 (`gz adr promote --kind`).
- No validator-level pool-id detection — OBPI-04.
- No ADR file backfill — OBPI-05. Existing ADRs without `kind:` will fail validation until OBPI-05 lands; that is expected and is NOT our concern.
- No BDD scenario authoring — `features/heavy_lane_gate4.feature` isn't touched; Gate 4 BDD rides with the CLI OBPIs.
- No docs/user or AGENTS.md edits — OBPI-06.

## Critical Files (final reference)

- `src/gzkit/schemas/adr.json:11-33` — schema insertion zone
- `src/gzkit/core/models.py:19-30` — `AdrFrontmatter` model
- `src/gzkit/core/models.py:268-277` — `_literal_values` helper (already handles Literal introspection)
- `src/gzkit/core/models.py:314-323` — `literal_error` translation branch
- `src/gzkit/core/models.py:339-362` — `validate_frontmatter_model`
- `tests/test_schemas.py:80-149` — alignment helpers + ADR tests
- `tests/test_models.py:15-126` — existing `AdrFrontmatter` test fixtures to update
- `src/gzkit/traceability.py:119` — `@covers` decorator import
