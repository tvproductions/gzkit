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

An R&D run fans out to any or all of five destinations:

1. ADR / OBPI · 2. GHI / direct fix · 3. chores · 4. control surface, rules, docs,
skills, structures, hooks · 5. broad one-shot refactorings and recalibrations, often
system-wide

Plus a sixth outcome the operator names as common: **take no action.**

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

**Undecided, for the R&D skill design session:** whether the R&D artifact is a document or
a first-class registered artifact (operator: *"VERY LIKELY first class … but it can fan
out"*, and *"premature at this stage"*) · whether the discipline is one orchestrator or an
orchestrator plus a namespace · how "sensing" is reconciled with the invocation-class
invariant, since sensing implies model-invocation and the invariant reserves that for
disciplines.

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
