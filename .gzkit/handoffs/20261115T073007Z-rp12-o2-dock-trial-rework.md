---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-15T07:30:07Z'
agent: claude-code
session_id: a2ab930e-fb4b-4c49-873c-a602a7f9fbe8
continues_from: .gzkit/handoffs/20261114T124031Z-ghis-1326-1328-closed.md
---

## Current State Summary

Resumed from 20261114T124031Z-ghis-1326-1328-closed.md and, on the operator's ranking question, returned to the drydock's critical path: RP-12, stalled since the 2026-11-08 checkpoint (33f142d89). O2 task 4 Act 4 is closed: the docs, event and schema review found 17 findings, the operator ruled three (rulings 87 to 89), every finding and a follow-up inspection's five were fixed and pushed (1e2f75c6b..b2f5b2aee). O2 task 5, the dock trial, is open: rulings 90 (a mutation sweep) and 91 (narrow the inconclusive rows, disclose the rest) and the two first-sweep survivors' tests landed in 6cdb446f0, committed locally and not pushed. The sweep itself did NOT pass independent inspection and is uncommitted: the script, its JSON record and the record prose section in the RP-12 spec are in the working tree only.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md. The ruled order is RP-5, RP-12, RP-11, RP-4 (contract § Rulings of 2026-11-02); RP-12 is the bootstrap every order from RP-11 on runs under, so it is the critical path. Ruling 27 has each order's dock trial run its refusal tests red then green, with gz check over what the order touched, inspected by a reviewer that did no part of the work. The instrument is gzkit.mutation_witness.run_mutation_sweep; tests.md § Mutation-sweep integrity cites a sweep only when is_conclusive, and ruling 91 departs from that for rows it discloses, which the record prose must say. The working tree holds the uncommitted trial, untracked so not cited as evidence: the sweep script o2_mutation_sweep.py and its record o2-sweep-2026-11-15.json under docs/governance/harbor-ro12-dock-trial-evidence/, and the section 'O2's dock trial, swept 2026-11-15' in the RP-12 spec; none of it stands as written. A full sweep takes about five minutes; run it in the background.

## Decisions Made

- [operator-ruled] Proceed on the resumed handoff (verbatim: "Proceed").
- [operator-ruled] Resume RP-12 at O2 task 4's pending docs review (verbatim: "Resume RP-12").
- [operator-ruled] RP-12 ruling 87, a superseded REQ's refusal names every head of its chain (verbatim: "A: Name every head").
- [operator-ruled] RP-12 ruling 88, acceptance reads the footprint on every order (verbatim: "A: Always read it").
- [operator-ruled] RP-12 ruling 89, ruling 72's reopen route is withdrawn (verbatim: "A: Withdraw it").
- [operator-ruled] Push the seven RP-12 commits (verbatim: "Push it").
- [operator-ruled] Close O2 task 4 Act 4 and open task 5 (verbatim: "Close, open task 5").
- [operator-ruled] RP-12 ruling 90, O2's dock trial by mutation sweep (verbatim: "A: Mutation sweep").
- [operator-ruled] RP-12 ruling 91, narrow the inconclusive rows and disclose the rest (verbatim: "A: Narrow, disclose rest").
- [operator-ruled] Hand the trial's rework to a fresh session (verbatim: "Hand off").
- [agent-chose] Committed rulings 90 and 91, the two survivors' tests and the Gate 5 Mode Contract row, and kept the failed trial's script, record and prose out of main until the rework passes inspection.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id, then ask whether to push 6cdb446f0 and this handoff.
2. Rework O2's dock trial to the inspection's conditions: widen the sweep script to the missed guards (a refusal returned as a list at catalog.py:148, raised ResourceNotFoundError in wp_order.py _package and _order, the round-bound refusal in wp_order_accept_cmd, the order id series in order_breaches, work_package_ledger._check_repair_close and _check_baselined, order_store.stage_order, and the order arms of work_package_run _dispatch_subject, record_work_package_dispatch, _check_blockable and record_work_package_unblock).
3. Write tests for the two new survivors the inspection found: gz wp order new on an unknown package (the test passes on the crash) and order_store's id-held check (no test); then re-narrow catalog.py:147 to a test that a valid repair REQ passes, order_move_refusal:532 and record_order_transition:571 to test_a_skipped_or_backward_step_is_refused, and _package_order:351 to test_another_packages_blocked_order_is_refused.
4. Re-run the sweep, rewrite the record prose to the new JSON (name the nominate-all attribution, the is_conclusive departure under ruling 91, and drop the claim of two first-sweep survivors or back it), amend the stale lifecycle Mode Contract clause 'closed refused until O2 task 4', stage everything together, run gz check under an ARB receipt, and send it to a fresh independent inspector.
5. On a standing trial, put O2's close to the operator, then O3, the tag-out log.

## Pending Work / Open Loops

- Hexagon guard canaries: tests.governance.test_guard_canaries fails on four claims from the hexagon work (hexagon-dependencies, hexagon-dependencies-baselined, hexagon-tests, hexagon-tests-baselined), with no canary and no grandfather row; recorded as a defect insight. It belongs to RP-15 tranche 6 and RP-7's hexagon gates and should go on the contract's list of discrepancies as blocking return to service, on the operator's word.
- The inspection's finding 11: with the package arm of work_package_run._check_blockable's unblockable-state guard removed, O2's 266 tests stay green; check tests/test_work_package_run.py and track it if no test there catches it.
- The ruling 90 insight says each mutant ran against its named test; the script nominated every executed test. The insight is append-only; the record prose notes the difference.
- The mx-session lock is past half its lease; renew or release it through gz-mx.
- Open siblings #1314 and #1316 stand, to be taken only on the operator's word.
- Shift turnover: no tag-outs hung, no work package commenced; gz obpi lock list shows only the mx-session lock.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 1 or 0 2 until 6cdb446f0 and the handoff are pushed.
- uv run -m unittest tests.test_order_ledger tests.test_order_ledger_schema tests.commands.test_wp_order tests.commands.test_wp_order_acceptance passes.
- git status shows the three uncommitted trial surfaces: the sweep script, its JSON and the modified RP-12 spec.
- uv run -m unittest tests.governance.test_guard_canaries fails only on the four hexagon claims.
- uv run gz obpi lock list shows the mx-session lock and its elapsed lease.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` — rulings 87 to 91 and the Gate 5 Mode Contract row (committed); the trial record section is uncommitted.
- `src/gzkit/order_ledger.py`, `src/gzkit/commands/wp_order.py`, `src/gzkit/governance/trust_audits/catalog.py`, `src/gzkit/schemas/ledger.json` — the O2 task 4 fixes.
- `tests/test_order_ledger.py`, `tests/test_order_ledger_schema.py`, `tests/commands/test_wp_order.py`, `tests/commands/test_wp_order_acceptance.py`, `tests/governance/test_catalog_repair_reqs.py` — the tests.

## Settled Rulings

2244 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
