---
id: ADR-0.27.0-namespace-router-product-surface
status: Proposed
kind: feature
semver: 0.27.0
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-05-23
promoted_from: ADR-pool.namespace-router-product-surface
---

# ADR-0.27.0-namespace-router-product-surface: Namespace Router Product Surface

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

Adopt a GSD-style namespace router layer as gzkit's first-stage product
surface. The current gzkit skill and CLI surface exposes too much internal
governance ontology up front: ADR, OBPI, ARB, Gate 5, reconcile, attest,
ledger, and adjacent verbs compete for model and operator attention before
the user has experienced value.

GSD's v1.40 namespace router pattern shows the superior product shape:
small first-stage routers keep eager skill-listing token cost low while the
full concrete skill surface remains directly invocable. The model first
chooses an intent namespace, then routes to a concrete sub-skill. gzkit
should adopt that product-surface pattern without weakening the underlying
governance machinery.

## Decision

Create a small namespace-router layer for gzkit skills and, where useful,
matching operator-facing command/help surfaces. Concrete gzkit skills remain
directly invocable; routers are additive entry points that organize intent
before exposing ceremony.

Proposed initial routers:

| Router | Routes to |
|---|---|
| `/gz-workflow` | design, plan, implement, verify, attest, release |
| `/gz-project` | init, upgrade, PRD, constitution, status, state |
| `/gz-governance` | ADR, OBPI, gates, ledger, attestation, reconcile |
| `/gz-quality` | check, lint, test, typecheck, complexity, tech-debt |
| `/gz-context` | handoff, state, map, parity, docs, orientation |
| `/gz-manage` | git-sync, issue, patch release, agent sync, tidy |

Each namespace router should be short: an intent-to-skill table plus a
single instruction to invoke the matched concrete skill directly. The router
must not duplicate the concrete skill's procedure, governance contract, or
verification steps.

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 4
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.27.0-01: **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony.
- [ ] OBPI-0.27.0-02: **router-surface-sync** — Register the six router skills in the canonical skill catalog under `.gzkit/skills/` and refresh generated control-surface mirrors by running `gz agent sync control-surfaces` (mirrors are sync outputs, not edited surfaces).
- [ ] OBPI-0.27.0-03: **router-tables-validator** — Add `gz validate --router-tables` mechanical check — every routed skill resolves to a registered skill on disk, and every concrete skill is reachable from at least one router.

## Target Scope

- Add canonical namespace-router skills under `.gzkit/skills/`.
- Refresh generated control-surface mirrors via `gz agent sync control-surfaces`
  (mirrors under `.agents/skills/`, `.claude/skills/`, `.github/skills/` are
  sync outputs — never edited directly).
- Preserve every concrete skill as directly invocable.
- Update user skill index/docs so namespace routers are presented before the
  flat catalog.
- Record GSD as prior art, specifically the v1.40 namespace meta-skill pattern
  that reduced first-stage router listing cost while preserving direct command
  invocation.

## Non-Goals

- No change to ADR/OBPI/ledger semantics.
- No removal or renaming of concrete skills.
- No replacement of `gz-skill-router`; it remains a deeper lookup aid.
- No command-runtime automation DSL. Routers choose skills; they do not execute
  arbitrary workflows.

## Dependencies

- **Related**: `ADR-pool.focused-context-loader`
- **Related**: `ADR-pool.progressive-context-disclosure`
- **Related**: `ADR-pool.command-aliases`
- **Related**: `ADR-pool.skill-control-surface-contract`
- **Related**: `ADR-pool.workflow-specification`
- **Inspired by**: [GSD](https://github.com/gsd-build/get-shit-done) namespace
  meta-skills (`/gsd-workflow`, `/gsd-project`, `/gsd-quality`,
  `/gsd-context`, `/gsd-manage`, `/gsd-ideate`)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The first-stage router set is accepted as the product surface.
2. The concrete skill inventory is mapped under routers without orphaned
   high-use skills.
3. The generated skill index presents routers before the full flat catalog.
4. Token-cost and choice-cost success metrics are defined.
5. A first-10-minute user path uses routers rather than governance internals as
   the entry surface.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

This is a product-surface correction, not a governance retreat. The underlying
gzkit machinery remains stricter than GSD: append-only ledger, ARB receipts,
lane-aware gates, and human attestation stay intact. The router layer makes
that machinery approachable.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.namespace-router-product-surface` on 2026-05-23; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.27.0 | Pending | | | |
