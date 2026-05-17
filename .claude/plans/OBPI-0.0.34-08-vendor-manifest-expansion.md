# Plan: OBPI-0.0.34-08 — Vendor Manifest Expansion

**OBPI:** OBPI-0.0.34-08-vendor-manifest-expansion
**Parent ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**Lane:** Heavy
**Date:** 2026-05-17

## Context

Implements ADR-0.0.34 § Decision item #8 (verbatim):
> "Vendor manifest expansion. ADR-0.16.0 OBPI-03 seeded the vendor manifest schema; this ADR binds it as the canonical declaration of which content types render to which vendor mirrors."

The render pipeline (`src/gzkit/content/render/pipeline.py`) already has a placeholder:
```python
# OBPI-0.0.34-08 (vendor manifest) replaces this table when it lands.
_VENDOR_ROUTING: frozenset[tuple[str, str]] = frozenset({...})
```

This plan replaces that placeholder with manifest-driven routing.

## Discrepancies from Brief

1. **Prerequisite mismatch:** Brief claims `data/vendor-manifest.json` and `src/gzkit/schemas/vendor_manifest.json` are "ADR-0.16.0 OBPI-03 artifacts." OBPI-0.16.0-03 only extended `.gzkit/manifest.json` with a `vendors` enablement section; it did NOT create these separate files. The render pipeline's explicit placeholder confirms these files are created here, not extended.

2. **`trust_audits.py` is a package, not a file.** Brief lists `src/gzkit/governance/trust_audits.py` (does not exist). Correct paths are `src/gzkit/governance/trust_audits/vendor_manifest.py` (new) and `src/gzkit/governance/trust_audits/__init__.py` (modify for re-export).

3. **Expanded allowlist.** CLI flag registration requires additional paths not in brief:
   - `src/gzkit/commands/validate_cmd.py` — scope parameter registration
   - `src/gzkit/cli/parser_maintenance.py` — `--vendor-manifest` argument

## Files

### Create (new)
- `src/gzkit/schemas/vendor_manifest.json` — JSON Schema for `data/vendor-manifest.json`
- `data/vendor-manifest.json` — vendor manifest with `content_type_routes`
- `src/gzkit/content/vendors.py` — `routes_for(content_type) -> list[str]` helper
- `src/gzkit/governance/trust_audits/vendor_manifest.py` — `validate_vendor_manifest(project_root)` audit
- `tests/content/test_vendor_manifest.py` — schema validation, route enumeration, drift fail-closed

### Modify (existing)
- `src/gzkit/content/render/pipeline.py` — replace `_VENDOR_ROUTING` frozenset with `vendors.routes_for()`
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_vendor_manifest`
- `src/gzkit/commands/validate_cmd.py` — add `check_vendor_manifest: bool` scope parameter
- `src/gzkit/cli/parser_maintenance.py` — add `--vendor-manifest` argument

## Steps

### Step 1: TDD Red — Write failing tests

Write `tests/content/test_vendor_manifest.py` with tests derived from REQs:

- `TestSchemaValidation` — REQ-0.0.34-08-01: manifest validates against schema; `gz validate --vendor-manifest` exits 0
  - `test_manifest_validates_against_schema`: load manifest + schema, jsonschema validate passes
  - `test_schema_clean_case`: data/vendor-manifest.json validates with no errors

- `TestRoutesFor` — REQ-0.0.34-08-04: `routes_for(content_type)` returns declared vendors (no implicit expansion/drop)
  - `test_routes_for_known_content_type`: `routes_for("AgentContract")` returns `["claude"]`
  - `test_routes_for_all_eight_types`: all 8 content types return non-empty lists
  - `test_routes_for_unknown_returns_empty`: `routes_for("Unknown")` returns `[]`

- `TestManifestDriftFailClosed` — REQ-0.0.34-08-03: missing `content_type_routes` entry fails validation
  - `test_missing_content_type_route_fails_validation`: manifest with extra content_type but missing route → validate exits non-zero

- `TestRoundTrip` — REQ-0.0.34-08-04: enumerated `(content_type, vendor)` pairs equal manifest's declared routes
  - `test_route_enumeration_round_trip`: enumerate all routes from manifest, compare to expected set

- `TestTestSuiteCovers` — REQ-0.0.34-08-05: covers schema-clean, drift fail-closed, round-trip
  - (covered by the tests above; this REQ is satisfied structurally)

Add `@covers("REQ-0.0.34-08-NN")` decorators to each test class/method.

Run: `uv run -m unittest tests.content.test_vendor_manifest -v` → expect failures (no implementation yet).

### Step 2: Create JSON Schema `src/gzkit/schemas/vendor_manifest.json`

Schema structure:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "vendor_manifest",
  "type": "object",
  "required": ["content_type_routes"],
  "additionalProperties": false,
  "properties": {
    "content_type_routes": {
      "type": "object",
      "description": "Maps each content type class name to the vendor mirrors it renders to.",
      "additionalProperties": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1
      }
    }
  }
}
```

