---
id: OBPI-0.0.4-10-cli-consistency-tests
parent: ADR-0.0.4-cli-standards-presentation-foundation
item: 10
lane: heavy
status: in_progress
---

# OBPI-0.0.4-10: CLI Consistency Tests

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.4-cli-standards-presentation-foundation/ADR-0.0.4-cli-standards-presentation-foundation.md`
- **Checklist Item:** #10 - "CLI consistency tests — policy enforcement via recursive parser auditor"

**Status:** Completed

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

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

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

- [x] **REQ-0.0.4-10-01:** [doc] `tests/policy/test_cli_consistency.py` exists with recursive parser auditor that walks the full argparse tree
- [x] **REQ-0.0.4-10-02:** [doc] No-underscore-flags test catches `--dry_run` style violations
- [x] **REQ-0.0.4-10-03:** [doc] Description-required test fails when any parser lacks `.description`
- [x] **REQ-0.0.4-10-04:** [doc] Help-text-required test fails when any argument/option has `None` or `SUPPRESS` help
- [x] **REQ-0.0.4-10-05:** [doc] Epilog-required test fails when any parser lacks a non-empty `.epilog` containing "Examples" and "Exit codes"
- [x] **REQ-0.0.4-10-06:** [doc] `tests/policy/test_import_boundaries.py` enforces command modules do not import from `core/` adapters and do not call `os.getenv()` outside allowlist
- [x] **REQ-0.0.4-10-07:** [doc] All policy tests pass: `uv run gz test` and `uv run gz lint` clean

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
Ran 7 tests in 0.165s — OK (test_cli_consistency)
Ran 13 tests in 0.108s — OK (test_import_boundaries)
Full suite: 1480 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.90 seconds
```

### Gate 4 (BDD)

```text
No BDD scenarios specific to this OBPI — policy tests ARE the acceptance tests.
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-25
```

### Value Narrative

Before this OBPI, gzkit had no automated enforcement of CLI conventions. New commands could be added with missing help text, underscore flags, no epilogs, or debugging artifacts — and nothing would catch it until human review. Now, a recursive parser auditor walks the entire argparse tree on every test run and catches regressions automatically, while AST-based policy tests enforce import boundaries and env-var hygiene in command modules.

### Key Proof

```bash
uv run -m unittest tests.policy.test_cli_consistency -v
# 7/7 tests pass: underscore flags, descriptions, help text, epilogs, debug artifacts, render speed, self-isolation
```

### Implementation Summary

- Files created/modified: tests/policy/test_cli_consistency.py (created), tests/policy/test_import_boundaries.py (modified)
- Tests added: 10 (7 consistency + 3 boundary)
- Date completed: 2026-03-25
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeff`
- Attestation: `attest completed`
- Date: `2026-03-25`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-25

**Evidence Hash:** -
