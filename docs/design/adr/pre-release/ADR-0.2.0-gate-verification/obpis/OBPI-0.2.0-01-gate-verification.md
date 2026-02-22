---
id: OBPI-0.2.0-01-gate-verification
parent: ADR-0.2.0
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.2.0-01-gate-verification: Implement gate verification commands

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md`
- **Checklist Item:** #1 — "Implement `gz implement` and `gz gates`, including `gate_checked` ledger events."

**Status:** Completed
## Objective

Create operational gate verification commands that run configured checks, report results, and append `gate_checked` events to the ledger.

## Lane

**Heavy** — external CLI contract (new commands)

## Allowed Paths

- `src/gzkit/cli.py` — add `implement` and `gates` commands
- `src/gzkit/ledger.py` — add `gate_checked` event factory
- `src/gzkit/quality.py` — reuse check runners
- `tests/test_cli.py` — CLI behavior coverage
- `tests/test_ledger.py` — event recording coverage

## Denied Paths

- `docs/design/**` — governance changes out of scope for this OBPI
- `docs/user/**` — handled in OBPI-0.2.0-03
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. `gz implement` MUST run Gate 2 using the manifest `verification.test` command.
2. `gz gates` MUST run all required gates for the current lane, or a specific gate via `--gate`.
3. Each gate execution MUST append `gate_checked` to the ledger with gate number, command, status, and return code.
4. Gate commands MUST NOT modify project files (ledger-only side effects).
5. Any failed required gate MUST cause a non-zero exit code.

> STOP-on-BLOCKERS: if `.gzkit/manifest.json` is missing, print BLOCKERS and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand scope and checklist

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/manifest.json` — verification commands
- [ ] `.gzkit/ledger.jsonl` — ledger output

**Existing Code (understand current state):**

- [ ] `src/gzkit/cli.py` — command definitions
- [ ] `src/gzkit/quality.py` — existing check runners
- [ ] `src/gzkit/ledger.py` — ledger events

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated (OBPI-0.2.0-03)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Gate commands
uv run gz implement
uv run gz gates
uv run gz gates --gate 2
```

## Acceptance Criteria

- [ ] `gz implement` runs the manifest test command and exits non-zero on failure
- [ ] `gz gates` runs the required gates for the current lane
- [ ] `gz gates --gate 2` runs only Gate 2
- [ ] Each gate run appends a `gate_checked` ledger event
- [ ] Gate failure produces non-zero exit code

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **OBPI Acceptance:** Evidence recorded below

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

### Implementation Summary

- Files created/modified: src/gzkit/cli.py, src/gzkit/ledger.py, src/gzkit/quality.py
- Tests added: tests/test_cli.py, tests/test_ledger.py
- Date completed: 2026-02-22 (historical reconciliation)

---

**Brief Status:** Completed
**Date Completed:** 2026-02-22
**Evidence Hash:** reconciled-2026-02-22
