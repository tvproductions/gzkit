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

---

## Why this record exists

gzkit has a newly designated **R&D** class of work — the fourth Workflow front in the
active campaign. Operator characterization, 2026-09-12:

> *"MOST adrs came from an externally or observationally motivated inquiry I develop
> from working with gzkit and reasoning about its purpose … Almost everything
> comprehensive or potentially new usually emerges from this newly-designated R&D class
> of work."*

Earlier in the same session, 21:10Z: *"I commonly do this sort of work and the documentation and
ledger will bear this out. In fact MOST future ADRs come form work exactly like this
work."*

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
implementation."* Only the operator converts an R&D proposal into an ADR, and the skill
must carry that stop mechanically (§ Where gzkit is stronger).

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

Two lessons from the exemplar belong in the skill. **First, the capture failure:** the
run's first handoff recorded the destinations and lost the reasoning, and the operator
rejected it as one that *"misses the major chore and R&D work."* A chargé d'affaires
that retains outcomes but not the reasoning behind them has failed at its job. **Second,
the retraction is an outcome:** the run proposed two chores and then withdrew them on
canon grounds. With no durable home, a retracted proposal is re-proposed by the next
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
Matter More Than Ever*:

> *"**Frederick P. Brooks, The Design of Design** … talks about this idea called **the
> design concept**. It's that when you have more than one person designing something
> together, you have this idea sort of floating between you, this ephemeral idea of the
> thing that you're building… **It's not an asset. It's not something you can put in a
> Markdown file. It is the invisible sort of theory of what you're building.**"*
>
> *"**Me and the AI don't share a design concept.** So I came up with a skill…
> 'Interview me relentlessly'… It turns the AI into a kind of **adversary**."*

This explains the repo's most surprising fact: **`grilling` emits no file.** Its target
is an unwritable shared model; documents are downstream and secondary.

---

## The skill set, as read

### Disciplines (model-invoked — the agent reaches for these)

| Skill | Shape | Emits | Stopping condition |
|---|---|---|---|
| **`grilling`** | Not phased. Model the subject as a **design tree**; compute the **frontier** = *"every decision whose prerequisites are already settled"*; ask the whole frontier in one numbered round, each with a recommended answer; wait; recompute | **nothing** | *"The frontier is empty"* **and** *"Do not act on it until the user confirms you have reached a shared understanding."* |
| **`domain-modeling`** | Five inline behaviours: challenge against glossary · sharpen fuzzy language · discuss concrete scenarios · cross-reference with code · update inline | `CONTEXT.md` (glossary only) · `docs/adr/NNNN-slug.md` | *"Don't batch these up: capture them as they happen."* |
| **`codebase-design`** | Reference, not a sequence. Fixes vocabulary: module, interface, implementation, depth, **seam** (credited to Michael Feathers), adapter, leverage, locality | nothing | n/a |
| **`tdd`** | red → green, one vertical slice at a time | tests + code | per slice |
| **`diagnosing-bugs`** | Six gated phases: feedback loop → reproduce+minimise → hypothesise → instrument → fix+regression test → cleanup | fix + regression test + a stated hypothesis in the commit | four-box Phase-6 checklist |
| **`prototype`** | throwaway, logic or UI branch | one HTML file on a `prototype/<name>` branch | the design question has a one-line verdict |
| **`research`** | background agent → primary sources → cited markdown | one cited `.md` | file written |
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

**There is no `/plan` skill and no `/refactor` skill.** The source says so itself:
*"There is no dedicated `/refactor` skill for that case yet."* Planning is `to-tickets`
for a single session and `wayfinder` across many. The session's reading found
refactoring guidance in three places but did not record which three; the table above
shows `improve-codebase-architecture` and the `to-tickets` prefactoring step as
candidates. Re-read the source at `3cca18b` before citing the set. `grill-me` is a
one-line wrapper; the mechanism is `grilling`. The operator's
first framing — *"grill me, plans, specs, refacotring"* — names shapes the source
distributes differently, and the appropriation follows the source's anatomy, not the
names.

