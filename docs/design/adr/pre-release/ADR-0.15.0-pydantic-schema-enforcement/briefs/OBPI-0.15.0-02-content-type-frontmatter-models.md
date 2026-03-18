---
id: OBPI-0.15.0-02-content-type-frontmatter-models
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 2
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.15.0-02 — content-type-frontmatter-models

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- OBPI Entry: `OBPI-0.15.0-02 — "Create Pydantic models for ADR, OBPI, PRD frontmatter with pattern validators"`

## OBJECTIVE (Lite)

Create typed Pydantic models for each governance content type's frontmatter:
`AdrFrontmatter`, `ObpiFrontmatter`, `PrdFrontmatter`. Each model uses Pydantic pattern
validators for ID fields (e.g., `ADR-X.Y.Z`), enum validators for status/lane fields,
and optional reference validators for parent links. Replace manual frontmatter validation
in `validate.py` with Pydantic model instantiation.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `src/gzkit/models/` (new module for content type models)
- `src/gzkit/validate.py` (replace manual frontmatter validation)
- `tests/test_models.py` (new tests for frontmatter models)
- `tests/test_validate.py` (verify behavioral equivalence)

## DENIED PATHS (Lite)

- CI files, lockfiles
- `src/gzkit/schemas/` (touched in OBPI-04, not here)

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `AdrFrontmatter` model: `id` field with regex pattern `ADR-\d+\.\d+\.\d+`, `status` as enum, `lane` as enum, optional `parent`
1. `ObpiFrontmatter` model: `id` field with regex pattern `OBPI-\d+\.\d+\.\d+-\d+-[\w-]+`, `parent` reference, `status` as enum
1. `PrdFrontmatter` model: `id` field with regex pattern `PRD-[\w]+-\d+\.\d+\.\d+`, `status` as enum
1. `validate_frontmatter()` in validate.py uses Pydantic model instantiation instead of manual field checks
1. All existing validation tests pass — identical error messages and error types

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — all tests pass
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_models tests.test_validate -v
Ran 46 tests in 0.005s — OK
Full suite: 561 tests in 12s — OK
```

### Code Quality

```text
uv run ruff check src/gzkit/models/ src/gzkit/validate.py tests/test_models.py — All checks passed
uv run gz typecheck — All checks passed
Coverage: 95.00% (frontmatter.py), 66.26% (scoped modules)
```

### Implementation Summary

- Files added: `src/gzkit/models/frontmatter.py` (AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter)
- Files modified: `src/gzkit/validate.py` (validate_frontmatter uses Pydantic model instantiation)
- Tests added: `tests/test_models.py` (46 tests covering all three frontmatter models)
- Date completed: 2026-03-18
- Defects noted: None

### Key Proof

```bash
uv run -m unittest tests.test_models -v
# 46/46 pass — AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter validated
# Coverage: frontmatter.py 95.00%
```

## Human Attestation

- Attestor: human:Jeff
- Attestation: Completed
- Date: 2026-03-18

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
