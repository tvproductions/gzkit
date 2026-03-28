---
id: OBPI-0.32.0-21-sync-skills
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 21
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-21: sync-skills

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-21 -- "Compare sync-agents-skills/sync-claude-skills -- opsdev skill_sync_tools.py 456 lines vs gzkit sync.py"`

## OBJECTIVE

Compare opsdev's skill synchronization commands (skill_sync_tools.py, 456 lines) against gzkit's `sync.py`. At 456 lines, opsdev's implementation is substantial, suggesting it may handle multi-vendor skill discovery, template rendering, conflict resolution, or validation that gzkit's sync.py lacks. Determine what the 456 lines provide and whether gzkit should absorb improvements.

## SOURCE MATERIAL

- **opsdev:** `skill_sync_tools.py` (456 lines)
- **gzkit equivalent:** `sync.py`

## ASSUMPTIONS

- Skill synchronization is critical for agent governance
- 456 lines suggests comprehensive sync logic beyond simple file copying
- opsdev may support multiple agent vendors; gzkit is Claude-primary
- Template rendering and skill discovery may differ significantly

## NON-GOALS

- Adding non-Claude vendor support without justification
- Changing skill file format or conventions

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: skill discovery, template rendering, sync targets, conflict handling
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document what gzkit provides that makes 456 lines unnecessary

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
