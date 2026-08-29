---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-29T08:23:52Z'
agent: claude-code
session_id: 3fdca4e8-4467-4e7f-b038-6c255516e2b8
continues_from: .gzkit/handoffs/20260829T074045Z-session-exit-bookmark.md
---

## Current State Summary

CI was red on `main` for six consecutive runs (2026-08-29T00:55 through 07:37, both `ubuntu-latest` and `windows-latest`). Root-caused, fixed, and verified green. Two adjacent defects found during the investigation were filed rather than fixed.

The session opened with a pasted third-party diagnosis attributing the failure to the spec-test-code drift advisory (696 unlinked specs) and recommending that `gz check` return 0 on advisory-only drift. That diagnosis was WRONG and following it would have disabled a working gate while leaving the real failure in place. `src/gzkit/commands/quality.py` raises SystemExit(1) only on `not all_passed`; drift never touches the exit code. The advisory prints last, which is what made it look causal — it prints identically on green runs, including the one that just passed.

The real failure was a failing Behave step: two scenarios in `features/patch_release.feature` asserting `gz patch release --dry-run` exits 0 while arranging none of the gh authentication that command fails closed without. They passed for months on borrowed state — the operator's ambient gh login locally, and in CI on a fake gh that `features/steps/evaluation_feedback_loop_steps.py` installed process-wide and never removed. The commit that sharded Behave across four processes (GHI #906) split donor and victim into separate processes and the borrowed precondition vanished.

