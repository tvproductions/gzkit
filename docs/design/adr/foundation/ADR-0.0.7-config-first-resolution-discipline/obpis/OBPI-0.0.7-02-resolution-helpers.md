---
id: OBPI-0.0.7-02-resolution-helpers
parent: ADR-0.0.7-config-first-resolution-discipline
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.7-02-resolution-helpers: Resolution helpers

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #2 - "Resolution helpers — create `manifest_path(manifest, section, key)` helper; establish parameter-threading pattern"

**Status:** Completed

## Objective

Create a `manifest_path()` helper that resolves a path from a manifest section
and key, returning a `Path` relative to project root. Establish the
parameter-threading pattern where the CLI entry point loads the manifest once
and passes it to consumers — no module-level constants.

## Lane

**Lite** - Internal helper; no CLI/API contract change.

## Allowed Paths

- `src/gzkit/commands/common.py` — add `manifest_path()` helper near `load_manifest()`
- `tests/test_manifest_resolution.py` — new test module for resolution helper
- `tests/test_config.py` — if threading pattern changes config loading

## Denied Paths

- Paths not listed in Allowed Paths
- Modules that will be *migrated* to use the helper (that is OBPI-03, OBPI-04)
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `manifest_path(manifest, section, key)` MUST return a `Path` resolved relative to project root
2. REQUIREMENT: Helper MUST raise `KeyError` with a clear message when section or key is missing
3. NEVER: Import the helper at module level with a default manifest — callers must pass the manifest explicitly
4. ALWAYS: Helper must work with both v1 and v2 manifest structures (v1 sections return existing paths)

> STOP-on-BLOCKERS: if `load_manifest()` location or signature is unclear, inspect `src/gzkit/commands/common.py`.

## Discovery Checklist

**Context:**

- [ ] Parent ADR — understand threading pattern and anti-pattern warning
- [ ] `src/gzkit/commands/common.py` — current `load_manifest()` implementation
- [ ] OBPI-01 — manifest v2 schema (dependency)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 is implemented (v2 manifest sections exist)
- [ ] `src/gzkit/commands/common.py` contains `load_manifest()`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_manifest_resolution -v
```

## Acceptance Criteria

- [x] REQ-0.0.7-02-01: Given a v2 manifest with `data.eval_datasets` key, when `manifest_path(m, "data", "eval_datasets")` is called, then it returns a `Path` relative to project root
- [x] REQ-0.0.7-02-02: Given a manifest missing a requested key, when `manifest_path()` is called, then `KeyError` is raised with section and key names in the message
- [x] REQ-0.0.7-02-03: Given a v1 manifest (no `data`/`ops`/`thresholds` sections), when `manifest_path()` is called for an existing v1 key, then it resolves correctly

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

## Closing Argument

The `manifest_path()` helper eliminates ad-hoc path construction from manifest data
by providing a single resolution function that handles both v1 flat and v2 sectioned
manifest structures. Callers pass the manifest explicitly — no module-level constants
or default-argument coupling.

### Implementation Summary

- Helper: Added `manifest_path(manifest, section, key)` to `src/gzkit/commands/common.py`
- V2 support: Resolves `manifest[section][key]` for sectioned manifests
- V1 fallback: Falls back to `manifest[key]` top-level lookup for flat manifests
- Error handling: Raises `KeyError` with descriptive section+key messages
- Tests: Created `tests/test_manifest_resolution.py` with 7 tests covering all REQs

### Key Proof

```text
uv run -m unittest tests.test_manifest_resolution -v
test_resolves_v1_key_at_top_level ... ok
test_v1_missing_key_raises_keyerror ... ok
test_missing_key_raises_keyerror ... ok
test_missing_section_raises_keyerror ... ok
test_numeric_value_coerced_to_path ... ok
test_resolves_data_section_key ... ok
test_resolves_ops_section_key ... ok
Ran 7 tests in 0.000s — OK
```

## Evidence

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_manifest_resolution -v
Ran 7 tests in 0.000s — OK
```

### Code Quality

```text
uv run gz lint    → clean
uv run gz typecheck → clean
uv run gz test    → 2015 pass
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff (human)
- Attestation: attest completed
- Date: 2026-03-30

---

**Brief Status:** Completed

**Date Completed:** 2026-03-30

**Evidence Hash:** -
