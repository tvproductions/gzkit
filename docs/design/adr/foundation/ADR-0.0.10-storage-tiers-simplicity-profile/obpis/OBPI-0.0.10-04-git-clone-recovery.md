---
id: OBPI-0.0.10-04-git-clone-recovery
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 4
lane: lite
status: Draft
---

# OBPI-0.0.10-04: Git Clone Recovery

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #4 - "Validate git-clone recovery (all Tier A + B state survives)"

**Status:** Draft

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

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Related: OBPI-0.0.10-03 (storage catalog identifies what must survive)

**Prerequisites (check existence, STOP if missing):**

- [ ] `uv run gz state` command exists and works
- [ ] Git repository initialized with committed Tier A artifacts

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/` -- understand `gz state` implementation
- [ ] Test patterns: `tests/` for existing integration-style tests

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
uv run -m unittest tests.adr.test_storage_tiers -v
```

## Acceptance Criteria

- [ ] REQ-0.0.10-04-01: Test performs fresh clone and verifies `gz state` succeeds
- [ ] REQ-0.0.10-04-02: All Tier A artifacts present after clone
- [ ] REQ-0.0.10-04-03: Tier B artifacts rebuild from Tier A sources

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
