---
id: OBPI-0.32.0-02-lint
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-02: lint

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-02 -- "Compare lint -- opsdev lint_tools.py 69 lines vs gzkit quality.py"`

## OBJECTIVE

Compare opsdev's `lint` command (lint_tools.py, 69 lines) against gzkit's lint implementation in quality.py. gzkit consolidates lint/format/test/typecheck into a single quality.py module. Determine whether opsdev's dedicated lint module offers any advantages over gzkit's consolidated approach -- additional ruff configurations, error categorization, fix-mode handling, or output formatting.

## SOURCE MATERIAL

- **opsdev:** `lint_tools.py` (69 lines)
- **gzkit equivalent:** `quality.py` (lint section)

## ASSUMPTIONS

- gzkit's consolidated quality.py may sacrifice lint-specific depth for breadth
- opsdev's smaller dedicated file may have cleaner separation of concerns
- Both ultimately wrap ruff; the comparison is about orchestration quality

## NON-GOALS

- Splitting gzkit's quality.py into separate files without justification
- Comparing ruff configuration (pyproject.toml) -- only the invocation wrapper

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: ruff invocation, fix mode, error handling, output formatting
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's consolidated approach is sufficient

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
