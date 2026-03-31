---
id: OBPI-0.0.10-04-git-clone-recovery
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 4
lane: lite
status: Completed
---

# OBPI-0.0.10-04: Git Clone Recovery

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #4 - "Validate git-clone recovery (all Tier A + B state survives)"

**Status:** Completed

## Objective

Verify that all Tier A + Tier B state survives a git clone from scratch. A test
clones the repo into a temp directory, runs `gz state`, and confirms all entities
resolve. Tier B items rebuild without manual intervention.

## Lane

**Lite** - Test and documentation only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `tests/`
- `docs/`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `.gzkit/` -- no ledger/marker changes
- `AGENTS.md` -- no governance contract changes

## Requirements (FAIL-CLOSED)

1. Test MUST clone the repo into a temp directory (using `tempfile.TemporaryDirectory`)
2. Test MUST run `gz state` in the cloned directory and verify success (exit code 0)
3. All Tier A artifacts MUST be present after clone (ledger, ADR markdown, config)
4. Tier B artifacts MUST rebuild from Tier A sources without manual intervention
5. Test MUST NOT require network access beyond the initial clone (use local bare repo if possible)

> STOP-on-BLOCKERS: if git repo is not initialized or `gz state` command does not exist, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [x] Related: OBPI-0.0.10-03 (storage catalog identifies what must survive)

**Prerequisites (check existence, STOP if missing):**

- [x] `uv run gz state` command exists and works
- [x] Git repository initialized with committed Tier A artifacts

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/` -- understand `gz state` implementation
- [x] Test patterns: `tests/` for existing integration-style tests

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
uv run -m unittest tests.adr.test_storage_tiers -v
```

## Acceptance Criteria

- [x] REQ-0.0.10-04-01: Test performs fresh clone and verifies `gz state` succeeds
- [x] REQ-0.0.10-04-02: All Tier A artifacts present after clone
- [x] REQ-0.0.10-04-03: Tier B artifacts rebuild from Tier A sources

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
test_tier_a_artifacts_present_after_clone ... ok
test_tier_b_rebuild_and_gz_state ... ok
Ran 2 tests in 11.524s — OK
```

### Code Quality

```text
Lint: All checks passed!
Typecheck: All checks passed!
Tests: 2258 pass
```

### Implementation Summary

- Files created: `tests/adr/test_storage_tiers.py`
- Tests added: `test_tier_a_artifacts_present_after_clone`, `test_tier_b_rebuild_and_gz_state`
- Date completed: 2026-03-31
- Attestation status: human attested
- Defects noted: none

### Key Proof

```bash
uv run -m unittest tests.adr.test_storage_tiers -v
```

```text
test_tier_a_artifacts_present_after_clone ... ok
test_tier_b_rebuild_and_gz_state ... ok
Ran 2 tests in 11.524s — OK
```

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
