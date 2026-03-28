---
id: OBPI-0.35.0-13-validate-manpages
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 13
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-13: validate-manpages

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-13 — "Evaluate validate-manpages — manpage validation (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `validate-manpages` pre-commit hook — validates manpage markdown files for structural completeness and required sections. gzkit does not currently have this hook. Determine: Absorb-PreCommit (validate manpages on every commit), Absorb-Claude (validate during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit's manpage corpus needs structural validation and whether this belongs in pre-commit or Claude hooks.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `validate-manpages`, implementation script
- **gzkit equivalent:** None

## ASSUMPTIONS

- gzkit has manpages in `docs/user/manpages/` that follow a required structure
- The hook likely validates required sections: NAME, SYNOPSIS, DESCRIPTION, OPTIONS, EXAMPLES, EXIT CODES
- Manpage structural drift is a real documentation quality risk
- Validation is fast enough for pre-commit enforcement

## NON-GOALS

- Changing the manpage format convention
- Validating manpage content accuracy (only structure)
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `validate-manpages` hook implementation completely
1. Document: what sections it validates, how it reports violations, which files it scans
1. Evaluate whether gzkit's manpage corpus needs this enforcement
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
