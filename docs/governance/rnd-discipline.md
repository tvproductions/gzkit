# The R&D discipline — 2026-09-15

> **Status: RULED 2026-09-15.** The operator accepted all six recommendations below,
> verbatim: *"Accept all six (Recommended)"*. Each answers one question left open in
> [`mpas-appropriation-analysis.md`](mpas-appropriation-analysis.md) § Undecided, for the
> R&D skill design session and § Questions for the design session. The skill they specify
> is `.gzkit/skills/gz-rnd/SKILL.md`. Operator framing, 2026-09-13, verbatim: *"the mpas
> appropriation is meant to generate a design discussion, not a wholesale onboarding."*

This is the `rnd-discipline.md` record promised in session `5f61ae2b` (2026-09-12) and
never written. It carries no new research: the evidence is in the MPAS record,
[`chore-class-system.md`](chore-class-system.md) and
[`rules-tools-audits-refactors-alignment.md`](rules-tools-audits-refactors-alignment.md),
and this record cites rather than restates them.

## What is already settled

These are operator rulings, carried from the MPAS record's primary quotations. They are
not re-opened here.

- An R&D run **MUST** be governed by a new overarching agent skill, built on gzkit-aligned
  appropriation of MPAS. It stands alone: no ADR.
- The skill is a **chargé d'affaires**: it retains and organizes the possible outcomes of
  a design session, and it is *"sensing but also direct executable."*
- An R&D run fans out to any of five outcomes — ADR/OBPI, GHI/direct fix, chore, control
  surface or doc, one-shot refactoring — **or takes no action**, which is common and must
  be recorded.
- ADR/OBPI outcomes are **operator-initiated only** (IRON LAW). A chore is operator-directed.
- MPAS is appropriated, never onboarded. gzkit's needs govern.
- The artifact's final form is deferred: *"a document and maybe an artifact … VERY LIKELY
  first class."*

## Recommendations, one per open question

The first four are independent of one another and can be ruled together. The fifth and
sixth depend on the first.

### 1. Shape: one user-invoked orchestrator over existing gzkit disciplines

**Recommend: confirm both tentative in-session resolutions.** One skill, `gz-rnd`, declares
`disable-model-invocation: true`. That makes "only the operator starts an R&D run" a
mechanical property rather than prose. The precedent already ships: `.gzkit/skills/git-sync/SKILL.md`
declares it, and `src/gzkit/core/models.py` models the field. Sensing lives in the
model-invoked disciplines the orchestrator reaches; direct execution lives in the
orchestrator.

**The disciplines are gzkit's own, not MPAS clones:** `ghi-author` (outcome 2), the
chores surface (outcome 3, advise only), direct authoring (outcome 4), `gz-design` →
`gz-plan` (outcome 1, *proposed* to the operator, never started), and
`gz-insights-remember`. **No namespace router.** A router over model-invoked disciplines
adds a hop that MPAS's invocation-class invariant exists to remove.

*Alternative, not recommended:* orchestrator plus a `gz-rnd-*` namespace. It adds six to
eight new skills before the first run has shown which ones are needed.

### 2. Phases: route, interrogate, precipitate — chart only across sessions

Of the eight phases in the MPAS record's § The transferable anatomy:

