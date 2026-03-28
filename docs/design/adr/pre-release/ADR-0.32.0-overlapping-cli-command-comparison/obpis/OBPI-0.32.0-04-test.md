---
id: OBPI-0.32.0-04-test
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-04: test

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-04 -- "Compare test -- opsdev test_suites.py 389 lines vs gzkit quality.py"`

## OBJECTIVE

Compare opsdev's `test` command (test_suites.py, 389 lines) against gzkit's test implementation in quality.py. The opsdev implementation is substantial at 389 lines, suggesting it may include test suite discovery, parallel execution, coverage integration, selective test running, or reporting features that gzkit's simpler quality.py wrapper lacks. Determine what the 389 lines provide and whether gzkit should absorb any of those capabilities.

## SOURCE MATERIAL

- **opsdev:** `test_suites.py` (389 lines)
- **gzkit equivalent:** `quality.py` (test section)

## ASSUMPTIONS

- 389 lines for a test runner wrapper suggests significant orchestration beyond simple `unittest` invocation
- opsdev may have coverage integration, suite selection, or parallel test execution
- gzkit's quality.py test section may be a thin wrapper that misses these capabilities
- The comparison must account for gzkit's ARB integration for test receipts

## NON-GOALS

- Changing the test framework (staying with unittest)
- Adding pytest dependencies
- Rewriting the test runner from scratch

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: test discovery, coverage integration, selective running, reporting, error handling
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document what gzkit provides that makes 389 lines unnecessary

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
