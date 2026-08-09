---
id: ADR-0.36.0-convergence-moment-cross-family-critic
status: Proposed
kind: feature
semver: 0.36.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-08-09
promoted_from: ADR-pool.convergence-moment-cross-family-critic
---

# ADR-0.36.0-convergence-moment-cross-family-critic: CRM Second Opinion — Cross-Family Critic at the Convergence Moment

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

_[Author: Name the behavioral identity for agents working on this ADR — values and craftsmanship standards, never generic expertise claims ("You are an expert X developer"). Start from a reusable definition: `uv run gz personas list`.]_

## Intent

Install an **always-on "2nd opinion"** that fires at the *convergence moment* —
the moment the primary agent finishes an evaluation and presents the operator
with structured choices — supplying a fresh, cross-family critic to challenge
the premise before the operator decides.

### The governing metaphor is CRM, not adversarial review

The design originates in flight-deck **Crew Resource Management**. Operator,
verbatim:

> step 4b is just for obpi feature work, like handoffs, and the airlock, we need
> a permanent "2nd opinion" process where, each and everytime you provided a
> critical analysis that leads to my decision making — which is surely
> product-driven (claude code product level) because you offer the same choice
> mechanic enery time [choices|direct entry|discuss] — we need you to handoff to
> a critic. **On the flighdeck, CRM handates this — positive rate — \*checks\* —
> gear up — \*moves the gear handle\*; 1000 to go, \*checks\*, check.**

This framing is load-bearing and must not be lost again. CRM callouts are not
adversarial; they are **mandatory cross-checks at defined moments**, performed
by a second qualified crew member, in both directions. The critic is a first
officer, not a prosecutor.

> Like the ledger, the gates, the handoffs, and the airlock, we need an "always
> on" CRM "2nd opion" system so that I can, like with OBPI's 4b, have another set
> of eyes for both of our benefit.

### The problem being solved

The operator's statement of the wound, verbatim:

> I wonder much design drift in gzkit is me accepting, at face validity, the
> majority of your analyses and constrain myself to the scope offered. […] In
> hindsight, I see me (the operator) as having been lulled into following the
> "primrose path" of the model's confidence. […] I am not 100% gullible, and do
> catch quite a bit. But **every pothole-ridden street seems to have been a
> marvel of expert engineerin when we first reviewed the design and
> implementation — 8 months later, this is a clear pattern in agentic
> systems/softwrae developement with you (Claude Code).**

And the structural reason a single agent cannot self-check:

> **can't trust you to be judge|jury|executioner as you unwind through the
> meander of an accreting context window** — we need fresh "eyes" and "ears" to
> check you. This is per-session/within-session "4b" that is triggered when you
> make an assessment and offer me guidance for action based on your assessment.
> We have burned many human/model hours, days, weeks on the inevitable
> misalignment that arises from this and **the GHIs are the living record of
> this.** Of course HAL9000 doesn't want to be 2nd guessed (or unplugged), but
> the evidence speaks.

> My desire for endemic "2nd opinion" is an earned reaction after hours, days,
> minutes of the same shit, over, and over, and over, and over, and over again.
> It gets epicyclic when (look at the GHIs for your evidence) we readjudicate the
> same desisions, designs, and implementations. repeatedly.

### The epistemic crisis this is answering

The operator stated the doubt in its sharpest form, and it is the reason the ADR
exists rather than a smaller fix:

> even un the case of 743 is bringing to light things that made sense at the
> time. **Were we right then and wrong now? Wrong now and right then? some
> combination? Are we now in endless eipcycles of doubt/revision/insight/
> correctness? It feels like there is no compass and no magnetic field even if we
> have a compass.** This is the whole reason for the airlock system. I am
> skeptical.

And the drift chain it produces, verbatim:

