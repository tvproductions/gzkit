---
id: OBPI-0.0.10-03-storage-location-catalog
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 3
lane: lite
status: Draft
---

# OBPI-0.0.10-03: Storage Location Catalog

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Item:** #3 - "Catalog and classify all on-disk storage locations"

**Status:** Draft

## Objective

All on-disk storage locations are cataloged and classified as Tier A, B, or C.
Pipeline markers and other undocumented Tier B items are explicitly listed. No
storage location remains unclassified.

## Lane

**Lite** - Documentation and catalog only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/governance/`
- `.gzkit/`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI

## Requirements (FAIL-CLOSED)

1. Catalog MUST list every storage location in the repository
2. Each location MUST have an explicit tier classification (A, B, or C)
3. Undocumented Tier B items (pipeline markers in `.gzkit/markers/`) MUST be explicitly listed
4. Catalog MUST include the rebuild/recovery path for each Tier B item
5. No unclassified storage locations MUST remain after this OBPI

> STOP-on-BLOCKERS: if OBPI-0.0.10-01 tier definitions are not yet available, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [ ] Related: OBPI-0.0.10-01 (tier definitions required for classification)

**Prerequisites (check existence, STOP if missing):**

- [ ] Tier definitions from OBPI-0.0.10-01 (or ADR Decision section)
- [ ] `.gzkit/` directory exists with known contents

**Existing Code (understand current state):**

- [ ] `.gzkit/` directory contents
- [ ] `config/` directory contents
- [ ] `docs/` directory structure
- [ ] `src/gzkit/` directory structure

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] N/A -- documentation/catalog OBPI
- [ ] Validation: catalog completeness verified by manual inspection

### Code Quality

- [ ] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify storage catalog renders correctly
# Verify all known storage locations are classified
```

## Acceptance Criteria

- [ ] REQ-0.0.10-03-01: Storage catalog document exists with all locations classified
- [ ] REQ-0.0.10-03-02: Pipeline markers (`.gzkit/markers/`) listed as Tier B
- [ ] REQ-0.0.10-03-03: No unclassified storage locations remain

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Catalog completeness verified
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
# Paste catalog verification output here
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
