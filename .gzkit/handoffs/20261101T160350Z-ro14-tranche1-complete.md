---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T16:03:50Z'
agent: claude-code
session_id: e8f344c7-565b-43a5-a7d5-cf6fcb5cd569
continues_from: .gzkit/handoffs/20261101T131724Z-rulings-19-20-act6-next.md
---

## Current State Summary

RO-14 tranche 1 is complete: act 6 landed in c4dd29ae3 and act 7 in d4cd4a053, both pushed. The work package now crosses the airlock at commence and accept, gz wp accept refuses a file outside a declared footprint, and gz wp withdraw-legacy replaces gz obpi withdraw at parity. #1300 and #1301 are filed, and the cwd-escape guard proved to be #1296 already. Both commit witnesses read undriven.

## Important Context

The operator's objective is near-parity if not full between a work package and an OBPI: measure each surface against the control it replaces and name any shortfall before landing. A package footprint is read from the ledger after freeze, so a store edit moves nothing. Attribution is the Task trailer starting with the lowercased package id, such as TASK-wp-02-slug-#1185. gz lint --fix rewrites dated evidence scripts, so never run it on the whole tree here; use gz lint and targeted fixes. The pre-push hook stashes unstaged work and lints the staged copy, so stage everything before pushing. New verbs and events must join the attestor classification, the schema test map, the event-handler audit and the producer probe. Shift turnover: no tag hung, no run in flight, tag-out log still unbuilt, so this session read gz obpi lock list, gz wp runs and the RO-14 discrepancy lines; the hangar lease was renewed and the mx-session lock's expired lease evicts nothing.

## Decisions Made

- [operator-ruled] A repair package declares its own footprint and a delivery package reads its outcome's (verbatim: "Repair declares (Recommended)").
- [operator-ruled] A commit is the package's by its Task trailer (verbatim: "Task trailer (Recommended)").
- [operator-ruled] gz wp accept refuses a file outside a declared footprint (verbatim: "Refuse at accept (Recommended)").
- [operator-ruled] A repair package is held to the brief's standard at freeze (verbatim: "Hold at freeze (Recommended)").
- [operator-ruled] At the spent bound act 6 took one last repair and landed unreviewed (verbatim: "Fix the two, land (Recommended)").
- [operator-ruled] The docs-organization note holds until the handback (verbatim: "A", to the recommendation).
- [agent-chose] Kept #1185 open, because its exit condition needs a real package completion.
- [agent-chose] Moved the footprint rule out of _kind_breaches, leaving that canary's guard byte-identical, so no canary review was needed.

## Immediate Next Steps

1. Read CI for the latest main commit, including windows-latest.
2. Rule on whether --approver and --operator stay typed names, since an agent can take the refusal's recovery or a stopping exit itself.
3. Cover the undriven gaps on the RO-14 discrepancy list.
4. Start RO-14 tranche 2, which splits by owner under ruling 11.

## Pending Work / Open Loops

#1185 stays open until a real package completes. Delivery packages read undeclared until RO-11 tranche 2. Commits under another trailer escape the comparison. The last act 6 repair had no independent review. The act 7 review's findings were repaired and that repair was not re-reviewed. #1300 is owned by RO-15 tranche 5; #1301 is unrouted. The docs-organization note waits for the handback. MX debt keeps aging until gz mx exit.

## Verification Checklist

Run gh run list --branch main --limit 3 and read each job. Run uv run gz wp runs and expect no run in flight. Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Run uv run -m unittest tests.commands.test_wp_airlock tests.commands.test_wp_withdraw_legacy.

## Evidence / Artifacts

`src/gzkit/work_package_transit.py`
`src/gzkit/legacy_units.py`
`tests/commands/test_wp_airlock.py`
`tests/commands/test_wp_withdraw_legacy.py`
`docs/governance/harbor-ro14-obpi-forward-migration.md`

## Settled Rulings

1930 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
