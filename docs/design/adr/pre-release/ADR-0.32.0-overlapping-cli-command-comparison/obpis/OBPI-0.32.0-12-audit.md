---
id: OBPI-0.32.0-12-audit
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 12
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-12: audit

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-12 -- "Compare audit -- opsdev adr_evidence_audit.py 453 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `audit` command (adr_evidence_audit.py, 453 lines) against gzkit's audit implementation in cli.py. At 453 lines, opsdev's audit is one of the largest tool implementations. The audit command verifies ADR completion claims using reproducible evidence. Determine what those 453 lines provide -- evidence validation depth, cross-reference checking, receipt verification, compliance scoring -- and whether gzkit's implementation covers the same ground.

## SOURCE MATERIAL

- **opsdev:** `adr_evidence_audit.py` (453 lines)
- **gzkit equivalent:** `cli.py` (audit section)

## ASSUMPTIONS

- 453 lines suggests comprehensive audit logic beyond simple gate checking
- opsdev may validate evidence paths, cross-reference OBPIs, verify receipt artifacts
- gzkit's audit may be a thinner wrapper that delegates more to other commands
- Audit thoroughness directly impacts governance integrity

## NON-GOALS

- Changing audit scope or compliance criteria
- Adding audit checks beyond what either implementation provides

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: evidence validation, cross-referencing, receipt checking, reporting
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document what gzkit provides that makes 453 lines unnecessary

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-12-01: Read both implementations completely
- [x] REQ-0.32.0-12-02: Document comparison: evidence validation, cross-referencing, receipt checking, reporting
- [x] REQ-0.32.0-12-03: Record decision with rationale: Absorb Improvements / Confirm Sufficient
- [x] REQ-0.32.0-12-04: If absorbing: adapt to gzkit conventions and write tests
- [x] REQ-0.32.0-12-05: If confirming: document what gzkit provides that makes 453 lines unnecessary


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
