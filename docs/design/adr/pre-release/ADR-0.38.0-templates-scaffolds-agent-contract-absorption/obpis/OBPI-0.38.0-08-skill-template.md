---
id: OBPI-0.38.0-08-skill-template
parent: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.38.0-08: Skill Template Comparison

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.38.0-templates-scaffolds-agent-contract-absorption/ADR-0.38.0-templates-scaffolds-agent-contract-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.38.0-08 — "Compare skill templates — skill definition format, metadata, invocation contracts"`

## OBJECTIVE

Compare the skill template used in airlineops against the skill template used in gzkit. Evaluate skill definition format, metadata fields (description, triggers, prerequisites), invocation contracts, input/output specifications, error handling guidance, and example sections. Determine which template produces more effective skill definitions and absorb the best elements.

## SOURCE MATERIAL

- **airlineops:** Skill templates in `.github/skills/` or `.claude/skills/`
- **gzkit equivalent:** Skill templates in `.github/skills/` or `.claude/skills/`

## ASSUMPTIONS

- Skills are the primary mechanism for agent capability discovery and invocation
- Template quality determines whether agents can reliably discover and execute skills
- Invocation contracts (inputs, outputs, preconditions) must be explicit and machine-parseable
- Skill metadata must support both human browsing and agent discovery

## NON-GOALS

- Comparing individual skill implementations — only the template structure
- Changing the skill discovery or invocation mechanism
- Migrating existing skills to the new template

## REQUIREMENTS (FAIL-CLOSED)

1. Read both skill templates completely
1. Compare section-by-section: metadata, description, triggers, prerequisites, invocation contract, inputs, outputs, error handling, examples
1. Evaluate whether invocation contracts are specific enough for deterministic agent execution
1. Check that error handling guidance helps agents recover from failures
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.38.0-08-01: Read both skill templates completely
- [x] REQ-0.38.0-08-02: Compare section-by-section: metadata, description, triggers, prerequisites, invocation contract, inputs, outputs, error handling, examples
- [x] REQ-0.38.0-08-03: Evaluate whether invocation contracts are specific enough for deterministic agent execution
- [x] REQ-0.38.0-08-04: Check that error handling guidance helps agents recover from failures
- [x] REQ-0.38.0-08-05: Record decision with rationale: Absorb / Confirm / Merge


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
