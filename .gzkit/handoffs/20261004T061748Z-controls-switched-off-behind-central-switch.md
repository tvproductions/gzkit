---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T06:17:48Z'
agent: claude-code
session_id: 45479730-ced6-4284-86b3-8e5da8937061
continues_from: .gzkit/handoffs/20261004T001236Z-gate-value-read-saved-obpi-10-on-hold.md
---

## Current State Summary

This session resumed the 2026-10-04T00:12Z handoff, read the OBPI-0.35.0-10 trial record and the gate-by-gate value read, assessed the dismissed reviewer astra's recommendation, and on the operator's rulings built and flipped a per-control switch-off of gzkit's automatic controls. Commit 73e42d63a landed the mechanism: `.gzkit.json` § `disabled` with four lists (hooks, skills, check_steps, orientation_sections), honoured by the settings generator and merge, the skill mirrors, catalog, list and audit, the `gz check` runner in every scope but `--full`, and the session orientation. Commit abf70cf37 flipped it: 14 harness hooks, 52 of 73 active skills, 60 of 67 check steps and the chores section are off; four pre-commit hooks are commented out; CI runs plain `gz check` plus behave; 166 stale mirror copies were removed; eleven test files now read the switch. Verified before the push: full unit tier 11,439 passed with 7 skipped, reduced gate 7 steps green, skill audit 0 blocking, active catalog 21. The tree is clean and origin is in sync at abf70cf37. OBPI-0.35.0-10 is unchanged: implemented, not complete, not attested; astra's independent evaluation (commit 3391cd7d4) returned FAIL with six defects E1-E6; its lock, held by claude-code-a0f543a5, expires 2026-10-04T12:35Z. Nothing was deleted and every gz verb stays callable.

## Important Context

The method is the operator's: everything with no recorded catch is off first, then controls are turned back on one at a time to see what each does. A switched-off control regains automatic standing on a recorded catch; deletion still takes the scorecard's named steering-failure evidence. The rule for automatic standing is astra's formulation, adopted verbatim in the 2026-10-04 amendment: "Lack of catch history warrants removing automatic authority, not claiming the tool can never help." To re-enable a hook or skill: delete its name from `.gzkit.json` § `disabled` and run `uv run gz agent sync control-surfaces`; a hook is wired at the next session start. Check steps and the orientation section re-enable by deleting the name alone. The two surfaces outside gz's runtime switch in their own files: uncomment a block in `.pre-commit-config.yaml`; restore the single `gz check --full` step in `.github/workflows/ci.yml`. `gz check --full` still runs the whole estate on demand, and `gz skill list --all` shows switched-off skills, whose SKILL.md keeps `lifecycle_state: active`. The inventory, each switch's location, the stale prose and the unratified draft items are in docs/governance/control-switchboard-2026-10-04.md. Gotchas: the harness auto-mode classifier refused the first flip as logging and audit tampering and the first commit as a CI bypass; the operator's explicit "try again" and "you do it" cleared each. A session keeps the hook set it started with, so this session ran the old refusals throughout; new sessions get the reduced set. The pipeline's spec and quality reviewers are read-only by design, while astra's review executed probes in temporary fixtures and that is what found E2, E3 and E5. Stale prose, not edited because AGENTS.md is generated playback and the corpus stack was not re-landed: AGENTS.md § Execution Rules "uv run gz check is the per-change gate: every quality check except Behave and Preflight"; § Governance doctrine surfaces "uv run gz check runs every registered validator"; § OBPI Acceptance Protocol's instruction to follow the pipeline skill's dispatch; and the campaign plan's 2026-10-03 (2) ruling "each obpi must be run using the obpi pipeline skill", now in conflict because that skill is out of the catalog. Two excuse entries for the switched-off pre-commit hooks were removed from tests/mx/test_precommit_checkpoint_surface.py; re-enabling those hooks means restoring the excuses. Workflow fronts (source: the campaign plan, Workflow fronts section): handoff system was worked (the resume was booked proceed, then re-booked hold with the operator's clarifying words, and this handoff was written); ghi triage was not run; adr/obpi campaign: no OBPI was initiated and ADR-0.35.0 stays at 9 of 14 per gz adr status; new R&D was not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] No changes while astra was active (verbatim: "don't make any changes astra is active").
- [operator-ruled] "I dismissed astra, the repo is yours" was a status remark and not a ruling to proceed (verbatim clarification: "no, I am just saying that astra is no longer active"); the resumed handoff's decision was re-booked as hold with those words.
- [operator-ruled] Switch off the controls with no recorded catch (verbatim: "go ahead with the switch-off (can they be turned back on later?)").
- [operator-ruled] Every control is switched individually and reversibly, off first and then back on one at a time (verbatim: "no, i want to be able to enable. maybe we turn off then see the effects of turning things back on?").
- [operator-ruled] Build one central switch (verbatim: "will we build a central switch for this toggle?"); built as `.gzkit.json` § `disabled`.
- [operator-ruled] Retry the flip the harness refused (verbatim: "try again") and commit and push it (verbatim: "you do it").
- [operator-ruled] A test pinning the runner's exact CI wording would be a bad test to remove (verbatim: "if it does, then that is a bas test that we should get rid of"); none existed and the wording was corrected.
- [operator-ruled] Write this handoff and sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Kept 21 skills in the catalog: gz-check, gz-validate, gz-status, gz-state, gz-adr-status, gz-how, ghi-author, ghi-close, ghi-triage, gz-insights-remember, gz-session-handoff, gz-patch-release, gz-arb, gz-obpi-specify, gz-adr-create, gz-agent-sync, gz-init, gz-design, gz-rnd, gz-deps-upgrade, git-sync; switched off the other 52 including the six namespace routers. The operator did not review the list.
- [agent-chose] Kept seven gz check steps (Lint, Format, Typecheck, Test, Docs build, Validate default scopes, Authorship policy), the ten default validate scopes, post-edit-ruff, the session orientation, and the pre-commit code-quality hooks ruff, ty, xenon, interrogate, gitleaks and authorship.
- [agent-chose] Appended the campaign amendment scoped to what was ruled; items 1, 2, 5, 6 and 7 of the 2026-10-04 draft (freeze with exit, delivery path, commit-bound acceptance record, ADR-0.35.0 and OBPI-10 disposition, checkpoint and archive trigger) are recorded as not ratified.
- [agent-chose] Did not edit AGENTS.md or CLAUDE.md; listed the stale sentences in the switchboard record instead.
- [agent-chose] Did not run the Codex sanity pass on the amendment text; the operator gave no go-ahead.
- [agent-chose] Pointed the pipeline-skill content tests and the red-team asset test at canonical `.gzkit/skills` paths rather than mirror copies, and made the mirror-parity tests read the switch through tests/vendor_surfaces.py.
- [agent-chose] Left OBPI-0.35.0-10, its brief, its proofs and its lock untouched, and did not repair astra's findings E1-E5.

