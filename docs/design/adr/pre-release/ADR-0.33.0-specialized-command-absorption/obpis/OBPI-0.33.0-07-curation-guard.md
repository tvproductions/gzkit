---
id: OBPI-0.33.0-07-curation-guard
parent: ADR-0.33.0-specialized-command-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-07: curation-guard

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-07 -- "Evaluate and absorb curation guard (250 lines) -- curation guard enforcement"`

## OBJECTIVE

Evaluate opsdev's `curation guard` subcommand (250 lines) for absorption into gzkit. The curation guard command enforces curation policies -- preventing unauthorized modifications to curated content, validating content structure, and ensuring curation standards are met. Determine whether curation guard enforcement is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** curation guard implementation (250 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Curation guarding may be governance-generic (protecting governance artifacts from invalid changes)
- 250 lines suggests meaningful guard logic with validation rules
- Shares a curation module with curation inventory (OBPI-06)
- Guard patterns may be analogous to gzkit's admission control

## NON-GOALS

- Building content approval workflows
- Guarding non-governance content

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Is curation guarding universally useful?
1. Check for overlap with gzkit's admission control patterns
1. Document decision: Absorb (add to gzkit) or Exclude (too specialized or redundant)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need curation guarding

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.33.0-07-01: Read the opsdev implementation completely
- [x] REQ-0.33.0-07-02: Evaluate governance generality: Is curation guarding universally useful?
- [x] REQ-0.33.0-07-03: Check for overlap with gzkit's admission control patterns
- [x] REQ-0.33.0-07-04: Document decision: Absorb (add to gzkit) or Exclude (too specialized or redundant)
- [x] REQ-0.33.0-07-05: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.33.0-07-06: If excluding: document why gzkit does not need curation guarding


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
