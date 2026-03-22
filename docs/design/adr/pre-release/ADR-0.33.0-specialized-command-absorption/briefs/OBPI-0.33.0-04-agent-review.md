---
id: OBPI-0.33.0-04-agent-review
parent_adr: ADR-0.33.0-specialized-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-04: agent-review

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-04 -- "Evaluate and absorb agent-review (231 lines) -- agent configuration review"`

## OBJECTIVE

Evaluate opsdev's `agent-review` command (231 lines) for absorption into gzkit. The agent-review command reviews AI agent configurations -- checking AGENTS.md, CLAUDE.md, skill files, hook configurations, and instruction files for correctness and consistency. At 231 lines, this is a substantial review tool. Determine whether agent configuration review is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** agent-review implementation (231 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Agent configuration review is directly relevant to gzkit as a governance toolkit
- gzkit manages agent configurations (AGENTS.md, skills, hooks) and should validate them
- 231 lines suggests comprehensive validation beyond simple file existence checks
- This is likely governance-generic given gzkit's role as an agent governance tool

## NON-GOALS

- Reviewing agent runtime behavior (only static configuration)
- Adding vendor-specific agent review logic

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Is agent configuration review universally useful?
1. Document decision: Absorb (add to gzkit) or Exclude (too domain-specific)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need agent configuration review

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed command
- `tests/` -- tests for absorbed command
- `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