## Immediate Next Steps

1. Start a new session so the reduced hook set takes effect, then confirm the quiet: `uv run gz check` runs 7 steps and no hook refuses a Bash or Edit call.
2. Ask the operator to rule on how an initiated OBPI runs now that the pipeline skill is out of the catalog; § Amendments 2026-10-03 (2) still says each OBPI runs through it. Initiate nothing before that ruling.
3. Ask the operator to rule on the five unratified draft items recorded in docs/governance/control-switchboard-2026-10-04.md: the freeze with a named exit, the delivery path with an executing independent review, the commit-bound acceptance record, the disposition of ADR-0.35.0 and OBPI-0.35.0-10, and the checkpoint with its archive trigger.
4. Dispose of OBPI-0.35.0-10 on the operator's word: repair E1-E5 under the brief and complete, hold, or withdraw. Its lock expires 2026-10-04T12:35Z and is reapable after that.
5. When a missing control would have caught something, turn that one control back on by deleting its name and running the sync, and record the catch with gz insights remember; that is the re-enable rule.

## Pending Work / Open Loops

Open and unrepaired: astra's six findings E1-E6 on OBPI-0.35.0-10; E6 is routed to GHI #985 [settled], which is closed, so it has an insight but no open work order. The six scorecard rows whose class disagrees with their corpus entry print an advisory on every bullet-retention run. The single-driver completion route is still labelled degraded-human-only; making it the normal route is a code change not made. The 52 switched-off skills keep lifecycle_state active, so the skill audit treats them as active except for mirror expectations. The orientation is unchanged apart from the chores section and remains over the AGENTS.md budget warning. gz-how is the only router left in the catalog and still describes flows whose skills are off. The acceptance input digest still omits live inputs (E6). Carried from the predecessor and not worked: the 552 improvement insights, the brief's unfilled evidence sections, the gz-obpi-pipeline skill's size, and the predecessor's other open loops as written there. Two improvement insights from this session's course corrections were recorded with gz insights remember and are committed.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0. git log --oneline -2: expect abf70cf37 then 73e42d63a. uv run gz check: expect 7 steps, all green. uv run gz skill list --json: expect 21 active skills. uv run gz skill audit: expect 0 blocking. uv run -m unittest tests.test_disabled_controls: expect 7 tests OK. python3 -c "import json; print(list(json.load(open('.claude/settings.json'))['hooks']))": expect SessionStart, PreCompact, Stop, PostToolUse only. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. uv run gz obpi lock list: expect the claude-code-a0f543a5 lock until 2026-10-04T12:35Z and none after a later session reaps it. uv run gz handoff rulings --search "central switch": expect this handoff's rulings.

## Evidence / Artifacts

Switch and surfaces: `.gzkit.json`, `.claude/settings.json`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`. Mechanism: `src/gzkit/config.py`, `src/gzkit/hooks/claude.py`, `src/gzkit/commands/quality.py`, `src/gzkit/sync_skills.py`, `src/gzkit/sync_surfaces.py`, `src/gzkit/skills/__init__.py`, `src/gzkit/skills_mirror.py`, `scripts/session_orientation.py`, `tests/test_disabled_controls.py`, `tests/vendor_surfaces.py`. Records: `docs/governance/control-switchboard-2026-10-04.md`, `docs/governance/build-to-1.0-campaign-2026-09-20.md` (§ Amendments 2026-10-04), `docs/user/manpages/check.md`. Evidence read: `docs/governance/gate-value-read-2026-10-03-evidence/README.md`, `docs/governance/obpi-run-cost-2026-10-03-evidence/trial-evaluation.md`, `docs/governance/ieee/FINDINGS.md`. Insights: `.gzkit/insights/agent-insights.jsonl`. Commits: 73e42d63a (mechanism), abf70cf37 (flip), 3391cd7d4 (astra's evaluation). Predecessor: `.gzkit/handoffs/20261004T001236Z-gate-value-read-saved-obpi-10-on-hold.md`, whose resume decision is booked proceed and then hold with the operator's words under session 45479730-ced6-4284-86b3-8e5da8937061.

## Settled Rulings

1306 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