### Step 3: Create `data/vendor-manifest.json`

Seed with the 8 content types from `_VENDOR_ROUTING` (all route to `["claude"]`):
```json
{
  "content_type_routes": {
    "AgentContract": ["claude"],
    "Bullet": ["claude"],
    "Chore": ["claude"],
    "Handoff": ["claude"],
    "Persona": ["claude"],
    "Rule": ["claude"],
    "Scenario": ["claude"],
    "Skill": ["claude"]
  }
}
```

### Step 4: Create `src/gzkit/content/vendors.py`

Module with:
- `_load_manifest(project_root: Path | None) -> dict[str, list[str]]` — load and parse `data/vendor-manifest.json`; fall back to `_VENDOR_ROUTING` if not found (fail-safe during bootstrap)
- `routes_for(content_type: str, *, project_root: Path | None = None) -> list[str]` — return vendor list for a content type; `[]` if not registered

Use `importlib.resources` or `Path` for resolving the manifest path relative to project root or package root.

### Step 5: Create `src/gzkit/governance/trust_audits/vendor_manifest.py`

Implement `validate_vendor_manifest(project_root: Path) -> list[ValidationError]`:
- Load `data/vendor-manifest.json`
- Load `src/gzkit/schemas/vendor_manifest.json`
- Validate manifest against schema using `jsonschema` (already a dependency) or `gzkit.core.validation_rules`
- Check REQ-0.0.34-08-03: for each registered content type (from `content_type_routes`), all keys present → pass; any gap → exit 3

### Step 6: Wire trust_audits

**`src/gzkit/governance/trust_audits/__init__.py`:**
- Add import of `validate_vendor_manifest` from `vendor_manifest` module
- Add to `__all__`

**`src/gzkit/commands/validate_cmd.py`:**
- Add `check_vendor_manifest: bool = False` parameter to `collect_validation_errors()`
- Register in `explicit_scopes` dict: `"vendor_manifest": check_vendor_manifest`
- Add runner in scope dispatch: `"vendor_manifest": lambda: validate_vendor_manifest(project_root)`
- Add to `_other_scopes_active` list

**`src/gzkit/cli/parser_maintenance.py`:**
- Add `--vendor-manifest` argument with `dest="check_vendor_manifest"`, `action="store_true"`, and help text citing ADR-0.0.34 OBPI-08

### Step 7: Update render pipeline `src/gzkit/content/render/pipeline.py`

Replace `_VENDOR_ROUTING` frozenset with manifest-driven lookup:
- Remove `_VENDOR_ROUTING` constant
- In `render()`, call `vendors.routes_for(content_type, project_root=project_root)` and check vendor is in the returned list
- The check changes from `if (content_type, vendor) not in _VENDOR_ROUTING` to `if vendor not in vendors.routes_for(content_type)`

### Step 8: TDD Green — Verify all tests pass

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests.content.test_vendor_manifest -v
uv run -m unittest -q
```

All tests should now be Green.

### Step 9: Verification

Run full brief verification suite:
```bash
uv run gz validate --vendor-manifest
uv run python -c "import json; m = json.load(open('data/vendor-manifest.json')); assert 'content_type_routes' in m, sorted(m)"
uv run python -m unittest tests.content.test_vendor_manifest -v
rg -q "content_type_routes" src/gzkit/content/render/pipeline.py || echo "FAIL: no manifest ref in pipeline"
```

Check no hard-coded vendor branches remain:
```bash
rg -n "vendor\s*==\s*['\"]claude['\"]" src/gzkit/content/render/ && echo "FAIL: hard-coded branch found" || echo "PASS: no hard-coded branches"
```

## Verification Commands

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --vendor-manifest
uv run python -m unittest tests.content.test_vendor_manifest -v
uv run mkdocs build --strict
```

## Notes

### Destination-in-mind
Before writing this plan, I had already concluded: CREATE `data/vendor-manifest.json` with 8 content types all routing to `["claude"]`, replace `_VENDOR_ROUTING` frozenset with manifest-driven routing via a new `vendors.py` helper, and add `gz validate --vendor-manifest` by creating a new trust_audits submodule.

### Rejected alternatives
1. **Declare blocker GHI and halt.** Rejected — render pipeline's explicit comment names OBPI-08 as the creator. The "STOP-on-BLOCKERS" language in the brief was authored against an incorrect prerequisite assumption about OBPI-0.16.0-03.
2. **Extend `.gzkit/manifest.json` vendors section.** Rejected — brief explicitly lists `data/vendor-manifest.json` as a separate artifact; different concern (enablement vs. content routing).
3. **Use manifest.json schema for vendor routing.** Rejected — brief requires separate `src/gzkit/schemas/vendor_manifest.json`; separation of concerns (enablement schema vs. routing schema).
4. **Single module `trust_audits.py` (not package).** Rejected — `trust_audits` is already a package; new scope must follow the established pattern of a new submodule + `__init__.py` re-export.
