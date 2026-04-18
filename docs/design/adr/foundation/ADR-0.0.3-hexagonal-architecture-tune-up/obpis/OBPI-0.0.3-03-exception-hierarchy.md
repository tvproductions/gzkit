---
id: OBPI-0.0.3-03-exception-hierarchy
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 3
lane: Heavy
status: in_progress
---

# OBPI-0.0.3-03-exception-hierarchy: Exception Hierarchy & Exit Codes

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #3 - "OBPI-0.0.3-03: Exception Hierarchy & Exit Codes"

**Status:** Draft

## Objective

Create `src/gzkit/core/exceptions.py` with a retryability-oriented domain exception hierarchy (GzError, TransientError, PermanentError, OperatorError, PolicyError) and a deterministic exit code mapping (0/1/2/3).

## Lane

**Heavy** — Defines a public exception contract and exit code schema that CLI and adapters depend on.

## Allowed Paths

- `src/gzkit/core/exceptions.py` — Exception hierarchy definition
- `src/gzkit/core/__init__.py` — Re-export exception classes
- `tests/test_core_exceptions.py` — Unit tests for exception hierarchy
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-03-exception-hierarchy.md` — This brief

## Denied Paths

- `src/gzkit/cli.py` — Wiring exceptions into CLI is future work
- `src/gzkit/commands/**` — Command error handling migration is future work
- `src/gzkit/adapters/` — Adapter exception translation is future work
- `docs/design/**` — ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `GzError` is the base exception for all gzkit domain errors
2. REQUIREMENT: `TransientError(GzError)` represents retryable failures (network, temp I/O) → exit code 2
3. REQUIREMENT: `PermanentError(GzError)` represents non-retryable failures (data corruption, schema mismatch) → exit code 1
4. REQUIREMENT: `OperatorError(GzError)` represents human-action-needed failures (config, permissions) → exit code 1
5. REQUIREMENT: `PolicyError(GzError)` represents governance policy breaches → exit code 3
6. REQUIREMENT: Each exception class has an `exit_code` property returning its mapped integer
7. REQUIREMENT: Exit code mapping matches the ADR's Standard 4-Code Map (0=success, 1=user/config, 2=system/IO, 3=policy)
8. NEVER: Use bare `except:` or `except Exception:` — always catch specific exception types
9. NEVER: Define exceptions outside `core/exceptions.py` — this is the single source
10. ALWAYS: Exception classes are importable via `from gzkit.core.exceptions import GzError`

> STOP-on-BLOCKERS: if `src/gzkit/core/__init__.py` does not exist (OBPI-01), halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/core/__init__.py` exists (OBPI-01 completed)

**Context:**

- [ ] Parent ADR — Exit code mapping table and exception hierarchy design
- [ ] `.claude/rules/cli.md` — Exit code contract (Standard 4-Code Map)
- [ ] `.claude/rules/pythonic.md` — Exception handling conventions

**Existing Code:**

- [ ] Grep for existing exception patterns in `src/gzkit/` to understand current ad-hoc error handling

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify each exception class exists and has correct `exit_code`
- [ ] Tests verify inheritance hierarchy
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Exception hierarchy is internal contract, no CLI surface change yet

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from gzkit.core.exceptions import GzError, TransientError, PermanentError, OperatorError, PolicyError; print('All exceptions importable')"
python -c "from gzkit.core.exceptions import TransientError; assert TransientError('x').exit_code == 2"
python -c "from gzkit.core.exceptions import PolicyError; assert PolicyError('x').exit_code == 3"
uv run -m unittest tests.test_core_exceptions -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-03-01: `GzError` base exception exists in `core/exceptions.py`
- [x] REQ-0.0.3-03-02: `TransientError` has `exit_code == 2`
- [x] REQ-0.0.3-03-03: `PermanentError` has `exit_code == 1`
- [x] REQ-0.0.3-03-04: `OperatorError` has `exit_code == 1`
- [x] REQ-0.0.3-03-05: `PolicyError` has `exit_code == 3`
- [x] REQ-0.0.3-03-06: All exception classes inherit from `GzError`
- [x] REQ-0.0.3-03-07: Exception classes are importable via `gzkit.core.exceptions`
- [x] REQ-0.0.3-03-08: Unit tests verify hierarchy and exit code mapping

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_core_exceptions -v
Ran 15 tests in 0.000s — OK
Tests cover: hierarchy, exit codes, usability, import paths
$ uv run gz test — 1127 tests pass
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — Documentation built successfully
```

### Gate 4 (BDD)

```text
N/A — No CLI surface changes yet
```

### Gate 5 (Human)

```text
Attestor: human (operator)
Attestation: "attest completed"
Date: 2026-03-23
```

### Value Narrative

Before this OBPI, gzkit had no unified exception hierarchy — errors were ad-hoc with no
retryability classification or deterministic exit code mapping. Now, five domain exception
classes exist with a clear inheritance hierarchy and exit codes matching the ADR Standard
4-Code Map (0/1/2/3), enabling CLI commands to return consistent exit codes.

### Key Proof

```text
$ uv run python -c "from gzkit.core.exceptions import TransientError; assert TransientError('x').exit_code == 2"
$ uv run python -c "from gzkit.core.exceptions import PolicyError; assert PolicyError('x').exit_code == 3"
```

### Implementation Summary

- Files created/modified: src/gzkit/core/exceptions.py, tests/test_core_exceptions.py
- Tests added: tests/test_core_exceptions.py (15 tests)
- Date completed: 2026-03-23
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-23

---

**Brief Status:** Completed

**Date Completed:** 2026-03-23

**Evidence Hash:** -
