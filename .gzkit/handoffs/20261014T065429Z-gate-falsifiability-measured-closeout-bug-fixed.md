---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-14T06:54:29Z'
agent: claude-code
session_id: c3ad8afb-53ff-4ce1-99cc-8f63f8baed0e
continues_from: .gzkit/handoffs/20261013T233324Z-brief-size-canaries-reviewed-nothing-in-flight.md
---

## Current State Summary

This session did no OBPI work. It resumed the predecessor, started a re-cut of briefs OBPI-0.35.0-16 to -20, stopped it at the operator's challenge on modularity, measured which gates can fail, fixed one live defect and filed thirteen issues.

- Re-cut of OBPI-0.35.0-16 to -20: a 23-brief cut was proposed and challenged by the operator as not modular. It regrouped the old briefs' REQ lists, and several proposed briefs still spanned three or more modules. No checklist row, brief or scorecard was edited. Its three decisions (granularity, withdraw or narrow the old briefs, raising Baseline Selected) are unruled.
- Gate measurement at 60b994228 over the 161 gates gzkit inventories from code: 56 carry a registered enforcement claim and 105 do not. All 123 registered controls pass when run read-only. Each if-statement in each gate's own deciding function was replaced by pass, one at a time (487 removals), with the tests that name the function run. 88 gates had at least one removal fail a test assertion, and 54 of those also had removals no test noticed. 62 gates are unmeasured by this method: 27 whose decision sits in a helper, loop or returned list, and 35 with no guard at the inventory's depth.
- Of the 38 gates no targeted test noticed, three read-only readers classed 112 guards: 29 refusals, 56 stricter, 27 equivalent. Each refusal was removed alone and the full unit suite (11798 tests) run: 17 caught by an assertion, 3 only by an error, 1 only by the gate-inventory bytecode test, 12 by nothing.
- Fixed in 0e74d8f52 (GHI #1211): the closeout prompt's Partial choice always raised, and with a reason crashed with UnboundLocalError. RED observed, GREEN after a one-line indent fix, arb red verdict driven.
- Filed GHI #1211 and one GHI per untested refusal, #1212 to #1223; evidence added to GHI #1155.
- The session ends with the operator's git-sync, which pushes 0e74d8f52, the insight records and the ledger rows.

## Important Context

- THE OPERATOR'S STANDING VERDICTS THIS SESSION, verbatim: "gzkit is a house of cards, a ruse, and charade, all at the same time - DISMAL failure"; "you do this frequently, now I do not know what to trust"; on the measurement's limits paragraph, "this sounds sloppy". Report every measurement as counts, each saying what it shows and what it does not. Put unmeasured items first. Never fold them into a total.
- This session's reporting errors, each corrected in the insight store: the reconcile-receipt refusals of gz obpi complete were called verified untested, and they are tested by a suite that never names the function; six closeout gates were called verified, and their guards had not been read; 31 of 38 gates were said to have tests, and 27 of those are unmeasured.
- The name-based test selection of the first sweep missed real tests that drive the CLI or mock the function, so a survived result there is not evidence of an untested gate. The full-suite rerun is the evidence for the 29 refusals only.
- The sweep tooling lived in this session's scratchpad and is gone with it. The method: AST-enumerate if-statements in each gate's deciding functions from gate_enrollment.scope_population and gate_population.population_members, splice one to pass, run tests with a fresh PYTHONPYCACHEPREFIX in an isolated worktree with the worktree's .venv/bin first on PATH (several tests shell out to lizard and cohesion).
- A full unit-suite run takes about 95 seconds alone and about 4 minutes when two run side by side.
- The decomposition watchers were surveyed: the Matrix of Four overlay rules have no mechanical witness found by keyword search; gz specify checks only checklist count against the scorecard target; gz obpi validate --authored has a floor and no ceiling; the adr evaluate Size score cannot fail (GHI #1197); ADR-0.35.0's evaluation scorecard is dated 2026-09-06 and never scored briefs 15 to 20. The four split adders in src/gzkit/core/scoring.py are 0 or 1 and all four are already 1 on ADR-0.35.0.
- Workflow fronts (source: the active campaign plan, section Workflow fronts). adr/obpi campaign: not worked; the re-cut of items 16 to 20 is open and only the operator initiates OBPI work. ghi triage: thirteen issues filed and one fixed; the queue was not read as a whole. handoff system: used, not changed. new R&D: not touched.

## Decisions Made

- [operator-ruled] Take up the re-cut of briefs OBPI-0.35.0-16 to -20 (verbatim: "recut"). Booked with gz handoff decide on the predecessor.
- [operator-ruled] No letter-suffixed ids for re-cut briefs (verbatim: "i dan't want NNa as an id system").
- [operator-ruled] Measure which gates can actually fail before more re-cut work (verbatim: "measure which gates can actually fail").
- [operator-ruled] Read the remaining 23 unnoticed and 11 errors-only gates line by line (verbatim: "read the remaining 23 and the 11 line by line").
- [operator-ruled] Prioritize repairing the live closeout bug; file one GHI per finding; remove the five sweep worktrees (verbatim: "Prioritize repairing this", "1. one GHI each. 2. yes").
- [operator-ruled] Close the session with a fresh handoff and a git-sync (verbatim: "write fresh handoff then git sync").
- [agent-chose] Filed one GHI per untested guard, twelve in all, reading "one GHI each" literally, and cross-noted the two pairs that test the same check (lines 206 and 209, 221 and 229 of code_quality.py).
- [agent-chose] Did not close GHI #1211 or #1222 before the push, because the fix commit was not yet on origin.
- [agent-chose] Delegated the line-by-line read to three read-only subagents, then confirmed each refusal by a full-suite run and confirmed the closeout defect by reading the code.

## Immediate Next Steps

1. Present this handoff to the operator and take their ruling before executing anything. Confirm with git status --short, git rev-list --left-right --count origin/main...HEAD and gh issue view 1211 --json state.
2. If 0e74d8f52 is on origin and GHI #1211 or #1222 is still open, close each through ghi-close citing 0e74d8f52, tests/test_closeout_attestation_prompt.py and receipt arb-red-commit-0e74d8f5291b-19ac458ba5f54219a8aadda99bd716c8.
3. Put to the operator how the 62 unmeasured gates are measured: for the 27, mutate the deciding helper or loop each reader named; for the 35, drive the gate with a planted violation, since most shell out to another tool.
4. Put to the operator whether the twelve test-only issues GHI #1212 to #1223 are repaired as direct fixes now, and in what order.
5. Before any further re-cut of OBPI-0.35.0-16 to -20, cut from the code's modules and show the Matrix of Four tests per proposed brief; the three re-cut decisions remain the operator's.

## Pending Work / Open Loops

- Untracked findings from the line-by-line read, each recorded only as reader output: test_next_and_attest_conflict in tests/test_closeout_ceremony_cmd.py cannot fail; the lite-lane receipt test does not check that no meta-receipt-bind event is appended; the audits event_schemas, validator_fields, pool_adr_isolation, reconcile_freshness and event_handlers return green when their input file is missing; the reconcile-receipt staleness check skips a brief with an empty allowlist.
- Untracked decomposition findings, recorded as an insight: the Matrix of Four overlay rules have no witness; evaluation is not re-run when a checklist grows; ADR-0.35.0's scorecard shows Feature Checklist scored 1 under a STRUCTURALLY COMPLETE verdict. The operator was asked whether to file them and did not rule.
- Guards in the 88 gates shown able to fail that no test noticed have not been read.
- Carried from the predecessor and not acted on: GHI #1197, #1200, #1203 to #1210 open; OBPI-0.35.0-11, -12, -13 and -16 to -20 pending; OBPI-0.35.0-09 repudiated.

## Verification Checklist

- git log --oneline -1 origin/main shows 0e74d8f52 or a later commit containing it.
- uv run -m unittest tests.test_closeout_attestation_prompt runs 5 tests and passes.
- ls artifacts/receipts lists arb-red-commit-0e74d8f5291b-19ac458ba5f54219a8aadda99bd716c8.
- gh issue view 1212 --json state through 1223 read OPEN; 1211 and 1222 read CLOSED once step 2 is done.
- uv run gz validate --gate-enrollment exits 0 and reports 102 validate scopes and 59 other gates.
- uv run gz obpi lock list prints No active locks.

## Evidence / Artifacts

- `src/gzkit/commands/closeout.py` (the one-line fix at line 239, commit 0e74d8f52)
- `tests/test_closeout_attestation_prompt.py` (5 tests, GHI #1211)
- `.gzkit/insights/agent-insights.jsonl` (records gate-falsifiability, reporting-measurements, obpi-recut-adr-0.35.0, obpi-decomposition-watchers, gz-closeout, with corrections)
- `src/gzkit/governance/trust_audits/gate_population.py` and `src/gzkit/governance/trust_audits/gate_enrollment.py` (the gate inventories the measurement read)
- `src/gzkit/core/scoring.py` (split adders limited to 0 or 1)
- `docs/governance/GovZero/obpi-decomposition-matrix.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/EVALUATION_SCORECARD.md`
- Issues: GHI #1211 to #1223 filed; comment on GHI #1155.

## Settled Rulings

1530 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
