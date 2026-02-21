---
id: OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity
parent: ADR-0.5.0-skill-lifecycle-governance
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity: Obpi Acceptance Protocol Runtime Parity

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #5 — "Align OBPI completion runtime semantics with AirlineOps acceptance protocol."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Define and implement runtime enforcement so OBPI `Completed` status transitions require protocol-conformant evidence and human authority semantics.

## Lane

**Heavy** — Changes affect governance runtime behavior and operator-facing trust boundaries.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `AGENTS.md` — protocol source of truth for ceremony and authority inheritance
- `src/gzkit/hooks/**` — hook runtime behavior for completion enforcement
- `src/gzkit/cli.py` — OBPI/ADR status and audit command behavior
- `src/gzkit/ledger.py` — OBPI lifecycle event semantics
- `src/gzkit/schemas/ledger.json` — event schema contract
- `docs/governance/GovZero/**` — lifecycle policy documentation
- `docs/user/**` — operator command and workflow narratives
- `tests/**` — verification coverage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- New dependencies
- External network calls
- Destructive git operations

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: OBPI completion transitions MUST enforce Heavy/Foundation human attestation before status moves to `Completed`.
1. REQUIREMENT: Runtime checks MUST fail closed when required audit evidence is missing.
1. REQUIREMENT: OBPI completion recording MUST write machine-readable lifecycle evidence to ledger.
1. NEVER: Do not allow gate-centric rollup to claim ADR completion when OBPI units remain incomplete.
1. ALWAYS: Value narrative + key proof expectations remain part of OBPI acceptance evidence.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required module exists: `src/gzkit/hooks/core.py`
- [ ] Required CLI surfaces exist: `src/gzkit/cli.py`

**Existing Code (understand current state):**

- [ ] Canonical pattern: `../airlineops/.claude/hooks/obpi-completion-validator.py`
- [ ] Canonical pattern: `../airlineops/.claude/hooks/obpi-completion-recorder.py`
- [ ] Test patterns: `tests/test_cli.py`, `tests/test_ledger.py`

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

# Status/audit semantics
uv run gz status --json
uv run gz adr status ADR-0.7.0-obpi-first-operations --json
uv run gz adr audit-check ADR-0.7.0-obpi-first-operations --json
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [ ] OBPI completion enforcement matches Heavy/Foundation attestation inheritance rules.
- [ ] Ledger and schema surfaces represent OBPI completion evidence deterministically.
- [ ] Status/audit output reflects OBPI-unit completeness rather than gate-only rollup.

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
