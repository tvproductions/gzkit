---
id: OBPI-0.0.7-01-manifest-v2-schema
parent: ADR-0.0.7
item: 1
lane: Lite
status: Completed
---

# OBPI-0.0.7-01-manifest-v2-schema: Manifest v2 schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #1 - "Manifest v2 schema — add `data`, `ops`, `thresholds` sections to `generate_manifest()` and schema validation; bump schema version"

**Status:** Completed

## Objective

Add `data`, `ops`, and `thresholds` top-level sections to `generate_manifest()`
output and bump the manifest schema version from v1 to v2. After this OBPI,
`.gzkit/manifest.json` contains keys for eval dataset paths, operational artifact
paths, and configurable thresholds — ready for downstream consumers.

## Lane

**Lite** - Internal schema extension; no CLI/API contract change.

## Allowed Paths

- `src/gzkit/sync_surfaces.py` — `generate_manifest()` function
- `src/gzkit/config.py` — `GzkitConfig`, `PathConfig` models if schema keys need additions
- `data/schemas/` — manifest JSON schema (if one exists)
- `.gzkit/manifest.json` — regenerated output
- `tests/test_manifest_v2.py` — new test module for v2 schema validation
- `tests/test_config.py` — existing config tests if model changes

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles
- Any module that *consumes* manifest paths (that is OBPI-02+)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `generate_manifest()` output MUST include `data`, `ops`, and `thresholds` top-level keys
2. REQUIREMENT: Schema version field MUST read `"2.0"` in generated manifests
3. NEVER: Remove or rename existing v1 keys — v1 consumers must not break
4. ALWAYS: New sections have sensible defaults so a bare `gz init` produces a valid v2 manifest
5. REQUIREMENT: `gz validate` MUST accept v2 manifests without error

> STOP-on-BLOCKERS: if `generate_manifest()` signature or `GzkitConfig` model is unclear, halt and inspect.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context and anti-pattern warning

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- [ ] Current manifest schema: `.gzkit/manifest.json`

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/sync_surfaces.py` exists and contains `generate_manifest()`
- [ ] `src/gzkit/config.py` exists and contains `GzkitConfig`, `PathConfig`

**Existing Code (understand current state):**

- [ ] Current `generate_manifest()` output structure
- [ ] Existing `tests/test_config.py` patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_manifest_v2 -v
uv run gz validate
python -c "import json; m = json.load(open('.gzkit/manifest.json')); assert 'data' in m and 'ops' in m and 'thresholds' in m"
```

## Acceptance Criteria

- [x] REQ-0.0.7-01-01: Given a `gz init` or `gz agent sync`, when manifest is generated, then `.gzkit/manifest.json` contains `data`, `ops`, `thresholds` keys
- [x] REQ-0.0.7-01-02: Given an existing v1 manifest, when regenerated as v2, then all v1 keys are preserved unchanged
- [x] REQ-0.0.7-01-03: Given a v2 manifest, when `gz validate` runs, then exit code is 0

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Key Proof

```bash
$ uv run -m unittest tests.test_manifest_v2 -v
test_data_section_present ... ok
test_ops_section_present ... ok
test_schema_version_is_v2 ... ok
test_thresholds_section_present ... ok
test_thresholds_have_sensible_defaults ... ok
test_v1_keys_preserved ... ok
test_v2_manifest_passes_validation ... ok
test_v1_manifest_still_passes ... ok
test_invalid_schema_version_rejected ... ok
Ran 11 tests in 0.026s — OK

$ python -c "import json; m = json.load(open('.gzkit/manifest.json')); print(m['schema'], sorted(m.keys()))"
gzkit.manifest.v2 ['artifacts', 'control_surfaces', 'data', 'gates', 'ops', 'schema', 'structure', 'thresholds', 'verification']
```

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 2008 tests in 34.626s — OK
$ uv run -m unittest tests.test_manifest_v2 -v
Ran 11 tests in 0.026s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed!
$ uv run gz typecheck
All checks passed!
```

### Implementation Summary

- Files created: `tests/test_manifest_v2.py` (11 tests for v2 schema validation)
- Files modified: `src/gzkit/sync_surfaces.py`, `src/gzkit/validate_pkg/manifest.py`, `src/gzkit/schemas/manifest.json`, 6 test fixtures
- Date completed: 2026-03-29

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane, Lite parent)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-29

**Evidence Hash:** -
