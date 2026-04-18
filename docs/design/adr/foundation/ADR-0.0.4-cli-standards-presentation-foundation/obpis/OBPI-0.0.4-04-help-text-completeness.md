---
id: OBPI-0.0.4-04-help-text-completeness
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 4
lane: heavy
status: attested_completed
---

# OBPI-0.0.4-04: Help Text Completeness

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #4 - "Help text completeness on all ~123 bare arguments and all commands"

**Status:** Draft

## Objective

Ensure every argument, option, and subcommand across all 35 top-level commands and 26 subcommands has a `help=` string and every parser has a `description=`.

## Lane

**Heavy** - Changes all CLI help output across every command, which is an external operator-facing contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/cli/commands/`
- `src/gzkit/cli/main.py`
- `tests/`

## Denied Paths

- Epilog content (owned by OBPI-0.0.4-05)
- Runtime output changes (owned by OBPI-0.0.4-08)

## Requirements (FAIL-CLOSED)

1. Every `add_argument()` call MUST have a non-empty `help=` string.
2. Every parser and subparser MUST have a non-empty `description=` string.
3. Help text MUST be action-oriented (verb-first) and under 80 characters.
4. Help text MUST NOT contain `TODO`, `FIXME`, `XXX`, or `print(`.
5. No breaking changes to argument names or behavior. NEVER rename or remove existing arguments.
6. `formatter_class` MUST be set to combined NoHyphenBreaks+RawDescription on all parsers.
7. Positional arguments MUST be documented by name and purpose.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-01 (cli/ package structure) is complete - `src/gzkit/cli/` directory exists with `commands/` and `main.py`
- [ ] OBPI-0.0.4-03 (option factories) is complete - canonical help strings provided by factories

**Existing Code (understand current state):**

- [ ] Target commands with known gaps:
  - `gz validate`: `--manifest`, `--documents`, `--surfaces`, `--ledger`, `--instructions`, `--json`
  - `gz gates`: `--gate`, `--adr`
  - `gz implement`: `--adr`
  - `gz attest`: positional `adr`, `--reason`, `--force`, `--dry-run`
  - `gz status`: `--json`
  - `gz plan`: 12 arguments with no help
  - `gz specify`, `gz prd`, `gz init`: arguments undocumented
  - `gz closeout`, `gz audit`: critical arguments undocumented
  - All chores subcommand arguments
- [ ] Reference implementation: `airlineops` `tests/cli/test_cli_consistency.py` - recursive parser auditor
- [ ] Test patterns: `tests/` - existing CLI test files

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
# Recursive parser walk asserting all .help attributes are non-None and non-SUPPRESS
# Recursive parser walk asserting all parsers have .description
# Regex scan of help text for forbidden patterns (TODO, FIXME, XXX, print()
uv run -m unittest tests.test_help_text_completeness -v
```

## Acceptance Criteria

- [x] **REQ-0.0.4-04-01:** Recursive parser audit finds zero undocumented arguments (`help=` non-None, non-SUPPRESS on every argument)
- [x] **REQ-0.0.4-04-02:** Recursive parser audit finds zero commands without `description=` on their parser
- [x] **REQ-0.0.4-04-03:** No help text contains `TODO`, `FIXME`, `XXX`, or `print(`
- [x] **REQ-0.0.4-04-04:** All help text lines are under 80 characters
- [x] **REQ-0.0.4-04-05:** [doc] `uv run gz lint` passes clean
- [x] **REQ-0.0.4-04-06:** [doc] `uv run gz test` passes clean

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
uv run -m unittest tests.test_help_text_completeness -v
5 tests pass (REQ-01 through REQ-04 + formatter_class)
uv run gz test — 1367 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run ruff format — clean
uv run gz typecheck — pre-existing warnings only (not introduced by this OBPI)
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.93 seconds
```

### Gate 4 (BDD)

```text
N/A — no BDD features scoped to this OBPI
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-24
```

### Value Narrative

Before this OBPI, approximately half of gzkit's ~130 CLI arguments lacked help= strings and nearly all 50+ parsers/subparsers lacked description= strings. Operators running gz --help saw undocumented arguments. Now every argument and parser across all 35 top-level commands has action-oriented help text under 80 characters, enforced by a recursive parser audit test.

### Key Proof

```text
$ uv run -m unittest tests.test_help_text_completeness -v
test_all_arguments_have_help ... ok
test_all_parsers_have_description ... ok
test_formatter_class_set ... ok
test_help_text_under_80_chars ... ok
test_no_forbidden_patterns_in_help ... ok
Ran 5 tests in 0.110s — OK
```

### Implementation Summary

- Files created/modified: tests/test_help_text_completeness.py (new), src/gzkit/cli/main.py (modified)
- Tests added: 5 tests in test_help_text_completeness.py
- Date completed: 2026-03-24
- Attestation status: Human attested completed
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-03-24`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
