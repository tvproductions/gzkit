---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T06:31:22Z'
agent: claude-code
session_id: e6f7c004-e0be-471f-b8c4-9c598d5ab239
continues_from: .gzkit/handoffs/20261101T062851Z-ro14-act3-run-position.md
---

## Current State Summary

RO-14 tranche 1 acts 1 to 3 are landed. Act 3 is 58ea34d44, CI run 41280153727 green on ubuntu and windows with the full-strength report green; #1203, #1205, #1208 and #1209 are closed after independent review. The session then reported to the operator, who has not yet ruled on the fresh-project discrepancy. Nothing has changed since 3cb989135 except this handoff. No work is in flight and act 4 has not been started.

## Important Context

The predecessor handoff, 20261101T062851Z-ro14-act3-run-position.md, carries the technical detail of act 3. Read it for what changed in gz wp runs, the stale rule, the formatter, the console streams and read_claim_time. The fix-cycle discipline held on act 3 itself: review refuted two builds, the second cycle was the last, and what the third review named outside the issues went to the list of discrepancies. A subagent's reading is not evidence: every code finding was reproduced before it was fixed, and gz wp has no list verb but runs. 3cb989135 touched only .gzkit paths, so it has no CI run of its own. The mx-session lock stands at 1409 of 1440 minutes and will book its expiry at the next read; that announces and evicts nothing, and the hangar stays open.

## Decisions Made

- [agent-chose] Wrote this as a fresh successor rather than amending the last one, on the operator's request, carrying its technical detail by reference.
- [agent-chose] Left act 4 unstarted and made the fresh-project ruling the first step, because it blocks return to service and is the operator's to rule.

## Immediate Next Steps

1. Get the operator's ruling on the fresh-project discrepancy: gz init writes no data/catalog, so gz wp new and gz wp runs exit 1 there.
2. Act 4: #1206 and #1028, with #1028's stop-and-ask boundary.
3. Act 5: acceptance on the work package, which gives the block its refutation count.
4. Act 6, the airlock on the work package, #1185, then act 7, gz wp withdraw-legacy.
5. File the rebase trap and the cwd-escape guard through ghi-author.

## Pending Work / Open Loops

On the list of discrepancies: the fresh-project catalog gap, blocking return to service; two malformed lock files that still stop gz preflight, due with RO-12's tag-out log; the OBPI reader and record_dispatch gaps, until tranche 3 removes gz obpi. #1200 stays open for tranche 2 and the advisory score. #1194 stays a direct fix in place. The operator may reopen #1208 [settled], which closed by reading its exit condition on the successor. The operator still owes a look at the Mermaid drawing at line 86 of the contract and any ruling on the same-subject arming clause. The 39 open discrepancy rows were not walked one by one in this session's turnover.

## Verification Checklist

Run gh run view 41280153727 and read each job. Run gh issue view 1208 and read the close comment. Run uv run gz wp runs and expect no run in flight. Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0.

## Evidence / Artifacts

`.gzkit/handoffs/20261101T062851Z-ro14-act3-run-position.md`
`docs/governance/harbor-ro14-obpi-forward-migration.md`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`

## Settled Rulings

1912 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
