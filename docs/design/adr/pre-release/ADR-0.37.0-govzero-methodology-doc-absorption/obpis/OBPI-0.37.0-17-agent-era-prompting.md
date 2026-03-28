---
id: OBPI-0.37.0-17-agent-era-prompting
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 17
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-17: agent-era-prompting

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-17 — "Compare and absorb agent-era-prompting-summary.md — prompting methodology"`

## OBJECTIVE

Compare `docs/governance/GovZero/agent-era-prompting-summary.md` between airlineops and gzkit. This document summarizes prompting methodology for the agent era — how to write effective governance prompts, skill definitions, and agent instructions. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/agent-era-prompting-summary.md`
- **gzkit:** `docs/governance/GovZero/agent-era-prompting-summary.md`

## ASSUMPTIONS

- Prompting methodology is governance-generic and central to agent-governed development
- Both repos should describe the same prompting principles
- gzkit as the governance toolkit should have the authoritative prompting methodology

## NON-GOALS

- Changing the prompting methodology
- Adding domain-specific prompt templates

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in prompting principles, examples, anti-patterns
1. Evaluate which version is more comprehensive and actionable
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/agent-era-prompting-summary.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
