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
