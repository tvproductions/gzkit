---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T00:56:11Z'
agent: claude-code
session_id: 89db8fc3-11a3-4b76-8abe-aeb3edb12ce7
continues_from: .gzkit/handoffs/20260921T002935Z-land-survey-and-unruled-prior-advice.md
---

## Current State Summary

The operator ruled on the five carried advised steps and the session then discharged one of them. TRACK 1, LANDED: the cross-repository citation defect this session's predecessor surfaced is repaired and committed at 1841c53d9, TDD with RED observed on every increment. `uv run gz check` exits 0 (observed, not inferred: an earlier run of the same gate was detached by a session fork and its exit code lost, so it was re-run). TRACK 2, ANSWERED NOT ACTED: three operator questions were researched and reported — why the gz-skills local OpenCode plugin was replaced by a package adapter, what GHI #1069 still needs from the operator, and the state of ADR-0.35.0 as campaign priority. Nothing was initiated on ADR-0.35.0 and no OBPI lock was claimed. `uv run gz obpi lock list` reports no active locks. Layer-2 state otherwise unchanged from the predecessor: ADR-0.39.0 Pending at 0 of 7, ADR-0.35.0 Pending at 7 of 13 with closeout BLOCKED, open GHI queue 56.

## Important Context

THE REPAIR AND WHY ITS SHAPE MATTERS. A number glued to a repository token is GitHub's qualified citation form, and it is what a handoff spanning clones writes. The extractor read only the number, so the `gh` adapter — which runs in one project root — answered from the LOCAL repository. `StepReference` now carries the repository a citation names, `None` still meaning this repository. The alternative considered and rejected was dropping a foreign citation at extraction: that trades a wrong answer for no answer, and `ReferenceState.UNKNOWN` already exists to say "not verified". The adapter refuses a foreign citation without calling `gh` and without consuming its offline latch, so one foreign reference cannot blind every citation after it.

THE FALSE MARK IN THE COMMITTED PREDECESSOR STANDS. `.gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md` carries a settled mark on an issue that is open in another repository. It was left in place deliberately: the archive records what the annotator did, and rewriting it would falsify that record. The fix prevents the next one; it does not retroactively correct this one.

A SIBLING CLONE IS UNDER CONCURRENT EDIT BY ANOTHER SESSION. `C:/Users/Jeff/source/repos/agents/gz-skills` moved while this session read it: at 00:30Z it showed two modified files and one untracked proposal, and at 00:40Z it showed twelve modified paths, one deletion and three untracked. File timestamps put edits inside that window. Nothing in that tree was touched here, and a successor should not enter it concurrently either. The OpenCode v2 work there is entirely uncommitted on top of the v0.4.0 release commit, and the install it describes is blocked until a v0.5.0 tag is published.

THE PRE-COMMIT HOOK DOES NOT RUN THE UNIT TIER. The git-sync skill states the hook runs ruff, ty, unittest and xenon, and its Red Flags table rests on that claim. The installed chain observed on this commit runs ruff lint, ruff format, ty, forbid-pytest, xenon, interrogate, surface fidelity, validator reachability, ledger vocabulary, the flagged-marker scan, end-of-file, whitespace, merge conflicts, gitleaks and authorship — no unit tier. Test coverage for this commit came from the separate full `gz check`, not from the hook. This is an observation, unrouted.

THE DRIFT ADVISORY GREW BY THIS COMMIT. `gz check` now reports three unjustified code changes alongside the standing 713 unlinked specs. Both are advisory and neither affects the exit code; the three are this session's own source edits.

## Decisions Made

- [operator-ruled] Proceed with the five advised steps carried from the predecessor handoff (verbatim: "1. ok"). Booked as `handoff_resume_decided` / `proceed`.
- [operator-ruled] Repair the cross-repository citation defect now, directly, rather than filing an issue for it (verbatim: "2. yes, do it").
- [operator-ruled] ADR-0.35.0 is campaign priority, and the operator returns to it later rather than initiating OBPI work in this session (verbatim: "5. yes, that is campaign priority." and "yes, I'll return to 0.35.0 soon").
- [agent-chose] Carried the owning repository through the reference seam instead of dropping a foreign citation at extraction, so the signal survives as UNKNOWN rather than disappearing.
- [agent-chose] Left the false settled mark in the committed predecessor handoff rather than editing a published record.
- [agent-chose] Committed the repair separately from the handoff and ledger material, so the source change carries its own TASK trailer and its own message.
- [agent-chose] Treated the operator's `/git-sync` invocation at the session start, plus two follow-up questions about sync completion, as authorization to push this session's work.

