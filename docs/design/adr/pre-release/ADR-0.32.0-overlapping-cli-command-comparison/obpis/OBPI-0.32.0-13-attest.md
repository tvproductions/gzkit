---
id: OBPI-0.32.0-13-attest
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 13
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-13: attest

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-13 -- "Compare attest -- opsdev attestation surface vs gzkit commands/attest.py"`

## OBJECTIVE

Compare opsdev's `attest` command (attestation surface) against gzkit's `commands/attest.py`. Note that ADR-0.25.0 OBPI-01 separately evaluates the core attestation infrastructure module; this OBPI focuses on the CLI command surface -- how attestation is invoked, what flags it accepts, what output it produces, and how it integrates with the governance lifecycle.

## SOURCE MATERIAL

- **opsdev:** attest command surface implementation
- **gzkit equivalent:** `commands/attest.py`

## ASSUMPTIONS

- This is the CLI surface comparison, not the core library comparison (that is ADR-0.25.0 OBPI-01)
- Both implement `gz attest ADR-X.Y.Z --status {completed|in-progress}`
- Flag parity and output format matter for operator experience

## NON-GOALS

- Duplicating ADR-0.25.0 OBPI-01's core attestation evaluation
- Changing the attest command contract without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read both CLI command implementations completely
1. Document comparison: flags, output format, validation, lifecycle integration
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's CLI surface is sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
