---
id: OBPI-0.32.0-01-git-sync
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-01: git-sync

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-01 -- "Compare git-sync -- opsdev 682 lines vs gzkit 199 lines"`

## OBJECTIVE

Compare opsdev's `git-sync` implementation (682 lines) against gzkit's `git-sync` (199 lines) at the code level. The 483-line disparity is the largest in the entire comparison set and demands thorough examination. Determine what those additional lines provide -- error recovery, edge-case handling, multi-repo support, conflict resolution, hook integration -- and whether gzkit must absorb any of those capabilities.

## SOURCE MATERIAL

- **opsdev:** git-sync tool implementation (682 lines)
- **gzkit equivalent:** git-sync implementation (199 lines)

## ASSUMPTIONS

- The 3.4x line count ratio likely indicates significant feature or robustness gaps
- opsdev's implementation may have battle-tested error recovery paths gzkit lacks
- Some of the disparity may be opsdev-specific logic (multi-project orchestration)
- The comparison must categorize every major code block in both implementations

## NON-GOALS

- Rewriting git-sync from scratch -- absorb improvements surgically
- Changing opsdev -- this is upstream absorption only
- Adding features that are purely opsdev-specific (e.g., airline domain hooks)

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely -- every function, every error path
1. Categorize the 483-line gap: what does opsdev have that gzkit lacks?
1. Document comparison: error handling, edge cases, conflict resolution, hook integration
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document exactly why 199 lines is sufficient where 682 exists

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
