---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-18T00:57:47Z'
agent: claude-code
session_id: b5ddbaec-c545-40e5-814b-4b751e91e748
continues_from: .gzkit/handoffs/20261117T105912Z-ci-green-canaries-reviewed.md
---

## Current State Summary

RP-12 O3 task 3 is now repaired and re-reviewed; task 4 has not started. The operator ruled the predecessor handoff "Proceed: renew, then 3" (booked by gz handoff decide, steps 4 and 5 set aside), renewed the expired mx-session lease (d4b0928e7), and the session repaired every finding of task 3's independent review in five acts:
- 8a84c9839: the hang's stamp refusal names a step that can succeed, never the failed call; a hang on an opened, never-frozen order tested; the hang manpage EXAMPLES recaptured.
- 3fb182bb4: Restoration on a blocked and on an accepted order tested; the blocked fragments tightened.
- 9c1dd6616: gz's entry keeps a stamped id only beside a stamped root, two held wiring tests, both mutants killed by a conclusive run_mutation_sweep; the unstamped test asserts its reason.
- 784454bed: found in flight, a craftsman dispatch's booking line named its order twice.
- 610abf779: the kit's Mode Contract rows (the craftsman roles, the hang refusals, the issue and hang races as (O) limitations), wp-dispatch.md with captured Repair and Restoration EXAMPLES, the parser, events.py, both runbooks, the hang manpage's exit 2 and the gz-wp skill's step order.

A second independent reviewer, which did none of the work, read those five and found ten more; each was re-verified before acting. Nine were repaired: b290a7d2b (the unstamped refusal names a dispatch only as it may be; exit 2 includes an unknown flag; dates are the local 2026-11-17), 8e6133b56 (the blocked fragments name their order), 8b7981f1b (ruling 104's count, one high since 4dd618fe7, corrected to 36 as gz validate --hexagon-tests reports; the remaining commenced-only dispatch text; the hang row's rulings; rulings 134 and 135 in the governance runbook and skill). The tenth was put to the operator and ruled as ruling 136: gz wp runs reports a frozen order holding a live dispatch (a38024152).

Every act ran gz check under ARB (exit 0, the four demoted guards advisory) and gz arb red --commit; the full unit tier passed at a38024152 (13,897 tests); main was pushed to a38024152. CI passed at 8b7981f1b and was in progress at a38024152 when this was written.

## Important Context

