---
id: ADR-pool.external-strength-absorption-doctrine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.external-strength-absorption-doctrine: External Strength Absorption Doctrine

## Status

Pool

## Intent

Codify the doctrine for absorbing strengths from comparator systems without
turning gzkit into a lighter, trust-by-convention workflow tool.

The operator-approved statement is the seed invariant:

> gzkit should not chase competitors by becoming lighter. Its edge is heavier:
> ledger, receipts, validators, doctrine, attestation. The way to absorb
> competitor strengths is to improve the front door and the compounding loop
> while making every borrowed workflow mechanically witnessed.

This belongs in its own pool ADR because it is not merely a workflow feature.
It is an identity-shaping rule about how gzkit learns from outside systems:
borrow UX and compounding advantages, never borrow the weaker trust boundary.

**Target promotion kind:** foundation candidate.

**Comparator signals:** GitHub Spec Kit, Kiro, Tessl, Specmatic, BMAD, Compound
Engineering, GSD, Superpowers, specledger/betterspec, OpenAPI-style executable
spec ecosystems.

## Decision

When promoted, define an external-strength absorption doctrine with four
binding tests:

1. **Identity preservation test.** A borrowed workflow is acceptable only when
   its gzkit form strengthens or preserves ledger, receipt, validator, doctrine,
   and attestation surfaces.
2. **Front-door test.** Borrowed UX should reduce operator friction at entry
   points such as spec drafting, bugfix routing, and plan review without making
   completion easier to fake.
3. **Compounding-loop test.** Borrowed review or learning patterns must feed a
   governed reuse surface such as insights, pattern corpus, skill feedback, or
   receipt taxonomy.
4. **Mechanical-witness test.** Every borrowed stage carries an observed-output
   witness: receipt IDs, validator scope, ledger event, artifact path, or human
   attestation boundary.

Promotion should add a validator-facing record shape for comparator intake,
probably consumed by `ADR-pool.workflow-specification`,
`ADR-pool.design-references-bibliography`, and future `gz plan`/`gz status`
surfaces. The record should name:

- `source`: comparator project or reference
- `borrowed_strength`: the precise strength being absorbed
- `rejected_imitation`: what gzkit refuses to copy
- `identity_preserved`: ledger/receipt/validator/doctrine/attestation invariant
- `destination`: pool ADR, active ADR, OBPI, GHI, or explicit rejection
- `witness`: receipt, validator, ledger event, or artifact proof

## Alternatives Considered

- **Fold this into workflow specification.** Rejected. Workflow schemas are one
  consumer of the doctrine, but the rule also governs onboarding, context
  packages, review receipts, bugfix specs, and closed-ADR amendments.
- **Treat comparator review as informal research notes.** Rejected. Informal
  notes recreate the training-memory failure mode: useful ideas become
  vibe-shaped recollections instead of routed governance facts.
- **Pursue lighter adoption UX as a standalone priority.** Rejected. gzkit can
  make the front door more ergonomic, but not by removing witnesses from the
  completion path.
- **Create one feature ADR per comparator.** Rejected. The useful unit is the
  borrowed strength and its witness, not the brand name of the comparator.

## Promotion Triggers

- A comparator audit produces more than one destination-worthy lesson.
- A borrowed workflow is proposed for a user-facing command, skill, or pipeline
  stage.
- Closed/validated ADRs need comparator-derived amendment routing.
- Front-door or compounding-loop work risks being framed as "lighter ceremony"
  instead of "better witnessed entry and reuse."

## Related Destinations

- `ADR-pool.operator-first-spec-workspace`
- `ADR-pool.bugfix-spec-routing`
- `ADR-pool.review-receipt-taxonomy`
- `ADR-pool.context-package-registry`
- `ADR-pool.workflow-specification`
- `ADR-pool.design-references-bibliography`

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
