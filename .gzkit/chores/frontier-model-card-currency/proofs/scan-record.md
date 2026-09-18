# Scan record — frontier-model-card-currency

**Scan date:** 2026-09-17 (operator-triggered inside the `instructions-files-diet` run; GHI #934 refresh landed in the same pass)

## Hubs checked

- Anthropic — https://www.anthropic.com/system-cards (read 2026-09-17): newest listed card is *Claude Fable 5.1 and Mythos 5.1 — September 2026*; newest Opus-tier card is *Claude Opus 5 — July 2026*. Nothing newer than either.
- OpenAI — https://deploymentsafety.openai.com/ (read 2026-09-17): newest core-model card is *GPT-6 Astra System Card* (2026-09-03, `https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf`); *ChatGPT Images 2.5* (2026-09-08) is an image-model card, out of this registry's scope.

## Registry state read in step 1 (before this scan's writes)

```
anthropic Claude Fable 5 / Mythos 5 (Mythos-class tier) 2026-06-09 current
anthropic Claude Opus 5 (Opus tier) 2026-07-24 current
openai GPT-5.6 (Sol / Terra / Luna) 2026-07-09 current
```

## Findings and routing

- **CONSUMED (Anthropic, Mythos-class tier) — GHI #934.** The Claude Fable 5.1 & Claude Mythos 5.1 System Card (2026-09-01) replaced the Fable 5 / Mythos 5 entry. PDF retained at `data/system_cards/anthropic-claude-fable-5-1-mythos-5-1-2026-09-01.pdf` (16,397,488 B, from the vendor CDN); the superseded PDF and entry removed in the same commit. All nine registered doctrine surfaces plus `CLAUDE.md` re-sourced; the 5.1 card carries no § 2.3.3 cluster counts, no § 6.3.5 diligence rates, no § 6.3.7 steering pair and no Vending-Bench effort peak, so those figures left live doctrine with the card. Anthropic's live *Prompting Claude Opus 5* and *Prompting Claude Fable 5.1* guides consumed alongside as T2 (GHI #943, Opus-first precedence).
- **NO DRIFT (Anthropic, Opus tier).** Claude Opus 5 (2026-07-24) remains current.
- **DRIFT (OpenAI) — GPT-6 Astra (2026-09-03) supersedes the GPT-5.6 entry.** Registered as `unconsumed`; GPT-5.6 stays `current` until the refresh lands. Not read this scan (the card is judgment work with its own GHI, per § Workflow step 4); routing awaits the operator's word on filing the GHI (class ancestor GHI #750). Live GPT-side surfaces: `docs/governance/gpt-tuning.md`, `.gzkit/rules/agent-failure-modes.md` (pattern 9), `docs/governance/opus-tuning.md` § cross-vendor block, `docs/governance/trust-doctrine.md`, `docs/governance/model-regression-taxonomy.md`, `docs/governance/agent-contract-rationale.md`, `docs/governance/advisory-rules-audit.md`.
- **OPEN (scope, carried from 2026-09-02).** Claude Sonnet 5 (June 2026) has no registry entry; whether the Sonnet tier is in frontier scope is still unruled.

## Superseded-reference sweep (step 3)

`grep -rlE "Fable 5 |Fable 5/|Fable/Mythos 5 |Mythos 5 System|Opus 4\.7|GPT-5\.5" .gzkit/rules/ docs/governance/ CLAUDE.md` after the refresh hits only dated records: `docs/governance/rule-version-history.md` (lineage), the Evolution log of `model-regression-taxonomy.md`, and the Origin section of `opus-tuning.md`. Current-card quotations that name an older model as a comparison baseline (Opus 5 card § 6.1.2 on constraint adherence) are evidence from a current card and stand.
