---
id: OBPI-0.17.0-04-json-schemas-and-validation
parent: ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir
item: 4
lane: heavy
status: Completed
---

# OBPI-0.17.0-04-json-schemas-and-validation: JSON Schemas and Validation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir.md`
- **Checklist Item:** #4 - "JSON Schemas and Validation"

**Status:** Completed

## Objective

Wire the canonical Layer 1 JSON schemas (`.gzkit/schemas/skill.schema.json` and `rule.schema.json`) into the validation pipeline via Pydantic frontmatter models, replacing the hardcoded enum sets in `validate.py` and adding cross-validation tests that prevent schema/model drift.

## Lane

**heavy** - Inherited from parent ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir (heavy).

> Heavy is reserved for command/API/schema/runtime-contract changes. This OBPI changes the validation contract for control surfaces (skills and instructions).

## Allowed Paths

- `src/gzkit/models/frontmatter.py` - Add SkillFrontmatter and InstructionFrontmatter Pydantic models
- `src/gzkit/validate.py` - Refactor `_validate_skill_frontmatter()` and `_validate_instruction_frontmatter()` to use models
- `tests/test_schemas.py` - Add cross-validation tests for skill/rule schema alignment
- `docs/design/adr/pre-release/ADR-0.17.0-*/obpis/OBPI-0.17.0-04-*.md` - This brief

## Denied Paths

- `.gzkit/schemas/` - Canonical schemas are read-only (already exist)
- `src/gzkit/schemas/` - Document validation schemas (out of scope)
- `src/gzkit/skills.py` - Procedural skill audit (not changed by this OBPI)
- `src/gzkit/rules.py` - RuleFrontmatter for canonical rules (not changed)
- `src/gzkit/cli.py` - No CLI flag changes
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SkillFrontmatter` Pydantic model MUST mirror `.gzkit/schemas/skill.schema.json` field names, types, enums, and patterns.
2. REQUIREMENT: `InstructionFrontmatter` Pydantic model MUST mirror `.gzkit/schemas/rule.schema.json` field names, types, enums, and required fields.
3. REQUIREMENT: `_validate_skill_frontmatter()` MUST use `SkillFrontmatter` for validation instead of hardcoded `_VALID_SKILL_CATEGORIES` and `_VALID_LIFECYCLE_STATES` sets.
4. REQUIREMENT: `_validate_instruction_frontmatter()` MUST use `InstructionFrontmatter` for validation instead of ad-hoc `applyTo` check.
5. REQUIREMENT: Cross-validation tests MUST verify Pydantic model constraints match JSON schema constraints (required fields, enum values, patterns).
6. NEVER: Remove or weaken existing validation — only replace the implementation mechanism.
7. ALWAYS: All existing tests must continue to pass.

> STOP-on-BLOCKERS: if `.gzkit/schemas/skill.schema.json` or `.gzkit/schemas/rule.schema.json` are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - three-layer control surface model

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.17.0-*/`
- [x] Related OBPIs: OBPI-01 (Skill Catalog), OBPI-02 (Rules Mirroring), OBPI-05 (Manifest Sync)

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit/schemas/skill.schema.json` exists (52 lines, validates skill frontmatter)
- [x] `.gzkit/schemas/rule.schema.json` exists (21 lines, validates instruction frontmatter)

**Existing Code (understand current state):**

- [x] `src/gzkit/models/frontmatter.py` — AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter models exist; no skill/instruction models
- [x] `src/gzkit/validate.py` lines 886-948 — `_validate_skill_frontmatter()` uses hardcoded sets
- [x] `src/gzkit/validate.py` lines 954-995 — `_validate_instruction_frontmatter()` checks only `applyTo`
- [x] `tests/test_schemas.py` — cross-validation for ADR/OBPI/PRD models; none for skill/rule
- [x] `src/gzkit/rules.py` lines 400-412 — `RuleFrontmatter` for canonical rules (different from instruction schema)

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

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] N/A — no user-facing doc changes (internal validation mechanism)

### Gate 4: BDD (Heavy only)

- [x] N/A — no behave features for schema validation internals

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification: cross-validation tests pass
uv run -m unittest tests.test_schemas -v

# Specific verification: validate surfaces still works
uv run gz validate --surfaces
```

