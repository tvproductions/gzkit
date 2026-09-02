# CHORE: Frontier Model Card Currency (System-Card Doctrine Refresh)

**Version:** 1.1.0
**Lane:** Lite
**Slug:** `frontier-model-card-currency`

---

## Overview

Keep gzkit's model-sourced doctrine pinned to the **latest** frontier system
cards from Anthropic and OpenAI, and retire or re-source rules developed for
superseded models. The registry `data/frontier_model_cards.json` is the
source of truth for what has been consumed; the vendor publication hubs are
the source of truth for what exists.

**Mode: scan + route.** The chore detects drift (a published card the
registry marks `unconsumed`, or a `superseded` card that is still the sole
source of a live rule) and routes the refresh through the established
process — it never auto-rewrites doctrine. Card evaluation is judgment work
that lands as a GHI-tracked direct doc fix, exactly like the Opus 5 pass
(commit `1ddbfaaa1`) and the GPT-5.6 pass (GHI #750, commits `7f0b8bdf4`,
`79ce8b25b`).

**Why this chore exists:** doctrine surfaces sourced to system cards stale
silently on every vendor release. `docs/governance/opus-tuning.md`
§ Recalibration names the failure — that page sat pinned to Opus 4.7 for
three model generations before the Opus 5 evidence inverted its central
rule. Rules calibrated on a superseded model are pattern-matched memory, not
evidence (V.I.B.E.S. by another route).

## Source

Operator ruling 2026-08-02 (verbatim): "We keep the latest system cards and
go through this process as they update. No sense in keeping rules developed
for superseded models."

## Policy and Guardrails

- **Lane:** Lite — the scan is read-only; refresh work routes to its own
  GHI-tracked commits under AGENTS.md § Defect-fix routing
- **Network:** Required (vendor hubs, card PDFs via WebFetch/WebSearch)
- **Cards are retained and rotated (operator-ruled 2026-08-02).** The
  current card PDF for each vendor tier lives in `data/system_cards/`
  (named `<vendor>-<model>-<date>.pdf`); when a newer card is consumed, the
  new PDF lands and the superseded PDF and its registry entry are removed
  in the same commit. Verify claims against the retained primary PDF, never
  against secondary reporting alone.
