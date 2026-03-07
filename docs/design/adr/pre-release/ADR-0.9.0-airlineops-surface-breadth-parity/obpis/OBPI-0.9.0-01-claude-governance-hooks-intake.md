---
id: OBPI-0.9.0-01-claude-governance-hooks-intake
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.9.0-01-claude-governance-hooks-intake: Canonical .claude hooks governance tranche

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #1 — "Execute OBPI-0.9.0-01: import non-blocking `.claude/hooks` tranche with settings wiring and evidence."

**Status:** Draft

## Objective

Import a governance-safe first tranche of canonical `.claude/hooks` (non-blocking)
into gzkit and wire those hooks in `.claude/settings.json` with path-level parity
evidence and explicit deferrals for blocking/product-coupled hooks.

## Lane

**Heavy** — This changes operator control surfaces and must preserve governance
integrity while preventing product-capability leakage.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.claude/hooks/**` — Hook parity tranche import
- `.claude/settings.json` — Hook wiring
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` — OBPI and intake evidence

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/**` and `tests/**` — no runtime feature changes in this tranche
- `docs/design/adr/pool/**` except parent promotion pointer updates
- `../airlineops/**` (read-only canonical source)
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Import only non-blocking canonical hooks in this tranche.
1. REQUIREMENT: `.claude/settings.json` MUST keep `ledger-writer.py` active.
1. REQUIREMENT: A path-level intake matrix MUST classify all canonical `.claude/hooks` files.
1. NEVER: Do not import product-specific guard logic in this tranche.
1. NEVER: Do not enable blocking hooks until compatibility adaptation is documented.
1. ALWAYS: For every deferred hook, record reason and follow-up target OBPI.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical hooks source exists: `../airlineops/.claude/hooks/`
- [ ] Claude settings exists: `.claude/settings.json`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `.claude/hooks/ledger-writer.py`
- [ ] Pattern to follow: `../airlineops/.claude/hooks/instruction-router.py`

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
uv run gz check-config-paths
uv run gz cli audit
uv run mkdocs build --strict
uv run gz adr status ADR-0.9.0 --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.9.0-01-01: Given canonical `.claude/hooks` contains non-blocking governance hooks, when OBPI-01 completes, then gzkit contains imported `instruction-router.py` and `post-edit-ruff.py`.
- [ ] REQ-0.9.0-01-02: Given gzkit Claude settings, when hooks are wired, then `instruction-router.py`, `post-edit-ruff.py`, and `ledger-writer.py` are configured in `.claude/settings.json`.
- [ ] REQ-0.9.0-01-03: Given remaining canonical hooks are not imported, when intake evidence is reviewed, then each hook is classified with explicit defer/exclude rationale and follow-up.

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

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
uv run -m unittest discover tests
Ran 286 tests in 2.637s
OK
```

### Code Quality

```text
# Paste lint/format/type check output here
uv run gz check-config-paths
Config-path audit passed.

uv run gz cli audit
CLI audit passed.
```

### Implementation Summary

- Files created/modified:
  - `.claude/hooks/instruction-router.py`
  - `.claude/hooks/post-edit-ruff.py`
  - `.claude/hooks/README.md`
  - `.claude/settings.json`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- Tests added: none
- Date updated: 2026-03-06

---

**Brief Status:** In Progress

**Date Completed:** —

**Evidence Hash:** —
