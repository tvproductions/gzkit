---
id: OBPI-0.35.0-14-sync-manpage-docstrings
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 14
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-14: sync-manpage-docstrings

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-14 — "Evaluate sync-manpage-docstrings — manpage-docstring synchronization (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `sync-manpage-docstrings` pre-commit hook — ensures that command module docstrings stay in sync with their corresponding manpage documentation. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce sync on every commit), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit's Gate 5 runbook-code covenant needs automated enforcement beyond documentation policy.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `sync-manpage-docstrings`, implementation script
- **gzkit equivalent:** None (Gate 5 policy requires doc-code sync but no enforcement hook)

## ASSUMPTIONS

- gzkit's Gate 5 runbook-code covenant requires documentation to track behavior changes
- The hook likely compares command module docstrings against manpage content
- Drift between docstrings and manpages is a real documentation quality risk
- The concept is governance-generic — any CLI project with manpages benefits

## NON-GOALS

- Changing the docstring or manpage format
- Auto-generating manpages from docstrings (the hook validates sync, not generates)
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `sync-manpage-docstrings` hook implementation completely
1. Document: how it detects drift, what fields it compares, how it reports violations
1. Evaluate whether gzkit needs this enforcement for its Gate 5 covenant
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
