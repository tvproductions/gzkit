---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-26T08:31:14Z'
agent: claude-code
session_id: 15ccb03e-0293-4b54-a7de-76369e7d7d0d
continues_from: .gzkit/handoffs/20261026T001040Z-rnd-contractor-kit-matrix-ruled.md
---

## Current State Summary

The R&D run docs/rnd/contractor-kit.md resumed (operator: 'step 1') and ran through a long ruling session. The rows ruled were A8 (surveillance as a runtime hold), A3 (the coordinator's authority, now booked), C4 (stop work routed by trigger), A7 (the affected parties) and C3 (three tiers of check). The session then opened a new core subject, the two-way mode contract: every control carries a Minimum Equipment List entry with Meyer-style levels; the contract is onboarded per surface and only the condition signal is central; built-in self-test reports outbound and standby is the inbound command; there is one non-operational condition; and the contract is a permanent design requirement for everything built. Sources landed verbatim: the MEL (14 CFR 91.213/121.628, AC 91-67, N 8900.748), Design by Contract excerpts (Eiffel Software), and the aviation widening texts (Parts 65/145, 43 appendices, etc.). A census of controls landed (421 code controls, 206 model-oriented surfaces). Its defects were reviewed against the code and filed as GHIs #1271 to #1280 on the operator's approval. Every act is committed. The run is not signed off.

## Important Context

The run is gz-rnd diamond 1: it executes no disposition row without the operator's go on that row. The record accretes and is never tidied. Every mapping put to the operator reads both sides in full first. The JFMM and TUM PDFs are gitignored; fresh text extractions were made with pdftotext -layout from docs/rnd/contractor-kit/sources/*.pdf into the session scratchpad and must be re-made in a new session. Safe mode is open (.gzkit/mx.json is tracked in git with mode: safe; see #1263 and #1273), so the pre-push gz check is alarm-wrapped off. The mx-session lock was past 50% of its TTL at session start. FAA Order 8900.1 V4C4 and the MMEL policy letters (PL-25/34/36) could not be retrieved, because fsims.faa.gov is gone and DRS is a JS shell; only the operator can supply them. 'Standby', 'built-in self-test' and 'factory floor' are the operator's terms with no text source.

## Decisions Made

- [operator-ruled] Book the resume of the run at step 1 only (verbatim: 'step 1').
- [operator-ruled] A8: a surveillant outside the work chain, dispatched only by the operator, files a stop request on JFMM's three triggers, and the runtime holds the surface (selected 'A: request becomes hold (Recommended)').
- [operator-ruled] The coordinator's authority is booked as provisional A, filled in by the delve (selected 'Book A as stated (Recommended)').
- [operator-ruled] C4: stop work is a recorded package event, routed by trigger to the coordinator or the operator; the runtime refuses landing until resolved (selected 'A: routed by trigger (Recommended)').
- [operator-ruled] The questions are the right ones (verbatim: 'questions are fine').
- [operator-ruled] Affected parties are the operator, all agents, the control surfaces and rules that enforce behavior, and end users of an adopting system (verbatim: 'affected parties aee: the operator, plus all gzkit (or adopting system's) agents, control surfaces and rules designed to enforce system behavior, and, when applicable, all end users of an adopting system.').
- [operator-ruled] The mode contract is design by contract, honored at the place of call, and it is a massive refactor worth doing (verbatim: 'yes, that will be a MASSIVE refactor, but it is the best way that I can see.').
- [operator-ruled] The mode contract is shaped as a Minimum Equipment List entry with Meyer levels per signal (selected 'A: MEL with Meyer levels (Recommended)').
- [operator-ruled] The contract is each surface's compliance obligation; only the signal is central, in config (verbatim: 'one json file isn't each surface or actor onboarding the contract - the contract becomes a compliance obligation for the surface/actor.').
- [operator-ruled] The contract is two-way: built-in self-test reports suitability for function outbound, and standby is safe mode's command to reduce compliance inbound; do the design right, not fast (verbatim: 'I also caution us to not be so parsimonious or urgent to get back underway that we don't do this design the right way.').
- [operator-ruled] The census covers every control by kind (code; skills and prompt routing; rules and model surfaces), with priorities ordered (verbatim: 'The priorities have to be ordered, right? We can't just redo everything at once.').
- [operator-ruled] The mode contract is a permanent design requirement for everything built (verbatim: 'this is an overarching design requirement permanently and always with everything we build').
- [operator-ruled] C3: three tiers of check, (V) craftsman verification, second person and (I) inspection (selected 'A: three tiers (Recommended)').
- [operator-ruled] One non-operational condition; each control carries accepted-and-lowered or not-yet-accepted (selected 'A: one condition (Recommended)').
- [operator-ruled] Every census defect is fixed, the MX system is reviewed whole, and decorators or similar Python affordances are the code syntax direction (verbatim: 'I KNEW IT, I knew we had hidden slop and misalignments. those all must be fixed.').
- [operator-ruled] File the ten reviewed GHI groups (verbatim: 'yes, let's go with those').
- [agent-chose] Re-extracted the JFMM and TUM text fresh from the PDFs rather than reuse an earlier session's scratchpad.
- [agent-chose] Restarted the Design by Contract research limited to quoted excerpts after the first attempt hit a content filter while transcribing a copyrighted paper.

## Immediate Next Steps

1. Resume docs/rnd/contractor-kit.md through gz-rnd: append a decision entry with the operator's words, check the record against git, and recompute the frontier from the subject.
2. Put the mode contract's syntax: the candidate Python affordances for code controls (decorators, typing.Protocol ports, context managers, class registration, entry points), with the census's kinds and the seven chore --self-test arms read first.
3. Put the ADR admission question on the permanent mode-contract design requirement (hard to reverse, surprising without context, a real trade-off), and the open mode-contract items: who determines an inoperative control is no hazard (91.213(d)(4)) and where profound modification starts.
4. Put the remaining proposed matrix rows one at a time (C5, C10, C11, C12, C13, B1, B11, C1), then the GHI-system and pipeline subjects.
5. Close: the kit's RO number, the audit chore's shape, disposition rows 1 and 6, the restated challenge, review.md, and sign-off (kill or fund).

## Pending Work / Open Loops

- GHIs #1271 to #1280 are filed but not worked. #1273 is the MX-system review the operator ordered, and #1263 is its CI-side sibling.
- The matrix rows marked as gaps on the aviation texts must be re-checked against the newly landed widening sources before the review.
- The factory-floor construction-period counterpart (TUM 1.7.6 'ship's construction periods') is an unread hypothesis.
- Disposition row 4 drafts (the permanent requirement into canon and the templates; the C3 marks; the surveillance position) await the operator's go on the row.
- 8900.1 V4C4 and PL-25/34/36 are unretrieved; ask the operator for the PDFs if the repair categories become load-bearing.
- The mx-session lock and the 200-plus hours of MX advisory debt are for the operator to close through gz-mx when the drydock work is done.

## Verification Checklist

- git log --oneline -25 shows the session's docs(rnd) commits ending at the handoff commit, and git rev-list --left-right --count origin/main...HEAD shows 0 0 after the sync.
- gh issue view 1271 (through 1280) shows each issue open with its closure contract.
- grep -n '^## decision · ' docs/rnd/contractor-kit.md | tail -25 lists this session's decisions.
- uv run gz handoff rulings --search 'MASSIVE refactor' returns the booked ruling.

## Evidence / Artifacts

- `docs/rnd/contractor-kit.md`
- `docs/rnd/contractor-kit/vocabulary-matrix.md`
- `docs/rnd/contractor-kit/defect-review.md`
- `docs/rnd/contractor-kit/sources/census-code-controls.md`
- `docs/rnd/contractor-kit/sources/census-model-surfaces.md`
- `docs/rnd/contractor-kit/sources/14cfr91-213-121-628-mel.md`
- `docs/rnd/contractor-kit/sources/faa-mel-guidance-ac91-67-n8900-748.md`
- `docs/rnd/contractor-kit/sources/meyer-design-by-contract.md`
- `docs/rnd/contractor-kit/sources/14cfr-part65-145-gaps.md`
- `docs/rnd/contractor-kit/sources/14cfr91-119-121-maintenance-gaps.md`
- `docs/rnd/contractor-kit/sources/14cfr43-appendices.md`
- GHIs #1271 to #1280; cross-link comment on #1263

## Settled Rulings

1746 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
