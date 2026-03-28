---
id: OBPI-0.38.0-04-audit-template
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-04: Audit Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-04 — "Compare audit templates — audit sequence, evidence gathering, receipt emission"`

## OBJECTIVE

Compare the audit template used in airlineops against the audit template used in gzkit. Evaluate audit sequence steps, evidence gathering methodology, receipt emission format, gate verification commands, and compliance checking structure. Determine which template produces more thorough audits and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** Audit template (scaffold or exemplar audit document)
- **gzkit equivalent:** Audit template in `.gzkit/templates/` or exemplar audit documents

## ASSUMPTIONS

- Audits are the verification mechanism that ensures governance claims are backed by evidence
- Template quality determines whether audits are perfunctory or genuinely verify compliance
- Receipt emission format must be machine-parseable for downstream tooling
- Audit templates must reference reproducible CLI commands for evidence gathering

## NON-GOALS

- Changing the audit process or its relationship to gates
- Migrating existing audit documents to the new template
- Modifying ARB (Agent Self-Reporting) receipt format — only the audit template that references receipts

## REQUIREMENTS (FAIL-CLOSED)

1. Read both audit templates completely
1. Compare section-by-section: audit sequence, evidence gathering commands, receipt emission, gate verification, compliance summary
1. Evaluate whether audit steps are specific and reproducible
1. Check that evidence gathering references CLI commands (not manual inspection)
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
