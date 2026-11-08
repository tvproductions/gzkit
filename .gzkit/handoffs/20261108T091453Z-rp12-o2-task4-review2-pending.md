---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-11-08T09:14:53Z'
agent: claude-code
session_id: e22bd7d2-70d3-41b5-96ac-a1a3c3934566
continues_from: .gzkit/handoffs/20261108T074337Z-rp12-o2-task3-act6-reviewed.md
---

## Current State Summary

Continues 20261108T074337Z-rp12-o2-task3-act6-reviewed.md. RP-12 O2 task 4 (Gate 5 at the order) is built and first-reviewed; its second independent review has reported and its findings are NOT yet verified or worked. Opening rulings 73 to 78 and review rulings 79 to 81 are booked on the kit page. Acts: 72fa297e0 gz wp order close (73 to 75, 77); 95a0126f1 the repair package close reads its orders (76, 77); 804b7480d a repair REQ holds at the revision a proceed froze it (78), with an in-flight fix refusing an undelivered proceed. First-review fixes: 1938d4246 no closed order refuses the repair close (79); ce6dc0be7 the order writer refuses an unearned proceed via an acceptance_ready parameter (80); 0b489f98f a held REQ is never frozen again at that revision (81); fbaa64904 minor findings (fence recovery names gz wp order close, blank foreign fields refused, attestor stripped, repair close prints orders and holds, stale prose). Every act ran gz check and gz arb red --commit HEAD; each verdict and its survivors (rulings 55, 67, 68) are named in its commit message; inconclusive guards were hand-reverted without bytecode. All pushed: origin/main...HEAD reads 0 0. Checkpoint written because context filled (operator: "A: sync + handoff now (Rec.)").

## Important Context

