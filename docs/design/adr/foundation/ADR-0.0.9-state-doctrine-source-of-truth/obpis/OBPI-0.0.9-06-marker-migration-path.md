---
id: OBPI-0.0.9-06-marker-migration-path
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 6
lane: lite
status: in_progress
---

# OBPI-0.0.9-06: Marker Migration Path

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #6 - "Pipeline marker migration path (from L3 to L2 ledger events) is documented with clear timeline and trigger"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [x] OBPI-0.0.9-01 (three-layer model) for layer definitions
- [x] Pipeline Lifecycle ADR (if it exists)

**Existing Code (understand current state):**

- [x] `src/gzkit/pipeline_markers.py` -- current marker management
- [x] `.gzkit/markers/` -- current marker files (if any)
- [x] `src/gzkit/ledger_semantics.py` -- ledger event patterns

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] N/A -- documentation-only OBPI
- [x] Validation: `uv run mkdocs build --strict`

### Code Quality

- [x] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify migration path document renders correctly
```

## Acceptance Criteria

- [x] REQ-0.0.9-06-01: Migration path document exists
- [x] REQ-0.0.9-06-02: Document specifies ledger event types that will replace markers
- [x] REQ-0.0.9-06-03: Document references Pipeline Lifecycle ADR as migration vehicle

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** mkdocs build passes
- [x] **Code Quality:** N/A
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
INFO - Documentation built in 1.13 seconds (mkdocs build --strict, zero warnings)
```

### Value Narrative

Before this OBPI, pipeline markers existed as Layer 3 artifacts with no documented path for migrating their state into Layer 2 ledger events. Operators and agents had no reference for what ledger event types would replace markers, when migration would begin, or what the end-state looks like. Now `docs/governance/pipeline-marker-migration-path.md` provides a complete migration roadmap — event types, phased timeline, trigger conditions, and verification steps.

### Key Proof

```bash
uv run mkdocs build --strict
# INFO - Documentation built in 1.13 seconds
# pipeline-marker-migration-path.md renders at governance/pipeline-marker-migration-path/
# Document defines 7 pipeline-* ledger event types, references ADR-0.13.0 as vehicle
```

### Implementation Summary

- Files created: `docs/governance/pipeline-marker-migration-path.md`
- Files modified: `mkdocs.yml`
- Tests added: N/A (documentation-only)
- Date completed: 2026-03-31
- Attestation status: Human-attested
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
