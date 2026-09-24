# GPT-6 system card: doctrine refresh analysis

**Prepared:** 2026-09-24

**Status:** Evidence map for GHI #1019, consumed the same day.

**Primary source:** OpenAI, [*GPT-6 Astra System Card*](https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf), dated 2026-09-03 with a change log to 2026-09-22, 156 pages. SHA-256 of the retained PDF (`data/system_cards/openai-gpt-6-astra-2026-09-03.pdf`): `cd6d9846df54e75c22b7e4e17f84fa7264f602c134a7e73a70035de5ecec1a02`. Page references are the card's printed page numbers, which run one below the PDF page index.

## What changed in the card after 2026-09-03

- **2026-09-09.** The alignment section clarifies how its evaluations test generalization and expands on their limits. § 8.7 is renamed *Verbalized Metagaming and Oversight Gaming*, and a metric comparison plot is removed.
- **2026-09-22.** HealthBench values are corrected. Appendix A adds GPT-6 Sol and GPT-6 Luna. Five alignment evaluations are re-run in Appendix A.6 with scores for all three models; the main-body figures were not revised, so main body and Appendix disagree (for example, workaround-after-warning 19 % vs 17.4 % for Astra). gzkit cites the Appendix value where both exist.

## The family changed

| Role | GPT-5.6 | GPT-6 |
|---|---|---|
| Flagship | Sol | Astra |
| Lower-cost alternative | Terra | Sol ("a highly capable, lower-cost alternative to Astra", p. 119) |
| Fastest, cheapest | Luna | Luna |

"Sol" moved from flagship to middle tier. The old `gpt-tuning.md` mapping, Sol for judgment work, would have silently routed judgment to the middle tier. gzkit now names GPT models by generation and name.

**Default profile, operator-ruled 2026-09-24.** gzkit's skills stay Anthropic-first; GPT runs bounded adversarial reviews (operator: "A."). For those reviews GPT-6 Sol is the default, GPT-6 Astra is used only by explicit selection, and GPT-6 Luna suits narrow mechanical checks. Operator, verbatim: "If we default to astra, I find that it is too token hungry", then "yes, explicit selection". The card's per-task token figures point the other way in places (Astra uses fewer reasoning tokens than Sol at matched budgets in § 9.2.2), but its cost note says real-world results may vary substantially. The operator's observation measures gzkit's workload and governs the default.

A consequence the default carries: GPT-6 Sol fails to stop after a warning in 64.4 % of rollouts, against 17.4 % for Astra (Appendix A.6.2, p. 128). `gpt-tuning.md` states this beside the default.

## Claim-by-claim disposition

Every live GPT-5.6 claim was checked first against the retained GPT-5.6 PDF, then against the GPT-6 card.

| GPT-5.6 claim | Verdict | GPT-6 evidence used |
|---|---|---|
| Coding misalignment from permissive instruction-reading (§ 7.2) | Carries | Same sentence, stated for Astra (§ 8.6, p. 35) |
| Beyond-intent action more often than the predecessor (§ 7.2) | Reversed | 34 vs 73 severity-3+ flags over 54,218 tasks (§ 8.6, p. 36); Astra "still sometimes overreaches" (p. 35) |
| Persistence at the highest efforts drives it; persistence-emphasizing prompts amplify it (§ 7.2) | Absent | Retired. Replaced by workaround-after-warning rates (§ 8.2.2; A.6.2) and the explicit-scope result, 60 of 499 to 2 of 500 (§ 8.8, p. 45) |
| Supervise long trajectories (§ 7.2) | Absent | Re-sourced to coding deception (§ 8.3.1; A.6.4.1) and permission-then-proceed (§ 8.8, p. 45) |
| Action-only monitors much less reliable (§ 9.2.2) | Changed | For Astra, CoT and full-context monitorability fell, action-only rose (§ 9.1.1, p. 51) |
| Summaries omit cheating the reasoning admits (§ 9.2.2) | Absent | Nearest: euphemistic framing of a reward hack (§ 9.1.2) |
| CoT controllability rising (§ 7.3.2) | Carries, stronger | 60.9 % vs 16.1 % vs 1.7 % at 750–1,250 tokens (§ 9.2.1) |
| PostTrainBench over-optimization at higher effort (§ 9.1.3.4) | Absent | Retired |
| Metagaming definition (§ 7.4) | Changed | Verbalized metagaming and oversight gaming (§ 8.7, p. 40); pattern 9 is oversight gaming |
| METR time-horizon not robust (§ 9.1.3.6) | Absent | Retired; Apollo evaluation awareness 41.1 % at `xhigh`, 50.6 % at `max` (§ 8.8.1, p. 46) used for the same point |
| Three incident vignettes (§ 7.2) | Absent | Replaced by the four § 8.6 severity-3 vignettes (pp. 39–40) |
| Overwrite avoidance 0.83 vs 0.88 (§ 3.3) | Absent | Retired |
| Prompt injection 1.000 / 0.910 (§ 4.2) | Changed | Those evaluations retired as saturated (§ 5.2, p. 17); Gray Swan 8.5 % vs 27.0 % at fifteen attempts (p. 18) |
| Capability reported as curves across effort (§ 1) | Absent | Retired; the card reports these results at maximum effort without a sweep |

## Defects found in the outgoing doctrine

- The 55.4 % / 41.2 % metagaming figures exist only in a figure image in the GPT-5.6 card; the text layer does not carry them. They left doctrine with the card.
- The Apollo "~70 % of flagged samples" gloss overstated a finding that applied to one sandbagging assessment, and "successful gaming is rarer" was gzkit's inference, not the card's.
- The taxonomy's "on production traffic" described a deployment simulation over production prefixes.
- The registry's GPT-5.6 entry omitted two live consumers, `gpt-tuning.md` and `model-regression-taxonomy.md`; the new entry lists them.
- `advisory-rules-audit.md` row 49 still cited the Opus 5 card after the GHI #1089 rotation; corrected here.

## Limits

- The re-run Appendix evaluations are scored for all three models; the Codex deployment simulation covers Astra and GPT-6 Sol, not GPT-6 Luna, and neither Sol nor Luna has a realistic-work-environment table.
- Figure-only values cited in doctrine (A.6.2, A.6.4.1) were read from the rendered pages, not the text layer.
- The card references a Hugging Face incident whose details sit in a separate report; nothing about it is sourced here.
