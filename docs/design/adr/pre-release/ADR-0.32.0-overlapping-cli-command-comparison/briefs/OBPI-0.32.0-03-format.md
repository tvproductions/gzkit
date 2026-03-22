---
id: OBPI-0.32.0-03-format
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-03: format

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-03 -- "Compare format -- opsdev format_tools.py 33 lines vs gzkit quality.py"`

## OBJECTIVE

Compare opsdev's `format` command (format_tools.py, 33 lines) against gzkit's format implementation in quality.py. Both wrap ruff format. Determine whether opsdev's minimal dedicated module offers any advantages -- check-only mode, diff output, specific file targeting -- that gzkit's consolidated approach may lack.

## SOURCE MATERIAL

- **opsdev:** `format_tools.py` (33 lines)
- **gzkit equivalent:** `quality.py` (format section)

## ASSUMPTIONS

- At 33 lines, opsdev's implementation is minimal; gzkit may already match or exceed it
- The comparison may be quick but still requires code-level reading
- Both ultimately invoke `ruff format`

## NON-GOALS

- Refactoring quality.py's structure in this OBPI
- Comparing ruff format configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: invocation flags, check mode, diff mode, error handling
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation covers all needs

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
