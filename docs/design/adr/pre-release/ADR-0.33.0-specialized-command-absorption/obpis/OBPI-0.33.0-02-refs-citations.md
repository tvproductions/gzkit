---
id: OBPI-0.33.0-02-refs-citations
parent: ADR-0.33.0-specialized-command-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-02: refs-citations

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-02 -- "Evaluate and absorb refs-citations (37+797 lines) -- citation checking and validation"`

## OBJECTIVE

Evaluate opsdev's `refs-citations` command (37 lines CLI + 797 lines shared library) for absorption into gzkit. The refs-citations command validates that all citations in governance documents resolve to valid references -- ensuring no broken links, missing ADR references, or dangling OBPI citations. Determine whether citation validation is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** refs-citations CLI (37 lines) + reference library (797 lines, shared with refs-index)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Citation validation is governance-generic -- broken references undermine governance integrity
- Shares the 797-line library with refs-index (OBPI-01); absorption of one likely implies the other
- Citation checking is analogous to link checking in documentation systems

## NON-GOALS

- Validating external URLs (only internal governance references)
- Building a citation format standard beyond what opsdev defines

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely (both CLI and library)
1. Evaluate governance generality: Is citation validation universally useful?
1. Document decision: Absorb (add to gzkit) or Exclude (too specialized)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need citation validation

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.33.0-02-01: Read the opsdev implementation completely (both CLI and library)
- [x] REQ-0.33.0-02-02: Evaluate governance generality: Is citation validation universally useful?
- [x] REQ-0.33.0-02-03: Document decision: Absorb (add to gzkit) or Exclude (too specialized)
- [x] REQ-0.33.0-02-04: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.33.0-02-05: If excluding: document why gzkit does not need citation validation


## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed command
- `tests/` -- tests for absorbed command
- `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
