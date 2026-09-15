---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T08:46:49Z'
agent: claude-code
session_id: 6cc9dfd9-da90-4bb4-a765-20351dcbe1fe
continues_from: 20260915T015620Z-fix-1010-json-stdout.md
---

## Current State Summary

Session 6cc9dfd9 continued past `20260915T015620Z-fix-1010-json-stdout.md`. The operator put two matters from that handoff back to the agent as canon questions, not open choices, and both were corrected against `docs/design/cli-standards-v3.md` (canonical per ADR-0.0.4) in `649be0d8e`, synced as `b0215dd71`.

- Verbosity levels now follow the spec § Verbosity Levels: default WARNING, `--quiet` ERROR, `--verbose` INFO, `--debug` DEBUG, all to stderr (`src/gzkit/cli/logging.py` `VERBOSITY_TO_LEVEL`).
- The entrypoint error boundary (`src/gzkit/cli/main.py` `main()`) reports GzkitError, unexpected exceptions and interrupts on `err_console` (stderr) in every mode, human or `--json`.
- `.gzkit/rules/cli.md` bumped to `0.8.0`: the drifted `--verbose` "Debug output" row realigned, `--debug` listed, verbatim verbosity bullet added; mirrors synced; 0.7.0 lifted to the rule version history.
- New enforcement claim `NC:cli-log-levels-follow-spec` (`src/gzkit/cli/helpers/log_level_claims.py`), wired into `_ensure_production_claims_registered`; advisory scorecard row 93 scored Mechanical citing it; Summary recounted.
- Verification: `gz check` exit 0; 10430 tests OK; mutation sweep 5/5 killed, conclusive.
- Measured the remaining class and recorded it on GHI #810: 127 red error lines in 42 command modules still print to stdout, plus JSON error objects in `obpi complete`, `obpi lock`, `obpi acceptance` and the adversary-workspace failure branch.

At authoring: HEAD `b0215dd71` level with origin/main, tree clean, no OBPI locks.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** unchanged this delta.
- **ghi triage:** #1010 closed (prior delta). #810 gained a measured comment on stdout error prints. Open at authoring, verified via `gh issue list`: #1011, #1009, #1008, #1003, #998, #997, #993, #983, #978, #973, #969, #968, #956, #950, #943, #939, #934, #930, #927, #926, #922, #921, #919, #907, #894, #871, #870, #837, #832, #818, #810 (and older).
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 still topmost.
- **new R&D:** not worked.

### Found this session
- The canonical CLI spec's § Document status table already declared Output Rules "Live, UNMET" with GHI #810 as the work order. The prior handoff's "open ruling" framings for the level map and `--json` error routing were agent drift, not operator decisions: canon answered both. Insight `agent/canon-before-question` records it and supersedes `cli/logging-verbosity-levels` and `cli/json-error-paths` as open-ruling framings.
- Of the 127 in-body red lines on #810, some are FAIL rows inside reports rather than errors, so each needs a reading before it moves to stderr; a blanket rewrite would misroute report output.
- The scorecard surface-fidelity gate requires a Mechanical row's text to appear verbatim as a bullet in the per-turn rule; the private cross-package import ratchet refuses a claim module importing a `_private` CLI helper (hence `configure_logging_from_flags` is public).
- `FORCE_COLOR=3` remains set in this shell; probe Rich output with `env -u FORCE_COLOR`.

## Decisions Made

