---
id: OBPI-0.0.4-03-common-flags-option-factories
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 3
lane: heavy
status: attested_completed
---

# OBPI-0.0.4-03: Common Flags & Standard Option Factories

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #3 - "Common flags (--quiet, --verbose, --debug, --json) and standard option factories"

**Status:** Completed

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

- [x] **REQ-0.0.4-03-01:** `add_common_flags()` exists and is called on all command parsers
- [x] **REQ-0.0.4-03-02:** `--quiet`, `--verbose`, `--debug` accepted by every command
- [x] **REQ-0.0.4-03-03:** `--quiet` and `--verbose` are mutually exclusive (simultaneous use rejected)
- [x] **REQ-0.0.4-03-04:** All `--json`, `--adr`, `--dry-run`, `--force`, `--table` use factory functions
- [x] **REQ-0.0.4-03-05:** Help text from factories matches canonical wording
- [x] **REQ-0.0.4-03-06:** No duplicate option errors when factories are called
- [x] **REQ-0.0.4-03-07:** [doc] Unit tests exist for each factory function
- [x] **REQ-0.0.4-03-08:** [doc] `uv run gz lint` and `uv run gz test` pass clean

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

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 40 tests in 0.009s — OK
tests/unit/test_common_flags.py: 18 tests
tests/unit/test_standard_options.py: 22 tests
Full suite: 1362 tests pass
```

### Code Quality

```text
uv run gz lint: All checks passed
uv run gz typecheck: Passed (1 pre-existing warning in roles.py)
uv run ruff format: 177 files unchanged
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict: Documentation built in 3.69 seconds
```

### Gate 4 (BDD)

```text
N/A — no BDD scenarios defined for this OBPI
```

### Gate 5 (Human)

```text
Attestor: jbabb
Attestation: attest completed
Date: 2026-03-24
```

### Value Narrative

Before this OBPI, every command defined its own --json, --dry-run, --force, and --adr flags
independently (~20 ad-hoc --json, ~15 --dry-run) with inconsistent help text and no common
flags (--quiet, --verbose, --debug). Now, reusable factory functions enforce canonical help
text, consistent dest naming, and idempotent registration. Every command inherits --quiet,
--verbose, and --debug. --debug activates DEBUG-level logging and full tracebacks.

### Key Proof

```text
$ uv run gz status --help
usage: gz status [-h] [--json] [--table] [--show-gates] [--quiet | --verbose] [--debug]
```

### Implementation Summary

- Files created: common_flags.py, standard_options.py, test_common_flags.py, test_standard_options.py
- Files modified: helpers/__init__.py, cli/main.py
- Tests added: 40
- Date completed: 2026-03-24
- Attestation status: Completed (human)
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jbabb`
- Attestation: `attest completed`
- Date: `2026-03-24`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
