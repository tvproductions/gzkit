# Lodestar

This directory contains the **foundational canon** for gzkit-governed projects.

These are the philosophical, constitutional, and guiding principles that define what gzkit is and how gzkit-governed projects must operate. They are not suggestions—they are invariants.

## Documents

| Document | Purpose |
|----------|---------|
| [Foundational ADR Pattern](foundational-adr-pattern.md) | The 0.0.z series and ADR-0.0.0 requirement |
| [Project Structure](project-structure.md) | Canonical directory layout for gzkit-governed projects |

## What Belongs Here

Lodestar documents define:

- **Invariant concepts** — Semantic surfaces that all gzkit projects must have
- **Governance discipline** — How proof and attestation work
- **Structural patterns** — Where things live and why
- **Philosophical stance** — The "why" behind opinionated decisions

## What Does NOT Belong Here

- Project-specific configuration (lives in `.gzkit/`)
- Feature documentation (lives in `docs/`)
- ADRs themselves (live in `design/adr/`)

## Relationship to Project ADR-0.0.0

Every gzkit-governed project has an ADR-0.0.0 that **mirrors** these lodestar documents. The project's ADR-0.0.0 is the organizing doctrine that points to lodestar canon and adapts it to the project's specific surfaces and enablers.

```
Lodestar (gzkit canon)
    ↓ mirrors
Project ADR-0.0.0 (project organizing doctrine)
    ↓ enables
Project 0.0.z series (project foundations)
    ↓ enables
Project 0.1.x+ (product features)
```
