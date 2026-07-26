<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Work Phases and the Airlock — a North Star Model

**Status:** **BINDING** — the airlock's lawful North Star, made binding 2026-07-12 by ADR-0.33.0-airlock-membrane / OBPI-0.33.0-06 (the campaign's Movement III section-8 "1.0 gate"), promoted from its prior draft. The membrane described here is realized: the `gzkit.airlock` primitive is extracted and wired at pipeline Stage 1 (in) / Stage 5 (out), and its enforcement teeth are the registered floor claim `airlock-in-unaccounted-seam`, routed through the `gz validate --qc-binding` meta-validator. Captured from the operator design dialogue of 2026-06-16, apparatus-scanned the same day (5-pass skill scan; findings in §7), and ratified into the Build-to-1.0 campaign (Magna Carta) as item E.7. The *theory of the four phases* lives in its sibling doc [`four-phases-of-work.md`](four-phases-of-work.md); §4 here references it. Working-name terminology (see **Naming** below) still defers to Phase I (completion-before-reduction).

**Naming:** "airlock", "seam", "two-graph", "push/pull" are working names. Final terminology is the operator's to set — the operator has flagged that the five-gate vocabulary "came from one session ten or eleven months ago and stuck" and wants less cryptic terms.

**Why this exists:** gzkit governs *artifacts* (vertical traceability) well and *execution* (the OBPI pipeline) best-in-class. It does not yet give a strong model the single overarching North Star for *the act of working itself* — design, build, fix, refactor. So an agent, unable to hold a complex system resident, patches locally, perturbs laterally, discovers the damage late, and files compounding GHIs ("prior ecosystems of upsets"). This model is the missing glue.

---

## 1. The core idea: model-in / model-out

gzkit's essence is not "five gates." It is **model-in / model-out through a graph**, in four phases, across an **airlock**.

- **The stack (vertical)** — Constitution → PRD → ADR → OBPI → REQ → TASK. Where intent lives, decomposed. *Already exists.*
- **The phases (modes)** — design / build / fix / refactor. *How* you traverse the stack on one unit of work.
- **The airlock (the ritual)** — every entry into the artifact-or-code environment, *including a design act*, crosses the same in/out gate.

> **The airlock's real job is to make the model *not need the whole picture*.** On entry it is *handed* the bounded set of seams a change can touch; it accounts for exactly those and ignores the rest with a clear conscience. The seam-map *is* the externalized working set. This is why the ceremony is *less* cognitive load, not more — it replaces "hold everything" with "hold exactly these N accounted seams."

---

## 2. The two-graph: what a seam is

