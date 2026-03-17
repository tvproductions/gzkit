---
id: OBPI-0.15.0-01-core-model-migration
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 1
lane: Lite
status: Draft
---

# OBPI-0.15.0-01-core-model-migration: Core Model Migration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- **Checklist Item:** #1 - "OBPI-0.15.0-01: Migrate LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult to Pydantic"

**Status:** Draft

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

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- [ ] Related OBPIs in same ADR (02: frontmatter models, 03: ledger discrimination, 04: schema generation)

**Prerequisites (check existence, STOP if missing):**

- [ ] `pydantic>=2.12.5` in pyproject.toml dependencies
- [ ] `src/gzkit/ledger.py` exists with LedgerEvent dataclass
- [ ] `src/gzkit/config.py` exists with GzkitConfig, PathConfig dataclasses
- [ ] `src/gzkit/validate.py` exists with ValidationError, ValidationResult dataclasses

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/superbook_models.py` (existing Pydantic models)
- [ ] Test patterns: `tests/test_ledger.py`, `tests/test_config.py`, `tests/test_validate.py`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_ledger tests.test_config tests.test_validate -v
```

## Acceptance Criteria

- [ ] REQ-0.15.0-01-01: Given a LedgerEvent constructed with the same arguments, when serialized via model_dump(), then the output matches the original to_dict() output exactly.
- [ ] REQ-0.15.0-01-02: Given a GzkitConfig loaded from an existing manifest.json, when accessed via the same field paths, then all values match the dataclass version.
- [ ] REQ-0.15.0-01-03: Given a PathConfig with default values, when each field is read, then all 24 path defaults are identical to the dataclass defaults.
- [ ] REQ-0.15.0-01-04: Given a ValidationError and ValidationResult constructed with the same arguments, when serialized via model_dump(), then the output matches to_dict() exactly.
- [ ] REQ-0.15.0-01-05: Given the full gzkit test suite (532+ tests), when run after migration, then zero regressions — all tests pass.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

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

## Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

## Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: n/a
- Attestation: n/a
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
