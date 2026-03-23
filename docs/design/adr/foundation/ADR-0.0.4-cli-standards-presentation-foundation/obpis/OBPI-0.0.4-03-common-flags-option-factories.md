---
id: OBPI-0.0.4-03
title: Common Flags & Standard Option Factories
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-03: Common Flags & Standard Option Factories

## Objective

Create reusable flag registration functions that enforce consistent naming, help text,
and behavior across all commands. Eliminate ad-hoc argument definitions.

## Scope

### In Scope

- `src/gzkit/cli/helpers/common_flags.py`:
  - `add_common_flags(parser, *, include_help=True)` — registers:
    - `--quiet` / `-q` (mutually exclusive with `--verbose`)
    - `--verbose` / `-v`
    - `--debug` (full tracebacks, DEBUG-level logging)
  - Apply to all existing commands

- `src/gzkit/cli/helpers/standard_options.py`:
  - `add_adr_option(parser, *, required=False, help_override=None)` — `--adr` with canonical help
  - `add_json_option(parser, *, help_override=None)` — `--json` with canonical help
  - `add_dry_run_option(parser, *, help_override=None)` — `--dry-run` with canonical help
  - `add_force_option(parser, *, help_override=None)` — `--force` with canonical help
  - `add_table_option(parser, *, help_override=None)` — `--table` with canonical help
  - Each factory has canonical default help text and accepts `help_override`

- Replace all existing ad-hoc `--json`, `--adr`, `--dry-run`, `--force` definitions with factory calls

### Out of Scope

- `--skill` flag (opsdev-specific, may be added later)
- Command-specific arguments (those stay in command modules)

## Constraints

- Mutually exclusive group for `--quiet` and `--verbose`
- Factory functions must prevent duplicate option registration
- Canonical help text wording consistent with airlineops conventions

## Acceptance Criteria

### Evidence

- [ ] `add_common_flags()` exists and is called on all commands
- [ ] `--quiet`, `--verbose`, `--debug` accepted by every command
- [ ] All `--json`, `--adr`, `--dry-run`, `--force` use factory functions
- [ ] Help text from factories matches canonical wording
- [ ] No duplicate option errors
- [ ] Unit tests for each factory function
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure)
- OBPI-0.0.4-02 (parser infrastructure)

## Test Plan

- Test each factory produces correct option strings and help text
- Test mutually exclusive `--quiet`/`--verbose` behavior
- Test `help_override` parameter
- Test no duplicate option errors when factories are called
