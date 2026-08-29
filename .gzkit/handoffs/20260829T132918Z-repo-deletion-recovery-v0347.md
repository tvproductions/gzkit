---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-29T13:29:18Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260829T083531Z-ci-green-916-closed-917-918-open.md
---

## Current State Summary

Two patch releases shipped and the working repository was destroyed and restored.

v0.34.6 (34 GHIs) and v0.34.7 (1 GHI) are published, Latest is v0.34.7, pyproject reads 0.34.7. GHI #917 (Behave shard planner non-recursive glob) and #918 (uncalled step-module teardowns) were fixed and closed. GHI #919 was filed and remains OPEN. GHI #920 was filed and closed.

MID-SESSION INCIDENT: the agent deleted /Users/jeff/Documents/Code/gzkit. A negative-control test fixture was authored as `return REPO`, and `_run_single_claim` rmtree`s whatever Path a fixture returns, so `python -m unittest` removed the working tree. Recovery was a fresh clone from origin at cb1ef75f. All committed work survived; gitignored files did not. The root defect (an unguarded destructive cleanup) is fixed and closed as GHI #920 in b2a97951.

HEAD is b2a97951, branch main, 0 ahead / 0 behind origin, working tree clean, `uv run gz check` exit 0.

## Important Context

The fresh clone silently dropped two things git does not track, and both were caught only because `gz check` failed:

1. LOCAL GIT IDENTITY. user.name/user.email fell back to global config, which is the operator personal address. The next commit would have carried operator PII into history — AGENTS.md says that needs a filter-repo rewrite plus force-push to undo. Restored to g0 / 2949663+ahuimanu@users.noreply.github.com via `git config --local`. Verify this in ANY future fresh clone before the first commit.
2. PRE-COMMIT AND PRE-PUSH HOOKS. Not installed by clone. Restored with `uvx pre-commit install --hook-type pre-commit --hook-type pre-push` — note `uvx`, not `uv run`; pre-commit is not a project dependency and is not on PATH.

`.claude/settings.local.json` is gitignored and was NOT recovered. Its contents are unknown. Permission prompts may differ from before.

On the incident: `_mkroot` is the ONLY sanctioned NC fixture builder and always returns tempfile.mkdtemp(). Any fixture returning a live directory is now refused. The guard resolves both sides because TMPDIR is a symlink on macOS (/var/folders -> /private/var/folders); comparing one resolved path against an unresolved root would reject every legitimate fixture.

GHI #919 and #920 are siblings in the same runner. #920 (fixed) is the destructive-cleanup arm. #919 (open) is the verdict arm: `_command_fails_argv` returns a two-valued verdict over a three-valued world — caught / did not catch / could not observe — so a control that could not RUN is reported as theater. A DNS outage during the v0.34.7 git-sync made radon unfetchable and produced exactly that false accusation across three gate steps.

## Decisions Made

- [operator-ruled] Cut v0.34.6 as drafted and correct GHI #915 evidence SHAs (verbatim: "Approved, and fix GHI #915's SHAs"). #915 closing comment cited 37843341/6e50b90d, which resolve as git objects but are unreachable from main; the durable pair is 379ac35a/c92237e0.
- [operator-ruled] Land #917 and #918 (verbatim: "land 917 and 918").
- [operator-ruled] Cut v0.34.7 with #917 headlining and #918 disclosed as excluded (verbatim: "Approved as drafted"). #918 touched zero src/gzkit files and the wheel packages only src/gzkit, so it does not ship in the released artifact.
- [operator-ruled] Resolve GHI #919 as warn-and-abstain rather than fail-the-gate (verbatim: "warn and abstain"). An unobserved control is not evidence of enforcement, so it must not count as verified; it is also not evidence of theater, so it must not fail the gate. NOT YET IMPLEMENTED — the in-progress work was destroyed with the repo.
- [operator-ruled] Fix the unguarded rmtree immediately (verbatim: "fix it now"). Landed as b2a97951, GHI #920.
- [agent-chose] Delete rather than wire the #918 teardowns. Wiring would make environment.py import from a step module, recreating the N-way coupling GHI #916 replaced with one process-level stopall(). patch_release_steps.py already demonstrates the conforming shape.
- [agent-chose] Keep features/steps enumeration NON-recursive while making features/ recursive in #917. Verified against behave.runner.load_step_definitions: nested step modules load only under use_nested_step_modules, which behave.ini does not set.
- [agent-chose] Leave the v0.34.6 Known-issues section unchanged after #917/#918 landed. It was accurate at publish and remains accurate for that artifact, since the shipped wheel still contains both defects.
- [agent-chose] Report GHI #919 as a fresh sibling of #793 rather than reopening #793. #793 fixed the presentation channel (Rich SGR codes) and that fix has not regressed; it cannot reach dependency availability.

## Immediate Next Steps

1. Decide whether to reconstruct `.claude/settings.local.json`. It was gitignored and is unrecoverable from origin; its prior contents are unknown. Permission allowlists that existed before this session are gone.
2. Decide whether to implement GHI #919 (warn and abstain). The operator has already ruled on the design; only the implementation was lost. Shape: an INCONCLUSIVE sentinel whose __bool__ raises, a fourth ClaimRunResult.outcome, an inconclusive_count on RunnerResult, `_command_fails_argv` returning it on an unexpected non-zero exit (exit 0 stays FACADE — the tool ran and found nothing), and both consumers (quality.py enforcement floor, qc_binding.py) excluding it from failures while surfacing it. Roughly 25 source lines across 4 files plus tests.
3. Consider drawing campaign work. Nothing has been drawn in six sessions; docs/governance/build-to-1.0-campaign-2026-08-16.md sits at 7/25 with Movement B (calibrate the airlock gate before widening it) topmost. Only the operator can initiate it.
4. Carried forward and NOT re-verified this session: GHI #907 (authorship rule scopes file content, witness reads only git config) is OPEN and is directly adjacent to the identity gap this session hit on the fresh clone.

## Pending Work / Open Loops

GHI #919 — OPEN. Operator has ruled (warn and abstain); implementation lost with the repo and not redone. This is the only ruled-but-unbuilt item.

GHI #907 — OPEN, carried forward from prior sessions, not re-verified here beyond confirming its state. Adjacent to this session's fresh-clone identity gap.

`.claude/settings.local.json` — unrecoverable. No inventory of what it held exists.

Residual disclosed in GHI #920 [settled] and deliberately not claimed as fixed: `_is_disposable_fixture` answers "is this under the temp root", not "did this runner create it". A fixture returning someone else's temp directory would still be removed. Narrower exposure than the one closed; no instance known.

Uncovered cause disclosed in GHI #917 [settled]: a nested step module falsely flagged as a dist/ writer is deliberately NOT covered, because behave does not load nested step modules under the current behave.ini.

Advisory, unchanged and not acted on: `gz check` reports 696 unlinked specs (REQs with no test), and the instructions-files budget warns that AGENTS.md renders past the Codex delivery cap.

## Verification Checklist

git rev-parse --short HEAD                      # expect b2a97951
git status --short                                # expect empty
git rev-list --left-right --count origin/main...HEAD  # expect 0  0
git config --local user.email                     # MUST end @users.noreply.github.com
ls .git/hooks/pre-commit .git/hooks/pre-push      # both must exist
uv run gz check                                   # expect exit 0, "All checks passed"
uv run python -m unittest tests.governance.test_nc_fixture_cleanup_guard   # expect OK, 3 tests
uv run python -m unittest tests.governance.test_behave_sharding            # expect OK, 13 tests
uv run python -c "from pathlib import Path; from gzkit.enforcement import _is_disposable_fixture; print(_is_disposable_fixture(Path.cwd()))"   # expect False
gh issue view 919 --json state                    # expect OPEN
gh release list --limit 2                         # expect v0.34.7 Latest

## Evidence / Artifacts

`src/gzkit/enforcement.py`
`tests/governance/test_nc_fixture_cleanup_guard.py`
`src/gzkit/quality.py`
`tests/governance/test_behave_sharding.py`
`features/steps/justify_steps.py`
`features/steps/obpi_completion_coverage_gate_steps.py`
`RELEASE_NOTES.md`
`CHANGELOG.md`
`docs/releases/PATCH-v0.34.6.md`
`docs/releases/PATCH-v0.34.7.md`
`.gzkit/handoffs/20260829T083531Z-ci-green-916-closed-917-918-open.md`

Commits: b2a97951 (GHI #920 guard), cb1ef75f (v0.34.7 release), 1d785a21 (changelog), 4c513a93 (GHI #918), fa098fc0 (GHI #917), 8f16cd02 (v0.34.6 release).
GitHub: releases v0.34.6 and v0.34.7 published; GHI #919 open; GHI #915, #917, #918, #920 closed with evidence comments.

## Settled Rulings

588 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
