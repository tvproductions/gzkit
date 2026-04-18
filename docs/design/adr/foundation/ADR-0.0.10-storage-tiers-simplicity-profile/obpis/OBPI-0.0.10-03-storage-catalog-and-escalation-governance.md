---
id: OBPI-0.0.10-03-storage-catalog-and-escalation-governance
parent: ADR-0.0.10-storage-tiers-simplicity-profile
item: 3
lane: lite
status: in_progress
---

# OBPI-0.0.10-03: Storage Catalog and Tier Escalation Governance

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md`
- **Checklist Items:** #3 - "Catalog storage locations and enforce tier escalation governance"

**Status:** Completed

## Objective

All on-disk storage locations are cataloged and classified as Tier A, B, or C.
Pipeline markers and other undocumented Tier B items are explicitly listed. No
storage location remains unclassified.

Tier escalation (A/B to C) requires Heavy-lane ADR authorization, enforced by
documentation and review convention. The governance runbook, AGENTS.md, and ADR
review process all include explicit tier escalation checks.

## Lane

**Lite** - Documentation, catalog, and governance constraint only. No CLI or external contract changes.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/governance/`
- `.gzkit/`
- `AGENTS.md`

## Denied Paths

- `src/gzkit/` -- no code changes in this OBPI
- `tests/` -- no test changes in this OBPI

## Requirements (FAIL-CLOSED)

1. Catalog MUST list every storage location in the repository
2. Each location MUST have an explicit tier classification (A, B, or C)
3. Undocumented Tier B items (pipeline markers in `.gzkit/markers/`) MUST be explicitly listed
4. Catalog MUST include the rebuild/recovery path for each Tier B item
5. No unclassified storage locations MUST remain after this OBPI
6. Governance runbook MUST state the tier escalation rule: moving data from Tier A/B to Tier C requires a Heavy-lane ADR
7. `AGENTS.md` MUST include tier escalation as a governance constraint agents must respect
8. ADR template or review checklist MUST flag tier escalation as a Heavy-lane trigger
9. The anti-pattern (silent Tier B to Tier C drift) MUST be documented as a known risk

> STOP-on-BLOCKERS: if OBPI-0.0.10-01 tier definitions are not yet available, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - current agent operating contract
- [x] Parent ADR - understand full context, especially anti-pattern warning

**Context:**

- [x] Parent ADR: `ADR-0.0.10-storage-tiers-simplicity-profile.md`
- [x] Related: OBPI-0.0.10-01 (tier definitions required for classification)

**Prerequisites (check existence, STOP if missing):**

- [x] Tier definitions from OBPI-0.0.10-01 (or ADR Decision section)
- [x] `.gzkit/` directory exists with known contents
- [x] `AGENTS.md` exists
- [x] `docs/governance/governance_runbook.md` exists

**Existing Code (understand current state):**

- [x] `.gzkit/` directory contents
- [x] `config/` directory contents
- [x] `docs/` directory structure
- [x] `src/gzkit/` directory structure
- [x] Current `AGENTS.md` governance constraints
- [x] Current ADR template lane triggers

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] N/A -- documentation/catalog/governance OBPI
- [x] Validation: `uv run mkdocs build --strict`

### Code Quality

- [x] N/A -- no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify storage catalog renders correctly
# Verify all known storage locations are classified
# Verify governance runbook includes tier escalation rule
# Verify AGENTS.md includes tier escalation constraint
```

## Acceptance Criteria

- [x] REQ-0.0.10-03-01: Storage catalog document exists with all locations classified
- [x] REQ-0.0.10-03-02: Pipeline markers (`.gzkit/markers/`) listed as Tier B
- [x] REQ-0.0.10-03-03: No unclassified storage locations remain
- [x] REQ-0.0.10-03-04: Tier escalation rule documented in governance runbook
- [x] REQ-0.0.10-03-05: `AGENTS.md` includes tier escalation as governance constraint
- [x] REQ-0.0.10-03-06: ADR review checklist includes tier escalation check

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Catalog completeness and governance constraints verified
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
uv run mkdocs build --strict → pass (1.08s)
uv run gz lint → pass
uv run gz typecheck → pass
uv run gz test → 2254 tests pass
```

### Value Narrative

Before this OBPI, the storage tiers reference listed only "examples" — several on-disk
locations were unclassified and no governance surface enforced tier escalation awareness.
Now every storage location is cataloged and classified, tier escalation is a documented
constraint in both the governance runbook and AGENTS.md, and ADR review checklists flag
tier escalation as a check item.

### Key Proof

```bash
$ grep "Storage Catalog (exhaustive)" docs/governance/storage-tiers.md
**Storage Catalog (exhaustive):**
**Storage Catalog (exhaustive):**

$ grep "Tier C storage" AGENTS.md
5. Introduce Tier C storage dependencies without a Heavy-lane ADR ...
```

### Implementation Summary

- Files created: none
- Files modified: `docs/governance/storage-tiers.md`, `docs/governance/governance_runbook.md`, `AGENTS.md`
- Tests added: none (docs-only OBPI)
- Date completed: 2026-03-31
- Attestation status: Human attested
- Defects noted: none

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
