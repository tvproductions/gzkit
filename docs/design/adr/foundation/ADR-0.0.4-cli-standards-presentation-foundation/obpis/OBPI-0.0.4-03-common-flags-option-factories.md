---
id: OBPI-0.0.4-03-common-flags-option-factories
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 3
lane: heavy
status: Draft
---

# OBPI-0.0.4-03: Common Flags & Standard Option Factories

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #3 - "Common flags (--quiet, --verbose, --debug, --json) and standard option factories"

**Status:** Draft

## Objective

Create reusable flag registration functions that enforce consistent naming, help text,
and behavior across all commands, eliminating ad-hoc argument definitions.

## Lane

**heavy** - Changes the CLI flag surface across all commands; every command gains new flags and existing flag definitions are replaced with factory calls, altering the external contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/helpers/common_flags.py` - common flag registration functions
- `src/gzkit/cli/helpers/standard_options.py` - standard option factory functions
- `src/gzkit/cli/commands/` - wiring factories into all command parsers
- `tests/` - unit tests for factories and integration tests for flag behavior

## Denied Paths

- Command-specific arguments stay in their respective command modules (do not centralize)
- `--skill` flag is out of scope (opsdev-specific, may be added later)
- `src/gzkit/cli/main.py` - structural changes owned by OBPI-01
- `src/gzkit/cli/helpers/parser.py` - parser infrastructure owned by OBPI-02

## Requirements (FAIL-CLOSED)

1. `add_common_flags(parser)` MUST register `--quiet`/`-q`, `--verbose`/`-v`, and `--debug` on every command parser.
2. `--quiet` and `--verbose` MUST be mutually exclusive; argparse MUST reject simultaneous use.
3. Factory functions MUST NEVER allow duplicate option registration; calling a factory twice on the same parser MUST NOT raise an error.
4. Each factory function MUST provide canonical default help text and ALWAYS accept a `help_override` parameter.
5. Standard option factories MUST exist for: `--adr`, `--json`, `--dry-run`, `--force`, `--table`.
6. All existing ad-hoc `--json`, `--adr`, `--dry-run`, `--force` definitions MUST be replaced with factory calls; NEVER add new ad-hoc definitions.
7. Factory help text wording MUST be consistent with CLI doctrine conventions.
8. `--debug` MUST enable full tracebacks and DEBUG-level logging when activated.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs: OBPI-0.0.4-01 (cli/ package structure), OBPI-0.0.4-02 (parser infrastructure)
- [ ] CLI Standards v3 spec: `docs/design/cli-standards-v3.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01 delivered: `src/gzkit/cli/` package structure exists
- [ ] OBPI-0.0.4-02 delivered: `src/gzkit/cli/helpers/parser.py` exists with StableArgumentParser
- [ ] `src/gzkit/cli/helpers/` directory exists

**Existing Code (understand current state):**

- [ ] Reference: airlineops `src/airlineops/cli/helpers/standard_options.py`
- [ ] Reference: opsdev `src/opsdev/commands/_common_flags.py`
- [ ] Current ad-hoc flag definitions in `src/gzkit/cli/commands/`
- [ ] Test patterns: `tests/` for existing CLI tests

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
uv run -m unittest tests.unit.test_common_flags -v
uv run -m unittest tests.unit.test_standard_options -v
uv run -m gzkit --help           # verify common flags appear
uv run -m gzkit status --help    # verify --json from factory
```

## Acceptance Criteria

- [ ] **REQ-0.0.4-03-01:** `add_common_flags()` exists and is called on all command parsers
- [ ] **REQ-0.0.4-03-02:** `--quiet`, `--verbose`, `--debug` accepted by every command
- [ ] **REQ-0.0.4-03-03:** `--quiet` and `--verbose` are mutually exclusive (simultaneous use rejected)
- [ ] **REQ-0.0.4-03-04:** All `--json`, `--adr`, `--dry-run`, `--force`, `--table` use factory functions
- [ ] **REQ-0.0.4-03-05:** Help text from factories matches canonical wording
- [ ] **REQ-0.0.4-03-06:** No duplicate option errors when factories are called
- [ ] **REQ-0.0.4-03-07:** Unit tests exist for each factory function
- [ ] **REQ-0.0.4-03-08:** `uv run gz lint` and `uv run gz test` pass clean

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
