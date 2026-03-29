---
id: OBPI-0.0.7-02-resolution-helpers
parent: ADR-0.0.7
item: 2
lane: Lite
status: Accepted
---

# OBPI-0.0.7-02-resolution-helpers: Resolution helpers

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #2 - "Resolution helpers — create `manifest_path(manifest, section, key)` helper; establish parameter-threading pattern"

**Status:** Accepted

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

- [ ] REQ-0.0.7-02-01: Given a v2 manifest with `data.eval_datasets` key, when `manifest_path(m, "data", "eval_datasets")` is called, then it returns a `Path` relative to project root
- [ ] REQ-0.0.7-02-02: Given a manifest missing a requested key, when `manifest_path()` is called, then `KeyError` is raised with section and key names in the message
- [ ] REQ-0.0.7-02-03: Given a v1 manifest (no `data`/`ops`/`thresholds` sections), when `manifest_path()` is called for an existing v1 key, then it resolves correctly

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane, Lite parent)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