Landed on `main` and pushed: 4de926d2 (the fix, GHI #916) and a3b3e714 (the prior session's exit bookmark, committed separately so it would not bundle into the fix). Both CI runs green on both platforms. Tree clean, origin/main in sync 0/0, no active OBPI locks.

## Important Context

**Patching a module attribute named subprocess.run is NOT module-local.** A module's `subprocess` name is a reference to the singleton subprocess module, so patching its `run` attribute rebinds it process-wide. The dotted-path string reads like scoping and provides none. Contrast the target `gzkit.commands.patch_release.run_exec`, which IS local because an `import`-bound name is a fresh binding in the importing module. This distinction is the whole mechanism of the outage and is easy to misread in either direction.

**Behave shards are planned by FILE BYTE SIZE** (`src/gzkit/quality.py`, the shard planner). Shard membership is therefore unstable across commits: `features/patch_release.feature` sat in shard 1 at the CI commit and shard 2 at HEAD. Before the fix, the gate's verdict depended on which scenarios happened to share an interpreter, so an ordinary edit to an unrelated feature file could have flipped CI with no change to the code under test. Stopping all patchers in `features/environment.py` removes that coupling entirely.

**Parallelism did not create this defect; it revealed one.** GHI #906 was initially the obvious suspect and is innocent — it changed no test and no production behavior. Resist blaming the sharding commit when reading this back.

**A green test can be a false witness.** These scenarios were green under two DIFFERENT accidents (ambient local login; borrowed CI fake). Neither is a precondition the scenario declared.

**The tautological-test audit and the cross-platform subprocess validator both fired on my first draft of the new tests and both were right.** The audit caught a text-shape assertion on a feature file; the validator caught a subprocess capture missing an errors argument, which would have raised on Windows runners. Do not route around these — each caught a real defect in work authored this session.

## Decisions Made

- [agent-chose] Rejected the pasted diagnosis rather than implementing it, after disproving it against `src/gzkit/commands/quality.py` (the exit is gated on `not all_passed`, not on drift). Implementing it would have made a real gate advisory while leaving CI's actual failure untouched.
- [agent-chose] Fixed the CLASS, not the instance (AGENTS.md § DO IT RIGHT #1): scenario teardown now stops every patcher any step started, so none can outlive its scenario. Rejected the narrower alternative of calling the one step module's own stop helper, which would have fixed that module and left the other.
- [agent-chose] Made the scenario declare its own gh precondition (a step stubbing ONLY the auth probe, delegating every other exec to the real helper) rather than relaxing the auth check for the dry-run path. Changing the command would have altered a runtime contract and crossed into OBPI-ceremony routing; the command genuinely needs gh, so the test must arrange it.
- [agent-chose] Routed as GHI-tracked direct repair after checking the § Defect-fix routing precondition on the precise surfaces: every matching OBPI brief is terminal, so no live brief owns the work.
- [agent-chose] Filed #917 and #918 rather than fixing them in-patch — both are outside the defect that had CI red, and bundling them would have widened a red-gate repair.
- [operator-ruled] Push the fix to origin/main so CI could verify against a real unauthenticated runner (verbatim selection: "Push now").
- [operator-ruled] Commit the prior session's exit bookmark (verbatim: "yes, commit it") and push it (verbatim: "push it too").
- [operator-ruled] File both residual findings as GHIs (verbatim: "file both of those GHIs").

## Immediate Next Steps

1. Close GHI #916 citing commit 4de926d2 — the fix is landed, pushed, and CI-verified green on both platforms, so the GHI's routing purpose is fulfilled. Use `/ghi-close`; it was left open only because the session's asks ended before the lifecycle did.
2. Decide whether to land GHI #917 (shard planner drops nested feature files; the conservation test shares the blind spot). Direct-fix sized: a recursive glob, plus enumerating the test's expected set independently of the planner. A regression test MUST add a nested fixture feature or the new assertion is as blind as the old one.
3. Decide whether to land GHI #918 (a gh patcher teardown defined but never called). Either wire the call or delete the function; the current middle state is the only one that is not defensible.
4. Consider drawing campaign work. Nothing has been drawn in FIVE sessions; `docs/governance/build-to-1.0-campaign-2026-08-16.md` sits at 7/25 with Movement B (calibrate the airlock gate before widening it) topmost. Only the operator can initiate it.
5. Carried forward untouched from the prior session and NOT re-verified this session: GHI #912 [settled] (readiness-audit reachability predicate), the missing manpages index under `docs/user/` on a fresh tree, GHI #907 (scope-blocked by #611), and GHI #894.

## Pending Work / Open Loops

- GHI #916 is fixed, committed, pushed, and CI-green, but still OPEN. It needs closing with the 4de926d2 SHA. This is the only loop this session opened and did not close.
- GHI #917 — latent, not currently firing: a search for feature files below the top level returns none, so no scenario is being dropped today. It arms the moment anyone organizes `features/` into subdirectories, which nothing currently warns against.
- GHI #918 — consequence already neutralized by the teardown that landed in 4de926d2; what remains is a decoy stop-helper that reads as a discharged obligation. Not an active leak.
- The spec-test-code drift advisory (696 unlinked specs) is UNCHANGED and is NOT a defect in the gate. It printed on the green runs too. Do not act on it as a CI failure; that misreading is what opened this session.
- Carried forward from the prior session and untouched: GHI #912 [settled], GHI #907 (scope-blocked by #611), GHI #894, and the missing manpages index under `docs/user/` on a fresh init tree.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` returned 0 and 0 (in sync at handoff time).
- `git status --short` clean apart from this handoff.
- `uv run gz obpi lock list` reported no active locks.
- `gh run view 33242231040` reported success on both check jobs for commit 4de926d2.
- `gh run view 33242351081` reported success on both check jobs for commit a3b3e714.
- `uv run gz check` reported all checks passed (run before commit 4de926d2; the pre-push gate re-ran it on both pushes).
- Reproduce the original failure on any tree lacking the fix: run Behave against `features/patch_release.feature` alone with the gh config dir pointed at an empty directory and the gh token environment variables blanked.
- Confirm the fix holds under CI's shape: that same isolated run passes 3 scenarios; a full `uv run -m behave` passes 408; the sharded path returns exit 0.
- Both new tests were verified RED against the unfixed source before being accepted.

## Evidence / Artifacts

- `features/environment.py` — scenario teardown now stops every started patcher (the class fix).
- `features/patch_release.feature` — both dry-run scenarios now declare the gh-authenticated precondition.
- `features/steps/patch_release_steps.py` — new; stubs only the gh auth probe and delegates every other exec to the real helper.
- `tests/governance/test_behave_scenario_isolation.py` — new; three tests, all verified RED first.
- `features/steps/evaluation_feedback_loop_steps.py` — the donor of the leaked patch (not modified).
- `features/steps/justify_steps.py` — the second instance, tracked as GHI #918 (not modified).
- `src/gzkit/quality.py` — the shard planner and runner, the surface GHI #917 is filed against (not modified).
- `src/gzkit/commands/patch_release.py` — the fail-closed gh probe at the centre of the outage (not modified).
- `tests/governance/test_behave_sharding.py` — carries the conservation test whose blind spot GHI #917 documents (not modified).

## Settled Rulings

584 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
