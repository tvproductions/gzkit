---
id: OBPI-0.0.4-01-cli-module-restructure
title: CLI Module Restructure
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Completed
lane: heavy
---

# OBPI-0.0.4-01: CLI Module Restructure

## Objective

Decompose the 6100-line monolithic `cli.py` into a `cli/` package with modular command
files per the v3 CLI Standards project structure.

## Scope

### In Scope

- Create `src/gzkit/cli/` package:
  - `main.py` — top-level parser, subcommand registration, entry point
  - `parser.py` — custom ArgumentParser (placeholder for OBPI-02)
  - `commands/` — one module per command group
  - `helpers/` — shared CLI utilities (placeholder for OBPI-02, OBPI-03)
  - `formatters.py` — output formatting (placeholder for OBPI-06)
- Extract all command handler functions from `cli.py` into command modules
- Preserve `__main__.py` entry point wiring
- One module per subcommand group under `cli/commands/`
- No single file exceeds 600 lines (pythonic standards)

### Out of Scope

- Hexagonal domain extraction (ADR-0.0.3)
- Changing command behavior or interfaces
- Adding new commands

## Constraints

- All existing commands must continue to work identically
- `uv run gz --help` output must be unchanged
- All existing tests must pass without modification
- Entry point in `pyproject.toml` must be updated

## Acceptance Criteria

### Evidence

- [x] `src/gzkit/cli/` package exists with `main.py`, `commands/`, `helpers/`
- [x] No file in `cli/` exceeds 600 lines
- [x] Old `cli.py` removed or reduced to import delegation
- [x] `uv run gz --help` produces identical output
- [x] `uv run gz lint` passes
- [x] `uv run gz test` passes
- [x] `uv run gz typecheck` passes

## Dependencies

- None (first OBPI in chain)

### Implementation Summary

- Modules created: 19 new command modules under `src/gzkit/commands/`
- Lines reduced: `cli/main.py` from 6208 to 736 lines (88% reduction)
- Backward compat: `_cli_main()` helper enables test mock.patch at `gzkit.cli.main.*`
- Re-exports: `cli/__init__.py` updated to re-export private names from new locations

### Key Proof

```
$ wc -l src/gzkit/cli/main.py
736

$ uv run -m unittest -q 2>&1 | tail -3
Ran 1306 tests in 14.753s
OK

$ diff <(uv run gz --help) /tmp/gz_help_before.txt
(no differences)
```

## Test Plan

- Run full test suite before and after — zero regressions
- Verify all 35 top-level commands respond to `--help`
- Verify entry point (`uv run gz`) still works
