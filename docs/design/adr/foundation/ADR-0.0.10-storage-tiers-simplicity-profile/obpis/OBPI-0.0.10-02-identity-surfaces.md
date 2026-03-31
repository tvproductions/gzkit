---
id: OBPI-0.0.10-02-identity-surfaces
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 2
lane: lite
status: Completed
---

# OBPI-0.0.10-02: Identity Surfaces

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #2 - "Define five identity surfaces with ID schemes and portability rules"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [x] Related: OBPI-0.0.10-01 (tier definitions inform surface boundaries)

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/core/models.py` exists
- [x] Existing identity patterns in models.py

**Existing Code (understand current state):**

- [x] Current models in `src/gzkit/core/models.py`
- [x] Test patterns: `tests/` for existing model tests

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest -q

# Specific verification for this OBPI
uv run -m unittest tests.test_identity_surfaces -v
```

## Acceptance Criteria

- [x] REQ-0.0.10-02-01: Five identity surface ID formats are documented
- [x] REQ-0.0.10-02-02: Pydantic models exist in `core/models.py` for all five surfaces
- [x] REQ-0.0.10-02-03: Test verifies ID portability (same ID format across all tiers)

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_identity_surfaces -v
Ran 37 tests in 0.001s
OK
```

### Code Quality

```text
uv run gz lint    → All checks passed
uv run gz typecheck → All checks passed
uv run gz test    → 2254 tests pass (18s)
```

### Value Narrative

Before this OBPI, gzkit's five identity surfaces existed only as informal conventions — mentioned in docs but without validated Pydantic models or a formal portability guarantee. Now, all five have frozen, extra-forbid identity models in `core/models.py` with documented regex patterns and a lossless parse/str round-trip contract.

### Key Proof

```bash
uv run -m unittest tests.test_identity_surfaces.TestTierPortability -v
```
```text
test_adr_portable ... ok
test_all_surfaces_roundtrip — Every surface ID round-trips through parse -> str. ... ok
test_ev_portable ... ok
test_obpi_portable ... ok
test_req_portable ... ok
test_task_portable ... ok
Ran 6 tests in 0.001s — OK
```

### Implementation Summary

- Files created: `tests/test_identity_surfaces.py` (37 tests)
- Files modified: `src/gzkit/core/models.py` (AdrId, ObpiId, ReqId, TaskId, EvidenceId + IDENTITY_MODELS), `docs/governance/storage-tiers.md` (ID format specs, model contract, portability guarantee)
- Tests added: 37 (parse, roundtrip, whitespace, frozen, extra-forbid, portability, mapping, config)
- Date completed: 2026-03-31
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-03-31`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-31

**Evidence Hash:** -
