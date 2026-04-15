---
id: OBPI-0.37.0-22-handoff-chaining
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 22
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-22: handoff-chaining

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-22 — "Compare and absorb handoff-chaining.md — handoff chain documentation"`

## OBJECTIVE

Compare `docs/governance/GovZero/handoff-chaining.md` between airlineops and gzkit. This document defines how session handoffs chain together to form a continuous governance narrative across multiple agent sessions. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/handoff-chaining.md`
- **gzkit:** `docs/governance/GovZero/handoff-chaining.md`

## ASSUMPTIONS

- Handoff chaining is critical for long-running governance work (multi-session ADRs)
- Both repos should describe the same chaining mechanism
- gzkit's version should reflect the tooling's actual chaining behavior

## NON-GOALS

- Changing the handoff chaining mechanism
- Adding domain-specific chaining rules

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in chaining rules, linkage mechanisms, chain validation
1. Evaluate which version is more complete and matches the implementation
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-22-01: Read both versions completely
- [x] REQ-0.37.0-22-02: Document differences in chaining rules, linkage mechanisms, chain validation
- [x] REQ-0.37.0-22-03: Evaluate which version is more complete and matches the implementation
- [x] REQ-0.37.0-22-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/handoff-chaining.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
