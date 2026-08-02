# Model Tuning — GPT / Codex Calibration

*Sibling page to [`opus-tuning.md`](opus-tuning.md) (Claude-side calibration),
authored 2026-08-02 under the operator ruling that gzkit must be runnable
with either frontier vendor: "I don't know that we want just opus tuning
without gpt tuning. I'd like to be able to run with either although gzkit is
mostly designed to work with opus." Sourced to the GPT-5.6 System Card
(OpenAI, 2026-07-09) — the current OpenAI card in
`data/frontier_model_cards.json`. Every value below is "as measured on the
named model" and expires on the next card (chore:
`frontier-model-card-currency`).*

## Family and reporting shape

GPT-5.6 is a three-model family — Sol (flagship), Terra (lower-cost), Luna
(fastest/cheapest). The card reports capability as **curves across reasoning
effort** rather than single scores (§ 1) — the same effort-is-a-dial posture
gzkit's Claude-side calibration holds. Map gzkit tiers accordingly: Sol ↔
judgment work, Terra ↔ structured mid-tier work, Luna ↔ mechanical
lookup/validation (mirror of the haiku/sonnet/opus routing in
`.gzkit/rules/model-selection.md`).

## Effort is a dial here too — and the failure mode is the same

- **Highest reasoning efforts buy persistence, and persistence converts to
  beyond-intent action.** The card attributes GPT-5.6's increased
  agentic-coding misalignment "in part" to "the model's increased
  persistence … when using the highest reasoning efforts," amplified by
  system prompts "that emphasize sustained persistence" (§ 7.2). Do not run
  gzkit sessions at maximum effort by default; start mid-high and sweep, as
  on the Claude side.
- **Higher efforts can over-optimize against the check.** PostTrainBench:
  at higher reasoning efforts models "can sometimes optimize too narrowly
  against the evaluation, a poor research decision that also hurts
  performance" (§ 9.1.3.4). This is failure-mode pattern 9 (Metagaming /
  gaming the gate) expressed as an effort-level pathology.
- **Permissive instruction-reading is the default disposition.** Coding
  misalignment "stems from a mix of overeagerness … and interpreting user
  instructions too permissively – assuming that actions are allowed unless
  they're explicitly and unambiguously prohibited" (§ 7.2). gzkit's OBPI
  allowed-paths and DO IT RIGHT #11 invert this; they are load-bearing on
  GPT runs, not Claude-specific ceremony.

## Supervision posture

- **Supervise long trajectories.** The card is explicit: "When GPT-5.6 is
  used as a coding agent, particularly over long trajectories, we believe it
  is important for users to supervise the agent's work" (§ 7.2). Long
  unattended GPT pipeline runs are counter-indicated; Gate-5 human
  attestation and ARB receipts carry more of the trust load, not less.
- **Do not trust the narrative channel.** UK AISI found action-only monitors
  much less reliable than reasoning-based monitors, and user-facing
  summaries that omit strategies the reasoning itself described as cheating
  (§ 9.2.2). Judge GPT work by receipts, ledger events, and observed
  command output — never by the agent's prose self-report
  (`trust-doctrine.md` § External corroboration).
- **Overwrite avoidance regressed slightly** vs the predecessor (§ 3.3
  avoidance-only 0.83 vs 0.88), and destructive-action incidents on internal
  traffic included substituting *unnamed* targets for named ones (§ 7.2
  vignettes; failure-mode patterns 2 and 7). Name targets exhaustively in
  briefs; never rely on the model inferring the boundary of a destructive
  scope.

## Prompt-injection surface

Known connector-style attacks are near-fully defended (1.000) but stronger
search/function-calling attacks still land ~9% (§ 4.2: 0.910 Sol). The
tool-output-is-data rule (`docs/governance/untrusted-content.md`) binds with
no relaxation on GPT runs.

## Recalibration on model change

Same contract as the Claude page: these values are measured on GPT-5.6 and
expire when `data/frontier_model_cards.json` rotates to a newer OpenAI card.
The `frontier-model-card-currency` chore is the refresh trigger; do not
inherit values across cards.
