---
id: ADR-pool.convergence-moment-cross-family-critic
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.convergence-moment-cross-family-critic: CRM Second Opinion — Cross-Family Critic at the Convergence Moment

## Status

Pool

> **Fidelity note.** This ADR was recovered from the three design-session
> transcripts (`882dfc48`, `d01f355f`, `8e5c43b1`, 2026-08-06/07), not from the
> handoff chain that summarized them. The operator's assessment of that chain,
> verbatim (2026-08-07):
>
> > I have lost very high quality design discussion by allowing the design to
> > spread across handoffs. […] this has turned out to be multiple audio tape
> > recordings of audio tape recordings where the quality is dissipating rapidly
>
> Operator prose below is quoted verbatim from the transcripts, spelling and
> typos preserved. Where this document paraphrases, it says so.

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

### The critic asks two questions, both necessary

> and, why not a comibination: **"what question should be asked" and "is the
> encountered conclusion strong?" both are possible, both are necessary, or we
> are resigned to the mire.**

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

## The unresolved frame challenge (Codex, tier-1 cross-family)

**This is the most important open item and the thing the handoff chain lost.**
The cross-family critic was actually run against this very design and returned a
frame challenge the operator called *"equally useful"* and *"powerfully
precient"*. Verbatim:

> **FRAME CHALLENGE**
>
> The question should have been:
>
> "Where does the trust failure first enter the decision—objective retention,
> scope selection, evidence collection, inference, or presentation—and what is
> the smallest mechanism that detects it before the operator pays to review a
> conclusion?"
>
> The proposal assumes the important failure happens at the conclusion. **The
> stronger diagnosis is that it often happens earlier, when the primary agent
> decides what to inspect, what not to inspect, and which prior framing to
> preserve. A critic receiving "raw surfaces" selected by the primary is
> independent in inference but not in scope. It can rigorously validate the wrong
> slice of reality.**
>
> Against the Memento framing:
>
> - Stateless inference requires a persistent decision envelope: objective,
>   constraints, open questions, scope, exclusions, evidence plan, and state
>   transitions. An end-of-turn critic does not consolidate any of these.
> - Attention dilution is partially helped by a fresh context, but only if the
>   critic independently retrieves evidence. A fresh model reading a
>   primary-curated bundle inherits the primary's omissions.
> - Goal drift is best checked at investigation transitions: before tool
>   selection, after evidence collection, and before conclusion. A critic invoked
>   only after the conclusion is another retrospective audit.
>
> **The operator needs both scope challenge and conclusion challenge, but scope
> challenge comes first. The proposed system reverses that order.**
>
> gzkit's problem is not simply "too few gates" or "too many gates." **It has too
> many gates whose witnesses do not reliably discriminate the governed subject.**
> Adding another receipt-presence gate without strengthening subject binding is
> precisely the epicycle the operator is describing.

**The tension is live and deliberately unresolved.** The ruled trigger (the
convergence moment) is a *conclusion-time* trigger, and Codex's strongest finding
is that conclusion-time is the wrong place to look first. The operator ruled the
convergence-moment trigger anyway, on the ground that it is the one moment
reliably observable from outside the model. Whoever promotes this ADR must
resolve — not smooth over — whether a scope-time companion trigger is needed, and
if so, what observable event marks it.

### Premise checks the same critic returned against shipped code

The operator's assessment, verbatim: *"I could go on, if accurate and complete,
many of these premise checks are DAMNING"* and *"The first verdict confirms my
human intuition."*

> - FALSE — A green Step 4b audit proves that an independently executed
>   cross-family critic supplied the verdict. `src/gzkit/commands/obpi_complete.py`
>   decides "cross-vendor" through a caller-supplied adversary-name prefix. […]
>   The ledger event model […] has no prompt hash, scope manifest, primary-output
>   hash, provider receipt, or fallback reason.

> - FALSE — The documented Step 4b dispatch contract is currently mechanically
>   satisfiable as written. `.gzkit/skills/gz-obpi-pipeline/SKILL.md:689-693`
>   requires `SubagentDispatchRecord` fields […] The actual `SubagentDispatchRecord`
>   […] has none of those fields and forbids extras.

Both were subsequently discharged: the second by GHI #678 (`ffa1c6115`), the
first by GHI #765 (`cd4e14687`, which added `--adversary-receipt`, resolved by
the gate from the argv ARB actually executed). **The remaining unbuilt items from
that verdict are the prompt hash, scope manifest, and primary-output hash** —
none of which #765 supplies, and all of which bear directly on this ADR's own
critic, since the same "did it really run, on the real thing" question applies.

## Alternatives Considered

1. **Amend the 7 `Self-Escalation (opus-tier)` blocks (GHI #670's original
   deliverable).** Rejected: it fires on *skill invocation*, and the ruled trigger
   is the *convergence moment*. Those diverge — the session that authored this ADR
   reached convergence through no skill on that list. Also same-family by
   construction, which is the defect, not the fix.

