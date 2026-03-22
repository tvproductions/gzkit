---
id: OBPI-0.35.0-05-arb-validate
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-05: arb-validate

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-05 — "Evaluate arb-validate — ARB receipt validation (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `arb-validate` pre-commit hook — validates ARB receipt artifacts for schema compliance and consistency on every commit. gzkit does not currently have this as a pre-commit hook (though `uv run -m gzkit arb validate` exists as a CLI command). Determine: Absorb-PreCommit (enforce receipt validation on every commit), Absorb-Claude (validate during agent sessions only), Absorb-Both, or Exclude. The key question is whether commit-time receipt validation catches enough issues to justify the overhead.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `arb-validate`
- **gzkit equivalent:** None as pre-commit hook; `arb validate` CLI command exists

## ASSUMPTIONS

- ARB receipt validation is fast enough for pre-commit enforcement
- Invalid receipts committed to the repo could cause downstream audit failures
- gzkit already has the validation logic; the question is whether to add a pre-commit wrapper
- The hook may catch receipt corruption before it reaches the main branch

## NON-GOALS

- Rewriting ARB validation logic — this is about the pre-commit hook wrapper
- Evaluating ARB receipt schema design
- Modifying opsdev's configuration

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `arb-validate` hook implementation completely
1. Document: what it validates, how it invokes ARB, performance impact
1. Compare with gzkit's existing `arb validate` CLI command
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
