---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-15T09:48:30Z'
agent: claude-code
session_id: f6dec6b5-558f-4ce0-bac2-a6eb07ccb646
continues_from: 20260915T085452Z-handoff-refresh-canon-routing.md
---

## Current State Summary

Resumed `20260915T085452Z-handoff-refresh-canon-routing.md`; operator chose advised step (e), booked via `gz handoff decide` (steps c and f set aside).

GHI #1008 is FIXED and CLOSED by `7d113edbd`, pushed to `main`: the verifier-exit-status gate now reads `( … )` and `{ …; }` as one command, so a grouped verifier is masked or escaped on the same terms as a bare one. Evidence: 225 tests OK across the gate, packet-replay and hook suites; mutation sweep 26 killed / 0 survived / 0 invalid / 0 inconclusive; 732 committed transcripts with 0 verdict changes; `uv run gz check` all passed. Rule `tests.md` is at 0.25.0 with mirrors synced; scorecard row 66 and its version pin are updated.

Two independent findings filed via `/ghi-author`, both open: #1012 (reserved-word prefixes and `$( … )` hide a verifier) and #1013 (heredoc bodies read as shell statements).

The operator objected to the cost of a fix offered as short. Recorded as insight `agent/verification-scope-on-short-fixes`.

At authoring: HEAD `7d113edbd` level with origin/main, tree clean apart from this handoff and the insight line, no OBPI locks.

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** unchanged this delta.
- **ghi triage:** #1008 closed. #1012 and #1013 opened. Open, verified this session: #1013, #1012, #1011, #1009, #997, #983, #969, #968, #934, #894, #810, #808 (and others; 43 open before this session's two).
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 still topmost.
- **new R&D:** not worked.

### Found this session
- The gate reads heredoc bodies as statements. Writing any heredoc whose prose contains `; <verifier> …` (commit messages, attestation text, issue bodies) gets refused. Use a file (`git commit -F file`, `gh issue create --body-file`) until #1013 lands. This is not a bypass: no verifier runs.
- `shlex` merges adjacent punctuation (`);`, `;(`). `gzkit.verifier_pipe_gate._split_paren_runs` splits only runs that close or open shell-syntax parens, never a word-led one.
- `FORCE_COLOR=3` remains set in this shell.
- A mutation sweep rewrites the source file while it runs. Do not edit or test that module until the sweep reports.

## Decisions Made

- [operator-ruled] Resume ruling on `20260915T085452Z-handoff-refresh-canon-routing.md`: "e" (short direct fix #1008). Steps (c) chore staleness-gate inconsistency and (f) #810 set aside.
- [agent-chose] Unbalanced parens keep the exact pre-#1008 token reading rather than the split reading. The split fallback caught one more genuinely masked shape but also refused heredoc prose; heredoc handling belongs to #1013.
- [agent-chose] Repaired `(verifier &); ls` inside #1008 rather than declaring it, as an omitted member of the contract's own "separators inside a group" boundary.
- [agent-chose] Filed reserved-word/substitution residue (#1012) and heredoc misreading (#1013) as separate issues: different mechanisms, both declared in `UNWITNESSABLE`.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts: (a) frontier-model-card-currency scan (#934 drift); (b) the 36-overdue chores board; (c) the chore staleness-gate inconsistency carried from `20260915T085452Z` step 2, still unruled; (d) R&D skill design per `20260912T235557Z` step 4; (e) #1013 heredoc bodies, which blocks ordinary heredoc authoring; (f) direct repair of the GHI #810 stdout error-print population.
2. If (e): the contract is on #1013. Its uncertainty that needs measuring first: a body fed to a shell (`bash <<EOF`) is code and must not be elided into a silent permit. Keep verification to the contract's named evidence (insight `agent/verification-scope-on-short-fixes`).
3. If (c): present it as the named inconsistency quoted in `20260915T085452Z` step 2, never as an open menu.

## Pending Work / Open Loops

- GHI #1013 (heredoc bodies read as statements; 52 false refusals at HEAD in session history plus an apostrophe fail-open). GHI #1012 (reserved-word prefixes and `$( … )`; 0 committed occurrences).
- Independent, untracked except here: the shared lexer reads a quoted lone metacharacter (`echo "|" x`) as an operator, so the `shell_reading` docstring claim that a quoted metacharacter is never mistaken for one is false. The docstring also names `handoff_resume_gate` as a consumer, which no longer imports it.
- Carried unchanged from `20260915T085452Z`: #810 stdout error prints; #934, #1009, #1011, #997, #808; #983 and #894 ruling-gated; #969 open by ruling; #968; insights `chores/staleness-gate-class-fit`, `chores/staleness-signal-fit`, `cli/manpage-flag-claims` awaiting calibration; `--log-file` absent; permission-consent-drift lacks `proofs/settings-patch.md`; `obpi_stages.py` BASELINE_VERIFICATION non-canonical unittest step.

## Verification Checklist

```bash
git status -sb
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run -m unittest tests.hooks.test_verifier_pipe_gate tests.governance.test_stage4_packet tests.test_hooks > "$CLAUDE_JOB_DIR/tmp/v.log" 2>&1; echo "exit $?"
gh issue view 1008 --json state --jq .state
gh issue view 1013 --json state --jq .state
```
Expected: level with origin; no locks; tests exit 0; #1008 CLOSED; #1013 OPEN. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260915T085452Z-handoff-refresh-canon-routing.md` (predecessor, resumed).
- `src/gzkit/verifier_pipe_gate.py`, `src/gzkit/shell_reading.py`, `tests/hooks/test_verifier_pipe_gate.py`.
- `.gzkit/rules/tests.md` (0.25.0), `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md`.
- `.gzkit/insights/agent-insights.jsonl` (insight scope agent/verification-scope-on-short-fixes).
- Commit `7d113edbd`; GHI #1008 contract-amendment and close comments; GHIs #1012 and #1013.

## Settled Rulings

870 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
