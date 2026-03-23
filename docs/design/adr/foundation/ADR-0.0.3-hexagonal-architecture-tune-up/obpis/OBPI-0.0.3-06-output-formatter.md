---
id: OBPI-0.0.3-06-output-formatter
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.3-06-output-formatter: Output Formatter

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #6 - "OBPI-0.0.3-06: Output Formatter"

**Status:** Draft

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

- [ ] `src/gzkit/core/__init__.py` exists (OBPI-01 completed)
- [ ] `src/gzkit/adapters/__init__.py` exists (OBPI-01 completed)

**Context:**

- [ ] Parent ADR — Output contract specification and layer rules
- [ ] `.claude/rules/cli.md` — Output contract (default, `--json`, `--plain`)

**Existing Code:**

- [ ] `src/gzkit/commands/` — Current output patterns to understand (not to modify)
- [ ] `src/gzkit/cli.py` — Current CLI entry point structure

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify each output mode produces correct format
- [ ] Tests verify json mode stdout/stderr separation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Formatter is infrastructure; CLI surface wiring is incremental

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.3-06-01: `src/gzkit/cli/` package exists with `__init__.py`
- [ ] REQ-0.0.3-06-02: `OutputFormatter` class supports `human` mode with Rich tables/colors
- [ ] REQ-0.0.3-06-03: `OutputFormatter` supports `json` mode (data→stdout, logs→stderr)
- [ ] REQ-0.0.3-06-04: `OutputFormatter` supports `quiet` mode (errors only)
- [ ] REQ-0.0.3-06-05: `OutputFormatter` supports `verbose` mode
- [ ] REQ-0.0.3-06-06: `OutputFormatter` supports `debug` mode
- [ ] REQ-0.0.3-06-07: `OutputFormatter` respects `NO_COLOR` in human mode
- [ ] REQ-0.0.3-06-08: Unit tests cover all 5 modes

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
N/A — Formatter infrastructure
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
