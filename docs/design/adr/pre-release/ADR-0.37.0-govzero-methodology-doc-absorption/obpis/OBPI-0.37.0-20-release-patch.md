---
id: OBPI-0.37.0-20-release-patch
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 20
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-20: release-patch

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-20 — "Compare and absorb releases/patch-release.md — patch release process"`

## OBJECTIVE

Compare `docs/governance/GovZero/releases/patch-release.md` between airlineops and gzkit. This document defines the patch release process — hotfix criteria, expedited steps, validation, and rollback procedures. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/releases/patch-release.md`
- **gzkit:** `docs/governance/GovZero/releases/patch-release.md`

## ASSUMPTIONS

- Patch release processes should be consistent across GovZero-governed projects
- Patch releases are time-sensitive — documentation must be concise and actionable
- airlineops may have operational refinements from emergency patch releases

## NON-GOALS

- Changing the patch release process
- Adding domain-specific hotfix criteria

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in hotfix criteria, steps, validation, rollback procedures
1. Evaluate which version is more complete and actionable
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-20-01: Read both versions completely
- [x] REQ-0.37.0-20-02: Document differences in hotfix criteria, steps, validation, rollback procedures
- [x] REQ-0.37.0-20-03: Evaluate which version is more complete and actionable
- [x] REQ-0.37.0-20-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/releases/patch-release.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
