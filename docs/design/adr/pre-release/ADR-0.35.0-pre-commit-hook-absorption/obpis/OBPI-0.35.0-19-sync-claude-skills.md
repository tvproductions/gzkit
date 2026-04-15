---
id: OBPI-0.35.0-19-sync-claude-skills
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 19
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-19: sync-claude-skills

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-19 — "Evaluate sync-claude-skills — Claude skills synchronization (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `sync-claude-skills` pre-commit hook — ensures Claude skills files stay synchronized with their source definitions. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce sync on every commit), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit needs automated skills synchronization enforcement and whether this overlaps with `gz agent sync control-surfaces`.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `sync-claude-skills`, implementation script
- **gzkit equivalent:** None (gzkit has `gz agent sync control-surfaces` but no pre-commit enforcement)

## ASSUMPTIONS

- gzkit has `.claude/skills/` directory with skill definitions
- The hook likely detects when skill source files change without updating the synchronized copies
- gzkit's `gz agent sync control-surfaces` performs the sync but doesn't enforce it at commit time
- Pre-commit enforcement would catch missed sync operations

## NON-GOALS

- Changing the skills synchronization architecture
- Auto-running sync (the hook validates, not executes)
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `sync-claude-skills` hook implementation completely
1. Document: what it validates, how it detects drift, what files it compares
1. Evaluate whether gzkit needs commit-time sync enforcement
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-19-01: Read the opsdev `sync-claude-skills` hook implementation completely
- [x] REQ-0.35.0-19-02: Document: what it validates, how it detects drift, what files it compares
- [x] REQ-0.35.0-19-03: Evaluate whether gzkit needs commit-time sync enforcement
- [x] REQ-0.35.0-19-04: Determine enforcement timing: pre-commit, Claude hook, or both
- [x] REQ-0.35.0-19-05: Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude


## ALLOWED PATHS

- `.pre-commit-config.yaml` — hook configuration
- `src/gzkit/hooks/` — hook implementations
- `.claude/hooks/` — Claude hook configurations
- `tests/` — tests for absorbed hooks
- `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
