---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T12:29:07Z'
agent: claude-code
session_id: 1bea2c5b-f75b-4511-bd03-991ecab8d39a
continues_from: .gzkit/handoffs/20261101T095404Z-ro14-act4-closed-ro15-added.md
---

## Current State Summary

RO-14 act 5 is landed in 76be66047: acceptance runs on the work package through gz wp acceptance, on the same store and reducer as the pipeline. gz wp accept refuses until the reducer reads ready, three adversarial rounds with a mapped finding stop gz wp dispatch and gz wp accept and name gz wp block, and the block carries refutations per subject. CI for 76be66047 was still running when this handoff was written, so read it before closing #1028, which stays open until that run is green. The operator confirmed the general arrangement's six flows. Act 6 has not been started.

## Important Context

A package supplies the contract a brief supplies, through acceptance_package.package_contract, so proofs, reviews, closures and readiness run unchanged. resolve_brief is the seam. A delivery package owes its frozen REQs less any a departure moved out; a repair package owes one obligation per carried issue. Issues and catalog REQs bind by killing mutants, because neither has the @covers scan. load_history scopes departed REQs out in one place; refutation_counts alone reads the unscoped _replay_history, so a departed REQ's refutations stay facts. Reviews are always recorded past the limit: the bound stands at dispatch and accept, never at import. A review round is an adversarial review with a mapped finding, not the verdict token. The limit is 1 + MAX_REVIEW_FIX_CYCLES, so N=2 lives in one place. An unblock or a human-review restarts the count. A package stopped by reopen or terminate is excused at gz wp accept and cannot close as proceed unless acceptance reads ready. OBPI acceptance is unchanged, except that its digest no longer reads data/catalog/work_packages.json. Lessons from three refuted builds: hand-built proofs hid that a catalog REQ could not be proved, so tests must run the real prove, and a hand-written departure row hid dead ends, so tests must go through the real verbs. gz lint --ratchet lowers the Ruff baseline when a held finding goes. Shift turnover: no tag-out log or work-package register exists, so this session read gz obpi lock list and the contract's discrepancy list; no tag was hung; no run is in flight. The mx-session lock reads LEASE EXPIRED, which announces and evicts nothing, and the hangar stays open.

## Decisions Made

- [operator-ruled] The general arrangement's six flows are confirmed and act 5 proceeds (verbatim: "yes, those match, proceed with act 5").
- [operator-ruled] Act 5 adapts the existing pipeline rather than building anew (verbatim: "we will adapt, as much as possible, the current gz-obpi-pipeline").
- [operator-ruled] At the spent fix bound, act 5's count was fixed and it landed (verbatim: "Fix the count, land (Recommended)").
- [agent-chose] Read the operator's direction to adapt the pipeline as meaning acceptance gates gz wp accept, as it gates completion today, stated to the operator before building.
- [agent-chose] Bound proofs of issues and catalog REQs to the mutation sweep rather than widening the @covers scan.
- [agent-chose] Opened --exit terminate on any block, widening ruling 12, because the round limit can stop a package with no subject at the fix-cycle bound; recorded on the discrepancy list for the operator's ruling.
- [agent-chose] Let human-review restart the round count with no block row; recorded on the same list for the operator's ruling.
- [agent-chose] Refused proceed at close on a stopped package whose acceptance does not read ready.

## Immediate Next Steps

1. Read 76be66047's CI run; if it is green, close #1028 with its evidence and flag that it closed on the successor, and that its observed comparison and the Stage 4 text move with tranche 2.
2. Rule on the two agent choices on the discrepancy list: terminate open on any block, and human-review restarting the round count.
3. Act 6, the airlock on the work package, #1185.
4. Act 7, gz wp withdraw-legacy.
5. File through ghi-author: the brownfield build break, the rebase trap and the cwd-escape guard.

## Pending Work / Open Loops

Act 5's residue is on the contract's discrepancy list under RO-14: a carried issue is always a BEHAVIOR obligation, so a docs or chore issue has no honest proof; catalog STRUCTURAL-FENCE REQs cannot be proved and a SUPPORT REQ needs a witness clause in its statement; the refutation count reads one package; a package whose every REQ departed leaves by terminate; a review begun before a departure and imported after is refused whole; no gz wp verb composes a reviewer frame; gz wp acceptance prove --spec is unexercised through the verb. The fence's residue is there too. RO-15's two blocking discrepancies stand, and its open points remain: tranche owner, exact-patch .python-version in a scaffold, hashes in build-constraint-dependencies. gz init scaffolds nine Ruff families and leaves an existing project's Ruff config alone, which needs a home. The sea trial has not created a work package on a fresh project. The reconcile-receipt and plan-audit gates stay with tranche 2. The operator may reopen #1206 [settled] or #1208 [settled]. #1200 stays open for tranche 2 and the advisory score; #1194 stays a direct fix in place. MX debt keeps aging until gz mx exit.

## Verification Checklist

Run gh run list --commit 76be66047 and read each job. Run gh issue view 1028 and read its last comment. Run uv run -m unittest tests.commands.test_wp_acceptance tests.commands.test_wp_fence. Run uv run gz wp acceptance --help. Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0.

## Evidence / Artifacts

`src/gzkit/acceptance_package.py`
`src/gzkit/acceptance_store.py`
`tests/commands/test_wp_acceptance.py`
`docs/user/manpages/wp-acceptance.md`
`docs/governance/harbor-ro14-obpi-forward-migration.md`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`

## Settled Rulings

1922 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
