<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Externalized Metacognition — gzkit's Anti-V.I.B.E.S. Architecture (Design Note)

**Status:** Draft North-Star / **precursor capture** — conversational, pre-decisional.
**Date:** 2026-06-24.
**Origin:** Operator design dialogue (g0), 2026-06-24. Triggered by Lanham, *AI Agents in Action* 2e — Table 5.1, Fig 10.1, Fig 10.2.
**Mode:** Recorded at operator request ("record this for later use"). This is the *Record* terminal of the three-mode interaction contract in §6 — **not an ADR, not a pool entry, not an OBPI, not a plan.** Nothing here is booked or decided.
**Precursor to:** pre-decisional. The gaps in §3 and §7 *may* later spawn foundation ADRs. **None are booked.** A future session promotes specific rows only on operator direction.
**Reading guard (state-doctrine):** this is a Layer-1-adjacent *design note*, never canon and never a derived view. Do not cite it as a decision. It captures thinking, not law.

---

## 1. Why this exists

gzkit governs *artifacts* (vertical traceability) and *execution* (the OBPI pipeline) well. What it has never formed is an **explicit organizing model for the agent's cognition itself** — the act of reasoning, not the act of recording. This note names that missing layer and maps it against existing surfaces so a later session can see, in one place, what is built, what is prose-only, and what is simply absent.

The operator's opening wager, verbatim:

> "gzkit's design intentions are sound, it just needs re-calibration of execution. I've perhaps not paid enough attention to architectural anti-V.I.B.E.S. design."

The skeptical read this note records: those two sentences are in quiet tension, and the second is the more honest. The enforcement *intentions* (structural binding) exist and are partly built — that part of the wager holds. But the **organizing cognition layer was never formed**. This is a **gap, not execution drift.** (Operator agreed with the gap-not-drift read.)

## 2. The core thesis

**gzkit's strategic anti-V.I.B.E.S. bet = externalize metacognition out of the stochastic model into a deterministic harness, so that reasoning-mode selection and self-monitoring fire *structurally* (enforced) rather than *by request* (stochastic).**

A reasoning step that fires *by request* is a V.I.B.E.S. surface — it depends on the model choosing, in the moment, to do the right cognitive thing. A reasoning step that fires *structurally* cannot be vibed away. The whole point is to move metacognition from "the model will remember to self-check" to "the harness will not let the model skip the self-check."

### Two distinctions from Lanham

- **Reasoning primitives are static; cognitive architecture is dynamic (Fig 10.2).** Chain-of-Thought, ReAct, Tree-of-Thought, Reflexion (and self-consistency, plan-execute, least-to-most, debate) are *prompt-defined primitives* — fixed strategies. A *cognitive architecture* is the dynamic process that **selects among them**: Query → **Perception** (classify the problem) → **Attention** (select the reasoning strategy) → branch by class {Simple → Direct; Multistep → Planning/decompose; Ambiguous → Exploration/gather-info; Contradictory → Hypothesis-testing} → **Evaluation** (monitor quality, re-loop on bad output). The primitives become a *selection within the process*, not a thing the operator hand-picks per prompt.
- **Failure modes map to cognitive deficits map to fix-modules (Fig 10.1).** Each production failure is a missing cognitive function, repaired by an architecture module.

## 3. The map — cognitive function → gzkit externalized form → maturity

This is the heart of the note. Lanham's internal fix-modules, re-expressed as gzkit's *externalized* (harness-side, deterministic) forms:

| Lanham fix-module (cognitive function) | Production failure it stops (Fig 10.1) | gzkit externalized form | Maturity |
|---|---|---|---|
| **Evaluation** — monitor output quality, re-loop on bad | Confident-wrong-answer | AIRLOCK-OUT drift-diff / `gz validate` (push-edge "what did I break?") | **Mature** |
| **Confidence gate** — know the knowledge boundary | Overcommitted-guess | Behavior Rule 7 — "<90% sure? ask the human" | **Prose-only** — not mechanical; fires by request, the V.I.B.E.S. surface |
| **Planning** — update the model, don't follow a stale plan | Rigid-plan | Phases-in-conversation + Rule 9 "STOP on inconsistency, don't resolve unilaterally" | **Partial** |
| **Perception / Compositional reasoning** — classify the problem, compose sub-results | Shallow-composition | Seam-map / blast-radius (the two-graph) | **Waits on the graph engine** (Architectural Boundary 3) |
| **Attention / Stagnation-awareness** — detect the broken loop | Broken-record | — | **Absent** — no stagnation detector exists. This is the one module with *zero* gzkit form. |

The Attention/stagnation row is the sharpest finding: it is a genuine hole, not a weak implementation. The nearest unpromoted candidate is `ADR-pool.agent-execution-intelligence` **CAP-10 (analysis-paralysis / stall detection)**, but it sits in a capability grab-bag, not a cognition architecture.

## 4. Gap-not-drift: why the layer was never formed

gzkit's anti-V.I.B.E.S. is organized around **governance ceremony** (gates, ledger, attestation) and a **trust/safety failure taxonomy** (the SIX-pattern axis from the Opus 4.7 / GPT-5.5 system cards: Safeguard-circumvention, Reckless-action, Fabrication, Skipped-cheap-verification, Correction-fails, Dishonest-when-caught). It was **never organized around a cognition model.**

These are two complementary, orthogonal axes:

