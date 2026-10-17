---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-17T07:51:08Z'
agent: claude-code
session_id: 4b44a0f9-c403-4d99-84df-fd5feabf79bd
continues_from: .gzkit/handoffs/20261017T053342Z-ci-health-six-ghis-closed.md
---

## Current State Summary

Since the predecessor handoff this session did one more CI item and then stopped on the operator's course-correction. Main is green and in sync with origin; no OBPI locks are held; `.gzkit/mx.json` is absent, so neither safe mode nor the hangar is open. The drydock plan has not moved since 2026-10-16.

- The slowest unit test, `test_fidelity_gate_passes_now_recovery_is_complete` in `tests/governance/test_qc_binding_self_check.py`, was slow because the fidelity gate built a fresh worktree (a full checkout) for every row. Fixed in c0379819e: one worktree per gate run, forced back to the HEAD commit and cleaned before each later row.
- Measured with the unit-tier profile, before (run 38984988910) and after (run 39012602540): Windows 190.3 s to 69.0 s; Ubuntu 39.6 s to 41.4 s, unchanged, consistent with cheap checkouts on Linux. Locally, `gz adr fidelity` on ADR-0.0.73: 27.5 s to 17.3 s.
- CI run 39012602695 on 98796a71e passed on both jobs (Ubuntu 547 s, Windows 869 s).
- The operator then asked why no drydock work was happening. The agent had kept offering the next CI thread after each fix without saying it was off the campaign sequence. Recorded as an improvement insight; CI work stopped there.

## Important Context

- The campaign governs what is pulled next, and the predecessor's step 1 is H8. Do not offer CI or test-speed threads as the next move; track any that surface (GHI or insight) and name the campaign's next step instead (operator course-correction, recorded in `.gzkit/insights/agent-insights.jsonl`, scope `campaign-sequencing`).
- The fidelity gate change keeps the GHI #1156 invariant: every row's verdict depends only on the committed tree at HEAD, and the live checkout is untouched. A worktree that cannot be built or restored still fails rows closed with WORKTREE_UNAVAILABLE. A stale `index.lock` makes `git checkout` fail while `git clean` succeeds, so the restore checks both.
- The profile workflow was dispatched again with `gh workflow run`, which is outside `.gzkit/rules/gh-cli.md`'s allowed-command list; the operator was told both times.
- Everything in the predecessor's Important Context still holds; it is not restated here.

## Decisions Made

- [operator-ruled] Fix the slowest unit test (verbatim: "fix the 190s test in test_qc_binding_self_check").
- [operator-ruled] Course-correction: the drydock was being displaced by CI work (verbatim: "i am not doing any work towards the dry dock over this ci work, what is going on?").
- [agent-chose] Fixed the cause in the fidelity gate (`src/gzkit/fidelity.py`) rather than weakening or moving the test, because the test's subject, the ADR passing its own check, is the right claim and the cost was the gate's mechanism.
- [agent-chose] Routed it as a direct fix without a GHI: one source file, in one surface, found in flight, with existing tests, and no live brief owning `src/gzkit/fidelity.py`.

## Immediate Next Steps

1. Operator: H8, invoke /gz-mx and enter safe mode under docs/governance/harbor-pilotage-candidate-2026-10-15.md; then GHI #1244 closes fixed against ac3b0005e.
2. Operator: H9, rule on the four cutover disclosures and attest OBPI-0.35.0-17 and -20; with it, rule whether OBPI-0.35.0-17 records features/steps/acceptance_recovery_steps.py as a coupled consumer (edited in f88ea9a7e outside the brief's Allowed Paths).
3. Cheaper sessions, in the predecessor's order: WP-13 #1249 first; then WP-10 #1245, WP-8 #1247 and WP-12 #1248; WP-11 #1246 once the WP-16 #1252 protocol is written.

## Pending Work / Open Loops

- Every open loop in the predecessor stands, re-verified 2026-10-17: GHI #1244 to #1252 open; OBPI-0.35.0-17 and -20 Completion PENDING; the WP-16 protocol, WP-14 merge plan, H5, H6, H10, drydock D1 to D6 and the sea trial not started.
- The slow test now takes 69 s on Windows and 41 s on Ubuntu; the rest is the seven commands ADR-0.0.73's Fidelity Assertions declare. Tracked by the slow-test insight (scope `unit-tier-slowest-test`); not to be drawn ahead of the campaign.

## Verification Checklist

- `gh run list --workflow ci.yml --limit 1` shows the newest main run green on both jobs.
- `uv run gz obpi lock list` shows no active locks, and `.gzkit/mx.json` is absent unless H8 has run.
- `uv run gz obpi status OBPI-0.35.0-17` and `OBPI-0.35.0-20` show Completion PENDING before H9 is offered.
- `uv run python -m unittest tests.governance.test_fidelity_committed_state` passes.
- `uv run gz handoff rulings --search "190s test"` returns this handoff's booked ruling.

## Evidence / Artifacts

- `src/gzkit/fidelity.py` — one worktree per run; `_restore_head` between rows.
- `tests/governance/test_fidelity_committed_state.py` — row isolation, one worktree per run, unrunnable command, unrestorable worktree, failed checkout with working clean.
- `artifacts/receipts/arb-red-commit-c0379819e9ce-7fbf9997a29848c4b1f87b74469d7ba5.json` — red witness, no surviving hunk.
- `.gzkit/insights/agent-insights.jsonl` — the `campaign-sequencing` course-correction and the `unit-tier-slowest-test` record.
- CI run 39012602695; profile runs 38984988910 (before) and 39012602540 (after).

## Settled Rulings

1564 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
