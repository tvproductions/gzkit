---
id: OBPI-0.38.0-01-adr-template
parent_adr: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-01: ADR Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-01 — "Compare ADR templates between airlineops and gzkit — sections, guidance, frontmatter"`

## OBJECTIVE

Compare the ADR template used in airlineops against the ADR template used in gzkit. Evaluate frontmatter fields, section structure, guidance quality, Agent Context Frame presence, OBPI decomposition table format, evidence ledger structure, and completion checklist. Determine which template produces higher-quality ADRs and absorb the best elements into gzkit's canonical ADR template.

## SOURCE MATERIAL

- **airlineops:** ADR template (scaffold or exemplar ADR)
- **gzkit equivalent:** ADR template in `.gzkit/templates/` or exemplar ADRs

## ASSUMPTIONS

- Both repos produce ADR documents but may use different template structures
- Template quality is measured by: section completeness, guidance clarity, enforcement of required fields, and agent-readability
- The comparison must read actual template content, not just file names or line counts
- Frontmatter schema differences may indicate missing governance metadata in one repo

## NON-GOALS

- Migrating existing ADRs to the new template — only the template itself is in scope
- Changing the ADR lifecycle or governance process
- Comparing ADR content (decisions, rationale) — only the template structure

## REQUIREMENTS (FAIL-CLOSED)

1. Read both ADR templates completely
1. Compare section-by-section: frontmatter, tidy first plan, agent context frame, feature checklist, intent, decision, interfaces, OBPI decomposition, rationale, consequences, evidence, acceptance note, evidence ledger, completion checklist
1. Document which sections exist in one template but not the other
1. Record decision with rationale: Absorb / Confirm / Merge
1. If Absorb or Merge: produce the improved canonical template

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
