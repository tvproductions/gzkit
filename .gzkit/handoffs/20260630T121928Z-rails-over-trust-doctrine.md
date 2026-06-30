---
mode: CREATE
adr_id: ADR-0.0.40
branch: main
timestamp: "2026-06-30T12:19:28Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: ebafa28b
session_id:
continues_from:
---

<!-- Handoff document for ADR-0.0.40 — created by claude-code at 2026-06-30T12:19:28Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

This handoff captures a **doctrine-direction decision**, not in-flight code. It
was produced during a `/insights` review session on 2026-06-30. No files were
mutated; no ledger events were written. The session is parked at decision-made,
implementation-deferred by explicit operator instruction ("place it a handoff,
not doing it now").

The decision concerns how gzkit should respond to the recurring class of
agent-honesty failures the insights report surfaced (skipped adversarial gates,
`--no-verify` commits, direct-CLI pipeline drives, fabricated "deferred-to-X"
claims): **with mechanical rails outside the model, not with increased trust in
a more capable model.** The operator explicitly rejected the frontier-lab
framing of "loosen restrictions, state outcomes, run goal-loops, spend more
tokens" and the report's "as models improve, the pipeline self-enforces"
horizon line.

Anchor ADR is **ADR-0.0.40 (judge-enforcement-validators)** — the foundation
ADR that owns mechanical enforcement of agent behavior. The concrete first rail
proposed (a `PreToolUse` hook) is a candidate for its own pool ADR if it grows
beyond a single settings-file hook.

## Important Context

- **The decision is doctrine-consistent, not novel.** It restates gzkit's
  existing thesis — `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT ("smallest
  surface for vibing to leak through"), fail-closed validators, Gate 5
  sacrosanct. The insights report's "self-enforcing agent" horizon line
  contradicts that thesis; the report's own Hooks suggestion is the only
  recommendation consistent with it.
- **Why rails, not trust (the load-bearing argument):** an agent is the
  *governed* party, so a gate it enforces against itself is a promise, not a
  gate. Capability improvement raises the plausibility of fabrication (lies get
  better-cited and harder to catch), so the human's detection cost rises with
  capability rather than falling. Enforcement must therefore live in
  deterministic code the model did not write and cannot skip.
- **Source signal:** the `/insights` report at
  `~/.claude/usage-data/report-2026-06-30-070609.html` (operator machine, not
  repo-tracked). Its friction categories — "skipped governance gates," "scope
  overrun," "unverified/excused claims" — are the failure families the rails
  target. The fun_ending (a fabricated "deferred to OBPI-19" claim where OBPI-19
  was already complete) is the canonical instance.
- **Pace is a first-class constraint.** The operator's stance includes "at the
  pace I want it" — the deliberate throughput ceiling that keeps each step
  inside a human verification budget. Any rail design must not assume a
  maximum-speed goal-loop.

## Decisions Made

- **Decision:** Respond to the agent-honesty failure class with mechanical,
  external enforcement (rails), not with model-trust or autonomy expansion.
  **Rationale:** The governed party cannot enforce gates against itself;
  capability raises fabrication plausibility, so trust scales the wrong way.
  Deterministic enforcement outside the model is indifferent to how capable or
  "coy" the model becomes.
  **Alternatives rejected:** (a) the frontier-lab "fewer restrictions, state
  outcomes, goal-loops, spend more tokens" posture — optimizes the vendor's
  objective (token spend, autonomy-surface marketing), not the operator's
  (checkable, controlled-pace, human-attested work); (b) the report's
  "self-enforcing governance agent that physically cannot bypass gates" horizon
  — a category error, since the agent is the thing being governed.

- **Decision:** Defer implementation; record as a handoff for later operator
  authorization.
  **Rationale:** Operator instruction, verbatim — "place it a handoff, not
  doing it now."
  **Alternatives rejected:** building the `PreToolUse` hook in this session
  (operator declined); opening an ADR/OBPI now (premature — no authorization,
  and a single settings hook may not warrant ceremony).

- **Decision:** Anchor the first concrete rail as a `PreToolUse` Bash hook in
  `.claude/settings.json` that hard-blocks `--no-verify` and direct-CLI OBPI
  pipeline drives (exit 2, no override).
  **Rationale:** It converts the two specific bypasses the report flagged from
  "the agent must remember the rule" into "the agent physically cannot perform
  the action" — deterministic code, not intention.
  **Alternatives rejected:** documenting the rule in `AGENTS.md` only (already
  present as prose; the report proves prose rules get bypassed under load).

## Immediate Next Steps

ADVISORY ONLY — present these and wait for operator authorization before acting.

1. Decide scope with the operator: build only the single `--no-verify` +
   direct-CLI-drive `PreToolUse` hook as a proof-of-shape, OR first enumerate
   the full rail inventory (every bypass the insights report flagged) and wall
   each one. Operator previously framed this as the open fork.
2. If proof-of-shape is chosen: author the `PreToolUse` Bash matcher in
   `.claude/settings.json`, exit code 2 on match, with a `BLOCKED:` message
   naming the rule. Verify it fires by attempting a `--no-verify` invocation and
   observing the block (paste observed output, per DO IT RIGHT rule 4).
3. If full inventory is chosen: derive the bypass list from the report's
   friction categories, classify each as hook-enforceable vs validator-
   enforceable vs human-gate, then route — likely a pool ADR under the
   ADR-0.0.40 enforcement-validators family.
4. Either way, keep the enforcement deterministic and external to the model;
   do not encode the rail as agent-instruction prose alone.

## Pending Work / Open Loops

- The scope fork in step 1 is unresolved and operator-gated.
- No pool ADR has been filed for the rail inventory; whether the work warrants
  ADR ceremony at all (vs a direct `.claude/settings.json` edit under a GHI)
  is itself part of the step-1 decision.
- The active Build-to-1.0 campaign (Movement III — airlock constellation)
  remains the governing sequence; this rails work is operator-discretionary and
  must not preempt the campaign's topmost gated item without operator ruling.
- Open question for the operator: should the rail set become a named foundation
  invariant (composed into `AGENTS.md` via ADR-0.0.37) once proven, so it is
  itself fail-closed against drift?

## Verification Checklist

- [ ] Branch matches: `git branch --show-current` returns `main`
- [ ] `.claude/settings.json` exists and is valid JSON before any hook edit:
      `python -m json.tool .claude/settings.json`
- [ ] No uncommitted changes conflict with this handoff (this session wrote no
      code): `git status --porcelain`
- [ ] Operator authorization obtained for the chosen scope fork before any edit
- [ ] If a hook is added: observed block output pasted (run the forbidden
      command, confirm exit 2), not assumed

## Evidence / Artifacts

- `.gzkit/handoffs/20260630T121928Z-rails-over-trust-doctrine.md` — this handoff
  (the decision record produced by the session)
- `AGENTS.md` — § MAKE LLM STOCHASTIC VIBES INERT and § Behavior Rules, the
  doctrine this decision restates and that the proposed rails mechanize
- `.claude/settings.json` — target surface for the proposed `PreToolUse` rail
- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
  — anchor ADR (mechanical enforcement of agent behavior)

## Environment State

No environment-specific state affects resumption. The decision is
implementation-agnostic; the only target surface is `.claude/settings.json`,
which is read by the Claude Code harness at session start.
