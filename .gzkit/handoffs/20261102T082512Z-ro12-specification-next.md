---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-02T08:25:12Z'
agent: claude-code
session_id: d9edca47-0445-407d-9a38-840afac55103
continues_from: .gzkit/handoffs/20261101T160350Z-ro14-tranche1-complete.md
---

## Current State Summary

The RO-14 discrepancy list's four undriven gaps are covered (7c9593488). #1194 is closed: fix bf69bdd70, docstrings 30fd4e43e, independent review confirmed, CI green on ubuntu and windows-latest. #1296 stays open, routed by ruling into RO-12's specification (832e22a58). Nothing is in flight; the next work is specifying RO-12.

## Important Context

The ruled order is RO-5, RO-12, RO-11, RO-4; RO-14 tranche 1 preceded RO-12 and tranche 2 only has to precede RO-13's retrofit. RO-12 has no specification: it is diamond 2 of docs/rnd/contractor-kit.md, 3,404 lines, whose rows 2 and 4 were funded on 2026-10-28, and it belongs to the operator and a working session. Before putting a mechanism choice on a GHI, read whether it names something broken or a control never built, and raise the route first: the operator asked "why are doing this anyway? for a defect fix?" of #1296. Harness facts for that guard are in the contract's Rulings of 2026-11-02: hooks fire in subagents with agent_id, no variable marks a subagent, updatedInput is undocumented for subagents, and worktree isolation refuses a Bash command aimed at the main checkout but not shell file writes. Text-search hooks here refuse Python-looking symbols; repeat the command when the search is truly for a string. gz lint --fix stays off the whole tree. Shift turnover: no tag hung, no package commenced, no run in flight; the tag-out log is still unbuilt, so this session read gz obpi lock list, gz wp runs and the RO-14 discrepancy lines, and the mx-session lock is the only lock.

## Decisions Made

- [operator-ruled] --approver and --operator stay typed names, the limit staying on the discrepancy list and any fix taken up for every human-act verb together (verbatim: "A").
- [operator-ruled] Repair #1296 and #1194 first, then specify RO-12; RO-14 tranche 2's pipeline move waits (verbatim: "A").
- [operator-ruled] The cwd-escape guard leaves RO-12's preconditions and becomes a requirement of its specification, with #1296's acceptance cases unchanged (verbatim: "A").
- [operator-ruled] Cover the four undriven gaps with tests as one commit (verbatim: "yes").
- [agent-chose] A rename onto a renamed-away id re-binds that id, the new-id side of the #1151 rule, over refusing at the writer, because the fold repairs rows already written.
- [agent-chose] Set the gzkit.ledger_events first-import item due with RO-14 tranche 3; that date is not a ruling.
- [agent-chose] Added the guard's refusal to RO-12's witness floor as item 9.

## Immediate Next Steps

1. Read docs/rnd/contractor-kit.md and docs/rnd/contractor-kit/review.md in full, as the design spine of RO-12.
2. Read the RO-12 row and its nine-item witness floor in the contract, and the RO-5 and RO-14 specifications it builds on.
3. Draft the RO-12 specification at docs/governance/harbor-ro12-contractor-kit.md, putting each open point to the operator one at a time.
4. Carry #1296's three acceptance cases into that specification, then close #1296 as superseded against it.

## Pending Work / Open Loops

#1296 stays open until RO-12's specification carries it. #1185 stays open until a real package completes. #1200 stays open for the pipeline skill's sentence in tranche 2. Delivery packages read undeclared until RO-11 tranche 2. import gzkit.ledger_events as a first import still fails, on the discrepancy list. evaluation_justify_binding folds an unnetted rename stream, recorded as an insight in scope gzkit.ledger. #1301 is unrouted and #1300 sits with RO-15 tranche 5. RO-14 tranche 2's pipeline move awaits a working session; the rest of it waits for the kit. The docs-organization note waits for the handback. MX debt keeps aging until gz mx exit.

## Verification Checklist

Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Run gh run list --branch main --limit 3 for commit 832e22a58, since its CI was not read. Run gh issue view 1194 and expect CLOSED, and gh issue view 1296 and expect OPEN. Run uv run gz wp runs and expect no run in flight. Run uv run -m unittest tests.governance.test_rename_fold tests.commands.test_wp_airlock.

## Evidence / Artifacts

`src/gzkit/obpi_lifecycle.py`
`src/gzkit/legacy_units.py`
`tests/governance/test_rename_fold.py`
`tests/commands/test_wp_airlock.py`
`tests/commands/test_wp_withdraw_legacy.py`
`tests/test_ledger_producer_probe.py`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`
`docs/governance/harbor-ro14-obpi-forward-migration.md`

## Settled Rulings

1934 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
