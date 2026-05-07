---
id: ADR-pool.evidence-vs-authority-doctrine
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
promoted_to: ADR-0.0.38-evidence-authority-projection-doctrine
---

# ADR-pool.evidence-vs-authority-doctrine: Evidence-vs-authority doctrine
> Promoted to `ADR-0.0.38-evidence-authority-projection-doctrine` on 2026-05-06. This pool file is retained as historical intake context.


## Status

Superseded

## Intent

Two surfaces being proposed in adjacent pool ADRs —
`ADR-pool.solved-problem-pattern-corpus` and
`ADR-pool.advisory-judge-surface` — both pivot on the same distinction:
**evidence-producing surfaces are not authoritative**. Without a
named, foundation-level rule, every future surface re-derives the
boundary, and inevitably one will drift toward gate-shaped use because
nothing names the constraint they inherit.

The state-doctrine layer model (`docs/governance/state-doctrine.md`)
already names a *storage* hierarchy (Layer 1 canon, Layer 2 ledger,
Layer 3 derived views). What is missing is the orthogonal *function*
hierarchy: which surfaces are **authoritative** (their output binds
gate decisions) and which are **evidentiary** (their output informs
operator judgment but does not bind). The two layer models are
orthogonal: an evidentiary surface still produces Layer-2 receipts; an
authoritative surface still derives from Layer-1 canon. Conflating them
is the named risk.

## Decision

_[To be filled at promotion time]_

Sketch — codify a two-axis doctrine:

| Surface kind | Authority | Examples |
|---|---|---|
| **Authoritative** | Output binds gate decisions | `gz validate --*`, `gz audit-check`, schema validators, ARB canonical-step floor, ledger reconciliation |
| **Evidentiary** | Output informs operator judgment, never binds gates | `gz-plan-audit` findings, `gz-adr-evaluate` scores (advisory mode), proposed advisory-judge surface, proposed pattern corpus, `gz-tech-debt-review` |

Foundation-rule deliverable: a new `.gzkit/rules/evidence-vs-authority.md`
naming:

- The two-axis distinction with explicit examples from current surfaces.
- The rule that **promotion from evidentiary to authoritative requires
  a foundation-kind ADR**, never silent uptake by a calling skill.
- The rule that **every new surface declares its axis at authoring
  time** in its `SKILL.md` or rule front-matter, validated by a new
  `gz validate --surface-axis` scope.
- The corollary: an evidentiary surface citing an ARB-shaped receipt
  is producing **evidence, not authority**, even though its receipt
  shape is identical to an authoritative surface's. The receipt-ID
  contract is shared; the binding semantics are not.

## Target Scope

- **rule-and-schema** — Author the canonical rule file at `.gzkit/rules/evidence-vs-authority.md` codifying the three-axis taxonomy (Authoritative / Evidentiary / Projection); register the rule in the advisory-rules-audit scorecard; define the axis-declaration schema fields surfaces must carry (frontmatter for skills/rules; module-level constant for code-level surfaces; CLI registration metadata for validator scopes).
- **surface-axis-validator** — Implement `gz validate --surface-axis` enumerating every surface against the canonical inventory, fail-closing on (a) any surface missing an axis declaration, (b) any caller treating a Projection-tagged surface as a gate input, (c) any Evidentiary-to-Authoritative promotion lacking a foundation-kind ADR justification.
- **retroactive-classification** — One-time audit pass classifying every existing skill, rule, validator scope, code-level fail-closed function (e.g. `_enforce_human_attestation_authenticity`), and Layer-3 derived view (e.g. `gz status` output, `docs/governance/GovZero/adr-status.md`); emit a `surface_axis_classified` ledger event per surface naming axis + rationale; produce `artifacts/audits/surface-axis-2026-05-06.md`.

## Proposed OBPI Decomposition

| Slug | Description |
|---|---|
| `rule-and-schema` | Author `.gzkit/rules/evidence-vs-authority.md` (three-axis taxonomy: Authoritative / Evidentiary / Projection) + register in advisory-rules-audit scorecard + define axis-declaration schema for every surface kind (skill frontmatter, rule body marker, code-level module constant, validator-scope registration) |
| `surface-axis-validator` | Implement `gz validate --surface-axis` (Heavy-lane CLI surface) — enumerates surfaces, fail-closes on missing declarations, on Projection-as-gate-input call shapes, and on Evidentiary→Authoritative promotion without foundation-kind ADR |
| `retroactive-classification` | Classify every existing surface (skills, rules, validator scopes, fail-closed functions, derived views); emit `surface_axis_classified` ledger event per surface; produce `artifacts/audits/surface-axis-2026-05-06.md` baseline |

## Alternatives Considered

1. **Leave the distinction implicit.** Rejected — every new surface
   re-derives the boundary, and at least one will drift to gate-shape
   without a named foundation rule. This is exactly the doctrine-drift
   failure class the anti-vibing mantra exists to close.
2. **Encode the distinction inside each surface's `SKILL.md` without
   a foundation rule.** Rejected — local declaration without a global
   rule leaves the cross-cutting invariant unenforced; advisory
   scorecard cannot grade against a missing rule.
3. **Fold into the storage-tier state-doctrine.** Rejected —
   conflates orthogonal axes. A Layer-2 receipt can be produced by
   either an authoritative or an evidentiary surface; storage tier and
   binding authority are different questions.
4. **Wait until a third surface forces the issue.** Rejected — the
   two pool ADRs already in flight (pattern corpus, advisory judge)
   each need this rule to land cleanly. Deferring guarantees one of
   them will land with implicit drift toward gate-shape.

## Notes

Promotion ordering: this ADR should promote **before** the two pool
ADRs that depend on it (`solved-problem-pattern-corpus`,
`advisory-judge-surface`). Both reference the four-invariant frame
this doctrine names; without it, their invariants are local rather
than inherited.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
