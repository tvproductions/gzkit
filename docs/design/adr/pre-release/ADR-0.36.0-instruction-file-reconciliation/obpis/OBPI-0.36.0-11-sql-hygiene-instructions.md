---
id: OBPI-0.36.0-11-sql-hygiene-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 11
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-11: sql-hygiene-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-11 — "Evaluate sql_hygiene.instructions.md for generic pattern extraction"`

## OBJECTIVE

Evaluate airlineops's `sql_hygiene.instructions.md` for extractable generic patterns. This file has no gzkit counterpart. While nominally SQL-specific, it may contain generic patterns applicable to any Python project using SQLite or databases: parameterized queries, injection prevention, connection management, transaction patterns, encoding requirements. Determine: Extract (generic patterns warrant a new gzkit rules file) or Exclude (entirely domain-specific).

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/sql_hygiene.instructions.md`
- **gzkit equivalent:** None

## ASSUMPTIONS

- gzkit uses SQLite for ledger and governance data storage
- SQL hygiene patterns like parameterized queries and connection management are governance-generic
- The file may mix generic SQL patterns with airline-specific database patterns
- If generic patterns exist, they warrant a new `.claude/rules/sql-hygiene.md` in gzkit

## NON-GOALS

- Importing airline-specific database schemas or queries
- Creating a full SQL governance framework in gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops `sql_hygiene.instructions.md` completely
1. Categorize each section as: generic (applicable to any SQLite/DB project) or domain-specific (airline data)
1. If generic patterns exist: document what to extract and propose a new gzkit rules file
1. Record decision with rationale: Extract / Exclude

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
