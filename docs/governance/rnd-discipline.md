# The R&D discipline

> **Status: RULED.** Frame settled 2026-09-15 → 2026-09-17 across a multi-session design
> discussion. This record **supersedes in part** its own first edition (2026-09-15, *"Accept
> all six (Recommended)"*) — see § What changed from the first edition for exactly which
> rulings moved and why. Evidence:
> [`mpas-appropriation-analysis.md`](mpas-appropriation-analysis.md). The skill this
> specifies is [`.gzkit/skills/gz-rnd/SKILL.md`](../../.gzkit/skills/gz-rnd/SKILL.md).
>
> Operator framing, 2026-09-13, verbatim: *"the mpas appropriation is meant to generate a
> design discussion, not a wholesale onboarding."* And 2026-09-16, verbatim: *"also, we are
> appropriating mpas JUST for r&d."*

Three documents share the letters R&D and must never collapse into one another:

| Term | What it is |
|---|---|
| an **R&D run** | the activity — one governed exploratory session, possibly spanning several |
| an **R&D record** | that run's own document, one per run, at `docs/rnd/<slug>.md` |
| the **R&D discipline record** | *this file* — the single doctrine document governing all runs |

## The frame: a run is diamond 1

**An R&D run IS diamond 1 of the Design Council's double diamond — Discover and Define.**
It ends with the problem defined and a plan naming which fan-out artifacts are warranted,
closed by operator sign-off: kill or fund.

**Diamond 2 is producing those artifacts.** It happens downstream, by machinery that
already carries its own gates — the OBPI pipeline, `ghi-close`, the chore runner, direct
authoring. A run never enters diamond 2.

Three sources compose, each supplying what the others lack:

- **The Design Council** supplies the *shape* and the *gate apparatus*. Its Define phase
  "ends with a clear definition of the problem(s) and a plan for how to address this… ends
  in a project go-ahead through corporate level sign-off." That sentence is the whole of
  diamond 1's contract.
- **MPAS** supplies the *mechanics that run inside each diamond* — the interrogation
  mechanic, the entry-at-the-moment-of-resolution rule, the invocation-class invariant.
- **gzkit** supplies the *six-way fan*, which neither source has, because neither begins
  destination-unknown. MPAS's every entry point is destination-typed before it starts.

Re-entry is native, not an exception: the primary source states that findings "can send
them back to the beginning of their diamond work."

> **A caution about secondary Double Diamond material.** The personas / empathy-map /
> affinity-map / Crazy-8s artifact vocabulary that circulates around the framework appears
> **nowhere** in the primary source; it comes from downstream UX vendor pages. Importing it
> into a governance repo would be furniture.

## Stopping conditions

Both diamonds carry MPAS invariant 4's pair — one mechanical, one human. They answer
different questions and neither substitutes for the other.

| | Mechanical | Human |
|---|---|---|
| **Diamond 1** | the frontier is empty **and** the challenge has been deliberately restated **and** every one of the six dispositions carries a decision | **sign-off — kill or fund** |
| **Diamond 2** | every row carries a disposition | the operator agrees convergence is reached |

**"Deliberately restated"** is satisfied by a restatement made on purpose at the close. It
does not require the challenge to have *changed*.

**Sign-off is a beat, not a boundary** (ruled 2026-09-17). It fires whenever diamond 1's
mechanical condition is met, in the session that met it or a later one. A run that outgrows
one session is carried by the **handoff** system, which already owns exactly that job —
inventing an R&D-specific session-boundary rule would duplicate it and would be a gate with
no mechanism, since nothing can make an operator wait a session. The property a mandated
boundary was reaching for — *does this record stand up to a cold read?* — is delivered
instead by the record being written throughout rather than composed at the end.

**Diamond 2's human condition is the operator agreeing convergence has been reached**, as
MPAS works. Operator verbatim, 2026-09-16: *"we would agree that we've hit convergence,
this is how mpas works."* The IRON LAW is **not** that condition. The IRON LAW gates who
may *initiate* artifact production; a stopping condition asks whether the work is *done*.
Substituting one for the other answers the wrong question.

## The record

One **R&D record** per run, at `docs/rnd/<slug>.md`, **written throughout the run and
finished at the end — never composed at the end.** MPAS is explicit that an entry lands "at
the moment it is resolved, in the middle of the conversation, rather than producing a tidy
glossary at the end."

### Entries: two kinds, and only two

The record **accretes entries**. It is not a form with sections waiting to be filled.

| Kind | Carries |
|---|---|
| `source` | a primary source — **cited, never summarized**, with its verbatim quotation |
| `decision` | something crystallized in session, with the reasoning that produced it, and the operator's verbatim words where they ruled it |

A `decision` may carry a **`commissions:`** field naming the fan-out disposition it
warrants. **A plan item is deliberately not its own kind** — that shape would let work be
commissioned with no recorded reasoning behind it.

Everything else is a **view over the entries**, derived and never separately authored:

- the **plan** is the set of decisions with `commissions:` set;
- the **six-row disposition map** renders from those;
- the **sign-off one-pager** is derivable rather than written.

### `term` and `insight` are not entry kinds

They resolve *outward*, at the moment they resolve, carrying the run id as provenance:

- a **term** writes to [`GLOSSARY.md`](../../GLOSSARY.md) at the repo root;
- an **insight** writes through `gz insights remember`.

The destination points back at the run. **The record never holds a copy** — a copy is the
duplicate state that Layer-3 views become when they shadow Layer-2 truth.

### The disposition map: six rows, two states

All six rows are always present. Every one carrying a decision is half of diamond 1's
mechanical stopping condition, so an absent row is an unfinished run, not a tidy one.

| # | Disposition | The agent may |
|---|---|---|
| 1 | ADR / OBPI | **propose only** — the operator initiates, or not (IRON LAW) |
| 2 | GHI / direct fix | file via the `ghi-author` skill, on the operator's go for that row |
| 3 | chore | **advise only** — the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | draft, on the operator's go for that row |
| 5 | one-shot refactoring | propose a program; the operator selects its route |
| 6 | no action | record it, with the reason |

**State is one of two values — `commissioned` or `not pursued`.** There is deliberately no
third `retained` state (ruled 2026-09-17). Where a finding is set aside but worth revisiting,
the **reason field carries the revisit condition**. Anything that deserves more than a
sentence routes to a **pool ADR** or a **GHI** — surfaces that already have lifecycles,
promotion ceremonies and validators.

The primary source does support a third state: Alessi archives set-aside projects and
revisits them "if trends change"; Yahoo retains out-of-scope findings "for future use." It
was declined because nothing would read the field and nothing would fire the revisit — a
`retained` row would record an intention with no mechanism, which is the
doctrine-declared-without-mechanism family the active campaign is trying to close. The
worked precedent is in-repo: `opencode` is "a future target, keep," and its durable record
is `ADR-pool.vendor-alignment-opencode`, not a field in a document.

### Where records live

`docs/rnd/**` is **excluded from the published site**, alongside `design/**`,
`proposals/**`, `lodestar/**` and `developer/**` — every directory on that list accumulates
and is artifact-shaped. Every piece of exploratory prose gzkit *does* publish
(`user/reference/genesis-transcript.md`, `user/reference/airlineops-exploration-verbatim.md`)
was placed in nav **by hand, one at a time**. Promoting a record stays available and costs
one nav line.

## Ledger events — designed, not built

An R&D run emits ledger events. Operator verbatim, 2026-09-16: *"yes to ledger."* Three of
them:

| Event | Fires |
|---|---|
| `opened` | at the start of the run |
| `sign-off` | at diamond 1's close |
| `run closed` | when the last commissioned row reaches its destination |

A run **killed at sign-off ends at two events**, not three. Operator verbatim: *"yes, closes
at sign-off."*

> **None of this is built, and the vocabulary must not be declared ahead of its producer.**
> Measured 2026-09-17: `src/gzkit/schemas/ledger.json` declares 76 event types and **no**
> `rnd_*` type among them. The `ledger-vocabulary-inertness` chore holds never-fired types
> to a shrink-only disclosure baseline and names the exact hazard — "a declared event type
> that nothing emits is vocabulary with no producer — it reads as a modelled fact and
> records nothing." **These three types land in the same change as the code that emits
> them, never before it.**

## The interrogation

- **Facts are the agent's job; decisions are the operator's.** Search canon and the
  codebase before asking. Dispatch research subagents for facts; do not block a round on
  them.
- **Ask one question at a time** (operator, verbatim: *"ask me the questions one at a
  time"*), each with a recommended answer and its tradeoffs. AGENTS.md § Operator Economy
  #2 already requires the recommendation; MPAS supplies the mechanism.
- **Never ask what canon answers** (AGENTS.md § Operator Economy #7). A settled matter
  presented as an open choice is a drift vector, not merely wasted tokens.
- **Research reports are primary sources.** Save each verbatim beside the record; never
  replace one with a summary.

## Invocation and the hard stop

These survive the first edition unchanged.

**`gz-rnd` is operator-invoked only**, and `disable-model-invocation: true` makes that a
mechanical property rather than prose. Operator verbatim, 2026-09-15: *"it is
operator-invoked, I think the sensing is a mistake because you'd need to deduce that an
exploratory session is meant to be R&D and I am not sure you'd do that realiably"*
(spelling preserved). The sensing arm is **out**.

**An offer is permitted** on four signals, seated in AGENTS.md or `.claude/rules/` rather
than in the skill: a paste of external material with no task attached; framing verbs; no
named artifact target; the subject is gzkit's purpose or shape. Operator verbatim: *"these
are compelling, I think an offer isn't too harmful either."*

**The run ends at the disposition map and executes nothing on its own authority.** Each row
names a **pre-declared** consultation point — pre-declared, never computed from agent
confidence (the Bainbridge finding in [`chore-class-system.md`](chore-class-system.md)
§ Consultation points). The stop lives in the skill file, which the run does not edit, and
in the invocation class, which the run cannot change. This closes the MPAS failure where
`wayfinder`'s *"Plan, don't do"* was overridable by text the agent wrote into its own notes.

**Before proposing disposition 1, ask the admission question:** is the decision hard to
reverse, surprising without context, **and** the result of a real trade-off? If any is
false, the finding routes to disposition 2 or 4.

**No namespace router.** A router over model-invoked disciplines adds a hop that MPAS's
invocation-class invariant exists to remove.

## The MPAS surfaces, named

**MPAS is appropriated JUST for R&D**, and only these surfaces. Inventory taken from
[`mpas-appropriation-analysis.md`](mpas-appropriation-analysis.md) § The source, as read,
which lists eight disciplines and nine orchestrators. **Everything not named below is not
appropriated**, and the reason is recorded — an unlisted surface is a decision, not an
oversight.

### Three disciplines, taken with named departures

The departures are the load-bearing part. Taking a mechanic whole, when gzkit canon already
rules the other way, is how an appropriation smuggles in a foreign posture.

| MPAS surface | What gzkit takes | What gzkit departs from, and why |
|---|---|---|
| **`grilling`** | the subject modelled as a **design tree**; the **frontier** computed as *"every decision whose prerequisites are already settled"*; a **recommended answer on every question**; recompute after each answer; the stopping condition *"the frontier is empty"* paired with the operator confirming shared understanding | **The batching.** MPAS asks *"the whole frontier in one numbered round"*. gzkit asks **one question at a time** — operator verbatim: *"ask me the questions one at a time."* The frontier still governs *which* question is askable next; it no longer governs how many are asked at once. |
| **`research`** | background agent → **primary sources** → one cited `.md`; sources cited, never summarized | **Where it lands.** MPAS writes *"where the repo already keeps such notes"*; gzkit writes the report **verbatim** under `docs/rnd/<slug>/sources/`, beside the run that commissioned it. |
| **`prototype`** | the throwaway probe, built only when talk cannot answer the question, closing on **a one-line verdict** | **The branch.** MPAS runs it on a `prototype/<name>` branch. gzkit forbids branches outright — operator verbatim: *"don't do that feature branch bullshit again."* The probe is built outside the mainline and discarded; no branch is created. |

### Two taken as technique and vocabulary, never as a skill

| MPAS surface | What gzkit takes | The fence |
|---|---|---|
| **`domain-modeling`** | its five inline behaviours — challenge against the glossary, sharpen fuzzy language, discuss concrete scenarios, cross-reference with code, update inline — its capture rule *"Don't batch these up: capture them as they happen"*, and its **`_Avoid_` convention** naming the rejected synonym beside the term that won | **It must not emit ADRs.** MPAS's `domain-modeling` writes `docs/adr/NNNN-slug.md` inline as decisions land. Under the IRON LAW an R&D run **proposes** disposition 1 and never initiates it. gzkit takes the glossary arm and leaves the ADR arm entirely. It is also **not a fourth R&D-scoped skill**: `GLOSSARY.md` is a foundational DDD surface, project-wide, fed by all work, with R&D one contributor among several. Operator verbatim: *"no, other routines use DDD in gzkit, DDD is foundational to gzkit, as are TDD, and BDD."* DDD is not an MPAS import and must never be described as one. |
| **`codebase-design`** | its fixed vocabulary — module, interface, implementation, depth, **seam** (credited to Michael Feathers), adapter, leverage, locality | A reference, not a sequence. A pattern, not a skill. |

### One orchestrator, taken as the shape of the run

**`grill-with-docs`, not `grill-me`.** `grill-me` is stateless — *"writes no files and leaves
no workspace behind"* — and emits nothing. `grill-with-docs` calls `grilling` and
`domain-modeling` together and **emits inline as decisions land**; the source calls it
*"strictly the better one"*, and it is the in-repo door. That is exactly the record
accreting entries and the disposition map maintained live. Operator verbatim: *"yes, so
that is consistent with grill-me-with-docs."*

### Not appropriated, and what already occupies the ground

| MPAS surface | Why not |
|---|---|
| **`wayfinder`** | The R&D-shaped one, and the closest rival to this design — but its core stop, *"Plan, don't do"*, was **overridable by text the agent wrote into its own notes**. gzkit puts the stop in the skill file, which the run does not edit, and in `disable-model-invocation`, which the run cannot change. Its multi-session arm is the **handoff** system's job. |
| **`to-spec`** | gzkit specifies through OBPI briefs and REQs, durable and reconciled (`gz validate --brief-reconcile`). |
| **`to-tickets`** | gzkit decomposes through the ADR Feature Checklist → OBPI 1:1 mandate. |
| **`improve-codebase-architecture`** | the chore estate and `gz-tech-debt-review` hold this ground. |
| **`triage`** | `ghi-triage` holds it. Its `.out-of-scope/<concept>.md` output was declined outright: a rejection is a `not pursued` row in the disposition map, and a third rejection surface beside that map and the rulings store is duplicate state. |
| **`implement`, `implement-spec`** | diamond 2. The OBPI pipeline owns them, with its own gates. |
| **`tdd`, `diagnosing-bugs`, `code-review`** | already foundational here — TDD and BDD are gzkit's own, defect repair routes through § Defect-fix routing and GHIs, and review is the two-stage spec-reviewer + quality-reviewer dispatch. |
| **`handoff`** | gzkit's handoff system exists and writes **in-repo**; MPAS writes to the OS temp dir. The three-system fence governs the word. |

### Disposable working artifacts, durable outcomes

MPAS treats the spec and tickets as throwaway and keeps only the glossary and ADRs. gzkit's
ADRs and OBPI briefs are durable, attested and reconciled. The collision is real but narrow,
and the run must say which is which rather than inherit either posture:

- **disposable** — the probe from `prototype`, and any scratch produced inside the run;
- **durable** — the R&D record itself, its verbatim sources, every `GLOSSARY.md` term, every
  insight, and every artifact a commissioned row routes to.

## Naming collisions, fenced

gzkit already owns these words. An R&D run must not redefine them:

| Word | Already means |
|---|---|
| `brief` | an OBPI brief |
| `gate` | the five-gate covenant; **Gate 5 is OBPI/ADR completion attestation and nothing else** |
| `freeze` | lock-down (LEGO, Virgin) *or* set-aside (Alessi) — **the source collides with itself**; do not import it |
| `work order` | a GHI is the work order and the receipt |
| `CONTEXT.md` | `gz context <ADR-ID>` is a registered verb — which is why the glossary is `GLOSSARY.md` |

**Three agent coinages were caught mid-session and retired.** Each was a wrong model
travelling under a new word:

- **`fan`** — smuggled *one-of-five* when the operator's own note says *any-or-all*.
- **`pinch`** — smuggled *one-way* when re-entry is native.
- **a section template for the record** — smuggled *compose-at-the-end*.

MPAS's own implementer advice covers the class: prefer pretrained metaphors to coined terms.
Follow the `domain-modeling` `_Avoid_` convention and name the rejected synonym alongside
the term it lost to.

## What changed from the first edition

The 2026-09-15 edition's six recommendations were accepted and then partly superseded by
the design discussion that followed. Reading that edition as current would reintroduce two
retired shapes.

| First edition | Now | Why |
|---|---|---|
| record at `docs/governance/rnd/<YYYY-MM-DD>-<slug>.md` | `docs/rnd/<slug>.md` | operator: *"maybe an area of docs that is rnd"* |
| **five required sections** | **two entry kinds**, accreting | the section template smuggled compose-at-the-end and was retired |
| five outcome classes plus take-no-action | **six dispositions**, all six always present | take-no-action is a disposition, not an exception to the list |
| Outcomes state: routed / proposed-awaiting-operator | **`commissioned` / `not pursued`** | two states; the reason field carries any revisit condition |
| first-class promotion deferred until three runs | **three ledger events, designed, unbuilt** | *"yes to ledger"*; the vocabulary lands with its producer |
| phases 0 / 1 / 2 / 3 / 7 | **diamond 1**, with those mechanics inside it | the phase list described the mechanics but not the shape or the gate |
| no glossary surface | **`GLOSSARY.md` at repo root**, foundational DDD | project-wide, fed by all work, not R&D-owned |

Unchanged: invocation class and the sensing-out ruling, the hard stop and its pre-declared
consultation points, the ADR admission question, no namespace router, MPAS appropriated
never onboarded, and the rule that an R&D run stands alone with no ADR.

## Still out of scope

Each needs its own run:

- whether REQ acceptance criteria must fail at the base commit;
- a named expand–contract shape for system-wide refactors;
- whether handoffs should rank below continuing a session.

## What this record does not license

- **It starts no R&D run.** Only the operator invokes `gz-rnd`.
- **It does not declare ledger vocabulary.** The three event types land with their producer.
- **It does not pre-create `docs/rnd/`.** The first run creates it.
- **It does not change the IRON LAW or any canon.**
