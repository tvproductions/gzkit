# Scan record — frontier-model-card-currency

**Scan date:** 2026-09-23 (operator supplied the Claude Opus 5.5 primary-card URL)

## Hubs checked

- Anthropic — https://www.anthropic.com/system-cards (read 2026-09-23): the hub lists *Claude Opus 5.5 — September 2026* ahead of Fable/Mythos 5.1 and Opus 5. The supplied primary PDF is dated 2026-09-22, has 230 pages, and has SHA-256 `7311c9c6bbb16d012f1c12c7418b05949fcf7ae3e30d2c40f22050074b2a7378`.
- OpenAI — https://deploymentsafety.openai.com/ (read 2026-09-23): the newest listed core-model card is *GPT-6 Astra System Card — September 3, 2026*. Its later September 22 amendments are on the same card page. *ChatGPT Images 2.5* is a separate image-model card.

## Registry state read before this scan's writes

```
anthropic Claude Fable 5.1 / Mythos 5.1 (Mythos-class tier) 2026-09-01 current
anthropic Claude Opus 5 (Opus tier) 2026-07-24 current
openai GPT-5.6 (Sol / Terra / Luna) 2026-07-09 current
openai GPT-6 Astra 2026-09-03 unconsumed
```

## Findings and routing

- **CONSUMED (Anthropic, Opus tier) — GHI #1089, 2026-09-24.** The Claude Opus 5.5 System Card (2026-09-22) replaced the Opus 5 entry. PDF retained at `data/system_cards/anthropic-claude-opus-5-5-2026-09-22.pdf` (17,795,106 B, SHA-256 as above); the Opus 5 PDF and registry entry removed in the same change. The analysis at `docs/governance/opus-5-5-system-card-analysis-2026-09-23.md` was verified against the PDF first (its § Review lists four corrections). Anthropic's *Prompting Claude Opus 5.5* guide consumed alongside as T2. Registered consumers reconciled: `.gzkit/rules/governance-core.md` (folded into `AGENTS.md` 2026-09-17) dropped; `trust-doctrine.md` and `model-regression-taxonomy.md` added.
- **CONSUMED (OpenAI tier) — GHI #1019, 2026-09-24.** The GPT-6 Astra System Card, as updated 2026-09-22 (Appendix A adds GPT-6 Sol and GPT-6 Luna), replaced the GPT-5.6 entry; the registry family is now `GPT-6 (Astra / Sol / Luna)`. Operator-supplied URL; PDF retained at `data/system_cards/openai-gpt-6-astra-2026-09-03.pdf` (13,878,246 B, SHA-256 `cd6d9846df54e75c22b7e4e17f84fa7264f602c134a7e73a70035de5ecec1a02`); the GPT-5.6 PDF and entry removed in the same change. Evidence map: `docs/governance/gpt-6-system-card-analysis-2026-09-24.md`. Family roles changed (GPT-5.6 Sol was the flagship; GPT-6 Sol is the lower-cost tier); the default GPT profile is GPT-6 Sol by operator ruling.
- **OPEN (tier scope, carried).** Claude Sonnet 5 still has no registry entry; whether the Sonnet tier is within the frontier-card registry's scope remains unruled.

## Superseded-reference sweep

`grep -rnE "Opus 5([^.0-9]|$)" .gzkit/rules/ .gzkit/skills/ docs/governance/ CLAUDE.md` after the refresh hits only dated records (`rule-version-history.md`, the Evolution log of `model-regression-taxonomy.md`, the Origin section of `opus-tuning.md`, the dated context-audit and card-analysis records) and current-card quotations that name Opus 5 as a comparison baseline (Fable 5.1 card §§ 5.2.1, 6.1.2, 6.4.2), which are evidence from a current card and stand.
