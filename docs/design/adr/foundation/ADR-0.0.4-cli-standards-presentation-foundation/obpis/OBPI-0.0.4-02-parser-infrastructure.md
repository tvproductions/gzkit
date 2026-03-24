---
id: OBPI-0.0.4-02-parser-infrastructure
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 2
lane: heavy
status: Completed
---

# OBPI-0.0.4-02: Parser Infrastructure

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #2 - "Parser infrastructure -- StableArgumentParser, NoHyphenBreaksFormatter, exit codes epilog"

**Status:** Draft

## Objective

Create the foundational parser classes and constants that all commands use: stable error
formatting, hyphen-preserving help text, and standardized exit code documentation.

## Lane

**heavy** - Changes parser error format and CLI error output, which are external contracts consumed by CI/governance tooling and operator workflows.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/parser.py`
- `src/gzkit/cli/helpers/exit_codes.py`
- `src/gzkit/cli/main.py`
- `tests/`

## Denied Paths

- `src/gzkit/cli/commands/` (command-specific help text is OBPI-0.0.4-04)
- `src/gzkit/cli/helpers/common_flags.py` (common flags are OBPI-0.0.4-03)

## Requirements (FAIL-CLOSED)

1. ALWAYS use stdlib-only dependencies (`argparse`, `textwrap`) -- NEVER introduce third-party parser dependencies.
2. ALWAYS emit parser errors in the format `BLOCKERS: {prog}: error: {message}` on stderr.
3. ALWAYS exit with code 2 on parse errors.
4. NEVER break hyphenated tokens (`ADR-0.0.4`, `YYYY-MM`, `OBPI-0.0.4-01`) across lines in help text.
5. ALWAYS define exit code constants matching the CLI Doctrine 4-code map (0, 1, 2, 3).
6. ALWAYS provide `STANDARD_EXIT_CODES_EPILOG` as a reusable `textwrap.dedent` block.
7. NEVER change existing exit code semantics for codes 0, 1, 2 already in use.
8. ALWAYS wire `StableArgumentParser` as the top-level parser in `cli/main.py`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (especially OBPI-0.0.4-01 restructure, OBPI-0.0.4-03 common flags)
- [ ] CLI Standards v3 spec: `docs/design/cli-standards-v3.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01 completed: `src/gzkit/cli/` package structure exists
- [ ] `src/gzkit/cli/main.py` exists (from OBPI-01 restructure)
- [ ] `src/gzkit/cli/helpers/` directory exists (from OBPI-01 restructure)

**Existing Code (understand current state):**

- [ ] Reference: airlineops `src/airlineops/cli/helpers/exit_codes.py`
- [ ] Reference: airlineops `src/airlineops/cli/helpers/shared.py`
- [ ] Test patterns: `tests/unit/test_parser.py` (if exists)

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
uv run -m gzkit --bad-flag 2>&1 | grep "BLOCKERS:"
uv run -m gzkit --help | grep -c "ADR-"
python -c "from gzkit.cli.helpers.exit_codes import EXIT_SUCCESS, EXIT_USER_ERROR, EXIT_SYSTEM_ERROR, EXIT_POLICY_BREACH, STANDARD_EXIT_CODES_EPILOG; print('OK')"
```

## Acceptance Criteria

- [x] **REQ-0.0.4-02-01:** `StableArgumentParser` class exists in `src/gzkit/cli/parser.py` and is used as top-level parser
- [x] **REQ-0.0.4-02-02:** Invalid arguments produce `BLOCKERS: gz: error: ...` on stderr
- [x] **REQ-0.0.4-02-03:** Parse errors exit with code 2
- [x] **REQ-0.0.4-02-04:** Help text preserves hyphenated tokens (`ADR-0.0.4`) as single tokens (no line break on hyphen)
- [x] **REQ-0.0.4-02-05:** `_NoHyphenBreaksFormatter` extends `RawDescriptionHelpFormatter` with `break_on_hyphens=False` in `_split_lines()` and `_fill_text()`
- [x] **REQ-0.0.4-02-06:** `STANDARD_EXIT_CODES_EPILOG` constant exists in `src/gzkit/cli/helpers/exit_codes.py`
- [x] **REQ-0.0.4-02-07:** Exit code constants defined: `EXIT_SUCCESS=0`, `EXIT_USER_ERROR=1`, `EXIT_SYSTEM_ERROR=2`, `EXIT_POLICY_BREACH=3`
- [x] **REQ-0.0.4-02-08:** Unit tests cover parser error format, formatter hyphen behavior, and exit code constants

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
$ uv run -m unittest tests.test_cli_parser -v
Ran 16 tests in 0.004s — OK
Coverage: parser.py 100%, exit_codes.py 100%
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — Type check passed
$ uv run gz test — Ran 1322 tests, OK
```

### Gate 3 (Docs)

N/A — no user-facing doc changes in this OBPI (parser internals).

### Gate 4 (BDD)

N/A — no BDD scenarios for parser infrastructure.

### Gate 5 (Human)

Human attestation: "attest completed" — 2026-03-24

### Value Narrative

Before: gzkit CLI used bare `argparse.ArgumentParser` with Python's default error format (`usage: gz ...` / `gz: error: ...`). Hyphenated governance tokens like `ADR-0.0.4` could be broken across lines in help text. Exit codes were ad-hoc with no centralized constants.

After: `StableArgumentParser` emits `BLOCKERS: {prog}: error: {message}` on stderr (machine-parseable for CI/governance). `_NoHyphenBreaksFormatter` preserves all hyphenated tokens. Four exit code constants and `STANDARD_EXIT_CODES_EPILOG` provide reusable infrastructure for every command.

### Key Proof

```
$ uv run gz --bad-flag 2>&1
BLOCKERS: gz: error: the following arguments are required: command
$ echo $?
2
```

### Implementation Summary

- Files created/modified: `src/gzkit/cli/parser.py`, `src/gzkit/cli/helpers/__init__.py`, `src/gzkit/cli/helpers/exit_codes.py`, `src/gzkit/cli/main.py`
- Tests added: `tests/test_cli_parser.py` (16 tests, 100% coverage)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:jeff`
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
