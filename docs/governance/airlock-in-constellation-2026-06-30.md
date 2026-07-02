<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# AIRLOCK-IN — the airlock-in/out constellation (judgment-grade, by hand)

> **Reflexive note.** The airlock does not yet exist; the *discipline* does. This
> is the first application of the entry membrane — applied, fittingly, to the act
> of building the entry membrane. It models the shape the Phase-3 HATCH ADR will
> mechanize. Operator-attested go/no-go is the Gate; this document is the seam-map
> and volume declaration that Gate reviews.
>
> **Mode:** Design (authoring/evaluating intent — Constitution → PRD → ADR → OBPI
> → REQ → TASK; campaign §3).
> **Authority:** Operator-ratified design dialogue 2026-06-30 + Magna Carta
> Movement III. The campaign governs sequencing.
> **Source-ranking:** L1 canon (pool ADRs, `work-phases-and-airlock.md`) > L2
> ledger (this session's `agent-insights.jsonl` records) > L3 derived views.
> External refs (graphify / LightRAG / Plumb / BEADS / Symphony) are **bones**,
> never authority.
> **Topology-purpose:** a sequential **keel-up constellation build** (one
> parallel-early node: corpus). Purpose: realize the §8 "work-phase theories
> lawful" 1.0 gate. Each new harness mechanism (monitor, graph engine, membrane)
> declares its own function · topology · verifier · termination (the absorbed
> loop/topology discipline).

## The move

Promote/author **four feature ADRs** (pool→feature) realizing the airlock-in/out
system: KEEL (`obpi-state-machine`) → HULL (one graph substrate superseding
`artifact-graph-navigation` + `execution-memory-graph` + `covers-source-anchors`)
→ HATCH (new airlock membrane) → RECALL (`rag-anything`, deferred).

## Seam-map — footprint (breadth)

### PUSH edges — what this move may break (blast radius, ↓ into fact)

| Surface | Why it is in the blast radius |
|---|---|
| 3 superseded pool ADRs | Anything referencing `artifact-graph-navigation` / `execution-memory-graph` / `covers-source-anchors` must be repointed when they are superseded by the HULL ADR. |
| Every governance read/write path | The KEEL's runtime invariant monitor sits on the artifact-graph read/write boundary — it touches every `gz` command that mutates artifact state. Largest push surface in the constellation. |
| `ADR-0.0.16`, `ADR-0.0.24` | Subsumed by the KEEL (coherence guard → monitor rule 4; receipt-binding → `attested` transition witness). Their behavior must be preserved through the subsumption. |
| ~30 audits / reconcilers | The KEEL retires the choreography; each retired reconciler is a behavior that must be re-homed as a transition, not dropped. |
| `gz adr promote` + taxonomy schema | pool→feature promotion runs while the `foundation` enum still exists in schema (mechanical abolition is Movement IV). Promote with `--kind feature`; do not assume the enum is gone. |
| `ADR-0.20.0-spec-triangle-sync` | Coupled to Plumb's spec↔test↔code reconciliation — the HATCH's airlock-out reuses Plumb-bones; keep the two coherent. |
| `work-phases-and-airlock.md` / `four-phases-of-work.md` | Promoted from "Draft North Star" to lawful by the HATCH ADR — their final terminology becomes binding. |
| This campaign file | Edited in the same move (Movement III rewrite + §3a pivot). |

### PULL edges — what binds this move (constraints, ↑ into intent)

| Constraint | Binding |
|---|---|
| **Arch-Boundary §12.3** | "Do not build the graph engine without locking state doctrine first." → KEEL (Phase 1) MUST precede HULL (Phase 2). The monitor *is* the lock. |
| **Arch-Boundary §12.1 / §12.6** | No post-1.0 pool promoted into active work (ours are pre-1.0, OK); derived views never source-of-truth (the Tier-B graph cache + L3 recall must never gate). |
| **§5 enforcement-claim rule** | The HATCH's "refuses GO on un-accounted seam" claim REQUIRES a live negative control; no NC ⇒ facade ⇒ rejected. |
| **STDLIB-FIRST** | `tree-sitter` + `networkx` is a departure — must be attested in the HULL feature ADR (named: deterministic multi-surface extraction + topo-sort/cycle-detection stdlib cannot supply). |
| **state-doctrine Rule 5** | L3 never fail-closes a gate. The fence that makes `graph.json` (Tier-B) and the recall tier (L3) legal assets. |
| **OBPI↔ADR 1:1 mandate** | Every OBPI traces to a parent feature ADR's Feature Checklist. No headless OBPIs. |
| **pool→feature taxonomy (§3a)** | `foundation` abolished; all four promote/author as `feature`, earning back to the release line one at a time with executable proof. |

## Volume declaration

- **Footprint (breadth):** wide — the KEEL alone touches the whole governance
  surface. Accounted above; the supersession + monitor edges are the heavy ones.
- **Reach (depth / tracer):** the FIRST end-to-end slice is **not** the full
  8-property state machine. It is the airlock-critical tracer: `State`/`Transition`
  Pydantic models → withdraw/supersede transition → runtime monitor → CLI verb →
  ledger event, piercing schema → model → monitor → CLI → ledger end-to-end. One
  working keel→hull-corpus→hatch-resense path before breadth expansion
  (tracer-bullet discipline; the deferred-in-keel properties wait).

## Pre-registered falsifier(s)

1. **Landing falsifier (keystone).** If the KEEL monitor does **not** refuse a
   silent `status:` frontmatter drift (the GHI #348 class) when run in
   *production* config, the keystone is unbuilt → re-sense is theater → **NO-GO on
   Phase 2** until fixed.
2. **Preservation falsifier (blast radius).** If superseding the three pool ADRs
   breaks any reference (`gz validate --documents` / `--cli-alignment` non-green)
   → unaccounted push edge → block and repair before promotion.
3. **Sequence falsifier (§12.3).** If HULL (graph) is attempted before KEEL locks
   state doctrine → boundary violated → the graph re-senses drift-prone nodes →
   reject the sequence jump.

## Go / No-Go

**Recommendation: GO**, keel-up, with two gates:

- Phase 0 (this record) gates Phase 1 — operator attestation required before any
  ADR is authored or promoted.
- Phase 1's landing falsifier (monitor refuses silent drift, live) gates Phase 2.

Phase 4 (RECALL) is severable and explicitly deferred past the first working
airlock. The §5 live NC is the binding teeth on the HATCH's GO-refusal claim.

## Deferred / future option — refactored graspologic

`graspologic` (Microsoft/NeuroData graph-statistics: spectral embedding, community
detection, graph matching) was stripped from the hull floor — unused for
seam-queries and not installable on Python 3.13+ (graphify #290). **Kept as a
possible future, not discarded:** a 3.13-compatible refactor (or a thin
extraction of its spectral/community algorithms over the seam graph) could power
*advanced* graph analytics the deterministic floor cannot — "god-node" detection
(over-coupled artifacts), community structure (latent module boundaries),
surprising-connection surfacing. A post-airlock enrichment only; **L3-advisory,
never gating** (state-doctrine Rule 5), peer to the RECALL tier. Parked here as a
named option so the door stays open.

---

**Status:** **Phase 0 EXECUTED — GO attested; Phase 0 → Phase 1 gate now OPEN
(2026-07-02).** Operator authorization (verbatim): *"take on Movement III Phase 0"*
/ *"this: Movement III Phase 0 — airlock-in, operator-gated."* The go/no-go
recommendation below (**GO, keel-up**) is ratified.

The seam-map was **re-sensed against current repo truth before recording GO**
(judgment-grade re-verification, 2026-07-02) — no blast-radius shift since the
2026-06-30 authoring: all five constellation pool ADRs present
(`obpi-state-machine`, `artifact-graph-navigation`, `execution-memory-graph`,
`covers-source-anchors`, `rag-anything-governance-retrieval`); the `foundation`
enum is **still live** in `src/gzkit/schemas/adr.json:36` (confirming the seam-map
directive to promote `--kind feature`, not assume abolition); the subsumption
targets `ADR-0.0.16` / `ADR-0.0.24` and the Plumb-coupled `ADR-0.20.0` all exist;
`work-phases-and-airlock.md` and `four-phases-of-work.md` present.

**Boundary held — nothing authored or promoted in this Phase 0 action.** Opening
this gate *authorizes* Phase 1 (KEEL `obpi-state-machine` promotion) to begin; it
does not itself begin it. Per the operator's standing distinction (2026-06-30:
*"if go means start work, I am not ready to"*) and Behavior Rule Always #17,
Phase 1 ADR authoring/promotion awaits an explicit **go-to-work** directive. The
Phase 1 → Phase 2 gate remains the landing falsifier (monitor refuses silent
`status:` drift, live).

This record stands as the pre-flight; the seam-map, volume, and falsifiers are
laid out for audit and reuse as the Phase-3 HATCH checklist.
**Provenance:** design dialogue 2026-06-30; ratifications + dependency weighing in
`.gzkit/insights/agent-insights.jsonl` (2026-06-30 records); Phase 0 GO record
(2026-07-02) in the same insights channel.
