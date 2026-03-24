---
id: OBPI-0.0.4-10-cli-consistency-tests
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 10
lane: heavy
status: Draft
---

# OBPI-0.0.4-10: CLI Consistency Tests

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #10 - "CLI consistency tests — policy enforcement via recursive parser auditor"

**Status:** Draft

## Objective

Create policy tests that enforce CLI conventions automatically via a recursive parser auditor, preventing regressions when new commands are added.

## Lane

**heavy** - These tests enforce CLI contract compliance by validating external-facing command surfaces (help text, flags, epilogs, exit codes). Contract validation is a heavy-lane concern.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `tests/policy/test_cli_consistency.py`
- `tests/policy/test_import_boundaries.py`
- `tests/` (supporting test utilities, `__init__.py` files)

## Denied Paths

- Domain import boundary tests (ADR-0.0.3 scope)
- Runtime output snapshot tests (OBPI-0.0.4-08 scope)
- `src/gzkit/` (this OBPI creates tests only, no production code changes)

## Requirements (FAIL-CLOSED)

1. Policy tests MUST scan source code structurally; they MUST NOT import or execute application code at runtime.
2. Policy tests MUST use `ast` for structural analysis and string matching for pattern detection.
3. A recursive parser auditor MUST walk the full argparse parser tree and collect all commands, options, and help text.
4. All `--` options MUST use hyphens (`--dry-run`), NEVER underscores (`--dry_run`).
5. Every parser (command and subcommand) MUST have `.description` set.
6. Every argument/option MUST have `.help` set (not `None`, not `SUPPRESS`).
7. Every parser MUST have a non-empty `.epilog` containing "Examples" and "Exit codes" substrings.
8. Help text MUST NOT contain debugging artifacts (`TODO`, `FIXME`, `XXX`, `print(`, `pdb.set_trace`).
9. Full `--help` rendering MUST complete in <1s.
10. Command modules MUST NOT import from `core/` adapters directly.
11. Command handlers MUST NOT call `os.getenv()` outside a narrow allowlist (`NO_COLOR`, `FORCE_COLOR`).
12. Error messages MUST explain what boundary was violated and where.
13. Allowlists for expected exceptions MUST be explicit and minimal.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- [ ] Related OBPIs in same ADR (all 9 prior OBPIs)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.4-04 completed (all help text in place)
- [ ] OBPI-0.0.4-05 completed (all epilogs in place)
- [ ] All prior OBPIs completed (tests validate the complete CLI state)

**Existing Code (understand current state):**

- [ ] Reference implementation: `/Users/jeff/Documents/Code/airlineops/tests/cli/test_cli_consistency.py`
- [ ] Existing policy tests: `tests/policy/` (if any)
- [ ] CLI parser entry point: `src/gzkit/cli/main.py`

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
uv run -m unittest tests.policy.test_cli_consistency -v
uv run -m unittest tests.policy.test_import_boundaries -v
```

The tests ARE the test plan -- they validate all prior OBPI deliverables. Manually verify a regression is caught by temporarily breaking a convention.

## Acceptance Criteria

- [ ] **REQ-0.0.4-10-01:** `tests/policy/test_cli_consistency.py` exists with recursive parser auditor that walks the full argparse tree
- [ ] **REQ-0.0.4-10-02:** No-underscore-flags test catches `--dry_run` style violations
- [ ] **REQ-0.0.4-10-03:** Description-required test fails when any parser lacks `.description`
- [ ] **REQ-0.0.4-10-04:** Help-text-required test fails when any argument/option has `None` or `SUPPRESS` help
- [ ] **REQ-0.0.4-10-05:** Epilog-required test fails when any parser lacks a non-empty `.epilog` containing "Examples" and "Exit codes"
- [ ] **REQ-0.0.4-10-06:** `tests/policy/test_import_boundaries.py` enforces command modules do not import from `core/` adapters and do not call `os.getenv()` outside allowlist
- [ ] **REQ-0.0.4-10-07:** All policy tests pass: `uv run gz test` and `uv run gz lint` clean

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
