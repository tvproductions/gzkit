---
id: OBPI-0.7.0-02-obpi-completion-recorder-and-anchor
parent: ADR-0.7.0-obpi-first-operations
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.7.0-02-obpi-completion-recorder-and-anchor: Obpi Completion Recorder And Anchor

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #2 — "Implement OBPI completion recorder and anchor parity."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Record OBPI completion transitions as first-class runtime events with optional git anchor capture for temporal provenance.

## Lane

**Heavy** — Recorder behavior defines authoritative completion evidence.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/hooks/**` — completion recorder lifecycle path
- `src/gzkit/ledger.py` — event representation and graph semantics
- `src/gzkit/schemas/ledger.json` — schema constraints
- `tests/**` — recorder and schema coverage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: OBPI completion records MUST be append-only and machine-readable.
1. REQUIREMENT: Anchor capture failures MUST degrade gracefully without crashing the completion flow.
1. NEVER: Never rewrite prior OBPI lifecycle evidence entries.
1. ALWAYS: Recorder output must preserve OBPI id, parent ADR context, and completion event semantics.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required file/module exists: `src/gzkit/ledger.py`
- [ ] Required config exists: `.gzkit/manifest.json`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `../airlineops/.claude/hooks/obpi-completion-recorder.py`
- [ ] Test patterns: `tests/test_ledger.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Recorder/ledger behavior
uv run -m unittest discover tests
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [ ] Completion recorder writes deterministic OBPI lifecycle events.
- [ ] Optional anchor semantics are represented in schema and runtime handling.
- [ ] Regression tests cover recorder success and graceful-degradation paths.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
