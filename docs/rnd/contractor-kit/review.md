# Contractor kit: the review before sign-off

> A view over [`docs/rnd/contractor-kit.md`](../contractor-kit.md), written 2026-10-27 for the
> operator to read before sign-off. It holds no authority: where it and the record disagree, the
> record governs. Every name below is marked **ruled**, **sourced**, **contradicted** or
> **unsourced**; the vocabulary rows are in [`vocabulary-matrix.md`](vocabulary-matrix.md).

## The problem

The challenge, restated at the close: gzkit was about to run safe mode's repair and restoration work
as prose prompts. The problem is wider than the two contractors. gzkit had no governed apparatus
for maintenance work: no positions kept apart by mechanism, no record of what was isolated, no
inspection independent of the performer, and no closure a reviewer witnesses. Its controls carried
no contract for the condition they run under, so the drydock demoted them from outside, and a
control cannot know it has been demoted.

The original challenge (2026-10-25) also asked *"How many other poorly-handled functions and
processes of MAJOR consequent … do we have in gzkit"*. This run does not answer that. It
commissions the chore that does.

## The model

### Who does the work

| Position | What it does | Separation |
|---|---|---|
| **operator**, always the commander (A1) | initiates every work package; issues change orders; accepts at Gate 5; dispatches surveillance | the only one who overrides the inspector |
| **coordinator** (A3) | the operator-facing session; performs no work; dispatches craftsmen; holds the Authorizing Officer duty on the tag-out log; records commencement; approves pen-and-ink changes; sequences overlapping work | cannot direct, override or filter the inspector |
| **craftsman**, one persona in two positions (A4, A6) | **repair** resists bias toward the present shape; **restoration** resists green by the wrong route | the runtime refuses a session that hung a tag from clearing it |
| **Quality Assurance Inspector** (A5) | inspects at the critical points against the work package and the tag-out log, never against gzkit's present shape | dispatched by the runtime, not by the coordinator; findings reach the operator unedited |
| **surveillant** (A8) | any session outside the work chain; on one of three triggers its stop request becomes a runtime hold | dispatched by the operator only |

