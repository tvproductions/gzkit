---
id: OBPI-0.0.9-06-marker-migration-path
parent: ADR-0.0.9
item: 6
lane: lite
status: Draft
---

# OBPI-0.0.9-06: Marker Migration Path

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #6 - "Pipeline marker migration path (from L3 to L2 ledger events) is documented with clear timeline and trigger"

**Status:** Draft

## Objective

Pipeline marker migration path (from L3 to L2 ledger events) is documented
with clear timeline and trigger. After migration, markers become pure
rebuildable cache -- deletable without data loss.

## Lane

**Lite** - Documentation and governance reference only. No CLI or external contract changes.

## Allowed Paths

- `docs/governance/`
- `docs/design/`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI

## Requirements (FAIL-CLOSED)

1. Document MUST specify what stage transition events will replace markers
2. Document MUST reference Pipeline Lifecycle ADR as the vehicle for migration
3. Document MUST state that markers become pure rebuildable cache after migration
4. Document MUST include a timeline or trigger condition for when migration begins

> STOP-on-BLOCKERS: if Pipeline Lifecycle ADR does not exist, note as dependency and proceed with placeholder reference.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] OBPI-0.0.9-01 (three-layer model) for layer definitions
- [ ] Pipeline Lifecycle ADR (if it exists)

**Existing Code (understand current state):**

- [ ] `src/gzkit/pipeline_markers.py` -- current marker management
- [ ] `.gzkit/markers/` -- current marker files (if any)
- [ ] `src/gzkit/ledger_semantics.py` -- ledger event patterns

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
# Verify migration path document renders correctly
```

## Acceptance Criteria

- [ ] REQ-0.0.9-06-01: Migration path document exists
- [ ] REQ-0.0.9-06-02: Document specifies ledger event types that will replace markers
- [ ] REQ-0.0.9-06-03: Document references Pipeline Lifecycle ADR as migration vehicle

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** mkdocs build passes
- [ ] **Code Quality:** N/A
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

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
