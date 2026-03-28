---
id: OBPI-0.35.0-17-md-docs
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 17
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-17: md-docs

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-17 — "Evaluate md-docs — markdown tidy and lint (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `md-docs` pre-commit hook — performs markdown tidying and linting across documentation files. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce markdown quality on every commit), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit's documentation corpus needs automated markdown linting beyond what mkdocs build catches.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `md-docs`, implementation script
- **gzkit equivalent:** None (mkdocs build catches some issues but no dedicated markdown lint hook)

## ASSUMPTIONS

- gzkit has a large documentation corpus (ADRs, manpages, methodology docs, runbooks)
- The hook likely uses markdownlint or similar tool for consistent markdown formatting
- mkdocs build catches link issues but not formatting inconsistencies
- Markdown quality affects readability for both humans and agents

## NON-GOALS

- Changing the markdown style conventions
- Replacing mkdocs validation
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `md-docs` hook implementation completely
1. Document: what tool it uses, what rules it enforces, which files it scans
1. Evaluate whether gzkit needs markdown linting beyond mkdocs build
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
