---
id: OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces
parent: ADR-0.10.0-obpi-runtime-surface
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces: OBPI query and reconcile command surfaces

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #2 -- "Deliver OBPI-native query and reconcile command surfaces."

**Status:** Draft

## Objective

Deliver first-class `gz obpi ...` query and reconcile surfaces so operators can
inspect OBPI status and drift directly at OBPI scope without relying on ADR-only
status views or manual brief review.

## Lane

**Heavy** -- This unit adds or changes user-facing CLI behavior.

## Allowed Paths

- `src/gzkit/cli.py` -- command registration and operator output.
- `src/gzkit/commands/` -- OBPI query/reconcile implementations.
- `src/gzkit/ledger.py` -- derived read models used by command surfaces.
- `tests/commands/` and `tests/` -- command/runtime verification.
- `docs/user/commands/` -- new or updated command docs.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.

## Denied Paths

- Replacing or removing `gz adr status` semantics instead of adding OBPI-native parity.
- New dependencies without a separate approved rationale.
- `../airlineops/**` canonical mutations.
- CI files and lockfiles unrelated to the in-scope command surface.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI query surfaces MUST support deterministic human-readable and JSON output.
1. REQUIREMENT: Reconcile behavior MUST identify missing ledger proof, missing brief evidence, and state drift fail-closed.
1. REQUIREMENT: Existing `gz obpi emit-receipt` and `gz obpi validate` flows MUST remain compatible.
1. NEVER: Hide drift by silently inferring completion when required proof is missing.
1. ALWAYS: Prefer OBPI-native identifiers and command outputs over ADR-only indirection when reporting OBPI state.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [ ] `docs/user/commands/obpi-emit-receipt.md`

**Context:**

- [ ] `src/gzkit/cli.py`
- [ ] `src/gzkit/commands/status.py`
- [ ] `tests/commands/test_status.py`
- [ ] `tests/test_obpi_validator.py`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI runtime contract from OBPI-0.10.0-01 is accepted or stubbed with explicit assumptions
- [ ] Existing `gz obpi` command group exists

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
uv run gz obpi validate <path-to-obpi-brief>
```

## Acceptance Criteria

- [ ] REQ-0.10.0-02-01: OBPI-native query surfaces render deterministic state at OBPI granularity.
- [ ] REQ-0.10.0-02-02: Reconcile output reports proof/evidence drift explicitly and fail-closed.
- [ ] REQ-0.10.0-02-03: Existing receipt and validation command surfaces remain compatible.

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
