---
id: OBPI-0.33.0-08-governance-setup
parent: ADR-0.33.0-specialized-command-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-08: governance-setup

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-08 -- "Evaluate and absorb governance setup (279 lines) -- governance initialization and setup"`

## OBJECTIVE

Evaluate opsdev's `governance setup` subcommand (279 lines) for absorption into gzkit. The governance setup command initializes a repository's governance infrastructure -- creating directory structures, configuration files, initial manifests, and control surfaces. At 279 lines, this is a substantial initialization tool. Determine whether governance setup is a capability gzkit should own (as the governance toolkit) or whether it remains in opsdev.

## SOURCE MATERIAL

- **opsdev:** governance setup implementation (279 lines)
- **gzkit equivalent:** None (gzkit assumes governance is already set up)

## ASSUMPTIONS

- Governance setup is a prime candidate for gzkit ownership -- gzkit IS the governance toolkit
- 279 lines suggests comprehensive initialization beyond simple directory creation
- This is the first of three governance orchestration commands (setup/report/runners)
- gzkit currently lacks a `gz init` or `gz setup` command

## NON-GOALS

- Building a project scaffolding tool (only governance structure)
- Supporting non-gzkit governance frameworks

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Should gzkit own its own setup/initialization?
1. Document decision: Absorb (add to gzkit) or Exclude (leave in opsdev)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit should not own governance initialization

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.33.0-08-01: Read the opsdev implementation completely
- [x] REQ-0.33.0-08-02: Evaluate governance generality: Should gzkit own its own setup/initialization?
- [x] REQ-0.33.0-08-03: Document decision: Absorb (add to gzkit) or Exclude (leave in opsdev)
- [x] REQ-0.33.0-08-04: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.33.0-08-05: If excluding: document why gzkit should not own governance initialization


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
