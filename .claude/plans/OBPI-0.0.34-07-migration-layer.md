# Plan: OBPI-0.0.34-07 — Migration Layer

## OBPI Reference
OBPI-0.0.34-07-migration-layer

## ADR Decision Item (verbatim)
"Migration layer. Pydantic schema versioning so model refactors do not break rendered-output stability across releases."

## Context

OBPI-07 adds the schema migration backstop for the ADR-0.0.34 content substrate.
All models are currently at schema_version 1; MIGRATIONS dict starts empty.
Prerequisites confirmed: CONTENT_MODELS importable, `gz content import --help` exits 0.

## Files

### New
- `src/gzkit/content/migration/__init__.py` — public MIGRATIONS export
- `src/gzkit/content/migration/registry.py` — MIGRATIONS dict + apply_migrations dispatcher
- `tests/content/test_migration_layer.py` — 5 REQ tests (TDD-derived from brief)

### Modified
- `src/gzkit/content/models/base.py` — add `schema_version: int = 1` to BaseContentModel
- `src/gzkit/content/parse/markdown_parser.py` — add _extract_schema_version helper + auto-migration in parse()

## Steps

### Step 1: TDD Red Phase — write failing tests

Write `tests/content/test_migration_layer.py` with test classes derived from
the brief's 5 REQs. All tests fail at start (no migration module, no schema_version field).

Test classes:
- `TestSchemaVersionField` — REQ-0.0.34-07-01: every model instance has schema_version == 1
- `TestMigrationRegistry` — REQ-0.0.34-07-02: MIGRATIONS is a dict
- `TestAutoMigrationOnParse` — REQ-0.0.34-07-03: registered migrations applied in sequence
- `TestStabilityInvariant` — REQ-0.0.34-07-04: unknown version fails-closed with non-zero exit
- `TestMigrationPurity` — REQ-0.0.34-07-05: calling a migration twice yields equal output

### Step 2: Add schema_version to BaseContentModel

Modify `src/gzkit/content/models/base.py`:
- Add `schema_version: int = 1` field to BaseContentModel
- No other changes; all subclasses inherit the field with default 1

### Step 3: Create migration registry

Create `src/gzkit/content/migration/registry.py`:
- `class MigrationError(ValueError): pass`
- `MIGRATIONS: dict[tuple[str, int, int], Callable[[BaseContentModel], BaseContentModel]] = {}`
- `apply_migrations(model, content_type, source_version, target_version) -> BaseContentModel`:
  - If source_version == target_version: return model unchanged
  - If source_version < target_version: apply migrations v→v+1 in sequence using MIGRATIONS[(content_type, v, v+1)]
  - If any step has no registered migration: raise MigrationError with version info
  - If source_version > target_version (unknown future): raise MigrationError

Create `src/gzkit/content/migration/__init__.py`:
- Export MIGRATIONS from registry

### Step 4: Wire auto-migration in parser

Modify `src/gzkit/content/parse/markdown_parser.py`:
- Add `_extract_schema_version(lines: list[str]) -> int` helper:
  - Scan lines for "Schema-version: N" (using _find_inline_value pattern), default 1
- Modify `parse()` to:
  1. Extract source_version using _extract_schema_version(lines)
  2. Construct model via _PARSERS dispatch (unchanged)
  3. Determine target_version = type(model).model_fields['schema_version'].default
  4. If source_version != target_version: call apply_migrations(model, as_type, source_version, target_version)
  5. Return (possibly migrated) model

### Step 5: Verify all REQs pass

Run tests, lint, typecheck:
```
uv run gz arb step --name unittest -- uv run -m unittest tests.content.test_migration_layer -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Verification

```bash
uv run python -c "from gzkit.content.migration import MIGRATIONS; assert isinstance(MIGRATIONS, dict)"
uv run python -m unittest tests.content.test_migration_layer -v
uv run gz check
```

## Notes

**Destination-in-mind:** MIGRATIONS = {} at initial release. All models at
schema_version 1. The infrastructure is in place for future model refactors
to register migration callables without breaking rendered-output stability.

**Rejected alternatives:**
1. YAML frontmatter for schema_version — stdlib-first constraint; no pyyaml.
   Inline "Schema-version: N" follows existing _find_inline_value pattern.
2. Migrations on field dicts — brief requires model-instance callables.
3. Separate SchemaVersionMixin — unnecessary; adding to BaseContentModel
   directly keeps the hierarchy flat.

**MigrationError inherits ValueError** so callers using ValueError catch
blocks remain compatible without widening their except surface.
