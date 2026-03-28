---
id: OBPI-0.38.0-03-closeout-template
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-03: Closeout Form Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-03 — "Compare closeout form templates — checklist items, evidence paths, attestation sections"`

## OBJECTIVE

Compare the ADR closeout form template used in airlineops against the closeout form template used in gzkit. Evaluate pre-attestation checklist items, evidence path tables, OBPI status tracking, attestation section structure, and sign-off ceremony format. Determine which template produces more rigorous closeout documentation and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** ADR-CLOSEOUT-FORM template (scaffold or exemplar)
- **gzkit equivalent:** ADR-CLOSEOUT-FORM template in `.gzkit/templates/` or exemplar closeout forms

## ASSUMPTIONS

- Closeout forms are the final governance checkpoint before an ADR is considered complete
- Template rigor directly impacts whether closeout is a rubber stamp or a genuine verification
- Evidence path tables must reference reproducible commands, not just file paths
- OBPI status tracking in the closeout form must match the ADR's OBPI decomposition table

## NON-GOALS

- Changing the closeout ceremony process itself
- Migrating existing closeout forms to the new template
- Automating closeout verification — only the template is in scope

## REQUIREMENTS (FAIL-CLOSED)

1. Read both closeout form templates completely
1. Compare section-by-section: status, pre-attestation checklist, evidence paths, OBPI status table, attestation section
1. Evaluate whether checklist items are specific and verifiable vs. vague
1. Check that evidence paths reference CLI commands (not just file paths)
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `.gzkit/templates/` — template storage
- `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
