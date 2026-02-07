---
id: OBPI-0.6.0-01-chores-system-core
parent: ADR-0.6.0-pool.gz-chores-system
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.6.0-01-chores-system-core: Chores system core scaffolding

## ADR Item

- **Source ADR:** `docs/design/adr/pool/ADR-0.6.0-pool.gz-chores-system.md`
- **Checklist Item:** #1 -- "Stand up a minimal gz chores system (registry + list/plan/run/audit)."

**Status:** Draft

## Objective

Deliver a minimal gz chores subsystem that can list chores from a registry, generate a plan template, run lane
commands, capture evidence, and write a per-chore log entry.

## Lane

**Heavy** -- New CLI command surface (`gz chores ...`) is an external contract change.

## Allowed Paths

- `src/gzkit/` -- chores registry parsing, runner, and CLI plumbing.
- `tests/` -- unit tests for registry parsing and runner behavior.
- `docs/design/briefs/` -- migration report and chore brief/log scaffolding.
- `config/gzkit.chores.json` -- new config-first chore registry.

## Denied Paths

- `docs/design/adr/**` -- ADR text changes out of scope (except this OBPI reference link).
- `docs/user/**` -- public docs deferred to a later OBPI.
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

- [ ] `AGENTS.md` / `CLAUDE.md` -- agent operating contract
- [ ] Parent ADR: `docs/design/adr/pool/ADR-0.6.0-pool.gz-chores-system.md`
- [ ] Migration report: `docs/design/briefs/REPORT-airlineops-chores-migration.md`

**Existing Code (understand current state):**

- [ ] CLI command registration pattern: `src/gzkit/cli.py`
- [ ] Quality runner patterns: `src/gzkit/quality.py`

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit.json` exists and points to `docs/design`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] `gz chores` command group exists with list, plan, run, and audit subcommands.
- [ ] Registry loads from `config/gzkit.chores.json` with lanes, evidence, acceptance.
- [ ] Running a chore writes a dated log entry under `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`.
- [ ] Lane commands execute with timeouts and non-zero exit status on failure.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
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

**Date Completed:** --

**Evidence Hash:** --
