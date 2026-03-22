---
id: OBPI-0.37.0-21-governance-audits
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-21: governance-audits

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-21 — "Compare and absorb audits/ — governance harmonization audits"`

## OBJECTIVE

Compare the `docs/governance/GovZero/audits/` directory between airlineops and gzkit. This directory contains governance harmonization audit records — evidence of cross-repo governance alignment. Determine: Absorb (airlineops has audit records gzkit lacks), Confirm (gzkit's audits are complete), or Merge (both have unique audit records).

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/audits/`
- **gzkit:** `docs/governance/GovZero/audits/`

## ASSUMPTIONS

- Audit records document historical governance alignment activities
- Both repos may have audit records from different perspectives
- gzkit should have the complete audit history as the governance authority
- Audit records are append-only — no records should be lost

## NON-GOALS

- Conducting new governance audits
- Changing audit record format
- Deleting historical audit records

## REQUIREMENTS (FAIL-CLOSED)

1. List all files in both `audits/` directories
1. Compare each file present in both repos
1. Identify files present in only one repo
1. Evaluate which version of shared files is more complete
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/audits/` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
