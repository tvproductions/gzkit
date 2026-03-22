---
id: OBPI-0.33.0-09-governance-report
parent_adr: ADR-0.33.0-specialized-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-09: governance-report

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-09 -- "Evaluate and absorb governance report (608 lines) -- governance status reporting"`

## OBJECTIVE

Evaluate opsdev's `governance report` subcommand (608 lines) for absorption into gzkit. At 608 lines, this is the largest specialized command in the evaluation set. The governance report command generates comprehensive governance status reports -- ADR progress, OBPI completion, gate compliance, attestation status, and overall governance health metrics. Determine whether governance reporting belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** governance report implementation (608 lines)
- **gzkit equivalent:** Partial -- `gz adr report` and `gz status` provide some reporting

## ASSUMPTIONS

- 608 lines suggests comprehensive reporting well beyond what `gz adr report` provides
- May include aggregate metrics, trend analysis, compliance scoring
- gzkit's existing reporting commands may be a subset of this capability
- As the governance toolkit, gzkit should likely own comprehensive governance reporting

## NON-GOALS

- Building a dashboard (CLI reporting only)
- Real-time monitoring

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Compare against gzkit's existing reporting (`gz adr report`, `gz status`)
1. Evaluate: Does opsdev's report provide capabilities gzkit lacks?
1. Document decision: Absorb (add to gzkit) or Exclude (existing reporting sufficient)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit's existing reporting is sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed command
- `tests/` -- tests for absorbed command
- `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
