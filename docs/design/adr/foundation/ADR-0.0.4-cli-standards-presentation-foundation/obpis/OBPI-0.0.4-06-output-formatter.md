---
id: OBPI-0.0.4-06-output-formatter
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.4-06: OutputFormatter

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #6 — "OutputFormatter as single chokepoint for all user-facing output (5 modes)"

**Status:** Draft

## Objective

Create a single output chokepoint that replaces all direct `console.print()` and bare
`print()` calls in command handlers. Supports 5 output modes (HUMAN, JSON, QUIET,
VERBOSE, DEBUG) per the v3 specification and routes all user-facing output through a
unified `OutputFormatter` class.

## Lane

**Heavy** — Changes all CLI runtime output, affecting every command's external contract
(stdout/stderr behavior, JSON schema, quiet suppression).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/formatters.py` — OutputFormatter class, OutputMode enum
- `src/gzkit/cli/commands/` — migrate all command handlers to use OutputFormatter
- `tests/` — unit tests for formatter and migration verification

## Denied Paths

- structlog integration (ADR-0.0.3 scope)
- Progress bars (OBPI-0.0.4-09 scope)
- Parser infrastructure (OBPI-0.0.4-02 scope)
- Common flags definition (OBPI-0.0.4-03 scope — this OBPI consumes those flags)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `OutputFormatter` MUST be the single chokepoint for all user-facing output in command handlers. NEVER call `console.print()` or bare `print()` directly from command code.
2. REQUIREMENT: `OutputMode` enum MUST contain exactly 5 modes: `HUMAN`, `JSON`, `QUIET`, `VERBOSE`, `DEBUG`.
3. REQUIREMENT: `OutputFormatter.__init__` MUST accept `mode: OutputMode` and `console: Console`.
4. REQUIREMENT: `emit(data)` MUST route to the appropriate renderer based on mode. MUST handle `dict`, `list`, `str`, and Pydantic `BaseModel` instances natively.
5. REQUIREMENT: `emit_error(message)` MUST ALWAYS write to stderr regardless of output mode. NEVER suppress errors in quiet mode.
6. REQUIREMENT: `emit_table(table)` MUST render Rich tables in HUMAN mode and dict-list JSON in JSON mode.
7. REQUIREMENT: `emit_status(label, success)` MUST render check/cross symbols in HUMAN mode and key-value pairs in JSON mode.
8. REQUIREMENT: `emit_blocker(message)` MUST write with `BLOCKERS:` prefix to stderr.
9. REQUIREMENT: JSON mode output MUST be valid JSON to stdout with no Rich markup. ALWAYS use `model_dump_json()` for Pydantic models and `json.dumps(sort_keys=True, indent=2)` for dicts.
10. REQUIREMENT: Quiet mode MUST suppress all non-error output. NEVER emit to stdout in quiet mode.
11. REQUIREMENT: OutputFormatter MUST respect the `NO_COLOR` environment variable.
12. REQUIREMENT: Mode selection MUST derive from common flags (`--quiet`, `--verbose`, `--debug`, `--json`) established in OBPI-0.0.4-03.
13. REQUIREMENT: After migration, NEVER leave direct `console.print()` or bare `print()` in any command handler code.

> STOP-on-BLOCKERS: if OBPI-0.0.4-01 (cli/ package structure) or OBPI-0.0.4-03 (common flags for mode selection) are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01: `src/gzkit/cli/` package structure exists
- [ ] OBPI-0.0.4-03: common flags (`--quiet`, `--verbose`, `--debug`, `--json`) are registered

**Existing Code (understand current state):**

- [ ] Current output patterns: `src/gzkit/commands/` — identify all `console.print()` and `print()` calls
- [ ] Rich Console usage: `src/gzkit/cli/` — understand current console setup
- [ ] Test patterns: `tests/` — find existing output-related tests

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
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_formatters -v
# Expected: all output mode tests pass (HUMAN, JSON, QUIET, VERBOSE, DEBUG)

uv run -m gzkit --json status
# Expected: valid JSON to stdout, no Rich markup

uv run -m gzkit --quiet status
# Expected: no stdout output (errors only to stderr)

# Verify no direct console.print/print in command handlers
# (automated grep scan in test suite)
```

## Acceptance Criteria

- [ ] REQ-0.0.4-06-01: Given `OutputFormatter` initialized with `OutputMode.HUMAN`, when `emit(data)` is called with a string, then output renders via Rich console to stdout.
- [ ] REQ-0.0.4-06-02: Given `OutputFormatter` initialized with `OutputMode.JSON`, when `emit(data)` is called with a dict, then valid JSON with sorted keys and indent=2 is written to stdout.
- [ ] REQ-0.0.4-06-03: Given `OutputFormatter` initialized with `OutputMode.JSON`, when `emit(data)` is called with a Pydantic BaseModel, then `model_dump_json()` output is written to stdout.
- [ ] REQ-0.0.4-06-04: Given `OutputFormatter` initialized with `OutputMode.QUIET`, when `emit(data)` is called, then nothing is written to stdout.
- [ ] REQ-0.0.4-06-05: Given any output mode, when `emit_error(message)` is called, then the message is written to stderr.
- [ ] REQ-0.0.4-06-06: Given `OutputFormatter` in HUMAN mode, when `emit_status("check", True)` is called, then a check symbol is rendered; when called with `False`, a cross symbol is rendered.
- [ ] REQ-0.0.4-06-07: Given `OutputFormatter` in JSON mode, when `emit_status("check", True)` is called, then a key-value JSON object is written to stdout.
- [ ] REQ-0.0.4-06-08: Given any mode, when `emit_blocker(message)` is called, then `BLOCKERS:` prefix is written to stderr.
- [ ] REQ-0.0.4-06-09: Given a full grep scan of `src/gzkit/commands/`, then zero direct `console.print()` calls exist in command handler code.
- [ ] REQ-0.0.4-06-10: Given a full grep scan of `src/gzkit/commands/`, then zero bare `print()` calls exist for user-facing output in command handler code.

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
