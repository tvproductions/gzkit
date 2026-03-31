---
id: OBPI-0.0.10-04-tier-escalation-governance
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 4
lane: lite
status: Draft
---

# OBPI-0.0.10-04: Tier Escalation Governance

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #4 - "Enforce tier escalation governance (ADR-required for Tier C)"

**Status:** Draft

## Objective

Tier escalation (A/B to C) requires Heavy-lane ADR authorization, enforced by
documentation and review convention. The governance runbook, AGENTS.md, and ADR
review process all include explicit tier escalation checks.

## Lane

**Lite** - Documentation and governance constraint only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/governance/`
- `AGENTS.md`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI
- `.gzkit/` -- no ledger/marker changes

## Requirements (FAIL-CLOSED)

1. Governance runbook MUST state the tier escalation rule: moving data from Tier A/B to Tier C requires a Heavy-lane ADR
2. `AGENTS.md` MUST include tier escalation as a governance constraint agents must respect
3. ADR template or review checklist MUST flag tier escalation as a Heavy-lane trigger
4. The anti-pattern (silent Tier B to Tier C drift) MUST be documented as a known risk

> STOP-on-BLOCKERS: if OBPI-0.0.10-01 tier definitions are not yet available, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - current agent operating contract
- [ ] Parent ADR - understand full context, especially anti-pattern warning

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Related: OBPI-0.0.10-01 (tier definitions)
- [ ] Related: OBPI-0.0.10-03 (storage catalog)

**Prerequisites (check existence, STOP if missing):**

- [ ] `AGENTS.md` exists
- [ ] `docs/governance/governance_runbook.md` exists

**Existing Code (understand current state):**

- [ ] Current `AGENTS.md` governance constraints
- [ ] Current ADR template lane triggers

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] N/A -- documentation/governance OBPI
- [ ] Validation: `uv run mkdocs build --strict`

### Code Quality

- [ ] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify governance runbook includes tier escalation rule
# Verify AGENTS.md includes tier escalation constraint
```

## Acceptance Criteria

- [ ] REQ-0.0.10-04-01: Tier escalation rule documented in governance runbook
- [ ] REQ-0.0.10-04-02: `AGENTS.md` includes tier escalation as governance constraint
- [ ] REQ-0.0.10-04-03: ADR review checklist includes tier escalation check

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
