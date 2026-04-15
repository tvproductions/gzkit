---
id: OBPI-0.38.0-07-agents-md-contract
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-07: AGENTS.md Template/Contract Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-07 — "Compare AGENTS.md templates/contracts — generic governance sections, agent role definitions"`

## OBJECTIVE

Compare the AGENTS.md contract/template used in airlineops against the AGENTS.md contract/template used in gzkit. Focus on the generic (non-domain-specific) sections: agent role definitions, governance workflow sequences, non-negotiable rules, skill catalogs, control surface definitions, and gate enforcement sections. Determine which contract provides better agent guidance and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** `AGENTS.md` — full contract with generic and domain-specific sections
- **gzkit equivalent:** `AGENTS.md` — full contract with generic and domain-specific sections

## ASSUMPTIONS

- AGENTS.md is the authoritative governance contract that agents must follow
- Generic sections (roles, workflows, gates, rules) should be consistent across repos
- Domain-specific sections are out of scope — only generic governance guidance is compared
- The contract's effectiveness is measured by agent compliance and artifact quality

## NON-GOALS

- Comparing domain-specific sections of AGENTS.md
- Changing the AGENTS.md generation pipeline (`gz agent sync control-surfaces`)
- Modifying agent behavior beyond what template/contract changes naturally produce

## REQUIREMENTS (FAIL-CLOSED)

1. Read both AGENTS.md files completely
1. Identify and extract generic sections (non-domain-specific governance guidance)
1. Compare section-by-section: agent roles, workflow sequences, non-negotiable rules, skill catalogs, control surfaces, gate enforcement
1. Document which guidance exists in one contract but not the other
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.38.0-07-01: Read both AGENTS.md files completely
- [x] REQ-0.38.0-07-02: Identify and extract generic sections (non-domain-specific governance guidance)
- [x] REQ-0.38.0-07-03: Compare section-by-section: agent roles, workflow sequences, non-negotiable rules, skill catalogs, control surfaces, gate enforcement
- [x] REQ-0.38.0-07-04: Document which guidance exists in one contract but not the other
- [x] REQ-0.38.0-07-05: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `.gzkit/templates/` — template storage
- `AGENTS.md` — agent contract (for comparison reference only)
- `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
