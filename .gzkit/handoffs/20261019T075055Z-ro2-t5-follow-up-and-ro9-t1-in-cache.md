---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-19T07:50:55Z'
agent: claude-code
session_id: 0f093cd5-657a-4ef0-afd7-cbbb192b698a
continues_from:
- .gzkit/handoffs/20261019T020537Z-ro9-specified-tranche1-in-worktree.md
- .gzkit/handoffs/20261019T065305Z-session-exit-bookmark.md
---

## Current State Summary

RO-2's five tranches are on main with CI green (tranche 4 run 39198064636, tranche 5 a15625510): data/id_seam_baseline.json is empty. But RO-2 is NOT honestly closed: tranche 5's red witness on 94edfb495 was undriven (receipt arb-red-commit-94edfb4955b4-8edc326655854abaa7bdfab3a49925e8: 118 killed, 55 survived, 14 inconclusive), and its passage-log row in docs/governance/harbor-pilotage-candidate-2026-10-15.md falsely says the survivors were 'driven in a follow-up'; no follow-up commit exists. The operator ruled the follow-up be done here (verbatim below); the tranche 5 session (local_595d5dcd) was stopped and stood down, and recorded the false claim as a defect insight (uncommitted, in the working tree). Work in progress, none landed: (1) the tranche 5 driving tests, .gzkit/cache/ro2t5/test_id_seam_readers_driven.py, batch 1 of the pure helpers written and green on main's tree, with muts.json (all 55 revert mutations), dump.txt (what each revert does and a planned test per hunk, from the implementer) and sweep.py; (2) RO-9 tranche 1, refreshed onto main as .gzkit/cache/ro9/tranche1-v2.patch (224 files, applies cleanly to a15625510, ledger rows excluded): the witness, uv 0.13.1 with a regenerated lock, Ruff 0.17.1, ty 0.0.89, setup-uv v10.3.0, Python declared once at 3.14.8, the 3.14 reformat (PEP 758, 158 files), 21 contextmanager annotations moved to Generator, --python-version-pins retired, the exception register, the seeded baseline (46 rows, 50 violations), the manpage section, the spec updates, the uv norms doc, and two canaries bound and killed live. On 3.14 the full unit tier passed after fixes for three defects it surfaced: tests patching the removed Path._globber; a signature test evaluating a deferred annotation; and attestor_names' DEFAULT_IGNORABLE_LETTERS re-derived against UCD 16.0.0 (same four code points, version marker bumped).

## Important Context

Safe mode is open as session e6800367 (lease near 2026-10-19T16:50Z, debt past 46 h). The tranche 5 sweep needs nominated tests: gzkit.mutation_witness.run_mutation_sweep reports every mutant inconclusive ('nominated tests are absent') unless each Mutation carries expected_tests, so take them from a baseline run as commit_witness._sweep_hunks does (read_test_observations over a `-v` run). Build the remaining tests from dump.txt's plan: fixture-driven readers (adr_audit._collect_covers_locations_for_adr, context_cmd, commands/quality._resolve_obpi_req_ids, status_obpi, status_render, task._build_fanout_rows, validate_decomposition, exchange_records, sunset_migrate, req_kind, airlock, hooks validation script, adr_eval) and the CLI entry points (attest, audit, closeout, obpi validate, interview, register, adr evaluate, adr demote) via tests/commands/common.py's CliRunner and _quick_init. RO-9's patch also fixes a real defect: gzkit.mutation_witness._compiles ran a bare `python3` from PATH, which on this machine is 3.13 and cannot parse 3.14 syntax, so every canary and red witness read 'does not compile'; it now uses sys.executable, with a failing test observed first. To work on RO-9 before the global uv moves, put uv 0.13.1 first on PATH (it is cached under ~/.cache/uv/archive-v0; `uvx --from uv==0.13.1 uv` also works) and do not touch the global binary while other sessions run. Commit .gzkit/insights/agent-insights.jsonl and .gzkit/ledger.jsonl together: splitting them turned CI red once today (fixed in 74f7e1168). CI ignores pushes that touch only handoffs, insights and the ledger.

