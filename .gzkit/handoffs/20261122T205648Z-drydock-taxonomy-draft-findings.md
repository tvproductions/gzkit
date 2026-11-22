---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-22T20:56:48Z'
agent: claude-code
session_id: e870dccc-bfdb-48be-baa8-a327a1e81cb8
continues_from: 20261122T150821Z-ghi-1338-provider-rule-bookmark-folded.md
---

## Current State Summary

This session worked the predecessor's steps, ran one R&D run to sign-off, fixed two guards, and stopped repair order 5 of RP-12 from opening when it found the drydock's work and repair taxonomy has no single home and does not match its own records. The taxonomy is drafted for the operator's rulings; none is ruled.
- RP-12 O4's Gate 5 attested (operator: "Proceed: O4 attested"), recorded in the contractor kit under ruling 165 (f7f055eab).
- Predecessor step 3 traced: the pre-push gz check does not run in the drydock (`gzkit.mx.alarms` skips it and exits 0); pre-commit prints "Passed" because it hides a passing hook's output. Neither the hook nor the skill was stale; the finding became the R&D below.
- GHI #1339 (the ledger guard passed when git failed, or under color.diff, diff.external or textconv) fixed in 4fda55e8b, 88a650164 and 0b32c54f1, reviewed and closed. GHI #1340 (the authorship guard read git config, not the identity a commit stamps) fixed in ea16c67a0 and 4e8a9fba3, reviewed and closed.
- R&D docs/rnd/check-outcome-reporting.md signed off and funded (operator: "1. fund; 2. approve"); row 2 filed as #1341, #1342 and #1343, with evidence comments on #1154 and #1224 and #919's ruling answered.
- The work and repair taxonomy drafted at docs/governance/drydock-taxonomy.md (dd6cc87cc): eleven decisions T1 to T11, none ruled.

## Important Context

