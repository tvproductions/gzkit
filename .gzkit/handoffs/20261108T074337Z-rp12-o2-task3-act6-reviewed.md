---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-08T07:43:37Z'
agent: claude-code
session_id: e22bd7d2-70d3-41b5-96ac-a1a3c3934566
continues_from: .gzkit/handoffs/20261108T022921Z-rp12-o2-task3-act5-landed.md
---

## Current State Summary

Continues 20261108T022921Z-rp12-o2-task3-act5-landed.md. RP-12 O2 task 3 is complete through Act 6, its independent review. The operator ruled the handoff proceed, the MX lease was renewed (gz mx renew, 24h), and two independent reviewers inspected acts 1 to 5 and then the fix acts and four surfaces the first left unread. Every confirmed finding landed as its own act with gz check and gz arb red --commit HEAD: 44f4d001c a stopped order releases its REQs (ruling 53); e4e6e443b a move's refusal names the lifecycle and block before readiness; 66a334e19 a blocker's doubled period; d09aee5cd an accepted run takes no block (ruling 69); a1967bfe6 the ledger-before-store order of gz wp order new pinned (ruling 70); 73b460783 a path the package moved does not refuse a later order's freeze (ruling 56); 8de6ffd21 a later freeze refuses a store that dropped a sealed path (ruling 71); f510c3c8f a lost order record refuses every order move (ruling 70); 0d092fd1b order manpages and the kit status; d28509538 a worktree the root no longer registers is another root (ruling 51). Rulings 68 to 72 are booked on the kit page. One first-review finding was refuted (the fence test it named missing exists since e01878db1). Everything is pushed; origin/main...HEAD reads 0 0.

## Important Context

- Shift turnover (MX hangar open, session 57346836): this session hung no tags, raised no finding for buy-back and commenced no work package. gz obpi lock list shows the mx-session lock only, renewed this session to a fresh 24h lease. The contract's discrepancy list and passage log were not read in full.
- Workflow fronts (campaign plan): this session worked the adr/obpi front only, RP-12 O2 task 3 Act 6, on the operator's direction.
- Witness verdicts by act: driven for 66a334e19, d09aee5cd, 8de6ffd21, f510c3c8f, d28509538; undriven with every survivor named under rulings 67 and 68 for 44f4d001c, e4e6e443b, 73b460783; no-production-hunks for a1967bfe6 and 0d092fd1b.
- A hand revert of equal byte length restored within one second leaves CPython's cached .pyc of the mutant in place; run hand reverts with PYTHONDONTWRITEBYTECODE=1 (booked as an insight). zsh does not word-split an unquoted variable, so pass module lists to unittest through xargs.
- Task 4 is next: Gate 5 at the order with ruling 30's four outcomes, the order's close, the re-freeze, and the repair package's close reading every order's Gate 5 (rulings 44, 62). Ruling 62's limit stands until then: a repair package's close records a Gate 5 decision of its own.

## Decisions Made

- [operator-ruled] Proceed on the act 5 handoff, renew the lease and start Act 6 (verbatim: "yes, renew the lease and start Act 6").
- [operator-ruled] RP-12 ruling 68: a commit witness survivor that a test outside the commit kills does not hold an act back (by selection: "A: stands, named (Rec.)").
- [operator-ruled] RP-12 ruling 69: an accepted run takes no block (by selection: "A: refuse it (Rec.)").
- [operator-ruled] RP-12 ruling 70: an order's opening is booked before its record is written (by selection: "A: ledger first (Rec.)").
- [operator-ruled] Git-sync the Act 6 acts and send a second reviewer at the uncovered surfaces (by selection: "A: git-sync, review rest (Rec.)").
- [operator-ruled] RP-12 ruling 71: a later order's freeze is refused when the store dropped a sealed path (by selection: "A: refuse the freeze (Rec.)").
- [operator-ruled] RP-12 ruling 72: a stopped order's REQ keeps its fix-cycle count in a later order (by selection: "A: intended, say so (Rec.)").
- [operator-ruled] Git-sync, write a handoff and open task 4 (by selection: "A: sync, handoff, task 4 (Rec.)").
- [agent-chose] Moved order_took_stopping_exit and the stopping exits down into order_ledger so the live-holder check could read them without an import cycle.
- [agent-chose] Fixed finding 2 as a class at both levels, through order_move_refusal and block_refusal read by the writers and the verbs.
- [agent-chose] Rewrote the fence test that blocked an accepted package to assert ruling 69's refusal and the standing accepted fence.
- [agent-chose] Re-observed the wp-order-new opening row by running the manpage's own command through the real CLI against the test fixture that seeds the same catalog.

## Immediate Next Steps

1. Present this handoff to the operator and book the ruling with uv run gz handoff decide.
2. Put task 4's first opening question to the operator: what Gate 5 at the order records, with ruling 30's four outcomes.
3. Then, one at a time, the order's close and the re-freeze, and how the repair package's close reads every order's Gate 5 (rulings 44, 62).
4. Plan task 4's acts from those rulings and build them as Act 1 onward, each with gz check and uv run gz arb red --commit HEAD.

## Pending Work / Open Loops

- O2 task 4: Gate 5 at the order, the order's close and re-freeze; the repair package's close then reads every order's Gate 5 (rulings 30, 44, 62).
- O2 task 5: the dock trial (ruling 27).
- O5: the operator's verbatim words for return to service (ruling 32).
- The 32 overdue chores and the MX hangar's advisory debt are announced by session orientation and untouched here.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz check passes on a staged tree.
- uv run -m unittest tests.test_order_ledger tests.test_order_run tests.test_work_package_run tests.commands.test_wp_order tests.commands.test_wp_order_acceptance tests.commands.test_wp_acceptance tests.commands.test_wp_fence tests.test_dispatch_stamp passes.
- uv run -m behave features/work_packages.feature passes.
- uv run gz handoff rulings --search "ruling 72" returns the ruling.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` (rulings 68 to 72)
- `src/gzkit/order_ledger.py`, `src/gzkit/work_package_ledger.py`, `src/gzkit/work_package_run.py`, `src/gzkit/work_package_transit.py`, `src/gzkit/acceptance_store.py`, `src/gzkit/dispatch_stamp.py`, `src/gzkit/commands/wp.py`, `src/gzkit/commands/wp_order.py`
- `docs/user/manpages/wp-block.md`, `docs/user/manpages/wp-order-new.md`, `docs/user/manpages/wp-order-freeze.md`, `docs/user/manpages/wp-order-commence.md`, `docs/user/manpages/wp-order-accept.md`
- Commits 44f4d001c, d96b55600, e4e6e443b, 66a334e19, 4ef4b36ae, d09aee5cd, 1fa05794f, a1967bfe6, 73b460783, 36512a903, 8de6ffd21, f510c3c8f, 0d092fd1b, d28509538, 0b83e2909; witness receipts arb-red-commit-1478795a69f8-d37d5bd2d6b8450d85482e4509b16221, arb-red-commit-cf4ba5374043-181e34734d0540bab805bddd2d5de332, arb-red-commit-66a334e19a4a-4fc30418e8c34c2f8dae4ded6519b5a7, arb-red-commit-d09aee5cd420-1063f930ad9c4101830bc2d9fe0a7c96, arb-red-commit-73b46078335f-57ea5ccb8d974c419950c9de5363050e, arb-red-commit-8de6ffd210b8-87fa78fc33114fc69862b69e56b43538, arb-red-commit-f510c3c8f8b3-324e17776699422d8185d553e8437c90, arb-red-commit-d28509538ca8-910594149fb7451d9815f466685d6675

## Settled Rulings

2075 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