- **Trust/safety axis (gzkit's SIX patterns):** *will the agent cheat, fabricate, or hide?* — already a first-class organizing taxonomy.
- **Cognition axis (Lanham's five):** *can the agent perceive, plan, self-monitor, compose, and detect its own stalls?* — never formed as an organizing taxonomy; its functions are scattered across prose rules and validators.

Confirming signal: `ADR-pool.agent-reliability-framework` (ARF) explicitly draws the boundary and leaves the cognition side empty — *"ARF deliberately does not try to solve the hard problem (agent cognition). It solves … artifact verification."* The cognition axis is exactly the empty quadrant.

## 5. What already exists, scattered (overlap inventory)

So a future promoter knows the pieces are not zero — they are *unorganized*:

- **`ADR-pool.interpretability-hardened-agent-surfaces`** — states the doctrine verbatim (*"agent-facing surfaces must bind to structural evidence, not narrative recall … replacing 'agent will remember to do X' with 'the system will not let agent X drift'"*) but scopes to three named surfaces, not an architecture.
- **`ADR-pool.agent-execution-intelligence`** — holds the scattered cognition candidates: CAP-10 stall detection (≈ Attention), CAP-21 predictive-failure-match (≈ Perception), CAP-09 goal-backward verify (≈ Evaluation). A capability list, not a unifying model.
- **`ADR-pool.harness-aware-execution-modes`** — the *enforcement substrate* (Mode-1 skill-chain vs Mode-2 hooks) the cognition layer would run on — not the layer itself.
- **`ADR-pool.agent-reliability-framework`** — the verification axis; disclaims cognition (see §4).

**No existing ADR takes the cognitive-architecture lens as gzkit's organizing model.** That absence *is* finding (a).

## 6. Methodological coda — finding (b), the interaction contract, the diet

Recording finding (a) surfaced a second finding of the **same shape**.

**The shared shape:** *the apparatus lacks an explicit home for a kind of work, so that work deforms to fit the nearest recognized container.*

- **(a)** Metacognition has no home → it deforms into prose Behavior Rules and scattered validators.
- **(b)** Pre-ADR design has no *recognized* home → it deforms into pool ADRs. The pool stands at **167 entries**, many of them note-shaped design documents wearing ADR-pool costume. Premature crystallization is itself a V.I.B.E.S. failure — *ceremony applied where exploration belonged*, the mirror image of *prose applied where structure belonged*.

Operator, verbatim:

> "We don't have a design level that predicates ADR creation."
> "gzkit needs to be on a diet."

**The skeptical correction this note records (do not over-read (b)):** the precursor tier is *not missing* — it already exists informally and is heavily used (`docs/governance/` holds ~30 strategy/North-Star/research notes, including this one's siblings `harness-loop-engineering-strategy-note`, `four-phases-of-work`, `external-proving-ground-note`). What is missing is **recognition**: the workflow vocabulary (Constitution → PRD → ADR → OBPI → REQ → TASK) skips it, and the `gz-design` skill's Hard Gate forbids landing there. The fix is therefore small — recognize, don't *invent* a tier. Building a new formal tier with CLI/schema/lifecycle would be over-production: answering "you over-crystallize into ceremony" with *more ceremony* is self-refuting. The diet **is** the fix for (b): the agent stops defaulting past the tier that already exists.

### The three-mode interaction contract (operator holds the triggers)

| Mode | Default? | Trigger | Terminal |
|---|---|---|---|
| **Conversational** | Yes | — | Nothing written. Think out loud. |
| **Record** | No | Operator says "record / capture this" | A precursor doc in `docs/governance/` (status header, "precursor to:", recognized home). *This note is an instance.* |
| **Design** | No | Operator says "let's design X" | `gz-design` runs; an ADR is the legitimate terminal. |

The agent's job is to **name the mode and flag the seams** — surface when a conversational thread has hardened into something worth recording, or has crossed into real design, and offer the pivot. The operator pulls the trigger; the agent never auto-crystallizes.

### The one code-level tooth

`gz-design`'s Hard Gate — *"All artifacts land in GovZero structures: pool ADRs, canonical ADRs, OBPI briefs"* — structurally cannot *not* yield an ADR. That is finding (b) encoded in the skill. A one-line relaxation (add "foundation/precursor document" as a first-class terminal) closes it. **Not proposed here; recorded as the single load-bearing change available when wanted.**

## 7. Considered and not taken (rejected alternatives)

Recorded per the interpretability discipline (a destination written backward is indistinguishable from a reasoned one):

- **Book this as an ADR now.** Rejected — premature crystallization; pre-decisional; violates the diet. The whole session's lesson was *not* to do this.
- **Invent a new formal precursor tier (CLI verbs, schema, lifecycle, gates).** Rejected — over-production; the tier already exists informally; self-refuting to answer ceremony-bloat with ceremony.
- **Treat (b) as a pure agent-disposition tweak, change nothing.** Rejected as under-reaction — the Hard Gate provably forces the ADR terminal and pool=167 shows real deformation; recognition debt would persist and re-deform next session.
- **Build the Attention/stagnation detector now** (finding (a)'s one true hole). Not taken — no decision to build; recorded as a candidate gap only.

## 8. Open threads — pre-decisional, none booked

Gaps a later session *may* (on operator direction) promote into foundation ADRs:

1. **Attention/stagnation detector** — the only cognition module with zero gzkit form (§3).
2. **Confidence-gate mechanization** — move Behavior Rule 7 from prose to a structural fire (§3).
3. **Precursor-tier recognition** — name the tier in the workflow vocabulary + relax the `gz-design` Hard Gate (§6). A correction, not a new tier.

No ADR booked. No pool entry created. No OBPI scoped. The floor remains the operator's.
