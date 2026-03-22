---
id: OBPI-0.38.0-06-constitution-template
parent_adr: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-06: Constitution Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-06 — "Compare constitution templates — governance principles, rule structure, enforcement"`

## OBJECTIVE

Compare the constitution template used in airlineops against the constitution template used in gzkit. Evaluate governance principle articulation, rule structure and hierarchy, enforcement mechanism documentation, amendment process, and authority delegation patterns. Determine which template produces more enforceable constitutions and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** Constitution template (scaffold or exemplar constitution)
- **gzkit equivalent:** Constitution template in `.gzkit/templates/` or exemplar constitutions

## ASSUMPTIONS

- Constitutions define the foundational governance rules that all other artifacts must comply with
- Template quality determines whether constitutions are aspirational statements or enforceable contracts
- Enforcement mechanism documentation is critical — a rule without enforcement is a suggestion
- Amendment process must be explicit to prevent governance drift

## NON-GOALS

- Changing gzkit's actual governance principles or constitution content
- Migrating existing constitutions to the new template
- Comparing constitutional content (actual rules) — only the template structure

## REQUIREMENTS (FAIL-CLOSED)

1. Read both constitution templates completely
1. Compare section-by-section: governance principles, rule hierarchy, enforcement mechanisms, amendment process, authority delegation
1. Evaluate whether enforcement sections require specific CLI commands or are vague
1. Check that amendment process is documented (not left implicit)
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
