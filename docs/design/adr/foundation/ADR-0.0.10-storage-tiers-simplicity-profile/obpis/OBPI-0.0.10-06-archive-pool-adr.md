---
id: OBPI-0.0.10-06-archive-pool-adr
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 6
lane: lite
status: Draft
---

# OBPI-0.0.10-06: Archive Pool ADR

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #6 - "Archive pool ADR with forwarding note"

**Status:** Draft

## Objective

Pool ADR `storage-simplicity-profile` is archived with forwarding note pointing to
ADR-0.0.10. The pool ADR's YAML frontmatter is updated with archived status, and a
visible forwarding note directs readers to the promoted foundation ADR.

## Lane

**Lite** - Pool ADR metadata update only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI
- `.gzkit/` -- no ledger/marker changes
- `AGENTS.md` -- no governance contract changes

## Requirements (FAIL-CLOSED)

1. Pool ADR MUST have YAML frontmatter updated with `status: archived`, `superseded_by: ADR-0.0.10`, and `archived_date: 2026-03-29`
2. Pool ADR MUST have a visible forwarding note at the top of the document body (below frontmatter)
3. Forwarding note MUST reference ADR-0.0.10 with its full path
4. No broken references to the pool ADR MUST remain in other documents

> STOP-on-BLOCKERS: if `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md` does not exist, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Pool ADR: `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Pool ADR file exists at `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

**Existing Code (understand current state):**

- [ ] Current pool ADR content and frontmatter
- [ ] References to pool ADR in other documents (grep for filename)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] N/A -- metadata/documentation OBPI
- [ ] Validation: verify frontmatter contains required fields

### Code Quality

- [ ] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify pool ADR frontmatter has status: archived
# Verify forwarding note is visible
# Grep for broken references to pool ADR
```

## Acceptance Criteria

- [ ] REQ-0.0.10-06-01: Pool ADR frontmatter has `status: archived` and `superseded_by: ADR-0.0.10`
- [ ] REQ-0.0.10-06-02: Forwarding note visible at top of pool ADR document
- [ ] REQ-0.0.10-06-03: No broken references to pool ADR in other documents

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Frontmatter and forwarding note verified
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
# Paste verification output here
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
