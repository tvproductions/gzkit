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
## 2026-08-02T10:40:40-06:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.26s) -- exit 0 == 0

```text
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```

## 2026-08-02 — Fable/Mythos 5 card consumed (GHI #751)

- Registry: Fable/Mythos 5 (2026-06-09) `unconsumed` → `current`; all three vendor-tier cards now consumed. Retained PDF verified as the evaluation source.
- Secondary-reporting correction booked: injection posture is best-in-family overall; regression was browser-use-under-deployed-safeguards only (§ 5.2.2.3), closed by updated safeguards. Registry notes rewritten from primary source.
- Superseded sole-sourcing discharged: model-regression-taxonomy.md re-evidenced to current cards (meta-finding direction flipped: overeagerness, not over-caution; F7 T3→T1, F8 T1→T3); tests-rationale eval-awareness corollary re-sourced to Fable §§ 6.1.2/6.4.1.2/6.4.2.
- Remaining archival documents (dated notes/plans) confirmed out of purge scope per GHI #751 classification.
## 2026-08-02T10:59:02-06:00
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
## 2026-09-02 — Mythos-tier drift detected; routed to GHI #934

- **DRIFT (Anthropic, Mythos-class tier).** Claude Fable 5.1 / Mythos 5.1 System Card, **2026-09-01**, supersedes the registry's `current` Fable 5 / Mythos 5 (2026-06-09). Verified against the primary PDF (244pp, operator-supplied URL, text-extracted — not secondary reporting). Nine `doctrine_surfaces` still sole-source the superseded card. Routed to **GHI #934** with a blocker comment naming the refresh sequence; no registry, doctrine, or PDF write performed (lane is read-only scan).
- **NO DRIFT (Anthropic, Opus tier).** Claude Opus 5 (2026-07-24) remains the newest Opus-tier card on the vendor hub. Registry entry correct.
- **OPEN QUESTION (OpenAI).** `GPT-5.6 — August Updates` (2026-08-06) is newer than the registry's GPT-5.6 card (2026-07-09) but reads as an addendum to the same family, not a new tier — a registry-`notes` refresh at most under § Anti-patterns ("one `current` entry per vendor tier"). Not read against primary source. Operator ruling needed.
- **OPEN QUESTION (scope).** Claude Sonnet 5 (June 2026) is on the Anthropic hub with no registry entry. § 2 says "any tier with no registry entry, is drift", but whether the Sonnet tier is in this registry's frontier scope is unresolved by the chore text.
- **CHORE-DEFINITION GAP.** `CHORE.md` declares no cadence or trigger — `grep -inE "cadence|trigger|schedule|when to run"` returns nothing — so detection depends on operator prompting. Sibling `gz-complexity-distill` carries explicit cadence triggers. This run happened only because the operator supplied the card URL; the card had been public since 2026-09-01. Recorded as an insight, not bundled into GHI #934.

## 2026-09-02T02:11:01-04:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.24s) -- exit 0 == 0

```text
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```
## 2026-09-12T14:33:23-05:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py frontier-model-card-currency` => rc=0 (0.03s) -- exit 0 == 0
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.02s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.28s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py frontier-model-card-currency] stdout:
scan-interval gate — frontier-model-card-currency
  maximum age:  30d
  last run:     2026-09-02 (10d ago)

PASS: the last recorded run is within the scan interval.
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```

## 2026-09-17 — Fable/Mythos 5.1 consumed (GHI #934); GPT-6 Astra detected

- **CONSUMED (Anthropic, Mythos-class tier).** Fable 5.1 & Mythos 5.1 card (2026-09-01) rotated in; Fable 5 / Mythos 5 PDF and entry removed; nine doctrine surfaces + `CLAUDE.md` re-sourced; Opus 5 / Fable 5.1 prompting guides consumed as T2 under GHI #943 ("favor opus over fable"). Details in `proofs/scan-record.md`.
- **DRIFT (OpenAI).** GPT-6 Astra System Card (2026-09-03) registered `unconsumed`; GHI filing awaits the operator's word.
- **Manual completion check:** every drifted item is routed — #934 landed (commit SHA in its close comment); GPT-6 Astra carried as an `unconsumed` registry entry pending the GHI.
## 2026-09-17T20:23:02-05:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.3.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py frontier-model-card-currency` => rc=0 (0.08s) -- exit 0 == 0
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.35s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py frontier-model-card-currency] stdout:
scan-interval gate — frontier-model-card-currency
  maximum age:  30d
  scan record:  .gzkit/chores/frontier-model-card-currency/proofs/scan-record.md
  last scan:    2026-09-18 (0d ago)

PASS: the scan record changed within the scan interval.
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```
## 2026-09-23T20:13:28-05:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.4.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py frontier-model-card-currency` => rc=0 (0.09s) -- exit 0 == 0
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.02s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.31s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py frontier-model-card-currency] stdout:
scan-interval gate — frontier-model-card-currency
  maximum age:  30d
  scan record:  .gzkit/chores/frontier-model-card-currency/proofs/scan-record.md
  last scan:    2026-09-24 (0d ago)

PASS: the scan record changed within the scan interval.
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```

## 2026-09-23 — Opus 5.5 scan disposition

- **DRIFT (Anthropic, Opus tier).** The 2026-09-22 Opus 5.5 primary card was read and mapped to live doctrine at `docs/governance/opus-5-5-system-card-analysis-2026-09-23.md`; the registry records it as `unconsumed`, with Opus 5 still `current`. GHI #1089 owns the refresh.
- **DRIFT (OpenAI), already routed.** GPT-6 Astra remains `unconsumed` under GHI #1019.
- **Manual completion check:** both drifted cards have a GHI and registry entry. The scan record names the open Sonnet-tier scope question. No card was marked consumed by this scan.

## 2026-09-24 — Opus 5.5 consumed (GHI #1089)

- **CONSUMED (Anthropic, Opus tier).** Registry rotated: Opus 5.5 `current`, Opus 5 entry and PDF removed. Nine doctrine surfaces re-sourced; `model-selection.md` mapping moved to the current catalog.
- **Defect found in the outgoing doctrine:** two quotations attributed to the Opus 5 card's § 8.4 are not in that card's text; retired with the rotation, recorded in the analysis § Review.
- **Manual completion check:** every drifted item is routed. GPT-6 Astra stays with GHI #1019.

## 2026-09-24T01:49:38-05:00
- Status: PASS
- Chore: frontier-model-card-currency
- Title: Frontier Model Card Currency (System-Card Doctrine Refresh)
- Lane: lite
- Version: 1.4.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py frontier-model-card-currency` => rc=0 (0.08s) -- exit 0 == 0
  - [PASS] `python3 -c "import json; cards=json.load(open('data/frontier_model_cards.json'))['cards']; assert cards, 'registry empty'; missing=[c for c in cards if not all(c.get(k) for k in ('vendor','model_family','card_date','url','status'))]; assert not missing, f'incomplete entries: {missing}'; assert all(c['status'] in ('current','unconsumed','superseded') for c in cards), 'bad status'"` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents` => rc=0 (0.35s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py frontier-model-card-currency] stdout:
scan-interval gate — frontier-model-card-currency
  maximum age:  30d
  scan record:  .gzkit/chores/frontier-model-card-currency/proofs/scan-record.md
  last scan:    2026-09-24 (0d ago)

PASS: the scan record changed within the scan interval.
[uv run gz validate --documents] stdout:
Validated: documents

✓ All validations passed (1 scopes).
```
