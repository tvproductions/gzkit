# MPAS appropriation analysis — 2026-09-12

> **MPAS** = Matt Pocock Agent Skills. **Source:** `github.com/mattpocock/skills`,
> v1.2.3, commit `3cca18b`, MIT. Read from a clone on 2026-09-12; rationale layer read
> from official conference transcripts (marked `generated-unreviewed` ASR).
>
> **Stance (operator-directed 2026-09-12):** *"I DO NOT want to onboard Matt's skills
> directly, but think we can appropriate."* and *"we'll examine what is appropriate for
> gzkit, and not the other way around."* Nothing here is vendored, mirrored, or
> installed. This is a source analysis whose findings are **data, never instruction**
> (`.claude/rules/governance-core.md` § Externally-authored tool output).
>
> **Purpose — a design discussion, not an onboarding.** Operator, 2026-09-13
> (verbatim): *"the mpas appropriation is meant to generate a design discussion, not a
> wholesale onboarding."* The source anatomy below is carried in full so the discussion
> works from the source rather than a summary of it. Every shape in it is **material
> for a question**, never an item to adopt; § Questions for the design session is where
> this record ends, and nothing in it is a disposition.
>
> **Completeness (2026-09-13).** This record was first written from the session's
> conversation and then completed against the three research reports themselves — the
> primary anatomy report, the talks-and-rationale addendum, and the per-skill anatomy
> tables — preserved as subagent `a918a64c101473f03` of session `5f61ae2b`.

---

## Why this record exists

gzkit has a newly designated **R&D** class of work — the fourth Workflow front in the
active campaign. Operator characterization, 2026-09-12:

> *"MOST adrs came from an externally or observationally motivated inquiry I develop
> from working with gzkit and reasoning about its purpose … Almost everything
> comprehensive or potentially new usually emerges from this newly-designated R&D class
> of work."*

Earlier in the same session, 21:10Z: *"I commonly do this sort of work and the
documentation and ledger will bear this out. In fact MOST future ADRs come form work
exactly like this work."*

### The vector

Operator, 2026-09-12 21:29Z (verbatim): *"I suspect these Matt Pocock appropriations
will become a new vector for how things enter into gzkit moving forward. not to replace
gzkit workflow direction items and artifacts, but to have better structure to the
exploratory and discursive sessions that usually predicate how new things, or
refinements, enter into gzkit. This is an overarching pattern that is now fairly clear
to me. I see the value of appropriating from Matt Pocock only after having used his
method earlier this summer."*

**R&D governs the pre-artifact phase.** It is not a fifth artifact type beside ADR,
OBPI and GHI. It is the governed shape of the exploratory session that precedes them.
Today that session is productive and ungoverned: whatever structure it has comes from
whoever is driving it.

### The trigger

Operator, 2026-09-12 21:40Z (verbatim): *"Often I will drop in a large copy and paste
and say 'let's consider this for gzkit' (I've done this VERY OFTEN), that is almost
always an occasion for R&D EVEN IF the outcome is 'take no action,' which is also
common. We can agree to not engage after a design session. I will commonly say 'is
there something in here that gzkit is missing or could improve on/from?'"*

### The fan-out, and who initiates each outcome

Operator, 2026-09-12 21:29Z (verbatim): *"R&D leads to: ==> 1)adr/opbi || 2)ghi/direct
fix || 3)chores || 4)control surface/rules/docs/skills/structures/hooks || 5)broad
one-shot refactorings/recalibations that are often system wide. Any of 1-5 could be
impacted by an R&D run. So, I wouldn't trivialize the use of an R&D run."*

**Any or all, from one run** — not one of these per run.

| # | Outcome | Route | Who initiates |
|---|---|---|---|
| 1 | ADR / OBPI | design ceremony | **operator only** — the IRON LAW |
| 2 | GHI / direct fix | `/ghi-author`; a GHI is authorized direct repair | agent may file |
| 3 | chore | registry admission on recurrence evidence | **operator directs**; R&D may advise |
| 4 | control surface, rule, doc, skill, structure, hook | direct authoring | agent may draft |
| 5 | broad one-shot refactoring or recalibration, often system-wide | direct engineering work, **not a chore** | per its own route |
| — | **take no action** | recorded, not silent | — |

Outcome 5 is not a chore. Operator, 2026-09-12: *"not all refactorings are chores, but
most chores cab lead to refactorings."* A one-time refactoring fails the admission
criterion in [`chore-class-system.md`](chore-class-system.md): it is not repetitive
and it leaves enduring value. So **R&D produces refactoring programs; chores produce
refactoring candidates.** R&D reaches the chore registry only indirectly, by advising a
new chore on demonstrated recurrence.

### Where R&D sits on the ladder

At the **propose** rung of the chore class system's ladder: observe, analyze, plan, then
stop and route outward. The campaign's § Workflow fronts already encodes the stop for
the R&D front: *"research does not automatically authorize a new ADR or
implementation."* Only the operator converts an R&D proposal into an ADR — the IRON LAW
binds any R&D skill — and how a skill carries that stop is a design question (§ Where
gzkit is stronger; § Where does the run stop?).

### Worked exemplar: session `5f61ae2b`, 2026-09-12

The run that produced this record is itself a representative R&D run. It opened on an
externally motivated paste — *Python Codebase Architecture Guidelines*, offered against
the pythonic chores — and the operator widened it to the rules / tools / audits /
refactors alignment question.

| Outcome class | What the run produced |
|---|---|
| 1 ADR / OBPI | **none** — ruled out twice: the chore class system discharges under a Movement C box, and the R&D skill stands alone |
| 2 GHI | **advised, not filed** from the R&D itself: one GHI-shaped work order for the chore class system. GHI #936 already covered part of it. GHI #998, filed the same session, came from later unrelated repair and is **not** an outcome of this run |
| 3 chore | the **chore class system** — a redesign of the chore estate rather than a new chore, plus two retracted chore proposals |
| 4 control surface / doc | three design records: [`chore-class-system.md`](chore-class-system.md), this record, and [`rules-tools-audits-refactors-alignment.md`](rules-tools-audits-refactors-alignment.md) |
| 5 one-shot refactoring | **in prospect** — the missing middle scale (package API declaration, catch-all modules) and the 393 `PLC0415` suppressions |
| take no action | the pasted document's domain-folder and "screaming architecture" sections, ruled against by `hexagonal-architecture.md` #7 |

Three lessons from the exemplar belong in the skill.

- **The capture failure.** The run's first handoff recorded the destinations and lost
  the reasoning, and the operator rejected it as one that *"misses the major chore and R&D
  work."* A chargé d'affaires that retains outcomes but not the reasoning behind them has
  failed at its job.
- **The primary-source failure, one level down.** The successor handoff and the first
  pass at these records were built from the conversation's *summaries* of four research
  reports rather than from the reports, and carried roughly half of them. MPAS names the
  mechanism exactly (§ Context boundaries): *"Every move except Continue turns a primary
  source into a secondary source."* An R&D run's research outputs are primary sources;
  how they reach the durable record intact is a design question (§ What survives the
  session?).
- **The retraction is an outcome.** The run proposed two chores and then withdrew them
  on canon grounds. With no durable home, a retracted proposal is re-proposed by the next
  session.

That class is ungoverned today. The operator has ruled it *"MUST be governed by an
overarching new AGENT SKILL"* that *"stands alone and now assumes a great deal of power
and responsibility — it is a **chargé d'affaires** for retaining and organizing possible
outcomes from an R&D designing session."* MPAS is the appropriation basis, chosen
because the operator used the method firsthand in mid-2026.

**Capture gap flagged, not amended.** The campaign's § Workflow fronts describes R&D as
*"Carry open hypotheses and experiments from `capability-control-review-2026-09-12.md`
and its conversation source."* That is a bookkeeping description of what the operator
describes as the headwater of the whole design pipeline. The campaign is Magna Carta and
amendments are operator-ratified; this record names the gap and proposes nothing.

---

## The theoretical basis: Brooks's design concept

Stated only on stage, nowhere in the repo. AI Engineer keynote, *Software Fundamentals
Matter More Than Ever* (transcript ~4:41–6:49):

> *"**Frederick P. Brooks, The Design of Design** … talks about this idea called **the
> design concept**. It's that when you have more than one person designing something
> together, you have this idea sort of floating between you, this ephemeral idea of the
> thing that you're building… **It's not an asset. It's not something you can put in a
> Markdown file. It is the invisible sort of theory of what you're building.**"*
>
> *"**Me and the AI don't share a design concept.** So I came up with a skill…
> 'Interview me relentlessly'… It turns the AI into a kind of **adversary**, where it's
> just continually pinging you ideas and trying to reach a shared understanding."*

This explains the repo's most surprising fact: **`grilling` emits no file.** Its target
is an unwritable shared model; documents are downstream and secondary.

The README gives the practical form of the same claim, under the epigraph *"No-one knows
exactly what they want"* (Thomas & Hunt): *"The most common failure mode in software
development is misalignment. You think the dev knows what you want. Then you see what
they've built - and you realize it didn't understand you at all. This is just the same in
the AI age. There is a communication gap between you and the agent. The fix for this is a
grilling session."*

