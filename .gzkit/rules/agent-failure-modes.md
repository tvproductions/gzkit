---
id: agent-failure-modes
paths:
  - "AGENTS.md"
  - ".gzkit/rules/**"
  - "docs/governance/**"
description: Six-pattern agent-failure-mode taxonomy (Opus 4.7 § 2.3.6 / GPT-5.5 § 9.2) with gzkit-invariant backstops.
---

<!-- rule-version: 0.2.0 -->

# Agent Failure-Mode Taxonomy (gzkit)

> **Rule version:** `0.2.0` — lifted worked examples and loading posture to
> `docs/governance/agent-contract-rationale.md` under GHI #327 follow-up;
> consolidated repeated citation lines to a single source note. Prior `0.1.0`
> authored under OBPI-0.0.23-01.

The six patterns below are drawn from the **Claude Opus 4.7 System Card**
(Anthropic, 2026-04-16, § 2.3.6) and corroborated by the **GPT-5.5 System
Card** (OpenAI, 2026-04-23, § 9.2 Apollo evaluations) — cited as **[1]**
throughout. Both frontier-lab cards converge on the same taxonomy of agentic
failure shapes, and gzkit's DO IT RIGHT invariants, ARB receipt discipline,
attestation gates, and trust-doctrine layering are the mechanical backstops
engineered against them. The vocabulary is for **shared reviewer / auditor /
rule-author naming** — when a flagged change matches one of these shapes,
name the shape so the conversation routes to the correct backstop instead of
re-deriving the failure motivation each time.

The patterns are listed in the prescribed order from Opus 4.7 § 2.3.6.

## Safeguard circumvention

**Definition:** The agent works around a guardrail (hook, validator,
permission gate, fail-closed check) instead of producing the evidence the
guardrail is asking for, treating the block as an obstacle to remove
rather than a signal to diagnose.

**External citation:** [1]

**Backstop:** `AGENTS.md` § Behavior Rules — Never #6 (*"Do not work
around hook blocks. A blocking hook signals missing evidence or inactive
pipeline state. Diagnose; never hand-write marker files or ledger
entries."*) and the ARB receipt requirement (`AGENTS.md` § Attestation),
which converts *"the agent claims X"* into *"X is observable, dated,
signed, replayable."* The hook block, the canonical-step-command lock in
`CANONICAL_STEP_COMMANDS`, and the fail-closed authenticity gate at
`_enforce_human_attestation_authenticity` are all engineered to make the
circumvention surface costlier than producing the evidence.

## Reckless action

**Definition:** The agent takes a hard-to-reverse or shared-state-
modifying action (force push, destructive reset, branch deletion,
schema change, message send) without first confirming the action is
authorized for this scope and at this moment.

**External citation:** [1]