**`domain-modeling` gates ADR authoring on three conditions, all required:** the
decision is hard to reverse, it would be surprising without context, and it is the
result of a real trade-off. *"If any of the three is missing, skip the ADR."* Worth
comparing against gzkit's own ADR admission when the R&D skill decides what to propose
under outcome 1.

### `wayfinder` in full — the R&D-shaped one

Largest skill in the repo (~2,000 words). Two modes, hard-broken from each other.

**Chart:** name the destination (grilling + domain-modeling) → grill again **breadth-first**
to map the frontier → create map issue → create specifiable tickets, then wire blocking
edges **in a second pass** (*"issues need ids before they can reference each other"*) →
fire research subagents in parallel → *"**Stop:** charting is one session's work; it
hand-resolves nothing."*

**Work:** load map (low-res only) → choose a frontier ticket, **claim by assigning before
any work** → resolve, *"zoom as needed"* → post resolution comment, close, append one line
to Decisions-so-far → graduate fog into new tickets.

**The map's five sections:** `Destination` · `Notes` · `Decisions so far` (index only) ·
`Not yet specified` (**the fog**) · `Out of scope`.

**Four ticket types:** `research` (AFK) · `prototype` (HITL) · `grilling` (HITL, *"the
default case"*) · `task` (*"the one type that does rather than decides"*).

**Load-bearing rules:**

- *"**Plan, don't do.** …absent that, produce decisions, not deliverables."*
- *"The map is an **index, not a store** … a decision lives in exactly one place, its ticket."*
- *"a grilling agent that answers its own questions has broken this"*
- Fog-vs-ticket test: *"whether you can **state the question precisely now**, not whether you can answer it now."*
- Hard session limit: *"**never resolve more than one ticket per session**, with the exception of research tickets."*
- Null-result exit: *"If this surfaces no fog… you don't need a map. **Stop and ask the user.**"*
- Hands off to `to-spec` invoked against **the map issue**, never the tickets.

---

## The mechanical rules worth taking wholesale

### 1. The invocation-class invariant

From `.agents/invocation.md`: every **orchestrating** skill is user-invoked
(`disable-model-invocation: true`); every reusable **discipline** is model-invoked. The
invariant:

> *"A user-invoked skill may invoke model-invoked skills, but it can **never** reach
> another user-invoked skill."*

Cross-skill calls must name the tool — `Call the Skill tool with "grilling"` — never a
bare `/skill` in prose, one skill per call. His stated reason:

> *"Every time you have a model-invoked skill, you get **a cost in unpredictability**…
> the model may just choose not to follow it… **you're removing a class of problem from
> even being a problem.**"*

**This is the answer to "one overarching skill."** One user-invoked orchestrator that
reaches only disciplines satisfies both the operator's instruction and the mechanic. It
also matches gzkit's IRON LAW, reached independently.

### 2. Hide the downstream step

> *"in plan mode we have two steps … the ask-clarifying-questions **just doesn't ever do
> enough leg work. It sees that its ultimate goal is to create a plan, and so it just
> does a small amount of leg work … and then eagerly creates the plan.**"*
>
> *"we have step one and step two, but **the agent only sees one step at a time** …
> increasing leg work on the step that you're on by **hiding the future goal**."*

A single skill that merely *names* its phases buys none of this — *"an inline call leaves
the later steps in context and clears nothing."*

**What this rule does and does not require — a correction made in session.** Hiding the
downstream step is a matter of **separate skills**, not **separate context windows**.
The session first read it as demanding a context break between every phase, then
corrected itself against § 4: MPAS keeps grill → spec → tickets **inline**, in one
unbroken context (*"Keep steps 1–3 in one unbroken context window"*). Each step is a
separately invoked skill, so the agent sees only the step it is on. The hard breaks come
later — at implementation, and between `wayfinder` tickets. The rule argues against one
skill that *enumerates* its phases, not against one session that runs several skills.

### 3. Frontier batching defeats passive assent

One-question-at-a-time was the **original** default and was abandoned:

> *"I just modified /grill-me locally to ask all its questions at once … and I kind of
> loved it … **doesn't have the failure mode where you just say 'I agree' turn after
> turn.**"* (2026-07-15)
>
> *"Before: 13 questions, 13 rounds. After: 13 questions, 3 rounds. **Still only asks
> questions at the 'frontier' — i.e. those that don't depend on any other decisions.**"* (2026-07-16)

Batching defeats passivity; the frontier makes batching safe. This sharpens gzkit's
§ Operator Economy of Effort, which asks for economy but names no mechanism.

### 4. Context boundaries: hard break vs inline

| Boundary | Kind |
|---|---|
| grill → to-spec → to-tickets | **INLINE — must not break.** *"Keep steps 1–3 in one unbroken context window"* |
| to-tickets → implement, and between tickets | **HARD BREAK** — one ticket per fresh context |
| grilling ↔ prototype | **HARD BREAK both directions**, via `/handoff` |
| wayfinder chart → work; ticket → ticket | **HARD BREAK** |
| implement → code-review | inline, but the two review axes are parallel subagents |

Boundary procedure, first-yes-wins: **Continue → `/clear` → `/handoff` → Subagent →
`/compact`.** Compact is last by design.

---

## Collisions with gzkit — resolve deliberately, do not inherit

### The attestation inversion

Asked whether he reviews the generated spec:

> *"**Yeah, I don't look at these. I don't look at these.** … what am I testing at this
> point? … I have reached the same wavelength as the LLM using the Grill Me skill …
> **all I'm doing is essentially checking the LLM's ability to summarize.**"*

**He attests to the conversation. gzkit's Gate 5 attests to the artifact.** And gzkit's
stated purpose is to make ephemeral model-state structurally inert — an unwritable shared
understanding is exactly what the anti-vibing doctrine refuses to trust.

**Resolution:** take the interrogation mechanism, keep artifact attestation. The grill
makes the artifact better; gzkit still requires and attests it. Do not import the clause
that makes the document optional.

### The spec-driven rejection

> *"I would get code out … and then I would run it, I would get worse code. And then I did
> it again, I got even worse code… **The idea that we can just ignore the code and just
> have the code let it manage itself is just sort of vibe coding by another name.**"*
>
> *"**I think code is not cheap. In fact, bad code is the most expensive it's ever been.**"*
> · *"**the code is your battleground.**"*

His target is spec-driven-*where-you-ignore-the-code*. gzkit does not: `@covers`, ARB
receipts, observed-output checks, BDD. Recorded because it is an abandonment adjacent to
gzkit's spine, not because it lands.

### Other abandonments

Plan mode (dated reversal — *"The whole point of planning is to get on the same
wavelength with the LLM, not to generate an asset you don't read"*) · compacting ·
`AskUserQuestion` (*"broken in a ton of different ways"*) · TDD's refactor stage · the
skills `caveman` and `zoom-out` (*"went unused in practice"*).

---

## Where gzkit is stronger — the hole to close

`wayfinder`'s governing refusal is **"Plan, don't do."** And:

> the *"plan, don't do"* default is overridable in `Notes`, **which the agent writes** —
> he documents an agent granting itself execution licence this way. **No hard in-skill stop.**

That is precisely the IRON LAW violation gzkit exists to prevent — an agent writing its
own permission into an artifact it controls. The gzkit appropriation must carry a hard
stop the source does not have.

---

## Where gzkit already agrees, independently

| MPAS | gzkit |
|---|---|
| `triage`'s two mandatory checks — redundancy *"by domain concept (not just the request's wording), **and report where you looked**"*, and prior rejection | `/ghi-author` Step-0 prior-art lookup |
| `tdd` names **tautological** tests — *"the assertion recomputes the expected value the way the code does… Expected values must come from an independent source of truth"* | `.gzkit/rules/tests.md` invariant 6f; `decommission-tautological-tests` chore |
| `DESIGN-IT-TWICE`: *"Be opinionated: the user wants a strong read, not a menu."* | AGENTS.md § Operator Economy of Effort #2 |
| Orchestrators are user-invoked only | IRON LAW — only the operator initiates OBPI work |
| `handoff` refusal: *"Do not duplicate content already captured in other artifacts… Reference them by path or URL instead."* | `gz handoff` settled-citation annotation |

---

## Proposed disposition

**Appropriate:** the frontier/grilling mechanic with batched rounds · the fog concept and
its state-the-question-precisely test · the map-as-index-not-store rule · the
invocation-class invariant · hide-the-downstream-step decomposition · the explicit
null-result exit · typed tickets (research / prototype / grilling / task) · the
one-unit-per-session limit · a durable `.out-of-scope/` record for rejected work · the
strength badge (`Strong | Worth exploring | Speculative`) from the architecture survey.

**Adapt:** the map artifact — gzkit likely needs it first-class with ledger events, since
*"the ledger will miss it"* otherwise (operator, 2026-09-12), and it must model fan-out to
all five destinations. His map is a tracker issue; gzkit's may not be.

**Reject:** attesting the conversation instead of the artifact · the one-paragraph ADR
template · handoffs written to the OS temp dir (gzkit's are Layer-2 provenance, in-repo) ·
the soft `Notes` override on "plan, don't do".

**Scope of appropriation.** Asked which MPAS shapes to take, the operator answered
(2026-09-12 21:40Z, verbatim): *"the whole system, but let's not get ahead of the
subagents findings."* The lists above are proposals against the whole system, and
nothing on them is ratified.

**Carry into the R&D shape from gzkit's own practice:** a required `## What this record
does not license` section. `docs/governance/capability-control-review-2026-09-12.md`
invented it independently. It is the declared-non-authority convention that every
surveyed fixer publishes (see [`chore-class-system.md`](chore-class-system.md) §
Declared non-authority), and an R&D run, which fans out to five destinations, needs it
more than a chore does.

**Proposed, not ratified: `.out-of-scope/`.** MPAS `triage` writes rejected enhancements
to `.out-of-scope/<concept>.md` and checks that directory before triaging anything new,
so a rejected idea is not re-argued. Take-no-action is a common R&D outcome with no
durable home today. The directory's name, location and relation to the settled-rulings
store (`gz handoff rulings`) are the operator's to rule on.

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
user-invoked orchestrator that reaches only disciplines** (§ The mechanical rules worth
taking wholesale, rule 1). From where the operator sits, that is still one overarching
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
- **It does not make MPAS authoritative.** gzkit's needs govern the appropriation.

## Verified gaps in the source reading

- Two videos unreachable (YouTube blocks transcript retrieval): **"I stopped using
  /grill-me for coding. Here's what I use instead"** — his own chapter markers read
  *"Where /grill-me Fails"* and *"Is /grill-me dead?"* — and the video form of the
  *Missing Manual* talk. The first is the likeliest statement of the interrogation
  shape's limits.
- The `unhandledexceptionpodcast.com` interview has no transcript.
- X coverage is search-mediated, ~20 posts fetched verbatim; Bluesky dormant since
  2025-05-27 (verified empty, not unchecked).
- Conference transcripts are `generated-unreviewed` ASR — near-verbatim, quoted with that
  caveat.
- Attribution of the interview technique to **Thariq Shihipar** (Anthropic Claude Code
  team) is the podcast host's, not Matt's; the versions diverge (Thariq's uses
  `AskUserQuestion` and is spec-first, both of which Matt rejects).

## Prior art credited by the source

Frederick P. Brooks, *The Design of Design* (the design concept) · Dex Horthy /
HumanLayer (*smart zone / dumb zone*) · Ryan Singer / Basecamp, *Shape Up* · Michael
Feathers (*seam*) · Anthropic, *effective harnesses for long-running agents*.
