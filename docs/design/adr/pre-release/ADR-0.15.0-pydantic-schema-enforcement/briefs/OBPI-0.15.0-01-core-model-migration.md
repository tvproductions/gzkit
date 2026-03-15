<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.15.0-01 — core-model-migration

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- OBPI Entry: `OBPI-0.15.0-01 — "Migrate LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult to Pydantic"`

## OBJECTIVE (Lite)

Migrate the 5 core dataclass models to Pydantic BaseModel v2. Add `pydantic>=2.0` to
`pyproject.toml`. Preserve exact field types, defaults, and frozen semantics. All existing
tests must pass without modification.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `pyproject.toml` (add dependency)
- `src/gzkit/config.py`
- `src/gzkit/validate.py`
- `src/gzkit/ledger.py`
- `src/gzkit/quality.py`
- `tests/test_config.py`
- `tests/test_validate.py`
- `tests/test_ledger.py`

## DENIED PATHS (Lite)

- CI files, lockfiles
- `src/gzkit/schemas/` (touched in OBPI-04, not here)

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `pydantic>=2.0` added to `pyproject.toml` dependencies
1. `LedgerEvent` migrated: all fields, `LEDGER_SCHEMA` constant, event factory functions work
1. `GzkitConfig` and `PathConfig` migrated: config loading from manifest.json unchanged
1. `ValidationError` and `ValidationResult` migrated: all validation functions return identical results
1. `QualityResult` migrated: quality check reporting unchanged
1. All existing tests pass with zero modifications (behavioral equivalence proof)

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` — all tests pass
- [ ] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean
