---
id: OBPI-0.0.4-05-epilog-templates
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 5
lane: heavy
status: Draft
---

# OBPI-0.0.4-05: Epilog Templates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #5 - "Epilog templates — examples and exit codes on every command"

**Status:** Draft

## Objective

Add epilogs with `Examples` and `Exit codes` sections to every command and subcommand,
following the airlineops/opsdev pattern, via a shared `build_epilog()` helper.

## Lane

**heavy** - Changes all CLI `--help` output across every command and subcommand (external contract).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/helpers/epilog.py`
- `src/gzkit/cli/commands/`
- `src/gzkit/cli/main.py`
- `tests/`

## Denied Paths

- Help text content (`src/gzkit/cli/` help strings owned by OBPI-04)
- Runtime output formatting (owned by OBPI-08)

## Requirements (FAIL-CLOSED)

1. Every top-level command MUST have a non-empty `.epilog` containing "Examples" and "Exit codes" sections.
2. Every subcommand MUST have a non-empty `.epilog` containing "Examples" and "Exit codes" sections.
3. All example commands in epilogs MUST be real, executable `gz` invocations -- no placeholder or aspirational examples.
4. All epilogs MUST use `RawDescriptionHelpFormatter` (or compatible) to preserve whitespace formatting.
5. Examples MUST demonstrate the most common usage patterns for each command.
6. Exit codes MUST default to `STANDARD_EXIT_CODES_EPILOG` from OBPI-02 unless a command defines command-specific codes.
7. The `build_epilog()` helper MUST be the single construction point for all epilog strings.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (especially OBPI-01, OBPI-02, OBPI-04)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01 completed: `src/gzkit/cli/` package structure exists
- [ ] OBPI-0.0.4-02 completed: `STANDARD_EXIT_CODES_EPILOG` constant exists
- [ ] OBPI-0.0.4-04 completed: help text in place on all commands

**Existing Code (understand current state):**

- [ ] Reference implementation: `airlineops/src/airlineops/cli/helpers/` (epilog pattern)
- [ ] Current command registrations: `src/gzkit/cli/commands/`
- [ ] Test patterns: `tests/`

**Example Pattern (target epilog output):**

```
Examples
    gz status --table
    gz status --json
    gz status --show-gates

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
```

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
uv run -m unittest tests.test_epilog -v
uv run -m gzkit status --help  # verify epilog renders
uv run -m gzkit adr --help     # verify subcommand epilog renders
```

## Acceptance Criteria

- [ ] **REQ-0.0.4-05-01:** `build_epilog()` helper exists in `src/gzkit/cli/helpers/epilog.py` with signature `build_epilog(examples: list[str], *, exit_codes: str | None = None) -> str`
- [ ] **REQ-0.0.4-05-02:** All top-level commands have non-empty `.epilog` values
- [ ] **REQ-0.0.4-05-03:** All subcommands have non-empty `.epilog` values
- [ ] **REQ-0.0.4-05-04:** Every epilog contains "Examples" and "Exit codes" sections
- [ ] **REQ-0.0.4-05-05:** All example commands in epilogs are syntactically valid `gz` invocations
- [ ] **REQ-0.0.4-05-06:** `uv run gz lint` passes
- [ ] **REQ-0.0.4-05-07:** `uv run gz test` passes

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
# Paste behave output here
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
