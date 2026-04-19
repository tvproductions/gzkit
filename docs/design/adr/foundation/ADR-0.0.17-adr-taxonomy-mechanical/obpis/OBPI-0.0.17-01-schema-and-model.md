---
id: OBPI-0.0.17-01-schema-and-model
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 1
lane: Heavy
status: Completed
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

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — full taxonomy context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [ ] Sibling OBPIs: 02 (plan-create-kind), 03 (adr-promote-kind), 04 (validate-taxonomy), 05 (backfill-and-roundtrip), 06 (agents-md-correction)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/adr.json` — schema to extend
- [ ] `src/gzkit/core/models.py` — Pydantic model to extend
- [ ] `tests/test_schemas.py::TestFrontmatterSchemaAlignment` — helpers already present
- [ ] `src/gzkit/traceability.py` — `@covers` decorator available

**Existing Code (understand current state):**

- [ ] `AdrFrontmatter` at `src/gzkit/core/models.py:19-30` — 6 existing required fields; `status` and `lane` are bare `Literal[...]` patterns to mirror for `kind`
- [ ] `_literal_values` / `_translate_pydantic_errors` at `src/gzkit/core/models.py:268-323` — already handle the `literal_error` translation path used by `status` and `lane`; `kind` extends this naturally
- [ ] `_check_required_fields` / `_check_enum_fields` at `tests/test_schemas.py:80-117` — schema-driven helpers; adding `kind` to both schema and model is sufficient
- [ ] Sibling `test_models.py` fixtures at `tests/test_models.py:15-126` — 9 `AdrFrontmatter(...)` constructions plus 3 `validate_frontmatter_model` fixture dicts must carry `kind` after the field becomes required

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted (item #1 — "Schema + Pydantic model + cross-validation test")

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test --obpi OBPI-0.0.17-01`
- [ ] ARB receipts attached: ruff, typecheck, unittest

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff`
- [ ] Type check clean: `uv run gz arb typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Schema description field on `kind` reads as operator-facing documentation (no separate docs surface changed in this OBPI — CLI/manpage work lives in OBPI-02/03/04)

### Gate 4: BDD (Heavy only)

- [ ] BDD deferred to CLI-exposing OBPIs (02/03/04) per exploration finding; this OBPI is schema/model only

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Each checkbox carries a deterministic REQ ID. -->

- [ ] REQ-0.0.17-01-01: `src/gzkit/schemas/adr.json` frontmatter schema includes `kind` as a string property with `enum: ["foundation", "feature"]` and a clear `description`.
- [ ] REQ-0.0.17-01-02: `"kind"` is listed in the schema's frontmatter `required` array. Pool ADRs are out-of-scope for this schema — `kind: pool` is NEVER a valid enum value.
- [ ] REQ-0.0.17-01-03: `AdrFrontmatter` in `src/gzkit/core/models.py` carries `kind: Literal["foundation", "feature"]` as a required field with no default.
- [ ] REQ-0.0.17-01-04: `tests/test_schemas.py::TestFrontmatterSchemaAlignment::test_adr_required_fields_match` and `test_adr_enum_values_match` both cover `kind` via the existing `_check_required_fields` and `_check_enum_fields` helpers (no new assertion shape).
- [ ] REQ-0.0.17-01-05: The Pydantic `AdrFrontmatter` model rejects `kind: "pool"`, `kind: ""`, missing `kind`, and arbitrary non-enum strings, each producing a `literal_error` or `missing` Pydantic error.
- [ ] REQ-0.0.17-01-06: `validate_frontmatter_model` translates a Pydantic `literal_error` on `kind` into a `ValidationError` dict with `type='frontmatter'`, `field='kind'`, and the allowed-values list `['foundation', 'feature']` embedded in the message.

## REQ Coverage

- REQ-0.0.17-01-01 through REQ-0.0.17-01-06 (one per Acceptance Criterion above, mapping 1:1 to the numbered Requirements)

### Value Narrative

Before this OBPI, gzkit had no mechanical way to distinguish a *foundation* ADR (infrastructure work under semver `0.0.x`) from a *feature* ADR (end-user capability under any other semver) — the classification lived only in prose and agent judgment. This OBPI lays the schema and model foundation for that taxonomy: `AdrFrontmatter` now carries a required `kind: Literal["foundation", "feature"]` field mirrored by a JSON-schema enum, so every downstream OBPI (`gz plan create --kind`, `gz adr promote --kind`, `gz validate --taxonomy`, backfill) has a locked, cross-validated contract to build on. Pool ADRs remain unaffected — their kind derives from the `ADR-pool.*` id prefix in a later OBPI.

