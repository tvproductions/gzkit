---
id: OBPI-0.0.8-07-config-gates-removal
parent: ADR-0.0.8-feature-toggle-system
item: 7
lane: Heavy
status: Pending
---

# OBPI-0.0.8-07: Config Gates Removal

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #10 — "config.gates removal and .gzkit.json migration"

**Status:** Pending

## Objective

Remove the `config.gates` prototype entirely. Migrate any operator `.gzkit.json`
files that use the `gates` key to the new `flags` key format. Clean up all
references to the old gates dict throughout the codebase.

## Lane

**Heavy** — Removes the `gates` key from `.gzkit.json`, which is an
operator-facing schema change. Any project with `gates` in their config will
need migration. This is a breaking change to the config contract.

## Dependencies

- **Upstream:** OBPI-06 (closeout migration must complete first — the last consumer of config.gates).
- **Downstream:** OBPI-08 (docs must document the migration).
- **Parallel:** None — sequential dependency on OBPI-06.

## Allowed Paths

- `src/gzkit/core/config.py` — Remove gates field from config model
- `src/gzkit/flags/service.py` — Remove any config.gates compatibility shim
- `data/schemas/gzkit.schema.json` — Remove gates from .gzkit.json schema (if present)
- `tests/test_config_gates_removal.py` — Migration and removal tests
- Any file with stale `config.gate(` or `config.gates` references

## Denied Paths

- `.gzkit/ledger.jsonl` — Never edit manually
- `src/gzkit/flags/decisions.py` — Read-only; belongs to OBPI-03

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The `gates` field MUST be removed from the config model in `core/config.py`.
1. REQUIREMENT: All `config.gate(` and `config.gates` references in the codebase MUST be removed or replaced.
1. REQUIREMENT: If the `.gzkit.json` schema includes `gates`, it MUST be removed.
1. REQUIREMENT: A grep for `config.gate` across the codebase MUST return zero matches outside of test/migration files.
1. REQUIREMENT: The `migration.config_gates_to_flags` flag itself MUST be set to `true` (migration complete) in the registry default, or removed if the migration is done in-band.
1. REQUIREMENT: Error messaging for operators who still have `gates` in `.gzkit.json`: config loading MUST produce a clear warning naming the replacement.
1. NEVER: Silently ignore a `gates` key in config — either migrate it or error.
1. ALWAYS: Test that config loads cleanly without the gates key.

> STOP-on-BLOCKERS: OBPI-06 must be complete (all config.gates consumers migrated to FeatureDecisions).

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #10 referenced

### Gate 2: TDD

- [ ] Unit tests validate config loads without gates field
- [ ] Unit tests validate config with stale gates key produces warning/error
- [ ] Unit tests validate no stale config.gate references in codebase
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Migration note in operator docs (delivered with OBPI-08)

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.0.8-07-01: Given a clean `.gzkit.json` without `gates`, when config loads, then no errors or warnings related to gates.
- [ ] REQ-0.0.8-07-02: Given a `.gzkit.json` with a `gates` key, when config loads, then a clear deprecation warning names the `flags` replacement.
- [ ] REQ-0.0.8-07-03: Given a grep for `config\.gate` across `src/gzkit/`, when run, then zero matches found.
- [ ] REQ-0.0.8-07-04: Given the full test suite, when run after removal, then all tests pass with no gate-related failures.

## Verification Commands

```bash
# Removal-specific tests
uv run -m unittest tests.test_config_gates_removal -v

# Verify complete removal of config.gates references
grep -rn "config\.gate" src/gzkit/ --include="*.py" | grep -v "__pycache__"
# Expected: zero matches

grep -rn "\"gates\"" src/gzkit/ --include="*.py" | grep -v "__pycache__" | grep -v "test_"
# Expected: zero matches (outside tests)

# Config loads cleanly
python -c "from gzkit.core.config import load_config; c = load_config(); print('OK')"

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
