---
id: OBPI-0.8.0-02-chores-runner
parent: ADR-0.8.0-gz-chores-system
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.8.0-02-chores-runner: Chores runner and execution engine

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- **Checklist Item:** #2 -- "Runner: Execution engine with evidence capture."

**Status:** Completed

## Objective

Deliver fail-closed `gz chores run` execution semantics with timeout, non-zero failure propagation, missing-executable handling, and deterministic log evidence capture.

## Lane

**Heavy** -- Execution behavior is an externally observable CLI contract.

## Allowed Paths

- `src/gzkit/commands/chores.py` -- runner execution behavior and failure handling.
- `tests/commands/test_chores.py` -- runner success/failure-path verification.
- `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/obpis/OBPI-0.8.0-02-chores-runner.md` -- completion evidence and attestation.

## Denied Paths

- `docs/user/**` -- lifecycle/manpage expansion remains scoped to OBPI-03.
- New dependencies beyond test/verification tooling.
- CI files and lockfiles unrelated to in-scope verification.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz chores run <slug>` executes only registry-declared `steps[*].argv` commands.
2. REQUIREMENT: Non-zero subprocess exits and timeouts return non-zero CLI status.
3. REQUIREMENT: Missing executable errors fail closed and are recorded in runner logs.
4. NEVER: Execute shell-string commands outside registry-declared argv arrays.
5. ALWAYS: Append deterministic dated log entries under `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` -- agent operating contract
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- [x] Related OBPIs in same ADR reviewed for boundary (`OBPI-0.8.0-01`, `OBPI-0.8.0-03`)

**Prerequisites (check existence, STOP if missing):**

- [x] `config/gzkit.chores.json` exists and parses
- [x] `src/gzkit/commands/chores.py` contains runner implementation

**Existing Code (understand current state):**

- [x] Runner implementation path: `src/gzkit/commands/chores.py::chores_run`
- [x] Test harness pattern: `tests/commands/test_chores.py` with isolated filesystem runner

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Coverage maintained: `uv run -m coverage run -m unittest discover tests && uv run -m coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz check` (includes format check)
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated (OBPI brief evidence and runner acceptance criteria)

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
# Runner behavior
uv run gz chores run quality-check
uv run gz chores audit --all

# Gate verification
uv run -m unittest discover tests
uv run -m coverage run -m unittest discover tests && uv run -m coverage report
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.8.0-02-01: `gz chores run` executes registry-declared argv steps and records step rc/duration.
- [x] REQ-0.8.0-02-02: Timeout and non-zero subprocess exits fail closed with non-zero CLI status.
- [x] REQ-0.8.0-02-03: Missing executable errors fail closed and produce `Status: FAIL` runner log entries.
- [x] REQ-0.8.0-02-04: Runner evidence is captured in deterministic chore log paths.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now documented via receipt evidence
- [x] **Key Proof:** One concrete usage example included below
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.commands.test_chores
Ran 8 tests in 1.174s
OK

$ uv run -m unittest discover tests
Ran 303 tests in 7.992s
OK

$ uv run -m coverage run -m unittest discover tests && uv run -m coverage report
TOTAL                                    8478   1097    87%

$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Code Quality

```text
$ uv run gz lint
All checks passed.

$ uv run gz typecheck
All checks passed.

$ uv run mkdocs build --strict
Documentation built successfully.
```

### Key Proof

`uv run gz chores run quality-check` completed and appended a dated runner log entry at:
`docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md`

### Implementation Summary

- Files created/modified:
  - `tests/commands/test_chores.py` (added non-zero exit and missing-executable failure-path coverage)
  - `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/obpis/OBPI-0.8.0-02-chores-runner.md`
  - `docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md`
- Tests added:
  - `test_chores_run_nonzero_exit_returns_nonzero_and_logs_fail`
  - `test_chores_run_missing_executable_returns_nonzero_and_logs_fail`
- Date completed: 2026-03-07

## Human Attestation

- Attestor: human:jeff
- Attestation: Accepted. Runner behavior now demonstrates fail-closed execution for success, timeout, non-zero, and missing-executable paths with deterministic evidence logs.
- Date: 2026-03-07

---

**Brief Status:** Completed

**Date Completed:** 2026-03-07

**Evidence Hash:** d92a0f5