| Phase | In an R&D run? | Why |
|---|---|---|
| 0 Route | **yes** | the run starts by naming what was pasted or asked and which outcome classes are plausible |
| 1 Chart | **only when the run spans sessions** | a map with Destination / Decisions so far / Not yet specified / Out of scope; a null result is a legal exit |
| 2 Interrogate | **yes** | frontier-batched questions, each with a recommended answer (AGENTS.md § Operator Economy #2 already asks for this; MPAS supplies the mechanism) |
| 3 Concretise | optional | a throwaway probe when a question cannot be answered by talk |
| 4 Synthesise, 5 Decompose, 6 Execute | **no — these belong to the destination** | `gz-design`/`gz-plan`, the OBPI pipeline and `ghi-close` already own them |
| 7 Precipitate | **yes** | the run ends by routing each outcome, including not-pursued ones |

**Recommend: the skill defines phases 0, 2 and 7 (with 1 and 3 conditional) and hands off
to destinations for 4–6.** This also satisfies invariant 8 (hide the downstream step): the
run's goal is routing, not building, so interrogation is not rushed toward a plan.

### 3. The record: a document with required sections, first-class later on evidence

**Recommend: document now.** Each run writes `docs/governance/rnd/<YYYY-MM-DD>-<slug>.md`
with five required sections:

1. **Question** — what was asked or pasted, and the operator's framing, verbatim.
2. **Findings** — each with its evidence. Research subagent reports are saved **verbatim**
   beside the record, never summarized (the primary-source failure measured in session
   `5f61ae2b`).
3. **Outcomes** — one row per routed outcome: class 1–5, destination, who initiates, and
   state (routed / proposed-awaiting-operator / not pursued).
4. **Not pursued** — take-no-action and agent-retracted proposals, with the reason.
5. **What this record does not license** — carried from `capability-control-review-2026-09-12.md`.

**First-class promotion is deferred until three runs exist.** Then the question becomes
measurable: did anything need a ledger event (for example `rnd_run_recorded` with routed
outcome ids) that the record could not carry? This follows the operator's *"premature at
this stage"* and gzkit's evidence-before-mechanism posture.

### 4. `.out-of-scope/`: adapt into the record, do not add a directory

**Recommend: adapt.** A rejection lands in the record's **Not pursued** section. `/ghi-author`
Step 0 then gains one grep over `docs/governance/rnd/` so a rejected idea is found as prior art.

Two kinds of rejection stay distinct:

- **An operator-ruled rejection** is a ruling. It is booked through the existing rulings
  store (`gz handoff rulings`) when the handoff that carries it is written.
- **An agent retraction** is not a ruling. It lives only in **Not pursued**.

*Alternative:* adopt `.out-of-scope/<concept>.md` as MPAS does. That creates a third
rejection surface beside the rulings store and the record.

### 5. The hard stop (depends on 1)

**Recommend: the orchestrator ends at the Outcomes table and executes nothing on its own
authority.** Each outcome row names a **pre-declared consultation point**. Pre-declared,
never computed from agent confidence: the Bainbridge finding in `chore-class-system.md`
§ Consultation points.

- **Outcome 2 (GHI) and outcome 4 (doc or rule draft)** may proceed in the same session on
  the operator's per-row go.
- **Outcome 1 (ADR/OBPI)** is proposed only.
- **Outcome 3 (chore)** is advised only.
- **Outcome 5 (one-shot refactoring)** proposes a program, and the operator selects the route.

**The MPAS failure this closes:** `wayfinder`'s *"Plan, don't do"* was overridable by text
the agent wrote into its own notes. Here the stop lives in the skill, which the run does
not edit, and in `disable-model-invocation`, which the run cannot change.

### 6. Whether to ask the ADR admission question (depends on 1)

**Recommend: yes, as one question before proposing outcome 1:** is the decision hard to
reverse, surprising without context, **and** the result of a real trade-off? If not, the
finding routes to outcome 2 or 4. It costs one question and filters ADR accretion, which
Architectural Boundary 2 already resists.

## Out of scope for this skill

These stay separate R&D topics, each needing its own run:

- whether REQ acceptance criteria must fail at the base commit;
- a named expand–contract shape for system-wide refactors;
- whether handoffs should rank below continuing a session.

## Implementation, once ruled

The deliverable is **one skill** authored under `.gzkit/skills/gz-rnd/`: SKILL.md plus a
record template. It is synced with `uv run gz agent sync control-surfaces`. It is a GHI-free,
ADR-free direct authoring task (outcome class 4), consistent with the operator's *"the R&D
skill stands alone."* **The first real run is the acceptance test:** the next paste the
operator offers for gzkit consideration.

## What this record does not license

- **It starts no R&D run.** Only the operator invokes `gz-rnd`.
- **It does not amend the campaign.** That is § Amendments 2026-09-15 of the active plan,
  ratified separately.
- **It does not pre-create `docs/governance/rnd/`.** The first run creates it.
- **It does not change the IRON LAW or any canon.**
