---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-21T23:59:19Z'
agent: claude-code
session_id: 524804f1-5554-4dcc-8004-60272ec3b090
continues_from: .gzkit/handoffs/20261121T131110Z-rp12-o4-task5-sweep-running.md
---

## Current State Summary

This session continued past handoff 20261121T131110Z.

- The O4 dock-trial sweep finished: its record docs/governance/harbor-ro12-dock-trial-evidence/o4-sweep-2026-11-21.json landed in d38e2c790. 574 mutants: 466 killed, 92 survived, 16 disclosed (no single test killed them alone, though some test failed); every baseline green, every source restored; order_ledger.py's entry reads +dirty from the handoff alone.
- The survivors were shown to the operator in three rough buckets read by eye: 12 parser_governance helpers (noise from ruling 197's helpers), about 50 in older code the hand-picked test modules left out (work_package_run.py's unblock and fix-cycle helpers, mx_cmd.py's lock and airlock helpers), and about 45 in O4's new code, most in task 4's gzkit/mx/log.py and mx_exit_cmd.
- The operator ruled the internal mutation tool a mistake and asked to look into it; the 2026-07-18 enforcement audit had recommended Cosmic Ray, and ADR-pool.test-integrity-tooling left the engine choice to its promotion, never made.
- The operator raised whether each RO/RP is being returned to seaworthiness as it goes or at the end, and named the co-drift: multiple-choice questions with recommendations draw the operator into going with the flow.

## Important Context

- The drydock doctrine defers seaworthiness to the end: docs/governance/safe-mode-doctrine.md § Records per act, item 5, reads 'No long check runs during the drydock' and 'no commit witness, gz check or failing-test-first is owed per act', with the operator's 2026-10-25 ruling 'leave things partially broken until the reconfiguration is complete, then we adjust tests and turn the security alarms back on'; seaworthiness is judged once, at exit, by a sea trial.
- RP-12 ruling 27 (operator 'A', 2026-11-04) puts a full-strength dock trial on every order: 'Each order's dock trial runs its own refusal tests at full strength, each refusal shown red then green, with gz check over what the order touched.' It speaks of orders, the doctrine of acts, but the two pull opposite ways; whether other ROs or RPs carry per-order trials has not been read.
- The previous handoff's step 4, gz check over the session's commits, is owed by AGENTS.md's per-change gate but not by the drydock doctrine's item 5; it was not run. Name that disagreement to the operator rather than settle it.
- Measured in the RP-12 kit: 199 rulings, 123 by selection, 114 the recommended option, 9 selections departing from it. AGENTS.md rules cost out as a reason ('Maintenance burden, speed and lighter ceremony are not reasons to choose'; DO IT RIGHT 3), so recommendations lean heaviest and a ruling series ratchets toward ceremony (insight scope agent-question-form).
- The September audit's Cosmic Ray pilot (docs/evals/test-suite-integrity-audit-2026-09-24.md § Mutation pilot) ran 3,034 mutants over 9 enforcement modules, 1,635 killed and 1,393 survived, a raw kill being any nonzero exit; no run time is recorded there.
- Shift turnover: gz wp tag show --all reads no tag issued, gz wp runs no work package in flight, gz obpi lock list mx-session ACTIVE at 1068m of 1440m, the lease lapsing near 2026-11-22T06:10Z.

## Decisions Made

- [operator-ruled] The internal mutation tool was a mistake and is to be investigated (verbatim: "our vibed internal tool was a mistake. we need to look into this.").
- [operator-ruled] Write the handoff and git-sync (verbatim: "write the handoff and git sync").
- [agent-chose] Recorded the operator's corrections as insights (scopes rp12-dock-trial, rp12-dock-trials, agent-question-form) rather than as kit rulings, since none was put as an option.
- [agent-chose] Ran no further sweep and no survivor re-run, under the insight's next action: no sweep on the internal tool until the investigation rules.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide; renew the mx-session lease through the gz-mx skill if the session runs past 2026-11-22T06:10Z.
2. Open the mutation-tool investigation the operator called for: read docs/governance/enforcement-claim-nc-audit-2026-07-18.md, docs/design/adr/pool/ADR-pool.test-integrity-tooling.md and the September audit's mutation pilot, then lay out for the operator what the internal tool did against what Cosmic Ray would do, each with its cost; ask open questions, one at a time, and state every option's cost.
3. Read every RO and RP under docs/governance/harbor-*.md for per-order trials, then put RP-12 ruling 27 against the drydock doctrine's item 5 to the operator, both quoted verbatim.
4. Name to the operator the disagreement on gz check per act: AGENTS.md's per-change gate against the drydock doctrine's item 5.
5. Hold O4's survivor triage, its dock-trial section and its inspection until steps 2 and 3 are ruled; the record stands committed.

## Pending Work / Open Loops

- O4's trial: survivors to triage, the kit's dock-trial section, ruling 198's inspection, then O4's Gate 5 under ruling 165, all held behind the mutation-tool investigation.
- The cost clause in AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT and § DO IT RIGHT 3 is doctrine; any change goes to the operator (insight scope agent-question-form).
- o4_mutation_sweep.py writes its record only at the end and prints only per file (insight scope rp12-o4-dock-trial).
- GHI #1337 open: gz mx reads a hard-coded ledger path.
- GHI #1331 open: a timed-out fetch reports stale ahead/behind as current.
- Insight, scope tautological-test-audit: debt over its ceiling, routed through the decommission-tautological-tests chore before gz mx exit.
- The contract's hexagon-test discrepancy line: 113 covers, 13 label and 2 patch findings, unchanged.

## Verification Checklist

- git log -1 -- docs/governance/harbor-ro12-dock-trial-evidence/o4-sweep-2026-11-21.json names d38e2c790.
- Entries with scopes rp12-dock-trials and agent-question-form appear in .gzkit/insights/agent-insights.jsonl.
- uv run -m unittest tests.test_tag_out.PausedCarryTests passes.
- gh run list --workflow CI --limit 3 reads check success on the synced HEAD.
- uv run gz obpi lock list reads mx-session ACTIVE until the lease lapses.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-dock-trial-evidence/o4-sweep-2026-11-21.json`
- `docs/governance/harbor-ro12-dock-trial-evidence/o4_mutation_sweep.py`
- `docs/governance/harbor-ro12-contractor-kit.md`
- `docs/governance/safe-mode-doctrine.md`
- `docs/governance/enforcement-claim-nc-audit-2026-07-18.md`
- `docs/design/adr/pool/ADR-pool.test-integrity-tooling.md`
- `docs/evals/test-suite-integrity-audit-2026-09-24.md`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

2420 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
