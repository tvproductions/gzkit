---
id: OBPI-0.0.8-01-flag-models-and-registry
parent: ADR-0.0.8-feature-toggle-system
item: 1
lane: Heavy
status: attested_completed
---

# OBPI-0.0.8-01: Flag Models and Registry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #1 — "Typed flag models with category rules" and #2 — "Source-controlled registry with JSON Schema"

**Status:** Completed

## Objective

Define the foundational Pydantic data models for the feature flag system:
FlagSpec (individual flag metadata), FlagCategory (release, ops, migration,
development), FlagEvaluation (resolved value with source attribution), and
custom error types (UnknownFlagError, InvalidFlagValueError). Implement the
registry loader that reads and validates `data/flags.json` against a JSON
Schema.

## Lane

**Heavy** — Introduces a new `src/gzkit/flags/` subpackage, a new
`data/flags.json` registry artifact, and a `data/schemas/flags.schema.json`
schema. These are new source-controlled contracts.

## Dependencies

- **Upstream:** None. This is the foundation OBPI.
- **Downstream:** OBPI-02 (FlagService), OBPI-04 (diagnostics).

## Allowed Paths

- `src/gzkit/flags/__init__.py` — Public API exports
- `src/gzkit/flags/models.py` — FlagSpec, FlagCategory, FlagEvaluation, errors
- `src/gzkit/flags/registry.py` — Registry loader and validator
- `data/flags.json` — Source-controlled flag registry
- `data/schemas/flags.schema.json` — JSON Schema for registry validation
- `tests/test_flag_models.py` — Model unit tests
- `tests/test_flag_registry.py` — Registry unit tests

## Denied Paths

- `src/gzkit/flags/service.py` — Belongs to OBPI-02
- `src/gzkit/flags/decisions.py` — Belongs to OBPI-03
- `src/gzkit/commands/` — CLI belongs to OBPI-05
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: FlagSpec MUST use Pydantic BaseModel with `ConfigDict(frozen=True, extra="forbid")`.
1. REQUIREMENT: FlagCategory MUST be a StrEnum with members: `release`, `ops`, `migration`, `development`.
1. REQUIREMENT: FlagSpec MUST include all fields from ADR Section 6.5: key, category, default, description, owner, introduced_on, review_by, remove_by, linked_adr, linked_issue.
1. REQUIREMENT: Category-specific validation rules MUST be enforced at model level: `release` and `migration` require `remove_by`; `ops` requires `review_by`; `development` requires `remove_by` and `default=false`.
1. REQUIREMENT: FlagEvaluation MUST capture: key, resolved value, source (which precedence layer provided the value).
1. REQUIREMENT: UnknownFlagError and InvalidFlagValueError MUST be typed exceptions inheriting from a common FlagError base.
1. REQUIREMENT: Registry loader MUST validate `data/flags.json` against `data/schemas/flags.schema.json`.
1. REQUIREMENT: Registry loader MUST return a dict mapping flag keys to FlagSpec instances.
1. REQUIREMENT: Duplicate keys in the registry MUST raise an error at load time.
1. NEVER: Use stdlib dataclasses — Pydantic only.
1. ALWAYS: Type hints use modern syntax (`str | None`, `list[str]`).

> STOP-on-BLOCKERS: None expected. This is the foundation OBPI.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist items #1 and #2 referenced

### Gate 2: TDD

- [x] Unit tests validate FlagSpec creation with valid metadata
- [x] Unit tests validate category-specific validation rules (remove_by, review_by)
- [x] Unit tests validate FlagCategory enum membership
- [x] Unit tests validate FlagEvaluation roundtrip
- [x] Unit tests validate error type hierarchy
- [x] Unit tests validate registry loading from valid JSON
- [x] Unit tests validate registry rejection of invalid JSON (schema mismatch)
- [x] Unit tests validate duplicate key detection
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [x] Module docstrings in models.py and registry.py

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.0.8-01-01: Given valid flag metadata with category `ops` and `review_by` set, when FlagSpec is constructed, then the model validates without error.
- [x] REQ-0.0.8-01-02: Given flag metadata with category `release` and no `remove_by`, when FlagSpec is constructed, then a ValidationError is raised.
- [x] REQ-0.0.8-01-03: Given flag metadata with category `development` and `default=true`, when FlagSpec is constructed, then a ValidationError is raised.
- [x] REQ-0.0.8-01-04: Given a valid `data/flags.json` file, when the registry loader runs, then all entries parse into FlagSpec instances keyed by flag key.
- [x] REQ-0.0.8-01-05: Given a `data/flags.json` with a duplicate key, when the registry loader runs, then an error is raised.
- [x] REQ-0.0.8-01-06: Given a `data/flags.json` that violates the JSON Schema, when the registry loader runs, then a validation error is raised.

## Verification Commands

```bash
# Model and registry tests
uv run -m unittest tests.test_flag_models tests.test_flag_registry -v

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck

# Schema validation (registry loads cleanly)
python -c "from gzkit.flags.registry import load_registry; print(len(load_registry()))"
```

## Evidence

### Implementation Summary

- Files created: `src/gzkit/flags/__init__.py`, `src/gzkit/flags/models.py`, `src/gzkit/flags/registry.py`, `data/flags.json`, `data/schemas/flags.schema.json`, `tests/test_flag_models.py`, `tests/test_flag_registry.py`
- Validation commands run: lint (clean), typecheck (clean), test (2095 pass), docs validate (pass), mkdocs build --strict (pass)
- Date completed: 2026-03-30

### Key Proof

```
$ uv run -m unittest tests.test_flag_models tests.test_flag_registry -v
Ran 39 tests in 0.004s — OK (27 model tests, 12 registry tests)
All 6 REQ acceptance criteria covered by @covers-decorated tests.
```

---

**Brief Status:** Completed
