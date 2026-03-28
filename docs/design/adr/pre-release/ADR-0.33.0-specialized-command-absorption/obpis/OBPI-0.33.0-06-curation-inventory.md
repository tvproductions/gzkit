---
id: OBPI-0.33.0-06-curation-inventory
parent: ADR-0.33.0-specialized-command-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-06: curation-inventory

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-06 -- "Evaluate and absorb curation inventory (250 lines) -- curation inventory management"`

## OBJECTIVE

Evaluate opsdev's `curation inventory` subcommand (250 lines) for absorption into gzkit. The curation inventory command manages inventories of curated content -- tracking what governance artifacts exist, their status, and their relationships. Determine whether curation inventory management is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** curation inventory implementation (250 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Content inventory management may be governance-generic (tracking ADRs, briefs, docs)
- 250 lines suggests meaningful inventory logic beyond simple file listing
- Shares a curation module with curation guard (OBPI-07)
- May overlap with gzkit's existing ADR discovery and status commands

## NON-GOALS

- Building a full content management system
- Inventorying non-governance artifacts

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Is curation inventory universally useful?
1. Check for overlap with existing gzkit commands (adr status, adr map)
1. Document decision: Absorb (add to gzkit) or Exclude (too specialized or redundant)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need curation inventory

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