gzkit exists to make **code and design artifacts that either enable or constrain** — and a seam is both a BODY (a contiguous region of similarity) and a BOUNDARY (the join between regions); the airlock reasons about both. The **body** is the FOOTPRINT (at the pipeline door, the OBPI brief's declared Allowed Paths); the **boundary** is the push/pull edges — a typed relationship between any two artifacts (code or design). Two edge-types, two origins, two layers, two directions:

| edge | origin | provenance | direction | the airlock asks |
|---|---|---|---|---|
| **constrain** | specify with intent | LAW — Layer-1 canon | **pull** ↑ | "what must I satisfy?" (compliance) |
| **enable** | derive from fact | OBSERVED — Layer-3 view | **push** ↓ | "what did I break?" (blast radius) |

Intent-edges are *authored* (parent links, invariants, validators) — prescriptive, "what should relate." Fact-edges *exist materially* (imports, call-sites, `@covers`, `@advances`) — descriptive, "what does relate."

**The defect is the diff.**

- A fact-edge with no intent-edge = a coupling design never sanctioned — *you wrecked something*.
- An intent-edge with no fact-edge = a declared relationship gone slack — *a broken contract*.

"Leave no trace" = leave no unsanctioned gap between push and pull. Every GHI in the backlog is a drift caught late instead of at the airlock.

**State-doctrine guard (ADR-0.0.9):** the graph is irreducibly two-layered. The OBSERVED (fact) projection is a Layer-3 derived view — recomputed, *never stored as truth*. The day OBSERVED is mistaken for LAW, gzkit is dead. Provenance (LAW vs OBSERVED) must be a non-erasable property of every edge, or drift is uncomputable and the airlock is blind.

---

## 3. The airlock: same shape both ways — *tool informs, authority decides*

```text
        declare {target, phase, intent}
                    │
                    ▼
        ┌──────────────────┐   pre-flight checklist (computed seam-map):
        │    AIRLOCK IN     │ → push edges you might break · pull edges that bind you
        └──────────────────┘
                    │  go / no-go   ◄── delegated (small) or captain (large)
                    ▼
             [  do the work  ]      ◄── light review in the routine middle
                    │
                    ▼
        ┌──────────────────┐   drift diff (push vs pull):
        │    AIRLOCK OUT    │ → block · surface · resolve
        └──────────────────┘
                    │
                    ▼
        logged for the captain (ledger = flight recorder)
```

- **Entry** is a **pre-flight checklist → go/no-go decision** — not a wall, not a warning, but *evidence for a decision*. You cannot reach GO without confronting every seam. That is the anti-vibe: you cannot vibe past a go/no-go you had to run the checklist to reach.
- **Exit** is **drift diff → block / surface / resolve.** Not pass/fail — a **tuning loop.** Fact and intent never sit perfectly aligned; the airlock keeps them tuned; drift is the error signal, not the enemy. *Bugs will happen always* → the invariant is **zero *unaccounted* drift**, not zero drift.
  - **block** = halt the exit.
  - **surface** = expose the diff.
  - **resolve** = realign — ratify fact→LAW, fix fact→intent, or amend intent.
- **Review concentrates at the membranes** (entry and exit) and goes light in the routine middle — scrutiny at the crossing, freedom inside the habitat. *(Open: "either" may also mean the blast-radius extremes — heavy at both the trivial and the catastrophic ends — the same principle on a different axis.)*

### Authority — the captain

**The captain (human) has final responsibility.** Authority *delegates*; responsibility does *not*. Blast radius can hand the agent the small calls (delegated authority), but the captain owns every outcome, auto-go included — recorded in the ledger, revocable at any time.

- Blast radius is the **delegation dial**, never a responsibility dial.
- `gz attest` / operator-verbatim attestation remains Gate 5 — the captain's GO at the highest stakes.

---

## 4. The four phases — operations on the two-graph

> **Canonical theory:** the full theory of the four phases — the proof-obligation per phase, the (intent × behavior) signature, the forbidden fifth cell (V.I.B.E.S.), and *"a phase is the proof you can produce, not the intention you declare"* — lives in [`four-phases-of-work.md`](four-phases-of-work.md). What follows is the airlock-specific view: how each phase runs through the airlock as an operation on the two-graph.

Each phase is the same airlock run over a different sub-graph, with a different definition of drift:

| phase | operates on | the work | drift = |
|---|---|---|---|
| **design** | **intent** graph (LAW) | author / edit intent-edges | new intent that strands existing fact — a contract nothing honors |
| **build** | **fact** graph | *add* fact-edges to fulfill intent | a fact-edge no intent sanctioned (scope creep) |
| **fix** | **fact** graph | *repair* fact-edges back onto intent | the repair breaks another fact-edge |
| **refactor** | **fact** graph | *reshape* fact-edges, intent held invariant | *any* behavior change at all |

**Design writes law, build extends fact toward law, fix pulls fact back to law, refactor restyles fact without moving law.**

Refactor is not a fourth wheel — its entire risk surface is lateral (behavior preserved, form changed), so it is the phase the lateral-accountability glue was invented for. Most of "the model wrecked three things it didn't see" is *unaccounted refactoring smuggled inside a build or a fix.*

The phases are *in conversation*: drifting the intent mid-build means you are actually in **design** → stop and re-enter; a fix that reveals the intent was underspecified is a **design** act, not a fix.

---

## 5. The coherence thesis — "the apparatus will tell"

The model does not get to *claim* completeness. It earns its place only where the existing skills and tools snap onto it — **the misfits are the real findings.** The cohering move is **alignment, not invention** (operator: "I have everything it takes for this discipline ... it's just not well governed enough").

Hypotheses to test by scanning the apparatus — not yet claims:

- Every skill/tool maps onto **{phase, airlock-function, which graph}**. The unmappable ones are gaps.
- The computed **blast radius** subsumes the hand-tuned defect-fix routing thresholds (≤10 lines / ≤2 files) *and* the lite/heavy lane call — two hand-maintained surfaces collapse into one computed number.
- The five gates re-file as **pre-flight checklist items / go-no-go criteria**.
- The OBPI pipeline is **the airlock specialized for the build phase**; brief-reconcile is its pre-flight; `gz attest` is the captain's GO.

---

## 6. Open questions / deferred

- **The seam-query depends on the artifact/coupling graph.** Architecture Boundary §12 item 3 — *"do not build the graph engine without locking state doctrine first"* — gates the mechanical form. A *judgment-grade* airlock (agent enumerates seams under discipline, Invariant 1a as the seed, the ledger as memory) is available now; the *tool-computed* airlock waits on the graph.
- **Adopting ADR + alignment campaign.** Re-filing gates, lanes, and routing under this model is foundation work that touches the Build-to-1.0 campaign and needs operator ratification (Magna Carta). Deferred until the apparatus scan shows its shape.
- **Final terminology** (airlock, seam, push/pull) — the operator's to set.
- **The "either" review axis** — membranes vs blast-radius extremes.

---

## 7. Apparatus scan findings (2026-06-16)

A 5-pass scan mapped ~60 gzkit skills onto `{phase, airlock-function, which graph}`. "The apparatus told us":

**Validated.** The four phases are real and populated. `gz-obpi-pipeline` is the full-airlock reference implementation (operator: *"the process that had MOST earned its keep"*) — Stage 1 = pre-flight, Stage 4 = captain's GO, Stage 5 = exit + ledger. `gz-pythonic-pattern-apply` is the refactor exemplar (semantics-pin = "intent invariant"; xenon/radon non-regression = "any behavior change is drift"). `gz-obpi-simplify` is refactoring housed *inside* the build pipeline — confirming the model's claim that wrecking is unaccounted refactor smuggled into build.

**AIRLOCK-OUT is already built; AIRLOCK-IN is not.** The exit membrane is mature: `gz-obpi-brief-drift` (exit-3 = block, report = surface, `--apply` = resolve), `gz-obpi-sync` (withdraws phantoms = intent-edge-with-no-fact), `gz-validate` (the drift-diff engine); plus the captain's-GO membrane (closeout/audit ceremonies, operator-verbatim attestation = "authority decides", ledger = flight recorder). The **entry** membrane has only seam-query *precursors* — `gz-state`, `gz-adr-map`, `gz-context` — no skill computes a seam-map → go/no-go *before* work. That asymmetry is the disease: drift is found on the way out (mature) because there is no pre-flight on the way in. **Building the entry-airlock is the cure**, and `gz-obpi-pipeline` is the pattern to generalize from.

**The airlock is the primitive; the four phases are its code/artifact application.** The unmappable skills cluster into sibling modes that share the airlock's pack-in/pack-out + drift-diff geometry but are not design/build/fix/refactor:

| sibling mode | evidence | what it is |
|---|---|---|
| Intake / horizon-scan | foundation-triage, ghi-triage, competitor-radar | choosing/seeding the target *before* the airlock |
| Meta-governance | content-compose, content-remember, context-diet | reshaping the LAW-surface (the contract) itself |
| Continuity airlock | session-handoff | a per-*session* in/out membrane with a claim-vs-ledger drift gate |
| Surface/repo coherence | agent-sync, parity-scan, tidy, cli-audit | airlock shape over canon→derived / repo→repo drift (a second drift species) |

**Node-internal quality is off-graph.** The two-graph is *edge-only*; the complexity cluster (advisor/guide/distill) measures a property *inside* a node, which neither push nor pull expresses. The model needs a node-health axis or an explicit delegation to a parallel apparatus. Smaller gaps: external/upstream law (deps-upgrade), cross-repo seams (issue-file), phase-polymorphism (chore-runner), concurrency (obpi-lock). Routers (~7) are correctly out of scope — plumbing, not work.

**Disposition.** Ratified into Magna Carta as **E.7**. Alignment (close the sibling-mode + node-health gaps), tuning, and the entry-airlock build are constructive follow-on; renaming defers to Phase I.

---

## Provenance

Captured verbatim-anchored from the operator design dialogue, 2026-06-16. Operator anchors preserved unchanged (economy-of-effort: operator phrasing passes through):

- "model in / model out" — "everything around model go in ... everything around model go out, including ... any design act."
- "pack in, pack out ... leave no trace ... all perturbation and disturbance is accounted for."
- "specify with intent, derive from fact. but. graph it is, regardless. push and pull."
- "block, surface, resolve" — "a defect is a misalignment, but also tuning and alignment. bugs will happen always."
- "it's a pre-flight checklist to inform a go-no-go decision point."
- "captain has final responsibility."
- "the apparatus we place around it will tell. most skills/tools need to align."

**Related:** [State Doctrine](state-doctrine.md) · [Defect-fix routing](defect-fix-routing.md) · [Hexagonal Architecture](hexagonal-architecture.md) · [Trust Doctrine](trust-doctrine.md) · [Build-to-1.0 Campaign](build-to-1.0-campaign-2026-06-10.md)