- Shift turnover (MX hangar open, session 57346836): no tags hung, no finding for buy-back, no work package commenced. The mx-session lease was renewed this session (24h). The contract's discrepancy list and passage log were not read in full.
- Workflow fronts (campaign plan): adr/obpi front only, RP-12 O2 task 4.
- SECOND REVIEW FINDINGS, reported by a subagent, UNVERIFIED by the main session (verify each before acting):
  1. MAJOR: ruling 53 counts accepted as terminated, so while ORD-01 sits accepted awaiting Gate 5, ORD-02 can freeze the same REQ@rev; ORD-01 then proceeds (holds) and ORD-02 later terminates, so one REQ@rev reads held and returned unbound (breaks 81's invariant; also two proceeds on one REQ@rev). Fix is an operator ruling: refuse the proceed while another live order holds the REQ@rev, or refuse the freeze while an accepted order has not passed Gate 5. Code: order_ledger.py TERMINATED, _live_holders, the ruling 81 check in _check_frozen.
  2. minor: docs/user/manpages/wp-order-close.md says a closed order holds no REQ and may be re-frozen; contradicts 78 and 81.
  3. minor: docs/user/runbook.md repair flow ends with gz wp close and no order, now refused by 79; governance_runbook.md and the gz-wp skill step 6 omit the at-least-one condition.
  4. minor: ruling 81's refusal names a reopen exit as the route to a new revision, but a reopen needs a block on a frozen subject at the bound, unreachable once 81 refuses the freeze; no verb raises a REQ revision (hand edit of reqs.json does). Needs a ruling or a message change; the superseding-REQ route works.
  5. minor: ruling 80's acceptance_ready is read at Gate 5, not at acceptance: a stopped order accepted excused can later get acceptance init, proof and reviews and then proceed; the lambda also skips the footprint and round-bound checks. Operator to say which reading 80 means.
  - Open question raised: one order may freeze a REQ together with the REQ that supersedes it; a superseded REQ is not refused at freeze.
- Gotchas: run hand reverts with PYTHONDONTWRITEBYTECODE=1 (stale .pyc trap); zsh does not word-split, pass module lists through xargs; order manpage examples are observed through scripts in the job tmp dir driving tests.commands.test_wp_order._seed_catalog with CliRunner.

## Decisions Made

- [operator-ruled] Git-sync, write a handoff and open task 4 (by selection: "A: sync, handoff, task 4 (Rec.)").
- [operator-ruled] RP-12 ruling 73: an order's Gate 5 books its decision and that decision's fields (by selection: "A: decision + its own fields (Rec.)").
- [operator-ruled] RP-12 ruling 74: an order's Gate 5 closes it from accepted, and an order never frozen only as terminate (by selection: "A: accepted, one exception (Rec.)").
- [operator-ruled] RP-12 ruling 75: a redirect names an order already opened in the same package (by selection: "A: an opened order (Rec.)").
- [operator-ruled] RP-12 ruling 76: a repair package closes once every order is closed, with no decision of its own (by selection: "A: orders closed, no own decision (Rec.)").
- [operator-ruled] Build task 4 on the four-act plan (by selection: "A: build on this plan (Rec.)").
- [operator-ruled] RP-12 ruling 77: Gate 5 refuses a subagent-stamped call at the order and the package (by selection: "A: refuse it, both closes (Rec.)").
- [operator-ruled] RP-12 ruling 78: a repair REQ holds at the revision a proceed froze it; outcome validated is RP-14's (by selection: "A: a holds reader, outcomes later (Rec.)").
- [operator-ruled] RP-12 ruling 79: a repair package closes only once at least one order is closed (by selection: "A: refuse it (Rec.)").
- [operator-ruled] RP-12 ruling 80: a stopped order acceptance never read ready never closes as proceed, held in the writer (by selection: "A: rule it, in the writer (Rec.)").
- [operator-ruled] RP-12 ruling 81: a REQ a proceed holds is never frozen again at that revision (by selection: "A: refuse the re-freeze (Rec.)").
- [operator-ruled] Checkpoint: git-sync and write a handoff now (by selection: "A: sync + handoff now (Rec.)").
- [agent-chose] Fixed the undelivered proceed in act 3's commit, since its files overlapped act 3's, and named it there as an act 1 defect found in flight.
- [agent-chose] Passed acceptance readiness to the order writer as a parameter, since the writer holds no project root (hexagonal rule 4).

## Immediate Next Steps

1. Present this handoff to the operator and book the ruling with uv run gz handoff decide.
2. Verify second-review finding 1 (the accepted-window double hold) by reading order_ledger.py, then put its ruling to the operator: refuse the proceed while another live order holds the REQ at that revision, or refuse the freeze while an accepted order has not passed Gate 5.
3. Verify findings 4 and 5 and put each ruling to the operator one at a time (81's reopen route; 80's readiness read at acceptance or at Gate 5).
4. Fix findings 2 and 3 (wp-order-close.md holds sentence; runbook, governance runbook and gz-wp skill repair flow under ruling 79) as one docs act, with gz check and gz arb red --commit HEAD.
5. After the fixes, close Act 4 and put task 5 (the dock trial, ruling 27) to the operator.

## Pending Work / Open Loops

- Second-review findings 1 to 5 and the supersedes-in-one-baseline question, above.
- O2 task 5: the dock trial (ruling 27).
- O5: return to service on the operator's words (ruling 32); the tag-out log a pause clears (ruling 30).
- RP-14: an outcome's derived validated from a proceed's catalog proofs (ruling 78).
- The 32 overdue chores and the MX hangar's advisory debt, untouched.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz check passes on a staged tree.
- uv run -m unittest tests.test_order_ledger tests.test_order_run tests.test_work_package_ledger tests.commands.test_wp_order tests.commands.test_wp_order_acceptance tests.commands.test_wp_run tests.commands.test_wp_acceptance passes.
- uv run -m behave features/work_packages.feature passes.
- uv run gz handoff rulings --search "ruling 81" returns the ruling.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` (rulings 73 to 81)
- `src/gzkit/order_ledger.py`, `src/gzkit/work_package_ledger.py`, `src/gzkit/commands/wp_order.py`, `src/gzkit/commands/wp.py`, `src/gzkit/cli/parser_wp_order.py`, `src/gzkit/work_package_fence.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json`
- `docs/user/manpages/wp-order-close.md`, `docs/user/manpages/wp-close.md`, `docs/user/manpages/wp-order-show.md`, `docs/user/manpages/wp-order-freeze.md`, `docs/user/runbook.md`
- Commits 72fa297e0, 95a0126f1, 804b7480d, 1938d4246, ce6dc0be7, 0b489f98f, fbaa64904 and the ruling commits 11e19e024 to e604cf06b

## Settled Rulings

2086 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
