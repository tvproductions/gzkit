<!--
TEMPLATE — copy into the TARGET repo (not gzkit) alongside the campaign
instance. This is the engagement's append-only flight-data recorder: the
Layer-2 truth the campaign checklist is a view of. Append entries; never
rewrite a landed one. One block per sortie (add CARD at freeze, then fill the
rest as the sortie flies).
-->

# Flight Log — <TARGET>

Append-only. Each sortie gets one block, written in flight order. A campaign
checkbox may be ticked only against a block here whose Chase verdict is PASS.

---

## SORTIE S<N> — <name>

- **Card frozen:** <YYYY-MM-DDThh:mmZ>  ·  **Envelope:** <center|expansion|corner>
- **Design claim:** <the falsifiable property this sortie asserts>
- **Substrate state at open:** <clean tree / green `gz check` / no active locks>

### CARD (pre-registered — frozen before fly)
> Full card per gzkit `docs/flighttest/flight-card-template.md`. Paste the
> frozen card here. The expected observables below are the falsifier — do not
> edit after Go.

- **Test points:** <the ordered governed-path chain>
- **Instrumentation (PASS signature):** ledger ⟨events/counts/fields⟩ · receipts ⟨prefixes⟩ · state ⟨assertions⟩ · artifacts ⟨files+linkage⟩
- **Pre-registered falsifiers:** <any-one ⇒ FAIL, incl. the "passed only by leaving the governed path" tripwire>

### GO / NO-GO (human — test director)
- **Ruling (verbatim):** "<operator words>" — <name>, <YYYY-MM-DDThh:mmZ>
- **Verdict:** <GO | NO-GO>

### BLACK BOX (collected in flight)
- **Ledger slice:** <event kinds observed + IDs, in order>
- **Receipts:** <receipt IDs emitted>
- **State at exit:** <gz state / gz status output>

### CHASE (independent verdict)
- **Observer:** <spec-reviewer | quality-reviewer>
- **Read:** <the exact evidence handed over>
- **Verdict:** <PASS | FAIL> — <one-line justification from evidence alone>

### DEBRIEF
- **Black box vs. card:** <what matched, what diverged>
- **Design signal:** <sound | awkward-but-correct | wrong> — <why>
- **Squawks & disposition:** (gzkit-directed feedback files cross-repo via `gz issue file`, never a target-local `/ghi-author`)
  - <squawk> → <gzkit issue # (via `gz issue file`) | target-local defect | card amendment>
- **Director ruling:** "<operator words>" — <name>, <YYYY-MM-DDThh:mmZ>
- **Re-fly needed?** <yes/no — if a gzkit design change was prompted>

---
