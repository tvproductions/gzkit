---
id: OBPI-0.32.0-07-cli-audit
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-07: cli-audit

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-07 -- "Compare cli-audit -- opsdev cli_tools.py 142 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `cli-audit` command (cli_tools.py, 142 lines) against gzkit's cli-audit implementation in cli.py. The CLI audit command verifies that all CLI commands have proper help text, examples, and documentation. Determine whether opsdev's 142-line implementation includes validation checks that gzkit's version lacks.

## SOURCE MATERIAL

- **opsdev:** `cli_tools.py` (142 lines)
- **gzkit equivalent:** `cli.py` (cli-audit section)

## ASSUMPTIONS

- CLI audit is a governance enforcement tool -- thoroughness matters
- opsdev's 142 lines may include help text validation, example checking, flag consistency
- gzkit's implementation may be simpler or more comprehensive depending on architecture

## NON-GOALS

- Changing CLI audit scope or contract
- Adding new audit checks beyond what either implementation provides

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: validation checks, reporting format, error categorization
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-07-01: Read both implementations completely
- [x] REQ-0.32.0-07-02: Document comparison: validation checks, reporting format, error categorization
- [x] REQ-0.32.0-07-03: Record decision with rationale: Absorb Improvements / Confirm Sufficient
- [x] REQ-0.32.0-07-04: If absorbing: adapt to gzkit conventions and write tests
- [x] REQ-0.32.0-07-05: If confirming: document why gzkit's implementation is sufficient


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
