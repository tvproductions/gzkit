---
id: OBPI-0.0.10-01-three-tier-model-and-pool-archive
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 1
lane: lite
status: attested_completed
---

# OBPI-0.0.10-01: Three-Tier Model Documentation and Pool ADR Archive

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Items:** #1 - "Document three-tier model and archive pool ADR"

**Status:** Completed

## Objective

A reference document defines Tier A (canonical), Tier B (derived/rebuildable), and
Tier C (external/ADR-required) with authority boundaries. Operators and agents can
reference this document to determine where data belongs and what governance rules apply.

Pool ADR `storage-simplicity-profile` is archived with a forwarding note pointing to
ADR-0.0.10, completing the promotion lifecycle.

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
5. Pool ADR MUST have YAML frontmatter updated with `status: archived`, `superseded_by: ADR-0.0.10`, and `archived_date: 2026-03-29`
6. Pool ADR MUST have a visible forwarding note at the top of the document body (below frontmatter)
7. Forwarding note MUST reference ADR-0.0.10 with its full path
8. No broken references to the pool ADR MUST remain in other documents

> STOP-on-BLOCKERS: if ADR-0.0.10 Decision section is incomplete, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [x] Pool ADR: `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

**Prerequisites (check existence, STOP if missing):**

- [x] `docs/governance/governance_runbook.md` exists for linking
- [x] Pool ADR file exists at `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

**Existing Code (understand current state):**

- [x] Current governance docs structure in `docs/governance/`
- [x] Current pool ADR content and frontmatter
- [x] References to pool ADR in other documents (grep for filename)

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
# Verify storage-tiers.md renders correctly
# Verify governance_runbook.md links to storage tier reference
# Verify pool ADR frontmatter has status: archived
# Verify forwarding note is visible
# Grep for broken references to pool ADR
```

## Acceptance Criteria

- [x] REQ-0.0.10-01-01: Storage tier reference document exists in `docs/governance/`
- [x] REQ-0.0.10-01-02: Each tier has definition, examples, and authority boundary
- [x] REQ-0.0.10-01-03: Governance runbook links to storage tier reference
- [x] REQ-0.0.10-01-04: Pool ADR frontmatter has `status: archived` and `superseded_by: ADR-0.0.10`
- [x] REQ-0.0.10-01-05: Forwarding note visible at top of pool ADR document
- [x] REQ-0.0.10-01-06: No broken references to pool ADR in other documents

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** mkdocs build passes
- [x] **Code Quality:** N/A
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run mkdocs build --strict
INFO - Documentation built in 1.08 seconds
```

### Implementation Summary

- Files created: `docs/governance/storage-tiers.md`
- Files modified: `mkdocs.yml`, `docs/governance/governance_runbook.md`
- Tests added: N/A (documentation-only)
- Date completed: 2026-03-31
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```bash
$ uv run mkdocs build --strict
# Exits 0 — storage-tiers.md renders in doc site under Governance nav
# governance_runbook.md Reference Links section includes storage tier link
# Pool ADR forwarding note visible at line 13
```

### Value Narrative

Before this OBPI, gzkit had no reference document explaining the three-tier storage model. Operators and agents had to read the full ADR-0.0.10 Decision section to understand where data belongs and what governance rules apply. Now a dedicated storage-tiers.md provides a quick-reference with tier definitions, concrete gzkit examples, authority boundaries, escalation governance, and anti-patterns — linked from the governance runbook and mkdocs nav.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `Completed`
- Date: `2026-03-31`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-31

**Evidence Hash:** -
