# CHORE-LOG: frontier-model-card-currency

## 2026-08-02 — seed inventory (chore authoring run)

- OpenAI: **current** — GPT-5.6 (2026-07-09) consumed 2026-08-02 (GHI #750; commits 7f0b8bdf4, 79ce8b25b). No newer card on deploymentsafety.openai.com.
- Anthropic: **drift** — Claude Fable 5 / Mythos 5 System Card (2026-06-09) registered `unconsumed`; never evaluated against doctrine despite Fable 5 being the active session model. Routing pending operator ruling on Fable adoption (discussion open 2026-08-02).
- Superseded sole-sourcing sweep: `docs/governance/model-regression-taxonomy.md` still cites Opus 4.7 § 6.2.2.2 as current-best evidence — surfaced to operator 2026-08-02, unruled. All other Opus 4.7 / GPT-5.5 citations are historical provenance alongside current-generation corroboration (acceptable per CHORE.md guardrails).
## 2026-08-02T10:07:09-06:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.22s) -- exit 0 == 0

```text
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```
