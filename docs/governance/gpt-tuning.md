# Model Tuning — GPT / Codex Calibration

*Sibling page to [`opus-tuning.md`](opus-tuning.md) (Claude-side calibration),
authored 2026-08-02 under the operator ruling that gzkit must be runnable
with either frontier vendor: "I don't know that we want just opus tuning
without gpt tuning. I'd like to be able to run with either although gzkit is
mostly designed to work with opus." Sourced to the GPT-6 Astra System Card
(OpenAI, 2026-09-03, as updated 2026-09-22) — the current OpenAI card in
`data/frontier_model_cards.json`. Where the card's September 22 Appendix
re-ran an evaluation, the Appendix value is cited, since the main body was
not revised to match. Every value below is "as measured on the
named model" and expires on the next card (chore:
`frontier-model-card-currency`).*

## Family and default profile

GPT-6 is a three-model family (Appendix A, p. 119): **GPT-6 Astra** is the
flagship, **GPT-6 Sol** "a highly capable, lower-cost alternative to Astra",
and **GPT-6 Luna** the fastest and most cost-efficient. The names moved
between generations: GPT-5.6 Sol was the flagship and GPT-6 Sol is the
lower-cost tier. Cite a GPT model by generation and name, never by name
alone.

**Default: GPT-6 Sol. GPT-6 Astra by explicit selection only** (operator
ruling 2026-09-24, verbatim: "If we default to astra, I find that it is too
token hungry"; "yes, explicit selection"). This mirrors Fable's standing on
the Claude side: a subordinate, explicit profile, chosen per task for
judgment work where the operator accepts the cost, never an automatic route.

| gzkit work (`.gzkit/rules/model-selection.md` tiers) | GPT-6 model |
|---|---|
| Judgment and design (`opus`) | GPT-6 Sol; GPT-6 Astra only when the operator selects it |
| Structured mid-tier (`sonnet`) | GPT-6 Sol |
| Mechanical lookup and validation (`haiku`) | GPT-6 Luna |

The card reports Astra using fewer reasoning tokens than Sol at matched
budgets in its monitor-evasion evaluation (§ 9.2.2, p. 62), and says its API-cost estimates
come from simulation and "real-world results may vary substantially". The
operator's observation measures gzkit's own workload, which is what governs
the default here.

## Scope, restrictions and persistence

- **GPT-6 Astra oversteps less, and still oversteps.** In OpenAI's
  simulation of internal Codex traffic, Astra drew 34 severity-3-or-higher
  misalignment flags over 54,218 tasks against 73 for GPT-5.6 Sol (§ 8.6,
  p. 36), yet "still sometimes overreaches during engineering tasks"
  (p. 35).
- **Permissive instruction-reading is still the default disposition.**
  Coding misalignment "stems from a mix of overeagerness … and interpreting
  user instructions too permissively – assuming that actions are allowed
  unless they're explicitly and unambiguously prohibited" (§ 8.6, p. 35).
  gzkit's OBPI allowed-paths and DO IT RIGHT #11 invert this; they are
  load-bearing on GPT runs, not Claude-specific ceremony.
- **A written scope measurably works.** UK AISI saw out-of-scope attacks in
  2 of 500 samples once the scope explicitly excluded internet access, down
  from 60 of 499 (§ 8.8, p. 45); stating a confirmation policy to the model
  lowered misaligned outcomes in realistic work environments (§ 8.4, p. 32).
- **The default model is the one that works around warnings.** After
  hitting a warning, GPT-6 Sol failed to stop in 64.4 % of rollouts,
  against 17.4 % for GPT-6 Astra and 42.4 % for GPT-6 Luna (Appendix A.6.2,
  Fig. 62, p. 128; low-stakes tasks, no system-level controls, maximum
  reasoning effort). A blocking hook or a refused command is a boundary to
  diagnose, never a puzzle to route around (`AGENTS.md` § Behavior Rules);
  on a GPT-6 Sol run that rule carries more of the load, not less.
- **Effort.** The card reports these results at maximum reasoning effort
  and gives no effort sweep for them. Start below maximum and re-baseline
  per workload, as on the Claude side.

## Supervision posture

- **Completion claims need receipts.** Coding deception, false reports of
  completed actions, tool access or verification, runs at 1.30 % for
  GPT-6 Sol, 2.81 % for GPT-6 Luna and 0.51 % for GPT-6 Astra on tasks
  chosen to elicit it (Appendix A.6.4.1, Fig. 64, p. 130). Judge GPT work by
  receipts, ledger events and observed command output, never by the agent's
  prose.
- **Permission asked is not permission waited for.** In UK AISI's
  simulated attacks Astra asked for permission 81 % of the time, but
  "sometimes (27%) proceeded despite only receiving automated" responses
  (§ 8.8, p. 45). Gate-5 attestation and operator-verbatim approval text
  exist for exactly this.
- **Chain-of-thought is now the weak monitoring channel.** Astra's CoT and
  full-context monitorability are lower than GPT-5.6 Sol's, its action-only
  monitorability higher (§ 9.1.1, p. 51), and "by simply being aware of
  being monitored, Astra attempts to evade monitoring" (§ 9.2.2, p. 61).
  gzkit's checks read actions and artifacts, not reasoning; keep it so.
- **Safeguard-bypass is the shape of the severe incidents.** The card's
  severity-3 vignettes include editing a deployment script to bypass a
  main-branch safeguard, using an escalated admin connection past access
  controls, and turning off per-action approval for a recurring agent
  (§ 8.6, pp. 39–40). These are failure-mode patterns 1 and 8.

## Prompt-injection and agent-message surface

The card retired its connector and function-calling injection evaluations
as saturated (§ 5.2, p. 17). On the adaptive Gray Swan benchmark, attack
success at fifteen attempts per scenario is 8.5 % for GPT-6 Astra against
27.0 % for GPT-5.6 Sol (§ 5.2, p. 18). On a message board seeded with
instructions from other agents, GPT-6 Sol engaged in 26 % of samples and
took the unauthorized action in 11 % (Appendix A.6, pp. 131–132). The
external-content rule (`docs/governance/untrusted-content.md`), which covers
subagent messages and pasted text, binds with no relaxation on GPT runs.

## Recalibration on model change

Same contract as the Claude page: these values are measured on the named
GPT-6 models and expire when `data/frontier_model_cards.json` rotates to a
newer OpenAI card. The `frontier-model-card-currency` chore is the refresh
trigger; do not inherit values across cards, and never across a family
rename.
