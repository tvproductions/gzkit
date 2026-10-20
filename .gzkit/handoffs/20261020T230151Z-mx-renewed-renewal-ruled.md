---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-20T23:01:51Z'
agent: claude-code
session_id: 57346836-b4d2-414f-b5b1-04898f13456f
continues_from: .gzkit/handoffs/20261020T225132Z-ro9-t1-landed-ghi1260-closed.md
---

## Current State Summary

Since `.gzkit/handoffs/20261020T225132Z-ro9-t1-landed-ghi1260-closed.md`, the MX session was renewed. The first `gz mx exit` refused on two guards safe mode had held advisory, the tautological-test audit (`tests/complexity/test_citation.py`) and ledger-vocabulary inertness (`obpi_lock_lease_expired` never fired). Both were repaired at source in `80747fda8`, the second exit passed, and safe mode reopened under the same contract as session 57346836 with a fresh lease. Everything is pushed; the tree is clean.

## Important Context

- `.gzkit/mx.json` is committed, so CI runs in safe mode too, and the demoted guards run at full strength nowhere until `gz mx exit`. That is why both drydock cycles met red guards at exit.
- There is no renewal: renewing an expired lease today means a full exit through the hard gate and a re-entry.
- The other open items stand as the predecessor lists them: RO-9 tranches 2 to 7, RO-3 to specify, GHI #1259, 30 overdue chores.

## Decisions Made

- [operator-ruled] The expired MX session is renewed, not ended (verbatim: "reopen lease"), asked whether exiting with six of eight exit conditions unmet meant ending the drydock.
- [operator-ruled] Safe mode needs a renewal distinct from exit (verbatim: "yes, we need the concept of a renewal"), after objecting (verbatim: "this shouldn't be a pain in the ass for me to enter and exit").
- [agent-chose] Proved the `obpi_lock_lease_expired` producer with an isolated probe of the real reaper, not by raising the grandfather baseline, which the guard reserves to the operator.

## Immediate Next Steps

1. File a GHI through `ghi-author` for the safe-mode renewal: a verb that books a fresh lease and resets debt aging without running the guards, the full-strength exit gate kept for the drydock's actual end. It is a new CLI subcommand, so the seven obligations of `.gzkit/rules/cli.md` apply.
2. Put to the operator whether `.gzkit/mx.json` stays committed, or whether CI ignores it so the demoted guards run at full strength on each push.
3. Then the predecessor's order: RO-9 tranche 2 as its own session, specify RO-3, GHI #1259.

## Pending Work / Open Loops

- `tests/complexity/test_citation.py::TestRuleVersionConsistency` still restates the rule-version regex; recorded as an insight (scope `tests-rule-version`). It is a baselined tautological operation, so the fix moves the shrink-only ratchet too.
- `ledger_event_corrected` and `unowned_ratchet_updated` now fire but stay in the inertness baseline. `--report --write` refuses to drain while `obpi_lock_lease_expired` is never-fired in the live ledger.

## Verification Checklist

- `ls .gzkit/mx.json` exists, and `uv run gz obpi lock list` shows the session lock for 57346836 inside its TTL.
- `git log --oneline -1` is `80747fda8` or a later sync commit; `git rev-list --left-right --count origin/main...HEAD` reads `0 0`.
- `uv run python .gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py` exits 0.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (the 2026-10-20 drydock session cycle row)
- `src/gzkit/ledger_producer_probe.py`
- `tests/test_ledger_producer_probe.py`
- `tests/complexity/test_citation.py`

## Settled Rulings

1634 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
