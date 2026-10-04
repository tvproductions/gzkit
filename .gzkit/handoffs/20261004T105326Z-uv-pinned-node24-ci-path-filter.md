---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T10:53:26Z'
agent: claude-code
session_id: 9bc22653-d764-4d49-97e0-ecedc08e1eab
continues_from: .gzkit/handoffs/20261004T102117Z-six-ghis-filed-five-closed-bound-1800.md
---

## Current State Summary

This session continued after the predecessor handoff was written, on three further operator directions, and landed two commits. First, 3a172c7ca: uv is pinned to one exact version for the developer host and CI, and every workflow action that targeted Node 20 is moved to a Node 24 version. Second, 106b5b660: ci.yml no longer runs the sweep for a push that changes only session records. The local gz check passed on the tree with the pin (exit 0, on uv 0.12.23). origin/main is in sync at b07f29f99. Two CI runs were still in progress when this was written, and neither had been read: 37196265264 on a6e867750 (the pin and Node 24 commit; its ubuntu-latest job had finished green, windows-latest was running) and 37196682011 on b07f29f99 (the same tree plus the path filter). Whether CI installed uv 0.12.23 from the pin, and whether the Node 20 warning is gone, is therefore unconfirmed. GHI #1165 received its second measurement: CI run 37195226152 on 422f8a6df passed with windows-latest Test 870.97s, so two consecutive healthy Windows runs are in hand under the 1800 second bound (1117.23 and 870.97 seconds). GHI #1165 and GHI #1171 remain open.

## Important Context

