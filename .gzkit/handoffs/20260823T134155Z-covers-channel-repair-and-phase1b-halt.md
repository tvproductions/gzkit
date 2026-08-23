---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-08-23T13:41:55Z'
agent: claude-code
obpi_id: OBPI-0.35.0-08-remember-post-append-advisory
session_id: d2b65186-ff25-4c42-93b2-90cc5e541727
continues_from: 20260823T123741Z-brief-ownership-precondition-and-route-filter.md
---

## Current State Summary

Opened as a handoff review; the operator ruled "Bind the OBPI-08 @covers first" and set aside both building OBPI-0.35.0-07 and resuming ADR-0.35.0 more broadly. Ran OBPI-0.35.0-08 through the gz-obpi-pipeline skill with full subagent dispatch (implementer + spec-reviewer + quality-reviewer, 3 of 3 mandated roles receipted).

THE PIPELINE HALTED AT STAGE 3 PHASE 1b AS PREDICTED, and no Gate 5 was claimed. REQ-0.35.0-08-04 is blocked on `gz content land` (unregistered; ships in OBPI-0.35.0-07, still Draft) and REQ-0.35.0-08-06 is unprovable through this harness. Both are BEHAVIOR REQs whose coverage gate is unwaivable on every lane, so `gz obpi complete` cannot run. OBPI-0.35.0-08 remains pending; ADR-0.35.0 remains 1/10, heavy, Pending, closeout BLOCKED.

What landed: `covered_reqs` 2 -> 5 and `behavior_uncovered_reqs` 5 -> 2 for OBPI-0.35.0-08, one new test, three `@covers` bindings net, and a reconciled brief.

## Important Context

THE COVERAGE COUNT IS NOT THE EVIDENCE, and this session is the worked example. The implementer's first pass produced five covered REQs. The review removed one of its bindings and strengthened another, and the count read 5 either way. `gz covers` counts decorators; it cannot see whether a decorator's test reaches the code path its REQ names.

THE DEFECT THE SPEC REVIEW CAUGHT IS A NEW SHAPE: a `@covers` binding falsified by a SUCCESSFUL production fix. `@covers("REQ-0.35.0-08-02")` was placed on `test_malformed_manifest_never_costs_the_exit_code`, claiming proof of REQ-02's raise-survival semantics. But `809f1370` added `if not isinstance(data, dict): return {}` to `vendors.py::_read_manifest_key`, so a `[]` manifest now returns `{}` cleanly, `drifted_consumers()` completes normally, and `_drift.py`'s `except (OSError, ValueError)` is NEVER ENTERED. Nothing raises. The test is a good regression guard for the guard itself; the decorator asserted a proof its body had stopped carrying. Verified independently at `vendors.py:81` before acting. Recorded as a discovery insight.

THE RED WITNESS RETURNED `not-applicable` FOR ALL THREE BOUND REQs and that is correct, not a pass. Production landed yesterday, so `gz arb red` withholds nothing and the experiment has no premise. The trap the skill names explicitly: `not-applicable` sits adjacent to `none` ("your test cannot fail"), and treating them as equivalent leads to weakening real assertions until the witness goes quiet. MANUAL negative controls were used instead. The first (REQ-01, breaking `append_entry`) produced an ERROR-class red (`FileNotFoundError`), recorded honestly as weak. The second (REQ-05, forcing a fake drifted consumer) produced a genuine `AssertionError` — a strong red.

THE DISPATCH-CHANNEL GAP IS NARROWER THAN THE PRIOR HANDOFF LOGGED. That handoff recorded `gz obpi dispatch` as unable to record reviews. Measured this session: it works cleanly under a live pipeline marker and reported "3 of 3 mandated roles". The prior observation was made on a DIRECT-FIX path, where no marker exists to bind to. The gap is not "dispatch is broken" but "dispatch has no home outside the pipeline."

THE HARNESS/CANON CONFLICT RECURRED AND WAS NOT RESOLVED SILENTLY. The session harness forbids unrequested Agent calls; canon forbids working an OBPI outside the pipeline skill, whose Stage 2 IS subagent dispatch. Surfaced to the operator with both texts quoted, and resolved by the standing ruling booked 2026-08-22 ("Run the full pipeline with subagent dispatch"), which is carried in the rulings corpus rather than re-asked.