## Immediate Next Steps

1. When the operator returns to ADR-0.35.0, read its OBPI table before choosing anything: brief 08 is Active with runtime state IN PROGRESS and no lock held, brief 07 is Draft and unstarted, and briefs 11 and 12 have no brief text at all. Only the operator initiates OBPI work, and brief 08 has been paused since 2026-08-23 so it needs a reconcile before any resume.
2. Rule the two open implementation choices on GHI #1069, which is deferred behind campaign priority rather than closed: whether the detector arm lives inside `audit_line_endings` or as a sibling audit, and whether its scope stays at `tests/**` per the closure contract or also measures `src/**`. The GHI already authorizes direct repair, so no ADR or OBPI is owed.
3. Decide the disposition of OBPI-0.35.0-08's dangling state — resume, withdraw, or leave it recorded — since a runtime state of IN PROGRESS with no lock and no proof is readable as any of the three.
4. Route or rule on the pre-commit hook gap: the git-sync skill claims the hook runs the unit tier and the installed chain does not. Either the skill text is wrong or the hook is missing a step, and the two cannot both be right.
5. Leave the gz-skills clone to the session working in it. Its OpenCode v2 bundle is uncommitted and its install path opens only when a v0.5.0 tag is published.

## Pending Work / Open Loops

DEFERRED BY RULING, NOT CLOSED. GHI #1069, verified OPEN, deferred behind campaign priority with two implementation choices unruled.

OBSERVED THIS SESSION, UNROUTED. The pre-commit hook chain does not run the unit tier while the git-sync skill says it does. The drift scope's three unjustified code changes, which are this session's own source edits.

CARRIED, UNRESOLVED. OBPI-0.35.0-08's IN PROGRESS state with no lock and no completion proof. GHI #1063, counting 51 validator scopes never invoked, with the remainder unmeasured. The standing 713 unlinked specs. GHI #1028, open under the explicit campaign hold for 2026-09-19 and not a next action until the operator resumes it. Commit 84ea8e435, which carries no Task trailer and is published, so repair would need a force-push that policy forbids.

OUTSIDE THIS REPOSITORY. The gz-skills OpenCode v2 bundle: `adapters/opencode/gz-skills.js`, a rewritten install guide, a version bump to 0.5.0, a new adapter test and eleven other modified paths, all uncommitted on top of the v0.4.0 release commit, with another session active in that tree. Not installable until the tag is published.

A LIMIT, NOT A DEFECT. The repaired annotator now says UNKNOWN for a foreign citation. It does not resolve one. Resolving a citation in another repository would need a repository-aware resolver, which nothing here asks for yet.

## Verification Checklist

Run `uv run gz check` and expect exit 0. If you pipe it, use `set -o pipefail` first: the verifier-pipe-gate hook refuses a bare pipe. Do not run it detached across a session boundary — an earlier run in this session was detached by a fork and its exit code was lost even though it had printed a pass.

Run `uv run -m unittest tests.commands.test_reference_checker tests.governance.test_handoff_api tests.test_handoff_cli` and expect 101 tests passing.

Confirm the repair against observed behaviour rather than the tests: build `live_reference_checker` on this project root, extract the references from a step naming both a qualified foreign citation and `#1069`, and expect the foreign one to resolve `unknown` and `#1069` to resolve `live`.

Run `git log -1 --format=%H -- src/gzkit/handoff_api.py` and expect 1841c53d9, whose message carries `Task: TASK-fix-foreign-repo-citations`.

Run `git rev-list --left-right --count origin/main...HEAD` and expect zero and zero.

Run `uv run gz obpi lock list` and expect no active locks. Run `uv run gz adr status ADR-0.39.0-gzkit-internal-config-surface` and expect Pending with every brief pending and draft; anything else means OBPI work began without operator initiation.

Run `gh issue view 1069 --json state` and expect OPEN.

In `C:/Users/Jeff/source/repos/agents/gz-skills` run `git status --short` READ-ONLY and expect an uncommitted v0.5.0 bundle; do not edit that tree while another session holds it.

## Evidence / Artifacts

`src/gzkit/handoff_api.py`
`src/gzkit/commands/reference_checker.py`
`src/gzkit/commands/handoff.py`
`tests/commands/test_reference_checker.py`
`tests/governance/test_handoff_api.py`
`.gzkit/handoffs/20260921T002935Z-land-survey-and-unruled-prior-advice.md`
`.gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md`
`.gzkit/insights/agent-insights.jsonl`
`.gzkit/ledger.jsonl`
`docs/governance/build-to-1.0-campaign-2026-09-20.md`

## Settled Rulings

1009 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
