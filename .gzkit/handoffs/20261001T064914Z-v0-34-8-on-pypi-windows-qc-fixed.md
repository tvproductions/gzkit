---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-01T06:49:14Z'
agent: claude-code
session_id: 9adabbaa-a49e-4431-83ee-52b6cddfb4ca
continues_from: .gzkit/handoffs/20261001T004323Z-v0-34-8-released-hollow-gates-filed.md
---

## Current State Summary

v0.34.8 is on PyPI (wheel and sdist uploaded 2026-10-01T06:23:56Z/06:24:00Z), published from the existing v0.34.8 tag (checkout 5f6df4b) by a new workflow_dispatch path in release.yml, run 36824471515. Its tag-push run 36797509249 had failed at uv build because e43c55c90 committed three .codex/tmp/arg0 symlinks to /opt/homebrew/bin/codex. Landed on main: gzkit.org/ redirects to Home at /user/ (6a2d59365); .codex/tmp untracked and gitignored with a test that fails on any indexed external symlink (40f7c3b71, made Windows-safe in 7bcfad1e1); release.yml dispatch path plus .codex/tmp removal before build (129327afe); .claude/scheduled_tasks.lock and .gzkit/tmp untracked and gitignored (56d48f42e); the rendition-lineage negative control writes LF fixtures and pins its expected reason, so on Windows it trips for drift, not the byte floor (b551c4896). CI on 7bcfad1e1 was green on windows-latest and ubuntu-latest; CI on b551c4896 (run 36826746141) was in progress when this was written. The predecessor's advised steps were presented and not ruled on; the operator directed this session's work instead.

## Important Context

A tag push runs release.yml as it stands AT the tag, so a fix on main never reaches a re-run of that push; publish a tag whose push failed with: gh workflow run release.yml --ref main -f tag=vX.Y.Z (docs/developer/release_process.md step 8). The PyPI job checks out refs/tags/<tag>, verifies that tag's pyproject version, and skips the build and release jobs. hatch honours .gitignore for the sdist, so ignore rules (not pyproject excludes) keep scratch out. An exclude_docs pattern without a leading slash matches at every depth: a bare README.md dropped governance/GovZero/releases/README.md; /README.md is anchored. The enforcement runner scores ANY refusal as PASS unless the claim pins expect; 65 of 87 single-fixture controls still pin none. A pasted CI diagnosis this session blamed a generated working-tree .codex/ directory; the symlinks were committed, so cleaning the working tree would not have fixed it. Verify pasted diagnoses against the repo.

## Decisions Made

- [operator-ruled] Site root should be Home (verbatim: "I think the current / path in our docs is wrong, this should be \"home\" https://gzkit.org/user/").
- [operator-ruled] Do not start v0.34.9 (verbatim: "no, do NOT start 0.34.9, we are NOT at that step - fix this.").
- [operator-ruled] Publish v0.34.8 via the proposed workflow fix (verbatim: "I would think a few errant symlinks would be a very easy issue to correct. why don't we do the fixes you propose?").
- [operator-ruled] Untrack the other committed runtime files (verbatim: "untrack the scheduled_tasks.lock and .gzkit/tmp files too").
- [operator-ruled] Fix the Windows rendition-lineage fixture defect (verbatim: "fix that please").
- [operator-ruled] Close the session (verbatim: "create a handoff and git-sync").
- [agent-chose] Ignored .codex/tmp/ only, not all of .codex/, because config.toml and agents/*.toml are tracked surfaces.
- [agent-chose] Fixed only _qc_negative_controls._write: a whole-registry replay under simulated Windows text mode showed no other fixture module's write_text changes a control's findings.
- [agent-chose] Recorded the course-correction and both defect resolutions with gz insights remember rather than filing GHIs; each fix was within direct-fix size and test-covered.

## Immediate Next Steps

1. Confirm CI run 36826746141 (b551c4896) is green on windows-latest and that its log no longer prints the 'unowned_byte_floor 54' rendition-lineage message.
2. Re-present the predecessor's advised steps, none ruled on this session: the four repudiation rulings (OBPI-0.0.24-04, OBPI-0.35.0-09, OBPI-0.34.0-02 repudiate and re-complete; OBPI-0.0.28-03 ledger correction), all four still ATTESTED COMPLETED in the ledger.
3. The five audit defects (closeout Demos and verify-packet run in the live checkout; validate_stage4_evidence has no production caller; justify never runs at ADR closeout; red-parity treats missing base provenance as working-tree): confirm, file through ghi-author, fix. None was filed as of this session (newest GHI #1155).
4. Ask the operator to rule on docs/evals/test-suite-integrity-audit-2026-09-24.md sections 9 and 10, which GHI #1154 waits on; then GHI #1155.
5. Carried: whether to draw the next ADR-0.35.0 OBPI, and the chore_decommission_processed emitter gap.

## Pending Work / Open Loops

GHI #1154 and #1155 open; 65 of 87 single-fixture negative controls pin no expect and can pass on an unrelated refusal (the #1154 class, measured this session). Trackers #611, #921, #978, #1028, #799 open. The predecessor's unconfirmed observations stand unfiled (patch-release diff_only bucket listing open GHIs; ghi-author runtime predicate firing on rule/skill/template edits; registry gate_targets for module-size and tautological-debt; red-parity overwriting 15 'none' rows). docs/README.md is no longer published on the site and remains a repo-browsing file. AGENTS.md is over its advisory char budget. The next release ceremony should follow docs/developer/release_process.md, whose step 8 is new.

## Verification Checklist

curl -s https://pypi.org/pypi/py-gzkit/0.34.8/json (expect version 0.34.8, a wheel and an sdist); gh run view 36824471515 (expect success, pypi job only); gh run view 36826746141 (expect both platforms success); git ls-files -s | awk '$1=="120000"' (expect empty); uv run -m unittest tests.governance.test_tracked_symlinks tests.governance.test_release_pypi_dispatch tests.governance.test_enforcement_nc_discrimination (expect OK); uv run mkdocs build --strict and grep refresh site/index.html (expect redirect to user/); git rev-list --left-right --count origin/main...HEAD (expect 0 0); uv run gz check (expect exit 0).

## Evidence / Artifacts

Docs root: `docs/index.md`, `mkdocs.yml`. Packaging: `.gitignore`, `tests/governance/test_tracked_symlinks.py`. Release path: `.github/workflows/release.yml`, `docs/developer/release_process.md`, `tests/governance/test_release_pypi_dispatch.py`. QC fixture: `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `tests/governance/test_enforcement_nc_discrimination.py`. Insights: `.gzkit/insights/agent-insights.jsonl`. Predecessor: `.gzkit/handoffs/20261001T004323Z-v0-34-8-released-hollow-gates-filed.md`.

## Settled Rulings

1241 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
