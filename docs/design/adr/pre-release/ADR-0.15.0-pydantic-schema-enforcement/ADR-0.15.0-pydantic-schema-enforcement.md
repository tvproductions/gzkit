<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.15.0 — pydantic-schema-enforcement

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit all 14 dataclass models for field types, defaults, and frozen status
  1. Verify existing JSON schemas in `src/gzkit/schemas/` match current dataclass shapes
  1. Add `pydantic>=2.0` to `pyproject.toml` without changing any models yet

State: Prep is commit 1 (dependency + audit). Migration is commits 2-5 (one per OBPI).
STOP/BLOCKERS if any existing validation function has behavior that cannot be expressed
declaratively in Pydantic (hand-audit before migration).

**Date Added:** 2026-03-15
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.15.0
**Area:** Schema Enforcement — Lodestar AI-000

## Agent Context Frame — MANDATORY

**Role:** Migration implementer — replacing dataclasses with Pydantic BaseModel across
the entire model layer.

**Purpose:** Every structured data type in gzkit is enforced by Pydantic at runtime.
No dataclass for governance data. No ad-hoc validation for things Pydantic can express
declaratively. The lodestar (AI-000) and the code agree.

**Goals:**

- All 14+ dataclass models migrated to Pydantic BaseModel
- All hand-written validation in validate.py replaced with declarative Pydantic validators
- JSON Schema generation from Pydantic models (`model_json_schema()`) verified equivalent to hand-authored schemas
- Zero behavioral regression in existing `gz` commands

**Critical Constraint:** Implementations MUST preserve exact behavioral equivalence with
existing dataclass models and validation functions. Every field default, every validation
rule, every error message must produce identical outcomes. Migration is mechanical, not
redesign.

**Anti-Pattern Warning:** A failed implementation looks like: models migrate but validation
behavior changes subtly — a field that was optional becomes required, a default that was
`None` becomes `""`, a validation that checked `len(x) > 0` silently disappears. Tests
pass because they test the happy path, but governance validation regresses for edge cases.

**Integration Points:**

- `src/gzkit/config.py` — GzkitConfig, PathConfig
- `src/gzkit/validate.py` — ValidationError, ValidationResult, all validate_* functions
- `src/gzkit/ledger.py` — LedgerEvent, all event factory functions
- `src/gzkit/decomposition.py` — DecompositionScorecard
- `src/gzkit/quality.py` — QualityResult
- `src/gzkit/interview.py` — Question, Answer, InterviewResult
- `src/gzkit/skills.py` — Skill, SkillAuditIssue, SkillAuditReport
- `src/gzkit/commands/chores.py` — ChoreStep, ChoreDefinition, StepExecution
- `src/gzkit/schemas/` — 6 JSON schema files

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract unchanged (Lite lane) — no CLI/API/schema changes
  - Internal model layer migrated from dataclasses to Pydantic
- Config and schemas
  - JSON Schema files verified equivalent to Pydantic-generated schemas
  - `pyproject.toml` updated with Pydantic dependency
- Tests
  - stdlib `unittest` guards all model construction, validation, and serialization
  - Existing tests pass without modification (behavioral equivalence)
  - New tests cover Pydantic-specific validation (field validators, discriminated unions)
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

Close the gap between gzkit's stated architecture (AI-000: "JSON Schema defines shape;
Pydantic enforces at runtime") and its implemented reality (Python dataclasses with
hand-written validation). After this ADR, every structured data type in gzkit is a
Pydantic BaseModel, every validation rule is declarative, and JSON Schema can be
generated from models rather than hand-authored separately.

## Decision

- Migrate all 14+ dataclass models to Pydantic BaseModel (v2+)
- Replace hand-written validation functions in validate.py with Pydantic field validators
  and model validators where they express the same rules more declaratively
- Use Pydantic discriminated unions for ledger event type dispatch
- Verify `model_json_schema()` output matches hand-authored schemas; decide single-source
  direction (Pydantic-generated vs. hand-authored with cross-validation)
- Preserve frozen semantics for immutable models (DecompositionScorecard, ChoreStep, etc.)

## Interfaces

- **CLI (external contract):** No changes. All `gz` commands behave identically.
- **Config keys consumed:** `.gzkit/manifest.json` — now loaded via Pydantic model
- **Schemas:** `src/gzkit/schemas/*.json` — verified equivalent or replaced by Pydantic generation

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.15.0-01-core-model-migration | Migrate LedgerEvent, GzkitConfig, PathConfig, ValidationError, ValidationResult to Pydantic | Lite | Pending |
| 2 | OBPI-0.15.0-02-content-type-frontmatter-models | Create Pydantic models for ADR, OBPI, PRD frontmatter with pattern validators | Lite | Pending |
| 3 | OBPI-0.15.0-03-ledger-event-discrimination | Discriminated unions for typed ledger events; replace manual dispatch | Lite | Pending |
| 4 | OBPI-0.15.0-04-schema-generation-unification | Verify/generate JSON Schema from Pydantic models; decide single-source direction | Lite | Pending |

**Briefs location:** `briefs/OBPI-0.15.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)

---

## Rationale

The lodestar document (architectural-identity.md) declares AI-000: "Everything is
schema-driven. JSON Schema defines shape; Pydantic enforces at runtime." The codebase
uses dataclasses with 20+ hand-written validation functions. This is the single largest
gap between stated architecture and implemented reality. Every other lodestar claim is
realized in code. This one is not.

Pydantic v2 provides: field validators, model validators, discriminated unions, frozen
models, JSON Schema generation, and serialization — all capabilities currently
reimplemented by hand in validate.py. The migration eliminates ~200 lines of manual
validation code and makes the schema the single source of truth for both runtime
enforcement and documentation.

## Consequences

- Pydantic v2 added as a runtime dependency
- Hand-authored JSON schemas in `src/gzkit/schemas/` may be replaced by Pydantic-generated
  equivalents (decision in OBPI-04)
- All future data models must be Pydantic BaseModel — no new dataclasses for governance data
- validate.py shrinks significantly as declarative validators replace procedural code

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_models.py`, `tests/test_validate.py`, `tests/test_ledger.py`
- **BDD:** not applicable (Lite lane, no external contract change)
- **Docs:** lodestar architectural-identity.md already declares Pydantic; code now matches

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note
  in the brief once gates are green.

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.15.0`
- **Related pool ADR:** `ADR-pool.pydantic-schema-enforcement` (promoted)

### Source and Contracts

- Core modules: `src/gzkit/config.py`, `src/gzkit/validate.py`, `src/gzkit/ledger.py`,
  `src/gzkit/decomposition.py`, `src/gzkit/quality.py`, `src/gzkit/interview.py`,
  `src/gzkit/skills.py`, `src/gzkit/commands/chores.py`
- Schemas: `src/gzkit/schemas/*.json`

### Tests

- Unit: `tests/test_models.py`, `tests/test_validate.py`, `tests/test_ledger.py`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: Migration is mechanical — model shapes unchanged, validation behavior preserved

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| pyproject.toml | M | Pydantic v2+ in dependencies | Diff link | |
| src/gzkit/config.py | M | GzkitConfig, PathConfig are BaseModel | Diff link | |
| src/gzkit/validate.py | M | Declarative validators replace manual dispatch | Diff link | |
| src/gzkit/ledger.py | M | LedgerEvent is BaseModel; discriminated unions | Diff link | |
| src/gzkit/schemas/*.json | M or D | Verified equivalent or replaced by generation | Diff link | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. …

1. …

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.15.0 | Completed | Test User | 2026-03-18 | completed |
