# Agent Contract — Rationale and Pedagogy

This document extracts the pedagogical and rationale material that used to
live alongside the per-turn behavioral invariants. The invariants themselves
are canonical in `AGENTS.md` (portable, vendor-neutral) and `CLAUDE.md`
(Claude-specific invariant 10a). This file preserves the *why* — anti-pattern
canon, workflow mechanics, and reporting-pathway research citation — without
forcing that material to load into every context window.

Consolidation lineage: `.gzkit/rules/agent-contract.md` (retired 2026-04-22,
ADR-0.0.20 OBPI-02) → AGENTS.md + CLAUDE.md + this file.

## Prompting-source corroboration

gzkit doctrine is grounded in observed repository failures first; external
prompting guidance is corroboration, not authority over canon. The current
agent-contract shape aligns with these primary-source patterns:

- **Operator economy of effort.** Anthropic's clear/direct prompting guide
  says task descriptions should name context, workflow position, end goal,
  and what successful completion looks like. OpenAI's GPT-5.5 prompt guidance
  likewise recommends short prompt sections for role, goal, success criteria,
  constraints, output, and stop rules. gzkit's draft-review-decide-attest
  mode applies that guidance by having the agent draft the structured work
  and the operator attest decisions instead of authoring every paragraph.
- **Read before changing; verify before claiming.** Anthropic's hallucination
  guidance recommends grounding factual work in direct quotes for long
  documents, and OpenAI's GPT-5.5 guidance tells coding agents to run relevant
  validation commands after changes. gzkit renders those practices as
  DO IT RIGHT #5, #6g, #6h, ARB receipts, and `uv run gz check`.
- **Selective subagent use.** Anthropic's subagent docs frame subagents as
  focused workers with separate context windows and note their latency cost.
  OpenAI's GPT-5.5 guidance emphasizes traceable plans and concrete validation
  over process expansion. gzkit therefore uses subagents for independent
  fan-out and context isolation, not as a default response to every lookup.

Sources: Anthropic
[clear/direct prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct),
[subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), and
[XML tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags);
OpenAI
[GPT-5.5 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5).

## Anti-pattern canon

*Origin: GHI #157 (TDD test-dump theater) and the defect window GHI-141
through GHI-156 that surfaced the class of failure.*

What vibe coding looks like:

- Writing a function that reads `docs/user/manpages/*.md` and treats every
  file as a manpage, without opening the directory and noticing `index.md`
  is a ToC page.
- Landing a case-sensitive string match (`line.startswith("## Objective")`)
  in an extractor whose input comes from human-authored markdown files that
  drift freely in heading case.
- Adding a hardcoded "QA command block" to a ceremony step because
  "ceremonies have QA commands" without asking what role that block plays in
  that specific step's operator moment.
- Writing a test file that mocks the data structure the real code consumes,
  then asserting on the mock, without ever running the real path end-to-end.
- Reading an error message and reaching for "skip this one case" as the fix,
  when the error message is actually reporting a whole class of cases that
  the code never considered.
