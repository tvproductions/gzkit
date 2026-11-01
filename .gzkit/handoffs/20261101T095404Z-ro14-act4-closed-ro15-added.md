---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T09:54:04Z'
agent: claude-code
session_id: 1bea2c5b-f75b-4511-bd03-991ecab8d39a
continues_from: .gzkit/handoffs/20261101T063122Z-ro14-act3-closed-act4-next.md
---

## Current State Summary

RO-14 act 4 is closed on #1206 and RO-15 is added. The fresh-project discrepancy is cleared in ed6a324be: gz init and its repair path seed each absent data/catalog file with the cutover stamped at seeding, CI run 41282849165 green. RO-15, maximal Astral project structure, entered the contract by amendment in 99b0657e7 and b845ec244, placed immediately before RO-4, with exit item 13 and two discrepancy lines blocking return to service. The work-package fence landed in 00b046160, CI run 41292226655 green, and #1206 is closed. #1028 moved to act 5 in a8014abbf, whose CI was not read in this session. Act 5 has not been started.

## Important Context

Astral's uv project docs are RO-15's authority and gz-skills-first-starter is the worked reference; its acceptance rows A01 to A18 and worked migrations are what proof looks like. gzkit's own rulings stand against the starter: uv as a floor, each fact declared once, Ruff ALL with preview. Measured: gz init broke a flat setuptools build, uv build going from exit 0 to exit 2, because it adds data/ and design/ beside the package; in a scaffold, uv run gz resolved to ~/.local/bin/gz because gz is not in the project's lock. The fence reads the ledger alone, in gzkit.work_package_fence, through the pipeline-gate hook and the post-authoring-src-commits guard. The commit arm is on in safe mode; the write arm is advisory. Independent review refuted three builds of the fence, each for a reason worth knowing: a subject at the bound cannot be fenced because the ledger shows the same rows while the last admitted cycle runs and after it ends, and the count follows a subject across packages under ruling 15. Act 5 must read that before it builds a round bound. The hook template is a plain string, so an escape in it must be doubled. Shift turnover: no tag-out log or work-package register exists, so this session read gz obpi lock list and the contract's discrepancy list; no tag was hung; gz wp runs reports no run in flight. The mx-session lock reads LEASE EXPIRED, which announces and evicts nothing, and the hangar stays open.

## Decisions Made

- [operator-ruled] A fresh project gets its catalog from gz init (verbatim: "Seed at gz init (Recommended)").
- [operator-ruled] Project structure is a repair order (verbatim: "the reason I wanted you to look at that starter is because it adopts/assumes maximal python project structuring via astral's recommended best practices. I consider that RO worthy."), to the standard of uv's project docs (verbatim: "maxx: https://docs.astral.sh/uv/concepts/projects/" and "gz-starter maximizes this, we should too/").
- [operator-ruled] gz init on an existing project reports gaps and never refactors or breaks a build, and adoption stays incomplete until a governed migration passes (verbatim: "Report, then prove (Recommended)").
- [operator-ruled] RO-15 sits immediately before RO-4 (verbatim: "agree").
- [operator-ruled] #1206 is repaired by a fence on the work-package surface (verbatim: "Fence on the WP surface (Recommended)").
- [operator-ruled] At the spent fix bound, the bound state was dropped and the fence landed (verbatim: "Drop bound state, land (Recommended)").
- [operator-ruled] The #1028 hold lifts for this purpose only and its remainder moves into act 5 (verbatim: "Lift, fold into act 5 (Recommended)").
- [agent-chose] Stamped the catalog cutover at seeding rather than copying gzkit's date, so a repaired project's earlier delivery events stay legacy.
- [agent-chose] Added the stopped state to the fence beyond the two states first ruled, stated to the operator in the exit question they ruled on.
- [agent-chose] Closed #1206 on the successor and flagged on the issue that the operator may reopen it, and that the last two corrected sentences were not re-read.

## Immediate Next Steps

1. Read a8014abbf's CI run and confirm it is green.
2. Act 5: acceptance on the work package, giving gz wp block its refutation count and carrying #1028's exit and runtime bound at the ruled N=2, with its stop-and-ask boundary.
3. Act 6, the airlock on the work package, #1185, then act 7, gz wp withdraw-legacy.
4. File through ghi-author: the brownfield build break, the rebase trap and the cwd-escape guard.
5. Rule RO-15's open points when it is reached: tranche owner, exact-patch .python-version in a scaffold, hashes in build-constraint-dependencies.

## Pending Work / Open Loops

RO-15's two blocking discrepancies stand until it runs: gz init breaks a brownfield build, and the Astral scope has no structure rule. The sea trial still has not created a work package on a fresh project: a repair package stops at the gh label check without a remote, and a delivery package was not tried; the contract records that no verb writes outcomes yet. The fence's residue is on the contract's discrepancy list under RO-14, due with RO-12's tag-out log. gz init scaffolds nine Ruff families and leaves an existing project's Ruff config alone, against the RO-9 ruling for all adopters; the operator confined the starter comparison to structure, so this is not in RO-15 and needs a home. The family legend seeded at init describes gzkit's own features. The operator may reopen #1206 [settled] or #1208 [settled]. The operator still owes a look at the Mermaid drawing at line 86 of the contract and any ruling on the same-subject arming clause. #1200 stays open for tranche 2 and the advisory score; #1194 stays a direct fix in place. MX debt keeps aging until gz mx exit.

## Verification Checklist

Run gh run list --commit a8014abbf and read the run. Run gh run view 41292226655 and read each job. Run gh issue view 1206 and read the close comment. Run uv run gz wp runs and expect no run in flight. Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Run uv run -m unittest tests.commands.test_wp_fence tests.test_catalog_seed.

## Evidence / Artifacts

`docs/governance/harbor-ro15-project-structure.md`
`docs/governance/harbor-ro14-obpi-forward-migration.md`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`
`src/gzkit/work_package_fence.py`
`src/gzkit/catalog_seed.py`
`tests/commands/test_wp_fence.py`
`tests/test_catalog_seed.py`

## Settled Rulings

1919 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