- Safe mode (drydock) is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; MX session 57346836, its lease renewed 2026-11-18T00:02Z (UTC) for 24h; gz obpi lock list read the mx-session lock alone, active, 55 of 1440 minutes, held by claude-code-b5ddbaec. Every act is one commit with Task: TASK-rnd-repair-work-organization.
- Shift turnover: no tag is hung in the live repository, no work package is commenced, no finding awaits buy-back; this session hung, issued and commenced nothing in the live repository (every hang and dispatch ran in temporary test projects). Read: gz obpi lock list and the contract's list of discrepancies.
- Commit-witness verdicts to know: 610abf779, b290a7d2b and 8b7981f1b read no-tests, each changing help, docstring, description or refusal wording alone, where a string-pinning test is what the tests rule forbids; a38024152 reads undriven, its survivor src/gzkit/work_package_run.py:180-182, the RunPosition.state description. The ledger row of a38024152's witness is uncommitted and rides with this handoff's commit, whose message discloses that survivor.
- Ruling 104's held-test line now reads 36, matching gz validate --hexagon-tests (test_wp_acceptance 4, test_wp_order 7, test_wp_req 3, test_wp_run 4, test_wp_tag 18); count the validator's findings before amending it again.
- Manpage EXAMPLES are captured by subclassing a wiring-test fixture (tests.commands.test_wp_tag.TagHangWiringTests) and invoking gz's main in-process; the stamp is consumed after a passing call (ruling 37), so re-stamp before a repeat call; ids differ per run, so take every example of a page from one run. Dates in records are the local date.
- Never write an unquoted heredoc carrying backticks: the shell executes them (GHI #1147, observed this session, nothing harmful ran). Write edit scripts to the scratchpad and run them.
- run_mutation_sweep needs a unittest -v command, or it reads no executed tests and grades every mutant inconclusive.

## Decisions Made

- [operator-ruled] Ruling on the predecessor handoff, booked by gz handoff decide with steps 4 and 5 set aside (verbatim: "Proceed: renew, then 3").
- [operator-ruled] An independent review of the five repair acts before pushing (verbatim: "Review, then push").
- [operator-ruled] Ruling 136, gz wp runs reports a frozen order holding a live dispatch (by selection: "Yes, report it").
- [operator-ruled] Push a38024152 (verbatim: "Push it").
- [operator-ruled] Write a fresh handoff and git sync (verbatim: "fresh handoff and git sync").
- [agent-chose] Cut step 3 into acts A to D by surface (refusal code, unheld tests, held wiring tests, docs) rather than one act per finding.
- [agent-chose] Fixed the craftsman dispatch's doubled booking line in flight as a direct fix, its own act.
- [agent-chose] Stated the tag issue's same check-then-append race as a limit beside the hang's, the class of the review's finding 9.
- [agent-chose] Left the no-tests verdicts on description-only commits standing, writing no string-pinning test to satisfy the witness.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's id.
2. Read CI on a38024152 (gh run list --workflow CI --limit 1); if check is red, repair it before anything else.
3. Open O3 task 4 (clearance authorized and clear, refusal 1, the SubagentStop hook booking dispatch_ended, the not-available mark of rulings 7 and 118): a planning pass checked against the code, then its open questions one at a time, the first what an out-of-position clear does before O5's stop record exists.
4. Then O3 tasks 5 (commencement reads tags, acceptance refuses a hung tag, the frozen-order fence; rulings 108, 116, 117), 6 (the MX session as holder in gz mx enter and renew, and renew booking a lapsed lease's expiry) and 7 (the dock trial, refusals 1, 2 and 6 red then green under an independent inspector).

## Pending Work / Open Loops

- The check-then-append races of the tag issue and the tag hang are stated as (O) limitations; no refusal holds two concurrent writers apart yet.
- Ruling 104's RP-11 line holds 36 untagged held tests, cleared when RP-11's intake admits REQs and gz validate --hexagon-tests reports none of them, before gz mx exit.
- The four hexagon canaries leave the kernel checker and HEXAGON_TEST_BREACHES unmutated (GHI #1266, open).
- The per-change gz check misses whole-suite fences (insight 2026-11-17T07:11Z, open); run uv run gz test before calling an act done.
- Carried: gz mx renew books no expiry for a lease that lapsed mid-session (O3 task 6); the four demoted guards; refusal prose that cites no rule; the MX session's advisory debt; open siblings #1314 and #1316.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz test passes (13,897 tests at a38024152).
- uv run -m unittest tests.test_tag_out tests.test_order_run tests.commands.test_wp_tag tests.commands.test_wp_run passes.
- uv run gz validate --hexagon-tests reports 36 findings, the count ruling 104's line carries.
- uv run gz handoff rulings --search "Yes, report it" returns ruling 136.
- uv run gz obpi lock list shows the mx-session lock alone.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` (ruling 136, the Mode Contract's order-run, issue and hang rows)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (ruling 104's line at 36)
- `src/gzkit/mx/tag_out.py`
- `src/gzkit/work_package_run.py`
- `src/gzkit/commands/wp.py`
- `tests/test_tag_out.py`
- `tests/test_order_run.py`
- `tests/commands/test_wp_tag.py`
- `tests/commands/test_wp_run.py`
- `docs/user/manpages/wp-dispatch.md`
- `docs/user/manpages/wp-tag-hang.md`
- `docs/user/manpages/wp-runs.md`
- `.gzkit/skills/gz-wp/SKILL.md`

## Settled Rulings

2309 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
