# Design Note — DDD and Palantir Ontology as Lenses on gzkit

**Status:** Draft / design note. Not a proposal. Captured for later consideration.
**Date:** 2026-05-25
**Sources:**
- Book Overflow podcast, *Learning Domain-Driven Design* (Vlad Khononov, O'Reilly) — Part 1 walkthrough, chapters 1–6 (strategic DDD: subdomains, bounded contexts, ubiquitous language; tactical DDD intro).
- Khononov, V. *Learning Domain-Driven Design*. O'Reilly, 2021.
- Palantir Ontology system (Foundry's typed object/action/link/function model over operational data).

## Why this note exists

Reading the podcast adversarially against gzkit's current shape exposed two things worth recording before they fade:

1. gzkit already implements strategic DDD more rigorously than the book's tactical examples — the strategic / tactical split the podcast hosts call out as "skip strategic and you'll regret it" is exactly the failure mode gzkit's anti-vibing doctrine names.
2. Palantir's Ontology lens (typed objects + typed actions + typed links as a first-class artifact) exposes a real gap: gzkit's *governance ontology* is implicit, scattered across schemas, validators, and prose ADRs.

## Where gzkit already lands DDD

| DDD concept | gzkit realization |
|---|---|
| Ubiquitous language | Canonical step commands table; `gz validate --cli-alignment` verb-resolution; persona registry; `.gzkit/rules/*.md` scoped vocabulary |
| Bounded contexts | Skills, rules, schemas, validators, ledger, CLI verbs partitioned with `paths:` scoping (ADR-0.0.20 fail-closes unscoped rules in vendor dirs) |
| Aggregates + events | Layer 1 canon / Layer 2 ledger / Layer 3 derived views = event-sourced DDD + CQRS in all but name; `gz state` is a read model over the ledger stream |
| Strategic-over-tactical | "5:1 governance-to-output ratio is the product, not overhead" mechanizes the podcast's warning against tactical-tornado work |
| Subdomains discovered, not invented | "Doctrine drift is invariant drift"; foundation ADRs as identity-shaping facts, not invented sequence positions (ADR-0.0.57) |
| Core / supporting / generic | Stdlib-first doctrine: stdlib = generic; named departures (Pydantic, uv) = supporting; ledger/gate/attestation = core |

## Where Palantir Ontology lens exposes a gap

gzkit's *ontology itself* — the set of governance object types (ADR, OBPI, Gate, Receipt, Attestation, Insight, Lock, Pipeline, Persona, Lane, Kind) and their typed actions / links — is **implicit**, scattered across:

- `src/gzkit/schemas/` (object shapes)
- Validator code (action preconditions)
- Prose ADRs (semantic intent)
- `.gzkit/rules/**` (cross-object invariants)
- AGENTS.md (lifecycle prose)

The podcast's "what does *closing* mean?" example has a direct gzkit analog: overloaded verbs like *complete*, *ready*, *blocked*, *covered*, *attested* mean subtly different things in OBPI vs ADR vs Gate vs Pipeline contexts. There is no single artifact that disambiguates them per bounded context.

Palantir's lesson: when multiple consumers (skills, CLI, agents, validators) all write back to the same object graph, making the ontology a first-class artifact — typed objects, typed actions, typed links, with explicit context boundaries — pays off in preventing exactly this ambiguity.

## Three candidate impacts, ranked

1. **Canonical ontology surface** (foundation-ADR candidate). One document or generated `gz ontology` view enumerating every governance object type, its allowed state transitions, its bounded context, and its links to neighbors. Replaces "go read 8 ADRs to understand what an OBPI actually is." Natural home for Layer 1/2/3 trust boundaries as ontology-level invariants rather than prose rules.

2. **Verb-coherence audit across bounded contexts**. Mechanical check that overloaded terms (*complete*, *ready*, *blocked*) resolve to a single ontology action per bounded context, analogous to existing `--cli-alignment`. Catches semantic drift where the same word is used for different state transitions.

3. **Subdomain classification (core / supporting / generic) as governance artifact**. Formalizes the stdlib-first doctrine: stdlib = generic, named departures (Pydantic, uv, ruff, ty) = supporting, ledger/gate/attestation/trust-doctrine = core. Makes new-dependency decisions mechanically routable instead of judgment-class.

## Tradeoff

Making the ontology explicit is another layer to keep coherent, and `gz validate --invariant-coherence` already does a constrained version for AGENTS.md re-rendering. The right framing is probably **"lift the ontology out of the rules/schemas into a named artifact"** — not "add a new governance layer" — so the cost is migration, not net new surface. Would want one foundation ADR proposal before doing anything mechanical.

## Anti-takeaway (what this note is NOT recommending)

- **Not** adopting tactical-DDD code patterns (value objects, aggregates-as-classes, getters/setters). gzkit's Python + stdlib-first posture is already orthogonal to that style and the podcast hosts themselves flagged tactical DDD as the part most prone to going wrong.
- **Not** importing Palantir's *implementation* (Foundry, action types as runtime concept). The lesson is that an explicit ontology artifact is valuable; the mechanism would be gzkit-native (JSON schema + validators + a doc surface), not Palantir-shaped.
- **Not** a near-term work item. This is captured for the next time foundation-layer ontology questions surface (e.g., a new object type proposal, a verb-overloading defect, or a trust-doctrine refinement).

## Cross-references

- [`docs/governance/trust-doctrine.md`](../governance/trust-doctrine.md) — T1/T2/T3 layer doctrine
- [`docs/governance/state-doctrine.md`](../governance/state-doctrine.md) — Layer 1/2/3 storage tiers
- [`docs/governance/agent-contract-rationale.md`](../governance/agent-contract-rationale.md) — anti-vibing rationale
- ADR-0.0.20 — scoped rules invariant
- ADR-0.0.57 — foundation IDs as nominal integers
