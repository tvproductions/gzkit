---
id: ADR-pool.convergence-moment-cross-family-critic
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
promoted_to: ADR-0.36.0-convergence-moment-cross-family-critic
---

# ADR-pool.convergence-moment-cross-family-critic: CRM Second Opinion — Cross-Family Critic at the Convergence Moment
> Promoted to `ADR-0.36.0-convergence-moment-cross-family-critic` on 2026-08-09. This pool file is retained as historical intake context.


## Status

Superseded

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

## Decision (RULED BUT CONTESTED — read § Adversarial review before building)

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

## Operator rulings, 2026-08-07 — R1–R4 (these resolve the promotion blockers)

Made after reading the recovered verdicts. Each collapses a question this ADR had
recorded as open; three of them dissolve the dichotomy rather than picking a side.

### R1 — Scope AND conclusion. It was never a choice.

> **why is this a choice? we want the adversary to get full context. measure twice,
> cut once.**

The ADR had framed scope-challenge and conclusion-challenge as alternatives
because Codex framed them as an ordering problem (*"scope challenge comes first.
The proposed system reverses that order"*). The operator rejects the framing: the
critic receives **full context** and performs **both** challenges. "Measure twice,
cut once" is the CRM reading — a cross-check is not a cheaper substitute for
another cross-check.

This also completes the pre-emption begun by the earlier raw-surface ruling.
Codex's objection was that a critic fed a primary-curated bundle "is independent
in inference but not in scope." Full context plus independent raw-surface access
answers both halves. **What remains unresolved is not scope-vs-conclusion but
whether an additional *earlier* firing is warranted** — and R2 makes that cheap to
try rather than something to settle in advance.

### R2 — It is a SKILL with three invocation paths.

> **this is a skill but can be invoked by me, by agent, or at gate.**

This dissolves the gate-vs-skill conflict that both critics raised against the
operator's "every time" ruling. The critic is **one skill** with three doors:

| Door | Invoked by | Transport |
|---|---|---|
| Operator | `/second-opinion` | skill → `codex:codex-rescue` subagent |
| Agent | agent judges it warranted | skill → `codex:codex-rescue` subagent |
| Gate | `PreToolUse` on `AskUserQuestion` | hook → `codex-companion.mjs` CLI helper |

Consequences that retire recorded objections:

- **Pass 1's alternative A5** ("ship it as an operator-invoked skill, not a gate")
  is no longer an alternative — it is one of the three doors. Same for A7
  (measure before gating): the gate door can stay dark while the other two run.
- **The 0.57% coverage finding stops being disqualifying.** It measured the *gate*
  door only. The operator and agent doors have no such ceiling and reach the
  prose-delivered recommendations that make up the other 99.4%.
- **ADR-0.44.0's prohibition** on a fail-closed invariant living solely in a vendor
  hook is satisfied: the invariant lives in the skill; the hook is one adapter.
- **Movement C accretion** shrinks: one skill, and the hook becomes optional
  rather than the mechanism.

### R3 — Resolution is operator + main agent, on the Step 4b pattern.

> **operator and main agent work for resolution. obpi pipeline 4b already handles
> this well - observe it.**

Observed, in `src/gzkit/commands/obpi_complete.py`. Step 4b's existing transition
is exactly the "explicit verdict transition" Pass 2 said was missing — it already
exists one layer down:

> `:2170` — "A known refutation must never be handed to the operator **dressed as
> clean**."
>
> `:2196` — re-run with `--adversary-resolution '<what was fixed and how the
> adversary's own check was re-run>'`

The rule: a `refuted` verdict with no recorded resolution **blocks**, and the
resolution must state both *what was fixed* and *how the critic's own check was
re-run*. It is durable in the ledger, not a transcript.

**This answers Pass 2's sharpest finding against the design.** Its objection was
that verbatim passthrough "transfers adjudication back to an already exhausted
operator" without a mandatory state transition. The transition exists; it simply
was not carried up from 4b. Generalize the shape — do not invent one, and per the
standing boundary, do not alter 4b itself.

### R4 — Use the built-in Codex integration. Keep it simple.

> **we just want to run the most up-to-date codex. Anthropic offers a built-in
> feature to call a codex adversary, why not use that and keep it simple?**

Adopted. The installed plugin (`openai-codex/codex/1.0.6`) already supplies both
transports the three doors need — verified on disk:

- `agents/codex-rescue.md` — the `codex:codex-rescue` subagent, for the operator
  and agent doors.
- `scripts/codex-companion.mjs` — a CLI helper, for the gate door. **This retires
  the "must shell out by hand" constraint** that forced `type: "command"` reasoning
  earlier: the hook calls the plugin's own helper, not a raw binary.

**This is a ruling against Pass 2's port/adapter prescription for now**, and it is
consistent with the operator's standing posture (*"I need forward momentum, not
design niceties - they can come with the refactor"*). Pass 2's vendor-neutral
critic-provider port is **deferred, not adopted** — recorded in § Adversarial
review so the refactor has its design when platform stability arrives.

It also softens the outstanding residual: "most up-to-date codex" becomes whatever
the plugin resolves, rather than a hard-coded vendor-prefix list in the core. It
does not eliminate that residual — see § Risks item 8.

### R4 transport correction (measured 2026-08-09) — the ruling stands, its premise does not

**R4's ruling is unchanged: run the most up-to-date Codex, keep it simple. What is
corrected is the belief that the shipped plugin already supplies this transport.**
It does not. Measured while discharging § Promotion plan item 4, on plugin
`openai-codex/codex/1.0.6` with `codex-cli 0.147.0` present on PATH:

1. **The plugin's `adversarial-review` command reviews BRANCH DIFFS, not decisions.**
   Invoked against this repository it returned:

   ```
   # Codex Adversarial Review
   Target: branch diff against main
   Verdict: approve
   No branch diff against main was provided or present, so no substantive
   --help regression can be supported.
   ```

   Its subject is a code change. This ADR's subject is *a decision at a
   convergence moment*. They are different objects, and no configuration of the
   diff reviewer turns it into the other.

2. **The `codex:codex-rescue` subagent is a forwarder that fails silently by
   contract.** Its runtime skill states: *"Return the stdout of the `task` command
   exactly as-is. If the Bash call fails or Codex cannot be invoked, return
   nothing."* Two dispatches returned nothing; the second drifted into an
   unrelated filesystem search. The forwarder is also explicitly *"not an
   orchestrator"* and is forbidden from calling `adversarial-review` at all.

3. **What DID work is the plain CLI**, `codex exec --sandbox read-only`, driven
   from the main session with the prompt as stdin. That is what produced the
   re-run verdict recorded below.

**Consequences for this design, stated plainly:**

- The "just use the built-in" reading of R4 is not available. Some gzkit-owned
  surface must exist to carry a *decision* to the adversary and carry a verdict
  back, because the shipped plugin carries *diffs*. This is an argument FOR the
  skill R2 ruled, not against it.
- § Risks item 8's residual is larger than recorded: the gap is not only which
  binary the plugin resolves, it is that the plugin's adversarial surface has the
  wrong subject.
- **It weakens the strongest no-build argument.** That argument rests on "the
  installed plugin supplies both transports" and on A5 calling the manual path an
  "existence proof". The first half is now falsified by measurement. The manual
  path remains a genuine existence proof — but it is manual, which is the thing
  the operator asked to stop being.

Tracked at **GHI #786** so the transport question survives this ADR's own lifecycle.

### The transport that must exist, scoped (measured 2026-08-09, GHI #786)

**It composes entirely from surfaces that already ship. No new CLI verb, and none
may be scoped here** — a `gz` verb is a CLI-contract change, which AGENTS.md
§ Defect-fix routing sends through OBPI ceremony under a *promoted* ADR. This ADR
is `Pool`. Scoping a verb here would pre-empt the promotion this section exists to
inform.

Measured on `codex-cli 0.147.0`:

| Need | Surface | Evidence |
|---|---|---|
| Carry a **decision**, not a diff | `codex exec [PROMPT]` — *"If not provided as an argument (or if `-` is used), instructions are read from stdin"* | `codex exec --help`. Its subject is whatever the prompt carries. The diff-shaped path is the separate `codex exec review` subcommand, *"Run a code review against the current repository"* — the split is in the CLI itself. |
| Bound blast radius | `-s, --sandbox read-only` | `[possible values: read-only, workspace-write, danger-full-access]` |
| Return a **structured verdict**, not prose | `--output-schema <FILE>` — *"Path to a JSON Schema file describing the model's final response shape"*, plus `-o, --output-last-message <FILE>` | `codex exec --help` |
| **Prove** the adversary was cross-family | `uv run gz arb step --name <n> -- codex exec …` | The receipt records `step.command` as argv (`gzkit.arb.step_receipt.v1`), which is the channel GHI #780's resolver reads. Verified on a live receipt: `"step": {"command": ["uv","run","-m","unittest","-q"], "name": "unittest"}` |
| Operator / agent / gate doors | The **skill** R2 already ruled | No new surface |

**The ARB wrapper is not optional, and this is already ruled.** GHI #780 (closed)
established that a cross-vendor claim is `PROVEN (receipt) > DECLARED (tier) >
INFERRED (name)`, and the operator widened it: the requirement rides **any**
resolved cross-vendor claim, not only a declared tier 1. A critic verdict is a
cross-vendor claim. Invoking `codex` outside `gz arb step` therefore produces a
verdict that cannot be proven cross-family — the exact self-assertion #765/#780
closed. The wrapper is what makes the verdict *evidence* rather than narration.

**What this changes about the live objections.** The re-run verdict records
*"strong subject binding — prompt hash, scope manifest, primary-output hash — is
explicitly unbuilt."* `--output-schema` makes it buildable rather than aspirational:
those become required fields of the verdict schema, and a response missing them
fails the schema rather than being accepted as prose. That does not dissolve axis 3
(inverted coverage) or axis 4 (campaign accretion), which remain live.

**This is DEMONSTRATED, not scoped on paper.** The composition was run end to end
2026-08-09, which is § DO IT RIGHT 6g applied to the replacement rather than only
to the thing it replaces — the same discipline whose absence produced R4's
original error:

```
$ uv run gz arb step --name adversaryprobe -- \
    codex exec --sandbox read-only "Reply with exactly the token PROBE-OK and nothing else."
REAL EXIT: 0
arb-step-adversaryprobe-45bc3c72076246ec92e05d9b60d7fdbd

$ # reading that receipt back through the production resolver:
step.command: ['codex', 'exec', '--sandbox', 'read-only', 'Reply with exactly the token PROBE-OK...']
exit_status : 0
PROVEN cross-vendor from argv: True
stdout_tail : 'PROBE-OK\n'
```

The verdict came back, and `_receipt_proves_cross_vendor` resolved it **PROVEN**
from the argv — not DECLARED from a tier, not INFERRED from a name.

**One constraint the probe surfaced, recorded so the promoting session does not
rediscover it:** ARB step names must match `[a-z][a-z0-9]*` — no hyphens,
underscores, or leading digit — because the run_id binds against the canonical
receipt regex `arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}`. `--name
adversary-transport-probe` is refused at exit 2. The critic's step name must
therefore be a bare token such as `adversary`.

**What is still owed, and is NOT scoped here.** The verdict JSON Schema's own
fields; where it lives (`src/gzkit/schemas/` by convention); whether the skill
emits a ledger event; and the calibrated pilot the campaign's staged-delivery
amendment requires before the automatic `AskUserQuestion` door is lit. Those are
OBPI-shaped and belong to the promoted ADR's decomposition — item (i) of
§ Promotion plan, decomposed against the THREE DOORS.

## Adversarial review: TWO independent cross-family passes, BOTH returned PERFORATED

**This is the single most important fact about this design, and the handoff chain
lost nearly all of it.** The proposed mechanism was submitted to two independent
tier-1 (Codex) critics. Both returned **PERFORATED**. The need was affirmed both
times; the mechanism was refuted both times, on largely non-overlapping grounds.

Nothing below invalidates the § Intent — the operator's need is real,
operator-attested, and independently confirmed. What is contested is the
**mechanism**, and a promoting session that reads only § Decision without this
section will rebuild something two critics already broke.

> **Pass 2 verdict, verbatim:** "PERFORATED. The need for fresh, cross-family
> criticism is real. The proposed always-on implementation is not strong."

> **Pass 1 verdict, verbatim:** "PERFORATED. The need is real, operator-attested,
> and already booked — but the mechanism fails on four independent axes, any one
> of which is disqualifying."

### Pass 1 — the four disqualifying axes

1. **It duplicates shipped machinery.** Step 4b is already a fail-closed
   independent-adversary gate with a ledger event, a Layer-1 evidence section, a
   repo-wide re-audit, and a 225-entry shrink-ratchet. The proposal re-invented
   its verdict shape and minted parallel event types.

2. **Its critic was the tier gzkit's own doctrine forbids.** The proposal's critic
   was a fresh *Claude* subagent — *"precisely the correlated second draw #670
   exists to reject"* — which `SKILL.md:686` and `obpi_complete.py` treat as a
   Step-4b **bypass** absent checked Codex unavailability.

3. **Its coverage is inverted — and this is measured.** Verbatim:

   > 239 `AskUserQuestion` calls against **41,624** assistant turns over **160**
   > transcripts — ≈1.5 per session, **0.57%** of turns. The overwhelming majority
   > of recommendations reach the operator as prose. Trigger A gates the rare
   > case; Trigger B (the weak one) carries the actual load.

   **The convergence-moment trigger covers 0.57% of turns.** This is the hardest
   number in the entire corpus and it bears directly on whether the mechanism
   earns its surface. It was never carried into any handoff.

4. **It runs against the governing campaign.** Movement C's reduction deferral was
   lifted and *"the accretion is reduced"* is a named 1.0 gate. The critic
   measured the validate surface at **97 flags** against the campaign's recorded
   92 — *"that surface has grown by 5 while the mandate says shrink."*

   > *"gzkit has no external forcing function, and its only consumer is its own
   > construction. Self-inspection of a self-governing system is unbounded —
   > every governance surface is a new surface needing governance, and every audit
   > pass finds real defects, which is what makes the loop seductive rather than
   > obviously wasteful."*

Pass 1 also named the **re-adjudication** charge directly: the proposal re-derived
GHI #670 — an open, operator-authored ruling — in a weaker form, which is
*"Movement D, 'Stop the re-adjudication' … the named disease, and it fired
again."*

### Pass 1 — the cost evidence from the named comparable

The strongest empirical finding, quoted from gzkit's own source
(`handoff_resume_gate.py`): *"**Four times now this allowlist has been wrong**,
and every time the root was the same"* — four documented misses plus a pre-empted
fifth, across GHIs #574, #692, #697, #709, #732, #755, #756, #757, #758. And the
sentence the critic said should govern this decision:

> *"A gate that forbids the verification its own skill mandates cannot be complied
> with, and **an un-compliable gate gets worked around — the failure mode gzkit
> exists to close.**"*

**This session supplied live corroboration.** The resume gate refused four
compound read-only commands during the handoff review that opened this very
session — the fifth instance of exactly the profile the critic warned about.

### Pass 2 — the missing policy, which attacks the ruled passthrough directly

> The proposal also omits the policy that matters after the verdict. **If the
> critic returns PERFORATED, must the primary produce a new scope map, collect new
> evidence, or merely show the operator the criticism? Without a mandatory state
> transition, verbatim presentation transfers adjudication back to an already
> exhausted operator.**

This lands squarely on the ruled design. `updatedInput` passthrough was chosen
precisely so the verdict reaches the operator unedited — but unedited
presentation *without a required state transition* converts the critic into more
reading for the person the ADR exists to protect. **Unresolved.**

Pass 2 also enumerated the five ways critic and primary agree for the wrong
reason, which no amount of vendor separation fixes:

> - The primary-selected evidence boundary.
> - An omitted file or alternative.
> - The same repository doctrine and terminology.
> - A test or validator that observes the wrong subject.
> - The premise that another gate is the appropriate solution.

### Pass 2 — binding constraints the ruled mechanism violates

| Finding | Consequence |
|---|---|
| `AskUserQuestion` is broader than recommendation delivery — it also carries plan-mode requirements, interviews, attestation, and brief amendments | Trigger A "would interpose the critic before required *clarification*, not merely before recommendations" |
| `AGENTS.md:121-124` requires asking the human below 90% confidence | "A fail-closed critic dependency can **prevent the very question those rules require**. A plain-text question would also bypass an AskUserQuestion-only gate." |
| The `Stop` hook is **fail-open by contract** and yields immediately when `stop_hook_active` is set | It "can request one correction; it cannot guarantee that a critic ran" — so the fallback trigger cannot enforce either |
| **ADR-0.44.0 forbids placing a fail-closed invariant solely in a vendor hook** | A Claude-hook-only critic violates a standing boundary invariant. `.codex/hooks.json` carries only `SessionStart`/`UserPromptSubmit` — no `PreToolUse` or `Stop` equivalent |
| Hook behavior inside critic subagents is **UNVERIFIED** | "recommendation-shaped critic output risks **recursively triggering the critic gate**; if critics are exempted, that exemption becomes a bypass surface" |

### Pass 2 — the vendor-lock answer the operator asked for

The operator's stated fear was that this work *"casts definitve doubt on the
'multi-agent' premise of gzkit."* Pass 2 answered it directly, and the answer is
more optimistic than the fear:

> A cross-family critic requirement creates **supplier dependence. It does not
> inherently require vendor lock-in.**

> **"Decoupling versus determinism" is mostly a false dilemma.** Determinism comes
> from a stable contract, explicit state transitions, hashes, provenance,
> replayable evidence, and deterministic validation. The critic's judgment remains
> probabilistic regardless of vendor. **Ports and adapters increase determinism by
> preventing vendor transport details from becoming the invariant.**

The prescribed vendor-neutral contract:

- A **decision-review request**: the operator's exact question, objective, scope
  manifest, evidence references, primary draft hash, risk classification.
- A **critic-provider port** returning a typed verdict, premise findings, scope
  omissions, alternatives, provider identity, model family, and invocation
  receipt.
- Per-harness adapters (Claude, Codex, Gemini, Copilot, local) implementing
  whatever interception each supports.
- A **capability matrix** distinguishing automatic interception, explicit
  invocation, asynchronous review, and unavailable/degraded operation.

> **The core must not equate "cross-family" with the literal string `codex`.** It
> should require demonstrably distinct model-family provenance when that tier is
> mandated.

> The founding multi-agent premise is **not existentially disproven. It is,
> however, aspirational and incomplete today.** … The premise becomes genuinely
> untenable only if gzkit continues claiming identical fail-closed semantics on
> harnesses that lack the necessary interception capabilities. **Honest semantic
> capability levels are viable; fictional parity is not.**

> **Note against today's work.** GHI #765 (`cd4e14687`) discharged the
> *provenance* half of this — the tier is now proven from the argv ARB executed,
> not from an asserted name. It did **not** discharge the *literal-string* half:
> `_CROSS_VENDOR_ADVERSARY_PREFIXES` still hard-codes vendor names in the core,
> exactly what this finding forbids. That residual is unfiled.

### Pass 2 — the honesty caveat on the cross-family premise itself

The critic undercut its own family advantage, and this must not be lost:

> The correlated-draw concern is real, but "same family" and "independent" are not
> binary states. … **I cannot honestly claim that any finding here is structurally
> unavailable to Claude.** A sufficiently skeptical Claude critic with repository
> access could have found every item above. If the prior Claude review missed
> them, that is an **empirical miss, not proof of a family-level incapacity.**

> The cross-family benefit here is not magical independence. It is **a lower
> probability of sharing the primary agent's gate-shaped solution prior.** The
> proposal appears anchored in a Claude/gzkit habit: **when trust is weak, add a
> hook, event, and validator. The repository evidence says that habit itself now
> requires criticism.**

### Pass 2 — the narrower conclusion it recommends instead

> The appropriate conclusion is narrower: **retain cross-family review for
> consequential decisions, move the first independent challenge to scope-setting,
> and fix evidence provenance in the existing adversary mechanism before creating
> another universal gate.**

Note that the first clause is the operator's own stated session goal, verbatim.

## The frame challenge (Pass 2, quoted in full)

The operator called this *"powerfully precient"* and *"equally useful"*. Verbatim:

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

## Alternatives the critics offered (NOT yet adjudicated)

These came from the two perforating passes. **None has been ruled on.** They are
recorded verbatim-in-substance because they are the constructive half of a
PERFORATED verdict, and losing them was the costliest part of the dilution.

### Structural alternatives to the gate

| # | Alternative | Why it was offered |
|---|---|---|
| A1 | **Scope-first review** — before investigation, give the critic the operator's exact question and repo access; require an independent scope map, likely-omitted surfaces, and the question that should be answered. **Do not give it the primary synthesis.** | The only variant that breaks correlated draw at its source |
| A2 | **Emit the negative space** — require the primary to publish, with every recommendation, *the surfaces it chose not to read* and *the options it considered and dropped*; hand the critic that list plus the operator's raw question | "the critic's reading list is no longer the primary agent's reading list" — directly answers *"the meander of an accreting context window"* |
| A3 | **Persistent decision envelope** — carry target, constraints, assumptions, investigated surfaces, exclusions, open questions, and evidence plan across tool transitions | Addresses the Memento mechanisms structurally rather than at one moment |
| A4 | **Risk-tiered criticism** — mandate cross-family review for architecture, external contracts, irreversible operations, high-cost recommendations, explicit operator requests, and contradictions; **sample** routine decisions | The one thing BOTH passes independently converged on |
| A5 | **Operator-invoked skill (`/second-opinion`), not a gate** | Zero fail-closed surface, zero allowlist-erosion risk, operator controls when latency is paid. "**This session is the existence proof that the manual path works**" |
| A6 | **Generalize Step 4b into a vendor-neutral decision-review port** — do not mint a parallel event family until existing provenance defects are fixed | Reuses schema, audit, ratchet, and `gz validate --adversarial-validation` for free |
| A7 | **Measure before gating** — telemetry-only for N sessions | "there is **no base rate** for how often the primary agent's recommendations are actually wrong — the proposal spends a fail-closed surface on an unquantified harm" |
| A8 | **Widen the airlock instead of building beside it** — Movement B's *"Session entry triggers the airlock"* is open and operator-ruled; a recommendation is a transit | Closes a campaign item instead of opening a surface. NOTE: conflicts with the operator's *"we are not trying to make Airlock JR"* — the tension is unresolved |

### Mechanism-hardening alternatives (apply to whatever is built)

- **Strong subject binding** — bind every verdict to a decision ID, exact
  operator-question hash, objective/scope-manifest hash, primary-output hash,
  critic prompt version, provider/model family, invocation receipt, and
  timestamps. **Reject stale or replayed verdicts.**
- **Deterministic checks first** — campaign alignment, prior-decision lookup,
  contradiction detection, scope-to-evidence coverage, and validator-subject
  correspondence should run *before* spending a probabilistic critic call.
- **Explicit verdict transitions** — `CONFIRMED` may proceed; `PERFORATED` **must
  produce a revised scope or conclusion**; `INSUFFICIENT` must identify missing
  evidence and **cannot be represented as approval**. Operator override should be
  explicit and durable. *(This is the missing policy named above.)*
- **Calibrated pilot** — review a bounded sample and measure unique actionable
  findings, wrong agreements, false blocks, latency, operator reading time, and
  decisions changed. A universal fail-closed gate should follow evidence that the
  mechanism earns its surface area.

### The airlock conflict, stated plainly

Pass 1: the airlock is *"diagnostic-only … never a hard block — it always exits
0"* and *"never writes L1 canon"*, whereas the proposal is a hard block —
**"CONFLICTS on role, DUPLICATES on trigger."** Movement B's open
*"Session entry triggers the airlock"* item claims the same trigger real-estate.
Two mechanisms competing for the session door is how the 23-`airlock_in`
vs 10-`airlock_out` accounting gap happened. The operator's *"not Airlock JR"*
ruling and this finding are in direct tension and must be reconciled at promotion.

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

4a. **One critic or several, and how are several combined?** Operator, verbatim
   and explicitly undecided: *"I think we want both? or, do we want a
   composite/median/mean? I don't know if we can even alter the persentation"*.
   Unresolved on all three axes — how many critics, what aggregation (union /
   composite / median / mean), and how much of the presentation is mutable. The
   probe answered only the last in part: `updatedInput` renders, and the option
   cap is 4.

4b. **Two questions the operator returned to the agent unanswered**, preserved
   because they mark where the design was still open when the session ended.
   Verbatim: *"1. I don't know, are you asking me my design intent oor current
   behavior?"* and *"2. explain. do you mean the 2nd opinion agent's role in
   posing the question? or, does the question get posed after 2nd opinion
   modification?"* The second was subsequently settled — the question is posed
   *carrying* the critic's verdict, unedited — but the first was never resolved
   and should be re-asked at promotion.

4c. **The named blocker at session end**, verbatim: *"we need to allow the critic
   to operate, so that needs resolution."* Latency and transport were measured
   afterward; whether that fully discharges this is the promoting session's call.

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

7. **The operator's exhibit — recovered and transcribed.** In session `d01f355f`
   the operator supplied a screenshot with the remark *"do you see this? **this is
   exactly the mode that the work was designed to react to.** the whole reason for
   the '2nd opinion' is right there, we must discover its mechanics and work
   within those mechanics."* The image cache has since been cleared, but the PNG
   survives base64-embedded in the transcript and was recovered. It is an
   `AskUserQuestion` picker — the design's own subject, recursively, since it was
   asking the operator to rule *on the second-opinion handoff itself*:

   ```
   □ Ruling
   The resume gate is armed on the second-opinion handoff. How do you rule?
     1. Proceed — supersede with corrected handoff
     2. Proceed — file the Step 4b GHI now
     3. Proceed — rule on next-step 1 first
          Take up the ordering question the handoff calls the blocker:
          scope-challenge before conclusion-challenge (Codex) vs. the
          convergence moment (your stated trigger). Everything else waits.
     4. Hold
     5. Type something.
     ─────────────────────────
     6. Chat about this
   ```

   Three things it establishes that no prose in the chain preserved. **(a)** It is
   the `[choices|direct entry|discuss]` triple made concrete: 1–4 are
   agent-authored options, 5 is direct entry, 6 is discuss — the exact affordance
   the operator named as the trigger signature. **(b)** The agent-authored cap is
   visibly 4; 5 and 6 are harness-supplied. **(c)** Option 3 shows the
   scope-vs-conclusion tension *was* surfaced to the operator as a choice — and
   the operator's next message was the equivocation complaint (*"the option you
   always provide is 'discuss this' … You almost always equivocate and hedge"*),
   which is the behavior the critic is meant to attack.

   Recovery note: the cache directory is gone and the transcript itself expires
   ~2026-09-05, so the durable copy is now
   `appendices/A4-operator-exhibit-askuserquestion-picker.png` in this package. It
   was decoded from the `image` content block of
   `d01f355f-362e-45ed-9ed8-4d30ad06d452.jsonl`, not recovered from the file
   system.

8. **Residual: `_CROSS_VENDOR_ADVERSARY_PREFIXES` hard-codes vendor names in the
   core.** Pass 2: *"The core must not equate 'cross-family' with the literal
   string `codex`. It should require demonstrably distinct model-family
   provenance."* GHI #765 (`cd4e14687`) discharged the *provenance* half — the tier
   is proven from the argv ARB executed rather than an asserted name — but not the
   *literal-string* half.

   **Stated precisely, the sharper gap is not the hard-coding.** The receipt proves
   **which binary ran, not which model family answered**. The chain is argv →
   binary → *assumed* vendor → *assumed* model family; #765 hardened the first link
   and left the last two. A `--model` flag appears in argv and is therefore
   captured, but a model set in `~/.codex/config` never appears at all.

   **Not filed, by deliberate choice.** For all realistic current usage the `codex`
   binary means an OpenAI model, so the shipped surface substantially fulfils its
   declared intent; the gap is prospective, not observed. Filing it now would be
   the reflexive-GHI pattern the operator's moratorium targets, and the proper fix
   is the vendor-neutral port that **R4 explicitly deferred**. It becomes real when
   a second vendor is genuinely added or the refactor is undertaken.

   **Cheap tightening available without touching the classifier:** require the
   Step-4b adversary invocation to name the model in argv — e.g.
   `codex exec --model <model>` — so the receipt records the model, not merely the
   binary. Skill text only, no code, and it does not pre-judge the port design.

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

## Proposed OBPI Decomposition

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | critic-skill-contract | The `second-opinion` skill as one unit — both mandatory questions (scope challenge and conclusion challenge), a full-context read of the raw surface, and a schema-pinned verdict shape | Heavy |
| 02 | cross-family-transport | The composed ARB-wrapped `codex exec --sandbox read-only` transport carrying a decision, returning a schema-pinned verdict, with the cross-vendor property proven from the receipt's `step.command` argv | Heavy |
| 03 | operator-door | The operator-invoked door: the `second-opinion` slash command, callable on any decision at any moment | Heavy |
| 04 | agent-door | The agent-invoked door, fired on the A4 tier rules and never on the agent's own unvalidated confidence | Heavy |
| 05 | decision-envelope | A3 narrowed to one decision-scoped envelope carrying prompt hash, scope manifest and primary-output hash — the strong subject binding both adversary passes recorded as unbuilt | Heavy |
| 06 | risk-tiering | A4 narrowed — mandatory for the enumerated consequential categories and explicit operator requests, sampling the routine | Heavy |
| 07 | verdict-resolution-transition | Step 4b's resolution shape generalized without touching 4b — a refuted verdict with no recorded resolution blocks, and the resolution names what was fixed and how the critic's check was re-run | Heavy |
| 08 | pilot-instrumentation | The calibrated pilot measuring false blocks, latency, operator reading time, and decisions changed | Heavy |
| 09 | asked-question-gate-dark | The `PreToolUse` adapter on `AskUserQuestion` — wired, tested, and off by default, lit only by OBPI-08's measured result | Heavy |

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
