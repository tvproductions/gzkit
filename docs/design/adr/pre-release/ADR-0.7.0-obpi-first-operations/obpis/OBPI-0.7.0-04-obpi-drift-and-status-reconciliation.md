---
id: OBPI-0.7.0-04-obpi-drift-and-status-reconciliation
parent: ADR-0.7.0-obpi-first-operations
item: 4
lane: Heavy
status: attested_completed
---

# OBPI-0.7.0-04-obpi-drift-and-status-reconciliation: Obpi Drift And Status Reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #4 — "Add OBPI drift/status reconciliation reporting."

**Status:** Completed

## Objective

Expose OBPI completion drift and reconciliation signals in status/audit surfaces so operators can see when completed OBPI state has diverged from recorded evidence.

### Implementation Summary

- Files modified: `src/gzkit/commands/status.py` (added DRIFT detection and reporting), `src/gzkit/ledger.py` (added ledger-first completion tracking).
- Date completed: 2026-03-04

### Value Narrative

Before this OBPI, operators had no way to see when a completed OBPI's evidence had diverged from the recorded ledger state. After this OBPI, the status command detects and reports drift between file-claimed completion and ledger proof, enabling targeted reconciliation instead of opaque ADR-level claims.

### Key Proof

```bash
# Status command now detects and reports drift:
uv run gz adr status ADR-0.7.0-obpi-first-operations
# Output: OBPI-0.7.0-04: [red]DRIFT[/red] (file says Completed, ledger proof missing)
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Confirmed status reporting correctly identifies divergence between ledger and local files."
- Date: 2026-03-04

## Lane

**Heavy** — This affects operator-visible governance reporting and closeout quality signals.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/cli.py` — status and reconciliation rendering
- `src/gzkit/ledger.py` — OBPI lifecycle signal derivation
- `docs/user/commands/**` — status/audit documentation
- `tests/**` — status/audit regression coverage

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Status surfaces MUST report OBPI unit completion and outstanding items deterministically.
1. REQUIREMENT: Reconciliation output MUST separate complete, missing, and drifted OBPI evidence states.
1. NEVER: Never collapse OBPI drift into opaque ADR-only summary claims.
1. ALWAYS: Reporting must preserve OBPI identifiers for remediation targeting.

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

- [ ] Pattern to follow: `src/gzkit/cli.py` (`status`, `adr_status_cmd`)
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

# Status/reconciliation behavior
uv run gz status --json
uv run gz adr status ADR-0.7.0-obpi-first-operations --json
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [x] REQ-0.7.0-04-01: Status output reports OBPI-unit completion and open items correctly.
- [x] REQ-0.7.0-04-02: Reconciliation distinguishes missing proof from drifted proof states.
- [x] REQ-0.7.0-04-03: Tests validate OBPI-centric reporting behavior.

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

**Brief Status:** Completed

**Date Completed:** —

**Evidence Hash:** —
