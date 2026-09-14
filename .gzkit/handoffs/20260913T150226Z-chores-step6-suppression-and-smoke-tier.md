---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-13T15:02:26Z'
agent: claude-code
session_id: 00b3b9c0-98d7-4a61-bd95-b1ebcf93288e
continues_from: .gzkit/handoffs/20260913T124003Z-chores-step5-declared-and-refusal-flip.md
---

## Current State Summary

Session 00b3b9c0 resumed `20260913T124003Z-chores-step5-declared-and-refusal-flip.md` (Fresh). Resume ruling booked with `gz handoff decide` as proceed; step 2 (`gz chores status`, GHI #936) was set aside.

Landed and pushed to main (HEAD `ea52c2ef3`, level with origin, no locks):
- `e23b26c3b`: `test-isolation-compliance` no longer gates the full suite on 60s, a ceiling `.gzkit/rules/tests.md` § General Rules had retired. The profiler reports wall clock only; `acceptance.json` runs `uv run gz smoke`; `timeoutSeconds` 120 -> 900 (the timeout is per criterion and the profiler alone took 311s); registry version 2.2.0.
- `ea52c2ef3`: chores-revamp step 6. `.gzkit/rules/chores.md` 0.4.0 adds § Suppression is not a repair, witnessed by `audit_chore_suppression`. It fails a registered chore whose criterion runs through a shell interpreter, passes an exit-forcing flag, or writes suppression markers, or whose CHORE.md command span writes them. 0 findings on the live tree; `NC:chore-suppression` passes under the enforcement floor; a mutation sweep over its six guards killed all six (conclusive). Scorecard rows 56a (Mechanical) and 56b (Judgment). `gz check` exit 0.
- GHI #999 closed with a comment citing both commits and this session's rulings.

## Chores revamp — status at a glance

Plan: `docs/governance/chore-class-system.md` § Implementation order.

| Step | Status |
|---|---|
| 1. Registry schema | DONE `f1c9b0e59` |
| 2. `gz chores status` indicator + orientation announcement | NOT STARTED — GHI #936, set aside at four resume rulings |
| 3. Rung-conformance validator | DONE `6615d0a18` |
| 4. README: classes, rungs, admission | DONE `16caf8392` |
| 5. Declare all 40; flip absence to refusal | DONE `980691150` |
| 6. Suppression prohibition + witness | DONE `ea52c2ef3` |

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change. GHI #1003 and GHI #870 untouched.
- **ghi triage:** closed the chores work order (steps 1 and 3-6). No GHIs filed. The family-A class recommendation is now operator-ruled YES but no class inventory has been drafted.
- **adr/obpi campaign:** no OBPI work (IRON LAW), no locks. ADR-0.35.0 remains TOPMOST and untouched.
- **new R&D:** not worked.

### What the step-6 witness does and does not see
- The registry loader's `SHELL_OPERATORS_RE` already refused `&&`, `||`, `|`, `<`, `>` in a criterion. `;` was not refused, so `sh -c "check ; exit 0"` passed; the audit closes that with the shell-interpreter arm.
- Not flagged by design: workflow report captures such as `uvx xenon src/ > proofs/x.txt 2>&1 || true` (their exit gates nothing), and `noqa` in chore tooling code.
- Stated limits: a marker hand-written during a run (row 56b, advisory in rule text); a non-shell interpreter (`python -c`) can still exit 0; a writer named with its command inside prose code reads as an instruction.

### Live readings
- `test-isolation-compliance` will FAIL when run: two non-exempt tests over 3s (`test_validator_runs_to_completion_under_real_repo_load` 53.1s, `test_a_sequenced_verifier_is_refused_on_this_surface_too` 13.4s) and 99 stdout noise lines from the ledger-vocabulary report printing inside tests. The old 60s gate had been masking these. Recorded as a defect insight.
- Stale/overdue from the predecessor, unchanged: permission-consent-drift (overdue), rule-conflicts and skill-rule-reachability (stale proofs).

### Gotchas learned
- `gz validate --surface-fidelity` (bullet retention) requires a Mechanical or Promotable scorecard row's Rule cell to appear verbatim (case- and whitespace-folded) in AGENTS.md, CLAUDE.md or `.claude/rules/**`. Quote the rule's own sentence; put arm detail in Notes.
- An enforcement-floor fixture builder calls `create_fixture_tempdir`, which refuses outside a runner. Exercise one with `gzkit.enforcement._run_single_claim` after `_ensure_production_claims_registered()`.
- A chore's `timeoutSeconds` applies to each criterion subprocess, not the whole run.
- Editing `.gzkit/chores/<slug>/` without re-running `gz agent sync control-surfaces` fails `tests.test_chores` byte parity with the `src/gzkit/chores/` copy.
- The health profiler runs the suite twice (parallel, then serial in-process); budget about 5 minutes.

## Decisions Made

- [operator-ruled] Resume ruling on `20260913T124003Z`: "Step 6 (Recommended)". Step 2 (`gz chores status`, GHI #936) set aside.
- [operator-ruled] `frontmatter-ledger-coherence` rung: "Stays at repair" — the ledger is Layer-2 truth, so rewriting derived frontmatter stands as declared.
- [operator-ruled] Family A (a witness covers less than its claim): "Yes, as one class (Recommended)" — worked as one class under the Movement C box rather than instance by instance.
- [operator-ruled] Step 6 witness: "Static chore check (Recommended)" — a `gz check` audit over criteria and CHORE.md commands, with the hand-written-marker arm advisory in rule text; the run-time count and the repo-wide ratchet were not chosen.
- [agent-chose] Re-scoped the test-isolation 60s ceiling to the smoke tier rather than dropping it. The resume question stated this rode along with either proceed option, and `.gzkit/rules/tests.md` already names `uv run gz smoke` as the budget's enforcer.
- [agent-chose] Raised `test-isolation-compliance` `timeoutSeconds` to 900 after measuring the profiler at 311s against a per-criterion 120s timeout.
- [agent-chose] Scorecard row 56a quotes the rule's first sentence verbatim after bullet retention refused a paraphrase; the arms moved to its Notes cell.
- [agent-chose] Recorded the profiler's slow-test and stdout-noise findings as a defect insight rather than fixing them inside a commit scoped to the ceiling re-scope.

## Immediate Next Steps

1. Put the next move to the operator: (a) chores-revamp step 2, `gz chores status` plus the orientation announcement (GHI #936), the last open revamp step; (b) run `test-isolation-compliance` via `gz-chore-runner` to fix or name-exempt the two slow tests and silence the report noise; (c) start the family-A class work under the Movement C box.
2. If (c): draft a read-only inventory of family-A instances (checks whose subject is narrower than their claim) from open GHIs and recent closes, grouped by shape, for operator review before any repair. Name the class-level fix, not the instances.
3. If (a): read `scripts/check_proof_freshness.py` (it already reads declared `periodDays` and PASS-only run stamps) and `docs/governance/chore-class-system.md` § Implementation order step 2 before designing the verb; a new verb carries the seven obligations in `.gzkit/rules/cli.md` § New Subcommand.
4. If (b): the 53s test lives in `tests/commands/test_validate_frontmatter.py` (`TestFrontmatterGuard`), the 13s one in `tests/governance/test_stage4_packet.py` (`TestExitStatus`); read each before deciding fix versus a named `KNOWN_E2E_TESTS` exemption in `tests/tools/test_health_profiler.py`.

## Pending Work / Open Loops

- GHI #936 (step 2, status verb) — open, set aside four times.
- `test-isolation-compliance` fails on two slow tests and 99 noise lines (defect insight, 2026-09-13T15:00Z).
- Family-A class work: ruled YES, not started; no inventory exists.
- GHI #997 (`eval-feedback-cluster` runs fixtures) and GHI #808 (`decommission-tautological-tests` gates the ratchet) — open.
- Overdue or stale chores: permission-consent-drift, rule-conflicts, skill-rule-reachability.
- `complexity-reduction-xenon` post-cluster mode waits on the `.gzkit/rules/pythonic.md` threshold ruling.
- Follow-on once `governingRule` is populated: the rule-to-chore pass in `docs/governance/rules-tools-audits-refactors-alignment.md` § Advised order.
- GHI #1003, GHI #870, GHI #810 untouched.

## Verification Checklist

```bash
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
gh issue view 999 --json state,title
gh issue view 936 --json state,title
uv run -m unittest tests.governance.test_chore_suppression tests.governance.test_chore_rung_conformance tests.governance.test_chore_metadata_authority tests.test_chores
uv run gz validate --advisory-scorecard --surface-fidelity
uv run gz chores plan test-isolation-compliance
uv run gz handoff rulings --search "Static chore check"
```

Expected at authoring: `0 0` (the insights append after push may leave `.gzkit/insights/agent-insights.jsonl` uncommitted); no active locks; #999 CLOSED; #936 OPEN; tests green; validators exit 0; the plan shows three criteria including `uv run gz smoke`; the ruling is found once this handoff books it. Re-run these rather than trust them.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/chores.py` — `audit_chore_suppression` and its helpers.
- `tests/governance/test_chore_suppression.py` — live-tree and planted-case witnesses.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`, `src/gzkit/governance/trust_audits/_qc_claim_exemptions.py` — `NC:chore-suppression`.
- `.gzkit/rules/chores.md` 0.4.0, `docs/governance/rule-version-history.md`, `docs/governance/advisory-rules-audit.md` rows 56a/56b.
- `docs/governance/chore-class-system.md` step 6 as-landed note; `.gzkit/chores/README.md` MUST-NOT #7; `.gzkit/skills/gz-chore-runner/SKILL.md` 1.4.0.
- `tests/tools/test_health_profiler.py`, `.gzkit/chores/test-isolation-compliance/CHORE.md`, `.gzkit/chores/test-isolation-compliance/acceptance.json`, `.gzkit/chores/registry.json`.
- `.gzkit/chores/test-isolation-compliance/proofs/health-report.json` — the failing profiler report.
- Commits `e23b26c3b`, `ea52c2ef3`; GHI #999 close comment.

## Settled Rulings

845 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
