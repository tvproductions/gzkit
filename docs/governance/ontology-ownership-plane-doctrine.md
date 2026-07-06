<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Ontology Ownership/Plane Doctrine — Two-Axis Type Model and Boundary Invariants

**Source ADR:** [ADR-0.32.0 — gzkit ontology (object/link plane)](../design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md)

**Purpose:** State how the gzkit ontology classifies every object it images, and record the structural fences that keep the ontology honest. The ontology is a Tier-B derived projection that images the *actual* shape of gzkit's governance, work, and source so that silent reversals light up instead of slipping through as "corrections." This document is the single reference for two questions: *"what kind of object is this?"* (the two-axis type model) and *"what may the ontology never do?"* (the Boundary Invariants).

This is an **orientation surface**, not an enforcement surface. It is audited at ADR closeout (the STRUCTURAL-FENCE proof channel); it is never consumed as governance authority by any `gz validate` scope, gate, or closeout step (see § Boundary Invariant #2). Truth lives in Layer-1 canon and the Layer-2 ledger — this doctrine describes the shape the ontology images over them, it does not adjudicate it.

---

## Two-Axis Type Model

Every object the ontology images is classified on two orthogonal axes. The axes compose: any object carries exactly one value on each, and the pair determines both where the object may appear in the graph and how the ontology reasons about it.

### Axis 1 — Ownership (`harness | product`)

**What it separates:** whether an object type is part of the *universal GovZero harness* or part of *gzkit's own product*.

| Value | Meaning | Examples |
|-------|---------|----------|
| `harness` | A GovZero-universal object type — a governance primitive any GovZero-governed project has, independent of gzkit's specific features. | ADR, OBPI, REQ, GHI, Receipt, TASK, Doc |
| `product` | An object type that exists because gzkit is the thing being built — a feature of gzkit itself, not a governance universal. | CliVerb, Validator, Skill, Chore |

The ownership axis is what the **Harness-Purity Invariant** guards (§ below): the `ownership:harness` subgraph must stay a clean image of the *governance harness* and never accrete gzkit's product objects, or the harness ceases to be portable/universal and becomes a mirror of one project's feature set.

### Axis 2 — Plane (`product | process`)

**What it separates:** whether an object *constrains code* or *constrains governance* — the semantics already seated in the dormant `ontology.schema.json` `plane` field, reused here for continuity-of-naming rather than inventing a fresh term.

| Value | Meaning |
|-------|---------|
| `product` | The object constrains the **built artifact** — code, schemas, runtime behavior (the "product plane"). |
| `process` | The object constrains **how governance proceeds** — ceremonies, gates, attestations, lifecycle (the "process plane"). |

> **Naming caution (why `plane` is this axis, not ownership).** The `plane` field in `ontology.schema.json` canonically means `product|process` (constrains-code vs constrains-governance). Naming the *ownership* axis "plane" would invert a canonical field. The ownership axis is `ownership`; the `plane` axis keeps its dormant-schema meaning. This separation was a rejected-alternative in the parent ADR (`plane: harness|product` axis naming — REJECTED) and is recorded here so the two axes never collapse into one overloaded field.

### Why two axes, not one

The axes are orthogonal by construction: `ownership` answers *"is this a governance universal or a gzkit feature?"* while `plane` answers *"does this constrain code or governance?"* An ADR is `harness` × `process`; a CliVerb is `product` × `product`; a Validator is `product` × `process`. Collapsing them into a single field is exactly the "differing-semantics-under-a-shared-name" rot the ontology exists to kill — one type system resolves the classification by endpoint object-type; two overloaded fields let it drift. The parent ADR validates that the two axes *genuinely partition* the real objects, not merely that they are asserted.

---

## The Harness-Purity Invariant

> **`ownership:harness` admits only GovZero-universal object types. gzkit's own product objects (CliVerb, Validator, Skill, Chore) are `ownership:product` and never appear in the harness subgraph.**

The harness subgraph is the portable image of the governance harness — the objects any GovZero project has. If a gzkit-specific product object (a CLI verb, a validator scope, a skill, a chore) were admitted into `ownership:harness`, the harness image would silently become a mirror of gzkit's feature set, and its portability claim — the thing that makes GovZero a *harness* rather than one project's bespoke governance — would be a lie the graph tells confidently.

Purity is therefore a **fence, not a preference**: a product object pushed into `ownership:harness` is *refused* (the parent ADR lands a Harness-Purity validator with a refusal test in the same increment as the model — OBPI-0.32.0-01). This doctrine records the invariant; the validator enforces it.

---

## Boundary Invariants (STRUCTURAL-FENCE)

These five fences are established by the parent ADR's `## Boundary Invariants` section and are recorded here 1:1. They are **structural fences audited at ADR closeout** via the STRUCTURAL-FENCE proof channel (`resolve_fence_proof` resolves each to `pass` when the parent ADR carries the `## Boundary Invariants` heading) — they are *not* per-OBPI behavior tests, and nothing in this document is itself a gate. Each subsection names the parent-ADR anchor it mirrors.

### BI #1 — Rebuild fidelity: the graph never lies about the shape

*(Parent ADR `## Boundary Invariants` #1 — the load-bearing fence.)*

The Tier-B projection reconstructs from L1 canon + L2 ledger with **no missed event type or silent drop**, and `sense` self-reports its replay completeness and freshness. Completeness is computed by diffing replayed event types against the live `TypedLedgerEvent` discriminator registry — **never a hardcoded handled-type set** — so an event type added by a later ADR surfaces as `complete=False` (unaccounted) instead of being silently dropped while the report still reads `complete=True`. A graph that cannot confess an incomplete or stale replay is a defect.

This is the fence the entire trust premise rests on: the airlock (HATCH) certifies "every seam seen" against this graph, so a rebuild bug or missed event type would let the projection diverge from L1/L2 and certify a stale shape against a lie. A wrong graph is more dangerous than none because it is *trusted*. The deferred-breadth domains (work / source / OKF — OBPIs 05–07) do not begin until this fence is proven live against the registry.

### BI #2 — Derived-never-authority

*(Parent ADR `## Boundary Invariants` #2.)*

The ontology graph is a Tier-B projection: it **never gates**, and no `gz validate` scope, gate, or closeout step consumes it as enforcement evidence. Truth lives in L1 canon and the L2 ledger (state-doctrine Rule 5); the graph is an imaging/navigation aid. Writeback reaches the graph only by rebuild, never by direct edit.

**This doctrine document inherits BI #2 for itself.** It is an orientation surface audited at closeout — it is never read as governance authority against the current corpus. A future `gz validate` scope that consumed this doctrine (or the graph it describes) as a gate would breach BI #2.

### BI #3 — `sense` images structure only

*(Parent ADR `## Boundary Invariants` #3.)*

The `sense` sweep enumerates **STRUCTURAL** seams and never claims semantic completeness; the pre-registered falsifier is *"no un-accounted STRUCTURAL seam."* Semantic-seam recall — *"the code does X, the REQ meant Y"* — is out of scope, deferred to RECALL / Phase-4 as strictly L3-advisory. `sense` is honest about coverage: it labels STRUCTURAL vs semantic and never launders a semantic blind spot into false structural confidence.

### BI #4 — Harness purity

*(Parent ADR `## Boundary Invariants` #4 — the two-axis fence.)*

`ownership:harness` admits only GovZero-universal object types; gzkit's own product objects (CliVerb / Validator / Skill / Chore) are `ownership:product` and never appear in the harness subgraph. This is the fence form of the Harness-Purity Invariant stated above — recorded here so closeout audits the two-axis model actually held.

### BI #5 — OKF absorption stays open

*(Parent ADR `## Boundary Invariants` #5.)*

Doc `subtype` = OKF `type` **verbatim**; no consumer rejects a Doc for an unknown `type`, and no OKF frontmatter or link is consumed as enforcement evidence — preserving OKF (ADR-0.30.0) Boundary Invariants BI-1 and BI-3. A closed-set subset-validator over OKF types would breach both OKF fences and break shipped OKF v0.30.0; open-absorption (subtype = type verbatim) is the only OKF-legal path.

---

## Relationship to State Doctrine

This doctrine sits beside [`state-doctrine.md`](state-doctrine.md): the ontology graph is a **Layer-3 derived view** (state-doctrine Rule 5 — Layer-3 views are never source-of-truth). The two-axis type model and the five Boundary Invariants together are the discipline that keeps the L3 sonar trustworthy — derived-never-authority is not a limitation to work around but the property that lets the graph image the shape without ever becoming the shape.

---

## Related

- [ADR-0.32.0 — gzkit ontology](../design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md) (parent; § Decision, § Boundary Invariants)
- [State Doctrine](state-doctrine.md) (three-layer model; Rule 5 — L3 views never source-of-truth)
- OKF documentation knowledge structure (ADR-0.30.0) — the open-absorption fences BI #5 preserves
