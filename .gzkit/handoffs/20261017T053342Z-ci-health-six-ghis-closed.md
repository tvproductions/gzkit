---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-17T05:33:42Z'
agent: claude-code
session_id: 4b44a0f9-c403-4d99-84df-fd5feabf79bd
continues_from:
- .gzkit/handoffs/20261016T090058Z-control-plane-cut-booked-model-level-reduced.md
- .gzkit/handoffs/20261017T003314Z-session-exit-bookmark.md
- .gzkit/handoffs/20261017T003323Z-session-exit-bookmark.md
---

## Current State Summary

This session left the safe-mode plan untouched and worked CI health, by operator direction, from a pasted external diagnosis of a red `gz check --full` through six GHIs. Main is green and in sync with origin. No locks are held, and `.gzkit/mx.json` is absent, so neither safe mode nor the hangar is open.

- CI was red from three defects, not the stale flag or spec drift the pasted note claimed: a planned verb `gz release pressure` in the harbor pilotage contract tripped `--cli-alignment`; the `gz mx enter --mode` help ran 154 chars; and a behave fixture lacked the served stage procedures OBPI-0.35.0-17 now requires. Fixed in f88ea9a7e, together with the ops.product_proof flag's review date renewed to 2027-04-16.
- GHI #1254 fixed (766e36309): a newer push to a ref cancels the CI run it supersedes. Observed: run 38882366781 cancelled.
- GHI #1253 fixed (d7c47a3f8): windows-latest runs `gz check --cross-platform`, the full sweep minus `Guard canary sweep` and `Preflight`. The time after the unit tier fell from 298 s to 94 s.
- GHI #1255 fixed (48c2d3109, a225c0026): gated readers start when the writer lane ends, not when Test does. The Ubuntu gate fell from 542 s to 444 s.
- GHI #1171 closed as an investigation (45cca5205): Windows runs the serial unit tier 3.9x slower, scaling with file-system and process work. The new on-demand workflow `unit-tier-profile.yml` measures it.
- GHI #1256 fixed (a7b754898): a contended Windows file lock wakes in milliseconds. Four lock-using modules dropped from about 88 s to about 11 s on Windows.

Windows CI job: 702 s on a225c0026, against a typical 18 to 21 min before.

## Important Context

- The predecessor's plan (H8 safe mode, H9 attestations, the WP-8 to WP-16 work packages) is unchanged and still open; this session did not advance it. Every claim about it below was re-verified on 2026-10-17: #1244 to #1252 OPEN; OBPI-0.35.0-17 and -20 Completion PENDING, attestation missing.
- A verbatim operator ruling quoted in a commit body can be a GitHub closing keyword. "fix #1254 now" and "fix #1253 now" auto-closed both GHIs on push, before evidence existed. Later commits cite the ruling as quoted in the close comment instead. Recorded as an insight (scope `commit-message-ruling-quotes`).
- `gz check --cross-platform` is a new CLI flag and scope (`src/gzkit/check_step_scopes.json`), mutually exclusive with `--full`. It never records the reuse fingerprint, and only a `--full` pass satisfies it under `--reuse-verified`.
- `.github/workflows/unit-tier-profile.yml` runs only when the profiler or that workflow changes, or on `workflow_dispatch`; it gates nothing. This session dispatched it once with `gh workflow run`, which is outside `.gzkit/rules/gh-cli.md`'s allowed-command list; the operator was told.
- The config-registry gate reads any module constant named `*_CEILING`, `*_MAX` and similar as an operator policy knob. The lock's backoff constant is named `_LONGEST_PAUSE` for that reason (commit body says so).
- `gz arb red --commit` grades a rewritten loop as inconclusive, because single-hunk reverts break or hang it. The scheduler tests now bound the call at 30 s, so a deadlock fails instead of hanging the tier.

## Decisions Made

- [operator-ruled] Renew the stale flag rather than retire it, then sync (verbatim: "A, renew the review date, then git-sync").
- [operator-ruled] File the Windows-job trim and the supersede-cancel as GHIs (verbatim: "A and B, file both"). An earlier ruling, "C", chose parallelizing the unit suite on the agent's false claim that it ran in one process; it already runs on unittest-parallel across 4 workers. The agent withdrew the premise, recorded it as an insight, and the operator re-ruled.
- [operator-ruled] Cancel superseded CI runs, accepting that an intermediate commit superseded mid-run gets no verdict of its own (verbatim: "fix #1254 now, cancel superseded runs is fine").
- [operator-ruled] Fix #1253 (verbatim: "fix #1253 now").
- [operator-ruled] Fix #1255 (verbatim: "fix #1255 now").
- [operator-ruled] Fix #1171 (verbatim: "fix #1171 now").
- [operator-ruled] Fix #1256 and close it on the profile's evidence (verbatim: "fix #1256 now", then "close #1256 when the profile finishes").
- [agent-chose] Windows drops only `Guard canary sweep` and `Preflight`: every other step reads paths, spawns a subprocess, decodes output or compares bytes. `Docs build` stays because dropping it frees no wall time.
- [agent-chose] Investigated #1171 with a serial, one-process profile per platform rather than the parallel gate, to remove core contention from every figure.
- [agent-chose] Replaced #1253's planned negative control (injecting a Windows-only defect onto main) with structural tests, since this repository works directly on main.