- **No superseded-model references survive in live doctrine
  (operator-ruled 2026-08-02, verbatim: "I don't want to retain direct
  references, and rationale, to older models").** When a card is
  superseded, every live rule, calibration page, and rationale citation
  pinned to it is re-sourced to the current card or retired in the same
  refresh. Origin lineage moves to
  `docs/governance/rule-version-history.md` (audit trail, not doctrine);
  the ledger and commit history remain untouched.
- **Effort/tuning values expire with their model.** Any calibration page
  (opus-tuning.md and successors) must state which model measured its
  numbers; a card for a newer model in the same tier voids the values until
  re-derived (`docs/governance/opus-tuning.md` § Recalibration).

## Cadence

**Mechanically gated.** The maximum age of a recorded run is the
`frontier-model-card-currency` entry in `_SCAN_INTERVALS`
(`scripts/check_proof_freshness.py`), enforced as criterion 1 of
`acceptance.json`. The interval is not restated here: a value written in a
Markdown doc is illustrative, never authoritative
(`.claude/rules/governance-core.md`), and a cadence this file merely *declared*
would be the doctrine-declared-without-mechanism shape `AGENTS.md` forbids.
Read the constant; its comment carries the measured publication intervals the
number was derived from, and says to re-derive rather than transcribe it when
the observed vendor cadence moves.

The gate reads the timestamped blocks `gz chores run` appends to
`proofs/CHORE-LOG.md` — never the hand-authored findings headings beside them.
Appending prose is authorship, not a run.

**Event triggers (run regardless of the interval):**

- An operator supplies a card URL, or a vendor release is noticed in passing
- Before a release ceremony, or before ADR/OBPI work whose evidence cites any
  path in the registry's `doctrine_surfaces`
- Between OBPI implementations as a hygiene checkpoint, per the cadence of
  `.gzkit/chores/dependency-currency/CHORE.md` § Source that this chore mirrors

**Why a clock at all (GHI #935):** criteria 2 and 3 check the registry's
*shape*; nothing in this repository changes when a vendor publishes, so without
an elapsed-time arm the chore reports `All criteria pass` for as long as nobody
looks. On 2026-09-02 it did exactly that, 31 days after its previous run, while
the Mythos-class `current` entry had been superseded since 2026-09-01 (GHI
#934) — caught only because the operator supplied the URL.

## Workflow

### 1. Inventory the registry

```bash
python3 -c "import json; [print(c['vendor'], c['model_family'], c['card_date'], c['status']) for c in json.load(open('data/frontier_model_cards.json'))['cards']]"
```

### 2. Query vendor hubs for newer cards

Check each hub in the registry's `vendor_hubs` (WebSearch/WebFetch):
Anthropic news/system-card announcements; OpenAI
`deploymentsafety.openai.com`. A card newer than the registry's `current`
entry for that vendor/tier, or any tier with no registry entry, is drift.

### 3. Sweep live doctrine for superseded-model references

```bash
grep -rlE "Opus 4\.7|GPT-5\.5" .gzkit/rules/ docs/governance/ CLAUDE.md
```

**Every hit in live doctrine is drift** — re-source the citation to the
current card or retire the rule (operator ruling 2026-08-02). The only
legitimate homes for superseded-model text are
`docs/governance/rule-version-history.md`, the ledger, and commit history
(audit trail). Extend the grep pattern as models supersede.

### 4. Route drift

For each drifted item: file one GHI via `/ghi-author` (class ancestor:
GHI #750), evaluate the primary card PDF against the doctrine surfaces the
registry lists, land the refresh as a direct doc fix, update the registry
entry (`status`, `consumed_on`, `consumed_commits`, `doctrine_surfaces`),
and cite the commit when closing. New failure-mode patterns extend
`.gzkit/rules/agent-failure-modes.md` under ADR-0.0.23's living-rule
pre-authorization — check surface-weight headroom first
(`uv run gz validate --surface-weight`).

### 5. Record

Append the run's findings (or a clean no-drift line) to
`proofs/CHORE-LOG.md` with the date and registry state.

## Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Registry parses and every entry carries vendor, card_date, url, status | `acceptance.json` python check exit 0 |
| 2 | Documents validate after any refresh | `uv run gz validate --documents` exit 0 |
| 3 | Every drifted item is routed (GHI or registry note), never left untracked | manual — recorded in `proofs/CHORE-LOG.md` |

## Anti-patterns

- Consuming a card from secondary reporting without opening the primary PDF
  (Skipped cheap verification)
- Marking a card `current` without listing the doctrine surfaces its
  citations landed on — an unlisted surface is invisible to the next sweep
- Rotating a card out of the registry while its citations still stand in
  live doctrine — the re-source lands first (or in the same commit), then
  the rotation
- Keeping a superseded card's PDF or registry entry "for reference" — the
  rotation is the ruling; lineage lives in rule-version-history.md and git
  history
- Auto-rewriting doctrine inside the chore run — evaluation is judgment
  work with its own GHI and commit trail
- Treating a same-tier vendor rebrand as a new tier requiring a new entry —
  one `current` entry per vendor tier

## Related

- `data/frontier_model_cards.json` — the registry this chore reads and updates
- `.gzkit/chores/dependency-currency/CHORE.md` — the currency-scan pattern this chore mirrors
- `.gzkit/rules/agent-failure-modes.md` — living taxonomy the refreshes extend (ADR-0.0.23)
- `docs/governance/opus-tuning.md` § Recalibration on model change — the expiry doctrine
- GHI #750 + commits `1ddbfaaa1`, `7f0b8bdf4`, `79ce8b25b` — the refresh-process precedent