BRIEF-OWNERSHIP PRECONDITION APPLIED AND CLEARED. `OBPI-0.0.37-19-corpus-capture-tool-skill` contests `tests/commands/test_content_remember.py` in the plan-audit collision list; it is `Completed` and therefore TERMINAL, so it does not block.

THE PRE-PUSH GATE RUNS ~3.5 MINUTES. Background every push.

## Decisions Made

- [operator-ruled] "Bind the OBPI-08 @covers first" — chosen over building OBPI-0.35.0-07, starting at OBPI-0.35.0-01, or holding. Booked via `gz handoff decide` with steps 1 and 3 set aside.
- [operator-ruled] Commit and git-sync the verified coverage work now rather than holding it uncommitted or committing without pushing. No Gate 5 claimed; OBPI stays pending.
- [agent-chose] Dispatched the implementer at `sonnet` where the skill's complexity matrix says `haiku` (1 file -> simple). The matrix proxies complexity by file count and misreads a task whose entire difficulty is judging whether an assertion bites its REQ. Deviation declared to the operator rather than taken silently.
- [agent-chose] REMOVED a `@covers` binding rather than keeping the count at five. Losing a binding is the correct outcome when the proof was never real.
- [agent-chose] Did NOT author a test for REQ-05's first disjunct. It is structurally unreachable, and testing it through a direct `drifted_consumers()` call would prove a helper rather than the REQ — a green gate over an unexercised behaviour.
- [agent-chose] Left `test_malformed_manifest_never_costs_the_exit_code` in place with an explanatory comment instead of deleting it. It is a legitimate `vendors.py` regression guard; only the REQ claim was wrong.
- [agent-chose] Halted at Phase 1b rather than presenting Stage 4 evidence. Soliciting attestation with a failing parity gate is a Gate 5 bypass.

## Immediate Next Steps

1. Rule on the three residuals now recorded in the OBPI-0.35.0-08 brief. REQ-05's clause "and stderr is empty" and all of REQ-06 are INEXPRESSIBLE through `CliRunner`, which merges stdout and stderr into one buffer (`tests/commands/common.py:69`); REQ-05's first disjunct ("renditions already on the current corpus fingerprint") is STRUCTURALLY UNREACHABLE because `remember.py` appends before it advises and `corpus_fingerprint` digests every entry. Each needs either a re-worded REQ or a different test runner. Both are operator calls; an agent must not amend an acceptance criterion to match what is testable.
2. Decide whether OBPI-0.35.0-07-content-land-orchestrator is built next. It remains the sole blocker on REQ-0.35.0-08-04 and therefore on OBPI-0.35.0-08's completion. Heavy, 9 REQs, a new CLI verb plus landing state file, ledger events, manpage, runbook and features. Read live state from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`.
3. Resume ADR-0.35.0 proper — the lowest-semver feature ADR holding unlanded OBPIs, therefore the ADR in flight by ascending-semver doctrine. Set aside twice now (2026-08-22 and this session), not discharged. Any OBPI worked there runs through the gz-obpi-pipeline skill.
4. Consider whether REQ-02's two still-unbound channels deserve tests: "absent renditions directory" returns `[]` gracefully rather than raising, so it structurally cannot prove raise-survival, and "unreadable sidecar" is exercised only on the `ValueError` branch, never `OSError`. Both are disclosed in the brief's REQ-02 row.

## Pending Work / Open Loops

