---
id: OBPI-0.0.4-10-cli-consistency-tests
title: CLI Consistency Tests
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-10: CLI Consistency Tests

## Objective

Create policy tests that enforce CLI conventions automatically, preventing regressions
when new commands are added. Modeled on airlineops `test_cli_consistency.py`.

## Scope

### In Scope

- `tests/policy/test_cli_consistency.py`:
  - **Recursive parser auditor**: Walk the full argparse parser tree, collect all commands, options, and help text
  - **No underscore flags**: All `--` options use hyphens (`--dry-run`, not `--dry_run`)
  - **Descriptions required**: Every parser (command and subcommand) has `.description` set
  - **Help text required**: Every argument/option has `.help` set (not None, not SUPPRESS)
  - **Epilog required**: Every parser has non-empty `.epilog`
  - **Epilog structure**: Every epilog contains "Examples" and "Exit codes" substrings
  - **No debugging artifacts**: No `TODO`, `FIXME`, `XXX`, `print(`, `pdb.set_trace` in help text
  - **Help rendering performance**: Full `--help` renders in <1s

- `tests/policy/test_import_boundaries.py` (CLI-specific):
  - Command modules do not import from `core/` adapters directly
  - No `os.getenv()` in command handlers (outside narrow allowlist: `NO_COLOR`, `FORCE_COLOR`)

- Test utilities:
  - `flatten_ws(value) -> str` — normalize whitespace for robust help text assertions
  - Recursive `_audit_parser(parser, path="")` returning structured audit data

### Out of Scope

- Domain import boundary tests (ADR-0.0.3 scope)
- Runtime output snapshot tests (OBPI-08)

## Constraints

- Policy tests scan source code — they do not import or execute application code
- Policy tests use `ast` for structural analysis and string matching for patterns
- Clear error messages that explain what boundary was violated and where
- Allowlists for expected exceptions must be explicit and minimal

## Acceptance Criteria

### Evidence

- [ ] `tests/policy/test_cli_consistency.py` exists with all checks listed above
- [ ] All tests pass: `uv run -m unittest tests.policy.test_cli_consistency -v`
- [ ] Adding a new command without help text causes test failure
- [ ] Adding a `--dry_run` flag (underscore) causes test failure
- [ ] Adding a command without epilog causes test failure
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-04 (all help text in place)
- OBPI-0.0.4-05 (all epilogs in place)
- All prior OBPIs (tests validate the complete state)

## Test Plan

- The tests ARE the test plan — they validate all prior OBPI deliverables
- Manually verify a regression is caught by temporarily breaking a convention

## Reference Implementation

Adapted from `/Users/jeff/Documents/Code/airlineops/tests/cli/test_cli_consistency.py`
