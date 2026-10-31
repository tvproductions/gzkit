---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-31T09:11:56Z'
agent: claude-code
session_id: 2a8a16ab-25db-4f3a-8df7-7842ee3d1faa
continues_from: .gzkit/handoffs/20261031T072021Z-ro13-and-ro5-change-order-specified.md
---

## Current State Summary

Drydock safe mode, RO-0. RO-12's first precondition is done: GHI #1273's written review, its three rulings and its repair landed on main through ca318dab2, and #1273 and #1263 are closed with evidence. CI run 41186366297 on ca318dab2 has check green on ubuntu and windows; full-strength-report is red on the tautological audit alone, by design report-only. The last full unit run passed 12,950 tests with 4 skipped, before one test was added to tests/mx/test_mx_log.py, which was re-run alone. Last action: this handoff and the git sync.

## Important Context

The review found the R&D run had already ruled the model on 2026-10-27, so it audited every reader against it; read docs/governance/harbor-1273-mx-signal-review.md before touching the MX signal. marker.condition is the one reading for anything that lowers protection; is_active stays for the four readers that raise it; is_valid stays for readers asking whether the session is open. The session id comes from the harness and survives gz mx exit, so a close counts only until the next open: the open set is ordered in the marker, the banner, the hook fallback, hardening.open_sessions and the log. At the drydock level the pre-push hook does not run gz check, it runs gz lint, so a pre-push pass proves only lint; the previous handoff's claim of a passed pre-push gz check proved nothing, and gz-session-handoff 7.7.2 now says so. mx_session_opened keeps mode in the ledger; only the marker writes level. Two reviewers failed the repair before a third confirmed it, by reading only; the failures were real, so send MX changes to an independent reviewer. In zsh an unquoted variable does not split words and ===NAME fails, which cost one invalid red run here; a bulk sed over a file with dated records rewrote two of them and they were restored; check the commit actually landed, because refused commits printed the previous head and passed unnoticed several times. Shift turnover: gz obpi lock list showed only mx-session at the last read, this session's review of the contract's list of discrepancies covered the RO-0 lines, no tags are hung because the tag-out log does not exist until RO-12, no finding awaits buy-back, and no work package is commenced, WP-01 being closed. Workflow fronts (docs/governance/build-to-1.0-campaign-2026-09-20.md#workflow-fronts): this session worked the adr/obpi campaign front through the drydock and closed two issues on the ghi triage front; handoff system and new R&D were not worked.

## Decisions Made

- [operator-ruled] The four readers of the file itself keep presence; the one reading governs what lowers protection (verbatim: "a").
- [operator-ruled] The level is a new marker field, hangar or drydock, with mode read as its alias and the ledger's mode untouched (verbatim: "a").
- [operator-ruled] The recovery the announcement names is a new verb under gz mx, not plain git commands (verbatim: "b").
- [operator-ruled] Start the repair now with the verb as gz mx repair (verbatim: "a").
- [agent-chose] gz mx repair also rewrites a marker a killed exit left exiting, and refuses on two open sessions.
- [agent-chose] Landed the verb before the banner so the banner names a verb that exists; landed the level and the CI job in one commit because their tests share a file.
- [agent-chose] Closed #1273 and #1263 together on the third reviewer's confirmation, one comment each, #1263 as absorbed with its switch moved to the report-only job the operator ruled.
- [agent-chose] Graded the 7 tautological-test findings as blocking return to service, because gz mx exit would refuse on them.

## Immediate Next Steps

1. Continue RO-12's preconditions as direct fixes: put #1200, #1206, #1208 and #1028 to the operator in that order, one question at a time, with the other reused-part defects RO-12's row lists.
2. File the rebase trap through ghi-author: insight scope mx-1273, the post-commit recorder appending artifact_edited rows during a rebase.
3. Ask the operator to look at the Mermaid drawing at docs/governance/harbor-pilotage-candidate-2026-10-15.md line 84; it was never observed rendering.

## Pending Work / Open Loops

- The 7 tautological-test findings are open on the contract's list of discrepancies, blocking return to service.
- #1272 and #1289 stay open, owned by RO-13's F5; the solo validator scopes go to RO-13's enumerator and R1.
- RO-13's T0 tables are undrafted, owed before the retrofit.
- RO-4 ruling 6 against RO-8 ruling 1 remains open.
- The orientation hook output is over its injected-text budget, measured at 4366 B in the previous session.
- Known limits in the review: gz mx repair raises when the ledger itself cannot be parsed; the stdlib banner cannot see a schema failure; a value such as "exiting": "no" reads differently in the banner; SIGKILL during an exit leaves exiting for a retry or the repair.
- No red run stands for 0af0ab891, and gz arb red was not run on these commits because the commit witness is off in safe mode.
- The MX session has carried advisory debt past its lease; gz mx renew needs --attestor when the lease lapses.

## Verification Checklist

- git status -sb reads main in step with origin/main.
- gh issue view 1273 --json state shows CLOSED, and gh issue view 1263 --json state shows CLOSED.
- uv run python -c 'from gzkit.mx import marker; print(marker.condition().cause, marker.read().level)' prints on drydock.
- uv run gz mx repair --help shows the verb.
- uv run gz handoff rulings --search 'keep presence' returns the ruling.
- gh run list --branch main --workflow CI --limit 1 shows the latest run; a red conclusion there can be the report-only job, so read the job list.
- uv run gz obpi lock list shows the mx-session lease.

## Evidence / Artifacts

- `docs/governance/harbor-1273-mx-signal-review.md`
- `src/gzkit/mx/marker.py`
- `src/gzkit/mx/checkpoint.py`
- `src/gzkit/mx/alarms.py`
- `src/gzkit/mx/awareness.py`
- `src/gzkit/mx/hardening.py`
- `src/gzkit/mx/log.py`
- `src/gzkit/commands/mx_cmd.py`
- `src/gzkit/hooks/scripts/mx.py`
- `docs/user/manpages/mx-repair.md`
- `tests/mx/held.py`
- `tests/commands/test_mx_repair.py`
- `.github/workflows/ci.yml`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- Commits 5066b9c44 through ca318dab2 on main.

## Settled Rulings

1891 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
