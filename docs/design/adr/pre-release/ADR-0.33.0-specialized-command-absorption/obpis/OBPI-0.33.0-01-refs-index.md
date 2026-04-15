---
id: OBPI-0.33.0-01-refs-index
parent: ADR-0.33.0-specialized-command-absorption
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-01: refs-index

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-01 -- "Evaluate and absorb refs-index (37+797 lines) -- reference index building"`

## OBJECTIVE

Evaluate opsdev's `refs-index` command (37 lines CLI + 797 lines library) for absorption into gzkit. The refs-index command builds a reference index from governance documentation -- scanning ADRs, briefs, runbooks, and other documents to create a searchable cross-reference map. At 834 total lines, this is a substantial reference management system. Determine whether reference indexing is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** refs-index CLI (37 lines) + reference library (797 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Reference indexing is governance-generic -- any governed codebase benefits from document cross-referencing
- The 797-line library suggests mature reference parsing and indexing logic
- The CLI wrapper (37 lines) is thin; the value is in the library
- This shares infrastructure with refs-citations (OBPI-02)

## NON-GOALS

- Building a full-text search engine
- Indexing non-governance documents
- Changing reference format conventions without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely (both CLI and library)
1. Evaluate governance generality: Is reference indexing universally useful?
1. Document decision: Absorb (add to gzkit) or Exclude (too specialized)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need reference indexing

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.33.0-01-01: Read the opsdev implementation completely (both CLI and library)
- [x] REQ-0.33.0-01-02: Evaluate governance generality: Is reference indexing universally useful?
- [x] REQ-0.33.0-01-03: Document decision: Absorb (add to gzkit) or Exclude (too specialized)
- [x] REQ-0.33.0-01-04: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.33.0-01-05: If excluding: document why gzkit does not need reference indexing


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