## Acceptance Criteria

- [x] REQ-0.17.0-04-01: `SkillFrontmatter` Pydantic model exists in `frontmatter.py` with fields matching `skill.schema.json`
- [x] REQ-0.17.0-04-02: `InstructionFrontmatter` Pydantic model exists in `frontmatter.py` with fields matching `rule.schema.json`
- [x] REQ-0.17.0-04-03: `_validate_skill_frontmatter()` uses `SkillFrontmatter` model (hardcoded sets removed)
- [x] REQ-0.17.0-04-04: `_validate_instruction_frontmatter()` uses `InstructionFrontmatter` model
- [x] REQ-0.17.0-04-05: Cross-validation tests for skill schema alignment pass in `test_schemas.py`
- [x] REQ-0.17.0-04-06: Cross-validation tests for instruction/rule schema alignment pass in `test_schemas.py`
- [x] REQ-0.17.0-04-07: [doc] `uv run gz validate --surfaces` produces equivalent results to before

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
$ uv run gz test
Ran 692 tests in 19.403s — OK
$ uv run -m unittest tests.test_schemas -v
Ran 24 tests in 0.005s — OK (7 new cross-validation tests)
```

### Code Quality

```text
$ uv run gz lint
All checks passed! Lint passed.
$ uv run gz typecheck
All checks passed! Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
Documentation built in 2.31 seconds
N/A — internal validation mechanism, no user-facing doc changes
```

### Gate 4 (BDD)

```text
N/A — no behave features for schema validation internals
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-19
```

### Value Narrative

Before this OBPI, skill and instruction frontmatter validation used hardcoded Python sets (`_VALID_SKILL_CATEGORIES`, `_VALID_LIFECYCLE_STATES`) and ad-hoc field checks, disconnected from the canonical JSON schemas in `.gzkit/schemas/`. Schema and validation could drift silently. Now, `SkillFrontmatter` and `InstructionFrontmatter` Pydantic models mirror the canonical schemas, the validators use these models, and 7 cross-validation tests prevent model/schema drift.

### Key Proof

```text
$ uv run -m unittest tests.test_schemas.TestSkillSchemaAlignment tests.test_schemas.TestInstructionSchemaAlignment -v
test_all_schema_properties_have_model_fields (tests.test_schemas.TestSkillSchemaAlignment) ... ok
test_enum_values_match (tests.test_schemas.TestSkillSchemaAlignment) ... ok
test_pattern_constraints_match (tests.test_schemas.TestSkillSchemaAlignment) ... ok
test_required_fields_match (tests.test_schemas.TestSkillSchemaAlignment) ... ok
test_all_schema_properties_have_model_fields (tests.test_schemas.TestInstructionSchemaAlignment) ... ok
test_enum_values_match (tests.test_schemas.TestInstructionSchemaAlignment) ... ok
test_required_fields_match (tests.test_schemas.TestInstructionSchemaAlignment) ... ok
Ran 7 tests in 0.005s — OK

$ uv run gz validate --surfaces
All validations passed.
```

### Implementation Summary

- Files created/modified: `src/gzkit/models/frontmatter.py`, `src/gzkit/validate.py`, `tests/test_schemas.py`
- Tests added: TestSkillSchemaAlignment (4 tests), TestInstructionSchemaAlignment (3 tests)
- Date completed: 2026-03-19
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:Jeff`
- Attestation: attest completed
- Date: 2026-03-19

---

**Brief Status:** Completed

**Date Completed:** 2026-03-19

**Evidence Hash:** -
