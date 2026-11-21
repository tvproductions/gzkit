---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-21T13:11:10Z'
agent: claude-code
session_id: 524804f1-5554-4dcc-8004-60272ec3b090
continues_from: .gzkit/handoffs/20261121T102345Z-rp12-o4-task4-closed.md
---

## Current State Summary

This session resumed handoff 20261121T102345Z (operator: "proceed as recommended", booked with gz handoff decide) and worked its steps 2 to 4.

- Step 2: CI on e34c5ab7b was red on two task 4 leftovers, LandingCommit missing from ruff's runtime-evaluated-base-classes and a git rev-parse capture in tests/commands/test_wp_entry.py with no errors=; fixed in 4c770b263, and CI run 44896154584 passed check on ubuntu and windows (full-strength-report fails on every green run, the demoted guards' report).
- Step 3: RP-12 O4 task 5 opened. Rulings 195 to 199 were put one at a time and booked in the kit (635af5e4f). Ruling 199's fix landed red first (6e74a3f6d, gz arb red verdict driven, receipt arb-red-commit-6e74a3f6d465-aec9418a1dcc473382c24a0d2eccdf9d). The sweep script landed (593613793) and the carry's rows were amended with a new row for the record's views and the exit's refusals (3b67193f8).
- Step 4: the paused order's terminate exit was put at the opening and ruled as ruling 199.
- The sweep, 574 mutants over 16 files, was launched from the clean tree at 37e8a6ee9 and was still running at authoring, 15 of 16 files done, order_ledger.py last. Operator: "this taking 4 hours is ridiculous".

## Important Context

- The sweep writes docs/governance/harbor-ro12-dock-trial-evidence/o4-sweep-2026-11-21.json only when every file has finished; its per-file counts go to the session scratchpad log, which does not survive. If the run died with the session, the 15 finished files' detail is lost and only the counts quoted below remain.
- First-pass counts (killed/survived/inconclusive): parser_wp_entry 0/0/0, parser_governance 0/12/0, wp_entry 7/3/1, wp_tag 18/1/1, entries 24/1/5, wp_order 27/1/16, git_commits 5/2/5, record_rows 4/0/2, series 1/1/0, tag_out 7/0/2, mx_cmd 5/12/9, log 19/20/13, work_package_ledger 5/0/8, discrepancies 65/3/29, work_package_run 44/30/48. Inconclusive rows are re-run alone before the record is written.
- parser_governance's 12 survivors sit in two helpers of register_governance_parsers, whose only O4 change was registering wp entry; they read as noise from ruling 197's direct helpers.
- This handoff, the insights and the git-sync change tracked files before order_ledger.py's entry is stamped, so that one entry reads +dirty; the swept src matches HEAD.
- MODULES for the carry's files (_CARRY) were chosen by judgement, not read from a row; a module set too narrow shows as survivors, so it makes no false kill.
- Safe mode stays open; shift turnover: gz wp tag show --all reads no tag issued, gz wp runs no work package in flight, gz obpi lock list mx-session ACTIVE at 420m of 1440m.

## Decisions Made

- [operator-ruled] Proceed with the resumed handoff's steps (verbatim: "proceed as recommended").
- [operator-ruled] Ruling 195, O4's dock trial is a red-proof sweep alone (verbatim: "A: Sweep alone (Rec.)").
- [operator-ruled] Ruling 196, the trial takes its two rows and the code tasks 3 and 4 changed (verbatim: "A: Rows + O4's changes (Rec.)").
- [operator-ruled] Ruling 197, those changes selected by the functions they changed (verbatim: "A: Changed functions (Rec.)").
- [operator-ruled] Ruling 198, the trial inspected once, findings closed by red proofs (verbatim: "A: Once, as O3 (Rec.)").
- [operator-ruled] Ruling 199, a paused order's find block takes no exit (verbatim: "A: Refuse it (Rec.)").
- [operator-ruled] Let the sweep finish, then show the survivors (verbatim: "let it finish, then show me the survivors").
- [operator-ruled] Write the handoff and git-sync with the sweep left running (verbatim: "yes, write the handoff and git sync, this taking 4 hours is ridiculous").
- [agent-chose] Relaunched the sweep from a clean synced tree after the first launch would have stamped every entry +dirty from the live ledger.
- [agent-chose] Read a deleted line's neighbour as changed when selecting functions from the diffs; written in the script's docstring, not put to the operator.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide; the mx-session lease lapses near 2026-11-22T06:10Z.
2. Check whether docs/governance/harbor-ro12-dock-trial-evidence/o4-sweep-2026-11-21.json exists. If it does, show the operator every survivor and still-inconclusive row in one plain table, each with what the mutant broke and whether it reads as a gap or as noise, before any further ceremony (operator: "show me the survivors").
3. If it does not exist, fix o4_mutation_sweep.py to write each file's entry as it finishes and print per-mutant progress, then ask the operator whether to re-run it before re-running anything.
4. Run git add -A and uv run gz check over this session's five commits, which ran only the pre-commit hooks.
5. Put to the operator whether the every-branch sweep is worth its cost for O5 onward, each option's run time stated, ruling 152's option C among them (insight scope rp12-o4-dock-trial).

## Pending Work / Open Loops

- The survivors' reading, the dock-trial section of the kit, and ruling 198's one independent inspection, then O4's Gate 5 under ruling 165.
- GHI #1337 open: gz mx reads a hard-coded ledger path.
- GHI #1331 open: a timed-out fetch reports stale ahead/behind as current.
- Insight, scope tautological-test-audit: debt over its ceiling, routed through the decommission-tautological-tests chore before gz mx exit.
- The contract's hexagon-test discrepancy line carries 113 covers, 13 label and 2 patch findings, unchanged this session.
- The sensitivity floor names two ADR-0.39.0 briefs, tracked by RP-7 held ruling H6.

## Verification Checklist

- uv run -m unittest tests.test_tag_out.PausedCarryTests passes, test_a_paused_orders_find_block_takes_no_exit among them.
- uv run gz arb red --commit 6e74a3f6d reads verdict driven.
- uv run python docs/governance/harbor-ro12-dock-trial-evidence/o4_mutation_sweep.py --plan prints total mutants: 574.
- gh run list --workflow CI --limit 3 reads check success on the synced HEAD.
- uv run gz obpi lock list reads mx-session ACTIVE until the lease lapses.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` (rulings 195 to 199, the amended rows, the new row)
- `docs/governance/harbor-ro12-dock-trial-evidence/o4_mutation_sweep.py`
- `src/gzkit/work_package_run.py` (_check_paused_find_exit)
- `tests/test_tag_out.py`
- `docs/user/manpages/wp-unblock.md`
- `tests/commands/test_wp_entry.py`
- `pyproject.toml`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

2418 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
