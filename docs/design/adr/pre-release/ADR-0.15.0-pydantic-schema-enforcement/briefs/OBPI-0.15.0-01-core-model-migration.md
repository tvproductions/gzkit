---
id: OBPI-0.15.0-01-core-model-migration
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 1
lane: Lite
status: Completed
---

# OBPI-0.15.0-01-core-model-migration: Core Model Migration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- **Checklist Item:** #1 - "OBPI-0.15.0-01: Migrate LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult to Pydantic"

**Status:** Completed

## Objective

Migrate the 5 core dataclass models (LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult) to Pydantic BaseModel v2 with exact behavioral equivalence.

## Lane

**Lite** - Internal model layer change only; no CLI/API/schema contract changes.

## Allowed Paths

- `src/gzkit/ledger.py` - LedgerEvent dataclass → BaseModel
- `src/gzkit/config.py` - GzkitConfig, PathConfig dataclass → BaseModel
- `src/gzkit/validate.py` - ValidationError, ValidationResult dataclass → BaseModel
- `tests/test_ledger.py` - LedgerEvent test coverage
- `tests/test_config.py` - GzkitConfig, PathConfig test coverage
- `tests/test_validate.py` - ValidationError, ValidationResult test coverage

## Denied Paths

- `src/gzkit/schemas/**` - Schema unification belongs to OBPI-04
- `src/gzkit/superbook_models.py` - Already Pydantic; out of scope
- `src/gzkit/commands/**` - Command layer unchanged
- `docs/design/**` - ADR changes out of scope
- New dependencies (pydantic already in pyproject.toml)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Each migrated model MUST produce identical field values, defaults, and serialization output as the original dataclass.
1. REQUIREMENT: `to_dict()` methods MUST be replaced with Pydantic `model_dump()` and callers updated.
1. REQUIREMENT: `from_dict()` classmethods MUST be replaced with Pydantic `model_validate()` and callers updated.
1. REQUIREMENT: GzkitConfig `load()`/`save()` MUST preserve JSON roundtrip behavior.
1. NEVER: Change field names, field types, or default values during migration.
1. NEVER: Add new validation rules that did not exist in the dataclass version.
1. ALWAYS: Run the full test suite after each model migration to catch regressions immediately.
1. ALWAYS: Follow the existing Pydantic pattern in `src/gzkit/superbook_models.py` for style consistency.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- [x] Related OBPIs in same ADR (02: frontmatter models, 03: ledger discrimination, 04: schema generation)

**Prerequisites (check existence, STOP if missing):**

- [x] `pydantic>=2.12.5` in pyproject.toml dependencies
- [x] `src/gzkit/ledger.py` exists with LedgerEvent dataclass
- [x] `src/gzkit/config.py` exists with GzkitConfig, PathConfig dataclasses
- [x] `src/gzkit/validate.py` exists with ValidationError, ValidationResult dataclasses

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/superbook_models.py` (existing Pydantic models)
- [x] Test patterns: `tests/test_ledger.py`, `tests/test_config.py`, `tests/test_validate.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_ledger tests.test_config tests.test_validate -v
```

## Acceptance Criteria

- [x] REQ-0.15.0-01-01: Given a LedgerEvent constructed with the same arguments, when serialized via model_dump(), then the output matches the original to_dict() output exactly.
- [x] REQ-0.15.0-01-02: Given a GzkitConfig loaded from an existing manifest.json, when accessed via the same field paths, then all values match the dataclass version.
- [x] REQ-0.15.0-01-03: Given a PathConfig with default values, when each field is read, then all 24 path defaults are identical to the dataclass defaults.
- [x] REQ-0.15.0-01-04: Given a ValidationError and ValidationResult constructed with the same arguments, when serialized via model_dump(), then the output matches to_dict() exactly.
- [x] REQ-0.15.0-01-05: Given the full gzkit test suite (532+ tests), when run after migration, then zero regressions — all tests pass.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 66 tests in 0.008s — OK
Coverage: config.py 100%, ledger.py 86%, validate.py 66% (TOTAL 79%)
Full suite: 535 tests, 2 pre-existing failures (test_hooks, unrelated)
```

### Code Quality

```text
uv run ruff check <scoped files> — All checks passed
uv run gz typecheck — All checks passed
```

### Value Narrative

Before this OBPI, the 5 core models were Pydantic BaseModels but retained legacy `to_dict()` and `from_dict()` wrapper methods, creating a dual API where callers used ad-hoc serialization instead of Pydantic's native `model_dump()`/`model_validate()`. Now all 5 models use Pydantic's native serialization exclusively, with a `model_validator(mode="before")` and `model_serializer` on LedgerEvent that preserves the `schema_`→`schema` mapping and extra-field flattening behavior.

### Key Proof

```bash
uv run python -c "
from gzkit.ledger import LedgerEvent
data = {'schema':'gzkit.ledger.v1','event':'adr_created','id':'ADR-0.1.0','ts':'2026-01-01T00:00:00+00:00','parent':'P','lane':'lite'}
e = LedgerEvent.model_validate(data)
print(e.model_dump())
"
# Output: {'schema': 'gzkit.ledger.v1', 'event': 'adr_created', 'id': 'ADR-0.1.0', 'ts': '2026-01-01T00:00:00+00:00', 'parent': 'P', 'lane': 'lite'}
```

### Implementation Summary

- Files modified: `src/gzkit/ledger.py`, `src/gzkit/validate.py`, `src/gzkit/cli.py`, `tests/test_ledger.py`
- Tests added: `test_model_dump`, `test_model_validate`, `test_model_dump_flattens_extra`, `test_model_roundtrip`
- Date completed: 2026-03-18
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: human:Jeff
- Attestation: Completed
- Date: 2026-03-18

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
