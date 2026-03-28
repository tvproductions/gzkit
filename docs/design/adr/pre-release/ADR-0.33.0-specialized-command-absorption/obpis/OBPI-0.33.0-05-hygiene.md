---
id: OBPI-0.33.0-05-hygiene
parent: ADR-0.33.0-specialized-command-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-05: hygiene

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-05 -- "Evaluate and absorb hygiene (155 lines) -- repository hygiene enforcement"`

## OBJECTIVE

Evaluate opsdev's `hygiene` command (155 lines) for absorption into gzkit. The hygiene command enforces repository cleanliness standards -- checking for stale branches, uncommitted changes, orphaned files, naming convention violations, and other hygiene issues. Determine whether repository hygiene enforcement is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** hygiene implementation (155 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Repository hygiene is governance-generic -- all governed repositories benefit from cleanliness checks
- 155 lines suggests moderate but useful hygiene checking
- May overlap partially with existing gzkit commands (layout-verify, tidy/clean)

## NON-GOALS

- Automatically fixing hygiene issues (only reporting)
- Enforcing domain-specific naming conventions

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Is hygiene enforcement universally useful?
1. Check for overlap with existing gzkit commands (layout-verify, tidy/clean)
1. Document decision: Absorb (add to gzkit) or Exclude (too specialized or redundant)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need a dedicated hygiene command

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
