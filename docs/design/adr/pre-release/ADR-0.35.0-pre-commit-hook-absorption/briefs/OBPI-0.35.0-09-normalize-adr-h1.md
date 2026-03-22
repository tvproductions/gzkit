---
id: OBPI-0.35.0-09-normalize-adr-h1
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-09: normalize-adr-h1

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-09 — "Evaluate normalize-adr-h1 — ADR heading normalization (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `normalize-adr-h1` pre-commit hook — enforces consistent H1 heading format across ADR markdown files. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce heading normalization on every commit), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether ADR heading consistency is important enough for commit-time enforcement and whether gzkit's ADR volume warrants it.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `normalize-adr-h1`, implementation script
- **gzkit equivalent:** None

## ASSUMPTIONS

- ADR heading format consistency aids navigation and automated processing
- The hook likely enforces a pattern like `# ADR-X.Y.Z: Title`
- gzkit has a growing ADR corpus that would benefit from heading consistency
- Pre-commit timing catches format drift before it accumulates

## NON-GOALS

- Changing the ADR heading format convention
- Normalizing non-ADR markdown headings
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `normalize-adr-h1` hook implementation completely
1. Document: what heading format it enforces, how it normalizes, which files it scans
1. Evaluate whether gzkit's ADR corpus needs this enforcement
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

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