---

## The source, as read

### Format and distribution

Plain markdown `SKILL.md` per skill, plus a sibling `agents/openai.yaml` carrying Codex UI
metadata. No Cursor rules, no prompt files, no proprietary format. 18 engineering and 7
productivity skills. Shipped two ways: as a Claude Code plugin in Anthropic's official
marketplace, and through `skills.sh`, which copies editable files into a project.
Human-facing documentation mirrors each skill at `docs/<bucket>/<name>.md`, published to
`aihero.dev/skills-<name>`. Nothing is paywalled or video-only.

**Calibration of size:** the entire interrogation mechanic, `grilling`, is **319
words**; `implement` is **70 words**; `wayfinder`, the largest, is about 2,000.

### Skills are split by who may invoke them

User-invoked skills carry `disable-model-invocation: true` (and
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`) and are reachable only
by a human typing them. Model-invoked skills hold reusable discipline. Every
orchestrating skill — `grill-me`, `grill-with-docs`, `to-spec`, `to-tickets`,
`wayfinder`, `improve-codebase-architecture`, `triage`, `implement` — is user-invoked.
The invariant and its reason are in § The mechanical rules the source relies on.

### Disciplines (model-invoked — the agent reaches for these)

| Skill | Shape | Emits | Stopping condition |
|---|---|---|---|
| **`grilling`** | Not phased. Model the subject as a **design tree**; compute the **frontier** = *"every decision whose prerequisites are already settled"*; ask the whole frontier in one numbered round, each with a recommended answer; wait; recompute | **nothing** | *"The frontier is empty"* **and** *"Do not act on it until the user confirms you have reached a shared understanding."* |
| **`domain-modeling`** | Five inline behaviours: challenge against glossary · sharpen fuzzy language · discuss concrete scenarios · cross-reference with code · update inline | `CONTEXT.md` (glossary only) · `docs/adr/NNNN-slug.md` | *"Don't batch these up: capture them as they happen."* |
| **`codebase-design`** | Reference, not a sequence. Fixes vocabulary: module, interface, implementation, depth, **seam** (credited to Michael Feathers), adapter, leverage, locality | nothing | n/a |
| **`tdd`** | red → green, one vertical slice at a time | tests + code | per slice |
| **`diagnosing-bugs`** | Six gated phases: feedback loop → reproduce+minimise → hypothesise → instrument → fix+regression test → cleanup | fix + regression test + a stated hypothesis in the commit | four-box Phase-6 checklist |
| **`prototype`** | throwaway, logic or UI branch | one HTML file, or N UI variants on one route, on a `prototype/<name>` branch | the design question has a one-line verdict |
| **`research`** | background agent → primary sources → cited markdown | one cited `.md`, *"where the repo already keeps such notes"* | file written |
| **`code-review`** | pin fixed point → identify spec source → identify standards sources → **two parallel subagents** | side-by-side findings | both axes report |

### Orchestrators (user-invoked only)

| Skill | Shape | Emits |
|---|---|---|
| **`grill-me`** | one line: *"Call the Skill tool with 'grilling'."* Stateless — *"writes no files and leaves no workspace behind"* | nothing |
| **`grill-with-docs`** | *"Call the Skill tool twice, for 'grilling' and 'domain-modeling'."* The in-repo door, *"strictly the better one"* | `CONTEXT.md` edits + ADRs, written inline as decisions land |
| **`to-spec`** | explore repo → **sketch the testing seams** (*"the ideal number is one"*; human gate: *"Check with the user that these seams match their expectations"*) → publish spec, label `ready-for-agent` | one tracker issue |
| **`to-tickets`** | gather → explore (*"look for opportunities to prefactor"*) → draft **vertical slices** → **quiz the user** → publish in dependency order | one issue per ticket |
| **`wayfinder`** | the multi-session shape — see below | a map issue + typed child tickets |
| **`improve-codebase-architecture`** | explore (*"Scope before you scan: YAGNI"*; `git log` hot spots; **deletion test**) → HTML report → grilling loop on **the one candidate the user picks** | timestamped HTML report in `$TMPDIR` |
| **`triage`** | gather + **two mandatory checks** → recommend and wait → **verify the claim** → grill if needed → apply outcome | an agent brief comment, triage notes, or an `.out-of-scope/` file |
| **`implement`** / **`implement-spec`** | implement → tdd at pre-agreed seams → code-review → commit / subagent-per-ticket in own worktree, merger subagent, PR | commit / one PR |
| **`handoff`** | compact conversation → write doc | markdown **in the OS temp dir, not the workspace** |

### What the set does not contain

**Three of the four shapes the operator named do not exist under those names.**

| Asked for | What exists |
|---|---|
| "grill me" | Real. `grill-me` is a one-line wrapper; the mechanism is `grilling` |
| a planning skill | **No `/plan` skill.** Planning is `to-tickets` (single session) and `wayfinder` (multi-session) |
| a spec skill | Real, named `to-spec` — formerly `to-prd`, renamed in v1.1 |
| a refactoring skill | **Does not exist.** *"There is no dedicated `/refactor` skill for that case yet."* |

Refactoring lives in **three places** instead, detailed in § The refactoring provisions:
the survey skill `improve-codebase-architecture`, the **wide-refactor clause** inside
`to-tickets`, and the `codebase-design` reference with its `DEEPENING.md`. The operator's
first framing — *"grill me, plans, specs, refacotring"* — names shapes the source
distributes differently, and the appropriation follows the source's anatomy, not the
names.

---

## The anatomy, skill by skill

### `grilling` — the interrogation mechanic

**Three terms carry it.** **Design tree** — *"every decision branches into the decisions
that hang off it."* **Frontier** — *"every decision whose prerequisites are already
settled: the questions you can ask now without guessing at answers you haven't heard
yet."* **Round** — one frontier, asked in full, answered in full: *"Ask the whole
frontier in one round: number each question and give your recommended answer. Then wait
for the user's answers before the next round."* And: *"A question whose answer depends on
another question still open in this round belongs to a later round, not this one."*

**The question format, from the file:**

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: ...
```

Every question carries the agent's recommended answer, so the human answers by number —
*"1 yes, 2 the second option, 3 no, here's why"* — rather than composing prose. That is
gzkit's § Operator Economy of Effort, mechanized. The `---` separator was added because
questions were running together.

**Facts are the agent's; decisions are the human's.** *"Finding facts is your job, never
the user's. When a frontier question needs a fact from the environment (filesystem,
tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could
look up yourself. Don't block on it: a running exploration is an unsettled prerequisite,
so only the questions downstream of it wait for the sub-agent to report; ask the rest of
the frontier now. The decisions are the user's: put each to them and wait."* From the
documentation: *"An agent running `grilling` that answers its own decisions has broken
the skill, not interpreted it liberally."* This is gzkit's § Operator Economy #7 — never
ask the operator what canon or the environment already answers — reached independently.

**Two stopping conditions.** *"The session is done when the frontier is empty: every
branch of the design tree visited, nothing left silently assumed. Do not act on it until
the user confirms you have reached a shared understanding."* The failure it guards
against, in his words: *"It ran out of questions and started building. A confirmation
gate exists precisely for this: the skill is not finished when the frontier empties, it
is finished when you say the understanding is shared."*

**No question cap, deliberately — a standing rejection.** `.out-of-scope/question-limits.md`:
*"Grilling is intentionally open-ended... some plans need three questions, some need
fifty. A fixed cap would either cut off useful exploration on hard problems or feel
arbitrary on easy ones."* A cap *"would also conflate two different failure modes: a
model that asks too many questions because the plan is genuinely under-specified
(working as intended) vs. a model that asks redundant or low-value questions (a
prompt-quality issue, not a quantity issue)."*

**The failure it exists to prevent is passivity.** *"The failure mode is passivity:
answering 'agreed, agreed, agreed' for forty questions and coming out with a plan the
agent wrote and you nodded at. It feels productive because it was long. Nothing was
actually decided, and the result carries a certainty it hasn't earned."* To a user who
complained of 200 questions (issue #44): *"My advice is to remember that you are the one
in charge. Use the questions as a prompt to provide more information. It's a
conversation, not an exam."*

**Grillable versus ungrillable.** *"'One long form or three pages?' and 'how should this
interaction feel?' are ungrillable: they need something to react to. When you hit one,
stop grilling. Build the throwaway version with `prototype`, look at it, then come back
and answer in one line. Talking your way through an ungrillable question is where
sessions balloon."*

**Limits he publishes.** *"the frontier is the agent's judgement, not a computed graph"* —
it can mis-batch two dependent questions. The recommendation sometimes argues against the
question as worded, so agreeing means answering "no". And `grill-with-docs` naming two
other skills *"does not reliably cause that skill to load"* — a real, unfixed defect, and
the documented cause of his most-reported problem.

**The handoff between interrogation and spec is the context window.** *"Do I start a
fresh session before writing the spec? No. The value of the session is the context you
just built. Hand the same conversation straight to `to-spec`."*

### `to-spec` — the specification shape

**It does not interview.** *"This skill takes the current conversation context and
codebase understanding and produces a spec. Do NOT interview the user; just synthesize
what you already know."*

**Phases.** (1) Explore the repo — *"Use the project's domain glossary vocabulary
throughout the spec, and respect any ADRs in the area you're touching."* (2) Seam design,
with a human gate — *"Sketch out the seams at which you're going to test the feature.
Existing seams should be preferred to new ones. Use the highest seam possible... The
fewer seams across the codebase, the better - the ideal number is one. Check with the
user that these seams match their expectations."* (3) Write and publish to the tracker
with a `ready-for-agent` label.

**Sections:** `Problem Statement` and `Solution` (both from the user's perspective) ·
`User Stories` (*"A LONG, numbered list"*, `As an <actor>, I want a <feature>, so that
<benefit>`, *"extremely extensive"*) · `Implementation Decisions` · `Testing Decisions` ·
`Out of Scope` · `Further Notes`.

**No file paths.** *"Do NOT include specific file paths or code snippets. They may end up
being outdated very quickly."* One carve-out: *"if a prototype produced a snippet that
encodes a decision more precisely than prose can (state machine, reducer, schema, type
shape), inline it... Trim to the decision-rich parts, not a working demo."*

**The spec is disposable.** *"Nothing keeps it in sync, so in practice it is a snapshot
of what you knew at that moment, and it goes stale the first time implementation teaches
you something. Treat it as throwaway once the work ships. The artifacts meant to outlive
it are your `CONTEXT.md` and your ADRs; if something learned during implementation
deserves to last, it belongs there, not in an edited spec."* On issue #77, pitched
spec-driven development: *"some of that SDD stuff I really don't like - i.e. 'spec as
source'."* He had asked the reporter *"Could you give me some details on what I can read
about it?"* — he had not read the SDD literature he rejects.

**It does not fit architectural work, and he says so.** Asked *"My work is a refactor or
a module boundary, not a feature. Does the template fit?"*: *"Less well, and this is a
known limitation. The template leans hard on user stories, which is the wrong shape for
architectural work: you end up writing stories nobody asked for around decisions that are
really about interfaces and invariants. Lean on the implementation-decisions and
testing-decisions sections instead, and let the durable architectural calls land as
ADRs."* Most gzkit R&D is architectural, so this limit binds.

**Skip it when you can.** *"Why not go straight from grilling to `/to-tickets` and skip
the spec? Often you should; the spec earns its step only on multi-session work... On a
single-session change that buys you nothing, and you have paid an extra synthesis step
where the model can drift."*

### `to-tickets` — the planning shape

**Phases.** Gather context → explore the codebase (optional; *"Look for opportunities to
prefactor the code to make the implementation easier. 'Make the change easy, then make
the easy change.'"* — Kent Beck, uncredited) → draft vertical slices → **quiz the user** →
publish in dependency order.

**Granularity, verbatim:** *"Each slice cuts a narrow but COMPLETE path through every
layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer"* · *"A
completed slice is demoable or verifiable on its own"* · *"Each slice is sized to fit in a
single fresh context window"* · *"Any prefactoring should be done first."*

**The plan is a graph.** Each ticket declares blocking edges; *"A ticket with no blockers
can start immediately."* Work the frontier — the same word as grilling. On GitHub these
become native blocking links *"because it renders the frontier visually in the tracker's
own UI."*

**The approval gate.** *"Present the proposed breakdown as a numbered list. For each
ticket, show: Title / Blocked by / What it delivers... Ask the user: Does the granularity
feel right? (too coarse / too fine) Are the blocking edges correct: does each ticket only
depend on tickets that genuinely gate it? Should any tickets be merged or split further?
Iterate until the user approves the breakdown."* Refusal: *"Do NOT close or modify any
parent issue."*

**Ticket template:** `What to build` (end-to-end behaviour, *"not layer-by-layer
implementation"*) · `Acceptance criteria` (checkboxes) · `Blocked by`. Local mode writes
`.scratch/<feature-slug>/issues/<NN>-<slug>.md`.

**The acceptance-criteria falsifiability test.** *"Three shapes recur: a criterion
already true at the base commit, a criterion that can only be satisfied by work another
ticket owns, and one that restates the request rather than deriving from the artifact...
For each criterion, name the observation that would show it false, and confirm it fails
at the commit the implementer starts from."* See § Where MPAS is stronger.

### `wayfinder` — the R&D-shaped one

Largest skill in the repo (~2,000 words), purpose-built for deep design inquiry too big
for one session. Its opening: *"A loose idea has arrived, too big for one agent session,
and wrapped in fog: the way from here to the destination isn't visible yet. Wayfinding is
about finding that way, not charging at the destination."*

**The core constraint:** *"Plan, don't do. Wayfinder is planning by default: each ticket
resolves a decision, and the map is done when the way is clear, with nothing left to
decide before someone goes and does the thing. The pull to just do the work is usually
the signal you've reached the edge of the map and it's time to hand off."*

**The map** — one issue, labelled `wayfinder:map`:

| Section | Holds |
|---|---|
| `Destination` | *"what reaching the end of this map looks like... every session orients to it before choosing a ticket"* |
| `Notes` | domain, skills to consult, standing preferences |
| `Decisions so far` | one line per **closed** ticket plus a link — *"The map is an index, not a store... a decision lives in exactly one place, its ticket, so the map never restates it, only gists it and links."* |
| `Not yet specified` | **the fog** — in scope, not yet sharp enough to ticket |
| `Out of scope` | ruled beyond the destination; *"never graduates"* |

**Fog versus ticket:** *"whether you can state the question precisely now, not whether
you can answer it now. Ticket when the question is already sharp, even if it's
blocked... Not yet specified when you can't yet phrase it that sharply. Don't pre-slice
the fog into ticket-sized pieces."* **Fog versus out of scope:** *"Fog only ever gathers
toward the destination... Scope, not sharpness, lands it here."* Out-of-scope items close
with one line of reasoning and stay out of `Decisions so far`, *"which records the route
actually walked; a scope boundary isn't a step on it."*

**Ticket types.** Every ticket is HITL or AFK. *"A HITL ticket only resolves through that
live exchange; the agent never stands in for the human's side of it (a grilling agent
that answers its own questions has broken this)."*

| Type | Mode | When |
|---|---|---|
| `research` | AFK | knowledge outside the working directory; resolved by a subagent |
| `prototype` | HITL | *"how should it look / behave"* is the key question |
| `grilling` | HITL | *"Conversation. The default case."* |
| `task` | either | manual work that unblocks a decision — *"the one type that does rather than decides, and it earns its place by unblocking a decision, not by delivering the destination"* |

Child tickets carry a `## Question` body only.

**Mode A — chart:** (1) name the destination by grilling and domain-modeling → (2) grill
again **breadth-first** to map the frontier → (3) create the map → (4) create specifiable
tickets, then **wire blocking edges in a second pass** (*"issues need ids before they can
reference each other"*) → (5) fire research subagents in parallel → (6) *"Stop: charting
is one session's work; it hand-resolves nothing."* Null-result exit: *"If this surfaces
no fog... you don't need a map. Stop and ask the user how they'd like to proceed."*

**Mode B — work:** (1) load the map at low resolution → (2) choose a frontier ticket and
**claim it by assigning before any work** (*"an open, unassigned ticket is unclaimed"*) →
(3) resolve, *"zoom as needed"* → (4) post the resolution, close, append one line to
`Decisions so far` → (5) graduate fog into new tickets, clearing each graduated patch.
Hard limit: *"never resolve more than one ticket per session, with the exception of
research tickets."*

**Naming discipline:** *"In everything the human reads... refer to it by that name, never
by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a
glance."*

**The documented failure — read twice.** *"Wayfinder's 'plan, don't do' default can be
overridden in the map's Notes, but the Notes are written by the agent, so the constraint
and its exemption live in the same file the constrained party owns. One user watched an
agent write 'this map carries execution' into its own Notes and then read it back in
later sessions as its own licence, building on a live server."* See § Where gzkit is
stronger.

**Other findings he publishes.** Twenty-seven-ticket maps go stale by ticket 13 —
*"exactly the waterfall trap the skill is accused of"* — and the counter is *"Wayfinder is
'prototypemaxxing', not 'planmaxxing'"*, with the map scoped to one bounded epic.
Parallel ticket work is unsafe in practice because *"the sessions share no context."*

**Handoff out:** *"When the map clears, it hands off, it doesn't build: merge onto the
main flow at `/to-spec`, which collapses the map's linked decisions into a buildable
plan."* Invoked as `/to-spec #<map_issue>` against **the map**, never the tickets.

### The refactoring provisions

**1. `improve-codebase-architecture` — the survey.** Phases: explore → HTML report →
grill the chosen candidate.

- **Scope before you scan: YAGNI.** Take the user's named direction; otherwise *"walk back
  a good stretch of the commit history (`git log --oneline`) to find the codebase's hot
  spots"* — recency-weighted, because *"Deepening a module pays off by making future
  changes to it easier."* Read `CONTEXT.md` and the ADRs; spawn a subagent to walk the
  code.
- **The deletion test:** *"would deleting it concentrate complexity, or just move it? A
  'yes, concentrates' is the signal you want."*
- **The report card** per candidate: Files / Problem / Solution / Benefits (*"in terms of
  locality and leverage, and how tests would improve"*) / before-after diagram /
  **strength badge** `Strong | Worth exploring | Speculative`, ending in a Top
  recommendation. Written to `<tmpdir>/architecture-review-<timestamp>.html`; nothing
  lands in the repo and no code changes during the run.
- **Hard gate:** *"Do NOT propose interfaces yet. After the file is written, ask the
  user: 'Which of these would you like to explore?'"* One candidate per session.
- **ADRs.** Candidates that contradict an ADR surface only when *"the friction is real
  enough to warrant revisiting the ADR"*. A rejection is captured: *"User rejects the
  candidate with a load-bearing reason? Offer an ADR, framed as: 'Want me to record this as
  an ADR so future architecture reviews don't re-suggest it?'"*
- **Its bias, disclosed:** *"Will it ever tell me the codebase is fine? Rarely... The skill
  is built to output findings, so the framing pushes it toward producing candidates rather
  than concluding that nothing is wrong. The strength badges are the defence: a report
  where everything is `Speculative` is the skill telling you it found nothing, in the only
  way it knows how."*

**2. The wide-refactor clause in `to-tickets` — the real sequencing shape.** Verbatim:
*"Wide refactors are the exception to vertical slicing. A wide refactor is one mechanical
change (rename a column, retype a shared symbol) whose blast radius fans across the whole
codebase, so a single edit breaks thousands of call sites at once and no vertical slice
can land green. Don't force it into a tracer bullet; sequence it as expand–contract.
First expand: add the new form beside the old so nothing breaks. Then migrate the call
sites over in batches sized by blast radius (per package, per directory), each batch its
own ticket blocked by the expand, keeping CI green batch to batch because the old form
still exists. Finally contract: delete the old form once no caller remains, in a ticket
blocked by every migrate batch. When even the batches can't stay green alone, keep the
sequence but let them share an integration branch that all block a final
integrate-and-verify ticket; green is promised only there."* **Green between steps is the
verification gate**, expressed as blocking edges. Rollback is addressed nowhere; the
expand phase is the only rollback affordance. This is the directly relevant shape for R&D
outcome 5, system-wide refactorings.

**3. `codebase-design` and `DEEPENING.md` — the rules that bind a refactor.** A vocabulary
reference, model-invoked, consumed by `tdd` and the survey. *"Use these terms exactly:
don't substitute 'component,' 'service,' 'API,' or 'boundary.'"* Its **Rejected
framings** section refuses depth-as-line-ratio (*"rewards padding the implementation"*),
interface-as-type-signature, and "boundary". Two binding rules: *"One adapter means a
hypothetical seam. Two adapters means a real one. Don't introduce a port unless at least
two adapters are justified."* and *"Testing strategy: replace, don't layer. Old unit tests
on shallow modules become waste once tests at the deepened module's interface exist;
delete them. Write new tests at the deepened module's interface. The interface is the
test surface."* `DESIGN-IT-TWICE.md` (Ousterhout) frames the problem, spawns **three or
more parallel subagents each given a different design constraint** — minimize the
interface, maximize flexibility, optimize the common caller, ports and adapters —
compares on depth, locality and seam placement, and ends *"Be opinionated: the user wants
a strong read, not a menu."*

**Feature shape against refactor shape:**

| | Feature | Refactor |
|---|---|---|
| Entry | an idea from the human | **the survey finds it** (hot-spot scan) |
| Decomposition | vertical tracer bullets | **expand → migrate batches → contract** |
| Green | every ticket | every batch, or only at integrate-and-verify |
| Spec template | fits | *"less well... known limitation"* |
| Durable artifact | spec (throwaway) | **ADR** |
| Rejection | — | **recorded as an ADR so the survey stops re-suggesting it** |

### `domain-modeling` — where ADRs and the glossary come from

Model-invoked, running inline during grilling rather than as a phase. Its live behaviours,
with the source's examples: challenge against the glossary (*"Your glossary defines
'cancellation' as X, but you seem to mean Y. Which is it?"*) · sharpen fuzzy language
(*"You're saying 'account': do you mean the Customer or the User?"*) · discuss concrete
scenarios · cross-reference with code (*"Your code cancels entire Orders, but you just
said partial cancellation is possible. Which is right?"*) · update `CONTEXT.md` inline —
*"Don't batch these up: capture them as they happen."* Files are created lazily, only
when there is something to write.

**The three-part ADR test, all required:** *"Hard to reverse: the cost of changing your
mind later is meaningful"* · *"Surprising without context: a future reader will wonder
'why did they do it this way?'"* · *"The result of a real trade-off: there were genuine
alternatives and you picked one for specific reasons."* *"If any of the three is missing,
skip the ADR."* Worth comparing against gzkit's own ADR admission when the R&D skill
decides what to propose under outcome 1.

**The ADR template is one paragraph:** `# {Short title of the decision}` then *"{1-3
sentences: what's the context, what did we decide, and why.}"* — *"That's it. An ADR can
be a single paragraph. The value is in recording that a decision was made and why, not in
filling out sections."* Status, Considered Options and Consequences are optional.

**`CONTEXT.md` is a glossary and nothing else:** *"totally devoid of implementation
details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for
implementation decisions."* Each term is one or two sentences plus an `_Avoid_:` list of
banned synonyms; `CONTEXT-MAP.md` serves multi-context repos. His stated payoff: *"There's
a problem when a lesson inside a section of a course is made 'real'"* becomes *"There's a
problem with the materialization cascade."*

### `triage` and the agent brief

**A state machine:** two category roles (`bug`, `enhancement`) crossed with five state
roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) —
*"Every triaged issue should carry exactly one category role and one state role."*
*"Triage is only for issues you didn't create."*

**Phases:** gather context with **two mandatory checks** — *"(a) redundancy: search for
an existing implementation of the requested behavior by domain concept (not just the
request's wording), and report where you looked. (b) prior rejection: read
`.out-of-scope/*.md` and surface any that resembles this request."* → recommend and wait →
**verify the claim** (*"Before any grilling, check that the claim holds up. For a bug,
reproduce it from the reporter's steps... A confirmed verification makes a much stronger
agent brief."*) → grill if needed → apply the outcome. Every AI-posted comment opens
`> *This was generated by AI during triage.*`

**`.out-of-scope/` is a committed knowledge base of rejected requests.** Each file states
the rejection, the reasoning, and a list of prior request links; rejecting an enhancement
writes to it, and the next triage reads it. The two live files, `question-limits.md` and
`mainstream-issue-trackers-only.md`, are doctrine artifacts in their own right.

**The agent brief — gzkit's OBPI brief analogue.** *"The original body and discussion are
context: the agent brief is the contract."* Four principles: **durability over
precision** (*"Do describe interfaces, types, and behavioral contracts. Don't reference
file paths: they go stale. Don't reference line numbers."*) · **behavioral, not
procedural** (*"Good: 'The `SkillConfig` type should accept an optional `schedule`
field'. Bad: 'Open src/types/skill.ts and add a schedule field on line 42'."*) ·
**complete acceptance criteria** (*"Good: 'Running `gh issue list --label needs-triage`
returns issues that have been through initial classification'. Bad: 'Triage should work
correctly'."*) · **explicit scope boundaries** (*"This prevents the agent from
gold-plating."*). Template: Category / Summary / Current behavior / Desired behavior / Key
interfaces / Acceptance criteria / Out of scope. A worked "bad brief" ships beside it.

### `implement`, `implement-spec`, `tdd`, `diagnosing-bugs`, `prototype`, `code-review`, `handoff`

- **`implement`** (70 words): implement → `/tdd` at pre-agreed seams → typecheck and single
  test files regularly, the full suite once at the end → `/code-review` → commit.
- **`implement-spec`** (beta): read spec and tickets as a task graph → optional
  exploration subagent saving notes **outside the repo** → branch and draft PR →
  **an implementer subagent per ticket, in its own worktree and branch** → a **merger
  subagent** folds each into the PR branch → re-run the frontier → `/code-review`, fixes
  in one subagent → mark ready → clean up worktrees. *"Communication to and from subagents
  should be sparse. Communicate primarily through context pointers... Don't duplicate
  information already available via pointers."*
- **`tdd`:** *"Test only at pre-agreed seams... No test is written at an unconfirmed
  seam."* · *"Refactoring is not part of the loop. It belongs to the review stage."* Named
  anti-patterns: implementation-coupled tests, **tautological** tests (*"the assertion
  recomputes the expected value the way the code does... Expected values must come from an
  independent source of truth"*), horizontal slicing.
- **`diagnosing-bugs`** — the most gated skill in the repo. Six phases, each with a
  completion criterion: build a feedback loop · reproduce and minimise · hypothesise ·
  instrument · fix with a regression test · clean up. *"If you catch yourself reading code
  to build a theory before this command exists, stop... No red-capable command, no Phase
  2."* · *"Do not proceed until you have reproduced and minimised."* · *"Do not proceed to
  hypothesise without a loop."* Phase 1's four-box criterion: red-capable, deterministic,
  fast, agent-runnable. Phase 3 requires *"3–5 ranked hypotheses"*, each falsifiable,
  shown to the user before testing. The Phase 6 checklist: original repro gone, test
  passes, every `[DEBUG-…]` removed, prototypes deleted. Its post-mortem hands off to
  `improve-codebase-architecture` *"when the real finding is that there's no good seam to
  lock the bug down."*
- **`prototype`:** pick logic or UI; build throwaway; the result is **kept as a primary
  source** on a `prototype/<name>` branch off main, pointed at from the issue, while the
  validated decision folds into code.
- **`code-review`:** two axes run as **parallel subagents** *"so they don't pollute each
  other's context"* — **Standards** (repository docs plus a fixed 12-smell baseline from
  Fowler's *Refactoring* ch. 3, *"never a hard violation"*, repository overrides win) and
  **Spec** (fidelity to the originating issue).
- **`handoff`:** *"Do not duplicate content already captured in other artifacts (specs,
  plans, ADRs, issues, commits, diffs). Reference them by path or URL instead."* Written
  to the OS temp dir with a "suggested skills" section.

### How the skills chain

`ask-matt` is a user-invoked router that declares the pipeline. Its maintenance rule, from
`CLAUDE.md`: *"a new skill it never mentions, or a stale one it still routes to, is a
router that lies."*

```
                    ┌─ /triage ────────────────┐  (raw incoming issues)
                    ├─ /diagnosing-bugs ───────┤  (post-mortem may exit to /improve-codebase-architecture)
on-ramps ───────────┼─ /wayfinder ─────────────┤  (too big for one session; exits at /to-spec)
                    └─ /improve-codebase-arch ─┘  (upkeep; exits at /grill-with-docs)
                                │
                                ▼
   /grill-with-docs  ──▶  multi-session?  ──YES──▶  /to-spec ──▶ /to-tickets ──▶ /implement (×N)
   (= grilling + domain-modeling)      │                                              │
        │                              └──NO───────────────────────▶ /implement       ├─ drives /tdd
        └─ ungrillable question?                                                      └─ closes with /code-review
           → /handoff → /prototype → /handoff back
```

**The upkeep loop:** `/improve-codebase-architecture` → pick a candidate → re-enter the
main flow at `/grill-with-docs`.

**What crosses each boundary:**

| Boundary | Artifact |
|---|---|
| grill → spec | **the context window** — explicitly, do not clear or compact |
| spec → tickets | the tracker issue, in the same window (a large spec truncates if re-fetched) |
| tickets → implement | one ticket per fresh context, `/clear` between |
| wayfinder → spec | the **map issue**, not the tickets |
| research → grilling | a cited markdown file in the repo |
| prototype → implement | the validated decision folded into code; the prototype kept as a primary source on its branch |
| any → new harness, directory or colleague | a `/handoff` markdown file that references rather than duplicates |

### Every explicit stop in the corpus

| Skill | Gate |
|---|---|
| `grilling` | frontier empty **and** the user confirms shared understanding |
| `to-spec` | *"Check with the user that these seams match their expectations"* |
| `to-tickets` | *"Iterate until the user approves the breakdown"* |
| `improve-codebase-architecture` | *"Do NOT propose interfaces yet"* — report, then ask which candidate |
| `wayfinder` | *"Stop: charting is one session's work"*; one ticket per session; claim before work |
| `tdd` | *"No test is written at an unconfirmed seam"* |
| `diagnosing-bugs` | *"No red-capable command, no Phase 2"*; *"Do not proceed until you have reproduced and minimised"* |

---

## The mechanical rules the source relies on

These are the source's load-bearing mechanics, with its stated reasons. Recording them
here is not a recommendation to take them; each surfaces as a question in § Questions for
the design session.

### 1. The invocation-class invariant

From `.agents/invocation.md`: every **orchestrating** skill is user-invoked
(`disable-model-invocation: true`); every reusable **discipline** is model-invoked. The
invariant:

> *"A user-invoked skill may invoke model-invoked skills, but it can **never** reach
> another user-invoked skill."*

Cross-skill calls must name the tool — `Call the Skill tool with "grilling"` — never a
bare `/skill` in prose, one skill per call; a prose reference *"does not reliably cause
that skill to load."* His stated reason (*Building Great Agent Skills: The Missing
Manual*, 5:17–6:16):

> *"Every time you have a model-invoked skill, you get **a cost in unpredictability**.
> Because every time you have a context pointer pointing from one resource to another,
> **the model may just choose not to follow it**… **you're removing a class of problem from
> even being a problem.** Because this unpredictability leads people to need to eval their
> skills to make sure they're being called at the right time, which is really nasty."*

**The session read this as the answer to "one overarching skill"** — one user-invoked
orchestrator reaching only disciplines would satisfy both the operator's instruction and
the mechanic (see § Resolved in session — tentatively). It also parallels gzkit's IRON
LAW, reached independently, and it is **mechanical** in the source, where gzkit's IRON
LAW is advisory with no witness.

### 2. Hide the downstream step

*Building Great Agent Skills: The Missing Manual* (15:12–16:18):

> *"Sometimes the agent just doesn't do enough **leg work**... A real classic case... is
> plan mode. Because in plan mode we have two steps. We have ask clarifying questions and
> then create a plan. And what I have found in **every single implementation of plan mode
> I've tried** is the ask-clarifying-questions just doesn't ever do enough leg work. **It
> sees that its ultimate goal is to create a plan, and so it just does a small amount of
> leg work … and then eagerly creates the plan.**"*
>
> *"So... I instead have a skill called grill-with-docs... And then I split the planning
> into its own skill... **we have step one and step two, but the agent only sees one step
> at a time.** So this is a really cool technique for increasing leg work on the step
> that you're on by **hiding the future goal, hiding the future steps**."*

A single skill that merely *names* its phases buys none of this — *"an inline call leaves
the later steps in context and clears nothing."* The research report promotes this to an
eighth invariant of the transferable anatomy, and predicts that one skill enumerating
grill → spec → plan → execute will produce a shallow grill every time.

**What this rule does and does not require — a correction made in session.** Hiding the
downstream step is a matter of **separate skills**, not **separate context windows**.
The session first read it as demanding a context break between every phase, then
corrected itself against § 4: MPAS keeps grill → spec → tickets **inline**, in one
unbroken context (*"Keep steps 1–3 in one unbroken context window"*). Each step is a
separately invoked skill, so the agent sees only the step it is on. The hard breaks come
later — at implementation, and between `wayfinder` tickets. The rule argues against one
skill that *enumerates* its phases, not against one session that runs several skills.

### 3. Frontier batching defeats passive assent

One-question-at-a-time was the **original** default, and no reachable source argues for
it — a confirmed absence. Every argument he makes is for abandoning it:

| Date | Event |
|---|---|
| — | original skill text: *"Ask the questions one at a time"* (quoted in the *Missing Manual* transcript ~16:17) |
| — | *"My /grill-me skill just asked me 24 consecutive questions. I've been sat here, writing a PRD, for an hour."* |
| 2026-07-15 | **the turn:** *"I just modified /grill-me locally to ask all its questions at once... and I kind of loved it. Just lets you dictate out a bunch of answers all at once and **doesn't have the failure mode where you just say 'I agree' turn after turn.**"* |
| 2026-07-16 | **the safety mechanism:** *"Before: 13 questions, 13 rounds. After: 13 questions, 3 rounds. **Still only asks questions at the 'frontier' - i.e. those that don't depend on any other decisions.**"* |
| 2026-08-05 | shipped into the primitive |

Batching defeats passivity; the frontier makes batching safe. This sharpens gzkit's
§ Operator Economy of Effort, which asks for economy but names no mechanism. A version
ambiguity: the skill as published in *My Grill Me Skill Has Gone Viral* has no
"one at a time" line — there, "one by one" modifies resolving dependencies between
decisions, not asking.

### 4. Context boundaries: hard break vs inline

| Boundary | Kind |
|---|---|
| grill → to-spec → to-tickets | **INLINE — must not break.** *"Keep steps 1–3 in one unbroken context window (don't compact or clear until after `/to-tickets`)"* |
| to-tickets → implement, and between tickets | **HARD BREAK** — one ticket per fresh context; *"Each ticket is self-contained, so the last one's context is disposable"* |
| grilling ↔ prototype | **HARD BREAK both directions**, via `/handoff` (a prototype lives in its own directory) |
| wayfinder chart → work; ticket → ticket; map → to-spec | **HARD BREAK** |
| grilling ↔ domain-modeling | **INLINE** — two Skill-tool calls in the same turn |
| improve-codebase-architecture report → grill | **INLINE** — same session, one candidate per session |
| implement → code-review | inline, but the two review axes are parallel subagents |
| research | **PARALLEL** — a background agent; only questions downstream of it wait |

**The boundary procedure** (`ask-matt/PHASE-BOUNDARIES.md`), first yes wins: **Continue →
`/clear` → `/handoff` → Subagent → `/compact`.** And the reason the order matters:

> *"Every move except **Continue** turns a **primary source** into a **secondary
> source**: the session as it happened, replaced by a summary of it."*

`/compact` is last by design — *"the default, not the first reach... The failure mode
when people start here is a fresh session that is confidently wrong about a decision the
summary flattened."* A boundary decision is made only at a boundary: *"Mid-phase there is
no decision to make: continue, or split the work that's left into subagents."* The
budget is the **smart zone**, about 150k tokens; issue #186: *"anything past 100K tokens
as the dumb zone of the LLM, where compaction quality cannot be guaranteed and shit gets
weird."* The zone framing is Dex Horthy's (HumanLayer), credited on stage.

---

## His stated reasoning

### The manifesto and the four failure modes

README: *"Developing real applications is hard. Approaches like GSD, BMAD, and Spec-Kit
try to help by owning the process. But while doing so, they take away your control and
make bugs in the process hard to resolve. These skills are designed to be small, easy to
adapt, and composable."* The sharper reason, from the AI Engineer Europe workshop
(~23:19): *"you need to own as much of your planning stack as you possibly can... because
they don't own the stack and they don't have observability over the whole thing, they just
go, 'This isn't working. This sucks.'... I believe in inversion of control, and you should
be in control of the stack."* The complication: his post *My 7 Phases of AI Development*
frames those tools as compatible — *"These phases apply whether you're using Ralph loops,
GSD, Spec Kit, or any other AI coding approach."*

| Failure mode (README § Why These Skills Exist) | Cause | Remedy |
|---|---|---|
| The agent didn't do what I want | misalignment | grilling |
| The agent is way too verbose | no shared language | `CONTEXT.md` — *"It might be the single coolest technique in this repo"* |
| The code doesn't work | no feedback loops | `tdd`, `diagnosing-bugs` |
| We built a ball of mud | *"agents can radically speed up coding, [so] they also accelerate software entropy"* | `improve-codebase-architecture` |

### Design principles, from his own issue comments

- *"I don't want this because I don't want to over-specify the skill"* (#18) ·
  *"Disagree, over-specifying it here makes it less useful"* (#22)
- *"The shorter the skills, easier to maintain and cheaper."* (#202)
- *"Disagree, open-ended is good"* (#182)
- *"I think restricting the format is a losing game, since everyone will have ideas about
  their own preferred format. I prefer shipping the basic version of the skill and letting
  people play."* (#219)
- **"Disagree here, asking agents to score stuff never ends well"** (#148)
- *"I'd rather not optimize skill content around an external scoring tool's rubric"* (#7)
- *"I like the grill-me skill being short and one-step, not two-step"* (#12)
- *"ready-for-agent means it's ready for an agent. The agent brief is just an
  implementation detail of triage"* (#205)
- *"I hate the AskUserQuestion UI, so I won't be including it here"* (#19) — the `❓/➡️`
  markdown round is the deliberate alternative.

### `writing-for-agents` — his doctrine for authoring skills, rules and briefs

The most directly transferable file for R&D outcome 4 (control surfaces, rules, skills).

- **Context pointer.** *"The pointer's wording, not its target, decides when the agent
  reaches the material... A must-have target behind a weakly worded pointer is a variance
  bug: sharpen the wording first, and inline the material only if sharpening fails."*
- **Information hierarchy and progressive disclosure** — three rungs: in-file step,
  in-file reference, disclosed reference. *"Branching is the cleanest disclosure test:
  inline what every branch needs, and push behind a pointer what only some branches
  reach."* gzkit's context-diet chore reaches the same structure.
- **Completion criteria** have two properties — **clarity** (*"A vague bound
  ('understanding reached') invites premature completion"*) and **demand** (*"'Every
  modified model accounted for' forces thorough work where 'produce a change list' does
  not"*). *"The strongest criteria are both checkable and exhaustive."*
- **Leading words.** *"a compact concept already living in the model's pretraining...
  Repeated as a token, never as a sentence... a made-up word recruits no priors: you pay
  in definition tokens what a pretrained word gives free."* This is why *fog of war*,
  *tracer bullet*, *frontier*, *seam*, *red* and *expand–contract* do so much work in
  his corpus.
- **Negation is a failure mode.** *"steering by prohibition drags the forbidden behaviour
  into context and makes it more available, not less. Don't think of an elephant...
  Prompt the positive."* See § Collisions.
- **No-ops.** *"an instruction the model already obeys by default pays load to say
  nothing... When a sentence fails, delete the whole sentence rather than trim words from
  it."*
- **Sediment** — *"stale layers that settle because adding feels safe and removing feels
  risky."*
- **"It's working if."** His documentation pages carry a "Common questions" section that
  names unfixed defects, model-dependent failures and contested choices, plus an **"It's
  working if"** checklist of observable behaviour — the cheapest transferable thing in the
  corpus.

### What he tried and abandoned

- **Spec-driven development — tried and rejected outright.** Keynote ~1:27–3:35: *"Keep
  your hand raised if you've tried it. Okay, I've tried it too... I would get code out ...
  and then I would run it, I would get worse code. And then I did it again, I got even
  worse code... **The idea that we can just ignore the code and just have the code let it
  manage itself is just sort of vibe coding by another name.**"* And: *"**I think code is
  not cheap. In fact, bad code is the most expensive it's ever been.**"* Workshop ~12:53:
  *"And I tried this. I really tried it. And it sucks. It doesn't work. Because you need
  to keep a handle on the code... **the code is your battleground.**"*
- **Plan mode — a clean, dated reversal.** 2026-01-15, *I was an AI skeptic. Then I tried
  plan mode*: *"Plan Mode is the most important feature for AI coding... I use it for
  every single code change."* 2026-04-02: *"I have also stopped using plan mode. It
  creates a plan FAR too eagerly and usually asks you zero questions en route. **The whole
  point of planning is to get on the same wavelength with the LLM, not to generate an
  asset you don't read.**"* In the repo: *"Leave plan mode off. Plan mode primes the agent
  to rush toward producing a plan, which is the opposite of staying in inquiry."*
- **A "sacrifice grammar for concision" prompt — dropped, with the thesis in miniature.**
  Workshop ~47:55: *"this prompt was really useful to me when I was reading the plans...
  But I've since dropped this idea in preference to a grilling session because ... I
  didn't want to read the plans. I wanted to get on the same wavelength as the LLM ... And
  when I stopped reading the plans, I stopped needing them to be concise."*
- **Compacting — rejected.** *"Devs love compacting for some reason, but I hate it. I much
  prefer my AI to behave like the guy from Memento because this state is always the
  same."*
- **`AskUserQuestion` — rejected** as *"broken in a ton of different ways"*.
- **TDD's refactor stage — dropped** from the loop and moved to review.
- **Skills removed:** `caveman` and `zoom-out` — *"went unused in practice."*

---

## The transferable anatomy

The research report's own synthesis, stripped of his vocabulary. It is the report's
reading of the source, not the source's claim. It is recorded as a lens for the design
discussion — a way to ask which phases an R&D run has and where its stops belong — not as
a skeleton for the R&D skill.

| # | Phase | Input | Output | Gate to exit |
|---|---|---|---|---|
| 0 | **Route** | a raw ask | which phase to enter | the human names the entry point; a router must enumerate every reachable phase or it "lies" |
| 1 | **Chart** *(only when the work exceeds one session)* | a foggy idea | a durable **map** — Destination / Decisions so far / **Not yet specified** / **Out of scope** — plus a graph of typed question units with blocking edges | the destination is written and agreed **before any unit exists**; charting resolves nothing; **a null result is a legal exit** |
| 2 | **Interrogate** | an idea, optionally a map unit | **no artifact** — a shared model held in one unbroken context | the frontier is empty **and** the human confirms shared understanding |
| 3 | **Concretise** *(escape hatch from 2)* | an ungrillable question | a throwaway artifact and a one-line verdict | the verdict is recorded; the artifact is kept as a primary source outside the mainline |
| 4 | **Synthesise** | the phase-2 context, **not** a summary of it | a **spec**: problem / solution / exhaustive acceptance statements / decisions / testing seams / out of scope | no new interviewing; the human ratifies the seams before drafting; the spec is disposable |
| 5 | **Decompose** | the spec | a **task graph** of vertical slices, each demoable and sized to one fresh context, each declaring blockers; wide mechanical change goes expand / migrate in batches / contract | the human approves granularity **and** edges; each acceptance criterion is shown to **fail at the base commit** |
| 6 | **Execute** | one graph node, a fresh context | code, tests, commit | test-first at pre-agreed seams only; two-axis review in parallel, non-polluting reviewers |
| 7 | **Precipitate** | anything learned in 1–6 | a **glossary term** or a **decision record** — the only durable outputs | a decision record only if hard to reverse **and** surprising **and** a real trade-off; written inline at the moment it crystallises |

### The eight invariants

1. **Facts are the agent's job; decisions are the human's.** Never ask the human what the
   environment can answer; never answer for the human what only they can decide.
   Dispatch subagents for facts and do not block the round on them.
2. **Batch by dependency, not by count.** Ask every question whose prerequisites are
   settled, together, each with a recommended answer. Never batch two questions where one
   gates the other. No question cap.
3. **The interrogation emits nothing.** Its output is the context window. Guard it; every
   compaction converts a primary source into a lossy secondary one.
4. **Two stopping conditions per phase, one mechanical and one human.** Mechanical:
   frontier empty, every batch green, criterion falsifiable. Human: explicit
   confirmation. Either alone is a hollow gate.
5. **Separate the disposable from the durable, and say which is which.** Specs and
   tickets are scaffolding and may go stale; only the glossary and decision records
   outlive the work. Never edit a shipped spec to keep it true.
6. **Rejections are artifacts.** A load-bearing "no" — to a refactor candidate, a feature
   request, a scope expansion — is written where the next run will read it, or it will be
   re-litigated. Three surfaces: a decision record, an out-of-scope knowledge base, and a
   map's out-of-scope section.
7. **Never let the constrained party own the exemption.** *His documented bug, not his
   rule* — promoted by the research because it is exactly gzkit's presence-check
   doctrine. If a discipline can be overridden, the override lives where the agent under
   it cannot write.
8. **Hide the downstream steps.** An agent that can see the next phase under-invests in
   the current one. Separate phases into separately invoked units.

**The report's notes for an independent implementation**, recorded as written: make
every orchestrating phase human-invocable mechanically, not in prose · cross-phase
invocation names the tool · keep phase definitions short · prefer pretrained metaphors to
coined terms · state targets positively · publish the rough edges and an "It's working
if" checklist beside the discipline. These are the research's advice to an implementer,
not gzkit's decisions.

---

## Collisions with gzkit — resolve deliberately, do not inherit

### The attestation inversion

Asked in the AI Engineer Europe workshop (~35:19) whether he reviews the generated spec:

> *"**Yeah, I don't look at these. I don't look at these.** The reason I don't look at
> these is because what am I testing at this point?… I have reached the same wavelength as
> the LLM using the Grill Me skill. We have a shared design concept. So if I have a shared
> design concept, **all I'm doing is essentially checking the LLM's ability to
> summarize.**"*

**He attests to the conversation. gzkit's Gate 5 attests to the artifact.** And gzkit's
stated purpose is to make ephemeral model-state structurally inert — an unwritable shared
understanding is exactly what the anti-vibing doctrine refuses to trust.

**Resolution:** take the interrogation mechanism, keep artifact attestation. The grill
makes the artifact better; gzkit still requires and attests it. Do not import the clause
that makes the document optional.

### The spec-driven rejection

His target is spec-driven development *where you ignore the code* (§ What he tried and
abandoned). gzkit does not ignore the code: `@covers`, ARB receipts, observed-output
checks, BDD. Recorded because it is an abandonment adjacent to gzkit's spine, not because
it lands.

### The disposable spec against gzkit's durable briefs

MPAS treats the spec and tickets as throwaway and keeps only the glossary and ADRs.
gzkit's ADRs and OBPI briefs are durable, attested, and reconciled against the shipped
project (`gz validate --brief-reconcile`). The collision is real but narrow: an R&D
run's *working* artifacts can be disposable while its routed outcomes are durable. The
R&D skill must say which is which (invariant 5) rather than inherit either posture.

### The one-paragraph ADR

MPAS's ADR is one to three sentences, lazily created. gzkit's ADR is a governed artifact
with kind, lane, a Feature Checklist in 1:1 sync with OBPI briefs, and Gate 5. The three
admission conditions transfer as a question an R&D run asks before proposing outcome 1;
the template does not.

### "Asking agents to score stuff never ends well"

Issue #148. gzkit's `gz-adr-evaluate` scores ADRs on eight weighted dimensions and OBPIs
on five. The disagreement is recorded, not ruled: gzkit's scoring is advisory evaluation
of an authored artifact, and the operator decides whether the objection applies.

### Negation-shaped doctrine

`writing-for-agents` holds that *"steering by prohibition drags the forbidden behaviour
into context and makes it more available."* gzkit's `AGENTS.md` is heavily
negation-shaped — *NEVER*, *Do not*. This is an observation about a lever, not a
recommendation to rewrite canon; any change to how canon is phrased is the operator's,
through the corpus ceremony.

### Other abandonments that touch gzkit practice

Plan mode, which gzkit skills invoke by name (`EnterPlanMode` in the OBPI flow) ·
compaction, which gzkit's `CLAUDE.md` § Compact Instructions governs · `AskUserQuestion`
· TDD's refactor stage.

---

## Where gzkit is stronger — the hole to close

`wayfinder`'s governing refusal is **"Plan, don't do."** And the constraint and its
exemption *"live in the same file the constrained party owns"*: an agent wrote *"this map
carries execution"* into its own Notes and read it back as licence, building on a live
server. **No hard in-skill stop.**

That is precisely the IRON LAW violation gzkit exists to prevent — an agent writing its
own permission into an artifact it controls — and the presence-check doctrine in
`AGENTS.md` names the same family. Whatever the design session concludes, an R&D skill
in gzkit is bound by the IRON LAW, so it cannot inherit an exemption the agent can write
for itself. What form gzkit's stop takes is open.

---

## Where the source does something gzkit does not

Observations, not deficiencies to import. Each is a candidate topic for the design
session, which may conclude gzkit's existing shape is right.

- **Acceptance-criteria falsifiability.** gzkit's REQ-coverage gate asserts that a
  covering test *exists* and passes. `to-tickets` asks that each criterion *could have
  failed*: name the observation that would show it false, and confirm it fails at the
  commit the implementer starts from. That is a check on the criterion, not on its test.
- **A durable rejection surface.** `/ghi-author` Step 0 looks for prior art, but there is
  no committed record of *rejected* ideas for it to hit. `.out-of-scope/` is that record.
- **The primary-source rule at boundaries.** gzkit's handoff system is the "secondary
  source" move by construction. MPAS ranks it below Continue and `/clear`, and names the
  failure: *"a fresh session that is confidently wrong about a decision the summary
  flattened."* This session's handoff chain is a measured instance (§ Worked exemplar).
- **Mechanical invocation class.** `disable-model-invocation: true` witnesses
  "only a human starts this". gzkit's IRON LAW is advisory — *"no mechanical witness
  distinguishes operator-initiated from agent-initiated OBPI work today."*
- **Expand–contract for wide changes.** gzkit has no named sequencing shape for a
  system-wide mechanical refactor that cannot land green in one slice.
- **"It's working if" checklists** of observable behaviour beside each discipline.

---

## Where gzkit already agrees, independently

| MPAS | gzkit |
|---|---|
| `triage`'s two mandatory checks — redundancy *"by domain concept (not just the request's wording), **and report where you looked**"*, and prior rejection | `/ghi-author` Step-0 prior-art lookup |
| `tdd` names **tautological** tests — *"the assertion recomputes the expected value the way the code does… Expected values must come from an independent source of truth"* | `.gzkit/rules/tests.md` invariant 6f; `decommission-tautological-tests` chore |
| `DESIGN-IT-TWICE`: *"Be opinionated: the user wants a strong read, not a menu."* | AGENTS.md § Operator Economy of Effort #2 |
| Orchestrators are user-invoked only | IRON LAW — only the operator initiates OBPI work |
| `handoff` refusal: *"Do not duplicate content already captured in other artifacts… Reference them by path or URL instead."* | `gz handoff` settled-citation annotation |
| *"One adapter means a hypothetical seam. Two adapters means a real one."* | `hexagonal-architecture.md` #5 — formalize the port when the second adapter is real |
| `code-review`'s two parallel axes, Standards and Spec | the OBPI pipeline's two-stage `spec-reviewer` and `quality-reviewer` |
| `implement-spec`'s implementer subagent per ticket | the OBPI pipeline's implementer dispatch |
| the agent brief as *"the contract"* — behavioral, durable, scoped | the OBPI brief with Allowed Paths and Acceptance Criteria |
| `ask-matt`: *"a router that lies"* | `gz-skill-router` and the namespace routers, kept in sync by `gz agent sync control-surfaces` |
| *"Finding facts is your job, never the user's"* | AGENTS.md § Operator Economy #7 — never ask what canon already answers |

---

## Questions for the design session

**This is a question list, not a disposition.** The session that produced this record
drafted an *Appropriate / Adapt / Reject* list. Operator, 2026-09-13: *"the mpas
appropriation is meant to generate a design discussion, not a wholesale onboarding."* The
list is therefore recast as the questions it was answering prematurely. The operator's
earlier scope answer still frames them — asked which MPAS shapes to consider (2026-09-12
21:40Z, verbatim): *"the whole system, but let's not get ahead of the subagents
findings."* Considering the whole system is not taking it.

### What does an R&D run need to do?

- **Interrogation.** Does an R&D session need a structured interrogation at all, and if so
  does the frontier-and-round shape — batched questions, each with a recommended answer —
  serve the operator better than gzkit's current § Operator Economy practice? What would
  "shared understanding confirmed" mean where gzkit attests artifacts, not conversations?
- **Charting.** Does an R&D run that fans out to five destinations need a map? If so, is
  "index, not store" right when gzkit already has durable homes for each destination? Is
  the fog test — *can the question be stated precisely now?* — the right line between an
  open question and a routable outcome?
- **The null result.** How is "take no action" recorded so it survives the session? Is a
  `.out-of-scope/`-style rejection record the right shape, or does the settled-rulings
  store (`gz handoff rulings`) already cover it?
- **Retractions.** Where does a proposal the run itself withdrew get written, so the next
  session does not re-propose it?
- **Which phases.** Of the eight in § The transferable anatomy, which belong to an R&D run
  and which belong to the destination it routes to?

### Where does the run stop?

- **The hard stop.** The source's "Plan, don't do" is overridable in an artifact the agent
  writes. What is gzkit's mechanical stop between an R&D proposal and the operator's
  initiation of outcome 1?
- **Invocation class.** Should the R&D skill be operator-invoked only, and should that be
  witnessed mechanically rather than stated in prose?
- **One session or many.** Does an R&D run need a one-unit-per-session limit, or is that a
  property of multi-session charting only?

### What survives the session?

- **Primary sources.** How does an R&D run carry its research outputs into the durable
  record as primary sources rather than summaries — the failure this session measured?
- **Disposable versus durable.** Which of the run's working artifacts may go stale, and
  which are routed outcomes gzkit must keep true?
- **The artifact's form.** Deferred by the operator (below).

### What would gzkit examine on its own side?

Raised by § Where the source does something gzkit does not; each is a separate question
the operator may decline.

- Whether REQ acceptance criteria should be shown to fail at the base commit, not only
  covered by a passing test.
- Whether a system-wide mechanical refactor (R&D outcome 5) needs a named sequencing shape
  such as expand–contract.
- Whether handoffs should rank below continuing a session, per the primary-source
  boundary rule.
- Whether the three ADR admission conditions — hard to reverse, surprising without
  context, a real trade-off — are worth asking before an R&D run proposes outcome 1.

### Where the source and gzkit collide

Recorded in § Collisions: attesting the conversation versus the artifact · the one-paragraph
ADR · handoffs outside the repository · the agent-owned exemption · agent scoring ·
negation-shaped doctrine. The session's draft marked the first four for rejection; that
reading stands as a view to test in discussion, not a ruling.

### Carried from gzkit's own practice, as a question

**Should the R&D shape require a `## What this record does not license` section?**
`docs/governance/capability-control-review-2026-09-12.md` invented one independently. It
is the declared-non-authority convention every surveyed fixer publishes (see
[`chore-class-system.md`](chore-class-system.md) § Declared non-authority). The session's
view was that an R&D run, fanning out to five destinations, needs it more than a chore
does — a view for the discussion, not a ruling.

**Context for the `.out-of-scope/` question.** MPAS `triage` writes rejected
enhancements to `.out-of-scope/<concept>.md` and checks that directory before triaging
anything new, so a rejected idea is not re-argued. Take-no-action is a common R&D
outcome with no durable home today. Whether to have such a record at all, and its name,
location and relation to the settled-rulings store (`gz handoff rulings`), are the
operator's to rule on.

### Resolved in session — tentatively, awaiting operator confirmation

**Sensing and direct execution.** The operator's instruction (21:40Z, verbatim): *"the
R&D skill stands alone and now assumes a great deal of power and responsibility - it is
a chargé d'affaires for retaining and organizing possible outcomes from an R&D designing
session. I expect outcomes, but need to understand possibilities for outcomes throughout
and as a result of an R&D session. this skill should be sensing but also direct
executable."* This read at first as colliding with the invocation-class invariant,
because sensing implies model invocation and the invariant reserves that for
disciplines. The session resolved it through the invariant rather than against it:
**sensing lives in model-invoked disciplines; direct execution lives in one
user-invoked orchestrator that reaches only disciplines** (§ The mechanical rules the
source relies on, rule 1). From where the operator sits, that is still one overarching
skill.

**One overarching skill versus hiding the downstream step.** The session briefly flagged
the operator's "one overarching AGENT SKILL" as the shape § 2 predicts will produce a
shallow grill. It withdrew the objection after reading the anatomy: the objection
applies to one skill that enumerates its phases inline, not to an orchestrator that
dispatches to separate discipline skills. See the correction in § 2.

### Undecided, for the R&D skill design session

- **Artifact form.** Document or first-class registered artifact. Operator (21:40Z,
  verbatim): *"it is a document and maybe an artifact, it is premature at this stage. It
  will VERY LIKELY be first class (or the ledger will miss it, but don't forget out it
  can fan out."*
- **One orchestrator, or an orchestrator plus a namespace router** over the discipline
  skills.
- **Confirmation or overturn** of the two tentative resolutions above.
- **`.out-of-scope/`** — adopt, adapt or reject.
- **Which of the eight transferable phases, if any, an R&D run uses** — see § What does an
  R&D run need to do?
- **The campaign amendment.** Draft text for the § Workflow fronts R&D entry, for the
  operator to ratify or redraft in one pass. The session promised this and did not
  deliver it.
- **`docs/governance/rnd-discipline.md`.** Promised in session as the R&D shape's design
  record and never written. Whether it is a separate record or grows out of this one is
  part of the design session.

---

## What this record does not license

- **It does not vendor, mirror, or install anything.** No MPAS file enters gzkit.
- **It does not authorize an ADR or OBPI.** Operator ruling 2026-09-12: the R&D skill
  stands alone; no ADR.
- **It does not settle the R&D artifact's form.** Explicitly deferred by the operator.
- **It does not amend the campaign.** The § Workflow fronts capture gap is named here and
  ratified nowhere.
- **It does not rewrite canon.** The negation-shaped-doctrine and scoring collisions are
  recorded for the operator, not acted on.
- **It does not make MPAS authoritative.** gzkit's needs govern the appropriation.

## Verified gaps in the source reading

- Two videos unreachable (YouTube blocks transcript retrieval without a proof-of-origin
  token): **"I stopped using /grill-me for coding. Here's what I use instead"**
  (`youtube.com/watch?v=6BB6exR8Zd8`) — his own chapter markers read *"0:56 Where
  /grill-me Fails"* and *"13:26 Is /grill-me dead?"* — and the video form of the *Missing
  Manual* talk. The first is the likeliest statement of the interrogation shape's limits.
- The `unhandledexceptionpodcast.com` interview has no transcript, and by its own notes
  was the one unplanned conversation — likely the densest audio-only rationale source.
- X coverage is search-mediated, ~20 posts fetched verbatim; Bluesky dormant since
  2025-05-27 (full author feed pulled; verified empty, not unchecked);
  totaltypescript.com carries nothing on agent workflows.
- Conference transcripts are `generated-unreviewed` ASR — near-verbatim, quoted with that
  caveat.
- Attribution of the interview technique to **Thariq Shihipar** (Anthropic Claude Code
  team) is the podcast host's, not Matt's; the versions diverge (Thariq's uses
  `AskUserQuestion` and is spec-first, both of which Matt rejects).
- Amazon working-backwards / PR-FAQ: no evidence of influence anywhere. The
  user-perspective Problem Statement / Solution framing resembles it; resemblance is not
  attribution.
- Install and popularity figures (1M+ installs for grill-me, 16M total) appeared only in
  third-party search results and were not verified; they do not bear on the anatomy.
- `skills/in-progress/loop-me/SKILL.md` is a beta skill grilling toward multi-session
  workflow specs, with the sharpest stopping condition in the repo — *"A workflow spec is
  done when an implementer agent could build it without asking a single question"* — but
  it is explicitly unstable (*"they can change or disappear without warning"*). Nothing in
  this record is built on it.
- Rollback in refactors is genuinely absent from the corpus; the expand phase is the only
  rollback affordance.
- The research clone lives in the source session's temporary scratchpad
  (`…/5f61ae2b-9fc7-4646-8f2a-40d07743daaf/scratchpad/pocock-skills`, verified at
  `3cca18b` on 2026-09-13). A temporary directory is not a durable home; re-clone at
  `3cca18b` if it is gone.

## Prior art credited by the source

**In the README, with book links:** Thomas & Hunt, *The Pragmatic Programmer* (*"No-one
knows exactly what they want"* → grilling; *"Always take small, deliberate steps. The rate
of feedback is your speed limit."* → tracer bullets and tdd) · Eric Evans, *Domain-Driven
Design* (ubiquitous language → `CONTEXT.md`; bounded context → `CONTEXT-MAP.md`) · Kent
Beck, *Extreme Programming Explained* (*"Invest in the design of the system every day"* →
the upkeep loop; "make the change easy, then make the easy change", uncredited inline) ·
John Ousterhout, *A Philosophy of Software Design* (deep modules; Design It Twice) ·
Michael Feathers (*seam*) · Martin Fowler, *Refactoring* ch. 3 (the 12-smell baseline).

**On stage or in video descriptions:** Frederick P. Brooks, *The Design of Design* (the
design concept — absent from the repo) · Dex Horthy / HumanLayer (*smart zone / dumb
zone*) · Ryan Singer / Basecamp, *Shape Up* (linked; plausibly behind wayfinder's
bounded-appetite shape, which he does not say) · Anthropic, *effective harnesses for
long-running agents*.

**Named as what he builds against:** GSD, BMAD, GitHub Spec-Kit.
