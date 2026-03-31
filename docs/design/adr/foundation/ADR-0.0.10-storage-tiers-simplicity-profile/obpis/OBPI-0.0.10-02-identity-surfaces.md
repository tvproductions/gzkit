---
id: OBPI-0.0.10-02-identity-surfaces
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 2
lane: lite
status: Draft
---

# OBPI-0.0.10-02: Identity Surfaces

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #2 - "Define five identity surfaces with ID schemes and portability rules"

**Status:** Draft

## Objective

Five identity surfaces (ADR-*, OBPI-*, REQ-*, TASK-*, EV-*) have documented ID
schemes and portability rules. Pydantic models exist for all five surfaces in
`core/models.py`, and IDs are portable across all storage tiers without translation.

## Lane

**Lite** - Model additions and documentation. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/core/models.py`
- `docs/governance/`
- `tests/`

## Denied Paths

- `src/gzkit/commands/` -- no CLI changes
- `.gzkit/` -- no ledger/marker changes

## Requirements (FAIL-CLOSED)

1. Each identity surface MUST have a defined ID format documented in governance docs
2. IDs MUST be tier-portable (same format in Tier A markdown, Tier B indexes, and hypothetical Tier C stores)
3. Pydantic models MUST exist in `core/models.py` for all five surfaces (ADR, OBPI, REQ, TASK, EV)
4. Models MUST use `ConfigDict(frozen=True, extra="forbid")` per data model policy
5. Test MUST verify ID portability (same ID format parses identically regardless of tier context)

> STOP-on-BLOCKERS: if `src/gzkit/core/models.py` does not exist, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Related: OBPI-0.0.10-01 (tier definitions inform surface boundaries)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/core/models.py` exists
- [ ] Existing identity patterns in models.py

**Existing Code (understand current state):**

- [ ] Current models in `src/gzkit/core/models.py`
- [ ] Test patterns: `tests/` for existing model tests

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest -q

# Specific verification for this OBPI
uv run -m unittest tests.test_identity_surfaces -v
```

## Acceptance Criteria

- [ ] REQ-0.0.10-02-01: Five identity surface ID formats are documented
- [ ] REQ-0.0.10-02-02: Pydantic models exist in `core/models.py` for all five surfaces
- [ ] REQ-0.0.10-02-03: Test verifies ID portability (same ID format across all tiers)

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

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

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
