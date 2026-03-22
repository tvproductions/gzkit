---
id: OBPI-0.33.0-03-instrumentation-audit
parent_adr: ADR-0.33.0-specialized-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.33.0-03: instrumentation-audit

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.33.0-specialized-command-absorption/ADR-0.33.0-specialized-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.33.0-03 -- "Evaluate and absorb instrumentation-audit (122 lines) -- instrumentation coverage auditing"`

## OBJECTIVE

Evaluate opsdev's `instrumentation-audit` command (122 lines) for absorption into gzkit. The instrumentation-audit command verifies that code instrumentation (logging, metrics, tracing) meets governance standards -- checking that critical code paths have appropriate observability. Determine whether instrumentation auditing is a governance-generic capability that belongs in gzkit.

## SOURCE MATERIAL

- **opsdev:** instrumentation-audit implementation (122 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- Instrumentation auditing may be governance-generic (all codebases need observability)
- 122 lines is moderate; absorption would be manageable if decided
- The audit may check for specific patterns (logging calls, metric emissions) that are configurable

## NON-GOALS

- Adding instrumentation to gzkit itself (only the audit tool)
- Defining instrumentation standards (the tool enforces them)

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Evaluate governance generality: Is instrumentation auditing universally useful?
1. Document decision: Absorb (add to gzkit) or Exclude (too domain-specific)
1. If absorbing: adapt to gzkit conventions, implement, and write tests
1. If excluding: document why gzkit does not need instrumentation auditing

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
