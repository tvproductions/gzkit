---
id: OBPI-0.0.7-05-lint-rule-and-check-expansion
parent: ADR-0.0.7-config-first-resolution-discipline
item: 5
lane: Lite
status: Completed
---

# OBPI-0.0.7-05-lint-rule-and-check-expansion: Enforcement and chore integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #5 - "Enforcement and chore integration — add `Path(__file__).parents` lint rule; expand `check-config-paths`; update `hardcoded-root-eradication` chore with manifest-aware criteria"

**Status:** Completed

## Objective

Close the enforcement loop with three layers: (1) add a lint rule that catches
`Path(__file__).parents[` patterns at edit-time, (2) expand `gz check-config-paths`
to scan source for unmapped path literals at gate-time, (3) update the
`hardcoded-root-eradication` chore with manifest-aware acceptance criteria for
periodic sweeps. After this OBPI, regressions are caught at every stage.

## Lane

**Lite** - Internal enforcement tooling; no CLI/API contract change.

## Allowed Paths

- `src/gzkit/commands/quality.py` — lint rule additions
- `src/gzkit/commands/config_paths.py` — expand source-code path scanning
- `config/gzkit.chores.json` — update `hardcoded-root-eradication` chore
- `tests/test_config_paths.py` — expand tests for new scanning
- `tests/test_lint_*.py` — tests for new lint rule

## Denied Paths

- `src/gzkit/eval/` — already migrated in OBPI-03
- `src/gzkit/hooks/` — already migrated in OBPI-04
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz lint` MUST detect and fail on `Path(__file__).parents[` patterns in `src/gzkit/`
2. REQUIREMENT: `gz check-config-paths` MUST scan source for path literals not mapped to manifest keys
3. REQUIREMENT: `hardcoded-root-eradication` chore MUST include manifest-aware acceptance criteria
4. NEVER: Allow the lint rule to trigger on test files using `Path(__file__).parent` for fixture location
5. ALWAYS: Lint rule and check must exit non-zero when violations are found (fail-closed)

> STOP-on-BLOCKERS: if OBPIs 03 and 04 are not complete (violations still present), lint rule will produce false positives on known migration targets.

## Discovery Checklist

**Context:**

- [x] Parent ADR — understand three-layer enforcement model
- [x] OBPIs 03 and 04 complete (migration targets removed)

**Existing Code:**

- [x] `src/gzkit/commands/quality.py` — current lint implementation
- [x] `src/gzkit/commands/config_paths.py` — current check-config-paths implementation
- [x] `config/gzkit.chores.json` — current chore definitions

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Tests pass: `uv run gz test`
- [x] Lint rule catches synthetic violation in test
- [x] check-config-paths catches synthetic unmapped path in test

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint                           # passes (no violations remain)
uv run gz check-config-paths             # passes (all paths mapped)
uv run gz typecheck
uv run -m unittest -q
grep -rn "Path(__file__).*parents" src/gzkit/   # expect: no output
```

## Acceptance Criteria

- [x] REQ-0.0.7-05-01: Given a source file containing `Path(__file__).parents[`, when `gz lint` runs, then exit code is non-zero and violation is reported
- [x] REQ-0.0.7-05-02: Given a source file with a path literal not mapped to any manifest key, when `gz check-config-paths` runs, then it reports the unmapped literal
- [x] REQ-0.0.7-05-03: Given the `hardcoded-root-eradication` chore, when `gz chores show hardcoded-root-eradication` runs, then acceptance criteria reference manifest v2 keys
- [x] REQ-0.0.7-05-04: Given clean source (post-migration), when `gz lint` and `gz check-config-paths` run, then both exit 0

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, enforcement verified
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Implementation Summary

- Added `_find_parents_subscript_lines()` and `run_parents_pattern_lint()` to `quality.py` — AST-based detection of `Path(__file__).parents[N]` subscript access in `src/gzkit/`
- Added `_flatten_manifest_paths()`, `_is_path_covered_by_manifest()`, and `_collect_source_path_literal_issues()` to `config_paths.py` — AST-based source scanning for unmapped path literals with parent directory derivation
- Updated `ops/chores/hardcoded-root-eradication/acceptance.json` and `CHORE.md` with manifest-aware criteria (`gz lint`, `gz check-config-paths`, source-wide parents scan)
- Created `tests/test_lint_parents.py` (5 tests) and `tests/test_config_paths.py` (11 tests)

### Key Proof

```bash
$ uv run gz lint
# Lint passed. (includes ruff + ADR path contract + parents-pattern lint)

$ uv run gz check-config-paths
# Config-path audit passed. (includes source path literal scan)

$ uv run -m unittest tests.test_lint_parents tests.test_config_paths -v
# Ran 16 tests in 0.005s — OK
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff (human operator)
- Attestation: attest completed
- Date: 2026-03-30

---

**Brief Status:** Completed

**Date Completed:** 2026-03-30

**Evidence Hash:** -
