---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-23T01:19:45Z'
agent: g0
continues_from: 20260922T115210Z-astra-placement-ruled-session-close.md
---

## Current State Summary

Phase 3 of the IEEE/ISO-IEC-IEEE standards investigation is COMPLETE as of 2026-09-23. Agent 2's Act 1 cold read was taken and recorded; the full reconciliation pass ran against Astra's Phase 2 challenge table; and the operator ruled five open matters, closing every question the register carried. FINDINGS.md now stands at 2 CONFIRMED, 15 QUALIFIED, 2 DISPUTED, 14 OPEN, 2 REJECTED across 35 rows, with eight disagreements at D-01 to D-08. PHASE 4 IS NOT AUTHORISED and Phase 3 closing does not authorise it.

## Important Context

Read docs/governance/ieee/README.md first; it is the entry point and now also carries the measurement-program table and the binding-terms section that were missing. The five canonical files are README.md, FINDINGS.md, DISAGREEMENTS.md, OPEN-QUESTIONS.md and consequence-bands.md. Two new historical records exist: act1-cold-read-2026-09-23.md (Agent 2's verdict on the register itself, with a dated disposition table separating the reading from its consequences) and Astra's Phase 2 report, unchanged at the directory root. WORKFLOW FRONTS (campaign docs/governance/build-to-1.0-campaign-2026-09-20.md, section Workflow fronts): none of the four fronts advanced this session. handoff system - untouched. ghi triage - untouched. adr/obpi campaign - untouched; ADR-0.35.0 remains campaign TOPMOST with closeout BLOCKED on missing ledger proof under GHI #930. new R&D - untouched. This session worked the IEEE investigation, which is not one of the four fronts. TWO STANDING CAUTIONS. D-01 (F-006, does a persistent system model exist) and D-05 (F-021, can the system retire what it detects) are UNRESOLVED disagreements on load-bearing findings and must not be read as settled in either direction. And an OPEN row is settled but NOT confirmed: nothing challenged it, so it may never be cited as having survived challenge.

## Decisions Made

[operator] Act 1 cold read ordered ahead of reconciliation, because reconciliation rewrites the register and the cold read cannot be retaken. Correct call: it found four wrong source anchors, three wrong line numbers, two arithmetic errors and four contradictions. [operator] Q-02 NARROWED, verbatim: repair stale metadata and restore linkage. Replaces rewrite the PRD. The product-claim half of the 2026-09-22 ruling carries forward unchanged; superseded wording retained. Astra reached the same narrowing independently from the adversarial side. [operator] Q-11 CONFIRMED: F-### ratified, no identifier changes. Three files had been denying the 2026-09-22 ruling for eleven amendments; corrected. [operator] Q-12 CONFIRMED: design-candidates.md in this directory, tiered below FINDINGS.md, CREATED WHEN PHASE 4 OPENS AND NOT BEFORE. The entry no longer rules and un-rules itself. [operator] settled and ruled separated as vocabulary: status is about evidence, a ruling answers a Q-##, and the two are orthogonal. FINDINGS.md index gained a Ruling column, populated for eight rows. F-006 is the worked case - DISPUTED and ruled at Q-03 at once. [operator] Q-14 ALLOCATED AND RULED: OPEN is a settled disposition for a row the adversarial review never reached. Phase 3 stop condition met. The alternative - commissioning a second adversarial pass - was rejected because it would invent a fourth role the binding composition model does not have. [agent] Reconciliation classifications and the eight D-entries are the agent's, not the operator's, and are open to challenge.

## Immediate Next Steps

Nothing is REQUIRED next; Phase 3 closed cleanly and this is a stopping point. Everything below is available WITHOUT entering Phase 4, in rough order of value.
1. Run a measurement item from the program M-A to M-H, summarised in README.md section The measurement program. M-H is DISCHARGED (consequence-bands.md); seven are outstanding. M-B settles D-03, M-C bears on D-01, M-G settles D-04. M-F is independent and cheap and is the home of D-08. M-D is gated on its own method problem and must NOT be started until that is settled.
2. Decide whether a finding should be authored for D-08, the BDD-duplication claim that has a measurement home in M-F but no F-### and therefore no status.
3. Decide whether findings should be authored for the three independently observed D2 rows in consequence-bands.md (Attestation/completion events, @covers binding, Distribution/gz init), which currently cannot be re-scored when the register moves.
4. Decide whether to lift PROVISIONAL from consequence-bands.md. No band moved during reconciliation, but the file rests partly on F-021, which is DISPUTED.
5. Phase 4 requires EXPLICIT OPERATOR AUTHORISATION and the full triad when it opens. Phase 3 closing does NOT authorise it.
Unrelated and untouched by this session: the version_sync kind guard (GHI-sized, unblocked, unstarted) and ADR-0.35.0 closeout, BLOCKED on missing ledger proof under GHI #930.

## Pending Work / Open Loops

D-01 and D-05 remain UNRESOLVED and are standing conditions, not open tasks. Three cold-read gaps remain open by nature rather than by neglect: two senses of the word settled are now separated but the register has no glossary for its other assumed vocabulary; the same wrong source anchors that were repaired in the canonical files STILL EXIST in the frozen pieces 01 and 02, which may be corrected only by a later piece saying so; and re-derivation scripts were tiered as tooling rather than narrative, which NARROWS A BINDING READING LIST and the operator may overturn it. One structural gap worth a GHI if the operator wants it: no validator checks source anchors cited from docs/governance/**, so a path:line that does not resolve is invisible to gz check. That is why seven wrong anchors accumulated undetected. Agent 2 Act 2 does not exist until Phase 4 is authorised, and Act 1 cannot be retaken.

## Verification Checklist

uv run gz validate --cli-alignment --documents --surfaces exits 0, run after every edit this session. uv run mkdocs build --strict exits 0. Working tree clean and main level with origin/main at 6c1cfa73b. FINDINGS.md index holds 35 rows summing to 2 CONFIRMED + 15 QUALIFIED + 2 DISPUTED + 14 OPEN + 2 REJECTED. DISAGREEMENTS.md holds 8 D-entries. Astra challenge table counted directly: 25 data rows, 9 REJECT, 3 DOWNGRADE TO HYPOTHESIS, 11 CONFIRM WITH QUALIFICATION, 1 CONFIRM, 1 NEEDS MORE EVIDENCE. NOTE the register previously recorded 26 rows and 8 REJECT and the enumeration summed to 24; the corrected figures are the counted ones. Re-count before trusting any figure transcribed here.

## Evidence / Artifacts

Commits this session, all on main: e8e795601 Act 1 cold-read repairs; 32e511ce7 reconciliation pass; a4b086577 Q-02 narrowing; 2c7acbad7 Q-11 and Q-12; c0ab1778e IRON LAW and Architectural Boundaries pointers; 625c22ed1 Act 1 record written up; c27776571 settled/ruled split and Ruling column; 92220eaf8 measurement program, D2 provenance, raw/ line, D-08 home; 6c1cfa73b Q-14 and Phase 3 complete. Key files: docs/governance/ieee/README.md (entry point, measurement program, binding terms); FINDINGS.md (35 rows, Ruling column); DISAGREEMENTS.md (D-01 to D-08); OPEN-QUESTIONS.md (Q-01 to Q-14, all ruled); consequence-bands.md (PROVISIONAL, D2 provenance traced); act1-cold-read-2026-09-23.md (the cold read and its disposition table). Three insights recorded under scope docs.governance.ieee in .gzkit/insights/agent-insights.jsonl. Handoff ruling for the resumed 20260922T115210Z handoff booked via gz handoff decide.

## Settled Rulings

1028 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
