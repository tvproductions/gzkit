---
id: OBPI-0.0.8-02-flag-service
parent: ADR-0.0.8-feature-toggle-system
item: 2
lane: Heavy
status: Pending
---

# OBPI-0.0.8-02: Flag Service

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #3 — "Precedence resolution" and #4 — "Unknown/malformed flag detection"

**Status:** Pending

## Objective

Implement the FlagService (toggle router): the singleton that loads the
registry, resolves flag values through the five-layer precedence chain
(registry default → env var → project config → test override → runtime
override), and provides the override API for testing and development.

## Lane

**Heavy** — New API surface (`FlagService`) consumed by all downstream
OBPIs. Environment variable contract (`GZKIT_FLAG_<KEY>`) and `.gzkit.json`
`flags` section are operator-facing.

## Dependencies

- **Upstream:** OBPI-01 (FlagSpec, FlagCategory, registry loader, errors).
- **Downstream:** OBPI-03 (FeatureDecisions), OBPI-04 (diagnostics), OBPI-05 (CLI).

## Allowed Paths

- `src/gzkit/flags/service.py` — FlagService implementation
- `src/gzkit/flags/__init__.py` — Public API updates (get_flag_service)
- `tests/test_flag_service.py` — Service unit tests

## Denied Paths

- `src/gzkit/flags/models.py` — Read-only; belongs to OBPI-01
- `src/gzkit/flags/decisions.py` — Belongs to OBPI-03
- `src/gzkit/commands/` — CLI belongs to OBPI-05
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: FlagService MUST load the registry via OBPI-01's registry loader at construction.
1. REQUIREMENT: `is_enabled(key)` MUST resolve through the five-layer precedence chain in order: registry default, env var, project config, test override, runtime override.
1. REQUIREMENT: `is_enabled(key)` for an unknown key MUST raise UnknownFlagError.
1. REQUIREMENT: Env vars MUST follow the naming convention `GZKIT_FLAG_<KEY>` where dots are replaced with underscores and the result is uppercased (e.g., `ops.product_proof` → `GZKIT_FLAG_OPS_PRODUCT_PROOF`).
1. REQUIREMENT: Env var values MUST be parsed as boolean: `true`/`1`/`yes` → True, `false`/`0`/`no` → False. All other values MUST raise InvalidFlagValueError.
1. REQUIREMENT: Project config overrides MUST be read from the `.gzkit.json` `flags` section as `{"flag.key": bool}`.
1. REQUIREMENT: `set_test_override(key, value)` and `clear_test_overrides()` MUST be provided for unittest isolation.
1. REQUIREMENT: `set_runtime_override(key, value)` MUST be provided for development debugging.
1. REQUIREMENT: `evaluate(key)` MUST return a FlagEvaluation with the resolved value and the source layer that provided it.
1. REQUIREMENT: `list_flags()` MUST return all registered flags with current resolved values and sources.
1. NEVER: Cache env vars or config beyond construction — re-read on each `is_enabled` call for test isolation.
1. ALWAYS: Validate key existence before any lookup.

> STOP-on-BLOCKERS: OBPI-01 must be complete (models and registry loader available).

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist items #3 and #4 referenced

### Gate 2: TDD

- [ ] Unit tests validate precedence: registry default wins when no overrides
- [ ] Unit tests validate precedence: env var overrides registry default
- [ ] Unit tests validate precedence: project config overrides env var
- [ ] Unit tests validate precedence: test override overrides project config
- [ ] Unit tests validate precedence: runtime override overrides test override
- [ ] Unit tests validate UnknownFlagError for undeclared keys
- [ ] Unit tests validate InvalidFlagValueError for malformed env values
- [ ] Unit tests validate env var naming convention
- [ ] Unit tests validate test override set/clear cycle
- [ ] Unit tests validate FlagEvaluation source attribution
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Module docstring in service.py

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.0.8-02-01: Given a flag `ops.product_proof` with registry default `true` and no overrides, when `is_enabled("ops.product_proof")` is called, then it returns `True`.
- [ ] REQ-0.0.8-02-02: Given env var `GZKIT_FLAG_OPS_PRODUCT_PROOF=false`, when `is_enabled("ops.product_proof")` is called, then it returns `False` (env overrides registry).
- [ ] REQ-0.0.8-02-03: Given env var and project config both set, when `is_enabled` is called, then project config wins.
- [ ] REQ-0.0.8-02-04: Given `set_test_override("ops.product_proof", False)`, when `is_enabled` is called, then test override wins. After `clear_test_overrides()`, the prior resolution applies.
- [ ] REQ-0.0.8-02-05: Given `is_enabled("nonexistent.flag")`, when called, then UnknownFlagError is raised.
- [ ] REQ-0.0.8-02-06: Given env var `GZKIT_FLAG_OPS_PRODUCT_PROOF=maybe`, when FlagService resolves, then InvalidFlagValueError is raised.
- [ ] REQ-0.0.8-02-07: Given `evaluate("ops.product_proof")`, when called with env var set, then FlagEvaluation.source is `"env"`.

## Verification Commands

```bash
# Service tests
uv run -m unittest tests.test_flag_service -v

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck
```

## Evidence

### Implementation Summary

- Files created/modified: (to be filled on completion)
- Validation commands run: (to be filled on completion)
- Date completed: (to be filled on completion)

### Key Proof

(to be filled on completion)

---

**Brief Status:** Pending
