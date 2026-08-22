---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T18:14:30Z'
agent: claude-code
session_id: 626d1787-188d-464f-b139-a88a59a750f7
continues_from: 20260822T170107Z-two-cycle-time-levers-and-the-order-dependence-find.md
---

## Current State Summary

Handoff-review session that then executed every ruled item. Tree clean, origin/main in sync at ed0bf35e (0 0), no locks, no hangar.

The operator ruled on the resumed handoff: proceed on advised steps 2, 3 and 4, set aside step 1 (ADR-0.35.0), and repair GHI #859 directly. All four landed and closed in one session.

Commits: 040fa323 (GHI #859, refused handoff create no longer books orphan rulings), 07239238 (GHI #858, handoff-documents gate step 29.84s to 4.32s), f7c3c8de (GHI #857, suite made order-independent), 29b521e2 (GHI #860, tier boundary enforced on feature tags), ed0bf35e (git-sync chore).

GHI #860 was FILED this session through /ghi-author and fixed in the same session, per ghi-author Step 7 routing.

Verification: uv run gz check exit 0. Seeded full-suite shuffle clean on seeds 1, 2 and 3 (8694 tests, 0 errors, 0 failures each) where the same probe gave 4, 3 and 2 failures at GHI #857's filing.

## Important Context

THE HEADLINE, AND THE ONLY THING WORTH CARRYING IF NOTHING ELSE IS: every one of the four GHIs stated a hypothesis, all three that had one were WRONG, and each took under a minute of measurement to disprove. The hypotheses were not sloppy -- each was locally plausible from the symptom. Symptom-to-cause inference simply kept losing to one command.

- GHI #857 reasoned to import-time state captured across a cwd change, and correctly ruled out get_project_root(). Actual cause: a FIFO patcher unwind, entirely in the tests, needing no import-time state at all. patch.stop() restores whatever the attribute held when THAT patcher started, never the original, so unwinding two patchers on one attribute outer-first reinstalls the inner mock permanently.
- GHI #858 proposed re-parsing every document, an O(n^2) cross-check, or re-reading the rulings store per document. Actual cause: 2,858 subprocess.run calls, 25.2s of a 29.8s step in process spawn and select.poll, none of it in validation logic.
- GHI #860 inherited "34.15s spent BUILDING A WHEEL into dist/ on every routine quality run, the second-largest single cost in the gate". Measured on a quiet machine: the scenario is 3.3s of a 29.8s Behave step, roughly a tenth of it, wheel build cached.

THE BACKSTOP WAS DISARMED BY THE CODE IT WAS BACKING UP. tearDown in test_audit_check_covers_backfill already called patch.stopall(), and its comment named this exact symptom ("caught when test_runtime sees stubbed adr_audit internals"). stopall is itself LIFO and correct. The manual FIFO _stop_patches ran first and had already restored the wrong value, so the backstop dutifully restored a value that was already corrupt.

AN IN-PROCESS BISECT STRUCTURALLY CANNOT FIND ORDER-DEPENDENCE. The first probe re-ran the target test in every trial inside one process, so the first trial established the state every later trial depended on; it converged on the last array element and produced a confident wrong answer (a degenerate-bisect signature worth recognising). The subprocess-isolated rewrite found the single culprit in 14 steps. Reproduction is now two named tests instead of an 8,677-test shuffle.

WHY THE OBVIOUS ONE-LINE FIX FOR #860 WAS THE WRONG ONE, from three independent directions. (a) Cost: gz check is the PRE-PUSH gate, gz check --fast already drops the whole Behave step via _FAST_SKIPPED_STEPS, and --reuse-verified stops one tree paying twice -- so "every routine quality run" was false. (b) Doctrine: GHI #182 removed the --slow flag and audit_test_tiers fails closed if it returns, so giving @slow a reader re-introduces that tier under another name. (c) Coverage: audit_distribution names itself the STATIC audit, "no wheel build required", so the behave scenario is the only proof that the shipped wheel actually installed produces the baseline tree.

A STALE PROSE NUMBER WAS ABOUT TO BECOME A DECISION. The unmeasured "30-90s" sat in the feature header and in docs/governance/distribution_baseline.md and drove a recommendation to delete real coverage. That doc additionally told CI authors to add the scenario "rather than relying on the default gz check cascade", which would have duplicated a step the cascade already runs. Both are corrected with dated measurements marked as records.

THE GATE IS ABOUT 25s CHEAPER. Handoff documents 29.84s to 4.32s, with identical verdict and identical grandfather counts (12 pre-cutover, 4 hollow) before and after.

DATA/CHECK_STEP_CONCURRENCY.JSON IS NOW STALE BY 6.9x ON ONE ROW. It is a self-declared dated record (measured_at_commit 884c4e67) and nothing reads measured_seconds, so nothing is broken. Re-measuring means a per-step-alone sweep and would mix two measurement dates in one file, which is why it was left.

## Decisions Made

- [operator-ruled] Proceed on advised steps 2, 3 and 4; set aside step 1 (verbatim selection: '2 - GHI #857 order-dependence (Recommended), 3 - GHI #858 profile Handoff validator, 4 - File the Behave wheel-build finding'). Booked via gz handoff decide, session 626d1787, with the ADR-0.35.0 step recorded as a set-aside.
- [operator-ruled] GHI #859 is repaired this session rather than queued (verbatim: 'Fix it this session as a direct GHI repair').
- [agent-chose] Left the two orphaned entries in .gzkit/handoffs/rulings.jsonl in place. Nothing in production reads the source field, and rewriting an append-only governance log to erase a now-documented scar is an operator call, not an agent's. Flagged in the #859 close comment and carried as an open question here.
- [agent-chose] Did NOT add ~@slow to behave.ini, against the finding's own framing. Cost, doctrine and coverage each said no independently; the recommendation flipped on measurement rather than on taste.
- [agent-chose] Deleted a third candidate test for #859 rather than keeping it. read_rulings returns text only, so it passed with the defect present and could not discriminate -- a test that cannot fail when the logic is wrong is worse than no test.
- [agent-chose] THREADED the tracked-path index through validate_handoff_document rather than caching it. A cache keyed on a path has to guess when the repository changed underneath it, which is precisely the shape filed as GHI #857 the same day.
- [agent-chose] Swept every FIFO patcher unwind in the suite to LIFO, not only the one that leaked. The other 8 files were verified to have no observed leak with a probe that was itself validated by reverting the fix and watching it name the two leaked attributes -- preventive, and said to be preventive.
- [agent-chose] Two witnesses of different KINDS for #857 rather than one: a scoped deterministic test on the class that leaked, plus a broad probabilistic canary that names its own limits in its docstring. Both were confirmed RED against the FIFO unwind before being kept.
- [agent-chose] Extended audit_test_tiers to feature tags rather than only deleting @slow. Deleting the tag fixes the instance; without the audit arm the next one reappears and validates green.
- [agent-chose] Excluded @wip from the forbidden tag set deliberately. It has a real reader (behave.ini default_tags) and marks unauthored steps; unfinished work is not a test tier, and 37 live uses depend on the distinction.

## Immediate Next Steps

1. Resume ADR-0.35.0-canon-entry-corpus-landing through the gz-obpi-pipeline skill. Semver-topmost, heavy lane, closeout BLOCKED, and now deferred FIVE consecutive sessions -- run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing for the live landed count rather than trusting any figure here. Start at the lowest-numbered pending brief. Budget a fresh session; the skill is mandatory (operator verbatim: 'you are NEVER to work on an obpi without runnung the skill').
2. GHI #856 is UNBLOCKED and is the cheapest real item on the board. It was blocked on #857 [settled] by the prior session's ruling; the serial suite is now order-independent across three seeds, so the question returns to whether unittest-parallel is acceptable as attestation evidence. Scope is a one-line CANONICAL_STEP_COMMANDS change plus its RETIRED_STEP_COMMANDS row.
3. Rule on the two orphaned entries in .gzkit/handoffs/rulings.jsonl. They cite 20260822T170006Z, a document that never existed, because a refused create booked before validating. Nothing reads the source field so nothing is broken; the choice is between leaving a documented scar in an append-only log and rewriting one.
4. Consider re-measuring data/check_step_concurrency.json. The Handoff documents row is stale by 6.9x after this session. It is a dated record and nothing consumes measured_seconds, so this is routing hygiene rather than a defect -- and doing it right means a per-step-alone sweep, not editing one row.

## Pending Work / Open Loops

GHI #856 -- open and now UNBLOCKED by this session's #857 [settled] fix. The 86 seconds it names remain real.

GHI #849 (ARB RED witness inert on landed work) and GHI #611 (no general append-only corrective-action primitive) -- both open, both carried unchanged across seven handoffs now, both untouched again.

Two advisory findings gz check reports, both pre-existing and unaddressed this session: 715 REQs carry no covering test, and AGENTS.md renders over the codex delivery cap with operator-doctrine-verbatim canon straddling it.

RESIDUAL disclosed on the #858 [settled] fix, recorded and not built: 232 git subprocess calls remain, in _is_git_ignored (167 calls, 1.75s) and _existed_in_git_history (63 calls, 1.41s). Both fire only for candidates already found missing. check-ignore batches via --stdin; the history walk does not batch cheaply. Left because the step is now sibling-scale (Line endings 4.23s, Docs build 4.17s).

RESIDUAL disclosed on the #860 [settled] fix: cold-cache uv build runtime was never measured. The 3.3s figure is warm-cache and says so in both surfaces where it now appears.

RESIDUAL disclosed on the #857 [settled] fix: the broad canary cannot prove order-independence and says so in its own docstring. Only the scoped test is deterministic; the canary is a net that fires when a leaking module happens to run before it.

RESIDUAL disclosed on the #859 [settled] fix: the two orphaned rulings are left in the store (see Immediate Next Steps item 3).

adr_audit.py remains at 1034 equal to 1034, one of five modules sitting at zero ratchet headroom.

## Verification Checklist

uv run gz check  # expect: exit 0, All checks passed
uv run python -m unittest tests.governance.test_mock_leakage tests.governance.test_audit_check_covers_backfill  # expect: OK, exit 0
uv run python -m unittest tests.governance.test_handoff_ruling_store tests.governance.test_handoff_validation  # expect: OK, exit 0
uv run python -m unittest tests.governance.test_promoted_advisory_audits  # expect: Ran 87 tests, OK
uv run -m behave features/distribution_invariant.feature  # expect: 2 scenarios passed, 15 steps passed, exit 0
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0
uv run gz obpi lock list  # expect: No active locks
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing  # expect: heavy, Pending, closeout BLOCKED; read the landed count from the output, never from this document

## Evidence / Artifacts

`src/gzkit/handoff_rulings.py` -- prospective_corpus, and the corrected ordering docstring (GHI #859)
`src/gzkit/handoff_api.py` -- create_handoff validates before booking; the store still precedes the document
`src/gzkit/handoff_validation.py` -- build_tracked_path_index, the batched _is_git_tracked, the threaded git_index (GHI #858)
`src/gzkit/quality.py` -- run_handoff_document_audit builds one index for the whole corpus
`src/gzkit/governance/trust_audits/code_quality.py` -- _forbidden_feature_tag_errors, the third tier surface (GHI #860)
`features/distribution_invariant.feature` -- @slow removed, header corrected, runtime figure re-dated
`docs/governance/distribution_baseline.md` -- the false exclusion claim and the duplicate-CI-step advice, corrected
`tests/governance/test_mock_leakage.py` -- the broad canary (GHI #857)
`tests/governance/test_audit_check_covers_backfill.py` -- LIFO unwind plus TestPatchLeakageIntoSiblingModules
`tests/governance/test_handoff_ruling_store.py` -- RefusedCreateBooksNothingTests
`tests/governance/test_handoff_validation.py` -- TestReferencedFilesGitCostTests, the spawn-count witness
`tests/governance/test_promoted_advisory_audits.py` -- TestTierTagsOnFeatureFiles
`data/check_step_concurrency.json` -- the dated per-step record, now stale by 6.9x on one row
`.gzkit/handoffs/rulings.jsonl` -- the corpus, still carrying two orphaned-source entries

## Settled Rulings

474 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
