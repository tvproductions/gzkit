---
id: ADR-pool.hexagonal-folder-structure-realization
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.hexagonal-folder-structure-realization: Hexagonal Folder-Structure Realization (adapters-outside-core)

## Status

Pool

## Intent

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
is the tracked home for that deferred work.

**Scope to design when promoted.**

- `domain` / `application` / `adapters` / driving-edge zoning (candidate layout from
  Cockburn's folder-first discipline and the Python reference tree
  `domain/ · adapters/ · application/ · api/ · dependencies.py`).
- **Import-direction enforcement**: extend the existing AST test wall
  (`tests/policy/test_import_boundaries.py`) so "if it imports third-party X it is an
  adapter; core imports only stdlib + Pydantic" is mechanized, not narrated.
- `*_adapter` / `*_helper` naming for real driven adapters living outside the core.
- Whether/how to relocate existing edge code (`commands/` = driving adapter /
  configurator; `Ledger(path)`, subprocess runners = driven wiring).
- **Adopter-project impact**: `gz init` scaffolding + adopter guidance for the same
  layout — the "implementing projects" the operator flagged as not-yet-ready.

## Decision

_Deferred — pool backlog. No decision recorded until promotion via `gz adr promote`._

## Alternatives Considered

- **Do nothing** — leave the injection seam as the canonical hexagon with no folder
  discipline. Rejected as the long-term posture (loses the mechanized "adapters
  outside" guarantee) but is the *current* state until this promotes.
- **Bolt a folder mandate onto the correction** — explicitly rejected by the operator
  (2026-07-06): too big to rewire mid-correction; earns its own ADR.

## Notes

Canon: [`docs/governance/hexagonal-architecture.md`](../../../governance/hexagonal-architecture.md)
(§ "gzkit conformance" records the ruling and marks adapters-outside as this pool item's
future work). Reference reads fed by the operator 2026-07-06: Cockburn *Hexagonal
Architecture* talk (folder-first) + <https://alistair.cockburn.us/hexagonal-architecture>;
dev.to *Hexagonal Architecture in Python* (folder tree).

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
