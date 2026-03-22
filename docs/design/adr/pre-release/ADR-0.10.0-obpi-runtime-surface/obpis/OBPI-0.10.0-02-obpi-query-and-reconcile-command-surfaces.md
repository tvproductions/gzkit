---
id: OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
parent: ADR-0.10.0-obpi-runtime-surface
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces: OBPI query and reconcile command surfaces

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #2 -- "Deliver OBPI-native query and reconcile command surfaces."

**Status:** Completed

## Objective

Deliver first-class `gz obpi ...` query and reconcile surfaces so operators can
inspect OBPI status and drift directly at OBPI scope without relying on ADR-only
status views or manual brief review.

## Lane

**Heavy** -- This unit adds or changes user-facing CLI behavior.

## Allowed Paths

- `src/gzkit/cli.py` -- command registration and operator output.
- `src/gzkit/commands/` -- OBPI query/reconcile implementations.
- `src/gzkit/ledger.py` -- derived read models used by command surfaces.
- `tests/commands/` and `tests/` -- command/runtime verification.
- `docs/user/commands/` -- new or updated command docs.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.

## Denied Paths

- Replacing or removing `gz adr status` semantics instead of adding OBPI-native parity.
- New dependencies without a separate approved rationale.
- `../airlineops/**` canonical mutations.
- CI files and lockfiles unrelated to the in-scope command surface.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI query surfaces MUST support deterministic human-readable and JSON output.
1. REQUIREMENT: Reconcile behavior MUST identify missing ledger proof, missing brief evidence, and state drift fail-closed.
1. REQUIREMENT: Existing `gz obpi emit-receipt` and `gz obpi validate` flows MUST remain compatible.
1. NEVER: Hide drift by silently inferring completion when required proof is missing.
1. ALWAYS: Prefer OBPI-native identifiers and command outputs over ADR-only indirection when reporting OBPI state.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md`
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [x] `docs/user/commands/obpi-emit-receipt.md`

**Context:**

- [x] `src/gzkit/cli.py`
- [x] `src/gzkit/commands/status.py`
- [x] `tests/commands/test_status.py`
- [x] `tests/test_obpi_validator.py`

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI runtime contract from OBPI-0.10.0-01 is accepted or stubbed with explicit assumptions
- [x] Existing `gz obpi` command group exists

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Coverage maintained: `uv run coverage run -m unittest discover tests && uv run coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run ruff format --check .`
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
uv run gz test
uv run gz lint
uv run ruff format --check .
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/
uv run gz obpi status OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
uv run gz obpi reconcile OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json
uv run gz obpi validate docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md
```

## Acceptance Criteria

- [x] REQ-0.10.0-02-01: OBPI-native query surfaces render deterministic state at OBPI granularity.
- [x] REQ-0.10.0-02-02: Reconcile output reports proof/evidence drift explicitly and fail-closed.
- [x] REQ-0.10.0-02-03: Existing receipt and validation command surfaces remain compatible.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

### Value Narrative

Before this closeout pass, `gz obpi status` and `gz obpi reconcile` were already
implemented, documented, and covered by focused tests, but this OBPI still
looked incomplete at governance level because its brief remained a placeholder
with no recorded verification evidence or acceptance narrative.

After this pass, the operator-facing query/reconcile surfaces are verified
against the recorded OBPI contract: the repo has deterministic OBPI drill-down
surfaces for text and JSON inspection, fail-closed reconciliation for missing
proof or brief drift, and documentation/examples that match current CLI
behavior. Human attestation is now recorded, so the brief and receipt state can
move together to completed runtime evidence.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded.
- [x] Parent checklist item remains quoted and unchanged.
- [x] Existing command, doc, and test surfaces were audited instead of
  re-implemented: `src/gzkit/cli.py`, `src/gzkit/commands/status.py`,
  `docs/user/commands/obpi-status.md`, `docs/user/commands/obpi-reconcile.md`,
  `tests/commands/test_status.py`, and `tests/test_obpi_validator.py`.

### Gate 2 (TDD)

```text
$ uv run gz test
Running tests...
Ran 324 tests in 4.126s
OK

Tests passed.

$ uv run coverage run -m unittest discover tests
Ran 324 tests in 5.184s
OK

$ uv run coverage report
TOTAL                                    9189   1194    87%
```

### Code Quality

```text
$ uv run gz lint
Running linters...
All checks passed!

ADR path contract check passed.
Lint passed.

$ uv run ruff format --check .
68 files already formatted

$ uv run gz typecheck
Running type checker...
All checks passed!

Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.68 seconds
```

Audit note: the `obpi-status` and `obpi-reconcile` command docs already matched
current CLI behavior, so no operator-facing doc correction was required.

### Gate 4 (BDD)

```text
$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Key Proof

- `uv run gz obpi emit-receipt OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --event completed --attestor human:jeff --evidence-json ...`
  records completed proof and human attestation for the heavy-lane OBPI.
- `uv run gz obpi status OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json`
  reports `runtime_state: attested_completed`, `attestation_requirement:
  required`, and zero issues after receipt emission.
- `uv run gz obpi reconcile OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces --json`
  returns `passed: true` with no blockers, confirming ledger and brief evidence
  are coherent.

### Implementation Summary

- Files created/modified: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md`
- Existing implementation verified: `src/gzkit/cli.py`, `src/gzkit/commands/status.py`, `docs/user/commands/obpi-status.md`, `docs/user/commands/obpi-reconcile.md`, `tests/commands/test_status.py`, and `tests/test_obpi_validator.py`
- Repository hygiene for shared format gate: Ruff normalization on `.claude/hooks/instruction-router.py`, `.claude/hooks/ledger-writer.py`, `.claude/hooks/post-edit-ruff.py`, `.github/copilot/hooks/ledger-writer.py`, and `tests/commands/test_register_adrs.py`
- Tests added: none in this pass; existing status/reconcile coverage already exercised the OBPI contract
- Ledger event recorded: `obpi_receipt_emitted` (`completed`) for `OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces`
- Date completed: 2026-03-10

## Human Attestation

- Attestor: human:jeff
- Attestation: Completed
- Date: 2026-03-10
- Scope: OBPI-0.10.0-02 query/reconcile command surfaces, verification evidence, and operator closeout review accepted.

### Gate 5 (Human)

- [x] Human attestation explicitly received from the user on 2026-03-10.
- [x] Completion receipt emitted with matching attestation metadata and scoped REQ proof inputs.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-10

**Evidence Hash:** 58348d8
