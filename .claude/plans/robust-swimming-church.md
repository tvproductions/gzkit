# Plan: OBPI-0.25.0-05 — Dataset Version Pattern

## Context

OBPI-0.25.0-05 evaluates `airlineops/src/airlineops/core/dataset_version.py` (246 lines) against gzkit's `src/gzkit/lifecycle.py` (128 lines) to determine: Absorb, Confirm, or Exclude.

**Pre-analysis conclusion: Exclude.** The module is airline-domain-specific. The brief's premise of "partial coverage in lifecycle.py" is misleading — lifecycle.py handles governance state transitions, a completely different concern from dataset version identity/hashing.

This follows the established pattern from prior completed briefs in this ADR: domain-specific modules whose generic primitives are too trivial to warrant standalone absorption.

## Evidence Summary

**airlineops `dataset_version.py` — what it does:**
- `DatasetVersion` Pydantic model: composite identity for airline datasets via `dataset_id`, `source_version` (BTS/FAA archives), `schema_version`, `etl_version`, `content_hash`
- `compute_version_hash()`: deterministic JSON serialization -> SHA-256 (~10 lines)
- `compute_content_hash()`: raw bytes -> `sha256:hexdigest` (~3 lines)
- `create_dataset_version()`: factory with auto-computed hash
- `version_to_dict()` / `version_from_dict()`: Pydantic `.model_dump()` / `(**data)` wrappers

**gzkit `lifecycle.py` — what it does:**
- `LifecycleStateMachine`: validates state transitions for governance artifacts (ADR, OBPI, PRD, etc.)
- No version identity, no hashing, no content addressing
- Zero overlap with dataset versioning

**Subtraction test:**
- `dataset_id` — airline dataset identifier (BTS, FAA) -> domain-specific
- `source_version` — BTS/FAA archive version -> domain-specific
- `schema_version` / `etl_version` — ETL pipeline versioning -> domain-specific
- `content_hash` field + `compute_content_hash()` — generic but trivial (3 lines)
- Deterministic JSON -> SHA-256 pattern — a technique (~5 lines), not a module
- Frozen Pydantic + field validators — gzkit already follows this convention per models policy

**Generic residue: ~13 lines of trivial primitives.** Not enough to justify a module.

## Plan Steps

### Step 1: Document the comparison in the OBPI-0.25.0-05 brief

Update `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-05-dataset-version-pattern.md`:

- Add `## Comparison` section with feature-by-feature analysis table
- Add `## Decision: Exclude` section with rationale citing the subtraction test
- Add `## Closing Argument` authored from evidence
- Update frontmatter `status: Pending -> Completed` (will be set by `gz obpi complete` in Stage 5)
- Mark Gate 4 BDD as N/A with rationale (Exclude produces no operator-visible changes)
- Mark acceptance criteria checklist items

### Step 2: Verify

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
```

No code changes, so these should pass unchanged. The brief verification commands confirm the decision is recorded.

## Files Modified

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-05-dataset-version-pattern.md` — the only file changed

## Files NOT Modified (and why)

- No `src/gzkit/` changes — Exclude decision means no code absorption
- No `tests/` changes — no code to test
- No `features/` changes — Gate 4 BDD is N/A

## Verification

```bash
# Confirm decision is recorded in brief
rg -n 'Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-05-dataset-version-pattern.md

# Quality gates (should pass — no code changes)
uv run gz lint
uv run gz typecheck
uv run gz test
```
