---
id: OBPI-0.32.0-05-typecheck
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-05: typecheck

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-05 -- "Compare typecheck -- opsdev typing_tools.py 64 lines vs gzkit quality.py"`

## OBJECTIVE

Compare opsdev's `typecheck` command (typing_tools.py, 64 lines) against gzkit's typecheck implementation in quality.py. Both wrap `ty check`. Determine whether opsdev's dedicated module offers advantages -- exclude patterns, error categorization, ty configuration management -- over gzkit's consolidated approach.

## SOURCE MATERIAL

- **opsdev:** `typing_tools.py` (64 lines)
- **gzkit equivalent:** `quality.py` (typecheck section)

## ASSUMPTIONS

- Both wrap the same underlying tool (ty)
- 64 lines suggests moderate orchestration beyond bare invocation
- Exclude patterns and configuration may differ between projects

## NON-GOALS

- Changing the type checker (staying with ty)
- Comparing ty configuration files

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: ty invocation, exclude patterns, error handling, output formatting
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

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
