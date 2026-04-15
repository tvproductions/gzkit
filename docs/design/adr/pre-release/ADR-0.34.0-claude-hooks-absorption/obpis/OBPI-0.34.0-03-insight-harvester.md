---
id: OBPI-0.34.0-03-insight-harvester
parent: ADR-0.34.0-claude-hooks-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-03: insight-harvester

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-03 -- "Absorb insight-harvester.py -- harvests agent insights from conversations"`

## OBJECTIVE

Absorb airlineops's `insight-harvester.py` hook into gzkit. This hook harvests insights from agent conversations -- capturing patterns, decisions, recurring issues, and actionable observations that emerge during agent work. These insights are stored in `.gzkit/insights/agent-insights.jsonl` for later analysis. gzkit does not currently have this hook behavior. Evaluate and absorb.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/insight-harvester.py`
- **gzkit equivalent:** None -- this is a new behavior for gzkit

## ASSUMPTIONS

- Insight harvesting is governance-generic -- all agent-governed projects benefit from capturing agent observations
- gzkit already has the insights storage path (`.gzkit/insights/agent-insights.jsonl`)
- The harvester likely triggers on conversation patterns or explicit agent signals

## NON-GOALS

- Building an insight analysis dashboard
- Harvesting non-governance insights

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops implementation completely
1. Evaluate governance generality (expected: governance-generic)
1. Adapt to gzkit hook module architecture
1. Implement and write tests
1. Document the absorption rationale

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.34.0-03-01: Read the airlineops implementation completely
- [x] REQ-0.34.0-03-02: Evaluate governance generality (expected: governance-generic)
- [x] REQ-0.34.0-03-03: Adapt to gzkit hook module architecture
- [x] REQ-0.34.0-03-04: Implement and write tests
- [x] REQ-0.34.0-03-05: Document the absorption rationale


## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for new hook behavior
- `tests/` -- tests for new hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Absorption rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
