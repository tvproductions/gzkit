---
id: OBPI-0.7.0-01-obpi-completion-validator-gate
parent: ADR-0.7.0-obpi-first-operations
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.7.0-01-obpi-completion-validator-gate: Obpi Completion Validator Gate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #1 — "Implement OBPI completion validator gate parity."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Add a pre-completion validator gate that blocks OBPI `Completed` transitions when required evidence or human attestation prerequisites are not satisfied.

## Lane

**Heavy** — This enforces authority boundaries for OBPI lifecycle transitions.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/hooks/**` — completion-gate runtime logic
- `src/gzkit/cli.py` — surfaced status/audit behavior coupling
- `tests/**` — gate and regression coverage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Completion edit attempts MUST be blocked when OBPI evidence prerequisites are absent.
1. REQUIREMENT: Heavy/Foundation parent ADRs MUST require explicit human attestation before completion.
1. NEVER: Never silently downgrade failed completion gating to warning-only behavior.
1. ALWAYS: Gate failures must explain required next action to the operator.

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

- [ ] Required file/module exists: `src/gzkit/cli.py`
- [ ] Required config exists: `.gzkit/manifest.json`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `../airlineops/.claude/hooks/obpi-completion-validator.py`
- [ ] Test patterns: `tests/test_cli.py`

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

# Gate behavior
uv run -m unittest discover tests
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [ ] Validator gate blocks invalid `Completed` transitions deterministically.
- [ ] Heavy/Foundation attestation inheritance is enforced.
- [ ] Tests cover success, block, and error-handling paths.

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
