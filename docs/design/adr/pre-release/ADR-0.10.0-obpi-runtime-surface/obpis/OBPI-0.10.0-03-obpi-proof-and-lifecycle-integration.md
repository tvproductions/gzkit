---
id: OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration
parent: ADR-0.10.0-obpi-runtime-surface
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration: OBPI proof and lifecycle integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #3 -- "Integrate OBPI proof state with lifecycle guidance and parity-dependent operator flows."

**Status:** Draft

## Objective

Integrate OBPI runtime state with REQ proof, closeout guidance, and parity-driven
operator flows so future AirlineOps pipeline imports target a stable gzkit-native
lifecycle surface instead of bespoke manual routines.

## Lane

**Heavy** -- This unit changes lifecycle guidance, proof semantics, and operator-facing closeout behavior.

## Allowed Paths

- `src/gzkit/commands/` -- closeout/status/gate surfaces that consume OBPI proof state.
- `src/gzkit/hooks/` -- parity-dependent hook/runtime integration points if in scope.
- `src/gzkit/ledger.py` and related proof consumers.
- `tests/` and `features/` -- lifecycle verification and BDD coverage.
- `docs/user/commands/`, `docs/user/concepts/`, `docs/governance/GovZero/` -- operator and governance docs.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.

## Denied Paths

- Importing deferred AirlineOps pipeline hooks without compatible gzkit runtime support.
- Weakening heavy-lane attestation or receipt evidence requirements.
- Introducing hidden LLM-only lifecycle inference where deterministic proof is available.
- New dependencies or CI changes unrelated to lifecycle integration.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI proof state MUST be visible in lifecycle/closeout surfaces through deterministic command output.
1. REQUIREMENT: REQ linkage and proof gaps MUST surface as explicit drift or pending state, not implicit success.
1. REQUIREMENT: Operator docs MUST describe the OBPI-native flow coherently from verification through attestation and receipts.
1. NEVER: Mark or imply heavy-lane completion before explicit human attestation.
1. ALWAYS: Preserve compatibility with current receipt semantics while preparing clear integration seams for deferred AirlineOps parity hooks.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [ ] `docs/governance/GovZero/validation-receipts.md`

**Context:**

- [ ] `src/gzkit/hooks/core.py`
- [ ] `src/gzkit/commands/status.py`
- [ ] `src/gzkit/commands/attest.py`
- [ ] `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI runtime contract and command surfaces from OBPI-0.10.0-01 and OBPI-0.10.0-02 are defined
- [ ] REQ-proof linkage strategy is accepted or explicitly stubbed

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Coverage maintained: `uv run coverage run -m unittest discover tests && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Format clean: `uv run gz format`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz test
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/
uv run gz status
uv run gz closeout <adr-id> --dry-run
```

## Acceptance Criteria

- [ ] REQ-0.10.0-03-01: Lifecycle/closeout surfaces report OBPI proof state deterministically.
- [ ] REQ-0.10.0-03-02: REQ-proof gaps surface as explicit pending or drift state.
- [ ] REQ-0.10.0-03-03: Operator docs describe an OBPI-native verification -> attestation -> receipt flow.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
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
