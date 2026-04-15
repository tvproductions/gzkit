---
id: OBPI-0.36.0-12-warehouse-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 12
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-12: warehouse-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-12 — "Evaluate warehouse.instructions.md for generic pattern extraction"`

## OBJECTIVE

Evaluate airlineops's `warehouse.instructions.md` for extractable generic patterns. This file has no gzkit counterpart and is nominally domain-specific (data warehouse operations). However, it may contain generic patterns applicable to any data pipeline project: ETL conventions, data validation patterns, schema evolution, idempotency requirements, batch processing patterns. Determine: Extract (generic patterns warrant a new gzkit rules file) or Exclude (entirely domain-specific).

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/warehouse.instructions.md`
- **gzkit equivalent:** None

## ASSUMPTIONS

- The file is likely primarily airline-domain-specific (warehouse = airline data warehouse)
- Generic patterns may exist in: data validation, schema evolution, idempotency, batch processing
- Do not assume the file is entirely domain-specific without reading it
- If generic patterns are minimal, Exclude is the appropriate decision

## NON-GOALS

- Importing airline data warehouse patterns into gzkit
- Creating data pipeline governance in gzkit (unless generic patterns warrant it)
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops `warehouse.instructions.md` completely
1. Categorize each section as: generic (applicable to any data project) or domain-specific (airline warehouse)
1. If generic patterns exist: document what to extract and propose scope
1. Record decision with rationale: Extract / Exclude

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-12-01: Read the airlineops `warehouse.instructions.md` completely
- [x] REQ-0.36.0-12-02: Categorize each section as: generic (applicable to any data project) or domain-specific (airline warehouse)
- [x] REQ-0.36.0-12-03: If generic patterns exist: document what to extract and propose scope
- [x] REQ-0.36.0-12-04: Record decision with rationale: Extract / Exclude


## ALLOWED PATHS

- `.claude/rules/` — target for new rules file if extracted
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
