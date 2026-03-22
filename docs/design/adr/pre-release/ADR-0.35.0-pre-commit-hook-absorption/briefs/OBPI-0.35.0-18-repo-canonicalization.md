---
id: OBPI-0.35.0-18-repo-canonicalization
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-18: repo-canonicalization

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-18 — "Evaluate repo-canonicalization — repository structure enforcement (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `repo-canonicalization` pre-commit hook — enforces canonical repository structure by validating that required directories, files, and conventions are maintained. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce structure on every commit), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit needs automated repository structure enforcement and what "canonical" means for a governance toolkit.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `repo-canonicalization`, implementation script
- **gzkit equivalent:** None

## ASSUMPTIONS

- gzkit has a defined repository structure (documented in gzkit-structure.md)
- The hook likely validates: required directories exist, required files present, naming conventions
- Repository structure drift is a real risk as the project grows
- The concept is governance-generic — any structured project benefits

## NON-GOALS

- Changing the repository structure conventions
- Automatically creating missing directories or files
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `repo-canonicalization` hook implementation completely
1. Document: what structure it enforces, how it validates, what it reports
1. Evaluate whether gzkit needs repository structure enforcement
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
