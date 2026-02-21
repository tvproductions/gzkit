---
id: OBPI-0.7.0-03-ledger-first-obpi-audit-consumption
parent: ADR-0.7.0-obpi-first-operations
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.7.0-03-ledger-first-obpi-audit-consumption: Ledger First Obpi Audit Consumption

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #3 — "Move audit readiness to ledger-first OBPI consumption."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Make OBPI completion/audit checks consume ledger proof as primary evidence instead of relying only on brief text inspection.

## Lane

**Heavy** — This changes closeout readiness semantics and operator trust model.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/cli.py` — `adr audit-check` and related reporting behavior
- `src/gzkit/ledger.py` — OBPI evidence derivation logic
- `docs/user/commands/**` — operator-facing command documentation
- `tests/**` — command and lifecycle coverage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: OBPI audit-check semantics MUST classify completion from ledger proof.
1. REQUIREMENT: Missing or stale OBPI proof MUST produce explicit blocking findings.
1. NEVER: Never claim attestation readiness when OBPI proof is absent.
1. ALWAYS: Audit output must identify next corrective action for incomplete OBPIs.

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

- [ ] Pattern to follow: `../airlineops/src/opsdev/lib/adr_audit_ledger.py`
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

# Audit consumption behavior
uv run gz adr audit-check ADR-0.7.0-obpi-first-operations --json
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [ ] `adr audit-check` reflects ledger proof-first OBPI completeness.
- [ ] Incomplete/missing OBPI proof is reported with actionable findings.
- [ ] Tests protect backward compatibility for existing ledger events.

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
