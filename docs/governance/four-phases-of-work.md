<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# The Four Phases of Work — Design, Build, Fix, Refactor

**Status:** **BINDING doctrine** — made lawful 2026-07-12 by ADR-0.33.0-airlock-membrane / OBPI-0.33.0-06 (the campaign's Movement III section-8 "1.0 gate"), companion to its now-binding sibling [`work-phases-and-airlock.md`](work-phases-and-airlock.md). That doc holds the *airlock* (the in/out ritual + the two-graph); this doc holds the *theory of the four phases* the airlock is traversed in. Both originate in the operator design dialogue of 2026-06-16 and are ratified into the Build-to-1.0 campaign (Magna Carta) as item **E.7**. Per operator ruling 2026-06-17, Magna Carta could not be complete until these theories were realized, substantiated, and made lawful — this promotion, gated behind the section-5 live negative control biting un-forced in production, discharges that gate.

**Why this exists:** the operator's opening ask was for "a theory of the major phases: design, build, fix, refactor." This is that theory. The airlock doc absorbed the *mechanism*; this doc holds the *modes* — what each phase is, and the distinct proof each one owes.

---

## The core claim

**Each phase is defined by what it must *prove*, and that proof obligation is exactly the surface that makes vibing inert in that phase.** A phase is not chosen by intention; it is determined by the evidence you can produce (see § "A phase is the proof you can produce").

The four phases partition work along two questions, plus one tiebreaker:

- **Does the canonical *intent* change?** — the declared statement of what should be (ADR / REQ / invariant).
- **Does observable *behavior* change?**
- **Tiebreaker (build vs fix):** was the intent *previously realized*?

## The four phases

| phase | intent | behavior | must prove | the vibing it kills |
|---|---|---|---|---|
| **Design** | **changes** | none yet | coherence & traceability — the new intent decomposes down and traces up; no orphan intent | "everyone uses X" architecture; training-corpus-driven choices |
| **Build** | consumes (unchanged) | **new** | intent → behavior — every REQ covered by a passing test | plausible-looking code written without reading the surface |
| **Fix** | unchanged | **corrected** | behavior → intent — a red test proving the defect, now green; fix the *class* | fixing the instance, not the family |
| **Refactor** | unchanged | **preserved** | invariance — behavior unchanged + non-regressing complexity (semantics-pin; xenon/radon) | "cleanup" that silently changes behavior; taste-driven churn |

## Build vs Fix — the correction-vs-enhancement tiebreaker

Build and Fix both change behavior while leaving intent unchanged. They differ on one question: **was the intent previously realized?**

- **Build** realizes intent that was *never yet realized* — a new capability. The gap is "not built yet."
- **Fix** restores intent that *was realized but broke or fell short* — a correction. The gap is "built, but wrong / incomplete against its own declared intent."

This boundary *is* the operator's verbatim doctrine: *"discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction."* The four-phase theory **derives** that doctrine rather than asserting it.

## The forbidden fifth cell

The phases force intent-change and behavior-change into *separate, gated steps*. The cell where **both change at once, in one uncontrolled motion**, is not a fifth phase — it is the named failure class: **V.I.B.E.S.** ("Velocity Increased, Bugs Expected Software"). Changing the spec and the code in the same breath, with no gate between, is exactly what governance exists to forbid: **design must precede build.** The four phases are the four *legal* quadrants of work; vibing is the illegal one.

## A phase is the proof you can produce, not the intention you declare

You do not get to *call* a change a refactor — you are in Refactor only if you can show behavior-invariance. You do not get to call a change a Fix unless you can produce a red→green. **The actor's claim is precisely the vibing surface; the available proof is what is real.** This is why the phase is determined by evidence, not intention — and why each phase's proof-obligation (the table above) is its anti-vibing surface.

## Cross-phase tripwires — the phases are in conversation

A unit of work can discover mid-traversal that it is in a different phase. The tripwires:

- **Drifting the intent mid-build** → you are actually in **Design**. Stop; re-enter through design.
- **A fix that reveals the intent itself was underspecified** → that is a **Design** act, not a fix.
- **Tempted to restructure while building or fixing** → that is **Refactor**. Pull it out into its own gated traversal — never smuggle it in. (Most "the model wrecked three things it didn't see" is unaccounted refactor riding inside a build or a fix.)

## Relationship to the airlock

The four phases are the **modes of traversal** through the airlock (see [`work-phases-and-airlock.md`](work-phases-and-airlock.md)). Each phase's **proof-obligation** above is the airlock's *depth-proof* for that phase — what you must prove about the change itself. The airlock's other invariant, **lateral closure** (pack-in / pack-out; account for every seam perturbed), is universal across all four. And each phase is an *operation on the two-graph*: design writes intent-edges (LAW); build extends fact-edges toward law; fix repairs fact-edges back onto law; refactor reshapes fact-edges with law held invariant (airlock doc § 4).

---

## Provenance

Captured verbatim-anchored from the operator design dialogue of 2026-06-16 (the theory) and the 2026-06-17 ruling (separate doc + 1.0-gating). Operator anchors preserved unchanged:

- "a theory of the major phases: design, build, fix, refactor."
- "discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction." (the build/fix boundary)
- "have magna carta reference them, make it clear that we will never be complete with magna carta until those theories are realized/substantiated/make lawful."

**Related:** [Work Phases and the Airlock](work-phases-and-airlock.md) · [Build-to-1.0 Campaign (E.7 + goal-state)](build-to-1.0-campaign-2026-06-10.md) · [Defect-fix routing](defect-fix-routing.md)
