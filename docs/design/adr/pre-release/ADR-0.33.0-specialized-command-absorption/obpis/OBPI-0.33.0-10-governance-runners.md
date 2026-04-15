---
id: OBPI-0.33.0-10-governance-runners
parent: ADR-0.33.0-specialized-command-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-10: governance-runners

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-10 -- "Evaluate and absorb governance runners (355 lines) -- governance task runners"`

## OBJECTIVE

Evaluate opsdev's `governance runners` subcommand (355 lines) for absorption into gzkit. The governance runners command orchestrates governance task execution -- running sequences of governance operations (lint, test, gates, audit) in defined order with proper error handling and reporting. Determine whether governance task running is a capability gzkit should own.

## SOURCE MATERIAL

- **opsdev:** governance runners implementation (355 lines)
- **gzkit equivalent:** Partial -- `gz gates` runs quality gates; no general-purpose runner

## ASSUMPTIONS

- Task running is governance-generic -- orchestrating quality checks in sequence
- 355 lines suggests significant orchestration logic beyond simple sequential execution
- May include parallel execution, dependency ordering, or conditional runs
- gzkit's `gz gates` may be a subset of this capability

## NON-GOALS

- Building a CI/CD pipeline (only local governance orchestration)
- Replacing `gz gates` (may extend it)

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Compare against gzkit's existing orchestration (`gz gates`)
1. Evaluate: Does opsdev's runner provide capabilities gzkit lacks?
1. Document decision: Absorb (add to gzkit) or Exclude (existing orchestration sufficient)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit's existing orchestration is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.33.0-10-01: Read the opsdev implementation completely
- [x] REQ-0.33.0-10-02: Compare against gzkit's existing orchestration (`gz gates`)
- [x] REQ-0.33.0-10-03: Evaluate: Does opsdev's runner provide capabilities gzkit lacks?
- [x] REQ-0.33.0-10-04: Document decision: Absorb (add to gzkit) or Exclude (existing orchestration sufficient)
- [x] REQ-0.33.0-10-05: If absorbing: adapt to gzkit conventions, implement, and write tests
- [x] REQ-0.33.0-10-06: If excluding: document why gzkit's existing orchestration is sufficient


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
