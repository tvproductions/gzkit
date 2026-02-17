# Foundational ADR Pattern

This document defines the **foundational ADR pattern** for gzkit-governed projects.

## The 0.0.z Series

Foundational ADRs live exclusively in the **0.0.z series**. They establish governance, architecture, discipline, and tooling patterns that all higher versions depend on.

| Series | Purpose | Scope |
|--------|---------|-------|
| **0.0.z** | Governance & architecture foundations | Cross-cutting, system-wide rules |
| 0.1.x+ | Product features | Feature-specific implementation |

The 0.0.z series must exist before feature work (0.1.x+) begins. These ADRs establish the *rules of the game*—how data is represented, how subsystems interact, how agents report, how governance works.

## ADR-0.0.0: The Organizing Doctrine

Every gzkit-governed project **must** have an ADR-0.0.0 that serves as the **organizing doctrine**. This ADR mirrors the lodestar documents and acts as a directory pointing to where authority lives.

### Required Elements

ADR-0.0.0 must name:

1. **Surfaces** — User-visible products and interfaces the project exposes
2. **Enablers** — What makes surfaces possible (configs, data sources, receipts, tooling)
3. **Proofs** — The evidence pattern (Four Gates + OBPI discipline)

### Authority Hierarchy

ADR-0.0.0 establishes the authority hierarchy:

| Document | Role | Scope |
|----------|------|-------|
| **Lodestar** | Why & What | Target surfaces and features for next major |
| **Roadmap** | How & When | Rolling plan; may change frequently |
| **SemVer ADRs** | Decisions | Atomic, immutable once accepted |

### Governance Discipline

ADR-0.0.0 codifies the proof pattern:

- **Four Gates**: G1 ADR recorded → G2 Tests pass → G3 Docs updated → G4 BDD verified (external contracts only)
- **Gate 5**: Human attestation
- **OBPI**: One Brief Per Item — each ADR checklist item maps to one observable outcome

## Pattern from airlineops ADR-0.0.0

The canonical example is `airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.0-reset-organizing-doctrine.md`:

```
ADR-0.0.0: Reset Organizing Doctrine (Surfaces · Enablers · Proofs)

Intent:
Provide a single organizing ADR for the 0.x reset that:
1. Names the product surfaces we expose
2. Enumerates the enablers that make them possible
3. Fixes a lean proof pattern (Four Gates kept small + OBPI discipline)

This ADR is a directory pointing to where authority lives;
it does not restate those sources.
```

Key characteristics:

1. **Directory, not duplication** — Points to authoritative sources rather than restating them
2. **Surfaces enumerated** — CLI, schemas, ingest, receipts, exports
3. **Enablers enumerated** — Configs, data registry, adapters, normalizers
4. **Proof pattern fixed** — Four Gates + OBPI, with explicit scope limits
5. **Acceptance checklist** — OBPI items with human attestation

## The 0.0.z Progression

After ADR-0.0.0 establishes the organizing doctrine, subsequent 0.0.z ADRs build the foundation:

| ADR | Typical Focus |
|-----|---------------|
| 0.0.0 | Organizing doctrine (surfaces, enablers, proofs) |
| 0.0.1 | Data representation doctrine (JSON-first, canonical formats) |
| 0.0.2 | Data hygiene and schema discipline |
| 0.0.3 | Subsystem boundaries and architecture |
| 0.0.4 | Directory and artifact schema |
| 0.0.5 | I/O doctrine (cross-platform rules) |
| 0.0.6+ | Governance tooling, agent skills, contracts, etc. |

The exact progression depends on project needs, but the pattern holds: **0.0.z establishes rules; 0.1.x+ implements features**.

## Relationship to Lodestar Documents

```
┌─────────────────────────────────────────┐
│            LODESTAR DOCUMENTS           │
│   (gzkit canon: docs/lodestar/)         │
│   - Foundational ADR pattern            │
│   - Gate covenant                       │
│   - Governance invariants               │
└─────────────────┬───────────────────────┘
                  │ mirrors
                  ▼
┌─────────────────────────────────────────┐
│         PROJECT ADR-0.0.0               │
│   (project-specific organizing doctrine)│
│   - Names project surfaces              │
│   - Names project enablers              │
│   - References lodestar for proofs      │
└─────────────────┬───────────────────────┘
                  │ enables
                  ▼
┌─────────────────────────────────────────┐
│         PROJECT 0.0.z SERIES            │
│   (project-specific foundations)        │
│   - Data doctrine                       │
│   - Architecture boundaries             │
│   - Tooling and governance              │
└─────────────────┬───────────────────────┘
                  │ enables
                  ▼
┌─────────────────────────────────────────┐
│         PROJECT 0.1.x+ SERIES           │
│   (actual product features)             │
└─────────────────────────────────────────┘
```

## Enforcement

gzkit enforces:

1. **ADR-0.0.0 required** — No 0.1.x ADR may be accepted without ADR-0.0.0 in place
2. **Lodestar alignment** — ADR-0.0.0 must reference and align with lodestar documents
3. **Proof pattern adherence** — All ADRs must follow the Four Gates + OBPI discipline defined in ADR-0.0.0
