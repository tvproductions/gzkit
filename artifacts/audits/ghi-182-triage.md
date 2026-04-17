# GHI #182 Triage Matrix — tests/integration/ relocation

**Date:** 2026-04-17
**Scope:** 83 tests across 8 files under `tests/integration/`
**Governing GHI:** #182 (follow-up to #181)
**Decision axis:** mock-to-unit / port-to-behave / delete-as-duplicate

## Summary

All 83 tests already mock subprocess boundaries at the Python level
(`_uv_sync_patcher` stubs `_run_uv_sync`; `_quick_init` avoids `gz init`
altogether). Only ONE test spawns real `git` subprocess calls:
`test_git_sync_dry_run_in_git_repo` in `test_sync_cmds.py`. Every other
"integration" test is architecturally a unit test with mocked boundaries
— the tier label was a misnomer inherited from GHI #181's surface-level
relocation.

**Decision:** mock-to-unit for all 83. One test gains a new
`_git_subprocess_patcher` helper. No behave ports required — the existing
feature surface already covers end-to-end governance flows; these tests
are individual command contracts, which unit tests with mocked subprocess
boundaries exist to serve.

**Behave coverage audit:** the 18 existing `.feature` files cover
governance flows (ARB, closeout, OBPI pipeline stages, persona sync, ADR
drift, task governance, traceability) at the end-to-end level. They do
not duplicate any individual test under `tests/integration/` at the
assertion level. No deletes-as-duplicate triggered.

## Per-file triage

