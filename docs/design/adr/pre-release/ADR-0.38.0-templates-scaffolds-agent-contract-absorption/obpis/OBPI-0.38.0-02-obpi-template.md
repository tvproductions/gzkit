---
id: OBPI-0.38.0-02-obpi-template
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-02: OBPI Brief Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-02 — "Compare OBPI brief templates — objective, requirements, quality gates sections"`

## OBJECTIVE

Compare the OBPI brief template used in airlineops against the OBPI brief template used in gzkit. Evaluate frontmatter fields, objective section guidance, source material references, assumptions framing, non-goals boundary, requirements fail-closed pattern, allowed paths scoping, quality gates checklist, and closing argument structure. Determine which template produces more actionable briefs and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** OBPI brief template (scaffold or exemplar brief)
- **gzkit equivalent:** OBPI brief template in `.gzkit/templates/` or exemplar briefs

## ASSUMPTIONS

- OBPI briefs are the primary work unit for agents — template quality directly impacts agent effectiveness
- Both repos use similar brief structures but may differ in section detail and guidance
- The "fail-closed requirements" pattern and "allowed paths" scoping are critical for agent safety
- Template guidance quality determines whether agents produce thorough or superficial work

## NON-GOALS

- Migrating existing briefs to the new template
- Changing the OBPI lifecycle or numbering scheme
- Comparing brief content (actual objectives) — only the template structure

## REQUIREMENTS (FAIL-CLOSED)

1. Read both OBPI brief templates completely
1. Compare section-by-section: frontmatter, ADR item reference, objective, source material, assumptions, non-goals, requirements, allowed paths, quality gates, closing argument
1. Document which sections exist in one template but not the other
1. Evaluate guidance quality — does each section explain what the agent should write?
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
