---
id: {id}
parent: {parent_adr}
item: {item_number}
lane: {lane}
status: Draft
---

# {id}: {title}

## ADR Item

- **Source ADR:** `{parent_adr_path}`
- **Checklist Item:** #{item_number} — "{checklist_item_text}"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

{objective}

## Lane

**{lane}** — {lane_rationale}

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/module/` — Reason this is in scope
- `tests/test_module.py` — Reason

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/**` — ADR changes out of scope
- `features/**` — BDD handled separately
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: First constraint
1. REQUIREMENT: Second constraint
1. NEVER: What must not happen
1. ALWAYS: What must always be true

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `{parent_adr_path}`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required file/module exists: `path/to/prerequisite`
- [ ] Required config exists: `config/file.json`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `path/to/exemplar`
- [ ] Test patterns: `tests/path/to/similar_tests.py`

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

# Specific verification for this OBPI
command --to --verify
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [ ] Criterion 1: Description
- [ ] Criterion 2: Description
- [ ] Criterion 3: Description

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **OBPI Acceptance:** Evidence recorded below

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
