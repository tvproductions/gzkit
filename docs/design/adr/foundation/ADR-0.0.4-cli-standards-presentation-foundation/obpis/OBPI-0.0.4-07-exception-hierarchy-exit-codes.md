---
id: OBPI-0.0.4-07-exception-hierarchy-exit-codes
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 7
lane: heavy
status: Draft
---

# OBPI-0.0.4-07: Exception Hierarchy & Exit Codes

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #7 - "Exception hierarchy & exit codes"

**Status:** Draft

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

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (especially OBPI-01, OBPI-02, OBPI-06)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01 (cli/ package structure) - must be complete
- [ ] OBPI-0.0.4-06 (OutputFormatter for `emit_error`) - must be complete or in progress
- [ ] `src/gzkit/cli/helpers/exit_codes.py` exists (from OBPI-02)

**Existing Code (understand current state):**

- [ ] Current error handling: `src/gzkit/core/errors.py` or equivalent
- [ ] Reference implementation: airlineops `src/airlineops/cli/helpers/exit_codes.py`
- [ ] CLI Standards v3: `docs/design/cli-standards-v3.md`
- [ ] Test patterns: `tests/unit/test_exception_hierarchy.py` (to be created)

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] **REQ-0.0.4-07-01:** Exception hierarchy exists with typed exit codes (`GzkitError` base, `ValidationError`, `ResourceNotFoundError`, `SystemError`, `PolicyBreachError`)
- [ ] **REQ-0.0.4-07-02:** `exit_code_for()` mapping function exists in `src/gzkit/cli/helpers/exit_codes.py`
- [ ] **REQ-0.0.4-07-03:** All command handlers use the CLI boundary pattern (try/except GzkitError + except Exception at boundary only)
- [ ] **REQ-0.0.4-07-04:** `--debug` flag enables tracebacks on unexpected errors (stderr)
- [ ] **REQ-0.0.4-07-05:** No bare `except Exception:` outside CLI boundary
- [ ] **REQ-0.0.4-07-06:** Exit codes documented in all epilogs (via OBPI-05 integration)
- [ ] **REQ-0.0.4-07-07:** Unit tests for exception hierarchy and exit code mapping pass
- [ ] **REQ-0.0.4-07-08:** `uv run gz lint` passes
- [ ] **REQ-0.0.4-07-09:** `uv run gz test` passes

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