### Key Proof


```text
$ uv run gz covers OBPI-0.0.17-01 --json | tail -8
  "summary": {
    "identifier": "OBPI-0.0.17-01",
    "total_reqs": 6,
    "covered_reqs": 6,
    "uncovered_reqs": 0,
    "coverage_percent": 100.0
  }
```

All 6 REQs covered (100%), 0 uncovered. Full unittest suite: `Ran 3195 tests in 32.9s — OK`.

### Implementation Summary


- Files modified:
  - `src/gzkit/schemas/adr.json` — added `kind` property (enum `["foundation", "feature"]`, type string, with operator-facing description) and included `"kind"` in `frontmatter.required`
  - `src/gzkit/core/models.py` — added `kind: Literal["foundation", "feature"]` to `AdrFrontmatter` using the bare-Literal pattern already used by `status` and `lane`
  - `tests/test_models.py` — added 3 new tests (`test_invalid_kind_enum`, `test_missing_kind`, `test_translates_kind_literal_error`) decorated with `@covers`; updated 9 existing `AdrFrontmatter(...)` fixtures and 3 `validate_frontmatter_model` fixture dicts to carry `kind`
  - `tests/test_schemas.py` — added `@covers("REQ-0.0.17-01-01/02/04")` decorators plus explicit kind assertions on `test_adr_required_fields_match` (schema-required includes kind) and `test_adr_enum_values_match` (schema enum matches `{"foundation","feature"}`, description present)
  - `tests/test_core_models.py`, `tests/test_registry.py`, `tests/test_validate.py` — updated 4 adjacent fixtures that the model change broke (Prime Directive: my primary change surfaced them, so close in scope)
  - `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/obpis/OBPI-0.0.17-01-schema-and-model.md` — added Acceptance Criteria, Discovery Checklist, and Quality Gates sections required for `gz obpi precomplete` authored-readiness (template-drift fix discovered during Stage 1)
- Tests added: 3 unit tests in test_models.py; 2 existing alignment tests augmented with explicit kind assertions; 6/6 REQ coverage via `gz covers`.
- Date completed: 2026-04-19.
- Attestation status: Heavy lane — human attestation captured inline.
- Defects noted: 1 deferred (see Tracked Defects below).

## Tracked Defects

- **`gz obpi precomplete` lock-file search path is wrong.** `_check_lock_held` at `src/gzkit/commands/obpi_precomplete.py:174-195` globs `.gzkit/locks/*.json` but the actual lock files live at `.gzkit/locks/obpi/*.lock.json` (subdirectory + different suffix). Result: precomplete always reports "No lock file matches" even when `gz obpi lock list` shows an ACTIVE lock for the OBPI. Workaround for this OBPI: invoked `gz obpi complete` directly (the complete command has its own internal lock validation). File a GHI at completion.

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — Heavy-lane OBPI-0.0.17-01 lands kind: Literal["foundation", "feature"] on AdrFrontmatter + src/gzkit/schemas/adr.json in lockstep, cross-validated by existing TestFrontmatterSchemaAlignment helpers extended with explicit kind assertions. 3 new @covers-decorated tests prove pool/empty/missing/non-enum rejection and validate_frontmatter_model literal_error → ValidationError(field='kind', allowed=['foundation','feature']) translation. gz covers OBPI-0.0.17-01 --json reports 6/6 REQ parity (100%, 0 uncovered). Adjacent-file defects my change surfaced (4 fixtures across test_core_models/test_registry/test_validate) closed in-scope per Prime Directive; brief was amended in-scope to add Acceptance Criteria + Discovery Checklist + Quality Gates sections required for gz obpi precomplete authored-readiness (template-drift the brief author omitted). Pool-boundary discipline preserved: kind is NEVER a valid enum value for pool ADRs — id-prefix detection is OBPI-04's scope. Receipts: lint arb-ruff-d28bf4283dc64153bbb22f334d72ae8e; types arb-step-typecheck-d88d297a04444d3d9ef184781be071b9; tests arb-step-unittest-40bab0bba46f4cec945f4d421a5b7643. Full-suite regression green: Ran 3195 tests in 32.9s — OK. One defect filed for tracking: gz obpi precomplete _check_lock_held searches .gzkit/locks/ but actual locks live at .gzkit/locks/obpi/*.lock.json — workaround used, GHI to be filed post-sync.
- Date: 2026-04-19
