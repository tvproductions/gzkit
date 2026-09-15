---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T08:54:52Z'
agent: claude-code
session_id: 6cc9dfd9-da90-4bb4-a765-20351dcbe1fe
continues_from: 20260915T084649Z-cli-spec-verbosity-stderr.md
---

## Current State Summary

Refresh of `20260915T084649Z-cli-spec-verbosity-stderr.md` on operator instruction ("update handoff"). No commit, ledger event or working-tree change landed between that document and this one; it remains an accurate account of the session's work (`649be0d8e` verbosity levels and error output follow the canonical CLI spec, synced `b0215dd71`, handoff `7a202dcbe`), so its Important Context, Pending Work, Verification Checklist and Evidence carry forward unchanged.

What this refresh changes:
- Every carried claim was re-verified against live state at authoring: level with origin/main, no OBPI locks, GHIs #808 #810 #894 #934 #968 #969 #983 #997 #1008 #1009 #1011 all OPEN, chores board 36 overdue / 1 due / 3 unmeasured, and both of this session's operator rulings present in `rulings.jsonl` (`gz handoff rulings --search`).
- Advised step (c) is rewritten. It asked for "a ruling on insight `chores/staleness-gate-class-fit`" as an open prompt, the shape the operator corrected this session (AGENTS.md § Operator Economy #7). Canon speaks to it, and so does a later operator ruling on the same mechanism; the step now carries both, quoted, so the next session presents a named inconsistency rather than a menu.
- The pending note on insight `chores/staleness-signal-fit` gains the canon that bears on it.

At authoring: HEAD `7a202dcbe` level with origin/main, tree clean, no OBPI locks.

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

- [agent-chose] Authored a successor rather than editing `20260915T084649Z` in place: a committed handoff is a record, its rulings were booked at write time, and `continues_from` keeps the lineage traversable.
- [agent-chose] Did not reclassify `chores/staleness-gate-class-fit` as canon-settled. `docs/governance/chore-class-system.md` § Indicator, not gate reads "Staleness **announces**. The one exception is Currency, where staleness makes the chore assert something false; that class may gate", yet six non-Currency chores run `scripts/check_proof_freshness.py` as an acceptance criterion, and the 2026-09-14 GHI #935 ruling ("Declare it (Recommended)") repaired that very criterion for `control-surface-permission-consent-drift` (class conformance) instead of removing it. Whether a run-freshness criterion is a staleness gate in the doctrine's sense is a reading the two sources disagree on, so it is surfaced (Behavior Rules — Always #9), not resolved.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts: (a) the frontier-model-card-currency scan (#934 drift); (b) the 36-overdue chores board; (c) the chore staleness-gate inconsistency below; (d) R&D skill design per `20260912T235557Z` step 4; (e) a short direct fix, #1008; (f) direct repair of the GHI #810 stdout error-print population.
2. If (c): present it as an inconsistency, both sides quoted, never as an open menu. Canon: `docs/governance/chore-class-system.md` § Indicator, not gate, "Staleness **announces**. The one exception is Currency … that class may gate." Measured: seven chores run `scripts/check_proof_freshness.py` as an acceptance criterion; one is Currency (`frontier-model-card-currency`), six are not (`control-surface-permission-consent-drift` conformance; `control-surface-rule-conflicts`, `-rule-vs-check-drift`, `-skill-rule-reachability`, `-validator-reachability`, `ledger-vocabulary-inertness` coherence). Tension: the GHI #935 [settled] ruling repaired the permission-consent-drift criterion's witness shape rather than retiring it. The question for the operator is only whether a chore's run-freshness criterion counts as a staleness gate; if it does, the six are corrections under canon.
3. If (e): #1008 is the verifier-pipe gate not recognizing a verifier inside a ( ) or { } group; start from `gzkit.verifier_pipe_gate.decide`.
4. If (f): start from the measured comment on GHI #810; read each red line in context (error vs report FAIL row) before routing it to `err_console`, and treat the JSON error objects in `obpi_complete.py`, `obpi_lock.py`, `obpi_acceptance.py` and `obpi_adversary_workspace.py` as the same class.

## Pending Work / Open Loops

- GHI #810: per-site error prints to stdout (127 red lines in 42 modules; JSON error objects in the obpi complete/lock/acceptance verbs and the adversary-workspace failure branch). The shared boundary is fixed; the in-body sites are not.
- GHI #934 (frontier drift), #1008 (verifier-pipe groups), #1009 (accumulated-work counters), #1011 (CHORE.md drift), #997 and #808 (chores); #983 and #894 ruling-gated; #969 open by ruling; #968 open.
- Insights awaiting operator calibration: `chores/staleness-gate-class-fit`, `chores/staleness-signal-fit`, `cli/manpage-flag-claims`. `cli/logging-verbosity-levels` is resolved by `649be0d8e`; `cli/json-error-paths` is resolved at the boundary and its residue lives on #810.
- `--log-file` named by the spec's Logging section is still absent (recorded in the spec's status row).
- Carried: permission-consent-drift lacks `proofs/settings-patch.md`; `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes a non-canonical unittest step; three live justify-binding violations; 83 enforcement claims population-undeclared and 55 exemption-undeclared.
- Insight `chores/staleness-signal-fit` (quality-check, memory-hygiene): its next_action says signal choice "was calibrated with the operator at chore-class-system step 5", but step 5's as-landed record says only the control-surface five were calibrated one at a time. Canon that bears on it before any question: § Four signals, not interchangeable (content delta fits Conformance/Coherence, accumulated work fits Curation, elapsed time fits Mining/Currency) and step 5's precedent that `decommission-tautological-tests` declares a signal by subject over class. quality-check is class conformance on content delta (fits the table); memory-hygiene is class curation on content delta (does not). The 2026-09-14 GHI #936 [settled] ruling "Declare content-delta (Recommended)" covered all 30 content-delta chores, so changing either signal touches a booked ruling.

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

- `.gzkit/handoffs/20260915T084649Z-cli-spec-verbosity-stderr.md` (predecessor, refreshed by this document); `.gzkit/handoffs/20260915T015620Z-fix-1010-json-stdout.md` (its predecessor).
- `docs/governance/chore-class-system.md`, `.gzkit/chores/registry.json`, `.gzkit/chores/control-surface-permission-consent-drift/acceptance.json` (read for the step (c) and signal-fit reframing).
- `src/gzkit/cli/main.py`, `src/gzkit/cli/logging.py`, `src/gzkit/commands/common.py`, `src/gzkit/cli/helpers/log_level_claims.py`, `src/gzkit/enforcement.py`.
- `tests/test_logging.py`, `tests/cli/test_errors_reach_stderr.py`, `tests/cli/test_log_level_claims.py`, `tests/cli/test_json_stdout_log_isolation.py`.
- `.gzkit/rules/cli.md`, `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md`, `docs/design/cli-standards-v3.md`.
- `.gzkit/insights/agent-insights.jsonl` (insight scope agent/canon-before-question).
- `artifacts/receipts/arb-ruff-acf09082217d49778cd633b33524edf1.json`, `artifacts/receipts/arb-step-typecheck-3c2c2d2928bb4b0a8f0098d0abccf0ca.json`, `artifacts/receipts/arb-step-unittest-f22dccc3ea42438db33d44c2c6365b89.json`.
- Commits `649be0d8e` and `b0215dd71`; measured comment on GHI #810.

## Settled Rulings

870 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
