# Project Structure

This document defines the canonical documentation and governance layout for this repository.

## Guiding Principle

Opinionated structure wins over ad-hoc sprawl. Paths can evolve, but semantic surfaces and lineage rules cannot.

## Canonical Layout

```
project/
├── docs/
│   ├── design/
│   │   ├── adr/
│   │   │   ├── foundation/   # ADR-0.0.z packages
│   │   │   ├── pre-release/  # ADR-0.y.z packages (y > 0)
│   │   │   ├── <major>.0/    # ADR-1.y.z, ADR-2.y.z, ...
│   │   │   └── pool/         # ADR-pool.* proposals only
│   │   ├── prd/
│   │   ├── roadmap/
│   │   └── constitutions/
│   ├── governance/
│   ├── user/
│   └── developer/
├── .gzkit/
├── src/
└── tests/
```

## ADR Package Contract

Each promoted ADR is a package directory:

```
docs/design/adr/<bucket>/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md
  ADR-CLOSEOUT-FORM.md
  obpis/
  audit/
```

Pool entries stay as single markdown files under `docs/design/adr/pool/` and do not get OBPI folders.

## OBPI Placement

Canonical location: `docs/design/adr/<bucket>/ADR-.../obpis/`.

`docs/design/obpis/` is forbidden for OBPI authoring and must not contain active OBPI files.

## Invariants

| Concept | Required Surface |
|---|---|
| ADR governance lineage | `docs/design/adr/` |
| PRD lineage root | `docs/design/prd/` |
| Pool-to-promotion flow | `docs/design/adr/pool/` -> promoted ADR package |
| Runtime/tool state | `.gzkit/` |

## Reference

For migration details and settled restructuring decisions, see `docs/design/adr/meta/README.md`.
