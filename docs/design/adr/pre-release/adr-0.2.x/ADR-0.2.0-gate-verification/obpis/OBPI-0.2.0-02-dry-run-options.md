---
id: OBPI-0.2.0-02-dry-run-options
parent: ADR-0.2.0
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.2.0-02-dry-run-options: Add dry-run support for mutation commands

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/adr-0.2.x/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md`
- **Checklist Item:** #2 — "Add `--dry-run` to mutation commands listed above with no side effects."

**Status:** Draft

## Objective

Provide `--dry-run` on mutation commands so humans can rehearse governance workflows without writing files or appending to the ledger.

## Lane

**Heavy** — external CLI contract (new options)

## Allowed Paths

- `src/gzkit/cli.py` — add `--dry-run` flags and behavior
- `tests/test_cli.py` — dry-run behavior coverage

## Denied Paths

- `docs/design/**` — governance changes out of scope for this OBPI
- `docs/user/**` — handled in OBPI-0.2.0-03
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. `--dry-run` MUST be accepted by: `gz init`, `gz prd`, `gz constitute`, `gz plan`, `gz specify`, `gz attest`, `gz sync`, `gz tidy`.
2. Dry-run MUST NOT create/modify files or append to the ledger.
3. Dry-run MUST print intended actions and ledger events.
4. Dry-run MUST respect existing validation (e.g., init cannot overwrite without `--force`).
5. Commands MUST exit 0 when preconditions pass (even in dry-run).

> STOP-on-BLOCKERS: if dry-run would create paths outside the project root, print BLOCKERS and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand scope and checklist

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/adr-0.2.x/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/ledger.jsonl` exists (for commands that require init)
- [ ] `.gzkit.json` exists (for commands that require init)

**Existing Code (understand current state):**

- [ ] `src/gzkit/cli.py` — current command flows and file writes

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

# Dry-run examples
uv run gz init --dry-run
uv run gz prd DEMO-0.2.0 --dry-run
uv run gz plan demo --semver 0.2.0 --dry-run
```

## Acceptance Criteria

- [ ] Each listed command accepts `--dry-run` and returns exit code 0
- [ ] No files or ledger events are created during dry-run
- [ ] Output includes a clear list of intended actions
- [ ] Validation errors still surface (e.g., init without `--force`)

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

- Files created/modified:
- Tests added:
- Date completed:

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