The uv pin is pyproject.toml, tool.uv required-version, set to ==0.12.23. It is the one authority: uv refuses to run in this repository on any other version, and astral-sh/setup-uv reads it in every workflow. The developer host was moved to 0.12.23 with uv self update in the same pass. Consequence for every future session: after any uv update, every uv command here fails until the pin is moved, and gz-deps-upgrade step 1 (skill 1.3.0) now says so. docs.yml used the shell installer and now uses setup-uv. setup-uv is referenced by the exact tag v10.2.0 because its floating major tags ended at v7. The Node 20 class was six references, not the one the runner flagged: setup-uv v6 and v4, checkout v4, upload-artifact v4 and download-artifact v4, across ci.yml, queue-hygiene.yml, release.yml and docs.yml. The path filter ignores pushes whose every changed file is under .gzkit/handoffs, .gzkit/insights or .gzkit/ledger.jsonl; pull requests are unchanged. The sync of this handoff is the first records-only push since the filter landed, so it is the filter's first observation: no CI run should start for it. The step-level comparison recorded on GHI #1171 changed that question: Windows is not uniformly slower, the cost sits in the unit tier, Behave and the handoff-documents validator, and the unit tier's CI figure includes contention with Behave, which the gate runs in the same thread pool. The operator corrected the push cadence this session and it is recorded as an insight: three pushes in 45 minutes each started a full run, one of them for a handoff alone. Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section): handoff system was worked (this successor); ghi triage was not run; adr/obpi campaign is unchanged, with ADR-0.35.0's landed count read from gz adr status; new R&D was not touched. OBPI-0.35.0-10's lock is still held by claude-code-a0f543a5 and expires at 2026-10-04T12:35Z. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Fix the two CI findings read from the Windows job log: uv unpinned in CI, and setup-uv on Node 20 (verbatim: "fix:" followed by the two findings).
- [operator-ruled] uv keeps up with latest and stays the same on the developer host and in CI (verbatim: "why not just latest? I also want to keep up with latest and have them sync'd").
- [operator-ruled] The route to that is an exact pin moved to the latest release, with the agent updating the local binary (the operator's message selecting it, verbatim: "Which do you want for uv: pin to latest, with me running uv self update"). Rejected alternative offered: leaving CI on latest, unpinned.
- [operator-ruled] Node gets the same treatment, on the current LTS (verbatim: "same with node, LTS is 24").
- [operator-ruled] The push cadence was a loop and had to stop (verbatim: "we are stuck in a loop of rerunning CI").
- [operator-ruled] ci.yml ignores records-only pushes (verbatim: "add the paths-ignore").
- [operator-ruled] Write this successor before the session is cleared (verbatim: "write the handoff").
- [agent-chose] Included .gzkit/insights in the path filter beside the handoff and ledger paths the operator was offered, because every sync commit of the last day was made of exactly those three paths.
- [agent-chose] Did not dispatch docs.yml to verify it, because a dispatch deploys the site.
- [agent-chose] Left CI run 37196265264 running although run 37196682011 covers the same tree; cancelling it was offered and not ruled on.
- [agent-chose] Added no check that every workflow installs uv through setup-uv with no version input of its own.

## Immediate Next Steps

1. Read CI runs 37196265264 and 37196682011. Expect both jobs green in each. In a job log, expect setup-uv to report installing uv 0.12.23 found in pyproject.toml, with no "Falling back to latest" line and no "Node.js 20 is deprecated" warning. If either run is red, read the failing step before anything else: the pin and the action versions are the only changes those runs test.
2. Check whether the sync of this handoff started a CI run: gh run list --workflow CI --limit 3. None should exist for this handoff's commit. If one does, the path filter did not take and ci.yml needs reading again.
3. Record the windows-latest Test durations of those runs on GHI #1165. With two healthy runs already in hand, the operator decides how many more close it; close as fixed citing 0d632cb80 and the runs.
4. The operator opens the gz-design dialogue for the tune-up, as the predecessor handoff advises, including what an abort after failed verification does with its lock and whether one unit of work per session ended by a handoff becomes canon.
5. After 2026-10-04T12:35Z, the operator invokes gz-obpi-pipeline for OBPI-0.35.0-10, and then for each repudiated OBPI in turn: OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09. The human-review judgment and the attestation are the operator's words; never author them.

## Pending Work / Open Loops

The predecessor handoff's open loops are unchanged and are not restated here. New in this stretch: release.yml runs only on a version tag and docs.yml only on a release or manual dispatch, so their action-version and uv-install changes are unexercised until the next release; the first release after this is the test, and a failure there is most likely a changed input or default in upload-artifact v7, download-artifact v8 or setup-uv v10.2.0. Nothing mechanical stops a future workflow from installing uv by another route or passing its own version. Files under the three ignored paths are now validated server-side only at the next push that is not ignored. GHI #1171 still needs per-module unit-tier durations from both runners. The operator's handoff-retention observation still has no work order.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0. uv --version: expect uv 0.12.23. grep -n "required-version" pyproject.toml: expect ==0.12.23. grep -rn "uses:" .github/workflows: expect no setup-uv below v10.2.0, no checkout, upload-artifact or download-artifact at v4, and no install.sh line. grep -n "paths-ignore" -A4 .github/workflows/ci.yml: expect the three .gzkit paths. gh run list --workflow CI --limit 4: expect runs 37196265264 and 37196682011 completed with success, and no run for this handoff's sync commit. gh issue view 1165 --json state and gh issue view 1171 --json state: expect OPEN. uv run gz obpi lock list: expect no OBPI-0.35.0-10 lock after 2026-10-04T12:35Z. uv run gz handoff rulings --search "paths-ignore": expect this handoff's ruling.

## Evidence / Artifacts

Changed: `pyproject.toml`, `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/queue-hygiene.yml`, `.github/workflows/release.yml`, `.gzkit/skills/gz-deps-upgrade/SKILL.md`. Predecessor: `.gzkit/handoffs/20261004T102117Z-six-ghis-filed-five-closed-bound-1800.md`. Commits: 3a172c7ca (uv pin and Node 24), 106b5b660 (path filter), a6e867750 and b07f29f99 (syncs). CI runs: 37195226152 (passed, 422f8a6df, windows-latest Test 870.97s), 37196265264 (in progress when written, a6e867750), 37196682011 (in progress when written, b07f29f99). Issue comments: GHI #1165 (two run measurements) and GHI #1171 (step-level comparison of both runners, two runs). Insight recorded 2026-10-04, scope ci-push-cadence.

## Settled Rulings

1336 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