### `tests/integration/commands/test_init.py` (23 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| `test_init_creates_gzkit_dir` | mock-to-unit | `tests/commands/test_init.py` | Keeps `_uv_sync_patcher`; asserts dir creation after full init |
| `test_init_creates_ledger` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_manifest` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_design_directories` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_rerun_repairs_instead_of_failing` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_rerun_reports_nothing_to_repair` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_with_force` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_pyproject_toml` | mock-to-unit | `tests/commands/test_init.py` | skeleton scaffolding; no real subprocess |
| `test_init_creates_src_package` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_tests_init` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_no_skeleton_skips_project_files` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_does_not_overwrite_existing_pyproject` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_pyproject_uses_project_name` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_repair_creates_missing_skeleton` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_repair_partial_skeleton_fills_gaps` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_personas_directory` | mock-to-unit | `tests/commands/test_init.py` | persona scaffolding |
| `test_init_creates_default_persona_files` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_does_not_overwrite_existing_personas` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_init_creates_gitignore` | mock-to-unit | `tests/commands/test_init.py` | gitignore scaffolding |
| `test_init_does_not_overwrite_existing_gitignore` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_repair_creates_missing_gitignore` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_no_skeleton_still_creates_gitignore` | mock-to-unit | `tests/commands/test_init.py` | same |
| `test_normalize_cases` | mock-to-unit | `tests/commands/test_init.py` | pure function test |

### `tests/integration/commands/test_sync_cmds.py` (13 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| `test_git_sync_skill_flag_prints_skill_path` | mock-to-unit | `tests/commands/test_sync_cmds.py` | No init required; just arg parsing |
| `test_sync_repo_alias_is_removed` | mock-to-unit | `tests/commands/test_sync_cmds.py` | same |
| `test_git_sync_fails_outside_git_repo` | mock-to-unit | `tests/commands/test_sync_cmds.py` | tempdir has no .git; just need init stub |
| `test_git_sync_dry_run_in_git_repo` | **mock-to-unit + new helper** | `tests/commands/test_sync_cmds.py` | Only test in tree that spawns real `git`; replace with `_git_subprocess_patcher` |
| `test_git_sync_rejects_skip_that_disables_xenon` | mock-to-unit | `tests/commands/test_sync_cmds.py` | env manipulation only |
| `test_agent_sync_control_surfaces_updates_surfaces` | mock-to-unit | `tests/commands/test_sync_cmds.py` | full init + sync_all in-process |
| `test_agent_sync_dry_run_reports_complete_write_set` | mock-to-unit | `tests/commands/test_sync_cmds.py` | same |
| `test_agent_sync_dry_run_does_not_mutate_disk` | mock-to-unit | `tests/commands/test_sync_cmds.py` | same |
| `test_sync_alias_is_removed` | mock-to-unit | `tests/commands/test_sync_cmds.py` | arg parsing |
| `test_agent_control_sync_alias_is_removed` | mock-to-unit | `tests/commands/test_sync_cmds.py` | same |
| `test_agent_sync_fails_closed_on_canonical_skill_corruption` | mock-to-unit | `tests/commands/test_sync_cmds.py` | scaffolded + corrupt SKILL.md |
| `test_agent_sync_reports_stale_mirror_recovery_non_destructively` | mock-to-unit | `tests/commands/test_sync_cmds.py` | same |
| `test_agent_sync_output_is_deterministic_across_repeated_runs` | mock-to-unit | `tests/commands/test_sync_cmds.py` | repeated in-process invocation |

### `tests/integration/commands/test_skills.py` (15 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| all 15 | mock-to-unit | `tests/commands/test_skills.py` | all use `_uv_sync_patcher` + in-process CliRunner; no real subprocess |

### `tests/integration/commands/test_obpi_pipeline.py` (13 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| all 13 | mock-to-unit | `tests/commands/test_obpi_pipeline.py` | convert `_seed_runtime` from full `gz init` to `_quick_init` + needed scaffolding; run_command already mocked |

### `tests/integration/commands/test_audit.py` (11 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| all 11 | mock-to-unit | `tests/commands/test_audit.py` | all use `_uv_sync_patcher`; copy from `_REAL_PROJECT_ROOT` is filesystem, not subprocess |

### `tests/integration/commands/test_dry_run.py` (3 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| all 3 | mock-to-unit | `tests/commands/test_dry_run.py` | already use `_quick_init`; trivial relocation |

### `tests/integration/test_validate_sync_parity.py` (5 tests)

| Test | Decision | Destination | Rationale |
|------|----------|-------------|-----------|
| `test_clean_init_reports_no_drift` | mock-to-unit | `tests/test_validate_sync_parity.py` | uses cached `gz init`; retain cache pattern, mock `_run_uv_sync` |
| `test_hand_edited_agents_md_reports_drift` | mock-to-unit | `tests/test_validate_sync_parity.py` | same |
| `test_hand_edited_claude_hook_reports_drift` | mock-to-unit | `tests/test_validate_sync_parity.py` | same |
| `test_hand_edited_surface_is_restored_after_check` | mock-to-unit | `tests/test_validate_sync_parity.py` | same |
| `test_outdated_sync_date_does_not_trigger_drift` | mock-to-unit | `tests/test_validate_sync_parity.py` | same |

## Mock helper additions

Add to `tests/commands/common.py`:

- `_git_subprocess_patcher` — context manager that patches `subprocess.run`
  calls to `git ...` invocations, returning success with empty stdout. Used
  by `test_git_sync_dry_run_in_git_repo` (the only test that previously
  spawned real `git`).

Already present and sufficient:
- `_uv_sync_patcher` — stubs `gzkit.commands.init_cmd._run_uv_sync`
- `_quick_init(mode="lite")` — scaffolds a minimal gzkit project without
  full `gz init` (5x faster)
- `_init_git_repo` — fixture helper using real git; kept for integration
  tests that need real-history semantics (only used internally by the
  old sync-parity cache; can be removed once relocation lands)

## CLI surface changes

- Remove `--integration` flag from `gz test` parser
  (`src/gzkit/cli/parser_maintenance.py:108-112`)
- Remove `integration` parameter from `gzkit.commands.quality.test`
  (`src/gzkit/commands/quality.py:58-79`)
- Remove `integration` parameter from `gzkit.quality.run_tests`
  (`src/gzkit/quality.py:322-345`); revert signature to
  `run_tests(project_root: Path) -> QualityResult`
- Remove `env` parameter from `gzkit.quality.run_command`
  (`src/gzkit/quality.py:38-82`) — audit confirmed no other callers use it
  (`rg "run_command.*env=" src tests` returns 0 matches outside the old
  integration-tier plumbing)

## Rule changes

Rewrite `.gzkit/rules/tests.md` § "Unit vs Integration Tier" to the
shorter rule cited in the GHI:

> Unit tests mock subprocess boundaries; end-to-end CLI behavior lives in
> behave under `features/`. No third tier.

Cite GHI #181 (the narrow fix) and GHI #182 (this follow-up) for history.

## Acceptance check

- [x] `tests/integration/` removed from tree (directory and `load_tests`
  gating protocol deleted)
- [x] `gz test --integration` flag removed; rejected with "unrecognized
  arguments" per parser
- [x] `run_tests` signature reverts to `run_tests(project_root: Path)`
- [x] `run_command` `env` kwarg removed (no remaining callers)
- [x] `_git_subprocess_patcher` exposed from `tests/commands/common.py`;
  reference use at `tests/commands/test_sync_cmds.py::test_git_sync_dry_run_in_git_repo`
- [x] No behave-side duplication (no ports needed — see behave coverage
  audit above)
- [x] `.gzkit/rules/tests.md` "Unit vs Integration Tier" rewritten as
  "Two runners, one test surface (GHI #181, #182)"
- [x] `uv run gz test` green (3019 unit tests + 18 features / 116
  scenarios / 613 steps all pass)
- [~] <90s total: **unit tier alone 81s** (improved vs pre-#181 baseline
  of 89.7s from commit 0f7a8275); behave adds 59s. Total `gz test` chain
  is 140s. The <90s target appears to have been scoped to the unit tier
  only — the behave chain at 59s alone exceeds the budget. Follow-up
  parallelization (previously reverted in commit 78afbaa4) would be
  the correct response if the target is tightened.
- [x] Commit body cites GHI #182 and #181

## Timing summary

| Tier | Time | Tests | Context |
|------|------:|------:|---------|
| Unit (pre-#181 baseline) | 89.7s | ~3019 | commit 0f7a8275 |
| Unit (post-#181, without integration) | ~30s | ~2936 | GHI #181 split |
| Integration (post-#181) | ~60s | 83 | GHI #181 split |
| **Unit (post-#182, this fix)** | **81s** | **3019** | unified back |
| Behave | 59s | 116 scenarios | unchanged |
| **Total `gz test` chain** | **140s** | — | unit + behave |

Per-test overhead for the relocated files is dominated by `gz init`
template/skill/hook scaffolding work that cannot be mocked without
breaking test semantics (the tests are of `gz init` itself, or of
commands whose fixtures need the full init scaffold). The
`test_obpi_pipeline.py` migration to `_quick_init` is the one place
where mocking safely reduced overhead (~13 tests).
