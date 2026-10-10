# Scan record — frontier-model-card-currency

**Scan date:** 2026-10-10 (maintenance visit A, admitted by the operator: 'admit visit A')

## Hubs checked

- Anthropic — https://www.anthropic.com/system-cards (read 2026-10-10): the hub lists, newest first, *Claude Haiku 5.5* (October 2026, https://www.anthropic.com/claude-haiku-5-5-system-card), *Claude Sonnet 5.5* (September 2026, https://www.anthropic.com/claude-sonnet-5-5-system-card), *Claude Opus 5.5* (September 2026), *Claude Fable 5.1 and Mythos 5.1* (September 2026). The hub shows month and year only. Neither of the registry's Anthropic tiers (Mythos-class, Opus) has a card newer than its `current` entry.
- OpenAI — https://deploymentsafety.openai.com/ (read 2026-10-10): newest first, *GPT-6 Sol and GPT-6 Luna: October 2026 update* (Oct 07, 2026, `/gpt-6-october`, no description), *Addendum to GPT-6 Astra System Card: GPT-6.1 Sol* (Sep 29, 2026, `/gpt-6-1-sol`: "Safety evaluations and safeguards for GPT-6.1 Sol, an addendum to the GPT-6 Astra system card"), *ChatGPT Images 2.5 System Card* (Sep 08), *GPT-6 Astra System Card* (Sep 03). Two publications on the registry's OpenAI tier postdate its `current` entry.

## Registry state read before this scan's writes

```
anthropic Claude Fable 5.1 / Mythos 5.1 (Mythos-class tier) 2026-09-01 current
anthropic Claude Opus 5.5 (Opus tier) 2026-09-22 current
openai GPT-6 (Astra / Sol / Luna) 2026-09-03 current
```

No registry entry was changed by this scan; the primary PDFs were not opened. Step 4 is operator-only-repair.

## Findings and routing (proposed; the operator rules)

- **DRIFT (OpenAI tier).** The GPT-6.1 Sol addendum (2026-09-29) and the October 2026 update (2026-10-07) postdate the consumed GPT-6 Astra card (2026-09-03, as amended 2026-09-22). Both are publications on the same card family, not a new tier. Proposed routing: one GHI via `ghi-author` (class ancestor GHI #750 / #1019) to read both primary documents against the registry's `doctrine_surfaces` for the OpenAI entry (`gpt-tuning.md`, `trust-doctrine.md`, `model-regression-taxonomy.md` among them), then amend the entry's `card_date` and `consumed_commits` or record a no-change finding. Not consumed here: evaluation is judgment work with its own commit trail (§ Anti-patterns).
- **TIER SCOPE (Anthropic), carried and widened.** The 2026-09-23 record carried *Claude Sonnet 5* as unruled tier scope; the hub now lists *Sonnet 5.5* (September 2026) and *Haiku 5.5* (October 2026). gzkit's model-selection rule routes work to `haiku` and `sonnet` tiers (`.gzkit/rules/model-selection.md` § Routing matrix), so those tiers run gzkit work without a consumed card. Proposed routing: an operator ruling on whether the registry covers every tier the routing matrix names, or only the tiers that source doctrine; if the former, two `unconsumed` entries are added and each is consumed under its own GHI.
- **NO DRIFT (Anthropic Mythos-class and Opus tiers).** No card newer than the `current` entries.

## Superseded-reference sweep

`grep -rnE "Opus 4\.[0-9]|Opus 5([^.0-9]|$)|GPT-5\.[0-9]|Sonnet 4\.[0-9]" .gzkit/rules/ .gzkit/skills/ docs/governance/ CLAUDE.md`, 2026-10-10, excluding `rule-version-history.md`:

- Dated records, legitimate: `opus-5-5-system-card-analysis-2026-09-23.md`, `gpt-6-system-card-analysis-2026-09-24.md`, `externalized-metacognition-architecture-note-2026-06-24.md`, `return-to-health-plan-2026-05-30.md`, `GovZero/audits/governance-harmonization-2026-01-11.md`.
- **Comparative figures quoted from the CURRENT cards, in live doctrine:** `untrusted-content.md` (lines 67, 88, 93, 104: the Fable 5.1 card's fallback to Claude Opus 4.8; the Opus 5.5 card's re-run of Opus 5 Gray Swan figures), `opus-tuning.md` (166, 173, 214: the same fallback and "slightly elevated over Opus 5", both quoted from the Fable 5.1 card), `gpt-tuning.md` (20, 48, 86, 101: GPT-6 figures stated against GPT-5.6 Sol, as the GPT-6 card states them), `trust-doctrine.md` (164: GPT-6 Astra monitorability against GPT-5.6 Sol, from the GPT-6 card). Each reference is the current card's own comparison baseline, not a rule sourced to the superseded card. Whether such a quotation counts as a "direct reference to an older model" under the 2026-08-02 ruling is not settled in the chore text; the 2026-09-23 record read the sweep as clean on the same material. Proposed: the operator rules once; if the quotations are out, the eight lines are re-sourced to the current card's absolute figures under the OpenAI-tier GHI above.
- No rule in `.gzkit/rules/` or skill in `.gzkit/skills/` names a superseded model.