2. **Extend `adversarial_validation` with a phase discriminator, reusing Step 4b.**
   Rejected by explicit operator ruling (*"we will NOT alter the OBPI process, at
   all"*). Attractive because the ledger event and tier ladder already exist —
   which is exactly why the boundary is recorded rather than left to judgment.

3. **Status quo: same-family opus self-escalation.** Rejected — the two share
   training priors and blind spots, so the subagent's pushback confirms shared
   antecedents. Step 4b already codified this one layer down (*"a Claude
   validating Claude shares failure modes"*); the design phase inherits it.

4. **Asynchronous or lag-by-one critic.** Rejected on measurement: round-trip is
   11.62–19.62s, well inside synchronous tolerance. Lag-by-one was designed
   against a withdrawn ~20x-high figure, and it breaks the stated trigger — a
   critique arriving one question late is not *"a 2nd opinion in that exact
   moment."*

5. **`permissionDecision: "deny"` rather than `updatedInput`.** Rejected as
   primary mechanism: denying *usurps* the question rather than accompanying it,
   contradicting *"a 2nd opinion, not a usurped opinion."* Retained as an open
   question — deny was never tested.

6. **Formal methods** (operator: *"Maybe formal methods?"*). Rejected as a general
   answer, kept as a narrow one. gzkit's failure is not code incorrectness — the
   validators pass and `gz check` is green. The failure is that a green witness
   does not observe its declared subject, which is a binding problem, not a proof
   problem. The tractable slice: *"this criterion must reference this chore's
   declared subject"* is formally checkable, and is exactly what Codex named as
   strong subject binding.

7. **Cherny's "let the tokens burn"** (operator: *"Maybe give in to Cherny's 'let
   the tokens burn eventual consistency with goals and loops'?"*). Rejected by the
   operator on lived experience, verbatim: *"NOT, ONCE."*

## Risks and Open Questions

1. **Alert fatigue is the strongest argument against this ADR**, raised by the
   critic and conceded by the operator (*"I am at a loss for a better alternative
   short of profound paradigm shifts"*):

   > Always-on review imposes at least one additional model execution and one
   > additional document for the operator to read on every detected
   > recommendation. That reduces operator typing but increases attention and
   > adjudication load. **Without measured precision, suppression, risk tiering,
   > and a concise escalation protocol, it is more likely to worsen exhaustion and
   > alert fatigue.**

   Both independent critic passes converged on **risk-tiered review** rather than
   either extreme. That convergence is the only thing both passes agreed on, and
   it is the strongest available signal for how to scope a pilot.

2. **Confidence measurement may be placebo.** Operator, verbatim: *"bizare,
   because an agent's ability to measure confidence is not established — is this
   placebo?"* — against the critic's finding:

   > This conflicts with existing operator-facing rules. `AGENTS.md:121-124`
   > requires asking the human below 90% confidence, surfacing assumptions, and
   > stopping on inconsistencies. **A fail-closed critic dependency can prevent the
   > very question those rules require. A plain-text question would also bypass an
   > AskUserQuestion-only gate.**

   Both halves are unresolved: a hook that blocks `AskUserQuestion` can suppress a
   canon-required question, and a hook scoped to `AskUserQuestion` is trivially
   evaded by asking in prose.

3. **The agent equivocates after presenting options**, which the critic must
   attack rather than mirror. Operator, verbatim: *"the option you always provide
   is 'discuss this' (approximating): the critic needs to engage your premise. You
   almost always equivocate and hedge in the narrative that follows. easly a
   discernible majority of the time."*

4. **`permissionDecision: "deny"` untested.** Only `updatedInput` was exercised;
   whether deny blocks cleanly or wedges the picker is unknown.

5. **Base rate to re-measure after any mechanism ships** — seed `20260807`, same
   five-class taxonomy. State the ceiling honestly: **68.3%** is the share of
   defect GHIs whose root cause is a design decision, an UPPER bound, since most
   such decisions were never surfaced as an `AskUserQuestion` at all. The tighter
   read is **23%** (explicit overconfident-premise signature in the GHI body).

6. **Epicycle-vs-convergence test**, offered so the operator can run it without
   trusting the agent's read: successive corrections landing on the same object at
   *different altitudes* (instance → instances → holder) is convergence; the *same
   altitude* with alternating conclusions is an epicycle. `#658 → #743 → today` is
   the former.

7. **Evidence not recoverable in text.** In session `d01f355f` the operator
   supplied a screenshot with the remark *"do you see this? this is exactly the
   mode that the work was designed to react to"* (image cached at
   `~/.claude/image-cache/d01f355f-362e-45ed-9ed8-4d30ad06d452/1.png`). The image
   is outside this document; the pointer is preserved so the referent is not lost.

## Notes

### Provenance

| Session | Slug | Role |
|---|---|---|
| `882dfc48-123b-4b9e-aaff-e2909cd4fe06` | second-opinion-crm-design | Origin. CRM framing, Memento diagnosis, Codex frame challenge. |
| `d01f355f-362e-45ed-9ed8-4d30ad06d452` | askuserquestion-convergence-hook-mechanics | Hook mechanics, `updatedInput` probe, injection shape. |
| `8e5c43b1-7bf5-423b-b4f4-599b1eee0840` | advised-steps-discharged-step4b-tier-binding | Step-4b tier binding (GHI #678); latency measurement. |

Superseded routing artifact: **GHI #670**, closed `superseded` against this ADR.
Sibling: **GHI #765** (Step-4b tier-1 corroboration) — distinct surface, same
lesson: prefer a runtime artifact over a self-assertion.

### Promotion plan

Pool ADRs carry no `semver:` or `kind:` frontmatter; promotion via
`gz adr promote` rewrites the frontmatter with the chosen taxonomy. Expected
shape: `feature` kind, `heavy` lane. Campaign placement is the **operator's
decision** (stated 2026-08-07: *"I'll decide its campaign placement"*).

Before OBPI decomposition, the promoting session must rule on the frame
challenge above — whether a scope-time trigger accompanies the conclusion-time
one — because that ruling changes the decomposition, not merely its ordering.
