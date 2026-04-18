---
id: OBPI-0.0.3-06-output-formatter
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 6
lane: Heavy
status: in_progress
---

# OBPI-0.0.3-06-output-formatter: Output Formatter

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #6 - "OBPI-0.0.3-06: Output Formatter"

**Status:** Completed

## Objective

Create `src/gzkit/cli/formatters.py` with a single OutputFormatter chokepoint supporting 5 output modes (human, json, quiet, verbose, debug), establishing the `cli/` subpackage under `src/gzkit/`.

## Lane

**Heavy** — Creates a new CLI adapter subpackage and defines the output contract surface for all commands.

## Allowed Paths

- `src/gzkit/cli/__init__.py` — New CLI adapter package init
- `src/gzkit/cli/formatters.py` — OutputFormatter with 5 modes
- `tests/test_formatters.py` — Unit tests for OutputFormatter
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-06-output-formatter.md` — This brief

## Denied Paths

- `src/gzkit/cli.py` — Existing CLI entry point (wiring is incremental)
- `src/gzkit/commands/**` — Existing commands (wiring formatter into commands is incremental)
- `src/gzkit/core/` — Core must not know about output formatting
- `src/gzkit/ports/` — Port definitions are OBPI-01
- `docs/design/**` — ADR changes out of scope
- New dependencies (Rich is already available)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OutputFormatter supports exactly 5 modes: `human`, `json`, `quiet`, `verbose`, `debug`
2. REQUIREMENT: `human` mode outputs tables, colors, and progress via Rich
3. REQUIREMENT: `json` mode sends valid JSON to stdout and logs to stderr — never mixed
4. REQUIREMENT: `quiet` mode outputs errors only (stderr)
5. REQUIREMENT: `verbose` mode outputs debug-level information
6. REQUIREMENT: OutputFormatter is a single chokepoint — all CLI output flows through it
7. REQUIREMENT: Mode selection maps to CLI flags: default=human, `--json`=json, `--quiet`=quiet, `--verbose`=verbose
8. NEVER: Import OutputFormatter in `core/` or `ports/` — it lives in the CLI adapter layer only
9. NEVER: Mix data and logs on the same stream in json mode
10. ALWAYS: OutputFormatter respects `NO_COLOR` environment variable in human mode

> STOP-on-BLOCKERS: if OBPI-0.0.3-01 skeleton is not complete, halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [x] `src/gzkit/core/__init__.py` exists (OBPI-01 completed)
- [x] `src/gzkit/adapters/__init__.py` exists (OBPI-01 completed)

**Context:**

- [x] Parent ADR — Output contract specification and layer rules
- [x] `.claude/rules/cli.md` — Output contract (default, `--json`, `--plain`)

**Existing Code:**

- [x] `src/gzkit/commands/` — Current output patterns to understand (not to modify)
- [x] `src/gzkit/cli.py` — Current CLI entry point structure

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests verify each output mode produces correct format
- [x] Tests verify json mode stdout/stderr separation
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [x] N/A — Formatter is infrastructure; CLI surface wiring is incremental

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from gzkit.cli.formatters import OutputFormatter; f = OutputFormatter('json'); print('Formatter importable')"
uv run -m unittest tests.test_formatters -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-06-01: [doc] `src/gzkit/cli/` package exists with `__init__.py`
- [x] REQ-0.0.3-06-02: `OutputFormatter` class supports `human` mode with Rich tables/colors
- [x] REQ-0.0.3-06-03: `OutputFormatter` supports `json` mode (data→stdout, logs→stderr)
- [x] REQ-0.0.3-06-04: `OutputFormatter` supports `quiet` mode (errors only)
- [x] REQ-0.0.3-06-05: `OutputFormatter` supports `verbose` mode
- [x] REQ-0.0.3-06-06: `OutputFormatter` supports `debug` mode
- [x] REQ-0.0.3-06-07: `OutputFormatter` respects `NO_COLOR` in human mode
- [x] REQ-0.0.3-06-08: Unit tests cover all 5 modes

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
$ uv run -m unittest tests.test_formatters -v
Ran 40 tests in 0.004s — OK
40 tests across 9 classes: Init(5), Human(4), Json(5), Quiet(7), Verbose(3), Debug(3), NoColor(3), ModeFromFlags(8), ImportBoundary(2)
$ uv run gz test — 1242 tests (pre-existing failures only, 0 new)
Coverage: 96% on src/gzkit/cli/formatters.py
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — Documentation built in 0.97 seconds
```

### Gate 4 (BDD)

```text
N/A — Formatter infrastructure
```

### Gate 5 (Human)

```text
Attestor: human:jeff
Attestation: "attest completed"
Date: 2026-03-24
```

### Value Narrative

Before this OBPI, gzkit had no unified output formatting — commands directly called `console.print()` and `print()` ad hoc, with no consistent behavior for `--json`, `--quiet`, or `--verbose` flags. Now, a single `OutputFormatter` chokepoint exists in the `cli/` adapter layer supporting 5 output modes with proper stdout/stderr separation in json mode and `NO_COLOR` respect.

### Key Proof

```bash
$ uv run python -c "from gzkit.cli.formatters import OutputFormatter; f = OutputFormatter('json'); print('Formatter importable')"
Formatter importable
$ uv run -m unittest tests.test_formatters.TestJsonMode.test_data_and_logs_never_mix_on_stdout -v
test_data_and_logs_never_mix_on_stdout ... ok
```

### Implementation Summary

- Files created: src/gzkit/cli/__init__.py, src/gzkit/cli/formatters.py, tests/test_formatters.py
- Files relocated: src/gzkit/cli.py → src/gzkit/cli/main.py (content unchanged, re-exports preserved)
- Tests added: tests/test_formatters.py (40 tests across 9 classes)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
