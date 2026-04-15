---
id: OBPI-0.32.0-14-status-state
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 14
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-14: status-state

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-14 -- "Compare status/state -- opsdev governance_tools.py 64 lines vs gzkit commands/status.py"`

## OBJECTIVE

Compare opsdev's `status` and `state` commands (governance_tools.py, 64 lines) against gzkit's `commands/status.py`. These commands display governance state (ADR statuses, OBPI progress, pipeline state). Determine whether opsdev's implementation offers better formatting, more data points, or deeper state introspection.

## SOURCE MATERIAL

- **opsdev:** `governance_tools.py` (64 lines)
- **gzkit equivalent:** `commands/status.py`

## ASSUMPTIONS

- Both display governance state in table and JSON formats
- 64 lines is relatively small; implementations may be comparable
- Output formatting and data completeness matter for operator experience

## NON-GOALS

- Changing status/state output schemas
- Adding new governance metrics without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: data points displayed, output formats, state introspection depth
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-14-01: Read both implementations completely
- [x] REQ-0.32.0-14-02: Document comparison: data points displayed, output formats, state introspection depth
- [x] REQ-0.32.0-14-03: Record decision with rationale: Absorb Improvements / Confirm Sufficient
- [x] REQ-0.32.0-14-04: If absorbing: adapt to gzkit conventions and write tests
- [x] REQ-0.32.0-14-05: If confirming: document why gzkit's implementation is sufficient


## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
