# Plan: OBPI-0.25.0-09 Schema Pattern Comparison

## Context

OBPI-0.25.0-09 evaluates airlineops `core/schema.py` (90 lines) against gzkit `schemas/__init__.py` (49 lines) to decide: Absorb, Confirm, or Exclude. The two modules serve **entirely different purposes** despite sharing the word "schema":

- **airlineops `core/schema.py`**: SQLite DDL helpers (`infer_sql_type`, `ensure_table`, `ensure_table_with_schema`, `normalize_union_rows`) extracted from the data warehouse ingestion pipeline. Used in exactly one place: `airlineops/warehouse/ingest/loader/io.py`.
- **gzkit `schemas/__init__.py`**: JSON Schema loading for governance artifact validation (`load_schema`, `get_schema_path`). gzkit has zero SQLite usage.

**Decision: Exclude** — the airlineops module is airline-domain data warehouse infrastructure. It fails the subtraction test: SQLite DDL helpers for JSONL-to-SQL ingestion are pure airline domain, not reusable governance infrastructure.

## Implementation Steps

### Step 1: Update the OBPI brief with comparison and decision

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-09-schema-pattern.md`

Add three sections before the Completion Checklist:

1. **Comparison Analysis** — document what each module does, their different domains, the single-callsite isolation in airlineops, and gzkit's zero SQLite usage
2. **Decision: Exclude** — record rationale citing the subtraction test failure and domain mismatch
3. **Gate 4 (BDD): N/A** — no operator-visible behavior changes since nothing is absorbed

Check the Gate checkboxes:
- Gate 1 (ADR): check — intent recorded
- Gate 2 (TDD): check — no absorption, existing tests remain green
- Gate 3 (Docs): check — decision rationale completed
- Gate 4 (BDD): check — N/A recorded with rationale

### Step 2: Verify quality gates

```bash
uv run gz test
uv run gz lint
uv run gz typecheck
```

No code changes, so these should pass unchanged.

## Critical Files

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-09-schema-pattern.md` (edit)
- `../airlineops/src/airlineops/core/schema.py` (read-only reference)
- `src/gzkit/schemas/__init__.py` (read-only reference)

## Verification

```bash
# Brief records decision
rg -n 'Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-09-schema-pattern.md

# Quality gates
uv run gz test
uv run gz lint
uv run gz typecheck
```
