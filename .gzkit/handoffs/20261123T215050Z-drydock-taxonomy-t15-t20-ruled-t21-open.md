---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-23T21:50:50Z'
agent: claude-code
session_id: 44e42489-eff4-4b65-88ff-2c7ab99fc662
continues_from: .gzkit/handoffs/20261123T105743Z-drydock-taxonomy-walk-t1-t14-ruled.md
---

## Current State Summary

Drydock taxonomy walk resumed from the predecessor (booked proceed). T15, T16, T18, T19 and T20 ruled as W39 to W43 in docs/governance/drydock-taxonomy.md section 9; T17 recorded settled by canon (out of service is one state, the two levels being the defect GHI #1304 owns). Each ruling committed and synced on its own (050f99b56, 8da4211d7, e94731816, e61a65e48, 957391459, 159951aa0). T21 was put with options and the operator deferred it to this handoff: pick up exactly at T21. Before the walk the session renewed the MX lease (6c1213f66), booked the no-Task-trailer ruling for lease renewals, and ran the GHI #1356 test-suite survey (three read-only surveyors, partial sweep), booking three results comments and two rulings on the issue.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; the contract freezes the drydock scope at induction, so findings are graded, never added as new orders. The operator ruled one decision per question for the rest of the walk ("one-at-a-time please"): do not batch, even naming rows. T21 is a mechanism row: RP-13 rulings 5 and 8 key MEL defaults on a control role label, and alarm and tripwire mean opposite things in the census (census-code-controls.md:66-71, never ruled) and in RP-10 (in force, followed by the doctrine alarm test and gzkit.mx.alarms). The two schemes classify on different axes: the census by purpose in normal operation, RP-10 by behaviour while out of service. The ledger ADR-0.40.0 is an unrelated March ADR; the amendment ADR was only planned at that number. Shift turnover: gz wp tag show --all reports no tag issued, gz wp runs reports no work package in flight, and the only lock is mx-session held by the MX session; the buy-back record is unbuilt, so the contract list of discrepancies stands in.

## Decisions Made

- [operator-ruled] Renew the MX lease (verbatim: "renew lease").
- [operator-ruled] No Task: trailer on MX lease-renewal commits for now (verbatim: "no, we don't want that for the mx lease just yet, or is that specified somewhere?").
- [operator-ruled] Test-suite survey as a read-only exploration, filed as a GHI with results booked against it (verbatim: "A, but GHI it, then we'll book results against the GHI.").
- [operator-ruled] GHI #1356 deferred findings are held by the decommission-tautological-tests chore, widened to all three classes (verbatim: "A").
- [operator-ruled] The chore widening waits until after the drydock (verbatim: "no, we should not disrupt drydock.").
- [operator-ruled] Resume the predecessor handoff at step 1 (verbatim: "proceed with step 1 (we had to create a handoff mid-task)").
- [operator-ruled] W39, T15: the GHI sense of work order retired; a GHI carries a problem report (verbatim: "A").
- [operator-ruled] W40, T16: a squawk is one reported discrepancy and the GHI its write-up (verbatim: "A").
- [operator-ruled] W41, T18: the letters A to D are the check levels; a visit is named by its subject (verbatim: "A").
- [operator-ruled] W42, T19: the catalog absorbs the amendment and AMD- retires unbuilt (verbatim: "A").
- [operator-ruled] W43, T20: a supplement is a new package record naming its parent (verbatim: "A (why is this important? are we being too pendantic?)").
- [operator-ruled] Taxonomy decisions one at a time, no slate (verbatim: "one-at-a-time please").
- [operator-ruled] T21 deferred to a fresh handoff, picking up there (verbatim: "defer this to a fresh handoff (pick up right here) and git sync.").
- [agent-chose] Recorded T17 as settled by canon without a question, on the T8 precedent.
- [agent-chose] Corrected the T19 row claim that ADR-0.40.0 carries AMD- in the same commit as W42.

## Immediate Next Steps

1. Put T21 to the operator again: alarm and tripwire keep RP-10 senses; the census role set stays the MEL role field with its colliding names renamed (proposed interlock for the census tripwire, annunciator for the census alarm), so a MEL entry carries a role and an out-of-service behaviour (option A, recommended); B the census senses win; C drop the census role set. Record the ruling as W44 in section 9 and mark the row in section 8.
2. Continue in table order, one decision per question: T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T39, committing after each ruling.
3. Renew the MX lease through the gz-mx skill on the operator word before it lapses near 2026-11-24T18:21Z.
4. When the rulings are done, draft the execution plan: the contract amendment and the per-package revisions T10 (W35) routes, in an order the operator rules; then open the documentation R&D run through gz-rnd (W15).
5. Ask the operator whether the false settled marks in the committed handoff 20261122T051329Z are corrected or kept as the record of that defect (carried from the predecessor).

## Pending Work / Open Loops

Unruled naming rows drafted in this session as a slate the operator declined to batch; the draft recommendations, to be put singly: T22 RP-12 maps persona files to positions in the crosswalk data and the reviewer position is inspector with spec and quality sub-roles (the SingleDriver unreachable arm is GHI #1353); T23 the side is construction and its package the work package, store kind delivery renamed work, the maintenance visit not a third kind; T28 the passage log closed as a dated record, the maintenance record its successor, no backfill; T30 page file names kept, every sub-id cited with its package prefix, RP-0 specification is the contract; T31 one qualification rule, record-level senses win; T32 supersession recorded forward through --settled, never by editing rulings.jsonl; T33 pool entries take a record id such as POOL-nnnn-slug with ADR-pool.slug as alias (the POOL prefix is the agent proposal, not canon); T35 the no-separate-document rulings and the feature package declared compatible; T37 page-scoped ruling numbers stay citations, not records. GHI #1356 stays open as the record of the survey findings; its unswept parts are the widened chore first sweep after the drydock. GHI #1304 owns the two-level marker and banners (T17).

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- grep -n "W43" docs/governance/drydock-taxonomy.md shows the T20 ruling and grep -n "| T21 |" shows the row still unruled.
- uv run gz handoff rulings --search "W43" returns the supplement ruling.
- gh issue view 1356 --comments shows the three survey results and the two holder and timing rulings.
- uv run gz obpi lock list shows the mx-session lock and its ttl.

## Evidence / Artifacts

- `docs/governance/drydock-taxonomy.md`
- `.gzkit/insights/agent-insights.jsonl`
- `.gzkit/handoffs/20261123T105743Z-drydock-taxonomy-walk-t1-t14-ruled.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/rnd/contractor-kit/sources/census-code-controls.md`
- `docs/governance/harbor-ro10-safe-mode-classification.md`
- `docs/governance/harbor-ro13-mode-contract.md`

## Settled Rulings

2515 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
