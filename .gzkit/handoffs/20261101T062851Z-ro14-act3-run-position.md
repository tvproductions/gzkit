---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T06:28:51Z'
agent: claude-code
session_id: e6f7c004-e0be-471f-b8c4-9c598d5ab239
continues_from: .gzkit/handoffs/20261101T031123Z-ro14-act2-dispatch-defects.md
---

## Current State Summary

RO-14 tranche 1 act 3 is landed in 58ea34d44, CI run 41280153727 green on ubuntu and windows with the full-strength report green. #1203, #1205, #1208 and #1209 are closed after independent review, which refuted two builds and passed the third. gz wp runs and the position on gz wp show replay a run from its ledger rows with no new event and no marker read. The stale rule exists once as marker_time_is_stale. Local gates at the commit: gz check exit 0, gz test 13065 tests OK, behave on the work-package feature, mkdocs strict and ty exit 0, 19 mutants 19 killed.

## Important Context

A run is in flight from commenced until closed, so accepted is still reported. No OBPI run was in flight at the landing. Safe mode suspends OBPI initiation by ruling, and nothing in the launch path refuses one, so the older statement that none can start is a ruling and not a control. OutputFormatter.emit now prints text with markup and emoji off for every verb, and the CLI streams use backslashreplace. read_claim_time in gzkit.lock_manager reads a zoneless claim as UTC for scan and reap alike. The concurrent session of the last handoff has finished, so staging by path is no longer forced. Shift turnover: no tag-out log or work-package register exists yet, so this session read gz obpi lock list and the tail of the passage log; the 39 open discrepancy rows were not walked one by one, and gz wp has a runs verb now, which reports no run in flight here. The mx-session lock is near its TTL, which books and announces and evicts nothing.

## Decisions Made

- [operator-ruled] A work package's run position is a read of the rows its verbs already book, with no new event and gz wp runs answering #1203 (verbatim: "A: Read existing rows (Recommended)").
- [agent-chose] #1205 and #1209 repaired in place, stated in the question ruled above, because the contract's sentence about guarding no run names only RO-12's four preconditions.
- [agent-chose] Escaping fixed at the formatter and the console streams rather than per call site, so the class closes for every verb.
- [agent-chose] Stopped at the second fix cycle: the two lock defects the third review named are outside #1205's boundary and are booked as a discrepancy, and the fresh-project defect is booked as blocking return to service, not repaired here.

## Immediate Next Steps

1. Rule on the fresh-project discrepancy: gz init writes no data/catalog, so gz wp new and gz wp runs exit 1 there and the sea trial cannot run on a fresh install.
2. Act 4: #1206 and #1028, with #1028's stop-and-ask boundary.
3. Act 5: acceptance on the work package, which gives the block its refutation count.
4. Act 6, the airlock on the work package, #1185, then act 7, gz wp withdraw-legacy.
5. File the rebase trap and the cwd-escape guard through ghi-author.

## Pending Work / Open Loops

New discrepancies in the contract: the fresh-project catalog gap (blocks return to service), two malformed lock files that still stop gz preflight (due with RO-12's tag-out log), and the OBPI reader and record_dispatch gaps left until tranche 3 removes gz obpi. #1200 stays open for tranche 2 and the advisory score. #1194 stays a direct fix in place. The operator still owes a look at the Mermaid drawing, which now opens at line 86 of the contract, and a ruling on the same-subject arming clause if they disagree with it. #1208 [settled] closed by reading its exit condition on the successor, flagged on the issue for the operator.

## Verification Checklist

Run gh run view 41280153727 and read each job. Run uv run gz wp runs and expect no run in flight. Run gh issue view 1203 and the other three closed issues. Run uv run gz check after git add.

## Evidence / Artifacts

`docs/governance/harbor-ro14-obpi-forward-migration.md`
`docs/user/manpages/wp-runs.md`
`src/gzkit/work_package_run.py`
`src/gzkit/pipeline_markers.py`
`src/gzkit/lock_manager.py`
`tests/commands/test_wp_runs.py`
`tests/test_stale_marker_rule.py`

## Settled Rulings

1912 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
