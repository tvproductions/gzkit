---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-31T11:40:23Z'
agent: claude-code
session_id: 63a4e8a8-02b8-40ae-be37-ff789c2cc4bc
continues_from: .gzkit/handoffs/20261031T094947Z-resume-delta-folded-rulings-seated.md
---

## Current State Summary

Drydock safe mode, RO-14 tranche 1 act 1 landed. The operator ruled that nothing stays live in OBPI; the session amended the contract with RO-14 and exit item 12 and specified it in docs/governance/harbor-ro14-obpi-forward-migration.md. Act 1, the fix-cycle bound of GHI #1200 on gz wp dispatch, block and unblock, landed at 825e76198 after three builds failed independent review and the fourth passed. #1200 stays open: its exit condition has the pipeline's sentence name the mechanism, and the pipeline moves in tranche 2. Evidence: 194 affected tests, mutation sweep of 48 mutants with 38 killed, 10 inconclusive and 0 survived, gz check exit 0. Last action: this handoff and the sync.

## Important Context

Read the RO-14 specification first: its rulings, its Known limits of act 1 and its acts. RO-12's four pipeline preconditions moved to tranche 1, because a repair to gz obpi guards no run. The bound counts against a frozen subject, REQ-<n>@<rev> or #<issue>, across packages. Reviewers worked by reading only and failed real builds three times, finding routes that 26 passing tests missed; keep sending runtime changes to an independent reviewer, and see each test fail. The mutation sweep needs unittest -v and nominated ids, and a mutant that fails by error reports inconclusive, which is not a kill. Text search on a Python-looking word trips the LSP hook; repeat the command to pass it. Pushing in quick succession cancels CI runs, and full-strength-report can be red while the run reads success, so read the job list; f02ea21f9 failed it on two planned verbs with no skip marker, fixed in ae007ce92. A path-limited git commit lands a doc alone from a staged tree, and a plain commit also takes whatever else is staged. Shift turnover: read the contract's list of discrepancies, passage log and gz obpi lock list; only mx-session is held, no tags are hung because the tag-out log does not exist until RO-12, no finding awaits buy-back, and no work package is commenced. Workflow fronts (docs/governance/build-to-1.0-campaign-2026-09-20.md#workflow-fronts): this session worked the adr/obpi campaign front through the drydock and the handoff system front; ghi triage and new R&D were not worked beyond #1200.

## Decisions Made

- [operator-ruled] Nothing is retained in OBPI; it all forward migrates to WP (verbatim: "we shouldn't be retaining anything in obpi, it all needs to forward migrate to wp, discuss").
- [operator-ruled] Everything live moves, gz obpi is removed, and history stays as read-only record through the alias layer (verbatim: "A").
- [operator-ruled] The migration is RO-14, a new order by contract amendment, in three tranches with an exit item (verbatim: "a").
- [operator-ruled] One runtime, with the package's kind selecting the procedure (verbatim: "A").
- [operator-ruled] #1200 is a direct fix, not ruled into OBPI-0.35.0-18 (verbatim: "a").
- [operator-ruled] At the bound there is no further repair cycle; an unblock names an exit (verbatim: "a").
- [operator-ruled] The changed-requirement exit is usable once per requirement (verbatim: "A").
- [operator-ruled] An escalation may carry a recommendation beside facts the runtime writes (verbatim: "a").
- [operator-ruled] The single-driver route splits by kind (verbatim: "a").
- [operator-ruled] The exit baseline has one seam, a single alias module (verbatim: "a").
- [operator-ruled] The operator and a working session move the pipeline itself; the rest of tranche 2 and tranche 3 run under the kit (verbatim: "a").
- [operator-ruled] The exits fit the freeze rules: reopen, departure, hold, terminate, the once-only limit crossing packages (verbatim: "a").
- [operator-ruled] Tranche 1's names: gz wp dispatch, block, unblock and withdraw-legacy, with their work_package_ and legacy_unit_withdrawn events (verbatim: "a").
- [operator-ruled] The bound counts against the frozen subject (verbatim: "a").
- [operator-ruled] The count follows the REQ at its revision across packages (verbatim: "a").
- [operator-ruled] A subject's first dispatch is free and any review in the package arms every started subject (verbatim: "a").
- [operator-ruled] A hold stops only the subjects at the bound (verbatim: "a").
- [agent-chose] A review of a subject arms it in any package, read from ruling 15; it only tightens the bound and neither ruling states it, so the operator is told.
- [agent-chose] gz wp attach refuses a frozen package, because its issues are subjects the bound counts against.
- [agent-chose] The successor to gz obpi withdraw belongs to tranche 1, so RO-8's withdrawal does not hold gz obpi open; it is act 7 and is not built.
- [agent-chose] Settled four open points from the record rather than asking; the one on what a run is was later amended by rulings 12 and 15.

## Immediate Next Steps

1. Tranche 1 act 2: read #1198 and #1208 against gz wp dispatch and repair or close what the move already answered.
2. Act 3: run position and markers, #1203, #1205 and #1209.
3. Act 4: #1206 and #1028, with #1028's stop-and-ask boundary.
4. Act 5: acceptance on the work package, which gives the block its refutation count.
5. File the rebase trap and the cwd-escape guard through ghi-author, and ask the operator to look at the Mermaid drawing that opens at docs/governance/harbor-pilotage-candidate-2026-10-15.md line 83.

## Pending Work / Open Loops

- #1200 stays open until tranche 2; its same-root rule is owed an advisory score in docs/governance/advisory-rules-audit.md.
- The block carries no refutation count until act 5, a discrepancy line due by that event.
- The reopen exit is unchecked against a reopening until RO-5's tranche 6, which also lands the freeze lock.
- The Known limits of act 1 stand, including false labels, hand edits and a subject with no review.
- The handoff skill's three-level specification is unwritten, waiting on the operator's word.
- The pre-commit-stash defect is held as an insight; gz arb red on 759d1355e read undriven.
- Read docs/rnd/contractor-kit/sources/pipeline-regressions-2026-10-25.md before tranche 2 moves the pipeline; this session did not read it.
- #1272 and #1289 stay with RO-13's F5; RO-13's T0 tables are undrafted; RO-4 ruling 6 against RO-8 ruling 1 remains open.
- The orientation hook output is over its injected-text budget.
- The MX session has carried advisory debt past its lease.

## Verification Checklist

- git status -sb reads main in step with origin/main.
- gh run view on the run for 825e76198 shows check and full-strength-report, read job by job.
- uv run gz wp dispatch --help shows the --req and --issue flags.
- uv run -m unittest tests.test_work_package_run passes.
- uv run gz handoff rulings --search 'frozen subject' returns the ruling.
- uv run gz obpi lock list shows the mx-session lease.

## Evidence / Artifacts

- `docs/governance/harbor-ro14-obpi-forward-migration.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-contractor-brief.md`
- `src/gzkit/work_package_run.py`
- `src/gzkit/work_package_ledger.py`
- `tests/test_work_package_run.py`
- `tests/commands/test_wp_run.py`
- `docs/user/manpages/wp-dispatch.md`
- Commits aa40500ff through 825e76198 on main.

## Settled Rulings

1911 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
