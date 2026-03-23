---
id: OBPI-0.0.4-07
title: Exception Hierarchy & Exit Codes
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-07: Exception Hierarchy & Exit Codes

## Objective

Replace the single `GzCliError` catch-all with a typed exception hierarchy that maps to
well-defined exit codes, with a standardized CLI boundary pattern on every handler.

## Scope

### In Scope

- `src/gzkit/cli/helpers/exit_codes.py` (extend from OBPI-02):
  - Exit code constants with docstrings
  - `exit_code_for(exc: Exception) -> int` mapping function

- `src/gzkit/core/exceptions.py` (or extend existing error module):
  - `GzkitError` — base for all domain errors, `exit_code = 1`
  - `ValidationError` — input/config validation failures, `exit_code = 1`
  - `ResourceNotFoundError` — missing ADR, OBPI, config, `exit_code = 1`
  - `SystemError` — I/O, network, subprocess failures, `exit_code = 2`
  - `PolicyBreachError` — governance violations, partial success, `exit_code = 3`

- CLI boundary pattern applied to every command handler:
  ```python
  def handle_command(args, formatter):
      try:
          result = do_work(args)
          formatter.emit(result)
          return 0
      except GzkitError as e:
          formatter.emit_error(str(e))
          return exit_code_for(e)
      except Exception:
          if args.debug:
              traceback.print_exc(file=sys.stderr)
          formatter.emit_error("An unexpected error occurred.")
          return 1
  ```

- Remove bare `except Exception:` outside CLI boundary
- `--debug` flag enables full tracebacks on unexpected errors

### Out of Scope

- Retryability-oriented hierarchy (ADR-0.0.3 scope)
- Domain-specific error codes beyond 0-3

## Constraints

- Preserve backward compatibility: commands that currently exit 2 on GzCliError continue to do so
- Exception classes must be importable from core layer (no CLI dependencies)
- Raw tracebacks never reach user unless `--debug` active

## Acceptance Criteria

### Evidence

- [ ] Exception hierarchy exists with typed exit codes
- [ ] `exit_code_for()` mapping function exists
- [ ] All command handlers use CLI boundary pattern
- [ ] `--debug` enables tracebacks on unexpected errors
- [ ] No bare `except Exception:` outside CLI boundary
- [ ] Exit codes documented in all epilogs (via OBPI-05)
- [ ] Unit tests for exception hierarchy and exit code mapping
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure)
- OBPI-0.0.4-06 (OutputFormatter for emit_error)

## Test Plan

- Test each exception type maps to correct exit code
- Test CLI boundary catches domain errors and returns correct code
- Test `--debug` enables tracebacks
- Test unexpected exceptions return exit code 1
