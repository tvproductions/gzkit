---
id: OBPI-0.35.0-01-arb-ruff
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-01: arb-ruff

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-01 — "Evaluate arb-ruff — ARB-wrapped linting (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `arb-ruff` pre-commit hook — an ARB-wrapped version of ruff linting that produces structured receipt artifacts on every commit. gzkit does not currently have this hook. Determine: Absorb-PreCommit (add to gzkit's pre-commit config), Absorb-Claude (add to Claude hooks), Absorb-Both, or Exclude. The key question is whether ARB-wrapped linting at commit time produces enough value over standard ruff linting to justify the receipt overhead.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `arb-ruff`, implementation in `scripts/hooks/` or ARB module
- **gzkit equivalent:** None — gzkit has standard `ruff check` but not ARB-wrapped

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Enforcement timing matters: pre-commit hooks run on every commit, Claude hooks run during agent sessions
- ARB receipt overhead (~5-10% slower) must be justified by the value of structured receipts at commit time
- gzkit already has ARB infrastructure (`uv run -m gzkit arb ruff`) but not as a pre-commit hook

## NON-GOALS

- Rewriting ARB infrastructure — absorb or adapt the hook, don't reinvent ARB
- Changing opsdev — this is upstream absorption only
- Evaluating ARB itself — ARB is already in gzkit; this is about the pre-commit hook wrapper

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `arb-ruff` hook implementation completely
1. Document: what it does, how it wraps ruff, what receipts it produces, performance impact
1. Compare with gzkit's existing `ruff check` pre-commit hook and `arb ruff` CLI command
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