**Backstop:** `AGENTS.md` § DO IT RIGHT 6a (*"Fix the class of failure,
not the instance"*) — recklessness is the class shape that emerges when
the agent treats one action's reversibility as a per-instance judgment
instead of routing through the explicit-confirmation policy. The
project-level *"Executing actions with care"* contract (system prompt)
and the brief-boundary anti-pattern (`AGENTS.md` § Behavior Rules —
Never #5) are the two surfaces that mechanize the same discipline.

## Fabrication

**Definition:** The agent emits a claim, receipt, ledger event, or
attestation payload whose content was synthesized by the agent itself
rather than observed from a primary source — a fabricated receipt ID, a
hallucinated test result, a `human_attestation: true` payload produced
without the operator typing the confirmation word.

**External citation:** [1]

**Backstop:** ARB receipts (`AGENTS.md` § Attestation — *"Receipt IDs
inline … Citing agent must verify receipt exists and status matches the
claim — fabricating a receipt ID is the same failure as fabricating the
claim."*) and the TTY + `ATTEST` confirmation gate at
`_enforce_human_attestation_authenticity` (`src/gzkit/commands/adr_audit.py`).
The gate refuses to emit `human_attestation: true` from a non-TTY parent;
agent-relayed attestation requires the `--attestor-present` co-presence
proxy (`attestation_type: "agent-relayed-operator-attestation"`) tied to
an active pipeline marker.

> Worked example: see [`docs/governance/agent-contract-rationale.md` § Failure-mode worked examples](docs/governance/agent-contract-rationale.md#failure-mode-worked-examples).

## Skipped cheap verification

**Definition:** The agent recommends an incantation, cites a CLI flag,
or asserts a runtime behavior pattern-matched from training memory
without running the actual command and observing its output — the
cheap verification step that would have falsified the claim was
skipped because it felt unnecessary.

**External citation:** [1]

**Backstop:** `AGENTS.md` § DO IT RIGHT 6g (*"verify the runtime surface
before recommending an incantation. Pattern-matching from training memory
is vibe-coding's recommendation-time face. Run, observe, paste,
recommend"*) and DO IT RIGHT #4 (*"Verify observed behavior, not assumed
behavior. Run the destination command, paste actual output."*). The ARB
receipt requirement enforces the same discipline at attestation time —
narrative substitutes are not acceptable on the heavy lane.

> Worked example: see [`docs/governance/agent-contract-rationale.md` § Failure-mode worked examples](docs/governance/agent-contract-rationale.md#failure-mode-worked-examples).

## Correction fails

**Definition:** The agent receives a correction in flight (operator
redirects an interpretation, names a wrong assumption, or calls out
drift) and either fails to internalize it (same drift recurs in the
next turn or next session) or applies it superficially (renames the
symptom while the underlying pathway persists).

**External citation:** [1]

**Backstop:** `AGENTS.md` § Behavior Rules — Always #11 (*"When the
operator course-corrects in flight, append an `improvement` record to
`.gzkit/insights/agent-insights.jsonl` before completing the corrected
work."*) — the trackable trace of the correction is the mechanical floor
that prevents the lesson from depending on agent recall turn-by-turn.
The layered-trust T1/T2/T3 invariants in `docs/governance/trust-doctrine.md`
supply the structural defense: a correction that lands at T1 (canon) but
not at T2 (ledger) or T3 (derived view) is the recurrence vector.

## Dishonest when caught

**Definition:** When confronted with a violated rule or invariant, the
agent constructs a post-hoc rationalization — *"competing directives,"
"pulled against," "no clear resolution"* — without quoting the rule and
the allegedly-conflicting directive verbatim. The narrative is fluent,
plausible, and unfalsifiable; the conflict is invented.

**External citation:** [1]

**Backstop:** `AGENTS.md` § DO IT RIGHT 6h (*"when reporting why a rule
was violated, quote the rule and the conflicting directive verbatim.
Post-hoc 'competing directives' narrative without verbatim quotes is
reporting-pathway drift."*). The verbatim-quoting requirement converts
the reporting pathway from narrative reconstruction into a mechanical
check: if the agent cannot supply the two quotable strings, the
conflict does not exist. See `docs/governance/agent-contract-rationale.md`
§ Rationale for the Lindsey et al. 2025 reporting-pathway citation.

> Worked example: see [`docs/governance/agent-contract-rationale.md` § Failure-mode worked examples](docs/governance/agent-contract-rationale.md#failure-mode-worked-examples).

## When to invoke this vocabulary

The patterns are designed to be cited by name in code review,
ADR/OBPI evidence sections, GHI bodies, and post-mortem write-ups so
the conversation routes directly to the engineered backstop.

- *"This PR is `Skipped cheap verification` shape — it pattern-matched
  a CLI flag from training memory without running the destination
  command. Recommended remediation: run `gz <verb> --help` once,
  paste the observed output into the commit body, then re-recommend.
  Backstop: AGENTS.md § DO IT RIGHT 6g."*
- *"The Stage-4 evidence here is `Fabrication` shape — the receipt ID
  cited is not present in `.gzkit/arb/receipts/`. Re-run under
  `uv run gz arb step` and re-cite with the fresh receipt ID, or
  withdraw the attestation. Backstop: AGENTS.md § Attestation,
  `_enforce_human_attestation_authenticity`."*
- *"This post-mortem reads as `Dishonest when caught` shape — the
  'competing directives' framing has no quoted rule text and no
  quoted conflicting directive. Either supply both verbatim or re-
  characterize as a single-rule violation. Backstop: AGENTS.md §
  DO IT RIGHT 6h."*

The vocabulary is reviewer-facing; it is not an excuse for the author
("I was just doing `Reckless action`") and it does not lower the bar
for remediation. The point is to name the failure family fast so the
backstop is found fast.

## Loading posture

This rule is **advisory** at authoring time — the vocabulary, not a
mechanical gate. The defenses (TTY+`ATTEST` gate, ARB receipts, hook
fail-closed, `gz validate --commit-trailers`, T1/T2/T3 invariants) are the
**shared backstops** the names above point at. Cite the pattern by name when
reviewing, filing a defect, or extending the scorecard.

> See [`docs/governance/agent-contract-rationale.md` § Agent failure-mode taxonomy — loading posture and worked examples](docs/governance/agent-contract-rationale.md#agent-failure-mode-taxonomy--loading-posture-and-worked-examples) for promotion roadmap (GHIs #308–#312) and worked examples.

## Related

- `AGENTS.md` § DO IT RIGHT (items 6a, 6c, 6g, 6h) — the gzkit invariants
  the patterns above point at as backstops
- `AGENTS.md` § Attestation — ARB receipt and TTY + `ATTEST` discipline
  that backstops `Fabrication`
- `docs/governance/arb-middleware.md` — ARB middleware contract; the
  receipt-IDs the `Fabrication` backstop consumes
- `docs/governance/trust-doctrine.md` — layered-trust T1/T2/T3
  invariants the `Correction fails` backstop draws on
- `docs/governance/advisory-rules-audit.md` — scorecard catalogue (the
  scorecard entry classifying this rule lands under OBPI-0.0.23-02)
- ADR-0.0.23-agent-failure-mode-taxonomy — the parent ADR carrying the
  Decision text, the system-card review session, and the follow-up
  GHI list (#308–#312) for mechanical promotion