The **affected parties** (A7, the operator's definition) are the operator; every gzkit or adopting
system's agent, control surface and rule that enforces system behavior; and, where applicable, the
end users of an adopting system.

### What the work is held to

- **Work package** (B2–B5): every package is a *controlled work package* from opening. It bundles
  its formal work package (initial conditions as tag-out line items, the procedure as task cards,
  test and inspection) with its objective quality evidence.
- **Change ladder** (B10): pen and ink (the coordinator's), **change order** (the operator's, in
  writing), attachment, supplement. The **contract** changes only by its own amendment, never
  through a repair order (B1).
- **Alteration** and **departure from specification** (B9), both measured against the package's own
  approved specification.
- **Tag-out log** (B6, B7) of line items, with Danger and Caution tags. Each line carries its removal
  procedure, written when the tag is hung. **Maintenance record** for the permanent work. **List of
  discrepancies** (B8) for what is left outstanding. The **work package log** (B11) is a Layer 3
  view over the issues and the ledger, never edited.
- **Three tiers of check** (C3): (V) craftsman verification, second person, (I) inspection. A lower
  tier never satisfies a higher mark.

### The life of a work package

1. **Initiated** by the operator (C1, RO-5 ruling 5).
2. **Commencement of work**, recorded by the coordinator once every surface the package works has
   its tag hung (C1). Nothing is worked before both.
3. Work under the task cards. A **stop** is a recorded event routed by its trigger to the one who can
   resolve it (C4). A surveillance stop becomes a hold (A8).
4. After an inspection finding: **rework** by the craftsman, then a **buy-back** by the inspector
   limited to that finding. Only a buy-back closes a finding (C5).
5. **Dock trial** per package, as the package states it.
6. **Final inspection and acceptance** (C10): the inspector checks the record complete and every
   tag cleared; the operator accepts at Gate 5; then **closed**. *Closeout* belongs to the Release
   Package alone.
7. At every session relief inside the hangar, a **shift turnover** (C11): the relieving session
   reviews the tag-out log, the open buy-backs and the commenced packages, and every hung tag passes
   by name. The handoff carries it.

A GitHub issue's role is a **problem report** with AC 00-71's states: recorded, classified,
**resolved** (the fix commit), **closed** (only after a review). The GHI keeps its name (B12).

### Leaving the drydock

- The **sea trial** gates exit, in either approved form: best, a fresh project on the released wheel
  running one work package end to end; better, an increment of real work in gzkit through the
  restored structures while the hangar is still open.
- The **handback** takes the form of a **transfer of custody** (C12). It enumerates every open
  discrepancy, every departure from specification the hangar accepted, and each deferred action
  with its new holder. An empty category says *none*.

### The condition and the mode contract

- **The MX model is defined in this run**; #1273 audits the code against it and owns the repairs.
  The condition belongs to the repository. It is **on** only when the marker is present, readable,
  bound to the ledger and not exiting. It is **one condition with a standby level** commanded at
  entry: **hangar** or **drydock**. A drydock session is defined in `safe-mode-doctrine.md`
  § Maintenance mode (C13).
- **Every control carries a two-way mode contract**, its **Minimum Equipment List entry**, with
  Meyer's levels:
  - inbound: **standby** is the condition's command to reduce its level of compliance, honored at
    the **place of call**, because a control cannot stop itself;
  - outbound: a **built-in self-test** reports **suitability for function**: the latest self-test
    passed within the entry's declared interval.
- Each surface onboards its own contract. Only the signal is central. A control is **accepted and
  lowered** (restored at exit) or **not yet accepted** (enabled by its first acceptance).
- **Acceptance needs a red witness.** A self-test counts only once it has been shown failing against
  a broken input and the QAI has inspected that witness at restoration (ruled 2026-10-28, at the
  design review). Nothing is owed while the work goes on.
- **Syntax.** Code controls use **two decorators joined by reference**: the MEL entry names its
  self-tests, read at the place of call. Non-Python controls declare in their own slot against one
  shared schema.
- **Permanent.** Everything gzkit builds from now on carries the mode contract and its self-test.

### How the kit relates to the pipeline

- The pipeline is **repaired first, then reused unchanged**. Every open defect in a part the kit
  reuses is repaired before reuse.
- Lessons cross both ways, each as a GHI on the side that receives it.
- The **crosswalk** maps each pipeline stage to the kit act it carries. Five rows differ: commencement
  with no isolation; the buy-back done but not named; restore-to-normal after acceptance; turnover on
  a non-abort relief; and the GHI closed on its fix. The last is already carried by B12.

## Names, by standing

- **Ruled and sourced** (the text's own term, A–C rows of the matrix): QAI, surveillant, Authorizing
  Officer duty, controlled and formal work package, objective quality evidence, change order, pen
  and ink, attachment, supplement, alteration, departure from specification, tag-out log, line item,
  Danger and Caution tags, list of discrepancies, discrepancy, maintenance record, task card,
  commencement of work, rework, buy-back, final inspection and acceptance, shift turnover, transfer
  of custody, problem report with resolved and closed, Minimum Equipment List, built-in self-test,
  dock and sea trial.
- **Ruled, gzkit's or the operator's own** (no text term, departure recorded): **operator** and
  **commander** (A1); **coordinator** (rejected: *orchestrator*); **craftsman** with the
  **repair** and **restoration** positions (the earlier *repairer* and *restorer*); **contract**;
  **work package** and **work package log**; **handback**; **drydock** and **hangar** as standby
  levels; **standby**; **affected party** (the operator's definition, not OSHA's test).
- **Ruled with a liberty marked:** A3–A6, A8, B4, B7, B10. Each row says where gzkit departs from its
  text.
- **Contradicted and retired:** *punch list* (B8); *job order* as gzkit's name, kept as DFARS's term
  in the crosswalk (B3); *lockout* and *lockout log* (tag-out); *register* inside the hangar (B11);
  *fix cycle* (C5); *closeout review* (C10); *position relief briefing* (C11); a separate factory
  floor value of the signal.
- **Unsourced:** none is held as a decision. *Availability* was read and not taken, because Volume V
  never defines it.

## What each disposition row would produce

| # | State | Produces |
|---|---|---|
| 1 ADR / OBPI | not pursued | nothing. The kit's home is RO-12 and the mode contract's is row 5. Revisit at civil rule through RO-11's process. |
| 2 GHI / direct fix | commissioned | #1271–#1280, already filed; the pipeline-part repairs before reuse (#1200, #1206, #1208, #1028 and the reused-part set), plus #1273, all before RO-12 lands; the persona-witness GHI; the four crosswalk GHIs; the two self-test defect candidates (exit-3 self-tests colliding with demotion; an assert that passes vacuously), not yet routed. Each is filed through ghi-author on your go on that row. |
| 3 chore | commissioned | the vibe-coded audit chore as a signature catalogue, with five seed signatures; `frontier-model-card-currency` widened to model-level assignments (landed `9649d0eb0`). |
| 4 control surface, rule, doc, skill, hook | commissioned | the kit: the positions and personas, runtime, records, change ladder; contract amendments for RO-12 and RO-13, the contractor brief's order, the division of labor and the section renamed to the list of discrepancies; `safe-mode-doctrine.md` for the MX model, final inspection, transfer of custody and shift turnover; AGENTS.md § Defect-fix routing and the ghi skills for resolved and closed; the handoff skill's turnover section; the vocabulary crosswalk as canon beside Part 0; `gz-rnd`'s both-sides rule; RO-7's per-file persona cap. Each is drafted on your go on that row. |
| 5 one-shot refactoring | commissioned | **RO-13** after RO-12: the two-way mode contract across the 421 code controls and the 206 model-oriented surfaces, in tranches by kind. Its witness is a shrink-only baseline of controls with no MEL entry, closed at zero. The priority order is set when RO-13 is specified with you. |
| 6 no action | commissioned | C13; the handoff not renamed; the GHI not renamed; no separate pipeline design; the not-from-the-start question. |

## The order this sets

RO-5, with the five pre-kit repairs as RO-12's preconditions → **RO-12, the kit** → RO-4 and the
rest under the kit, as its first flight. **RO-13** follows RO-12; its place against RO-4 onward is
set when it is specified. Then the sea trial, the handback and `gz mx exit`.

## What this run does not do

It executes no row. It specifies no tranche, file or test; that is diamond 2. Every row above waits
for your go on that row.