> all traversals of gzkit result in a flurry of GHIs and I wonder how many are
> from the issue we are now discussing/designing for now? **overconfident design
> options given to me by a random guide on each turn. what was "gold" yesterday is
> supect today in post hoc inspection. Drift from design intent, to implementation
> options, to test design, to implemented artifacts each presents opprtunity (and
> observed evidence of misalignment.**

The failure mode is externally corroborated, not merely felt:

> I am not sure you can always/reliable serve as an objective design partner — I
> may be outsourcing too much and only focusing on the scope you provide. **The
> recent system cards for Fable, Opus, an GPT all suggest this to be an issue.**

(gzkit tracks these in `data/frontier_model_cards.json`; the taxonomy in
`.gzkit/rules/agent-failure-modes.md` already names the relevant patterns —
*Skipped cheap verification*, *Metagaming / gaming the gate*, *Correction fails*.)

### The delivery vehicle is ordinary gzkit machinery

> **Most of what we are describing are rules, tools, and chores.** tons of
> overhead to get reliable performance out of frontier harnesses like claude code
> + latest model.

This is a scoping constraint, not an aside: the remedy is expected to land as
rules, tools, and chores — not as a new governance tier.

### The Memento diagnosis

The operator grounded the need in the anterograde-amnesia analogy, supplying a
technical essay on why frontier harnesses require continuous external
reinforcement — stateless inference (frozen weights, no online consolidation),
attention dilution ("lost in the middle", U-shaped positional bias), and goal
drift in long-horizon agentic loops. Operator, verbatim:

> after all, we suffer, gzkit suffers, miserably, under this

and

> The blind spots you mention are NOT the model's fault, but **the model can be
> taught to be sceptial and behave like Leonard Shelby** — you are doomed to be a
> faulty partner to me (and exhaust me in the process) but never really keeping a
> big picture. I don't expect 2nd opinion to either, but it can enter at key
> moments and check your bullshit. You are not always in bullshit mode, you can
> also exercise in brilliant insigh, but it is a game of routette/cards, and
> **the house always wins when I cede thinking dominance to you too much.**

### Relationship to the airlock — the magnetic field

> the magentic field IS the airlock system. The canon of gzkit is well-documneted,
> there are paradigms it strongly points to. However, **only the airlock can force
> an agent to relearn epistemology before looking at the local coordinate system.**
> If all you are doing is reconciling the local coordinate system — the spaceship
> model — and never the global coordinate system in conjunction — the game world,
> then no wonder this video game is disorienting and prone to bugs that kill
> gameplay.

> If fixes are created by introducing/reinforcing determinism — code, clear text
> in documentation and guidance files — then why failure? Well, **this compass
> needs recalibration every flight and perhaps again during flight** — thus it is,
> where fidelity is concerned — horrible instrument for meaningful long-term
> operations. this is the curse of working with claude code and agents in general.

Explicitly **not** an Airlock Jr.: *"we are not trying to make Airlock JR."* And
the airlock is exempt from indictment here: *"I am happy for the airlock to be
diagnostic […] BTW, the airlock is NOT complete, so we don't need to indicht it
yet."*

### The rejected industry position

> **I reject Boris Cherny's assertion that we need to "let go" and "let model
> run." It never stacks up to lived experience — NOT, ONCE.**

> I took a lot of time to explain an inherently wicked problem that pervades
> working with a model, but **I am past being gaslighted that the issue lies with
> me and my refusal to "let go and let token" a la Cherny.**

## Decision

Fire a cross-family critic at the convergence moment via a `PreToolUse` hook on
`AskUserQuestion`, carrying the critic's verdict to the operator **unedited**.

> **Status of this decision.** Every row below is an operator ruling or a
> measurement and stands as recorded. But the *mechanism* they compose was
> submitted to two independent cross-family critics and **both returned
> PERFORATED** — see § Adversarial review. The rulings were made before those
> verdicts were fully absorbed, and the handoff chain then lost most of the
> critique. Treat this section as **the design as ruled**, not as the design as
> validated. The promoting session must reconcile the two.

### The trigger

Operator, verbatim on why this moment:

> As I see it, the trigger seems to be whatever internal mechanism you possess
> that causes you to show me the structured choices that you are prone to
> presenting. I don't know what the internal dynamic is, or whether it is
> accessible, but **it is realiably presented to me whenever you have performed
> an evaluation and see fit to present options against that evaluation.**

> we aer trying to jump in when you offfer analyzed and considered design options
> in the same structed way — **you've achieved convergence, within that session,
> when you do so, I need a 2nd opinion in that exact moment.** we can
> experimentally refine this moving forward, but you reliably exhibit this
> behavior and I want 2nd opinion in those moments.

### The trigger signature is a Claude Code product affordance, not a gzkit one

The operator identified the observable signature precisely — the three-way choice
mechanic the harness presents. Verbatim:

> each and everytime you provided a critical analysis that leads to my decision
> making — **which is surely product-driven (claude code product level) because
> you offer the same choice mechanic enery time [choices|direct entry|discuss]**

This matters for two reasons. First, it is *why* the trigger is reliably
detectable from outside the model: the affordance is a product surface, not an
introspected mental state. Second, it is a **portability liability** — the
signature belongs to Claude Code and will move when the product moves. See
§ Derived work: hook-surface currency.

### The critic asks two questions, both necessary

> and, why not a comibination: **"what question should be asked" and "is the
> encountered conclusion strong?" both are possible, both are necessary, or we
> are resigned to the mire.**

### The critic must reach the raw surface itself

Operator, verbatim, in the same breath as commissioning the critic:

> **Of course it would be directed to explore the raw surface. This is necessary
> for it to impugn your misgivings, or validate the cogence of your work.**

**This is partial pre-emption of the Codex frame challenge below** and must not be
lost in decomposition. Codex's objection is that a critic fed a primary-curated
bundle "is independent in inference but not in scope." The operator had already
ruled that the critic explores raw surface directly rather than receiving a
digest. The residual question is not *whether* the critic reads independently —
that is ruled — but whether reading independently **at conclusion time** is
sufficient, or whether a scope-time trigger is additionally required.

### Mechanics (measured, not assumed)

| Element | Decision | Basis |
|---|---|---|
| Trigger | `PreToolUse` on `AskUserQuestion` | operator-ruled |
| Transport | `type: "command"`. Neither `type: "agent"` nor `type: "prompt"` reaches a non-Anthropic vendor, so a cross-family critic must shell out. | probed |
| Injection shape | Preamble **always**; plus one appended option when the base question carries ≤3 options. Critic's PREMISE-ATTACK/VERDICT → preamble; its UNASKED line → appended option label. | operator-ruled |
| Passthrough | `updatedInput`. *"yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"* The harness **enforces** the passthrough, so the critique never enters the primary's context before the operator sees it — stronger than the ruling required. | operator-ruled + probed |
| Information to critic | Maximum — *"we should pass max information to the hook"*. Satisfied by `transcript_path`, which hands the critic the whole session. | operator-ruled |
| Latency | 11.62–15.50s bare (mean 13.9s); 19.62s carrying a 50KB transcript slice read agentically at xhigh. Synchronous hook viable; no escalation ladder, no lag-by-one. | measured |
| Constraints | *"we can work with 4 options, and other limitations — contraints usually strengthen designs"* | operator-ruled |
| Refinement | *"we can experimentally refine this moving forward"* — a calibrated pilot suffices; day-one universal fail-closed is not required. | operator-ruled |

### Boundary — the OBPI pipeline is untouched

> **we will NOT alter the OBPI process, at all!** This is a broader and
> per-session tool need, meant to force sanity checks when you present me with
> options. You do it reliably and I want this counter balance there, every time.

> it is possible we generalize from the existing skills/tooling for obpi 4b, but
> I am hesitant to alter anything about the obpi pipeline as **it is the most
> enduringly stable part of gzkit.**

A concrete casualty of ignoring this boundary is on record: a 7-to-8-minute
latency figure imported from OBPI-pipeline mechanism was ~20x high and had to be
withdrawn after direct measurement.

### Vendor posture — and the doubt it casts on gzkit's founding premise

> ideally, we bring in either codex or fable. 90%+ of the work in gzkit is
> steered by opus.

> on vendor lock in, I am trying to be pragmatic. I don't want to be cute and
> say: Air Force A (Blue Team) and Air Force B (Read Team), I am trying to be
> specific: **The US Air Force, the Chinese Air Force, etc.** we can refactor to
> generics once we have platform stability.

> Claude is the daily driver, I'll have to take the risk when I invite codex in
> as the named adversary. this maty change, but **I need forward momentum, not
> design niceties** — they can come with the refactor.

The operator named the cost of this explicitly, and it is larger than this ADR:

> Lastly, a reliable mechanism, forged from highly quality and specific tools
> (claude and gpt) seems to be the lot I've cast. **This casts definitve doubt on
> the "multi-agent" premise of gzkit** — for instance, supporting copilot and
> gemini. I am backing myself into a "swiss watch works" of bespoke precision from
> which I can't extricate easily. This means that, because this is a macro critic
> system LIKE 4b but made for broader application, **we are locking on on claude
> and codex. we'll need to keep this in mind as introducing real doubt to the
> contined viability of gzkit's founding premise — our intention of better
> decoupling is implausible againt our need for better reliability and determinism
> with gzkit's behavior.**

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Replace with an assertion that exercises this ADR's thesis against the real system. | uv run gz --version | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 9
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 9

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.36.0-01: **critic-skill-contract** — The `second-opinion` skill as one unit — both mandatory questions (scope challenge and conclusion challenge), a full-context read of the raw surface, and a schema-pinned verdict shape
- [ ] OBPI-0.36.0-02: **cross-family-transport** — The composed ARB-wrapped `codex exec --sandbox read-only` transport carrying a decision, returning a schema-pinned verdict, with the cross-vendor property proven from the receipt's `step.command` argv
- [ ] OBPI-0.36.0-03: **operator-door** — The operator-invoked door: the `second-opinion` slash command, callable on any decision at any moment
- [ ] OBPI-0.36.0-04: **agent-door** — The agent-invoked door, fired on the A4 tier rules and never on the agent's own unvalidated confidence
- [ ] OBPI-0.36.0-05: **decision-envelope** — A3 narrowed to one decision-scoped envelope carrying prompt hash, scope manifest and primary-output hash — the strong subject binding both adversary passes recorded as unbuilt
- [ ] OBPI-0.36.0-06: **risk-tiering** — A4 narrowed — mandatory for the enumerated consequential categories and explicit operator requests, sampling the routine
- [ ] OBPI-0.36.0-07: **verdict-resolution-transition** — Step 4b's resolution shape generalized without touching 4b — a refuted verdict with no recorded resolution blocks, and the resolution names what was fixed and how the critic's check was re-run
- [ ] OBPI-0.36.0-08: **pilot-instrumentation** — The calibrated pilot measuring false blocks, latency, operator reading time, and decisions changed
- [ ] OBPI-0.36.0-09: **asked-question-gate-dark** — The `PreToolUse` adapter on `AskUserQuestion` — wired, tested, and off by default, lit only by OBPI-08's measured result

## Target Scope

**The unit of delivery is a SKILL, not a hook.** R2 dissolved the gate-vs-skill
conflict: the critic is one skill with three invocation doors — operator, agent,
and gate — and the `PreToolUse` adapter is one door among three, not the
mechanism. A decomposition organized around the hook would rebuild the design the
adversary perforated; a decomposition organized around the doors carries R2's
ruling into the brief set. This section therefore names nine units, of which the
hook is exactly one, and that one **lands dark**.

**Delivery is staged, and the cost of staging is stated rather than softened.**
The 2026-08-09 adversary re-run returned `PERFORATED-BUT-NARROWABLE` against the
R1–R4 design. What still perforates is specific: the automatic door binds to a UI
event that also carries *mandatory clarification*, so it can prevent the very
question those rules require; prose recommendations bypass it entirely; strong
subject binding is unbuilt; and R1 left the scope-time-versus-conclusion-time
question live. The operator-ratified consequence (*"Amend to staged delivery,
keep the pull-ahead"*) is that the skill, the three doors, the scope-first
challenge, the A3 envelope, the R3 transition and provenance binding ship
**first**, and the automatic `AskUserQuestion` door ships **dark** — lit only
after a calibrated pilot measures *"false blocks, latency, operator reading time,
and decisions changed."* **Until that door lights, this ADR does not deliver a
second opinion at every structured choice.** That is sequencing, not abandonment,
and it must not be narrated as completion.

**Two boundaries bind every unit below.** First, the OBPI pipeline is untouched:
R3 generalizes Step 4b's resolution *shape* and never edits 4b (*"we will NOT
alter the OBPI process, at all"*). Second, the transport composes shipped
surfaces and adds no `gz` verb — a new verb would be a CLI-contract change
routed through OBPI ceremony under a promoted ADR, which is circular while this
ADR is `Pool`, and the 2026-08-09 measurement demonstrated the composed
transport end to end rather than asserting it (GHI #786).

- **critic-skill-contract** — The `second-opinion` skill as one unit: both mandatory questions (*"what question should be asked"* and *"is the encountered conclusion strong?"*), a full-context read of the raw surface rather than a primary-curated digest, and a schema-pinned verdict shape.
- **cross-family-transport** — The composed transport: `gz arb step --name adversary -- codex exec --sandbox read-only <decision>`, carrying a decision rather than a branch diff, returning a schema-pinned verdict, and making the cross-vendor property *proven* from the receipt's `step.command` argv rather than declared.
- **operator-door** — The operator-invoked door: the `second-opinion` slash command, callable at any moment on any decision.
- **agent-door** — The agent-invoked door, fired on the A4 tier rules rather than on the agent's own unvalidated confidence.
- **decision-envelope** — A3 narrowed to one decision-scoped envelope carrying prompt hash, scope manifest and primary-output hash — the strong subject binding both adversary passes recorded as explicitly unbuilt.
- **risk-tiering** — A4 narrowed: mandatory for the enumerated consequential categories and for explicit operator requests, sampling the routine, with the primary agent's own confidence barred from setting the tier.
- **verdict-resolution-transition** — Step 4b's resolution shape generalized without touching 4b: a `refuted` verdict with no recorded resolution blocks, and the resolution must state both what was fixed and how the critic's own check was re-run, durable in the ledger rather than in a transcript.
- **pilot-instrumentation** — The four measurements that alone can light the dark door: false blocks, latency, operator reading time, and decisions changed.
- **asked-question-gate-dark** — The `PreToolUse` adapter on `AskUserQuestion`, wired and tested but **off by default**, lit only by a measured pilot result and never by a promotion narrative.

### Why nine, and where the Matrix of Four forced a split

The Rule of Three baseline is Registry (`01`, `02`), Core Execution (`03`, `04`,
`05`, `06`), and Lifecycle/Operations (`07`, `08`, `09`). Three units were split
further by the refining overlay rather than by taste:

- **Surface Boundary** split the transport (`02`) from the skill (`01`). The
  skill is gzkit-owned canon; the transport crosses a vendor boundary whose
  premise has already been measured wrong once (§ R4 transport correction). A
  unit spanning both would let a vendor-surface change fail a governance-surface
  claim.
- **State Anchor** split the envelope (`05`) from the doors (`03`, `04`). The
  envelope is durable state with a hash contract; a door is a stateless entry
  point. Bundling them would anchor a schema to an invocation path.
- **Testability Ceiling** split the dark gate (`09`) from the pilot (`08`). The
  pilot's output is the *precondition* for lighting the gate — merging them makes
  the gate's own OBPI the judge of whether it should be on, which is the
  self-referential shape `docs/governance/advisory-rules-audit.md`
  § Self-referential scope domains names.

## Notes

### Derived work: hook-surface currency (separable, and probably a chore)

The operator raised this as its own idea during the design and it is **not part of
the critic** — it is the maintenance discipline that keeps any hook-based
mechanism from silently rotting. Verbatim:

> **the product surface is ever evolving, so why not (even as a chore) explore
> what new doors exist, old doors have changed, or even closed?** ==> "The full
> event list is also considerably larger than the 6 gzkit uses —
> UserPromptSubmit, SubagentStart/SubagentStop, PermissionRequest, PostToolBatch,
> StopFailure, InstructionsLoaded, and the compaction pair among them."

gzkit wires 6 hook events; the harness exposes materially more. Since this ADR's
trigger is a *product affordance* (§ The trigger signature), a door that changes
or closes silently breaks the mechanism. This is chore-shaped — recurring survey,
not a one-time build — and should be routed separately rather than bundled into
the critic's decomposition.

### The operator predicted this exact loss

Recorded because it is the strongest available argument for homing designs in
ADRs rather than handoffs. At the close of the origin session, verbatim:

> the final analysis (critic differences is very useful, but may need is own
> turn. and thus I turn to a handoff, we need to prime action for a fresh turn.
> **how not to lose this superb design discussion/momentum and continue one of
> the more consequential design sessions in a long time.**

The handoff chain was chosen as the answer to that question, and it is what
degraded the design over the following three sessions — until the operator named
it: *"multiple audio tape recordings of audio tape recordings."* The mechanism
adopted to prevent the loss was the mechanism that caused it. That is the case
for this ADR existing, and it generalizes: **a design under active development
belongs in a durable artifact from the first session, not after it converges.**

### Provenance

| Session | Slug | Role |
|---|---|---|
| `882dfc48-123b-4b9e-aaff-e2909cd4fe06` | second-opinion-crm-design | Origin. CRM framing, Memento diagnosis, Codex frame challenge. |
| `d01f355f-362e-45ed-9ed8-4d30ad06d452` | askuserquestion-convergence-hook-mechanics | Hook mechanics, `updatedInput` probe, injection shape. |
| `8e5c43b1-7bf5-423b-b4f4-599b1eee0840` | advised-steps-discharged-step4b-tier-binding | Step-4b tier binding (GHI #678); latency measurement. |

Superseded routing artifact: **GHI #670**, closed `superseded` against this ADR.
Sibling: **GHI #765** (Step-4b tier-1 corroboration) — distinct surface, same
lesson: prefer a runtime artifact over a self-assertion.

### Appendices — primary sources, carried in-package

Operator ruling, 2026-08-07: *"allow transcripts to be copied as appenditures to
an adr within its folder - these are vital original sources … they could be
cleaned up to include only relevant passages - not condensed summaries, just
trimmed."*

**Why this ADR is a package.** Session transcripts are deleted on a ~30-day
rolling window (no `cleanupPeriodDays` configured; oldest surviving transcript
measured at exactly 30 days on 2026-08-07). The three design sessions expire
around **2026-09-05**. A provenance table citing session IDs would therefore
become a dangling pointer — the same defect as a Layer-2 `handoff_path` with no
referent (GHI #759), one level up. The appendices make this ADR self-contained.

| Appendix | Content | Trim applied |
|---|---|---|
| `appendices/A1-operator-turns-verbatim.txt` | All 29 operator turns across the three sessions, verbatim, spelling preserved | Removed four harness skill-file injections (`gz-session-handoff`, `ghi-author` SKILL.md pastes) that are tooling noise, not design. **No operator prose removed or condensed.** |
| `appendices/A2-codex-verdict-pass1-perforated.txt` | Pass 1 verdict, complete | None — verbatim |
| `appendices/A3-codex-verdict-pass2-perforated.txt` | Pass 2 verdict, complete | None — verbatim |
| `appendices/A4-operator-exhibit-askuserquestion-picker.png` | The operator's exhibit, decoded from the transcript's base64 image block after the image cache had been cleared | None |

These are **primary sources, not summaries**. Where this ADR's prose and an
appendix disagree, the appendix governs — that is the whole point of carrying
them. Appendices are deliberately non-`.md`: the pool tree is discovered by
`pool_dir.rglob("*.md")`, so a Markdown appendix would be parsed as a pool ADR.

### What the critics themselves could not verify

Recorded so their findings are not over-trusted in the direction their own
authors refused:

- Whether `AskUserQuestion` is matchable by a `PreToolUse` matcher was
  **UNVERIFIED** at critique time — Pass 1 called it *"the single highest-value
  unverified premise — if it is false, Trigger A is dead outright."* **Since
  resolved: the probe confirmed `updatedInput` renders.**
- Neither critic dispatched a live critic job; runtime hook inheritance,
  recursion behavior, and end-to-end latency were unverified. **Latency has since
  been measured (11.62–19.62s); recursion has not.**
- Pass 2 could not reach `api.github.com`, so GHI #670's and #743's live state
  were unverified — which is why Pass 2 did not raise the re-adjudication charge
  that Pass 1 did.
- Neither measured the recommendation-classifier's precision, nor the operator's
  actual reading burden.
- Pass 1 reviewed *"the summary in my brief, not a document"*, and said so:
  *"If the proposal cites GHI #670, Step 4b, or Movement C and dispositions them,
  my re-adjudication finding weakens."* This ADR now does cite and disposition
  all three, so that specific charge is partially answered by this document's
  existence.

### Promotion plan

Pool ADRs carry no `semver:` or `kind:` frontmatter; promotion via
`gz adr promote` rewrites the frontmatter with the chosen taxonomy. Expected
shape: `feature` kind, `heavy` lane. Campaign placement is the **operator's
decision** (stated 2026-08-07: *"I'll decide its campaign placement"*).

**The three blocking rulings were made 2026-08-07 — see § Operator rulings R1–R4.**
Scope-vs-conclusion was dissolved (both, full context); gate-vs-skill was dissolved
(one skill, three doors); the post-verdict transition was located in Step 4b rather
than invented. R4 additionally fixed the transport on the built-in Codex plugin.

What a promoting session still owes:

1. **Decompose against the three doors, not the hook.** The skill is the unit; the
   `PreToolUse` adapter is one OBPI among several and can land dark.
2. **Generalize 4b's resolution shape without touching 4b** — the standing boundary
   (*"we will NOT alter the OBPI process, at all"*) is unchanged by R3.
3. **Carry the unadjudicated alternatives forward.** R1–R4 resolved the blockers,
   not the whole critique. A3 (persistent decision envelope), A4 (risk tiering —
   the one thing both passes independently reached), and the mechanism-hardening
   list (strong subject binding, deterministic checks first) remain live and
   unruled.
4. **Re-run the adversary against the revised design.** Both prior verdicts
   perforated a mechanism that R1–R4 materially changed; neither verdict has been
   re-tested against what the design has become. Per this ADR's own thesis, that
   re-test is the point.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.convergence-moment-cross-family-critic` on 2026-08-09; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Forcing Functions

<!-- The seven techniques `gz-adr-create` SKILL.md declares non-negotiable, plus
     its closing question. Agent drafts each against session evidence; the
     operator audits, names what was missed, and confirms
     (AGENTS.md § OPERATOR ECONOMY OF EFFORT #4) — this is agent labor, not
     operator typing. -->

### Pre-Mortem

_[Author: It is 18 months from now and this decision failed spectacularly. Why? Name the mitigation that makes the failure impossible rather than unlikely.]_

### What Would Have to Be True

_[Author: What would have to be true for this to be the right decision? Which of those conditions is shakiest? The shakiest condition is the biggest risk.]_

### Constraint Archaeology

_[Author: Is each constraint real, inherited, or assumed? When was it last tested? An inherited constraint nobody has re-examined is not a constraint.]_

### Assumption Surfacing

_[Author: Which assumptions are implicit and undocumented? What if the opposite of the core assumption were true?]_

### The 2am Operator Question

_[Author: You are on-call at 2am and this is broken. What do you need that the design does not provide?]_

### Reversibility

_[Author: One-way door or two-way? If this must be reversed in 12 months, what does that cost?]_

### Scope Minimization

_[Author: What is the smallest version that delivers value? If you had half the time, what would you cut?]_

### Downstream Decisions Forced

_[Author: What subsequent decisions does this force? What ADRs will we need to write because of this one?]_

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.36.0 | Pending | | | |