## Immediate Next Steps

1. Operator: rule on the predecessor's plan, which is unchanged: H8 (invoke /gz-mx and enter safe mode under docs/governance/harbor-pilotage-candidate-2026-10-15.md; then GHI #1244 closes fixed against ac3b0005e), then H9 (rule on the four cutover disclosures and attest OBPI-0.35.0-17 and -20).
2. Operator: say whether OBPI-0.35.0-17 should record features/steps/acceptance_recovery_steps.py as a coupled consumer. f88ea9a7e edited that file, outside the brief's Allowed Paths, to seed the stage procedures its requirement 7 made mandatory.
3. Cheaper sessions, as the predecessor ordered them: WP-13 #1249 first; then WP-10 #1245, WP-8 #1247 and WP-12 #1248; WP-11 #1246 once the WP-16 #1252 protocol is written.
4. When the slow-test work is drawn: rank the 40 s (Ubuntu) and 190 s (Windows) test in tests/governance/test_qc_binding_self_check.py first, under the test-consolidation-subtest-sweep chore's slow-tier item.

## Pending Work / Open Loops

- From the predecessor, re-verified open: GHI #1244 to #1252; OBPI-0.35.0-17 and -20 awaiting attestation; the WP-16 protocol, WP-14 merge plan, H5, H6, H10, drydock D1 to D6 and the sea trial not started; the four slice-size findings, GHI #1230 to #1241 routing, the 27 helper-or-loop gates tracker, and the three pointer-line lifts from the 2026-10-15 diet recommendation.
- The predecessor's "drop stash@{0}" step is moot: `git stash list` is empty.
- Unit-tier wall time on Windows is mostly the hosted runner's file-system and process overhead (#1171 [settled] finding 1). Not a defect; reducing it means tests doing less I/O and spawning, which is the test-consolidation chore's territory, undrawn.
- The 731 REQs with no linked test remain an advisory in every `gz check`; not worked.
- The `.gzkit/chores/test-consolidation-subtest-sweep/README.md` baseline still reads that the profiler "is wired to nothing"; it is labelled a 2026-07-27 baseline, a dated record, and was left as written.

## Verification Checklist

- `gh run list --workflow ci.yml --limit 1` shows the newest main run green on both jobs.
- `uv run gz check --help` lists `--cross-platform`.
- `gh issue view 1253`, `1254`, `1255`, `1256` and `1171` each show CLOSED with an evidence comment.
- `uv run gz obpi status OBPI-0.35.0-17` and `OBPI-0.35.0-20` still show Completion PENDING before H9 is offered.
- `uv run gz obpi lock list` shows no active locks; `.gzkit/mx.json` is absent unless H8 has run.
- `uv run gz handoff rulings --search "1253"` returns this handoff's booked ruling.

## Evidence / Artifacts

- `.github/workflows/ci.yml` — concurrency group (#1254); Linux `--full`, Windows `--cross-platform` (#1253).
- `.github/workflows/unit-tier-profile.yml` — the on-demand per-module profile (#1171).
- `src/gzkit/check_step_scopes.json` — the `cross-platform` scope and its per-step rationale.
- `src/gzkit/commands/quality.py` — `_run_check_steps` gated-reader start (#1255); `--cross-platform` handling and the reuse rule (#1253).
- `src/gzkit/cli/parser_maintenance.py` — the `--cross-platform` flag.
- `src/gzkit/file_lock.py` — Windows `LK_NBLCK` with 1 to 50 ms backoff (#1256).
- `scripts/profile_unittest_modules.py` — `--json` record (#1171).
- `tests/governance/test_check_step_scopes.py`, `tests/governance/test_check_step_writer_overlap.py`, `tests/test_file_lock.py`, `tests/scripts/test_profile_unittest_modules.py`.
- `docs/user/manpages/check.md` — documents `--cross-platform`.
- `data/flags.json` — the ops.product_proof flag review date 2027-04-16.
- `artifacts/receipts/arb-red-commit-d7c47a3f871c-e0c9c336cf3a462e919fd2f2702d7573.json` (#1253, driven); `artifacts/receipts/arb-red-commit-48c2d310993c-2db317d765e24805b6a03c15cba56937.json` (#1255, inconclusive); `artifacts/receipts/arb-red-commit-a7b754898b41-31775bb3cdd14bee81d1a3f19f9b5e91.json` (#1256, driven).
- CI runs 38883869626, 38983901338, 38985375317, 38987707680; profile runs 38984988910 (before) and 38987712451 (after #1256).

## Settled Rulings

1562 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