- [operator-ruled] Verbosity default follows the canonical spec rather than the adapter (verbatim: "why would we NOT follow spec? on --json, what is our standard approach for other modules?"). Landed `649be0d8e`.
- [operator-ruled] A question canon already answers is not put to the operator as an open decision (verbatim: "if we have all of that foundational documentation, then why did you ask those questions? are you saying that we have an entire application (gzkit) that is non-standard on this?"). Recorded as insight `agent/canon-before-question`.
- [agent-chose] Applied `cli-standards-v3.md` § Output Rules and `cli.md` § Output Contracts to `--json` failures: errors go to stderr at the shared boundary, stdout carries only the document; no new JSON error envelope was invented.
- [agent-chose] Built the NC claim `cli-log-levels-follow-spec` rather than downgrading scorecard row 93 when the Coverage Ledger refused a Mechanical row without one.
- [agent-chose] Did not blind-rewrite the 127 per-site red error lines; measured the population and posted it on GHI #810 for per-site repair.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts: (a) the frontier-model-card-currency scan (#934 drift); (b) the 36-overdue chores board; (c) a ruling on insight `chores/staleness-gate-class-fit`; (d) R&D skill design per `20260912T235557Z` step 4; (e) a short direct fix, #1008; (f) direct repair of the GHI #810 stdout error-print population measured this session.
2. If (e): #1008 is the verifier-pipe gate not recognizing a verifier inside a ( ) or { } group; start from `gzkit.verifier_pipe_gate.decide`.
3. If (f): start from the measured comment on GHI #810; read each red line in context (error vs report FAIL row) before routing it to `err_console`, and treat the JSON error objects in `obpi_complete.py`, `obpi_lock.py`, `obpi_acceptance.py` and `obpi_adversary_workspace.py` as the same class.

## Pending Work / Open Loops

- GHI #810: per-site error prints to stdout (127 red lines in 42 modules; JSON error objects in the obpi complete/lock/acceptance verbs and the adversary-workspace failure branch). The shared boundary is fixed; the in-body sites are not.
- GHI #934 (frontier drift), #1008 (verifier-pipe groups), #1009 (accumulated-work counters), #1011 (CHORE.md drift), #997 and #808 (chores); #983 and #894 ruling-gated; #969 open by ruling; #968 open.
- Insights awaiting operator calibration: `chores/staleness-gate-class-fit`, `chores/staleness-signal-fit`, `cli/manpage-flag-claims`. `cli/logging-verbosity-levels` is resolved by `649be0d8e`; `cli/json-error-paths` is resolved at the boundary and its residue lives on #810.
- `--log-file` named by the spec's Logging section is still absent (recorded in the spec's status row).
- Carried: permission-consent-drift lacks `proofs/settings-patch.md`; `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes a non-canonical unittest step; three live justify-binding violations; 83 enforcement claims population-undeclared and 55 exemption-undeclared.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run -m unittest tests.test_logging tests.cli.test_errors_reach_stderr tests.cli.test_log_level_claims tests.cli.test_json_stdout_log_isolation > "$CLAUDE_JOB_DIR/tmp/v.log" 2>&1; echo "exit $?"
uv run gz validate --advisory-scorecard; echo "exit $?"
gh issue view 810 --json state,comments --jq '.state, (.comments | length)'
```
Expected: level with origin/main; no locks; tests exit 0; scorecard exit 0; #810 OPEN with the measured comment. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T015620Z-fix-1010-json-stdout.md` (predecessor).
- `src/gzkit/cli/main.py`, `src/gzkit/cli/logging.py`, `src/gzkit/commands/common.py`, `src/gzkit/cli/helpers/log_level_claims.py`, `src/gzkit/enforcement.py`.
- `tests/test_logging.py`, `tests/cli/test_errors_reach_stderr.py`, `tests/cli/test_log_level_claims.py`, `tests/cli/test_json_stdout_log_isolation.py`.
- `.gzkit/rules/cli.md`, `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md`, `docs/design/cli-standards-v3.md`.
- `.gzkit/insights/agent-insights.jsonl` (insight scope agent/canon-before-question).
- `artifacts/receipts/arb-ruff-acf09082217d49778cd633b33524edf1.json`, `artifacts/receipts/arb-step-typecheck-3c2c2d2928bb4b0a8f0098d0abccf0ca.json`, `artifacts/receipts/arb-step-unittest-f22dccc3ea42438db33d44c2c6365b89.json`.
- Commits `649be0d8e` and `b0215dd71`; measured comment on GHI #810.

## Settled Rulings

868 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