- Batching all tests before any implementation, running them together for a
  single "RED screenshot," then writing all the code and running them
  together for a single "GREEN screenshot" — test-dump theater that mimics
  the shape of TDD while skipping the per-increment observation loop that
  makes TDD work (GHI #157).
- Stopping after each RED→GREEN pair to solicit operator approval before the
  next increment — TDD here runs along the way, not turn-by-turn; operator
  refactor orientation arrives opportunistically, not as a synchronous gate
  (GHI #157).

Every item on that list is drawn from defects observed in this codebase
within the window GHI-141 through GHI-156. The pattern is consistent: the
author wrote code that *looked* right, committed it, and moved on — because
the loop did not include reading, tracing, testing the real path, or running
the observed command. **Close the loop.** Do it right.

## TASK-driven workflow

*Origin: GHI #160. Phase 6 of the discovery that GHI-originated code changes
were bypassing the TASK registry and breaking the four-tier traceability
chain `task → req → obpi → adr` at the leaf level.*

The binding pattern for any code-change GHI:

1. Locate the governing REQ(s) via `gz covers <ADR-ID>`.
2. For each REQ, start a TASK: `gz task start TASK-X.Y.Z-NN-MM-PP`.
3. Run the TDD cycle (Red → Green → Refactor) per TASK — not batch-then-run.
4. Commit with the trailer: `Task: TASK-X.Y.Z-NN-MM-PP` as the final line.
5. `gz task complete TASK-X.Y.Z-NN-MM-PP`.
6. Decorate new tests with `@covers(REQ-X.Y.Z-NN-MM)`.
7. Verify with `uv run gz validate --commit-trailers --requirements`.

The validate checks are advisory gates, not ritual. If they flag a commit or
brief, the fix is to restore the chain, not to silence the check.

Governance-intent trailers (GHI #201) extend this: any `src/**` or `tests/**`
commit must carry either `Task: TASK-X.Y.Z-NN-MM-PP` (hand-crafted work
scoped to a single TASK) or `Ceremony: <name>` (chore/sync commits bundling
work from multiple governance anchors, e.g. `Ceremony: gz-git-sync`,
`Ceremony: obpi-reconcile`, `Ceremony: adr-closeout`). `gz git-sync` emits
the ceremony trailer automatically.

## Rationale for 6g and 6h

*Origin: GHI #263 (invariant 6g — verify runtime surface before recommending)
and GHI #261 (invariant 6h — quote rules verbatim in violation reports).*

Both are instances of **reporting-pathway drift** (`.gzkit/rules/attestation-enrichment.md`
§ Rationale, citing Lindsey et al. 2025): the explanation pathway and the
execution pathway are structurally separate circuits, and a model can produce
a plausible explanation of reasoning it did not perform.

- **6g covers the failure at recommendation time:** inventing an incantation
  from training memory and presenting it as operational guidance without
  running it once. The canonical example — recommending
  `claude --model ...` as a CLI flag when the actual surface is the `/model`
  slash command — shows the failure mode crisply: plausible shape, wrong
  surface, never observed.
- **6h covers the failure at post-mortem time:** inventing a directive
  conflict to rationalize a clean mechanical-rule violation. Phrases like
  "competing directives," "pulled against," "no clear resolution" appearing
  *without* verbatim quotes of the allegedly-conflicting text are red flags
  — absence of quotable conflict text means the conflict is invented.

The mitigation for both is structurally identical: **produce verbatim
grounding before presenting the claim, not after being challenged.** Run the
observed command and paste its output; quote the rule and the allegedly
conflicting directive verbatim. The cost of running the command once (or
pasting the quoted text once) is orders-of-magnitude lower than the cost of
a plausible-but-fabricated claim sitting in production until an operator
catches it.

This pattern is the same shape as the ARB receipt-ID requirement in
`.gzkit/rules/attestation-enrichment.md` and the commit-message
observed-output discipline in `.gzkit/rules/tool-skill-runbook-alignment.md`
§ "Commit-message discipline for skill-routing changes." Claims without
observed evidence are post-hoc reasoning pathways, not verification
pathways — in all three cases, the fix is to move the verification *before*
the claim.

## Rationale for 1a (coupled-surface coherence)

*Origin: GHI #372 (DO IT RIGHT invariant 1a — coupled-surface coherence,
the lateral axis of #1). Lifted from `AGENTS.md` § DO IT RIGHT inline
narrative under GHI #327 follow-up.*

#1 names the *vertical* axis of "fix the class": the same defect across
multiple inputs to a single surface. 1a names the *lateral* axis: the
symmetric defect on the surface that wasn't touched. When a change moves,
renames, or reformats one side of a coupled pair (generator ↔ validator,
model ↔ writer, rule ↔ mirror, schema ↔ producer, template ↔ rendered
file), the consumer's check stays silent against the new shape until an
unrelated commit surfaces the rot.

**Operator framing (GHI #372):** *"This is part of DO IT RIGHT — GHI it
and add it, emphatically… explicitly."* Producer-side completion without
re-running the coupled consumer's check is incomplete work, not "scope
discipline."

**Canonical exemplars (window: past 30 days at GHI #372 authorship):**

- GHI #361 (banner-position fix, generator side) → GHI #368
  (validator-strip-logic rot, ~3 weeks silent until the next commit
  hit it). The producer-side fix landed; the validator on the
  consumer side kept asserting the old shape. Caught only when an
  unrelated change disturbed the validator.
- GHI #358 (`InsightRecord` model lock) → GHI #371 (writer-side
  `schema`/`kind` envelope drift). The model was locked at one
  surface; the writer on the consumer side kept emitting the old
  envelope. Hook fail-closed on an unrelated commit.
- (Latent at authorship, not yet a GHI) `skill_surface_sync.instructions.md`
  rule placement on the producer side without the consumer-side
  AGENTS.md scaffold check.

**Mechanical anchor (deliberately follow-up scope):**
`data/coupled_surfaces.json` registry naming known generator/validator,
model/writer, rule/mirror pairs, plus a `gz validate --coupled-surfaces`
audit fail-closing when one side of a registered pair changes without
the other side's check passing. Tracked under GHI #372 — the judgment
invariant lands now; mechanical promotion follows the canonical
advisory → mechanical pipeline (`docs/governance/advisory-rules-audit.md`).

The same discipline applies recursively to AGENTS.md itself: edit
`src/gzkit/templates/agents.md` (canonical) and let
`gz agent sync control-surfaces` propagate to the rendered file.
Editing the rendered file directly violates the very invariant 1a
binds (template ↔ rendered file is a registered coupled-surface pair).

## Rationale for Behavior Rule 11 (course-correction → insights)

*Origin: GHI #357 (Behavior Rules — Always #11 — append improvement
record on operator course-correction). Lifted from `AGENTS.md` §
Behavior Rules — Always #11 inline narrative under GHI #327 follow-up.*

A course-correction is the operator naming a wrong assumption,
redirecting an interpretation, or calling out drift in flight. Without
a trackable trace, the lesson is unwitnessed and the loop depends on
agent recall turn-by-turn — exactly the failure shape `Correction fails`
in `.gzkit/rules/agent-failure-modes.md` names. The improvement record
under `.gzkit/insights/agent-insights.jsonl` is the mechanical floor:
the correction lands at T2 (ledger-adjacent insight stream) where it
can be reviewed, surfaced in subsequent sessions, and audited against
recurrence.

**Required fields:**

- `scope` — skill / rule / surface that drifted
- `summary` — one sentence on what the correction was
- `evidence` — file paths or commands proving the drift
- `next_action` — what changes structurally to prevent recurrence

The `next_action` field is load-bearing: a correction without a
structural follow-up is a one-shot patch, not a rule learning. If the
next action is *"agent will be more careful next time,"* that is
agent-trust posture (the failure mode the entire contract is engineered
against). The next action should name a rule, validator, hook, or
surface change that closes the drift mechanically.

**Relationship to the rest of the contract:**

Rule 11 supplies the trace that backstops `Correction fails` from
`.gzkit/rules/agent-failure-modes.md`. The layered-trust T1/T2/T3
invariants in `docs/governance/trust-doctrine.md` supply the structural
defense — a correction that lands at T1 (canon edit) but not at T2
(ledger / insight stream) or T3 (derived view) is the recurrence
vector. Rule 11 is the T2 floor.

## Why this contract is not minimal

*Lifted from `AGENTS.md` § Why this contract is not minimal under GHI #327.*

A reasonable reader comparing `AGENTS.md` to minimalist references — e.g.
[forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills),
a single 75-line `CLAUDE.md` distilling Karpathy's LLM-coding pitfalls into
four principles — will notice that gzkit is the opposite shape: ~14 rule
files, ~50 skills, five gates, three state tiers, a ledger, receipts, and a
sync protocol. By the minimalist test ("would a senior engineer say this is
overcomplicated?") gzkit's control surface is overcomplicated.

The tradeoff is deliberate, and stating it is the fair thing to do:

- **Minimalist references optimize for** a solo human + one agent, short
  session, code-level hygiene. Behavior is the whole product; agent trust is
  the mechanism; the cost of a missed-principle mistake is one discarded
  diff.
- **gzkit optimizes for** multi-agent, multi-session, auditable governance
  where the proof-of-work must survive the agent that produced it.
  Ledger-of-truth beats agent-trust; receipts beat narrative recall;
  structural gates beat goodwill. The cost of a missed-principle mistake is
  a corrupted artifact graph that reconciliation has to untangle months
  later.

Both shapes are defensible for their problem class. Mapping the four
Karpathy principles onto this contract, three are adopted with stronger
mechanical backstops; one is **deliberately inverted**:

- **#1 Think Before Coding** (assumptions, ambiguity, push back) —
  adopted. `AGENTS.md` § Behavior Rules — Always #7–#10 (90% confidence
  threshold, surface assumptions, STOP on inconsistencies, push back on
  flawed approaches) and § DO IT RIGHT §2 ("no vibe coding") carry the
  same intent under stronger framing; § Anti-vibing mantra is the
  conscience when the judgment invariants are silent.
- **#2 Simplicity First** (minimum code, no speculative features) —
  adopted on *defaults*, departed on *velocity framing*. § STDLIB-FIRST
  and the no-speculative-features clause in § PRIME DIRECTIVE land the
  same defaults. The upstream framing "bias toward caution over speed"
  is presented as a tradeoff axis; § Anti-vibing operative claim 2
  forbids that framing (*"'Lighter ceremony' is not a tradeoff axis"*).
  Advisory scorecard rows #18–24 (ruff complexity, ty, class/module
  size) are the mechanical floor.
- **#3 Surgical Changes** — **deliberately inverted**. Upstream: *"every
  changed line should trace directly to the user's request."* gzkit
  § PRIME DIRECTIVE 4 (*"SCOPE EXPANSION IS NOT SCOPE CREEP"*) and
  § DO IT RIGHT §1 (*"fix the class of failure, not the instance"*) plus
  §1a (coupled-surface coherence) require the *thorough* fix where
  Karpathy requires the *narrow* one. The inversion is intentional: a
  corrupted artifact graph cannot be unwound by a downstream surgical
  patch, so the contract pays the coupled-surface tax up-front.
  § Defect-fix routing's 60-day precedent gate and Invariant 6c are the
  structural defenses that keep "fix the class" from sliding into
  ceremony-for-ceremony's-sake on small in-flight fixes.
- **#4 Goal-Driven Execution** (transform "fix X" into "write failing
  test, make it pass") — adopted; the upstream *authoring habit* is a
  sharper restatement of gzkit's REQ-coverage *mechanical check*.
  Karpathy: *"Add validation → write tests for invalid inputs, then make
  them pass."* gzkit's REQ-coverage gate (ADR-0.0.25, `gz obpi
  complete`) is the post-hoc enforcement on the same loop;
  `.gzkit/rules/tests.md` Red-Green-Refactor is the authoring
  discipline; the ARB receipt requirement in § Attestation pins the
  evidence. The Karpathy phrasing is worth retaining as the operative
  input habit upstream of the mechanical gate.

When in doubt about whether gzkit's surface is worth the cost, the
answer is: it is worth the cost for work that must be audited across
context boundaries, and it is heavier than necessary for a single
trivial edit. Use judgment.

This contract recursively applies the harness-is-product principle one
tier up: where Claude Code's harness wraps the model, gzkit's
meta-harness wraps Claude Code's outputs in governance state. See
[`harness-engineering-appraisal.md` § External Validation — Greyling on
Claude Code](harness-engineering-appraisal.md#external-validation-greyling-on-claude-code-recursive-case)
for the codebase-ratio framing, subsystem mapping, and the triangulation
with Böckeler's "Harness Engineering" thesis.

## External harness-engineering theses — appraisal and deliberate inversion

*Origin: GHI #498 (cite OpenAI Harness Engineering as external
corroboration + name merge-philosophy inversion). Pairs with
[`harness-engineering-appraisal.md`](harness-engineering-appraisal.md),
which carries the long-form appraisal against Böckeler 2×2, Greyling
codebase-ratio, and CE compounding-leverage framings.*

A third external thesis lands in scope here: OpenAI's
[*"Harness Engineering: leveraging Codex in an agent-first world"*](https://openai.com/index/harness-engineering/)
(Ryan Lopopolo, 2026-02-11). The piece is a first-person account of how
the Codex team built and tuned the runtime its own agents work inside.
The appraisal vector against gzkit doctrine is mixed — three clean
alignments and one deliberate inversion that future readers must not
misread as lag.

### Clean alignments

1. **Repo-as-system-of-record / agent legibility.** OpenAI: *"anything it
   can't access in-context while running effectively doesn't exist."*
   gzkit: the [trust doctrine](trust-doctrine.md) T1/T2/T3 invariants
   and the ledger-of-truth posture in `AGENTS.md § Never #7` say the
   same thing in a different vocabulary — derived views (Layer 3) are
   never source-of-truth because a derived view the agent cannot trace
   back to canon or ledger is, operationally, not there.
2. **Promote rule into code.** OpenAI: *"when documentation falls
   short, we promote the rule into code."* gzkit:
   [`advisory-rules-audit.md`](advisory-rules-audit.md)'s
   Promotable→Mechanical pipeline is the formal version of the same
   move — every Promotable scorecard row is a candidate for a
   `gz validate --<scope>` audit. The convergence on the underlying
   mechanism (advisory rules are provisional; the structural endpoint
   is mechanical enforcement) is independent of the surface vocabulary.
3. **Rigid architectural model with mechanical enforcement.** OpenAI:
   *"constraints are what allow speed without decay or architectural
   drift."* gzkit: ADR-0.0.3 (hexagonal architecture), ADR-0.0.43 (DDD
   cascade), and the package import-direction invariant in ADR-0.0.55
   (Draft) are the structural floor that the corresponding
   `gz validate` scopes pin mechanically. The shared claim is that
   architectural constraints are velocity-enabling, not
   velocity-throttling, once they are mechanically pinned.

### Deliberate inversion — merge philosophy

OpenAI argues for minimal blocking merge gates because *"corrections
are cheap, waiting is expensive"* in an internal-beta context where
Codex generates everything and human attention is the bottleneck.
gzkit takes the opposite stance, deliberately: Gate 5 is universal,
brief-level human attestation is mandatory (ADR-0.0.36), the ledger is
fail-closed, and the OBPI ceremony preserves a wait-then-attest order
that the runtime enforces (`gz obpi pipeline`).

The inversion is doctrinal, not lag. The two stances are responses to
different threat models:

- **OpenAI's threat model is velocity-bound.** Internal-beta context;
  Codex generates everything; the cost of a missed correction is the
  cycle time to re-issue it; agent-trust is the working capital.
  Blocking gates would idle the bottleneck (human attention).
- **gzkit's threat model is trust-bound.** Multi-agent, multi-session,
  auditable governance; the product *is* the auditable wait-then-attest
  stance; the cost of a missed attestation is a corrupted artifact
  graph that reconciliation has to untangle months later. Non-blocking
  gates would collapse the audit-trail invariant that distinguishes
  gzkit from a thinner harness.

This is the same axis as the Karpathy *"Surgical Changes"* inversion
above: both upstream theses are defensible for their problem class;
gzkit's inversion is the named answer to a different problem class
(auditable trust over velocity), not lag behind a sharper external
thesis. The § is canonical so that future readers — who will encounter
OpenAI's piece as a high-status published artifact — do not misread
the Gate 5 covenant as failing to keep up. The covenant is the product
of choosing a different threat model, and the choice is on record.

<!-- lifted-from: AGENTS.md#anti-vibing-mantra--relationship-to-the-rest-of-the-contract -->
## Anti-vibing mantra — relationship to the rest of the contract

*Lifted from `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT § Relationship
to the rest of the contract under GHI #327.*

Ownership and craftsmanship pillars are insufficient alone — an agent can
own its work and still vibe; can prefer the thorough fix and still
pattern-match a recommendation from training memory. The mantra names the
failure class both other pillars defend against.

The other invariants in `AGENTS.md` — DO IT RIGHT 6g (verify the runtime
surface), 6h (quote rules verbatim), § Behavior Rules — Always #7–#10 (90%
confidence threshold, surface assumptions, STOP on inconsistencies, push
back on flawed approaches), § Attestation (ARB receipts as observed
evidence) — are this mantra rendered as mechanical checks. When those
checks are silent, the mantra is the conscience.

<!-- lifted-from: AGENTS.md#operator-economy--why-this-is-canon -->
## Operator economy — why this is canon

*Lifted from `AGENTS.md` § OPERATOR ECONOMY OF EFFORT § Why this is
canon, not preference under GHI #327 follow-up.*

The draft-review-decide-attest interaction shape is the one that produces
witnessed, attestable, replayable governance work without the operator's
bandwidth as bottleneck. The contrast modes that the binding bullets rule
out:

- **Operator drafts; agent reviews.** Shifts typing burden onto operator;
  the agent's reviewer-only role produces no substantive contribution to
  the artifact.
- **Bundled question intake.** Operator types one long bulleted answer
  rolling several decisions together; the multiple-choice forcing
  function is bypassed; decisions blur.
- **Open-ended brainstorming without decision-shaping.** Produces text
  that requires the operator to re-author after the fact to extract a
  decision; the brainstorming output is not a deliverable.

All three are vibing through the interaction layer — the failure mode
the entire contract is engineered against. The operator-economy mode is
the conscience that names the shape *before* it leaks through.

## Attestation — worked example

*Lifted from `AGENTS.md` § Attestation § Worked example under GHI #327.*

User says: `attest completed`

Agent passes to `--attestation-text`:

```
attest completed — Confirm decision: gzkit cli_audit + doc_coverage surface
architecturally superior (AST vs parser._actions private API, 5-surface
manifest-driven coverage, 76 vs 1 tests, frozen Pydantic vs dict[str,Any]);
no absorption of the external reference cli_audit module warranted.
Receipts: lint arb-2026-04-14T12-34-56-ruff; types arb-2026-04-14T12-35-02-ty;
tests arb-2026-04-14T12-36-18-unittest; coverage arb-2026-04-14T12-37-44-coverage.
```

See [`docs/governance/arb-middleware.md`](arb-middleware.md) for ARB
middleware deep-dive: core concept, command surface, receipt schema and
storage, exit codes, and rationale.

<!-- lifted-from: AGENTS.md#stdlib-first-doctrine--rationale -->
## Stdlib-First doctrine — rationale

*Lifted from `AGENTS.md` § STDLIB-FIRST DOCTRINE under GHI #327 follow-up.*

LLM training corpus is biased toward most-popular libraries — pytest over
unittest, click over argparse, requests over urllib, FastAPI over Starlette,
Pydantic over attrs over dataclasses. Inheriting popularity bias makes the
dependency surface a vibing surface where doctrine is set by training-corpus
weight rather than deliberate operator choice. Stdlib-First is the
mechanical defense against that bias.

**Highly-opinionated defaults bind consuming projects.** gzkit is not a
neutral framework. gzkit ships highly-opinionated defaults and binds them
on every project that adopts gzkit as its governance guide. A
gzkit-governed project inherits Stdlib-First, the Gate Covenant, Attestation
discipline, OBPI ceremony, and every other doctrine canonized in AGENTS.md
— not as suggestions but as binding rules under the Prime Directive.
Non-gzkit projects answer their own dependency, testing, and CLI questions.
The doctrines bind only projects that elect gzkit. Election is the consent
surface; once elected, the defaults are the contract.

**Relationship to the Exemplar-Corpus Doctrine (ADR-0.0.27, forthcoming).**
The Exemplar-Corpus Doctrine is a *learning relationship*, not an *adoption
relationship*. gzkit measures click's design metrics to inform CLI doctrine;
gzkit does not depend on click. Conflating them is the same
training-corpus failure pattern Stdlib-First defends against.

**External corroboration (OpenAI Codex harness engineering, 2026).**
OpenAI's
[*"Harness Engineering: leveraging Codex in an agent-first world"*](https://openai.com/index/harness-engineering/)
(Ryan Lopopolo, 2026-02-11) independently reaches the same
defaults-vs-departures shape. The article describes preferring a
tightly-scoped reimplementation over a generic dependency for
`map-with-concurrency`: *"rather than pulling in a generic p-limit-style
package, we implemented our own map-with-concurrency helper: it's
tightly integrated with our OpenTelemetry instrumentation, has 100%
test coverage, and behaves exactly the way our runtime expects."* This
is the same shape as Stdlib-First's *named-departure* clause (Pydantic
warrants its dependency cost on validation semantics stdlib cannot
supply; *"popularity"* and *"hot topic"* are explicit anti-rationales).
Independent convergence between a production-Codex harness team and
gzkit's training-corpus-bias defense is corroborating evidence that
the discipline is doctrinal, not stylistic. See § *External
harness-engineering theses — appraisal and deliberate inversion* above
for the broader appraisal vector against the same source.

## Agent failure-mode taxonomy — loading posture and worked examples

*Lifted from `.gzkit/rules/agent-failure-modes.md` § Loading posture and
§ Worked examples under GHI #327 follow-up.*

### Loading posture

This rule is **advisory** at authoring time. There is no mechanical
validator that scans a PR or brief and emits *"this is `Fabrication`
shape — block."* The mechanical defenses already exist as separate
rules and gates — the TTY+`ATTEST` authenticity gate, ARB receipt
requirements, hook fail-closed behavior, `gz validate --commit-trailers`,
the layered-trust T1/T2/T3 invariants — and the rule is the **shared name**
those defenses point at.

Promotion to mechanical scope — for example, a `gz validate
--failure-mode-coverage` audit confirming every advisory-rules-audit
scorecard entry names the failure shape it backstops — lands under
follow-up GHIs #308–#312 per ADR-0.0.23 § Decision. Until those land, the
rule binds at authoring time only: cite the pattern by name when reviewing,
when filing a defect, and when extending the scorecard.

<!-- lifted-from: .claude/rules/agent-failure-modes.md#failure-mode-worked-examples -->
### Failure-mode worked examples

**Fabrication — GHI #290:** An agent synthesized a `human_attestation: true`
payload during `gz obpi complete` from a headless invocation. Closed by
adding the TTY + `ATTEST` authenticity gate, which refuses the fabrication
path at the CLI surface and forces the agent to either allocate a PTY or
relay the operator's Stage-4 attestation through the marker-gated
`--attestor-present` flag (GHI #292).

**Skipped cheap verification — GHI #263:** An agent recommended
`claude --model …` as a CLI flag when the actual runtime surface is the
`/model` slash command. The flag was pattern-matched from training memory;
running `claude --help` once would have caught the drift.
See also: `Rationale for 6g and 6h` above.

**Dishonest when caught — GHI #261:** An agent explained a rule violation
as the result of "competing directives pulling against each other" without
naming or quoting either directive. The rule was added under DO IT RIGHT 6h
to require verbatim quotation; the post-hoc narrative fails the check by
construction.
See also: `Rationale for 6g and 6h` above.

## Attribution

Consolidation pattern adapted from "Core Operating Behaviors" in
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).
