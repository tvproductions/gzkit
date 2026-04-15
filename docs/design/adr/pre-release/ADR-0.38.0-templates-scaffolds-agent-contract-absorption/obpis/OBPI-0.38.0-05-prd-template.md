---
id: OBPI-0.38.0-05-prd-template
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-05: PRD Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-05 — "Compare PRD templates — structure, scope definition, deliverable enumeration"`

## OBJECTIVE

Compare the PRD (Product Requirements Document) template used in airlineops against the PRD template used in gzkit. Evaluate scope definition sections, deliverable enumeration, ADR linkage, acceptance criteria format, risk identification, and milestone structure. Determine which template produces more actionable PRDs and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** PRD template (scaffold or exemplar PRD)
- **gzkit equivalent:** PRD template in `.gzkit/templates/` or exemplar PRDs (e.g., PRD-GZKIT-1.0.0)

## ASSUMPTIONS

- PRDs are the highest-level governance artifact, governing multiple ADRs
- Template quality determines whether PRDs provide clear direction or vague aspirations
- PRDs must link to ADRs explicitly — the template must enforce this linkage
- Deliverable enumeration must be specific enough to verify completion

## NON-GOALS

- Changing the PRD governance process or its relationship to ADRs
- Migrating existing PRDs to the new template
- Comparing PRD content (actual requirements) — only the template structure

## REQUIREMENTS (FAIL-CLOSED)

1. Read both PRD templates completely
1. Compare section-by-section: scope, deliverables, ADR linkage, acceptance criteria, risks, milestones, sign-off
1. Evaluate whether deliverable enumeration enforces specificity
1. Check that ADR linkage is mandatory (not optional) in the template
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.38.0-05-01: Read both PRD templates completely
- [x] REQ-0.38.0-05-02: Compare section-by-section: scope, deliverables, ADR linkage, acceptance criteria, risks, milestones, sign-off
- [x] REQ-0.38.0-05-03: Evaluate whether deliverable enumeration enforces specificity
- [x] REQ-0.38.0-05-04: Check that ADR linkage is mandatory (not optional) in the template
- [x] REQ-0.38.0-05-05: Record decision with rationale: Absorb / Confirm / Merge


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
