# AUDIT PLAN (Gate-5) — ADR-0.15.0

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.15.0-pydantic-schema-enforcement |
| ADR Title | Pydantic Schema Enforcement |
| SemVer | 0.15.0 |
| ADR Dir | docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement |
| Audit Date | 2026-03-18 |
| Auditor(s) | Agent (Claude Code) + Human |

## Purpose

Confirm ADR-0.15.0 implementation is complete by validating its claims with reproducible CLI evidence. All dataclass models are migrated to Pydantic BaseModel, validation is declarative, and JSON Schema cross-validation is enforced by test.

**Audit Trigger:** Post-implementation Gate-5 validation. All 4 OBPIs attested completed.

## Scope & Inputs

**Primary contract surfaces:**

- Core models: `src/gzkit/config.py`, `src/gzkit/validate.py`, `src/gzkit/ledger.py`
- Frontmatter models: `src/gzkit/models/frontmatter.py`
- Typed events: `src/gzkit/events.py`
- Schemas: `src/gzkit/schemas/*.json`
- Tests: `tests/test_models.py`, `tests/test_validate.py`, `tests/test_ledger.py`, `tests/test_schemas.py`

## Planned Checks

| Check | Command / Method | Expected Signal | Status |
|-------|------------------|-----------------|--------|
| Unit tests pass | `uv run -m unittest -q` | 588+ tests OK | Pending |
| Lint clean | `uv run gz lint` | All checks passed | Pending |
| Type check clean | `uv run gz typecheck` | All checks passed | Pending |
| Docs build | `uv run mkdocs build --strict` | Build clean | Pending |
| Gates pass | `uv run gz gates --adr ADR-0.15.0` | Gate 1+2 PASS | Pending |
| Config paths | `uv run gz check-config-paths` | Passed | Pending |
| CLI audit | `uv run gz cli audit` | Note known issue | Pending |
| Ledger check | `uv run gz adr audit-check ADR-0.15.0-pydantic-schema-enforcement` | Review issues | Pending |
| Capability 1: Core models are Pydantic | Python import check | BaseModel bases | Pending |
| Capability 2: Frontmatter validation | Construct valid/invalid models | Rejects bad input | Pending |
| Capability 3: Discriminated unions | TypeAdapter dispatch | Correct type resolution | Pending |
| Capability 4: Schema cross-validation | Compare hand/Pydantic schemas | Fields agree | Pending |

## Risk Focus

- **Behavioral regression:** Fields that changed defaults or validation rules during migration
- **Completion anchor drift:** All 4 OBPIs report anchor drift — metadata issue, not functional
- **Dirty worktree receipts:** All receipts captured from dirty worktree — cosmetic concern

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `audit/AUDIT.md`.
- All 4 ADR capabilities demonstrated live with actual output.
- No unresolved blocking failures.
