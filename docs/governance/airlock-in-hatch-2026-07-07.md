<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# AIRLOCK-IN — HATCH (Movement III Phase 3, judgment-grade, by hand)

> **Reflexive note.** This is the second application of the entry membrane to the
> act of building the entry membrane — Phase 0 airlocked-in the *constellation*
> (KEEL→HULL→HATCH→RECALL); this pass airlocks-in the **HATCH membrane itself**,
> now that KEEL (v0.31.0) and HULL (v0.32.0, Validated 2026-07-07) are built rock
> beneath it. It reuses the checklist Phase 0 reserved for exactly this:
> *"this record stands as the pre-flight; the seam-map, volume, and falsifiers are
> laid out for audit and reuse as the Phase-3 HATCH checklist."* Operator-attested
> go/no-go is the Gate; this document is the seam-map and volume declaration that
> Gate reviews.
>
> **Mode:** Design (authoring/evaluating intent — the HATCH feature ADR realizing
> the airlock membrane; campaign §3).
> **Authority:** Operator-authorized 2026-07-07 (*"HATCH airlock-in pass
> (seam-map → volume declaration → falsifier)"*) + Magna Carta Movement III
> Phase 3. The campaign governs sequencing.
> **Source-ranking:** L1 canon (`work-phases-and-airlock.md`,
> `four-phases-of-work.md`, campaign §5/§8, ADR-0.31.0/ADR-0.32.0 as-built) > L2
> ledger (this session's insights + the `gz ontology resense`/`seams` sonar
> output recorded below) > L3 derived views (the ontology projection *itself* —
> it **informs**, it never **decides**; state-doctrine Rule 5). External refs
> (Plumb, LightRAG, graspologic) are **bones**, never authority.
> **Topology-purpose:** the **terminal node** of the keel-up constellation
> (KEEL → HULL → **HATCH**) — the membrane that closes the entry-airlock loop.
> Purpose: realize the §8 *"work-phase theories lawful"* 1.0 gate. Per the
> **ABSORBED** loop/topology declaration discipline, HATCH declares its own
> **function** (compute a seam-map → pre-flight → go/no-go at entry) ·
> **topology** (single-door tracer first, breadth after) · **verifier** (the §5
> live NC below) · **termination** (GO refused on un-accounted seam, in un-forced
> production).

## The move

Author **one new feature ADR** (ADR-0.33.0, heavy) that makes
`work-phases-and-airlock.md` **lawful** — the §8 gate — by realizing the
**AIRLOCK-IN** membrane: a judgment-grade `declare → seam-map → pre-flight →
go/no-go → ledger` gate invoked at each existing door (MX-enter,
`gz obpi pipeline` Stage 1). **AIRLOCK-OUT** wires the already-mature exit
surfaces (`gz validate` / `gz-brief-reconcile` / `gz-obpi-reconcile` / closeout)
as the falsifier-check + drift-diff. Bound by the single §5 `@enforces` live NC.

## Re-sense — query the hull (the campaign's Phase-3 precondition)

| Sonar | Result | Reading |
|---|---|---|
| `gz ontology resense` | `+nodes/-nodes/+edges/-edges: (none)` | **No drift since the last sweep.** The hull HULL built has not shifted under HATCH's feet since ADR-0.32.0 validated (2026-07-07). |
| `gz ontology seams` | `STRUCTURAL seams: 0` | **No unaccounted edge-defect drift** in the corpus-domain projection right now. |

**Re-sense gate: GREEN.** HATCH builds on stable rock. **But read `0 seams`
precisely** — it is `0` *STRUCTURAL* (edge-defect) seams. It is **not** `0`
*body*-seams; the tool measures only the boundary sense today (see next section).
Per §3, this sonar **informs** the go/no-go; it does not *reach* GO by itself.

## The seam is two things — the load-bearing refinement (operator, 2026-07-07)

`work-phases-and-airlock.md` §2 declares: *"A seam is therefore not a node-type
but an **edge**."* That captured **one** of the word's two structural senses. Both
matter, and the membrane needs both:

| sense | metaphor | what it is | who reasons about it |
|---|---|---|---|
| **seam-as-body** | *coal seam* / ore vein | a **contiguous stratum of internal similarity** — a coherent region (a domain, a module, an artifact cluster). The seam **is** the volume. | the **footprint** ("which coherent regions does this change live in?") |
| **seam-as-boundary** | *sewn / welded seam* | the **join where two distinct bodies meet** — the demarcation, the locus of tearing. The seam **is** the interface. | the **membrane** ("what crosses here — push ↓ / pull ↑?") |

**Why this is not wordplay — it is the membrane's architecture.** An airlock
*sits at a seam-as-boundary* (the join between inside and outside). But it can
only decide *let-pass / refuse* by knowing the *seam-as-body* on each side (which
coherent region is this, and does the passing thing belong to it?). §2's
"seam = edge" modeled only the boundary. Consequences:

1. **The HATCH ADR must carry both layers**, or the membrane is half-blind — it
   can gate transit but cannot name the regions it mediates. The seam-map below is
   therefore **two-layer**, not one.
2. **The tool already has the boundary layer, not the body layer.**
   `gz ontology seams` returns edge-defects (boundary drift) — built by HULL. The
   **body** layer (which strata/communities exist; latent module structure) is the
   **deferred graspologic option** from the Phase-0 record ("community detection =
   latent module boundaries"). So: *boundary-seam detection = built; body-seam
   detection = judgment-grade now, graspologic-enrichment later.*
3. **An edge-only airlock is blind to intra-body reshaping that touches no edge**
   — which is exactly *"unaccounted refactoring smuggled inside a build or a fix"*
   that §4 names as the core disease. **Seam-as-body is the view that catches
   lateral intra-region perturbation.** This is the sharpest reason the duality
   must land in the HATCH ADR, not be smoothed over.

> **Doctrine delta (finding, not an edit):** when HATCH makes §2 lawful, §2's
> "seam = edge" line must be widened to "a seam is both a **body** (a region of
> similarity) and a **boundary** (the join between regions); the airlock reasons
> about both." I am **not** editing `work-phases-and-airlock.md` in this pass —
> that promotion is the HATCH ADR's work. This records the required change.

## Seam-map — footprint (two-layer)

### Body-layer (seam-as-body: the coherent regions HATCH lives in / touches)

| Region (body) | HATCH's relation |
|---|---|
| **airlock-membrane** (new) | The new `declare → seam-map → pre-flight → go/no-go` surface. HATCH *is* this body. |
| **ontology** (HULL, as-built) | HATCH is a **reader** of `resense`/`seams`/`reach`/`trace` — never a writer (BI#2: the sonar never writes graph state). |
| **OBPI-pipeline** (the build-phase airlock reference impl) | HATCH **generalizes** its Stage-1 pre-flight / Stage-4 GO / Stage-5 exit geometry. Must *abstract*, never *fork*, pipeline semantics. |
| **exit-membrane** (mature) | `gz validate` / `gz-brief-reconcile` / `gz-obpi-reconcile` / closeout. AIRLOCK-OUT **reuses** these as drift-diff — does not rebuild. |
| **doctrine** | `work-phases-and-airlock.md` + `four-phases-of-work.md` promoted Draft North Star → lawful (the §8 gate). |
| **doors** | MX-enter and `gz obpi pipeline` Stage 1 — the existing entries HATCH is "invoked judgment-grade at." |

### Edge-layer — PUSH ↓ (what HATCH may break; blast radius into fact)

| Surface | Why it is in the blast radius |
|---|---|
| The two existing **doors** (MX-enter, pipeline Stage 1) | Inserting a judgment-grade airlock invocation at a **live chokepoint** is a behavior change — must *add* the pre-flight, *preserve* current entry behavior, never replace it. Largest push edge. |
| The **§5 meta-validator registry + runner** | HATCH registers a new `@enforces(claim="airlock refuses GO on un-accounted seam", neg_control=…)`; the registry must accept it and the meta-validator must find + run its live NC. |
| `work-phases-and-airlock.md` **§2 terminology** | Becomes binding, now widened to body+boundary. Any surface quoting the old "seam = edge only" wording must be reconciled in the same move. |
| The mature **exit surfaces** | AIRLOCK-OUT wiring must reuse `gz validate` / reconcile / closeout **without changing their current gating semantics** (L3-advisory stays advisory; fail-closed stays fail-closed). |
| **This campaign file** | Phase 3 box checked in the same move once complete. |

### Edge-layer — PULL ↑ (what binds HATCH; constraints into intent)

| Constraint | Binding |
|---|---|
| **§5 enforcement-claim rule** | *"live negative control ⇒ or the claim is facade ⇒ rejected."* HATCH's GO-refusal claim **REQUIRES** a live NC via `@enforces(claim, neg_control)`, run by the meta-validator through the **un-forced production path** (campaign lines 199, 203–206, 322–323). This is the binding teeth. |
| **§8 gate** | HATCH must *actually make the doctrine lawful* (promote Draft → binding), not merely cite it. That is the 1.0 gate it discharges. |
| **state-doctrine Rule 5 (ADR-0.0.9)** | The ontology projection HATCH reads is **L3**. It may **inform** the go/no-go ("tool informs") but must **never itself fail-close** the gate — the captain decides (§3). |
| **Arch-Boundary §12.3** | "No graph engine before state doctrine is locked." Satisfied: KEEL locked it, HULL built on it; HATCH **inherits** the lock. |
| **Arch-Boundary §12.6** | Derived views never source-of-truth — the computed seam-map is L3-advisory evidence for a human/delegated decision. |
| **Captain's authority (§3)** | Blast radius is a **delegation dial, never a responsibility dial.** Any auto-go (small blast, delegated) still logs to the ledger; the captain owns every outcome. |
| **Heavy lane** | New CLI verb + new ledger event + new `@enforces` claim = runtime-contract change ⇒ all gates, human attestation. |
| **OBPI↔ADR 1:1** | Every HATCH OBPI traces to the HATCH ADR Feature Checklist. No headless OBPIs. |
| **ABSORBED loop/topology discipline** | HATCH — and every new harness mechanism it subsequently gates — declares function · topology · verifier · termination (done for HATCH in the header block). |

## Volume declaration

- **Footprint (breadth):** *moderate* — narrower than the KEEL (which sat on every
  write path). HATCH is a **reader** of the hull + an **inserter** at two existing
  doors + a **promoter** of doctrine. The heavy edges are the two live-door
  insertions and the §5 NC (which must be a *real* refusal, not a mock).
- **Reach (depth / tracer):** the FIRST end-to-end slice is **not** the full
  membrane over every phase and door. It is the airlock-critical tracer:
  `declare{target, phase, intent}` → compute seam-map from `gz ontology reach`
  (push) + parent/invariant lookup (pull) → present pre-flight checklist →
  go/no-go decision → ledger event. **ONE door** (recommend
  `gz obpi pipeline` Stage 1 — the mature reference), **ONE phase** (build), with
  the §5 live NC piercing `declare → seam-compute → checklist → go/no-go → ledger`
  end-to-end. AIRLOCK-OUT, the second door (MX-enter), and the other three phases
  wait for breadth expansion (tracer-bullet discipline; mirrors the KEEL's tracer).

## Pre-registered falsifier(s)

1. **Landing falsifier (keystone — the §5 live NC).** Hand the airlock a *real*
   entry whose declared seam-set **omits an actual push/pull edge** (an
   un-accounted seam), run in **un-forced production** config through the §5
   meta-validator. If the airlock does **not refuse GO**, the keystone is unbuilt
   → the membrane is theater → **NO-GO on completion / breadth expansion** until
   fixed. This *is* the campaign's binding NC (lines 322–323): *"un-accounted seam
   → real entry → assert refuses GO."*
2. **Preservation falsifier (blast radius).** If inserting the airlock invocation
   at the door regresses existing entry behavior — `gz validate --documents` /
   `--cli-alignment` non-green, or the pipeline's current Stage-1 pre-flight
   changes shape — → unaccounted push edge → **block and repair** before
   proceeding.
3. **Body-blindness disclosure (flag, not block).** Because the tool computes only
   **edge**-seams today, a refactor that preserves every edge but reshapes a
   **body's** coherence is *currently outside the deterministic net*. The
   judgment-grade agent enumeration must cover it by hand; the graspologic
   body/community detection is the named future close. Disclosed as a **known
   limitation**, not a build-blocker — same posture as deferred RECALL.

## Go / No-Go

**Recommendation: GO** — author the HATCH feature ADR (ADR-0.33.0), single-door
build-phase **tracer first**, with the §5 live NC as the landing keystone —
**subject to operator attestation.** Gates:

- **This record gates HATCH ADR authoring.** Operator attestation is required
  before `gz-design` / `gz-plan` touch any ADR.
- **The landing falsifier gates HATCH completion/breadth** (live NC refuses GO on
  an un-accounted seam, un-forced production).
- **Re-sense is GREEN** — the hull is stable rock (clean diff, 0 edge-seams).

**Standing boundary (nothing is authored by this record).** Per the operator's
standing distinction (2026-06-30: *"if go means start work, I am not ready to"*)
and Behavior Rule Always #17, even a GO here only *opens the gate* to Phase 3
authoring; the HATCH ADR awaits an explicit **go-to-work** directive. This record
also does **not** itself write the ledger go/no-go event — that write is
Gate-5-shaped and operator-owned (the captain's GO; §3).

---

**Status:** **Phase 3 airlock-in EXECUTED — GO attested (operator, verbatim
"go", 2026-07-07); HATCH ADR-authoring gate OPEN.** Seam-map (two-layer
footprint), volume declaration (footprint + reach tracer), three pre-registered
falsifiers, and the Go/No-Go were laid out for audit; re-sense executed live
(`gz ontology resense` clean; `gz ontology seams` = 0) 2026-07-07; operator
recorded **GO**.

**Boundary held — nothing authored or promoted by this record.** Opening this
gate **authorizes** the HATCH feature ADR (ADR-0.33.0) to be authored; it does
**not** begin it. Per the operator's standing distinction (2026-06-30: *"if go
means start work, I am not ready to"*, re-affirmed in the Phase 0 record) and
Behavior Rule Always #17, HATCH ADR authoring/promotion awaits an explicit
**go-to-work** directive. The landing falsifier (the §5 live NC refuses GO on an
un-accounted seam, un-forced production) remains the gate on HATCH
completion/breadth. Go/no-go channel: insights provenance + this doc Status,
mirroring the Phase 0 precedent (no `gz` go/no-go verb; direct main-ledger writes
forbidden, § Never #2).
**Provenance:** operator authorization 2026-07-07 (*"HATCH airlock-in pass"*) +
the seam double-meaning refinement (operator, same date); Phase 0 constellation
record `airlock-in-constellation-2026-06-30.md`; doctrine
`work-phases-and-airlock.md` §2–§8; campaign `build-to-1.0-campaign-2026-06-30.md`
§5/§8 + Phase 3 checklist.
