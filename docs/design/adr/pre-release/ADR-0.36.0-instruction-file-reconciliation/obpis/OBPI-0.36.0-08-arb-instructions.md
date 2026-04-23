---
id: OBPI-0.36.0-08-arb-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-08: arb-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-08 — "Reconcile arb.instructions.md vs AGENTS.md § Attestation + docs/governance/arb-middleware.md"`

> Retargeted 2026-04-23 under GHI #291. Original target `.claude/rules/arb.md`
> was absorbed into `.gzkit/rules/attestation-enrichment.md` on 2026-04-21
> (OBPI-0.25.0-33), then folded on 2026-04-23 under ADR-0.0.20 OBPI-03 into
> two successor surfaces: binding content in `AGENTS.md § Attestation` and
> ARB middleware deep-dive in `docs/governance/arb-middleware.md`. This
> brief's reconciliation now targets those successor surfaces.

## OBJECTIVE

Compare airlineops's `arb.instructions.md` against gzkit's ARB doctrine as it lives today — binding invariants in `AGENTS.md § Attestation` and the middleware deep-dive in `docs/governance/arb-middleware.md`. Both surfaces together govern ARB (Agent Self-Reporting) middleware usage: core concept, when to use ARB, available commands, receipt schema, and exit codes. Determine: Absorb or Confirm, routing absorption decisions to whichever successor surface matches the content class (binding invariant → `AGENTS.md`; pedagogy → `docs/governance/arb-middleware.md`).

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/arb.instructions.md`
- **gzkit binding surface:** `AGENTS.md` § Attestation (pattern, canonical invocations table, lane behavior, applies-to, worked example)
- **gzkit pedagogy surface:** `docs/governance/arb-middleware.md` (core concept, commands, receipt schema/storage, exit codes, rationale)

## ASSUMPTIONS

- Both files describe the same ARB middleware system
- airlineops may have additional ARB commands or usage patterns from operational experience
- gzkit's ARB documentation may be the source of truth (as the governance toolkit)
- Receipt schema references should be consistent

## NON-GOALS

- Changing the ARB architecture
- Adding domain-specific ARB commands to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: core concept, when to use, commands, schema, exit codes
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-08-01: Read both files completely
- [x] REQ-0.36.0-08-02: Create a section-by-section comparison: core concept, when to use, commands, schema, exit codes
- [x] REQ-0.36.0-08-03: Document content gaps in either direction
- [x] REQ-0.36.0-08-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `AGENTS.md` — binding successor surface (§ Attestation) for reconciled content that lands as invariant
- `docs/governance/arb-middleware.md` — pedagogy successor surface for reconciled content that lands as deep-dive
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

### Closing Argument

*To be authored at completion from delivered evidence.*
