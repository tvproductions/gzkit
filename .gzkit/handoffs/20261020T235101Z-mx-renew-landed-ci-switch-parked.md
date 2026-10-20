---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-20T23:51:01Z'
agent: claude-code
session_id: 57346836-b4d2-414f-b5b1-04898f13456f
continues_from: .gzkit/handoffs/20261020T230151Z-mx-renewed-renewal-ruled.md
---

## Current State Summary

Since `.gzkit/handoffs/20261020T230151Z-mx-renewed-renewal-ruled.md`: `gz mx renew` landed (57a5e6d7f, driven in baac78a8d, passage-log row 3b6588a03) and GHI #1261 is closed. Renewing an expired drydock lease is now one command that runs no guard, keeps the marker, and leaves debt aging per contract. Three GHIs were filed: #1261 (renewal, closed), #1262 (debt reading should count what the demoted checks would refuse, not hours open), #1263 (CI full-strength switch, built then parked in git stash by the operator). Everything is pushed; origin/main reads 0 0.

## Important Context

- The resume loop is now: resume from the handoff, renew the lease through the gz-mx skill if the orientation announces it expired, work, write a handoff. Exit (the full-strength gate) is only for the drydock's actual end.
- The current lease (session 57346836) was opened 2026-10-20T22:59Z with a 24h TTL; it has not been renewed yet.
- Advisory debt keeps rising per contract (ruled 2026-10-18, GHI #1258); the WARNING at session start is that clock, not a sign that anything is broken. #1262 would make it name actual refusals.
- The CI switch is in `git stash` as 'GHI #1263 CI full-strength switch (parked 2026-10-20)'. It also bumps mx-mode to 1.10.0, which the renewal now owns, so unparking needs the rule bumped again and the stash reconciled.
- The operator's frustration this session: safe mode is meant to be freedom to modify without fuss. Do not add ceremony to the drydock loop; prefer the smallest step that keeps the session moving.

## Decisions Made

- [operator-ruled] Proceed on the handoff's step 1 (verbatim: "proceed: file the safe-mode renewal GHI through ghi-author").
- [operator-ruled] Renewal is lease-only and the debt reading gets its own GHI (verbatim: "Make renewal lease-only, as the 10-18 ruling already implies." and "File a separate GHI so the debt reading reports what the advisory checks would actually refuse, instead of elapsed time.").
- [operator-ruled] CI was to run the demoted guards at full strength (verbatim: "Have CI ignore .gzkit/mx.json so the demoted guards run at full strength on every push."), by an env switch (selection: "Env switch in gz (Rec.)"); then parked (verbatim: "Yes: stash the CI change, leave #1263 open as parked, build #1261 so renewing the lease is one command, then write a handoff.").
- [agent-chose] Expiry booking became per lease (`lease_started_at`) so a renewed lease that runs out again is still booked; the renewal carries `renewed_at` because `Ledger.append` stamps `ts` itself.
- [agent-chose] Proved the new event type with an isolated producer probe rather than renewing the live lease early or raising the inertness baseline.

## Immediate Next Steps

1. When the orientation announces the lease expired, renew it through the gz-mx skill (`gz mx renew --attestor g0`); the operator gives the word.
2. The predecessor's order: RO-9 tranche 2 as its own session, specify RO-3, GHI #1259.
3. When the operator chooses: GHI #1262 (debt reading names what the demoted checks would refuse).
4. GHI #1263 stays parked until the operator rules whether CI only reports in safe mode or fails.

## Pending Work / Open Loops

- GHI #1263 parked in git stash; unparking needs the operator's report-versus-fail ruling and a rule-version reconcile with the renewal's mx-mode 1.10.0.
- GHI #1262 open, not started.
- `tests/complexity/test_citation.py::TestRuleVersionConsistency` still restates the rule-version regex (insight scope `tests-rule-version`), carried from the predecessor.
- 30 overdue chores, carried.

## Verification Checklist

- `uv run gz mx renew --help` exits 0.
- `uv run gz obpi lock list` shows the mx-session lock for 57346836.
- `git rev-list --left-right --count origin/main...HEAD` reads `0 0`; `git stash list` shows the parked #1263 entry.
- `gh issue view 1261 --json state` reads CLOSED.

## Evidence / Artifacts

- `src/gzkit/commands/mx_cmd.py`
- `src/gzkit/mx/hardening.py`
- `src/gzkit/mx/lease.py`
- `tests/commands/test_mx_renew.py`
- `features/mx_renew.feature`
- `docs/user/manpages/mx-renew.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`

## Settled Rulings

1637 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
