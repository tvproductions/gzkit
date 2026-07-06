---
id: ADR-pool.hexagonal-folder-structure-realization
status: Superseded
superseded_by: "hexagonal-architecture directive v0.2.0"
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
amendments:
  - date: 2026-07-06
    scope: |
      Superseded by the deliberate v0.2.0 cohesion decision. This pool item's
      whole premise — realizing a domain/application/adapters FOLDER structure
      "enforced by import direction" — was reversed by the hexagonal primary
      directive v0.2.0 (.gzkit/rules/hexagonal-architecture.md rules 7-9;
      docs/governance/hexagonal-architecture.md § the DDD->HA->BDD->TDD
      cascade). Rule 7: "core/ stays; do NOT add
      domain/application/adapters/contexts folder partitions. Bounded contexts
      are subgraphs of the ontology, not directories." The canon names exactly
      this layout the "folder cosplay" trap. Domain cohesion lives in the type
      system (the ontology, ADR-0.32.0), not the folder tree. The one surviving
      concern — mechanizing content-based core purity ("third-party imports
      confined to sanctioned adapter modules; core imports stdlib + Pydantic
      only") — is NOT folder work; if pursued it routes as a direct correction
      under the hexagonal directive, never via this superseded folder ADR.
---

# ADR-pool.hexagonal-folder-structure-realization: Hexagonal Folder-Structure Realization (adapters-outside-core)

> **⚠️ SUPERSEDED (2026-07-06) — retained for history, not for promotion.** The
> hexagonal primary directive **v0.2.0** reversed this pool item's premise. Domain
> cohesion lives in the **ontology type system** (ADR-0.32.0), **not** a
> `domain`/`application`/`adapters` folder tree — which the canon now names the
> **"folder cosplay" trap** (rule 7: *"`core/` stays; do NOT add folder
> partitions; bounded contexts are subgraphs of the ontology, not directories"*).
> Do **not** promote this ADR. See `docs/governance/hexagonal-architecture.md`
> § "The DDD → HA → BDD → TDD cascade" for the governing doctrine.

## Status

Superseded

## Intent

_Superseded — this section records what the pool item **proposed**, now reversed
by v0.2.0._

Realize gzkit's hexagonal **folder structure** — separate the core (logic/intention,
stdlib + Pydantic only) from adapters (real infrastructure implementations carrying
third-party deps) and the driving edge, **enforced by import direction**, so that
"adapters live *outside* the core" becomes a real, mechanized directory discipline
rather than an aspiration.

**Origin (do not re-litigate).** The 2026-07-06 injection-seam ruling (facade
retirement, a correction under ADR-0.0.3) blessed **parameter-injection as gzkit's
canonical hexagon** and retired the dormant `src/gzkit/ports/` + `src/gzkit/adapters/`
+ `tests/fakes/` facade. That correction deliberately **deferred** the folder-structure
rewiring: the operator ruled it "too big to fully rewire" and that gzkit "and
implementing projects are not fully ready to tackle 'lives outside'." This pool item
was the tracked home for that deferred work — until v0.2.0 reversed the direction
itself (see § Decision).

**Scope that was proposed (now moot except where noted).**

- ~~`domain` / `application` / `adapters` / driving-edge zoning~~ — **reversed by
  v0.2.0 rule 7** (no folder partitions; the "folder cosplay" trap).
- **Import-direction enforcement**: extend the existing AST test wall
  (`tests/policy/test_import_boundaries.py`) so "if it imports third-party X it is an
  adapter; core imports only stdlib + Pydantic" is mechanized, not narrated. **This
  is the one surviving concern** — but as *content-based* purity (rule 1), NOT folder
  zoning. If pursued, it routes as a direct correction under the hexagonal directive.
- ~~`*_adapter` / `*_helper` naming for real driven adapters living outside the
  core~~ — **moot** (no outside-the-core relocation).
- ~~Whether/how to relocate existing edge code~~ — **moot** (`core/` stays; no
  relocation).
- ~~**Adopter-project impact**: `gz init` folder scaffolding~~ — **moot**; adopter
  guidance is now the DDD→HA→BDD→TDD cascade (type-system cohesion), not a folder
  layout.

## Decision

**Superseded (2026-07-06).** A deliberate design discussion produced hexagonal
directive **v0.2.0**, which reversed the "adapters live outside the core as a
folder discipline" direction this pool item existed to realize. The binding rule
now holds that **`core/` stays, no `domain`/`application`/`adapters`/`contexts`
folder partitions are added, and bounded contexts are subgraphs of the ontology,
not directories** (rules 7–9). Domain cohesion is a *type-system* property (the
ontology, ADR-0.32.0), not a directory-tree property. This pool item is therefore
**not promotable**; its single surviving concern (content-based core-purity
enforcement) is re-homed as a possible direct correction under the hexagonal
directive, not as folder work.

## Alternatives Considered

- **Do nothing** — leave the injection seam as the canonical hexagon with no folder
  discipline. Was "rejected as the long-term posture" when this item was authored;
  v0.2.0 partially vindicates it — the *positive* v0.2.0 doctrine (type-system
  cohesion + content-based purity) is not "do nothing," but it does reject the
  folder-discipline half this item proposed.
- **Bolt a folder mandate onto the correction** — explicitly rejected by the operator
  (2026-07-06): too big to rewire mid-correction. Now moot: there is no folder mandate
  to bolt (v0.2.0 forbids the partitions).

## Notes

Canon: [`docs/governance/hexagonal-architecture.md`](../../../governance/hexagonal-architecture.md)
(§ "gzkit conformance" records the supersession; § "The DDD → HA → BDD → TDD cascade"
states the governing v0.2.0 cohesion doctrine). Reference reads fed by the operator
2026-07-06: Cockburn *Hexagonal Architecture* talk (folder-first) +
<https://alistair.cockburn.us/hexagonal-architecture>; dev.to *Hexagonal Architecture
in Python* (folder tree). These informed the *proposed* (now superseded) folder
direction.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter. A
Superseded pool item is retained for history and is never promoted (mirrors the
`ADR-pool.obpi-pipeline-dispatch-attestation` absorption precedent).