- WHY THE TAXONOMY DRAFT EXISTS. Opening RP-12's repair order 5, the agent called it "RP-12's repair order 5", and the operator asked whether that was canon. Measured on 2026-11-22: requirements-model.md section 12's level table is canon (epic: feature package or return to service package; story: work package or repair package; order: work order or repair order, where Gate 5 sits; action: task). But data/catalog/work_packages.json holds one package (WP-01-astral-toolchain, closed) and data/catalog/orders.json holds none; the ledger has no order events. RP-0 to RP-15 and RP-12's O1 to O9 exist only as contract and kit prose (kit ruling 165: "O1 to O9 are this page's build orders, not ledger orders"), and O1 to O4's Gate 5s are dated prose on the kit page. The operator, verbatim: "if this isn't documented in one place, we are in trouble already"; "this is part of the drydock work and if it is still in "vibe" territory, we have real problems of the urgent kind"; "this is a HIGH CONSEQUENCE document and decision set, this is meant to bring sanity out of the dry dock - high priority".
- THE FINDINGS the draft records, each sourced there:
  (1) The id history: WO retired 2026-10-16 ("retire it, work package everywhere"); one WP-<NN>-<slug> series for both kinds, kind in a field (RO-5 ruling 6, 2026-10-25, "A"); RP-n replaces RO-n in live text, RO-n an alias, record id staying WP (2026-11-03, "A"); orders ORD-<NN>-<slug> for both kinds, with WO-<NN>-<slug> rejected because WO was retired and "a retired code is never reused" (RP-12 ruling 43, 2026-11-05, "a").
  (2) The operator now prefers kind-spelled names, verbatim: "since when did we make those only WP and ORD? if so, that is not good. I am happy for RP/RO and WP/WO, let's review and discuss." That reverses rulings 6 and 43 if adopted. Two collisions follow: RO-n already names repair packages (RO-9 is WP-01), and WO-1 to WO-11 are retired work-package rows.
  (3) The identity seam (src/gzkit/core/models.py IdKind) knows only ADR, OBPI, REQ and TASK; WP, ORD, TAG, ENT, DSC and dispatch ids are defined in src/gzkit/models/catalog.py and src/gzkit/events.py; RP-n and RO-n resolve nowhere (#1302, open).
  (4) The return to service package has no id, record, event or verb; the feature package's id is "to be named when its store lands".
  (5) Family codes were recoded to three letters on 2026-10-30 (X AIR, H SES, C CTL, M MNT, P PKG, D DEC, R RQW, G GAT, A ATT, L LED, Q QUA), but data/catalog/families.json still holds single letters and OUTCOME_CODE_PATTERN accepts one letter.
  (6) The contract's section Repair orders is headed "Order" and lists repair packages; safe-mode-doctrine.md:67 says "Each order is a repair package named RP-n"; its line 52 keeps a superseded lead.
- THE OPERATOR'S DIRECTION for what comes next, verbatim: "no, we aren't ready to rule yet, I need to clear context and resume. we'll review ALL of the taxonomy (make sure it is thorough and exhaustive), and then settle this, finally and once-and-for-all." No ruling on T1 to T11 is to be put before the draft is made exhaustive and reviewed whole.
- THE DRAFT IS NOT YET EXHAUSTIVE. It covers levels, record ids, drydock record ids, short names and the closed sets in events.py. Not yet gathered: the drydock vocabulary (drydock, hangar, out of service, dock trial, sea trial, handback, transfer of custody, change order, MEL, standby level); the control roles from the census (safeguard, tripwire, gate, monitor, alarm); the personas (craftsman, QAI, coordinator, surveillant); the RP-n specification pages' own sub-units (tranches, acts, rows); requirement kinds and REQ specializations; gates, lanes and ADR kinds; ledger event names; R&D entry kinds and disposition states; insight types; GHI labels; chore names; receipt and run ids (arb-, run ids); handoff and ceremony file names; the hexagon package map's parts; the contract's terms crosswalk and the kit's crosswalk JSON if present.
- Repair order 5 of RP-12 is not opened. The operator corrected the agent for putting a point question before the order's whole plan (verbatim: "if not, then you are vibe coding"; insight scope rp12-o5). When it opens, its full task cut comes first. It lands witness-floor rows 4, 10 and 14 (rulings 11 to 13, 32), and row 14 gates the change order the check-outcome R&D proposes for RP-13.
- The provider rule now stands in gz-session-handoff: a handoff says what gzkit expects of a provider repository, never its issue numbers (GHI #1338).
- Shift turnover, hangar open: gz wp tag show --all reads no tag issued; gz wp runs reads no work package in flight; findings awaiting buy-back are read from the contract's section List of discrepancies (unchanged this session) and gz obpi lock list (mx-session ACTIVE, 1242 of 1440 minutes at 2026-11-22T20:56Z, so the lease lapses near 2026-11-23T00:14Z). The buy-back record is not built.

## Decisions Made

- [operator-ruled] Proceed with the predecessor's next steps (verbatim: "proceed with next steps").
- [operator-ruled] RP-12 repair order O4's Gate 5 (by selection: "Proceed: O4 attested").
- [operator-ruled] No safe-mode-only exception is added to make a switched-off check visible (verbatim: "why would we introduce safe mode exceptions? that is going to get out of control and lost very quickly.").
- [operator-ruled] Fix the ledger and authorship guards, then run the R&D (verbatim: "fix the two guards now, then run the R&D").
- [operator-ruled] Close each GHI only once its review confirms (verbatim: "close it when the review confirms").
- [operator-ruled] Complete the R&D, then move to RP-12's repair order 5 (verbatim: "complete the rnd and move to RP-12/RO-5").
- [operator-ruled] The check-outcome-reporting R&D signed off, with row 2's go (verbatim: "1. fund; 2. approve").
- [operator-ruled] A repair order opens with its whole plan laid out before any point question (verbatim: "if not, then you are vibe coding").
- [operator-ruled] Land the taxonomy as a draft first (verbatim: "land it as a draft first.").
- [operator-ruled] The taxonomy is reviewed whole and made exhaustive before any ruling (verbatim: "no, we aren't ready to rule yet, I need to clear context and resume. we'll review ALL of the taxonomy (make sure it is thorough and exhaustive), and then settle this, finally and once-and-for-all.").
- [agent-chose] Left the committed handoff 20261122T051329Z's false settled marks as the defect's record, pending the operator's ruling.
- [agent-chose] Recorded the operator's sign-off words without claiming an explicit statement that the review was read, since the reply gave none.

## Immediate Next Steps

1. Renew the mx-session lease through the gz-mx skill before it lapses near 2026-11-23T00:14Z.
2. Make docs/governance/drydock-taxonomy.md exhaustive before any ruling: gather every term and identifier the Important Context names as not yet gathered, each read from its source, and mark each ruled, sourced, contradicted or unsourced.
3. Walk the operator through the whole taxonomy, then put T1 to T11 (and any decision the exhaustive pass adds) one at a time, recording each ruling with its options and verbatim words in the page's section 8.
4. Route what the rulings produce through the drydock's own procedure (contract amendment, change order or GHI), before RP-12's repair order 5 opens.
5. Ask the operator whether the false settled marks in the committed handoff 20261122T051329Z are corrected or kept as the defect's record.

## Pending Work / Open Loops

- RP-12's repair order 5 waits for the taxonomy rulings; when it opens, its task cut comes first (witness-floor rows 4, 10 and 14).
- The check-outcome-reporting R&D's row 1, a change order on RP-13 adding the outcome contract to its foundation tranche, awaits the operator's issue; its row 7 research (outcome vocabularies of JUnit XML, TAP and SARIF, and their standards status) opens with RP-13.
- GHI #1341, #1342 and #1343 are open under that R&D, owned by RP-13; GHI #1302 (RP-n and RO-n names do not resolve) bears on the taxonomy's T4.
- The contract's list of discrepancies carries five O4 lines due by the sea trial; four hexagon test findings join ruling 104's line under ruling 125.
- OBPI-0.35.0-20 reads PENDING; its completion attestation must name reworded rows S2-062, S2-064, S2-067, S2-074 and S2-080.
- GHI #1337 and GHI #1331 stay open.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz obpi lock list reads mx-session ACTIVE, renewed if the session runs past 2026-11-23T00:14Z.
- docs/governance/drydock-taxonomy.md reads DRAFT, with section 8 Rulings empty.
- data/catalog/work_packages.json holds WP-01-astral-toolchain alone and data/catalog/orders.json holds no order, unless a ruling has changed them.
- gh issue view 1339 and 1340 read CLOSED; 1341, 1342 and 1343 read OPEN.

## Evidence / Artifacts

- `docs/governance/drydock-taxonomy.md` — the draft taxonomy, T1 to T11 (dd6cc87cc)
- `docs/rnd/check-outcome-reporting.md` — the R&D record, signed off and funded
- `docs/rnd/check-outcome-reporting/review.md` — its review account
- `docs/rnd/check-outcome-reporting/sources/population-read-2026-11-22.md` — the 15-issue population, verbatim
- `docs/governance/harbor-ro12-contractor-kit.md` — O4's Gate 5 section (f7f055eab)
- `src/gzkit/hooks/guards.py` — the ledger guard fix (GHI #1339)
- `src/gzkit/governance/trust_audits/authorship.py` — the authorship guard fix (GHI #1340)
- `docs/governance/ieee/requirements-model.md` — the canon level table, section 12
- `.gzkit/insights/agent-insights.jsonl` — scopes check-reporting, drydock-formalism, rp12-o5, rnd-check-outcome-reporting

## Settled Rulings

2463 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
