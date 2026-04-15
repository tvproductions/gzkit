---
id: OBPI-0.8.0-01-chores-registry
parent: ADR-0.8.0-gz-chores-system
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.8.0-01-chores-registry: Chores registry and configuration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- **Checklist Item:** #1 -- "Define a config-first chore registry with lanes, evidence commands, and acceptance checks."

**Status:** Completed

## Objective

Define the `config/gzkit.chores.json` schema and implement the registry loader so chores are defined declaratively with lanes, evidence, and acceptance blocks.

## Lane

**Heavy** -- New CLI command surface (`gz chores ...`) is an external contract change.

## Allowed Paths

- `src/gzkit/` -- chores registry parsing, runner, and CLI plumbing.
- `tests/` -- unit tests for registry parsing and runner behavior.
- `docs/design/briefs/` -- migration report and chore brief/log scaffolding.
- `config/gzkit.chores.json` -- new config-first chore registry.
- `docs/user/commands/` -- command docs and index parity for new `gz chores` surface.

## Denied Paths

- Parent ADR text outside `ADR-0.8.0` checklist linkage is out of scope.
- New third-party dependencies.
- CI files, lockfiles.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Chore registry is config-first JSON with lanes, evidence, and acceptance blocks.
2. REQUIREMENT: `gz chores list` and `gz chores plan` run without network access.
3. REQUIREMENT: `gz chores run` executes only registry-declared commands and writes a dated log entry.
4. NEVER: Execute commands not declared in the registry.
5. ALWAYS: Preserve deterministic output paths for evidence and logs.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` -- agent operating contract
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`
- [x] Migration report: `docs/design/briefs/REPORT-airlineops-chores-migration.md`

**Existing Code (understand current state):**

- [x] CLI command registration pattern: `src/gzkit/cli.py`
- [x] Quality runner patterns: `src/gzkit/quality.py`

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit.json` exists and points to `docs/design`

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
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
# Registry inspection
uv run gz chores list

# Plan scaffold
uv run gz chores plan <slug>

# Execution + logging
uv run gz chores run <slug>

# Audit
uv run gz chores audit --all
```

## Acceptance Criteria

- [x] REQ-0.8.0-01-01: `gz chores` command group exists with list, plan, run, and audit subcommands.
- [x] REQ-0.8.0-01-02: Registry loads from `config/gzkit.chores.json` with lanes, evidence, acceptance.
- [x] REQ-0.8.0-01-03: Running a chore writes a dated log entry under `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`.
- [x] REQ-0.8.0-01-04: Lane commands execute with timeouts and non-zero exit status on failure.

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
$ uv run -m unittest discover tests
Ran 301 tests in 4.699s
OK

$ uv run -m coverage run -m unittest discover tests && uv run -m coverage report
TOTAL                                    8455   1102    87%

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

$ uv run gz cli audit
CLI audit passed.
```

### Key Proof

`uv run gz chores run quality-check` completed successfully and wrote a dated log entry:
`docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md`

### Implementation Summary

- Files created/modified:
  - `src/gzkit/commands/chores.py`
  - `src/gzkit/cli.py`
  - `src/gzkit/commands/common.py`
  - `config/gzkit.chores.json`
  - `docs/design/briefs/REPORT-airlineops-chores-migration.md`
  - `docs/design/briefs/chores/CHORE-quality-check/logs/CHORE-LOG.md`
  - `docs/user/commands/chores-list.md`
  - `docs/user/commands/chores-plan.md`
  - `docs/user/commands/chores-run.md`
  - `docs/user/commands/chores-audit.md`
  - `docs/user/commands/index.md`
- Tests added:
  - `tests/commands/test_chores.py`
  - `tests/commands/test_parsers.py` (`chores` help coverage)
- Date completed: 2026-03-07

## Human Attestation

- Attestor: human:jeff
- Attestation: Accepted. OBPI-0.8.0-01 delivers config-first chores registry semantics with fail-closed execution boundaries and deterministic log evidence.
- Date: 2026-03-07

---

**Brief Status:** Completed

**Date Completed:** 2026-03-07

**Evidence Hash:** d92a0f5
