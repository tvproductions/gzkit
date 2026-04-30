# Agent Contract — Rationale and Pedagogy

This document extracts the pedagogical and rationale material that used to
live alongside the per-turn behavioral invariants. The invariants themselves
are canonical in `AGENTS.md` (portable, vendor-neutral) and `CLAUDE.md`
(Claude-specific invariant 10a). This file preserves the *why* — anti-pattern
canon, workflow mechanics, and reporting-pathway research citation — without
forcing that material to load into every context window.

Consolidation lineage: `.gzkit/rules/agent-contract.md` (retired 2026-04-22,
ADR-0.0.20 OBPI-02) → AGENTS.md + CLAUDE.md + this file.

## Anti-pattern canon

*Origin: GHI #157 (TDD test-dump theater) and the defect window GHI-141
through GHI-156 that surfaced the class of failure.*

What vibe coding looks like:

- Writing a function that reads `docs/user/commands/*.md` and treats every
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

Both shapes are defensible for their problem class. The four Karpathy
principles (Think Before Coding, Simplicity First, Surgical Changes,
Goal-Driven Execution) are all present in this contract with stronger
mechanical backstops — see `AGENTS.md` § Behavior Rules (Judgment invariants
7–10) and § DO IT RIGHT (#6a–6h), `.gzkit/rules/tests.md` Red-Green-Refactor,
and the ARB receipt requirement in § Attestation. When in doubt about
whether gzkit's surface is worth the cost, the answer is: it is worth the
cost for work that must be audited across context boundaries, and it is
heavier than necessary for a single trivial edit. Use judgment.

## Anti-vibing mantra — relationship to the rest of the contract

*Lifted from `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT § Relationship
to the rest of the contract under GHI #327.*

The other invariants in `AGENTS.md` — DO IT RIGHT 6g (verify the runtime
surface), 6h (quote rules verbatim), § Behavior Rules — Always #7–#10 (90%
confidence threshold, surface assumptions, STOP on inconsistencies, push
back on flawed approaches), § Attestation (ARB receipts as observed
evidence) — are this mantra rendered as mechanical checks. When those
checks are silent, the mantra is the conscience.

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

## Attribution

Consolidation pattern adapted from "Core Operating Behaviors" in
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT).
