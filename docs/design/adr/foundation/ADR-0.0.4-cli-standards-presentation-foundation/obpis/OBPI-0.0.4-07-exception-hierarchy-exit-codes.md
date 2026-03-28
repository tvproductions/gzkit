---
id: OBPI-0.0.4-07-exception-hierarchy-exit-codes
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 7
lane: heavy
status: Completed
---

# OBPI-0.0.4-07: Exception Hierarchy & Exit Codes

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #7 - "Exception hierarchy & exit codes"

**Status:** Completed

## Objective

Replace the single `GzCliError` catch-all with a typed exception hierarchy that maps to
well-defined exit codes, with a standardized CLI boundary pattern on every handler.

## Lane

**heavy** - Changes CLI error handling and exit codes, which are external contract surfaces
visible to operators and scripts that depend on exit code semantics.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/helpers/exit_codes.py`
- `src/gzkit/core/exceptions.py`
- `src/gzkit/cli/commands/`
- `tests/`

## Denied Paths

- Retryability-oriented hierarchy (ADR-0.0.3 scope)
- Domain-specific error codes beyond the standard 0-3 map

## Requirements (FAIL-CLOSED)

1. Exception classes MUST be importable from the core layer (`src/gzkit/core/exceptions.py`) with NEVER any CLI dependencies.
2. The base exception `GzkitError` MUST define `exit_code = 1`; subclasses MUST override only where the standard 4-code map requires it (`SystemError` = 2, `PolicyBreachError` = 3).
3. An `exit_code_for(exc: Exception) -> int` mapping function MUST exist in `src/gzkit/cli/helpers/exit_codes.py`.
4. Every command handler MUST use the CLI boundary pattern: catch `GzkitError` via `exit_code_for`, catch bare `Exception` only at the CLI boundary, and NEVER allow raw tracebacks to reach the user unless `--debug` is active.
5. Raw tracebacks MUST NEVER reach the operator unless the `--debug` flag is active.
6. Bare `except Exception:` MUST NEVER appear outside the CLI boundary layer.
7. Backward compatibility MUST be preserved: commands that currently exit with specific codes MUST continue to do so.
8. The `--debug` flag MUST enable full tracebacks on unexpected errors (printed to stderr).
9. Exit codes MUST be documented in all command epilogs (integration with OBPI-05).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [x] Related OBPIs in same ADR (especially OBPI-01, OBPI-02, OBPI-06)

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-0.0.4-01 (cli/ package structure) - must be complete
- [x] OBPI-0.0.4-06 (OutputFormatter for `emit_error`) - must be complete or in progress
- [x] `src/gzkit/cli/helpers/exit_codes.py` exists (from OBPI-02)

**Existing Code (understand current state):**

- [x] Current error handling: `src/gzkit/core/exceptions.py`
- [x] Reference implementation: airlineops `src/airlineops/cli/helpers/exit_codes.py`
- [x] CLI Standards v3: `docs/design/cli-standards-v3.md`
- [x] Test patterns: `tests/unit/test_exception_hierarchy.py` (created)

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.unit.test_exception_hierarchy -v
uv run -m unittest tests.unit.test_exit_codes -v
```

## Acceptance Criteria

- [x] **REQ-0.0.4-07-01:** Exception hierarchy exists with typed exit codes (`GzkitError` base, `ValidationError`, `ResourceNotFoundError`, `TransientError`, `PolicyBreachError`)
- [x] **REQ-0.0.4-07-02:** `exit_code_for()` mapping function exists in `src/gzkit/cli/helpers/exit_codes.py`
- [x] **REQ-0.0.4-07-03:** All command handlers use the CLI boundary pattern (try/except GzkitError + except Exception at boundary only)
- [x] **REQ-0.0.4-07-04:** `--debug` flag enables tracebacks on unexpected errors (stderr)
- [x] **REQ-0.0.4-07-05:** [doc] No bare `except Exception:` outside CLI boundary
- [x] **REQ-0.0.4-07-06:** [doc] Exit codes documented in all epilogs (via OBPI-05 integration)
- [x] **REQ-0.0.4-07-07:** Unit tests for exception hierarchy and exit code mapping pass
- [x] **REQ-0.0.4-07-08:** [doc] `uv run gz lint` passes
- [x] **REQ-0.0.4-07-09:** [doc] `uv run gz test` passes

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

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 27 tests in 0.004s — OK
Coverage: 100% (exceptions.py + exit_codes.py)
```

### Code Quality

```text
uv run gz lint — All checks passed!
uv run gz typecheck — All checks passed!
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.92 seconds
```

### Gate 4 (BDD)

```text
uv run -m behave features/ — 3 features, 35 scenarios, 164 steps passed
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-25
```

### Value Narrative

Before this OBPI, gzkit had a single `GzCliError` catch-all exception — every error returned exit code 2 regardless of whether it was a user mistake, a system failure, or a policy breach. The CLI boundary lacked structured error handling and `--debug` re-raised raw exceptions to stdout. Now gzkit has a typed exception hierarchy (`GzkitError` base with `ValidationError`, `ResourceNotFoundError`, `TransientError`, `PolicyBreachError`) that maps to the standard 4-code exit map, with a proper CLI boundary pattern and stderr-directed debug tracebacks.

### Key Proof

```bash
$ uv run -m unittest tests.unit.test_exit_codes.TestCliBoundaryPattern -v
test_debug_flag_prints_traceback_to_stderr ... ok
test_main_catches_bare_exception_at_boundary ... ok
test_main_catches_gzkit_error ... ok
test_main_catches_policy_breach_with_code_3 ... ok
test_main_catches_transient_error_with_code_2 ... ok
----------------------------------------------------------------------
Ran 5 tests in 0.003s — OK
```

### Implementation Summary

- Files created/modified:
  - Created: `tests/unit/test_exception_hierarchy.py`, `tests/unit/test_exit_codes.py`
  - Modified: `src/gzkit/core/exceptions.py`, `src/gzkit/cli/helpers/exit_codes.py`, `src/gzkit/commands/common.py`, `src/gzkit/cli/main.py`
- Tests added: 27
- Date completed: 2026-03-25
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeff`
- Attestation: `attest completed`
- Date: `2026-03-25`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-25

**Evidence Hash:** -
