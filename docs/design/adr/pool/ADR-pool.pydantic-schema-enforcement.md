---
id: ADR-pool.pydantic-schema-enforcement
status: Promoted
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: architectural-identity-schema-driven
promoted_to: ADR-0.15.0
promoted_date: 2026-03-15
---

# ADR-pool.pydantic-schema-enforcement: Migrate to Pydantic Schema Enforcement

## Status

Promoted → [ADR-0.15.0](../../pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md)

## Date

2026-03-15

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

The lodestar declares "JSON Schema defines shape; Pydantic enforces at runtime"
as the primary architectural principle (AI-000). The codebase currently uses
**Python dataclasses** for all 14+ data models. This ADR captures the migration
from dataclasses to Pydantic BaseModel, closing the gap between stated
architecture and implemented reality.

---

## Current State

- **14 dataclass models** across config.py, validate.py, ledger.py,
  decomposition.py, quality.py, interview.py, skills.py, chores.py
- **6 JSON schemas** in `src/gzkit/schemas/` (manifest, ledger, adr, obpi,
  prd, agents) + 1 ontology schema in `.gzkit/governance/`
- **Hand-written validation** in validate.py — ~20 validation functions that
  manually check frontmatter fields, headers, ledger entries
- **No Pydantic dependency** in `pyproject.toml`
- The hand-written validators are correct but fragile — each new field requires
  manual validation code rather than schema declaration

---

## Target Scope

### Phase 1: Core Models

- Add Pydantic dependency to `pyproject.toml`
- Migrate `LedgerEvent` → Pydantic BaseModel with field validators
- Migrate `GzkitConfig` / `PathConfig` → Pydantic BaseModel
- Migrate `ValidationError` / `ValidationResult` → Pydantic BaseModel

### Phase 2: Content Type Models

- Create Pydantic models for each content type frontmatter:
  - `AdrFrontmatter` — validates id pattern, status enum, lane enum
  - `ObpiFrontmatter` — validates id pattern, parent reference, status enum
  - `PrdFrontmatter` — validates id pattern, status, semver
- Replace manual frontmatter validation in validate.py with Pydantic

### Phase 3: Ledger Event Discrimination

- Use Pydantic discriminated unions for ledger event types
- Each event type gets a specific model with typed `extra` fields
- Replace `_validate_ledger_event_fields()` manual dispatch with Pydantic

### Phase 4: Manifest and Config

- Generate JSON Schema from Pydantic models (single source of truth)
- Replace hand-authored `src/gzkit/schemas/*.json` with Pydantic-generated
  schemas, or validate that hand-authored schemas match Pydantic models

### Invariant

After migration, the rule is: **if it's structured data, it has a Pydantic
model. Period.** No dataclass for structured governance data. No dict-of-str
for config. No ad-hoc validation functions for things Pydantic can express
declaratively.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No change to the JSON Schema files consumed by external tools — Pydantic
  models must produce equivalent schemas.
- No change to ledger format — events remain JSONL, just validated differently.
- No change to the `gz` CLI interface — all commands behave identically.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: All vendor alignment ADRs (Pydantic models define the shapes
  that vendor surfaces render), ADR-pool.storage-simplicity-profile (DB
  integration benefits from Pydantic ORM mode)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Pydantic version decided (v2+ required for JSON Schema generation,
   discriminated unions, and model serialization).
3. Migration ordering agreed (ledger models first vs. config models first).
4. Decision made: generate JSON Schema from Pydantic (single source) vs.
   maintain parallel schemas with cross-validation.

---

## Notes

- The gap between stated architecture (Pydantic) and implemented reality
  (dataclasses) is the most significant technical debt relative to the
  lodestar. Every other architectural claim is realized in code.
- Pydantic v2 with `model_json_schema()` can generate JSON Schema directly
  from models. This could eliminate the hand-authored schema files entirely,
  making the Pydantic model the single source of truth for both runtime
  validation and schema documentation.
- The frozen dataclasses (DecompositionScorecard, ChoreStep, ChoreDefinition,
  StepExecution) map naturally to Pydantic's `frozen=True` config.
- The existing validation functions in validate.py are well-tested and
  correct. Migration should verify behavioral equivalence, not just
  structural equivalence.