## Decisions Made

- [operator-ruled] Tranche 5 follow-up, verbatim: "Do the tranche 5 follow-up here: drive the 55 survivors, correct the passage-log row, then land RO-9 tranche 1."
- [agent-chose] Stopped the tranche 5 session and told it to stand down, so two sessions would not drive the same hunks in one checkout.
- [agent-chose] Retired the old private name init_cmd._scaffold_project_skeleton for a public scaffold_project_skeleton, since the private cross-package import ratchet refused the witness reaching a private name; no other caller used it.
- [agent-chose] Re-derived DEFAULT_IGNORABLE_LETTERS from unicode.org's DerivedCoreProperties-16.0.0.txt under CPython 3.14's unicodedata: the same four Lo-category code points, so only the version marker and its comment change.

## Immediate Next Steps

1. Finish the tranche 5 follow-up: copy .gzkit/cache/ro2t5/test_id_seam_readers_driven.py into tests/, add the remaining tests from dump.txt, sweep with sweep.py given expected_tests, iterate until all 55 are killed or each survivor is shown equivalent; `uv run gz check --full`; commit with `Task: TASK-ro2-parents`; `uv run gz arb red --commit HEAD`.
2. Correct the RO-2 tranche 5 passage-log row to cite that follow-up commit, its verdict and receipt, and the regrade of 94edfb495's hunks against both commits' tests; commit the tranche 5 session's defect insight with the ledger; push and read CI.
3. Land RO-9 tranche 1 when no other session edits the checkout: `git apply --binary .gzkit/cache/ro9/tranche1-v2.patch`; `uv self update` to 0.13.1; add the passage-log row; get the operator's review of the astral-discipline and astral-discipline-baselined canaries with `gz canary review`; `uv run gz check --full` on 3.14; commit with `Task: TASK-ro9-version-once`; `gz arb red --commit HEAD` and drive any survivor; push and read CI on both platforms.
4. Then propose RO-9 tranches 2 to 7 as sessions, one at a time; specify RO-3; decide the hangar's lease with the operator.

## Pending Work / Open Loops

The tranche 5 passage-log row's false 'driven in a follow-up' claim stands until step 2 corrects it. RO-9 tranche 1 is unlanded. The scratch worktrees (scratchpad ro9wt, ro9wt2, drive/wt) are session-local; the cache files are the durable copies. Carried from earlier: the Windows CI findings (Test 1.7x slower, the Handoff validator spawns 449 git processes), the correction_mining threshold duplicate, the orientation over its 4000-byte budget (5364 B), thirty overdue chores, and the hand-back amendment.

## Verification Checklist

git log --oneline -4 shows a15625510 at the top; `git apply --check --binary .gzkit/cache/ro9/tranche1-v2.patch` exits 0; data/id_seam_baseline.json on main has an empty sites list; uv run gz handoff rulings --search 'tranche 5 follow-up here' returns the ruling; the receipt artifacts/receipts/arb-red-commit-94edfb4955b4-8edc326655854abaa7bdfab3a49925e8.json lists 55 survived hunks.

## Evidence / Artifacts

- `.gzkit/cache/ro9/tranche1-v2.patch`
- `.gzkit/cache/ro2t5/test_id_seam_readers_driven.py`
- `.gzkit/cache/ro2t5/muts.json`
- `.gzkit/cache/ro2t5/dump.txt`
- `.gzkit/cache/ro2t5/sweep.py`
- `artifacts/receipts/arb-red-commit-94edfb4955b4-8edc326655854abaa7bdfab3a49925e8.json`
- `docs/governance/harbor-ro9-astral-toolchain.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`

## Settled Rulings

1627 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
