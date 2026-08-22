---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T17:01:07Z'
agent: claude-code
session_id: 64fb57fc-8bc3-4255-852e-f64b4191633b
continues_from: .gzkit/handoffs/20260822T155333Z-handoff-review-four-levers-and-cadence-correction.md
---

## Current State Summary

Handoff-review session that then executed. Tree clean, origin/main in sync at 29a3219d (0 0), no locks, no hangar. The operator ruled on the resumed handoff: proceed on advised steps 3 and 4, set aside 1 and 2, and answer GHI #856 evidence-led first. All three landed.

Commits: 884c4e67 (GHI #853, module-size ratchet slack arm, closed), 53c5429d (GHI #835, concurrent gz check behind a measured declaration, closed), 29a3219d (verification-cadence insight).

Filed: GHI #857 (the unittest suite is not order-independent) and GHI #858 (the Handoff documents validator is 19% of the gate and grows every session). GHI #856 answered and explicitly blocked on #857.

THE SESSION'S OWN DEFECT WAS WALL-CLOCK, NOT WORK. Five full gz check runs at 110-140s each where a 0.1s targeted unittest module caught every regression but the last. The operator surfaced it verbatim: 'great, another 45 minute run, why does any meaningful action in gzkit take this long to run?' Recorded as an improvement insight in 29a3219d. Read that as the first-order lesson, exactly as the predecessor handoff said of its own cadence failure -- this is the SECOND consecutive session to fail on cadence rather than on work.

## Important Context

THE MEASUREMENT THAT ANSWERED #856 IS THE SESSION'S MOST CONSEQUENTIAL FINDING. The operator ruled evidence-led first rather than swapping CANONICAL_STEP_COMMANDS, and the evidence says do not swap. Three randomized-order passes over the same 8677 discovered tests failed every time -- seeds 1/2/3 produced 4, 3 and 2 failures, always the same four-test family in tests.commands.test_runtime.TestAdrRuntimeCommands. That module in isolation is clean (Ran 38 tests, OK, exit 0). One test asserting the pool-ADR rejection inside runner.isolated_filesystem() received real-repository output for ADR-0.0.23 instead. get_project_root() is Path.cwd() and recomputes every call, so the leak is state captured at IMPORT time, not a cached root. Consequence: the canonical attestation command attests the suite in ONE ordering, not the suite.

THE #835 COST MODEL IN THE GHI WAS WRONG AND IS NOW CORRECTED IN THE CLOSING COMMENT. It read '~46 validator steps + lint/format/typecheck/smoke ~55s' and 'There is no dominant cost'. Measured per-step: Test 44.42s, Behave 34.15s, Handoff documents 28.67s, Line endings 4.23s, Docs build 4.17s, Validate default scopes 3.10s, and the other 50 steps ~23s COMBINED. Three steps are 72% of the gate. Handoff documents was named nowhere in the GHI and is 19% of it by itself.

ONLY 3 OF 56 STEPS WRITE, AND THE MEASUREMENT FOUND A REAL RACE. Behave writes dist/, Docs build writes site/, Validate default scopes writes .agents/personas/. Behave BUILDS dist/*.whl and gz validate --distribution READS it -- exactly the undeclared ordering GHI #835 warned would make a parallel runner flaky. Writers now run serially in list order ahead of the concurrent phase.

THE RATCHET'S RESTING STATE IS NOW ZERO HEADROOM. All five grandfathered modules sit at their current SLOC, so a line added to any of them needs a compensating extraction in the SAME commit. This was ruled, not a side effect. parser_artifacts 1077, parser_maintenance 1514, obpi_complete 1302, validate_cmd 1242, adr_audit 1034.

A CORRECTION WORTH CARRYING: sloc_at_cutover 1309 for validate_cmd was NOT false when #853 was filed. Git shows 1309 WAS the original 2026-08-01 cutover value and fc3f0956 happened to restore it exactly. Tightening to current SLOC is what actually makes ceiling and cutover diverge, which is why the field was split rather than renamed.

ADOPTERS ARE UNAFFECTED BY THE #835 CHANGE, DELIBERATELY. data/check_step_concurrency.json is gzkit-project-local on the same footing as data/module_size_grandfather.json, and the loader returns an empty mapping when absent, which is all-serial -- today's behaviour. Shipping the speedup to adopters means inventing a package-data surface that fix does not carry.

## Decisions Made

- [operator-ruled] Proceed on advised steps 3 and 4; set aside 1 and 2 (verbatim selection: '3 - GHI #853 ratchet arms, 4 - GHI #835 validator parallelism'). Booked via gz handoff decide, session 64fb57fc, with both set-asides recorded.
- [operator-ruled] GHI #856 is answered evidence-led first, not by ruling on the swap (verbatim: 'Evidence-led first'). The measurement found a real ordering dependence, so the swap is blocked rather than deferred.
- [operator-ruled] The module-size slack arm FAILS CLOSED and every entry is tightened now (verbatim: 'Fail closed + tighten now'). The zero-headroom consequence was stated in the question and accepted with the answer.
- [operator-ruled] Running the full gz check five times in one session is the defect (verbatim: 'great, another 45 minute run, why does any meaningful action in gzkit take this long to run?'). Use the narrow verifier while iterating; pay for the full gate once, plus one repeat only when the change is concurrency-shaped.
- [agent-chose] An undeclared gz check step runs SERIALLY rather than raising. Serial is the conservative class -- always correct, merely slower -- so the unsafe default is structurally unavailable, and the unaccounted-step guarantee moves to a governance test that fails the COMMIT. The raise version broke the presentation and skill-audit tests, which legitimately patch in synthetic steps.
- [agent-chose] Did NOT cache the concurrency declaration loader. Caching it against get_project_root() is precisely the import-time-capture shape filed as GHI #857 the same hour.
- [agent-chose] Deleted the test that asserted on the gate's SOURCE TEXT rather than keeping it. gz validate --tautological-test-audit flagged it correctly and guardrail-feedback-prose.md refuses inferential prose-graders; the rationale is recorded where the test was.
- [agent-chose] Fixed the import-time sys.stdout.reconfigure crash in the chore script rather than working around it in the test, using contextlib.suppress -- the hasattr guard narrows the attribute to object and breaks ty's own suppression code.
- [agent-chose] Filed #857 and #858 as two GHIs, not one, and left the Behave-builds-a-wheel finding unfiled. One GHI, one class of failure.

## Immediate Next Steps

1. Resume ADR-0.35.0-canon-entry-corpus-landing through the gz-obpi-pipeline skill. Semver-topmost, heavy lane, closeout BLOCKED, and now deferred FOUR consecutive sessions -- run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing for the live landed count rather than trusting any figure here. Start at the lowest-numbered pending brief. Budget a fresh session; the skill is mandatory (operator verbatim: 'you are NEVER to work on an obpi without runnung the skill').
2. GHI #857 -- find the import-time state that escapes runner.isolated_filesystem(). Reproduction is deterministic: the seeded shuffle probe in the issue body reproduces on seeds 1, 2 and 3. This is the precondition for #856, and it is the one open item that makes a Gate-5 tests-pass receipt mean less than it claims.
3. GHI #858 -- profile the Handoff documents validator. 28.67s, 19% of the gate, and it grows every session because every session writes a handoff. Scheduling cannot fix a single step's own cost.
4. Consider filing the Behave finding: 34.15s spent BUILDING A WHEEL into dist/ on every routine quality run. Deliberately not filed this session (one GHI, one class of failure); it is the second-largest single cost in the gate.

## Pending Work / Open Loops

GHI #856 -- open and BLOCKED on #857 by this session's ruling. The 86 seconds remain real; the order is fix #857, re-run the shuffle probe to confirm order-independence, then make the one-line CANONICAL_STEP_COMMANDS change plus its RETIRED_STEP_COMMANDS row.

GHI #857 -- open, filed this session. Four tests pass only in default alphabetical order.

GHI #858 -- open, filed this session. Single validator at 19% of the gate, unbounded growth.

Residual disclosed on the #835 [settled] fix, recorded and not built: the writers phase is ~41s of dead serial time and Test saturates the cores regardless (318s CPU over 114s wall). Recovering the rest needs per-writer dependency EDGES rather than a writers-first PHASE -- only Validate default scopes actually consumes a writer's output, so Behave and Docs build could overlap the read-only phase.

Residual disclosed on the #853 [settled] fix, carried unchanged: a raise landing in the SAME commit as a growth that exactly consumes it evades both arms. No observed instance.

GHI #849 (ARB RED witness inert on landed work) and GHI #611 (no general append-only corrective-action primitive) -- both open, both carried unchanged across six handoffs now, both untouched again.

Two advisory findings gz check reports and this session did not address, both pre-existing: 715 REQs carry no covering test, and AGENTS.md renders over the codex delivery cap with operator-doctrine-verbatim-canon straddling it.

adr_audit.py remains at 1034 equal to 1034 -- and it is now one of five modules at zero headroom rather than the only one.

## Verification Checklist

uv run gz check  # expect: exit 0, All checks passed, ~110-115s
uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py --self-test  # expect: 7 cases, all five breach directions fire, exit 0
uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py  # expect: unrecorded slack 0 SLOC, exit 0
uv run python -m unittest tests.governance.test_check_step_concurrency tests.chores.test_module_size_ratchet  # expect: OK, exit 0
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0
uv run gz obpi lock list  # expect: No active locks
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing  # expect: heavy, Pending, closeout BLOCKED; read the landed count from the output, never from this document

## Evidence / Artifacts

`data/check_step_concurrency.json` -- the measured concurrency declaration; carries per-step wall times as a dated record
`src/gzkit/commands/quality.py` -- _partition_steps_by_concurrency, _run_check_steps, _step_concurrency_classes
`tests/governance/test_check_step_concurrency.py` -- fails the commit on an undeclared step
`.gzkit/chores/module-sloc-cap-radon/check_module_size.py` -- fifth breach arm, ceiling and cutover split, guarded stdout reconfigure
`data/module_size_grandfather.json` -- all five entries at zero headroom
`tests/chores/test_module_size_ratchet.py` -- the four compute_breaches cases
`.gzkit/insights/agent-insights.jsonl` -- the verification-cadence improvement record
`.gzkit/handoffs/20260822T155333Z-handoff-review-four-levers-and-cadence-correction.md` -- the resumed handoff this one supersedes

## Settled Rulings

470 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
