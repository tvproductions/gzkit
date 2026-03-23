---
id: OBPI-0.0.3-02-domain-extraction
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.3-02-domain-extraction: Domain Extraction

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #2 - "OBPI-0.0.3-02: Domain Extraction"

**Status:** Draft

## Objective

Extract core business logic from existing flat modules into `src/gzkit/core/`, creating `core/models.py`, `core/lifecycle.py`, `core/scoring.py`, and `core/validation_rules.py` while maintaining backward-compatible re-exports from original module paths.

## Lane

**Heavy** — Moves domain logic into a new architectural layer with import boundary constraints.

## Allowed Paths

- `src/gzkit/core/__init__.py` — Core package exports
- `src/gzkit/core/models.py` — Domain models extracted from `models/`
- `src/gzkit/core/lifecycle.py` — ADR/OBPI state machines extracted from `lifecycle.py`
- `src/gzkit/core/scoring.py` — Scorecard computation extracted from `decomposition.py`
- `src/gzkit/core/validation_rules.py` — Pure validation logic extracted from `validate.py`
- `src/gzkit/lifecycle.py` — Thin re-export shim after extraction
- `src/gzkit/decomposition.py` — Thin re-export shim after extraction
- `src/gzkit/validate.py` — Thin re-export shim after extraction
- `src/gzkit/models/__init__.py` — Update exports to delegate to `core/models.py`
- `tests/test_core_lifecycle.py` — Unit tests for extracted lifecycle logic
- `tests/test_core_scoring.py` — Unit tests for extracted scoring logic
- `tests/test_core_validation.py` — Unit tests for extracted validation logic
- `tests/test_core_models.py` — Unit tests for extracted domain models
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-02-domain-extraction.md` — This brief

## Denied Paths

- `src/gzkit/ports/` — Port definitions are OBPI-01 (must already exist)
- `src/gzkit/adapters/` — Adapter implementations are later OBPIs
- `src/gzkit/core/exceptions.py` — Exception hierarchy is OBPI-03
- `src/gzkit/config.py` — Config refactor is OBPI-05
- `src/gzkit/cli.py` — CLI layer changes out of scope
- `src/gzkit/commands/**` — Command refactoring out of scope
- `docs/design/**` — ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `core/` imports only `ports/` (Protocols), `pydantic`, `structlog` (binding only), and stdlib
2. REQUIREMENT: `core/` NEVER imports from `cli/`, `commands/`, `adapters/`, `rich`, `argparse`
3. REQUIREMENT: Original modules (`lifecycle.py`, `decomposition.py`, `validate.py`) become thin re-export shims so downstream imports do not break
4. REQUIREMENT: All existing tests continue to pass after extraction without modification
5. REQUIREMENT: Extracted logic is pure domain — no I/O, no filesystem access, no subprocess calls
6. REQUIREMENT: Each extracted module has corresponding unit tests in `tests/`
7. NEVER: Remove original module files — they become re-export shims
8. NEVER: Change the public API of any existing function during extraction
9. ALWAYS: Core domain models use Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`
10. ALWAYS: Preserve all existing function signatures and return types

> STOP-on-BLOCKERS: if OBPI-0.0.3-01 skeleton is not complete, halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/ports/interfaces.py` exists (OBPI-01 completed)
- [ ] `src/gzkit/core/__init__.py` exists (OBPI-01 completed)

**Existing Code (understand current state):**

- [ ] `src/gzkit/lifecycle.py` — State machine logic to extract
- [ ] `src/gzkit/decomposition.py` — Scorecard computation to extract
- [ ] `src/gzkit/validate.py` — Validation rules to extract
- [ ] `src/gzkit/models/` — Domain models to extract
- [ ] `tests/test_lifecycle.py` — Existing lifecycle tests
- [ ] `tests/test_decomposition.py` — Existing decomposition tests
- [ ] `tests/test_validate.py` — Existing validation tests
- [ ] `tests/test_models.py` — Existing model tests

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Unit tests written for each extracted core module
- [ ] All existing tests continue to pass unchanged
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Internal refactoring, no CLI surface changes

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Verify re-exports work (downstream imports unchanged)
python -c "from gzkit.lifecycle import LifecycleState; print('re-export works')"
python -c "from gzkit.core.lifecycle import LifecycleState; print('core import works')"

# Verify core layer boundary
python -c "
import ast, pathlib
for f in pathlib.Path('src/gzkit/core').glob('*.py'):
    tree = ast.parse(f.read_text())
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            assert not any(n.module.startswith(p) for p in ('gzkit.cli', 'gzkit.commands', 'gzkit.adapters')), f'{f}: forbidden import {n.module}'
print('Core boundary clean')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.3-02-01: `src/gzkit/core/lifecycle.py` contains ADR/OBPI state machine logic
- [ ] REQ-0.0.3-02-02: `src/gzkit/core/scoring.py` contains scorecard computation logic
- [ ] REQ-0.0.3-02-03: `src/gzkit/core/validation_rules.py` contains pure validation logic
- [ ] REQ-0.0.3-02-04: `src/gzkit/core/models.py` contains domain models
- [ ] REQ-0.0.3-02-05: Original modules are thin re-export shims
- [ ] REQ-0.0.3-02-06: All existing tests pass without modification
- [ ] REQ-0.0.3-02-07: `core/` has no forbidden imports (cli, commands, adapters, rich, argparse)
- [ ] REQ-0.0.3-02-08: New unit tests cover extracted core modules

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
N/A — Internal refactoring
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:<name>` — required (parent ADR is Heavy, Foundation series)
- Attestation: substantive attestation text required
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
