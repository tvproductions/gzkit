---
id: OBPI-0.34.0-06-pipeline-router
parent: ADR-0.34.0-claude-hooks-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-06: pipeline-router

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-06 -- "Compare pipeline-router.py -- routes pipeline execution"`

## OBJECTIVE

Compare airlineops's `pipeline-router.py` hook against gzkit's equivalent hook behavior. This hook routes pipeline execution based on the current governance context -- determining which pipeline steps to execute, in what order, and with what parameters based on the active ADR, OBPI, and lane. Determine whether gzkit's existing pipeline routing covers the same behavior.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/pipeline-router.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- pipeline routing behavior in existing modules

## ASSUMPTIONS

- Pipeline routing is critical for governance workflow automation
- gzkit likely has pipeline routing given its governance pipeline architecture
- airlineops's version may route based on additional context signals

## NON-GOALS

- Changing the governance pipeline stages
- Modifying pipeline execution order without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: routing logic, context detection, pipeline stage selection
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's pipeline routing is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.34.0-06-01: Read both implementations completely
- [x] REQ-0.34.0-06-02: Document comparison: routing logic, context detection, pipeline stage selection
- [x] REQ-0.34.0-06-03: Record decision: gzkit sufficient, or absorb airlineops improvements
- [x] REQ-0.34.0-06-04: If absorbing: integrate into gzkit hook module architecture and write tests
- [x] REQ-0.34.0-06-05: If confirming: document why gzkit's pipeline routing is sufficient


## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for absorbed hook behavior
- `tests/` -- tests for absorbed hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
