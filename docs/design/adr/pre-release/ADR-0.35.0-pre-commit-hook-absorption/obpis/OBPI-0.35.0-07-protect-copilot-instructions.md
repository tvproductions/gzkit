---
id: OBPI-0.35.0-07-protect-copilot-instructions
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-07: protect-copilot-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-07 — "Evaluate protect-copilot-instructions — instruction file protection (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `protect-copilot-instructions` pre-commit hook — prevents accidental modification or deletion of Copilot/agent instruction files. gzkit does not currently have this hook. Determine: Absorb-PreCommit (protect `.claude/rules/` and related governance files), Absorb-Claude (protect during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit needs similar protection for its `.claude/rules/` directory and `CLAUDE.md`, adapted from Copilot instruction protection to Claude governance protection.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `protect-copilot-instructions`, implementation script
- **gzkit equivalent:** None

## ASSUMPTIONS

- The concept (protecting agent instruction files from accidental modification) is governance-generic
- gzkit's equivalent would protect `.claude/rules/`, `CLAUDE.md`, `.claude/hooks/`
- The implementation may need adaptation from Copilot paths to Claude paths
- Pre-commit timing is ideal — catch accidental instruction file changes before they're committed

## NON-GOALS

- Preventing intentional governance file changes (those go through proper ADR/OBPI process)
- Protecting all files — only agent governance surfaces
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `protect-copilot-instructions` hook implementation completely
1. Document: what files it protects, how it detects changes, what it blocks
1. Evaluate whether gzkit needs equivalent protection for its governance surfaces
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
