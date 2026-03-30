---
id: OBPI-0.0.10-01-three-tier-model-documentation
parent: ADR-0.0.10
item: 1
lane: lite
status: Draft
---

# OBPI-0.0.10-01: Three-Tier Model Documentation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #1 - "Document three-tier model with authority boundaries"

**Status:** Draft

## Objective

A reference document defines Tier A (canonical), Tier B (derived/rebuildable), and
Tier C (external/ADR-required) with authority boundaries. Operators and agents can
reference this document to determine where data belongs and what governance rules apply.

## Lane

**Lite** - Documentation and governance reference only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/governance/`
- `docs/design/`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI
- `.gzkit/` -- no ledger/marker changes

## Requirements (FAIL-CLOSED)

1. Document MUST define all three tiers (A, B, C) with concrete examples from the gzkit repo
2. Document MUST state the authority boundary for each tier (who/what can create, modify, delete)
3. Document MUST be linked from `docs/governance/governance_runbook.md`
4. Tier definitions MUST be consistent with ADR-0.0.10 Decision section

> STOP-on-BLOCKERS: if ADR-0.0.10 Decision section is incomplete, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Pool ADR: `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/governance_runbook.md` exists for linking

**Existing Code (understand current state):**

- [ ] Current governance docs structure in `docs/governance/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] N/A -- documentation-only OBPI
- [ ] Validation: `uv run mkdocs build --strict`

### Code Quality

- [ ] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify storage-tiers.md renders correctly
# Verify governance_runbook.md links to storage tier reference
```

## Acceptance Criteria

- [ ] REQ-0.0.10-01-01: Storage tier reference document exists in `docs/governance/`
- [ ] REQ-0.0.10-01-02: Each tier has definition, examples, and authority boundary
- [ ] REQ-0.0.10-01-03: Governance runbook links to storage tier reference

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** mkdocs build passes
- [ ] **Code Quality:** N/A
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste mkdocs build output here
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
