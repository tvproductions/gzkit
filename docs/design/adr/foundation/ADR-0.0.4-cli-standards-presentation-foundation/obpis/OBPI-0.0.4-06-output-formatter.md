---
id: OBPI-0.0.4-06
title: OutputFormatter
parent: ADR-0.0.4-cli-standards-presentation-foundation
status: Pending
lane: heavy
---

# OBPI-0.0.4-06: OutputFormatter

## Objective

Create a single output chokepoint that replaces all direct `console.print()` and bare
`print()` calls in command handlers. Supports 5 output modes per v3 specification.

## Scope

### In Scope

- `src/gzkit/cli/formatters.py`:
  - `OutputMode` enum: `HUMAN`, `JSON`, `QUIET`, `VERBOSE`, `DEBUG`
  - `OutputFormatter` class:
    - `__init__(self, mode: OutputMode, console: Console)`
    - `emit(self, data: dict | list | str | BaseModel)` — routes to appropriate renderer
    - `emit_error(self, message: str)` — always to stderr
    - `emit_table(self, table: Table)` — Rich table in human mode, dict list in JSON mode
    - `emit_status(self, label: str, success: bool)` — renders `✓`/`❌` in human, key-value in JSON
    - `emit_blocker(self, message: str)` — `BLOCKERS:` prefix to stderr
  - Mode selection from common flags (`--quiet`, `--verbose`, `--debug`, `--json`)
  - Respects `NO_COLOR` environment variable
  - JSON mode: `model_dump_json()` for Pydantic models, `json.dumps(sort_keys=True)` for dicts
  - Quiet mode: suppresses all non-error output
  - Human mode: Rich console rendering

- Migrate all existing command handlers to use `OutputFormatter`
- Remove all direct `console.print()` and bare `print()` from command code

### Out of Scope

- structlog integration (ADR-0.0.3)
- Progress bars (OBPI-09)

## Constraints

- Formatter lives in CLI layer (not a port — it knows about Rich)
- JSON output must be valid JSON to stdout with no Rich markup
- Errors always go to stderr regardless of mode
- Must handle Pydantic BaseModel instances natively
- Deterministic JSON output (sorted keys, indent=2)

## Acceptance Criteria

### Evidence

- [ ] `OutputFormatter` class exists with all 5 modes
- [ ] No direct `console.print()` in command handler code
- [ ] No bare `print()` for user-facing output in command code
- [ ] JSON mode produces valid JSON to stdout
- [ ] Quiet mode suppresses all non-error output
- [ ] `emit_status()` renders `✓`/`❌` in human mode
- [ ] `emit_blocker()` writes `BLOCKERS:` to stderr
- [ ] Unit tests for each output mode
- [ ] `uv run gz lint` passes
- [ ] `uv run gz test` passes

## Dependencies

- OBPI-0.0.4-01 (cli/ package structure)
- OBPI-0.0.4-03 (common flags determine output mode)

## Test Plan

- Test each output mode renders correctly
- Test JSON output is valid JSON with sorted keys
- Test quiet mode suppresses stdout
- Test error output always goes to stderr
- Test Pydantic model serialization via emit()
- Capture stdout/stderr with io.StringIO for assertions