- OBPI-0.35.0-08 is PARTIALLY LANDED and STILL CANNOT COMPLETE. REQ-01, -02, -03, -05 and -08 are bound in the `@covers` channel; REQ-04 is blocked on the unlanded `gz content land` verb; REQ-06 is unprovable through this harness; REQ-07 is a closeout-layer structural fence. `behavior_uncovered_reqs` is 2 and the gate is unwaivable, so no Gate 5 is available and none was claimed.
- THREE RESIDUALS AWAIT AN OPERATOR RULING, all now recorded in the brief's PARTIALLY PRE-LANDED table rather than left silent: REQ-05's "and stderr is empty" clause, REQ-05's structurally-unreachable first disjunct, and REQ-06 in full. Do not resolve these by amending the REQs — that is an operator call.
- REQ-02 IS BOUND ON ONE CHANNEL OF THREE. `test_malformed_sidecar_never_costs_the_append_or_the_exit_code` genuinely raises a `ValidationError` into the drift seam and proves the REQ. "Absent renditions directory" cannot prove raise-survival at all (it returns `[]`), and "unreadable sidecar" never exercises the `OSError` branch. Disclosed, not fixed.
- `test_malformed_manifest_never_costs_the_exit_code` NOW CARRIES NO `@covers` AND MUST NOT HAVE ONE RE-ADDED. A comment block above the def states why. Re-adding it would restore a decorator asserting a proof the body does not carry.
- The candidate-exclusion arm of `is_graded_rendition` still SURVIVES DELETION against every fixture in the repo (carried from the prior handoff, untouched this session). It belongs to the TERMINAL OBPI-0.35.0-09.
- The rendition-drift reconciler still reports a brief CLEAN on all five dimensions while REQs are pre-landed or invalidated. Confirmed live this session: `gz obpi brief-drift` returned "clean" on a brief whose own table recorded four REQs as prose-landed and two as unprovable. Exit 0 there means "nothing contradicts it yet", never "the brief matches reality".
- Copilot mirror removal, deferred by operator in a prior session. 65 files including `src/gzkit/schemas/manifest.json`.
- AGENTS.md renders over the 32768 B Codex delivery cap (43310 B at last measure). Advisory until 1.0 per the operator stay; tracked at GHI #815 [settled]; the instructions-files-diet chore has still not run.

## Verification Checklist

```bash
uv run gz obpi lock list                                  # expect: No active locks
git rev-list --left-right --count origin/main...HEAD      # expect: 0	0
uv run gz covers OBPI-0.35.0-08-remember-post-append-advisory --json   # expect: covered 5/8, behavior_uncovered 2
uv run gz content land --help                             # expect FAILURE: proves REQ-08-04 still blocked
uv run gz validate --req-kind-discipline                  # expect: exit 0
uv run gz validate --rendition-freshness                  # expect: exit 0
uv run gz validate --documents                            # expect: exit 0
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
grep -n "No @covers here" tests/commands/test_content_remember.py   # the deliberate absence
```
Read `exit_status` from the ARB receipt for any backgrounded verifier, never the harness notification. Never pipe a verifier into `tail`/`grep` — a registered hook blocks it, because the shell would report the filter's exit code rather than the verifier's.

## Evidence / Artifacts

- `tests/commands/test_content_remember.py` — one new test `test_append_survives_and_exit_stays_0_when_the_advisory_fires`; `@covers` bound for REQ-0.35.0-08-01, -02, -05; the REQ-02 binding REMOVED from the manifest test with an explanatory comment block; REQ-05 assertions strengthened to the advisory's structural markers.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md` — four rows reconciled; COVERAGE CHANNEL WARNING marked discharged for 01/02/05 with REQ-06 standing and the count explicitly disclaimed as not being the evidence.
- `.claude/plans/OBPI-0.35.0-08-remember-post-append-advisory.md` — the plan, with Step 6a destination-in-mind and rejected-alternatives disclosures.
- `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-08-remember-post-append-advisory.json` — verdict PASS, gaps_found 0, 18 advisory sibling scope collisions.
- Final receipt ids, all exit_status=0: arb-step-unittest-e6b3ebe0671e4512b3e907ab35d34c4c (8752 tests), arb-ruff-664cc8c6cd054594aa51ae44d385a426, arb-step-typecheck-374793b918d04b35a8982ce52ee5417b, arb-step-mkdocs-bf8170e2cc2c4cacb5294c584b390cee.
- RED witness receipts, all failure_class=not-applicable (the experiment had no premise; production had already landed): arb-red-REQ-0.35.0-08-01-562f7b6175414f9e94c703a2342a6c49, arb-red-REQ-0.35.0-08-02-a3cd51c07d8a453b867b8e9c4b045b39, arb-red-REQ-0.35.0-08-05-fe43e52ed7544a8da70a9d7ab9e088a0.
- `.gzkit/insights/agent-insights.jsonl` — one discovery record this session: a `@covers` binding falsified by a successful production fix.
- `uv run gz cli audit` — 137/137 commands fully covered.

## Settled Rulings

489 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
