---
id: OBPI-0.10.0-01-obpi-runtime-contract-and-state-model
parent: ADR-0.10.0-obpi-runtime-surface
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.10.0-01-obpi-runtime-contract-and-state-model: OBPI runtime contract and state model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #1 -- "Define the OBPI runtime contract and derived state model."

**Status:** Draft

## Objective

Define the machine-readable OBPI runtime contract so status, proof, reconciliation,
and future pipeline hooks derive from one deterministic state model instead of
brief text heuristics alone.

## Lane

**Heavy** -- This unit defines lifecycle semantics consumed by operator-facing
commands and future parity hooks.

## Allowed Paths

- `src/gzkit/ledger.py` -- OBPI state derivation and graph semantics.
- `src/gzkit/commands/status.py` -- runtime status interpretation boundaries.
- `src/gzkit/schemas/ledger.json` -- ledger event/schema contract if new OBPI runtime evidence fields are required.
- `tests/` -- unit tests for OBPI state derivation and compatibility semantics.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.
- `docs/user/concepts/` and `docs/governance/GovZero/` -- runtime contract documentation if introduced.

## Denied Paths

- New external databases or network services.
- `../airlineops/**` -- canonical source remains read-only.
- Deleting or weakening existing ADR lifecycle semantics.
- CI files, lockfiles, or new dependencies unless a separate approved brief requires them.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI runtime state MUST derive from ledger and document evidence through deterministic rules.
1. REQUIREMENT: The OBPI model MUST define compatibility with existing ADR-first status, receipt, and audit flows.
1. REQUIREMENT: REQ-proof state inputs MUST be named and scoped, even if later OBPIs implement the consuming surfaces.
1. NEVER: Introduce an alternate planner/store that bypasses `.gzkit/ledger.jsonl`.
1. ALWAYS: Preserve human attestation as the authority boundary for heavy/foundation completion.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`

**Context:**

- [ ] `src/gzkit/ledger.py`
- [ ] `src/gzkit/commands/status.py`
- [ ] `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/obpis/OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/ledger.jsonl`
- [ ] `src/gzkit/schemas/ledger.json`

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
```

## Acceptance Criteria

- [ ] REQ-0.10.0-01-01: OBPI runtime lifecycle states and evidence inputs are defined deterministically.
- [ ] REQ-0.10.0-01-02: Compatibility boundaries with existing ADR-first receipt/audit behavior are explicit.
- [ ] REQ-0.10.0-01-03: Required REQ-proof inputs for later OBPI runtime surfaces are documented.

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
