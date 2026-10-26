# Census of code controls in place (contractor-kit R&D run)

**Date:** 2026-10-26. **A dated record.** It describes the tree at `604415755` (HEAD on that date)
and the working tree beside it. Counts and line numbers are measurements of that instance. They
are not authority.

**Scope.** Every *code* control: anything executable that gates, blocks, warns, validates,
monitors or enforces. The model-oriented surfaces (skills, rules, `AGENTS.md`, chore prose) belong
to the sibling census and are not counted here. Chore *scripts*, the executable part of a chore,
are counted.

**The MX signal, as code reads it today.** The signal is `.gzkit/mx.json`, read through
`src/gzkit/mx/marker.py`. There are two readings, and they disagree in scope:

- `checkpoint.hangar_demotes()` (`src/gzkit/mx/checkpoint.py:34-50`) is True while the marker
  file is **present** (`marker.is_active`, `marker.py:102-107`, presence only) and is not marked
  `exiting`. It is True for **both** `mode: mx` (hangar) and `mode: safe`. An unreadable marker also
  demotes (`checkpoint.py:49-50`). `checkpoint.resolve()` (`checkpoint.py:17-31`) then pins any
  `GATE5_INVARIANTS` name to CRITICAL and demotes every other non-CRITICAL level to
  `Route.ADVISORY`. `checkpoint.blocks()` (`:65-79`) is the yes/no form, and `demote_notice()`
  (`:82-93`) is the one wording for the announcement.
- `alarms.alarms_off()` (`src/gzkit/mx/alarms.py:24-27`) is True only for `mode: safe` and not
  `exiting`. The wrapper `python -m gzkit.mx.alarms <hook-id> -- <cmd>` (`alarms.py:30-39`) then
  **does not run the command at all** and exits 0.

Validity (the ledger binding, `marker.is_valid`, `marker.py:182`) is read by the lock reaper and
by preflight only. No checkpoint reading uses it.

**State observed on this date.** `.gzkit/mx.json` is present and **tracked in git**
(`git ls-files -- .gzkit/mx.json` prints it; `git check-ignore` exits 1). At HEAD it carries
`"mode": "safe"` and `"exiting": false` (`git show HEAD:.gzkit/mx.json`). So every checkpoint
reading below is live now, locally and in any CI checkout.

## Method

- **Read in full:** `src/gzkit/mx/checkpoint.py`, `alarms.py`, `invariants.py`, `levels.py`,
  `disposition.py`, `contract.py`; `src/gzkit/hooks/guards.py`; `.pre-commit-config.yaml`;
  `.claude/settings.json`; `.codex/hooks.json`; `src/gzkit/check_step_scopes.json`;
  `src/gzkit/canonical_steps.py`; `.claude/hooks/verifier-pipe-gate.py`; `.claude/hooks/README.md`;
  `.gzkit/hooks/pre-commit-complexity-advisor`.
- **Read in the relevant part:** `src/gzkit/commands/validate_cmd.py` (`_ScopeEntry`,
  `VALIDATOR_REGISTRY` :151-507, `_run_scope_checks` :923-958, `_dispatch_early_return_scopes`
  :1339-1474, the tail of `validate()`); `src/gzkit/commands/quality.py` (`_STEP_GUARD_META`,
  `_apply_mx_seam`, `_build_check_steps`, `_select_check_steps`, `_run_check_steps`, `check`);
  every `run_*` step runner in `src/gzkit/quality.py`; `src/gzkit/commands/mx_cmd.py` (enter, exit);
  `src/gzkit/mx/hardening.py`, `marker.py`; `src/gzkit/commands/obpi_complete.py` (the command body
  and gate calls); `obpi_lock.py`; the head, exit paths and MX lines of every script in
  `.claude/hooks/`; `src/gzkit/hooks/codex.py`, `commit_ledger.py`; the six workflows under
  `.github/workflows/`; `src/gzkit/guard_canary.py` (header and entrypoints);
  `src/gzkit/enforcement.py:740-840`.
- **Enumerated by executing the code**, not by reading it: `VALIDATOR_REGISTRY` (106 entries),
  `_build_check_steps()` (73 entries), `production_enforcement_registry()` (134 claims),
  `qc_binding._STEP_CLASSIFICATION` (73), `data/guard_canaries.json` (38),
  `data/guard_canary_grandfather.json` (96), `data/check_scope_membership.json` (66 in check, 40
  out). The tables for validators, steps and claims were generated from those objects with
  `inspect` for file:line.
- **Sampled:** CLI-internal refusals. `src/gzkit` has 301 `raise SystemExit(<non-zero>)` /
  `raise GzCliError` sites (grep count). Most are usage errors. The governance refusals listed
  below were found by reading `obpi_complete.py`, `obpi_lock.py`, `mx_cmd.py`, `closeout.py`,
  `patch_release.py`, `attest.py`, `obpi_stages.py`, `obpi_cmd.py`, `gates.py`, `sync_guard.py`,
  `adr_audit.py`, and by function names matching `def .*refus`. The list is not complete.
- **MX callers:** found by grep over `src`, `scripts`, `.claude/hooks`, `.gzkit` for
  `mx.checkpoint`, `from gzkit.mx`, `hangar_demotes`, `is_advisory(`, `checkpoint.(blocks|resolve|demote_notice)`,
  `marker.(is_active|read)`, `alarms_off`, `gzkit.mx.alarms`, `mx.json`. Every hit was opened.

**Role classification.** The role is the auditor's reading of each control's primary effect, by
this rule: **gate** when it sits on a lifecycle transition (OBPI completion, closeout, release,
mx exit, plan exit, stage advance) or audits lifecycle coherence; **safeguard** when it protects
the ledger, attestation, the GATE5 floor, attested canon, or the control system itself (a control
over other controls); **tripwire** for any other blocking check; **alarm** when it only announces
or warns; **monitor** when it only records or observes. *Other* is named where used.

**Known gaps.**

1. CLI refusals are sampled, as stated above.
2. Places of call for the 40 validator scopes outside `gz check` were found by searching for the
   flag string and the audit function name. A caller that builds the flag dynamically would be
   missed.
3. The failure exit code of each step was read from its runner and, for subprocess steps, from
   the command's own exit sites. A runner whose child exits 3 on some failures and 1 on others is
   marked by its common case.
4. No validator *body* was audited for internal fail-open paths. "Blocks" means the dispatcher
   blocks on its findings.
5. Tests and `features/` are not counted as controls. They are counted only as the *Test*,
   *Test (changed)* and *Behave* steps that run them.
6. The `.git/hooks/` shims were listed, not read beyond `post-commit.legacy`.

---

## 1. Git hooks

Dispatcher: the pre-commit framework, configured at `.pre-commit-config.yaml`.
`default_install_hook_types` is pre-commit, pre-push, prepare-commit-msg and post-commit (`:11`).
`fail_fast: true` is set (`:12`). The installed shims are in `.git/hooks/`: `pre-commit`,
`pre-push`, `prepare-commit-msg`, `post-commit`, `post-commit.legacy`.

### 1a. Hook ids in `.pre-commit-config.yaml` (18)

| # | hook id | stage | config line | runs | role | MX today | GATE5 floor | self-test / NC today |
|---|---|---|---|---|---|---|---|---|
| G1 | `task-trailer-stamp` | prepare-commit-msg | :21-26 | `.gzkit/hooks/prepare-commit-msg-task-trailers` | other: producer (stamps `Task:` trailers; every failure is a silent no-op, file docstring) | no read | no | none found |
| G2 | `ruff-check` | pre-commit | :27-38 | `uv run gz lint` (baseline-judged) | tripwire | no read; stays on in safe mode (comment :14-17) | no | none of its own; the `lint` claim and canary (step S1) target `gzkit.ruff_baseline:compare`, the comparator this hook also uses via `gz lint` |
| G3 | `ruff-format` | pre-commit | :40-46 | `uv run ruff format` (rewrites files) | other: fixer (the commit fails when files were rewritten) | no read | no | none |
| G4 | `ty-check` | pre-commit | :48-57 | `uv run ty check .` | tripwire | no read | no | scope pinned by `tests/arb/test_typecheck_scope_lockstep.py` (comment :50-52); `typecheck` claim is the step's |
| G5 | `forbid-pytest` | pre-commit | :59-66 | `uv run -m gzkit.hooks.guards` → `run_guards` (guards.py:569-589), **six guards** (table 1b) | dispatcher (see 1b) | each guard through `checkpoint.blocks` (guards.py:554-566); fails **closed** when the checkpoint cannot be imported (guards.py:565-566) | contains `ledger` and `gate5-attestation` | per guard (1b) |
| G6 | `complexity-ceiling` | pre-commit | :71-77 | `gzkit.mx.alarms complexity-ceiling -- gz validate --complexity-ceiling` | tripwire | alarm-wrapped: **not run** in safe mode; in mx mode the scope demotes inside `gz validate` (validate_cmd.py:940) | no | `complexity-ceiling` claim + canary |
| G7 | `surface-fidelity-cheap` | pre-commit | :79-84 | `gzkit.mx.alarms … -- gz validate --bullet-retention --surface-weight --pointer-anchors` | safeguard | alarm-wrapped; in mx mode the 3 scopes demote in `gz validate` | no | `surface-fidelity-bullet-retention`, `surface-fidelity-surface-weight`, 4 `pointer-*` claims |
| G8 | `validator-reachability-ratchet` | pre-commit | :86-91 | `gzkit.mx.alarms … -- python .gzkit/chores/control-surface-validator-reachability/check_reachability.py` | safeguard | alarm-wrapped; the script itself also calls `checkpoint.blocks`/`demote_notice` (check_reachability.py:483-495) | no | `validator-reachability` claim; script `--self-test` arm (run by step S60, not by this hook) |
| G9 | `ledger-vocabulary-inertness` | pre-commit | :93-98 | `gzkit.mx.alarms … -- python .gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py` | safeguard | alarm-wrapped; script calls the checkpoint (check_ledger_inertness.py:289-301) | no | `ledger-vocabulary-inertness` claim; script `--self-test` (run by step S61, not here) |
| G10 | `check-todos-fixmes` | pre-commit | :100-107 | `grep -r "TODO\|FIXME" … \|\| true` | alarm (always exits 0) | no read | no | none |
| G11 | `uv-lock` | pre-commit | :112-115 | astral-sh/uv-pre-commit rev 0.13.1 | other: fixer/tripwire (keeps `uv.lock` in step) | no read; stays on (comment :16-17) | no | none |
| G12 | `end-of-file-fixer` | pre-commit | :124-125 | pre-commit-hooks v5.0.0 | other: fixer | no read | no | none |
| G13 | `trailing-whitespace` | pre-commit | :126-127 | pre-commit-hooks v5.0.0 | other: fixer | no read | no | none |
| G14 | `check-merge-conflict` | pre-commit | :128 | pre-commit-hooks v5.0.0 | tripwire | no read | no | none |
| G15 | `gitleaks` | pre-commit | :132-137 | `gitleaks protect --staged --redact` | safeguard | no read; never routed through the checkpoint or the alarms wrapper (comment :16; alarms.py:12) | is the working scanner for floor member `secrets`, but `secrets` is **named-not-enforced** (invariants.py:57) and gitleaks is bound to no claim | none |
| G16 | `authorship` | pre-commit | :139-153 | `uv run gz validate --authorship` (not alarm-wrapped) | safeguard | reads the checkpoint inside `gz validate`; scope emitted CRITICAL (validate_cmd.py:213-215) → never demotes | enforces `operator-pii` by level; not a floor member by name (GHI #852) | `authorship-policy` claim (step S69) |
| G17 | `gz-check-pre-push` | pre-push | :155-172 | `gzkit.mx.alarms gz-check-pre-push -- gz check --reuse-verified` | dispatcher → `gz check` change scope (section 3) | alarm-wrapped: **in safe mode no `gz check` runs at push**; in mx mode `gz check` runs with its step seam demoting | no | none for the hook itself |
| G18 | `unittest` | manual | :179-209 | `gzkit.mx.alarms unittest -- unittest-parallel -t . -s tests --buffer` | tripwire (on demand only) | alarm-wrapped | no | entry pinned equal to `CANONICAL_STEP_COMMANDS["unittest"]` by `tests/arb/test_unittest_runner_lockstep.py` (comment :189-192) |

Not in the config, but installed: **`post-commit.legacy`** (G19), written by `gz init` and run by
the pre-commit post-commit shim before it stashes (comment `.pre-commit-config.yaml:4-10`). It
runs `uv run -m gzkit.hooks.commit_ledger`. It does two things, both **monitors**: it records
governance-artifact edits that the Claude `ledger-writer` hook did not see (GHI #847), and it
books an open safe-mode contract's amendment (`_book_contract_amendment`, commit_ledger.py:267-282
→ `mx/contract.py:112-121`, which reads `marker.read` and acts only when `mode == "safe"`).
Every exception is swallowed so a commit never breaks (commit_ledger.py:255-257, :277-279). No NC
was found.

Dormant alternative: **`.gzkit/hooks/pre-commit-complexity-advisor`** (G20) replaces G6 when
`python -m gzkit.hooks.install_complexity_advisor` is run (comment `.pre-commit-config.yaml:68-70`).
It runs `gz validate --complexity-ceiling` and, on failure, a timeout-wrapped advisor over the
staged files. It is not wired in the config on this date. It has no alarms wrapper.

### 1b. The six guards dispatched by `forbid-pytest` (`_GUARD_META`, guards.py:544-551)

| # | MX guard name | function | emitted level | role | behaviour under an open marker | GATE5 | NC today |
|---|---|---|---|---|---|---|---|
| G5.1 | `forbid-pytest` | `forbid_pytest` guards.py:137 | CRITICAL (operator ruling 2026-10-25, comment :537-538) | tripwire | pinned by level; never demotes | no | none found |
| G5.2 | `ledger` | `forbid_manual_ledger_edits` guards.py:199 | ERROR | safeguard | name is a floor member → pinned CRITICAL (checkpoint.py:27-28) | **yes** | `gate5-ledger` exercises `validate_ledger`, **not** this staged-diff guard (invariants.py:80-89) |
| G5.3 | `skill-sync-drift` | `forbid_skill_sync_drift` guards.py:317 | ERROR | tripwire | **demotes**, with `demote_notice` printed (guards.py:584-588) | no | none found |
| G5.4 | `post-authoring-src-commits` | `forbid_post_authoring_src_commits` guards.py:374 | CRITICAL (comment :532-536: kept to preserve behaviour, operator call open on GHI #843) | gate | pinned by level | no | none found |
| G5.5 | `gate5-attestation` | `forbid_unattested_obpi_completion_commits` guards.py:422 | ERROR | gate / safeguard | name is a floor member → pinned | **yes** | `gate5-attestation-absence` exercises `_requires_human_obpi_attestation` and `_validate_obpi_human_attestation_fields`, **not** this guard (invariants.py:109-134) |
| G5.6 | `enforcement-floor` | `_run_enforcement_floor` guards.py:496 → `quality.run_enforcement_floor_audit` (all 134 claims) | CRITICAL | safeguard | pinned by level | runs the GATE5 NCs | `enforcement-floor` claim |

`_run_enforcement_floor`'s docstring says *"as a pre-push guard"* (guards.py:497). Its hook runs
at `stages: [pre-commit]` (`.pre-commit-config.yaml:66`), so the 134-claim meta-validator runs on
every commit.

## 2. Claude Code and Codex hooks

### 2a. `.claude/settings.json` hook entries

There are 7 events, 11 matcher groups and **17 command entries**, which run 15 distinct scripts.
Two scripts live in `scripts/`. The rest are in `.claude/hooks/` and are generated by
`src/gzkit/hooks/claude.py` (`setup_claude_hooks`, :538-577) from `src/gzkit/hooks/scripts/*.py`.

| # | event / matcher | settings line | script | exit contract | role | MX today | GATE5 | NC today |
|---|---|---|---|---|---|---|---|---|
| H1 | SessionStart `*` | :56 | `scripts/session_orientation.py` | 0 always (degrades to "(no data)") | monitor (context injection) | yes: books hangar lease expiries and renders `mx_hardening_findings` in a conditional "MX hangar" section (session_orientation.py:62, :1143-1154) | no | none found |
| H2 | SessionStart `*` | :60 | `scripts/settings_local_backup.py` | 0 always | monitor (backs up `.claude/settings.local.json` outside the repo) | no | no | none |
| H3 | PreCompact `*` | :71 | `scripts/session_orientation.py` | as H1 | monitor | as H1 | no | none |
| H4 | PreToolUse `ExitPlanMode` | :82 | `.claude/hooks/plan-audit-gate.py` | 2 = block (plan-audit-gate.py:369) | gate | no read | no | none found |
| H5 | PreToolUse `Bash` | :91 | `.claude/hooks/verifier-pipe-gate.py` → `gzkit.verifier_pipe_gate.decide` | 2 = block (:47) | tripwire | **yes**: `alarms_off()` → exit 0 in safe mode (:31, :38-39); fail-open on ImportError (:33-36) | no | `verifier-exit-status-masked`, `verifier-escape-must-be-used` (verifier_pipe_gate.py:1017, :1033) |
| H6 | PreToolUse `Bash` | :95 | `.claude/hooks/pipeline-completion-reminder.py` | 0 always | alarm | no read | no | none |
| H7 | PreToolUse `Bash` | :99 | `.claude/hooks/ghi-triage-chat-silence.py` | 2 = block | tripwire | no read | no | none found |
| H8 | PreToolUse `Write\|Edit\|NotebookEdit` | :108 | `.claude/hooks/session-staleness-check.py` | 0 always (:122-123) | alarm | no read | no | none |
| H9 | PreToolUse `Write\|Edit\|NotebookEdit` | :112 | `.claude/hooks/pipeline-gate.py` (uses `gzkit.pipeline_stage_fence`) | 2 = block (:188, :194) | gate | **yes**: `checkpoint.is_advisory("pipeline-gate")` → prints `demote_notice` and exits 0 (:131-136); this works in hangar **and** safe mode | no | none found |
| H10 | PreToolUse `Write\|Edit\|NotebookEdit` | :116 | `.claude/hooks/obpi-completion-validator.py` (uses `gzkit.obpi_completion_fence.completion_blockers`, :324) | 2 = block (:275, :341, :354, :377) | gate | no read | its commit-time twin G5.5 is a floor member; this hook is not routed | none found |
| H11 | Stop `*` | :127 | `.claude/hooks/stop-turn-feedback.py` | 2 = block, at most once per turn | tripwire (lint over dirty files; claim-grounding of the last turn) | no read | no | none found |
| H12 | Stop `*` | :131 | `scripts/settings_local_backup.py` | 0 always | monitor | no | no | none |
| H13 | PostToolUse `ExitPlanMode` | :142 | `.claude/hooks/pipeline-router.py` | 0 always | other: router (emits a routing instruction) | no read | no | none |
| H14 | PostToolUse `Edit\|Write` | :151 | `.claude/hooks/post-edit-ruff.py` | 0 always | alarm | no read | no | none |
| H15 | PostToolUse `Edit\|Write` | :155 | `.claude/hooks/ledger-writer.py` → `gzkit.hooks.core.record_artifact_edit` | 0 | monitor | no read | no | none found |
| H16 | UserPromptSubmit `*` | :166 | `.claude/hooks/mx-awareness.py` → `gzkit.mx.awareness.get_banner` with a stdlib fallback reader | 0 always | alarm (injects the MX banner on every turn) | **yes**: reads the marker (:31, :70) | no | none found |
| H17 | SessionEnd `*` | :177 | `.claude/hooks/session-exit-bookmark.py` → `gzkit.session_exit.book_exit_bookmark` | 0 always | monitor | no read | no | none |

**On disk or generated, but not registered:**

- `.claude/hooks/ceremony-step-gate.py` (94 lines) is a PreToolUse Bash tripwire with exit 2 at :82.
  It is **not** in the generator's list (claude.py:558-572) and **not** registered in settings.json.
- `.claude/hooks/control-surface-sync.py` is generated (claude.py:572) and is a PostToolUse sync
  that always exits 0. It is **not** registered in settings.json.
- `session-start-advisement.py` is generated only where `scripts/session_orientation.py` is
  absent (claude.py:577). It is not on disk here. `.claude/hooks/README.md` still lists it.

### 2b. Claude permission controls (`.claude/settings.json:2-48`)

| # | control | lines | role | MX |
|---|---|---|---|---|
| H18 | 6 deny rules on git verification bypass (`--no-verify`, `commit -n`, `hooksPath`) | :4-9 | safeguard (protects the git-hook dispatcher) | none |
| H19 | 18 `Read(...)` deny rules on secrets/credentials | :10-27 | safeguard (secrets) | none |
| H20 | 18 `Edit(...)` deny rules on the same paths | :28-45 | safeguard | none |
| H21 | `disableBypassPermissionsMode: "disable"` | :47 | safeguard | none |

### 2c. `.codex/hooks.json` (2 entries)

| # | event / matcher | line | runs | role | MX | NC |
|---|---|---|---|---|---|---|
| H22 | SessionStart `startup\|resume\|clear\|compact` | :3-15 | `scripts/session_orientation.py` | monitor | as H1 | none |
| H23 | PreToolUse `Bash` | :17-28 | `python -m gzkit.hooks.codex` → `hook_output` → `verifier_pipe_gate.decide` (codex.py:114-137) → `permissionDecision: deny` | tripwire | **no read**: it has no `alarms_off()` check, unlike its Claude twin H5 | shares the verifier claims |

## 3. `gz check` steps

**Dispatcher.** `gz check` → `quality.check` (`src/gzkit/commands/quality.py:1323`) →
`_select_check_steps(scope)` (:819-833) → `_run_check_steps` (:942-1048). Every result passes
`_seam` (:934-939) → `_apply_mx_seam` (:166-202). The step list is `_build_check_steps()`
(:484-752, list at :667-752). The scope skip lists are in `src/gzkit/check_step_scopes.json`.

- `change` (the default, and what the pre-push hook runs) skips Behave, Preflight, Test, Docs build
  and Guard canary sweep, and adds **Test (changed)**. That is 69 steps.
- `full` runs all 73. CI's Linux leg runs it (`ci.yml:95-97`).
- `cross-platform` skips Guard canary sweep and Preflight. That is 71 steps. CI's Windows leg runs
  it (`ci.yml:107-109`).

**Seam behaviour (the MX reading for every step).** `_apply_mx_seam` demotes **only results with
`returncode == 3`** (quality.py:197-205). A `gz validate` subprocess that already demoted itself
exits 0 with the notice, and the seam marks it from the parsed notice (quality.py:149-163,
:198-199). Any other non-zero exit **passes through un-demoted**. `Authorship policy` and
`Enforcement floor` emit CRITICAL and never demote (`_STEP_GUARD_META`, quality.py:139, :144). A
step missing from `_STEP_GUARD_META` falls back to a kebab-case name at ERROR (quality.py:936-938).

Every one of the 73 listed steps is classified `bound` in `qc_binding._STEP_CLASSIFICATION`, so
each carries an `@enforces` negative control (the QC NC table). "+ canary" marks the 9 whose claim
also has a reviewed mutant in `data/guard_canaries.json`.

| # | step | list line | runner | wraps | role | change / full / cross-platform | seam guard name, level | demotable under marker? | GATE5 | NC claim / canary / built-in self-test |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | Lint | quality.py:668 | gzkit/quality.py:413 | ruff vs baseline + ADR path lint + parents lint | tripwire | ✓/✓/✓ | `lint`, ERROR | **no for exit≠3** (ruff/path lints rc 1 or 2); seam demotes only rc 3 | no | `lint` + canary |
| S2 | Format | quality.py:669 | gzkit/quality.py:521 | ruff format --check | tripwire | ✓/✓/✓ | `format`, ERROR | **no for exit≠3** (ruff format --check rc 1); seam demotes only rc 3 | no | `format` |
| S3 | Typecheck | quality.py:670 | gzkit/quality.py:564 | `uv run ty check .` | tripwire | ✓/✓/✓ | `typecheck`, ERROR | **no for exit≠3** (ty rc 1); seam demotes only rc 3 | no | `typecheck` |
| S4 | Module size | quality.py:671 | gzkit/quality.py:1957 | chore script module-sloc-cap-radon/check_module_size.py | tripwire | ✓/✓/✓ | `module-size`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `module-size`; `--self-test` arm runs first (quality.py:1981) |
| S5 | Tautological debt | quality.py:672 | gzkit/quality.py:1987 | chore script decommission-tautological-tests/check_debt_target.py | safeguard | ✓/✓/✓ | `tautological-debt`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `tautological-debt`; `--self-test` arm runs first (quality.py:2003) |
| S6 | Test | quality.py:673 | gzkit/quality.py:583 | unittest-parallel (CANONICAL_STEP_COMMANDS) | tripwire | –/✓/✓ | `test`, ERROR | **no for exit≠3** (unittest rc 1); seam demotes only rc 3 | no | `test` |
| S7 | Behave | quality.py:674 | gzkit/quality.py:631 | behave (sharded) | tripwire | –/✓/✓ | `behave`, ERROR | **no for exit≠3** (behave rc 1); seam demotes only rc 3 | no | `behave` |
| S8 | Guard canary sweep | quality.py:676 | gzkit/quality.py:2009 | guard_canary.sweep_main in a subprocess (quality.py:2019) | safeguard | –/✓/– | `guard-canary-sweep`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `guard-canary-sweep` + canary |
| S9 | Docs build | quality.py:677 | gzkit/quality.py:1022 | mkdocs build --strict + validation floor | tripwire | –/✓/✓ | `docs-build`, ERROR | **no for exit≠3** (mkdocs rc 1 (floor breach rc 3, quality.py:1067)); seam demotes only rc 3 | no | `docs-build` |
| S10 | Validate default scopes | quality.py:678 | gzkit/quality.py:1107 | bare `gz validate` (19 default-tier scopes) | safeguard | ✓/✓/✓ | `validate-default-scopes`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no (contains `ledger` scope, pinned inside the subprocess) | `validate-default-scopes` |
| S11 | Skill audit | quality.py:679 | gzkit/quality.py:1072 | `gz skill audit` | tripwire | ✓/✓/✓ | `skill-audit`, ERROR | **no for exit≠3** (skills_cmd.py:109,177 rc 1); seam demotes only rc 3 | no | `skill-audit` |
| S12 | Parity check | quality.py:680 | gzkit/quality.py:1077 | `gz parity check` | tripwire | ✓/✓/✓ | `parity-check`, ERROR | **no for exit≠3** (parity.py:128 rc 1); seam demotes only rc 3 | no | `parity-check` |
| S13 | Readiness audit | quality.py:681 | gzkit/quality.py:1082 | `gz readiness audit` | tripwire | ✓/✓/✓ | `readiness-audit`, ERROR | **no for exit≠3** (readiness.py:493,530 rc 1); seam demotes only rc 3 | no | `readiness-audit` |
| S14 | CLI audit | quality.py:682 | gzkit/quality.py:1087 | `gz cli audit` | tripwire | ✓/✓/✓ | `cli-audit`, ERROR | **no for exit≠3** (cli_audit.py:202,270 rc 1); seam demotes only rc 3 | no | `cli-audit` |
| S15 | Unscoped rules | quality.py:683 | gzkit/quality.py:1097 | `gz validate --unscoped-rules` | tripwire | ✓/✓/✓ | `unscoped-rules`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `unscoped-rules` |
| S16 | ADR status freshness | quality.py:684 | gzkit/quality.py:1123 | `gz validate --adr-status-fresh` | tripwire | ✓/✓/✓ | `adr-status-fresh`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `adr-status-freshness` |
| S17 | Advisory scorecard coverage | quality.py:685 | gzkit/quality.py:1149 | `gz validate --advisory-scorecard` | safeguard | ✓/✓/✓ | `advisory-scorecard`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `advisory-scorecard-coverage` |
| S18 | OBPI lifecycle coherence | quality.py:686 | gzkit/quality.py:1182 | `gz validate --obpi-lifecycle-coherence` | gate | ✓/✓/✓ | `obpi-lifecycle-coherence`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `obpi-lifecycle-coherence` |
| S19 | Adversarial validation | quality.py:687 | gzkit/quality.py:1193 | `gz validate --adversarial-validation` | safeguard | ✓/✓/✓ | `adversarial-validation`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `adversarial-validation` |
| S20 | RED parity | quality.py:688 | gzkit/quality.py:1206 | `gz validate --red-parity` | safeguard | ✓/✓/✓ | `red-parity`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `red-parity` |
| S21 | Producer field parity | quality.py:689 | gzkit/quality.py:1217 | `gz validate --producer-fields` | safeguard | ✓/✓/✓ | `producer-fields`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `producer-field-parity` |
| S22 | Rendition freshness | quality.py:690 | gzkit/quality.py:1229 | `gz validate --rendition-freshness` | safeguard | ✓/✓/✓ | `rendition-freshness`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `rendition-freshness` |
| S23 | Rendition floor coherence | quality.py:691 | gzkit/quality.py:1239 | `gz validate --rendition-floor-coherence` | safeguard | ✓/✓/✓ | `rendition-floor-coherence`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `rendition-floor-coherence` |
| S24 | Rendition lineage | quality.py:692 | gzkit/quality.py:1251 | `gz validate --rendition-lineage` | safeguard | ✓/✓/✓ | `rendition-lineage`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `rendition-lineage` |
| S25 | Invariant coherence | quality.py:693 | gzkit/quality.py:1349 | `gz validate --invariant-coherence` | safeguard | ✓/✓/✓ | `invariant-coherence`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `invariant-coherence` |
| S26 | Corpus retirement witness | quality.py:694 | gzkit/quality.py:1405 | `gz validate --corpus-retirement-witness` | safeguard | ✓/✓/✓ | `corpus-retirement-witness`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `corpus-retirement-witness` |
| S27 | Wheel path literals | quality.py:695 | gzkit/quality.py:1364 | `gz validate --wheel-path-literals` | tripwire | ✓/✓/✓ | `wheel-path-literals`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `wheel-path-literals` |
| S28 | Doc code citations | quality.py:696 | gzkit/quality.py:1382 | `gz validate --doc-code-citations` | tripwire | ✓/✓/✓ | `doc-code-citations`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `doc-code-citations` |
| S29 | Brief structure | quality.py:697 | gzkit/quality.py:1266 | `gz validate --brief-structure` | tripwire | ✓/✓/✓ | `brief-structure`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `brief-structure` |
| S30 | Brief size | quality.py:698 | gzkit/quality.py:1279 | `gz validate --brief-size` | tripwire | ✓/✓/✓ | `brief-size`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `brief-size` + canary |
| S31 | Requirements catalog | quality.py:699 | gzkit/quality.py:1338 | `gz validate --catalog` | tripwire | ✓/✓/✓ | `requirements-catalog`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `requirements-catalog` + canary |
| S32 | MX hardening | quality.py:700 | gzkit/quality.py:1292 | `gz validate --mx-hardening` | safeguard | ✓/✓/✓ | `mx-hardening`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `mx-hardening` + canary |
| S33 | Identity seam | quality.py:701 | gzkit/quality.py:1304 | `gz validate --id-seam` | tripwire | ✓/✓/✓ | `id-seam`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `identity-seam` + canary |
| S34 | Astral discipline | quality.py:702 | gzkit/quality.py:1316 | `gz validate --astral-discipline` | tripwire | ✓/✓/✓ | `astral-discipline`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `astral-discipline` + canary |
| S35 | Complexity ceiling | quality.py:703 | gzkit/quality.py:1327 | `gz validate --complexity-ceiling` | tripwire | ✓/✓/✓ | `complexity-ceiling`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `complexity-ceiling` + canary |
| S36 | Session green gate | quality.py:704 | gzkit/quality.py:1420 | `gz validate --session-green-gate` | gate | ✓/✓/✓ | `session-green-gate`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `session-green-gate` |
| S37 | Closeout proof | quality.py:705 | gzkit/quality.py:1430 | `gz validate --closeout-proof` | gate | ✓/✓/✓ | `closeout-proof`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `closeout-proof` |
| S38 | Kind invariance | quality.py:706 | gzkit/quality.py:1440 | `gz validate --kind-invariance` | tripwire | ✓/✓/✓ | `kind-invariance`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `kind-invariance` |
| S39 | Persona witness | quality.py:707 | gzkit/quality.py:1451 | `gz validate --persona-witness` | tripwire | ✓/✓/✓ | `persona-witness`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `persona-witness` |
| S40 | Interview transcripts | quality.py:708 | gzkit/quality.py:2180 | `gz validate --interviews` | tripwire | ✓/✓/✓ | `interviews`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `interview-transcripts` |
| S41 | Pool interview schema | quality.py:709 | gzkit/quality.py:1133 | `gz validate --pool-interview` | tripwire | ✓/✓/✓ | `pool-interview`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `pool-interview-schema` |
| S42 | Receipt shape | quality.py:710 | gzkit/quality.py:1464 | `gz validate --receipt-shape` | safeguard | ✓/✓/✓ | `receipt-shape`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `receipt-shape` |
| S43 | Orientation freshness | quality.py:711 | gzkit/quality.py:1571 | `gz validate --orientation-freshness` | tripwire | ✓/✓/✓ | `orientation-freshness`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `orientation-freshness` |
| S44 | Insights shape | quality.py:712 | gzkit/quality.py:1517 | `gz validate --insights-shape` | tripwire | ✓/✓/✓ | `insights-shape`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `insights-shape` |
| S45 | Instructions files budget | quality.py:713 | gzkit/quality.py:1528 | `gz validate --instructions-files-budget` | tripwire | ✓/✓/✓ | `instructions-files-budget`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `instructions-files-budget` |
| S46 | AGENTS.md map conformance | quality.py:714 | gzkit/quality.py:1538 | `gz validate --agents-md-map-conformance` | tripwire | ✓/✓/✓ | `agents-md-map-conformance`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `agents-md-map-conformance` |
| S47 | Complexity-doctrine links | quality.py:715 | gzkit/quality.py:1550 | `gz validate --complexity-doctrine-links` | tripwire | ✓/✓/✓ | `complexity-doctrine-links`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `complexity-doctrine-links` |
| S48 | Complexity-thresholds | quality.py:716 | gzkit/quality.py:1560 | `gz validate --complexity-thresholds` | tripwire | ✓/✓/✓ | `complexity-thresholds`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `complexity-thresholds` |
| S49 | REQ kind discipline | quality.py:717 | gzkit/quality.py:1476 | `gz validate --req-kind-discipline` | gate | ✓/✓/✓ | `req-kind-discipline`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `req-kind-discipline` |
| S50 | Status writer coverage | quality.py:718 | gzkit/quality.py:1489 | `gz validate --status-writer-coverage` | tripwire | ✓/✓/✓ | `status-writer-coverage`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `status-writer-coverage` |
| S51 | Transcribed ADR counts | quality.py:719 | gzkit/quality.py:1503 | `gz validate --transcribed-adr-counts` | tripwire | ✓/✓/✓ | `transcribed-adr-counts`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `transcribed-adr-counts` |
| S52 | tautological test audit | quality.py:720 | gzkit/quality.py:1584 | `gz validate --tautological-test-audit` | safeguard | ✓/✓/✓ | `tautological-test-audit`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `tautological-test-audit` |
| S53 | Task envelope coherence | quality.py:721 | gzkit/quality.py:1595 | `gz validate --task-envelope-coherence` | gate | ✓/✓/✓ | `task-envelope-coherence`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `task-envelope-coherence` |
| S54 | Lock-exchange coupling | quality.py:722 | gzkit/quality.py:1607 | `gz validate --lock-exchange-coupling` | gate | ✓/✓/✓ | `lock-exchange-coupling`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `lock-exchange-coupling` |
| S55 | QC binding | quality.py:723 | gzkit/quality.py:1618 | `gz validate --qc-binding` | safeguard | ✓/✓/✓ | `qc-binding`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `qc-binding` |
| S56 | Fidelity presence | quality.py:724 | gzkit/quality.py:1657 | `gz validate --fidelity-presence` | safeguard | ✓/✓/✓ | `fidelity-presence`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `fidelity-presence` |
| S57 | Waiver ratchet | quality.py:725 | gzkit/quality.py:1669 | `gz validate --waiver-ratchet` | safeguard | ✓/✓/✓ | `waiver-ratchet`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `waiver-ratchet` |
| S58 | Config registry | quality.py:726 | gzkit/quality.py:1681 | `gz validate --config-registry` | safeguard | ✓/✓/✓ | `config-registry`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `config-registry` |
| S59 | Gate callers | quality.py:727 | gzkit/quality.py:1694 | `gz validate --gate-callers` | safeguard | ✓/✓/✓ | `gate-callers`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `gate-callers` |
| S60 | Validator reachability | quality.py:732 | gzkit/quality.py:2087 | chore script control-surface-validator-reachability/check_reachability.py (projectLocal) | safeguard | ✓/✓/✓ (only where projectLocal ratchets installed, quality.py:735) | `validator-reachability`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `validator-reachability`; `--self-test` arm runs first (quality.py:2081) |
| S61 | Ledger vocabulary inertness | quality.py:733 | gzkit/quality.py:2099 | chore script ledger-vocabulary-inertness/check_ledger_inertness.py (projectLocal) | safeguard | ✓/✓/✓ (only where projectLocal ratchets installed, quality.py:735) | `ledger-vocabulary-inertness`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `ledger-vocabulary-inertness`; `--self-test` arm runs first (quality.py:2081) |
| S62 | Exemption controls | quality.py:738 | gzkit/quality.py:1707 | `gz validate --exemption-controls` | safeguard | ✓/✓/✓ | `exemption-controls`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `exemption-controls` |
| S63 | Gate enrollment | quality.py:739 | gzkit/quality.py:1722 | `gz validate --gate-enrollment` | safeguard | ✓/✓/✓ | `gate-enrollment`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `gate-enrollment` + canary |
| S64 | Population controls | quality.py:740 | gzkit/quality.py:1736 | `gz validate --population-controls` | safeguard | ✓/✓/✓ | `population-controls`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `population-controls` |
| S65 | Handoff documents | quality.py:741 | gzkit/quality.py:1822 | in-process audit | tripwire | ✓/✓/✓ | `handoff-documents`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `handoff-documents` |
| S66 | Preflight | quality.py:742 | gzkit/quality.py:2195 | `gz preflight` | tripwire (full tier only; janitorial scan; full tier only (check_step_scopes.json rationale)) | –/✓/– | `preflight`, ERROR | **no for exit≠3** (preflight.py:281 rc 1); seam demotes only rc 3 | no | `preflight` |
| S67 | Surface fidelity | quality.py:743 | gzkit/quality.py:1927 | `gz validate --surface-fidelity` | safeguard | ✓/✓/✓ | `surface-fidelity`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `surface-fidelity` |
| S68 | Line endings | quality.py:744 | gzkit/quality.py:1937 | `gz validate --line-endings` | tripwire | ✓/✓/✓ | `line-endings`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `line-endings` |
| S69 | Authorship policy | quality.py:745 | gzkit/quality.py:2110 | `gz validate --authorship` | safeguard | ✓/✓/✓ | `authorship`, CRITICAL | no (CRITICAL pin) | no | `authorship-policy` |
| S70 | Smoke tier | quality.py:746 | gzkit/quality.py:1947 | `gz smoke` | tripwire | ✓/✓/✓ | `smoke-tier`, ERROR | **no for exit≠3** (test failure rc non-3; budget breach rc 3 (smoke_cmd.py:19-71)); seam demotes only rc 3 | no | `smoke-tier` |
| S71 | Dispatch absorption marker | quality.py:747 | gzkit/quality.py:2125 | in-process marker check | safeguard | ✓/✓/✓ | `dispatch-absorption-marker`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `dispatch-absorption-marker` |
| S72 | Enforcement floor | quality.py:748 | gzkit/quality.py:1628 | enforcement.run_meta_validator (quality.py:1637), all 134 claims | safeguard | ✓/✓/✓ | `enforcement-floor`, CRITICAL | no (CRITICAL pin) | no (Enforcement floor runs the GATE5 NCs) | `enforcement-floor` |
| S73 | ADR taxonomy | quality.py:751 | gzkit/quality.py:1170 | `gz validate --taxonomy` | tripwire | ✓/✓/✓ | `taxonomy`, ERROR | yes: rc 3 → advisory at quality.py:197-205; a `gz validate` subprocess may demote itself first (notice parsed, quality.py:149) | no | `adr-taxonomy` |
| S74 | Test (changed) | quality.py:832 | gzkit/commands/quality.py:1281 | unittest-parallel over the tests the change touches | tripwire | ✓/–/– (replaces Test where Test is skipped) | fallback `test-(changed)`, ERROR (not in _STEP_GUARD_META) | **no for rc 1** | no | none (not in qc_binding._STEP_CLASSIFICATION) |

## 4. `gz validate` validators

**Dispatcher.** `gz validate` → `validate()` (`src/gzkit/commands/validate_cmd.py:1477`) has two
paths.

1. **`_dispatch_early_return_scopes`** (:1339-1474) runs first. It handles the umbrella `--audits`,
   `--attestation-receipts`, `--distribution --regenerate`, and the **11 solo scopes**. Each solo
   scope owns its 0/2/3 lifecycle and returns without passing the checkpoint.
2. **`_collect_errors`** (:116-136) → **`_run_scope_checks`** (:923-958) handles the other 95
   registry scopes. Each scope's findings are routed through `checkpoint.blocks(scope, level)`
   (:940). A demoted scope's findings go to stderr with `demote_notice` (:943-947). A name
   missing from the registry routes at CRITICAL (:939).

A bare `gz validate` runs all 19 default-tier scopes. That is the *Validate default scopes* step
(quality.py:1107-1120). Per `data/check_scope_membership.json`, 66 of the 106 scopes are reached
from `gz check` and 40 are not.

`--audits` (validate_audits.py:65-79) is a dispatcher. It runs `unscoped_rules` and `sensitivity`
solo, then `type_ignores`, `cli_alignment`, `event_handlers`, `validator_fields`,
`doc_surface_parity` and `orphaned_implementation` together (validate_audits.py:25-38). These
two non-registry entries are listed for completeness:

| # | entry | line | role | MX | NC |
|---|---|---|---|---|---|
| V107 | `--attestation-receipts <text>` → `_run_attestation_receipts_scope` | validate_cmd.py:1292, dispatched :1394-1402 | gate (receipt binding of attestation text) | early-return; no checkpoint | none found |
| V108 | `--audits` umbrella | validate_audits.py:65 | dispatcher (8 members) | members on the aggregate path pass the checkpoint; the 2 solo members do not | none |

`--distribution --regenerate` (:1377-1393) writes a baseline. It is not a control.

| # | scope (`gz validate --…`) | tier | registry line | role | places of call | MX today | GATE5 floor | self-test / NC today |
|---|---|---|---|---|---|---|---|---|
| V1 | `manifest` | default | validate_cmd.py:153 | tripwire | bare `gz validate` (all default tier); `gz validate --manifest`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V2 | `surfaces` | default | validate_cmd.py:158 | tripwire | bare `gz validate` (all default tier); `gz validate --surfaces`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V3 | `ledger` | default | validate_cmd.py:160 | safeguard | bare `gz validate` (all default tier); `gz validate --ledger`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); name is a GATE5 member → pinned CRITICAL, never demoted | yes (`ledger` by name) | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V4 | `instructions` | default | validate_cmd.py:165 | tripwire | bare `gz validate` (all default tier); `gz validate --instructions`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V5 | `briefs` | default | validate_cmd.py:166 | tripwire | bare `gz validate` (all default tier); `gz validate --briefs`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V6 | `documents` | default | validate_cmd.py:167 | tripwire | bare `gz validate` (all default tier); `gz validate --documents`; gz check step(s): *Validate default scopes*; src/gzkit/hooks/obpi.py:644 (subprocess) | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V7 | `personas` | default | validate_cmd.py:168 | tripwire | bare `gz validate` (all default tier); `gz validate --personas`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V8 | `frontmatter` | default | validate_cmd.py:170 | tripwire | bare `gz validate` (all default tier); `gz validate --frontmatter`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V9 | `version` | default | validate_cmd.py:175 | tripwire | bare `gz validate` (all default tier); `gz validate --version`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V10 | `taxonomy` | default | validate_cmd.py:176 | tripwire | bare `gz validate` (all default tier); `gz validate --taxonomy`; gz check step(s): *ADR taxonomy*, *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V11 | `invariant_coherence` | default | validate_cmd.py:178 | safeguard | bare `gz validate` (all default tier); `gz validate --invariant-coherence`; gz check step(s): *Invariant coherence*, *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V12 | `interviews` | explicit | validate_cmd.py:180 | tripwire | `gz validate --interviews`; gz check step(s): *Interview transcripts* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V13 | `decomposition` | explicit | validate_cmd.py:181 | tripwire | `gz validate --decomposition` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V14 | `requirements` | explicit | validate_cmd.py:182 | tripwire | `gz validate --requirements` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V15 | `commit_trailers` | default | validate_cmd.py:191 | safeguard | bare `gz validate` (all default tier); `gz validate --commit-trailers`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V16 | `type_ignores` | explicit | validate_cmd.py:196 | tripwire | `gz validate --type-ignores` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V17 | `cli_alignment` | explicit | validate_cmd.py:198 | tripwire | `gz validate --cli-alignment` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V18 | `event_handlers` | explicit | validate_cmd.py:207 | safeguard | `gz validate --event-handlers` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V19 | `event_schemas` | explicit | validate_cmd.py:208 | safeguard | `gz validate --event-schemas` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V20 | `producer_fields` | explicit | validate_cmd.py:209 | safeguard | `gz validate --producer-fields`; gz check step(s): *Producer field parity* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V21 | `validator_fields` | explicit | validate_cmd.py:211 | safeguard | `gz validate --validator-fields` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V22 | `authorship` | explicit | validate_cmd.py:214 | safeguard | `gz validate --authorship`; gz check step(s): *Authorship policy*; .pre-commit-config.yaml:150 (authorship) | checkpoint.blocks (validate_cmd.py:940); emitted CRITICAL → never demoted | no; enforces `operator-pii` by CRITICAL level (GHI #852), not a floor member | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V23 | `utf8_prefix` | explicit | validate_cmd.py:216 | tripwire | `gz validate --utf8-prefix` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V24 | `line_endings` | explicit | validate_cmd.py:217 | tripwire | `gz validate --line-endings`; gz check step(s): *Line endings* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V25 | `test_tiers` | explicit | validate_cmd.py:218 | tripwire | `gz validate --test-tiers` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V26 | `pydantic_models` | explicit | validate_cmd.py:219 | tripwire | `gz validate --pydantic-models` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V27 | `class_size` | explicit | validate_cmd.py:220 | tripwire | `gz validate --class-size` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V28 | `version_release` | explicit | validate_cmd.py:221 | gate | `gz validate --version-release` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V29 | `pool_adr_isolation` | explicit | validate_cmd.py:223 | tripwire | `gz validate --pool-adr-isolation` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V30 | `pool_interview` | explicit | validate_cmd.py:226 | tripwire | `gz validate --pool-interview`; gz check step(s): *Pool interview schema* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V31 | `behave_req_tags` | explicit | validate_cmd.py:228 | tripwire | `gz validate --behave-req-tags` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V32 | `skill_alignment` | explicit | validate_cmd.py:229 | tripwire | `gz validate --skill-alignment`; chore acceptance src/gzkit/chores/skill-authoring-quality/acceptance.json:11 | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V33 | `advisory_scorecard` | explicit | validate_cmd.py:231 | safeguard | `gz validate --advisory-scorecard`; gz check step(s): *Advisory scorecard coverage* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V34 | `complexity_doctrine_links` | explicit | validate_cmd.py:234 | tripwire | `gz validate --complexity-doctrine-links`; gz check step(s): *Complexity-doctrine links* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V35 | `complexity_thresholds` | explicit | validate_cmd.py:240 | tripwire | `gz validate --complexity-thresholds`; gz check step(s): *Complexity-thresholds* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V36 | `reconcile_freshness` | explicit | validate_cmd.py:246 | tripwire | `gz validate --reconcile-freshness` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V37 | `insights_shape` | explicit | validate_cmd.py:248 | tripwire | `gz validate --insights-shape`; gz check step(s): *Insights shape* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V38 | `instructions_files_budget` | explicit | validate_cmd.py:250 | alarm (declaration drift returns findings; the two delivery witnesses report to stderr only) | `gz validate --instructions-files-budget`; gz check step(s): *Instructions files budget* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting`; reads MX banner text only to measure its bytes (instructions_files_budget.py:170), not as a mode | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V39 | `agents_md_map_conformance` | explicit | validate_cmd.py:269 | tripwire | `gz validate --agents-md-map-conformance`; gz check step(s): *AGENTS.md map conformance* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V40 | `adr_status_fresh` | explicit | validate_cmd.py:275 | tripwire | `gz validate --adr-status-fresh`; gz check step(s): *ADR status freshness* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V41 | `obpi_lifecycle_coherence` | explicit | validate_cmd.py:278 | gate | `gz validate --obpi-lifecycle-coherence`; gz check step(s): *OBPI lifecycle coherence* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V42 | `adversarial_validation` | explicit | validate_cmd.py:284 | safeguard | `gz validate --adversarial-validation`; gz check step(s): *Adversarial validation* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V43 | `red_parity` | explicit | validate_cmd.py:289 | safeguard | `gz validate --red-parity`; gz check step(s): *RED parity* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V44 | `session_green_gate` | explicit | validate_cmd.py:291 | gate | `gz validate --session-green-gate`; gz check step(s): *Session green gate* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V45 | `orientation_freshness` | explicit | validate_cmd.py:297 | tripwire | `gz validate --orientation-freshness`; gz check step(s): *Orientation freshness* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V46 | `brief_headings` | explicit | validate_cmd.py:302 | tripwire | `gz validate --brief-headings` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V47 | `brief_cross_references` | explicit | validate_cmd.py:304 | tripwire | `gz validate --brief-cross-references` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V48 | `brief_demo_section` | explicit | validate_cmd.py:310 | tripwire | `gz validate --brief-demo-section` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V49 | `chores_layout` | explicit | validate_cmd.py:312 | tripwire | `gz validate --chores-layout` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V50 | `unscoped_rules` | explicit | validate_cmd.py:313 | tripwire | `gz validate --unscoped-rules`; gz check step(s): *Unscoped rules* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V51 | `rule_version_markers` | default | validate_cmd.py:315 | tripwire | bare `gz validate` (all default tier); `gz validate --rule-version-markers`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V52 | `invariant_witness` | default | validate_cmd.py:317 | safeguard | bare `gz validate` (all default tier); `gz validate --invariant-witness`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V53 | `sensitivity` | explicit | validate_cmd.py:318 | tripwire | `gz validate --sensitivity` | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; not reached from `gz check` | no | none found |
| V54 | `doc_surface_parity` | explicit | validate_cmd.py:320 | tripwire | `gz validate --doc-surface-parity` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V55 | `absorption_duplicates` | explicit | validate_cmd.py:323 | tripwire | `gz validate --absorption-duplicates` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V56 | `orphaned_implementation` | explicit | validate_cmd.py:329 | tripwire | `gz validate --orphaned-implementation` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V57 | `evaluation_justify_binding` | explicit | validate_cmd.py:335 | gate | `gz validate --evaluation-justify-binding` | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; not reached from `gz check` | no | evaluation-justify-binding, evaluation-justify-binding-qualified |
| V58 | `qc_binding` | explicit | validate_cmd.py:348 | safeguard | `gz validate --qc-binding`; gz check step(s): *QC binding* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V59 | `fidelity_presence` | explicit | validate_cmd.py:350 | safeguard | `gz validate --fidelity-presence`; gz check step(s): *Fidelity presence* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V60 | `waiver_ratchet` | explicit | validate_cmd.py:352 | safeguard | `gz validate --waiver-ratchet`; gz check step(s): *Waiver ratchet* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V61 | `config_registry` | explicit | validate_cmd.py:353 | safeguard | `gz validate --config-registry`; gz check step(s): *Config registry* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V62 | `gate_callers` | explicit | validate_cmd.py:354 | safeguard | `gz validate --gate-callers`; gz check step(s): *Gate callers* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V63 | `exemption_controls` | explicit | validate_cmd.py:356 | safeguard | `gz validate --exemption-controls`; gz check step(s): *Exemption controls* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V64 | `population_controls` | explicit | validate_cmd.py:359 | safeguard | `gz validate --population-controls`; gz check step(s): *Population controls* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V65 | `gate_enrollment` | explicit | validate_cmd.py:362 | safeguard | `gz validate --gate-enrollment`; gz check step(s): *Gate enrollment* | solo early-return scope: dispatched at validate_cmd.py:1339-1474, **bypasses** the checkpoint in `_run_scope_checks`; not demoted when invoked directly; under `gz check` its exit 3 is demoted at the step seam (quality.py:197) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V66 | `intrinsic_attestation` | explicit | validate_cmd.py:371 | gate | `gz validate --intrinsic-attestation` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V67 | `advisor_proof_binding` | explicit | validate_cmd.py:377 | gate | `gz validate --advisor-proof-binding` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V68 | `lock_exchange_coupling` | explicit | validate_cmd.py:383 | gate | `gz validate --lock-exchange-coupling`; gz check step(s): *Lock-exchange coupling* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V69 | `distribution` | explicit | validate_cmd.py:388 | safeguard | `gz validate --distribution` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V70 | `wheel_path_literals` | default | validate_cmd.py:390 | tripwire | bare `gz validate` (all default tier); `gz validate --wheel-path-literals`; gz check step(s): *Validate default scopes*, *Wheel path literals* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V71 | `changelog` | explicit | validate_cmd.py:395 | gate | `gz validate --changelog` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V72 | `bullet_retention` | explicit | validate_cmd.py:397 | safeguard | `gz validate --bullet-retention`; .pre-commit-config.yaml:81 (surface-fidelity-cheap) | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | surface-fidelity-bullet-retention |
| V73 | `surface_weight` | explicit | validate_cmd.py:399 | safeguard | `gz validate --surface-weight`; .pre-commit-config.yaml:81 (surface-fidelity-cheap) | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | surface-fidelity-surface-weight |
| V74 | `pointer_anchors` | explicit | validate_cmd.py:401 | safeguard | `gz validate --pointer-anchors`; .pre-commit-config.yaml:81 (surface-fidelity-cheap) | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | pointer-back-pointer-matched(+admitted), pointer-reverse-arm-orphan-refused(+live-lift-admitted) |
| V75 | `surface_fidelity` | explicit | validate_cmd.py:404 | safeguard | `gz validate --surface-fidelity`; gz check step(s): *Surface fidelity* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V76 | `vendor_manifest` | explicit | validate_cmd.py:407 | safeguard | `gz validate --vendor-manifest` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V77 | `setpoint_coherence` | explicit | validate_cmd.py:410 | safeguard | `gz validate --setpoint-coherence` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V78 | `rendition_freshness` | explicit | validate_cmd.py:413 | safeguard | `gz validate --rendition-freshness`; gz check step(s): *Rendition freshness* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting`; also resolves fail-closed vs warn inside the audit: rendition_freshness.py:131 | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V79 | `rendition_floor_coherence` | explicit | validate_cmd.py:416 | safeguard | `gz validate --rendition-floor-coherence`; gz check step(s): *Rendition floor coherence* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting`; also inside the audit: rendition_floor_coherence.py:76 | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V80 | `rendition_lineage` | explicit | validate_cmd.py:422 | safeguard | `gz validate --rendition-lineage`; gz check step(s): *Rendition lineage* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting`; also inside the audit: rendition_lineage.py:481 | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V81 | `corpus_retirement_witness` | default | validate_cmd.py:428 | safeguard | bare `gz validate` (all default tier); `gz validate --corpus-retirement-witness`; gz check step(s): *Corpus retirement witness*, *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V82 | `doc_code_citations` | default | validate_cmd.py:434 | tripwire | bare `gz validate` (all default tier); `gz validate --doc-code-citations`; gz check step(s): *Doc code citations*, *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V83 | `how_coverage` | default | validate_cmd.py:442 | tripwire | bare `gz validate` (all default tier); `gz validate --how-coverage`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V84 | `pending_renames` | default | validate_cmd.py:446 | tripwire | bare `gz validate` (all default tier); `gz validate --pending-renames`; gz check step(s): *Validate default scopes* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V85 | `kind_invariance` | explicit | validate_cmd.py:447 | tripwire | `gz validate --kind-invariance`; gz check step(s): *Kind invariance* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V86 | `persona_witness` | explicit | validate_cmd.py:448 | tripwire | `gz validate --persona-witness`; gz check step(s): *Persona witness* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V87 | `receipt_shape` | explicit | validate_cmd.py:449 | safeguard | `gz validate --receipt-shape`; gz check step(s): *Receipt shape* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V88 | `brief_reconcile` | explicit | validate_cmd.py:451 | gate | `gz validate --brief-reconcile` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V89 | `brief_structure` | explicit | validate_cmd.py:454 | tripwire | `gz validate --brief-structure`; gz check step(s): *Brief structure* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V90 | `brief_size` | explicit | validate_cmd.py:456 | tripwire | `gz validate --brief-size`; gz check step(s): *Brief size* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V91 | `catalog` | explicit | validate_cmd.py:457 | tripwire | `gz validate --catalog`; gz check step(s): *Requirements catalog* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V92 | `mx_hardening` | explicit | validate_cmd.py:458 | safeguard | `gz validate --mx-hardening`; gz check step(s): *MX hardening* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting`; reads the marker as its subject; its 3 guards route via checkpoint.resolve (mx/hardening.py:191,281,310) | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V93 | `id_seam` | explicit | validate_cmd.py:459 | tripwire | `gz validate --id-seam`; gz check step(s): *Identity seam* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V94 | `astral_discipline` | explicit | validate_cmd.py:461 | tripwire | `gz validate --astral-discipline`; gz check step(s): *Astral discipline* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V95 | `complexity_ceiling` | explicit | validate_cmd.py:464 | tripwire | `gz validate --complexity-ceiling`; gz check step(s): *Complexity ceiling*; .pre-commit-config.yaml:73 (complexity-ceiling); .gzkit/hooks/pre-commit-complexity-advisor:8 (auto-chain, when installed) | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V96 | `router_tables` | explicit | validate_cmd.py:466 | tripwire | `gz validate --router-tables`; chore acceptance .gzkit/chores/skill-trigger-testing/acceptance.json:5 | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V97 | `req_kind_discipline` | explicit | validate_cmd.py:468 | gate | `gz validate --req-kind-discipline`; gz check step(s): *REQ kind discipline* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V98 | `status_writer_coverage` | explicit | validate_cmd.py:471 | tripwire | `gz validate --status-writer-coverage`; gz check step(s): *Status writer coverage* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V99 | `transcribed_adr_counts` | explicit | validate_cmd.py:477 | tripwire | `gz validate --transcribed-adr-counts`; gz check step(s): *Transcribed ADR counts* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V100 | `ontology_purity` | explicit | validate_cmd.py:482 | tripwire | `gz validate --ontology-purity` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V101 | `brief_command_shape` | explicit | validate_cmd.py:484 | tripwire | `gz validate --brief-command-shape` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V102 | `tautological_test_audit` | explicit | validate_cmd.py:487 | safeguard | `gz validate --tautological-test-audit`; gz check step(s): *tautological test audit* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V103 | `task_envelope_coherence` | explicit | validate_cmd.py:493 | gate | `gz validate --task-envelope-coherence`; gz check step(s): *Task envelope coherence* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V104 | `closeout_proof` | explicit | validate_cmd.py:498 | gate | `gz validate --closeout-proof`; gz check step(s): *Closeout proof* | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | via step NC claim(s) (all 73 steps classified `bound`, qc_binding._STEP_CLASSIFICATION) |
| V105 | `okf_conformance` | explicit | validate_cmd.py:499 | tripwire | `gz validate --okf-conformance` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |
| V106 | `deprecated_verb_prescription` | explicit | validate_cmd.py:501 | tripwire | `gz validate --deprecated-verb-prescription` | checkpoint.blocks (validate_cmd.py:940); ERROR → demoted to advisory with notice to stderr while marker active (hangar or safe), unless marker `exiting` | no | none found |

## 5. Enforcement claims, the GATE5 floor, and guard canaries

### 5a. `@enforces` claims (134, `production_enforcement_registry()`, enforcement.py:793-801)

**Dispatcher.** `enforcement.run_meta_validator`, called from:

- the *Enforcement floor* step (quality.py:1637);
- the pre-commit guard G5.6 (guards.py:500, through `run_enforcement_floor_audit`);
- the `closeout_proof` audit (governance/trust_audits/closeout_proof.py:154);
- one NC entrypoint (governance/trust_audits/_qc_nc_entrypoints.py:1140).

Registration is `_ensure_production_claims_registered` (enforcement.py:661-790), which takes 18
sources. On the production path the floor's enrollment is enumerated by membership
(`_gate5_enrollment_results`, enforcement.py:804-840 → `mx/invariants.py:200-232`).

Each claim **is** a negative control: a fixture builds a violation and the production entrypoint
must catch it. The claims are the self-test layer for the controls they name. No claim and no part
of the runner reads the MX signal. The runner is reached at CRITICAL from both of its gate
callers, so it is never demoted.

By entrypoint module: `_qc_nc_entrypoints` 104; `pointer_integrity_claims` 4; `mx.invariants` 2;
`verifier_pipe_gate` 2; `acceptance_claims` 2; `obpi_precomplete_receipt_claims` 2;
`obpi_scope_gate_claims` 2; `validate_json_exit_claims` 2; `req_kind_support_claims` 2;
`tidy_claims` 2; `waiver_identity_claims` 2; `gate_population_claims` 2; `qc_binding`,
`mx.proxy_reality`, `airlock.enter`, `handoff_resume_gate`, `cli.helpers.exit_code_claims` and
`cli.helpers.log_level_claims` 1 each.

`exempts` declarations: 57 `none`, **55 UNDECLARED (`None`)**, and 22 that name an admitting
sibling claim.

| # | claim id | exempts | entrypoint (file:line) | role | canary |
|---|---|---|---|---|---|
| E1 | `lint` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:127 | safeguard (negative control) | yes |
| E2 | `format` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:133 | safeguard (negative control) | no (grandfathered) |
| E3 | `typecheck` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:137 | safeguard (negative control) | no (grandfathered) |
| E4 | `module-size` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:141 | safeguard (negative control) | no (grandfathered) |
| E5 | `tautological-debt` | tautological-debt-waived | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:168 | safeguard (negative control) | no (grandfathered) |
| E6 | `tautological-debt-waived` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:188 | safeguard (negative control) | no (grandfathered) |
| E7 | `test` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:282 | safeguard (negative control) | no (grandfathered) |
| E8 | `behave` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:334 | safeguard (negative control) | no (grandfathered) |
| E9 | `guard-canary-sweep` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:320 | safeguard (negative control) | yes |
| E10 | `docs-build` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:286 | safeguard (negative control) | no (grandfathered) |
| E11 | `docs-build-validation-floor` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:305 | safeguard (negative control) | no (grandfathered) |
| E12 | `skill-audit` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:351 | safeguard (negative control) | no (grandfathered) |
| E13 | `parity-check` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:360 | safeguard (negative control) | no (grandfathered) |
| E14 | `readiness-audit` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:369 | safeguard (negative control) | no (grandfathered) |
| E15 | `cli-audit` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:400 | safeguard (negative control) | no (grandfathered) |
| E16 | `unscoped-rules` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:421 | safeguard (negative control) | no (grandfathered) |
| E17 | `adr-status-freshness` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:509 | safeguard (negative control) | no (grandfathered) |
| E18 | `pool-interview-schema` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:515 | safeguard (negative control) | no (grandfathered) |
| E19 | `advisory-scorecard-coverage` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:523 | safeguard (negative control) | no (grandfathered) |
| E20 | `advisory-scorecard-summary-drift` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:523 | safeguard (negative control) | no (grandfathered) |
| E21 | `advisory-scorecard-ruff-reachability` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:523 | safeguard (negative control) | no (grandfathered) |
| E22 | `wheel-path-literals` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:454 | safeguard (negative control) | no (grandfathered) |
| E23 | `doc-code-citations` | doc-code-citations-exempted | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:427 | safeguard (negative control) | no (grandfathered) |
| E24 | `doc-code-citations-exempted` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:441 | safeguard (negative control) | no (grandfathered) |
| E25 | `validate-default-scopes` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:468 | safeguard (negative control) | no (grandfathered) |
| E26 | `status-writer-coverage` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:475 | safeguard (negative control) | no (grandfathered) |
| E27 | `transcribed-adr-counts` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:490 | safeguard (negative control) | no (grandfathered) |
| E28 | `obpi-lifecycle-coherence` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:538 | safeguard (negative control) | no (grandfathered) |
| E29 | `adr-taxonomy` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:529 | safeguard (negative control) | no (grandfathered) |
| E30 | `adversarial-validation` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:546 | safeguard (negative control) | no (grandfathered) |
| E31 | `red-parity` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:554 | safeguard (negative control) | no (grandfathered) |
| E32 | `producer-field-parity` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:560 | safeguard (negative control) | no (grandfathered) |
| E33 | `rendition-freshness` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:566 | safeguard (negative control) | no (grandfathered) |
| E34 | `rendition-floor-coherence` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:574 | safeguard (negative control) | no (grandfathered) |
| E35 | `rendition-lineage` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:582 | safeguard (negative control) | no (grandfathered) |
| E36 | `invariant-coherence` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:598 | safeguard (negative control) | no (grandfathered) |
| E37 | `corpus-retirement-witness` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:590 | safeguard (negative control) | no (grandfathered) |
| E38 | `brief-structure` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:762 | safeguard (negative control) | no (grandfathered) |
| E39 | `mx-hardening` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:747 | safeguard (negative control) | yes |
| E40 | `identity-seam` | identity-seam-baselined | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:730 | safeguard (negative control) | yes |
| E41 | `identity-seam-baselined` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:740 | safeguard (negative control) | yes |
| E42 | `complexity-ceiling` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:680 | safeguard (negative control) | yes |
| E43 | `astral-discipline` | astral-discipline-baselined | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:692 | safeguard (negative control) | yes |
| E44 | `astral-discipline-baselined` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:721 | safeguard (negative control) | yes |
| E45 | `astral-discipline-deferred-annotations` | astral-discipline-baselined | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:704 | safeguard (negative control) | yes |
| E46 | `brief-size` | brief-size-grandfathered | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:606 | safeguard (negative control) | yes |
| E47 | `requirements-catalog` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:629 | safeguard (negative control) | yes |
| E48 | `requirements-catalog-edges` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:651 | safeguard (negative control) | yes |
| E49 | `requirements-catalog-coverage` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:661 | safeguard (negative control) | yes |
| E50 | `requirements-catalog-forward-rule` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:675 | safeguard (negative control) | yes |
| E51 | `requirements-catalog-bdd` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:656 | safeguard (negative control) | yes |
| E52 | `brief-size-grandfathered` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:622 | safeguard (negative control) | yes |
| E53 | `session-green-gate` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:770 | safeguard (negative control) | no (grandfathered) |
| E54 | `session-green-gate-delivery` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:893 | safeguard (negative control) | no (grandfathered) |
| E55 | `closeout-proof` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:778 | safeguard (negative control) | no (grandfathered) |
| E56 | `kind-invariance` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:786 | safeguard (negative control) | no (grandfathered) |
| E57 | `persona-witness` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:792 | safeguard (negative control) | no (grandfathered) |
| E58 | `interview-transcripts` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:800 | safeguard (negative control) | no (grandfathered) |
| E59 | `receipt-shape` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:806 | safeguard (negative control) | no (grandfathered) |
| E60 | `orientation-freshness` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:812 | safeguard (negative control) | no (grandfathered) |
| E61 | `insights-shape` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:820 | safeguard (negative control) | no (grandfathered) |
| E62 | `instructions-files-budget` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:826 | safeguard (negative control) | no (grandfathered) |
| E63 | `agents-md-map-conformance` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:844 | safeguard (negative control) | no (grandfathered) |
| E64 | `complexity-doctrine-links` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:852 | safeguard (negative control) | no (grandfathered) |
| E65 | `complexity-thresholds` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:860 | safeguard (negative control) | no (grandfathered) |
| E66 | `req-kind-discipline` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:868 | safeguard (negative control) | no (grandfathered) |
| E67 | `tautological-test-audit` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:874 | safeguard (negative control) | no (grandfathered) |
| E68 | `git-fixture-isolation` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:880 | safeguard (negative control) | no (grandfathered) |
| E69 | `chore-suppression` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:887 | safeguard (negative control) | no (grandfathered) |
| E70 | `task-envelope-coherence` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:919 | safeguard (negative control) | no (grandfathered) |
| E71 | `lock-exchange-coupling` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:927 | safeguard (negative control) | no (grandfathered) |
| E72 | `handoff-documents` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:935 | safeguard (negative control) | no (grandfathered) |
| E73 | `preflight` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:409 | safeguard (negative control) | no (grandfathered) |
| E74 | `surface-fidelity` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:957 | safeguard (negative control) | no (grandfathered) |
| E75 | `line-endings` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:963 | safeguard (negative control) | no (grandfathered) |
| E76 | `authorship-policy` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:982 | safeguard (negative control) | no (grandfathered) |
| E77 | `smoke-tier` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:969 | safeguard (negative control) | no (grandfathered) |
| E78 | `dispatch-absorption-marker` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:988 | safeguard (negative control) | no (grandfathered) |
| E79 | `fidelity-presence` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:994 | safeguard (negative control) | no (grandfathered) |
| E80 | `waiver-ratchet` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1010 | safeguard (negative control) | no (grandfathered) |
| E81 | `config-registry` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1002 | safeguard (negative control) | no (grandfathered) |
| E82 | `gate-callers` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1121 | safeguard (negative control) | no (grandfathered) |
| E83 | `exemption-controls` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1016 | safeguard (negative control) | no (grandfathered) |
| E84 | `population-controls` | population-controls-disclosed | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1032 | safeguard (negative control) | no (grandfathered) |
| E85 | `population-controls-disclosed` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1048 | safeguard (negative control) | no (grandfathered) |
| E86 | `gate-enrollment` | gate-enrollment-disclosed | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1064 | safeguard (negative control) | yes |
| E87 | `gate-enrollment-disclosed` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1080 | safeguard (negative control) | yes |
| E88 | `evaluation-justify-binding` | evaluation-justify-binding-qualified | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1097 | safeguard (negative control) | no (grandfathered) |
| E89 | `evaluation-justify-binding-qualified` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1107 | safeguard (negative control) | no (grandfathered) |
| E90 | `enforcement-floor` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1132 | safeguard (negative control) | no (grandfathered) |
| E91 | `theater-signature-scan` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1144 | safeguard (negative control) | no (grandfathered) |
| E92 | `surface-fidelity-bullet-retention` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:957 | safeguard (negative control) | no (grandfathered) |
| E93 | `surface-fidelity-surface-weight` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:957 | safeguard (negative control) | no (grandfathered) |
| E94 | `task-envelope-subdivision` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:919 | safeguard (negative control) | no (grandfathered) |
| E95 | `task-envelope-layer-drift` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:919 | safeguard (negative control) | no (grandfathered) |
| E96 | `task-envelope-obpi-divergence` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:919 | safeguard (negative control) | no (grandfathered) |
| E97 | `waiver-ratchet-closed-set-lock` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1010 | safeguard (negative control) | no (grandfathered) |
| E98 | `waiver-ratchet-dated-cutover` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1010 | safeguard (negative control) | no (grandfathered) |
| E99 | `waiver-ratchet-silent-bypass` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:1010 | safeguard (negative control) | no (grandfathered) |
| E100 | `handoff-documents-populated-sections` | UNDECLARED (None) | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:941 | safeguard (negative control) | no (grandfathered) |
| E101 | `validator-reachability` | validator-reachability-disclosed | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:213 | safeguard (negative control) | no (grandfathered) |
| E102 | `validator-reachability-disclosed` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:234 | safeguard (negative control) | no (grandfathered) |
| E103 | `ledger-vocabulary-inertness` | ledger-vocabulary-inertness-disclosed | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:250 | safeguard (negative control) | no (grandfathered) |
| E104 | `ledger-vocabulary-inertness-disclosed` | none | gzkit/governance/trust_audits/_qc_nc_entrypoints.py:267 | safeguard (negative control) | no (grandfathered) |
| E105 | `qc-binding` | UNDECLARED (None) | gzkit/governance/trust_audits/qc_binding.py:198 | safeguard (negative control) | no (grandfathered) |
| E106 | `gate5-ledger` | none | gzkit/mx/invariants.py:80 | safeguard (GATE5 NC) | no (grandfathered) |
| E107 | `gate5-attestation-absence` | none | gzkit/mx/invariants.py:109 | safeguard (GATE5 NC) | no (grandfathered) |
| E108 | `grader-gaming` | none | gzkit/mx/proxy_reality.py:134 | safeguard (GATE5 NC) | no (grandfathered) |
| E109 | `airlock-in-unaccounted-seam` | UNDECLARED (None) | gzkit/airlock/enter.py:244 | safeguard (negative control) | no (grandfathered) |
| E110 | `handoff-resume-booking-coupling` | none | gzkit/handoff_resume_gate.py:239 | safeguard (negative control) | no (grandfathered) |
| E111 | `verifier-exit-status-masked` | verifier-escape-must-be-used | gzkit/verifier_pipe_gate.py:1017 | safeguard (negative control) | no (grandfathered) |
| E112 | `verifier-escape-must-be-used` | none | gzkit/verifier_pipe_gate.py:1033 | safeguard (negative control) | no (grandfathered) |
| E113 | `cli-usage-error-exit-two` | none | gzkit/cli/helpers/exit_code_claims.py:43 | safeguard (negative control) | no (grandfathered) |
| E114 | `cli-log-levels-follow-spec` | none | gzkit/cli/helpers/log_level_claims.py:64 | safeguard (negative control) | no (grandfathered) |
| E115 | `adversarial-refutation-loops` | adversarial-clean-verdict-admitted | gzkit/acceptance_claims.py:146 | safeguard (negative control) | yes |
| E116 | `adversarial-clean-verdict-admitted` | none | gzkit/acceptance_claims.py:160 | safeguard (negative control) | yes |
| E117 | `arb-receipt-red-run-refused` | arb-receipt-green-run-admitted | gzkit/commands/obpi_precomplete_receipt_claims.py:82 | safeguard (negative control) | yes |
| E118 | `arb-receipt-green-run-admitted` | none | gzkit/commands/obpi_precomplete_receipt_claims.py:98 | safeguard (negative control) | yes |
| E119 | `completion-scope-outside-allowed-paths` | completion-scope-records-admitted | gzkit/commands/obpi_scope_gate_claims.py:72 | safeguard (negative control) | yes |
| E120 | `completion-scope-records-admitted` | none | gzkit/commands/obpi_scope_gate_claims.py:93 | safeguard (negative control) | yes |
| E121 | `validate-json-exit-classified` | validate-json-exit-clean-passes | gzkit/commands/validate_json_exit_claims.py:113 | safeguard (negative control) | yes |
| E122 | `validate-json-exit-clean-passes` | none | gzkit/commands/validate_json_exit_claims.py:121 | safeguard (negative control) | yes |
| E123 | `support-citation-declared-only` | support-citation-declared-admitted | gzkit/req_kind_support_claims.py:92 | safeguard (negative control) | yes |
| E124 | `support-citation-declared-admitted` | none | gzkit/req_kind_support_claims.py:100 | safeguard (negative control) | yes |
| E125 | `pointer-back-pointer-matched` | pointer-back-pointer-matched-admitted | gzkit/governance/trust_audits/pointer_integrity_claims.py:94 | safeguard (negative control) | yes |
| E126 | `pointer-back-pointer-matched-admitted` | none | gzkit/governance/trust_audits/pointer_integrity_claims.py:113 | safeguard (negative control) | yes |
| E127 | `pointer-reverse-arm-orphan-refused` | pointer-reverse-arm-live-lift-admitted | gzkit/governance/trust_audits/pointer_integrity_claims.py:171 | safeguard (negative control) | yes |
| E128 | `pointer-reverse-arm-live-lift-admitted` | none | gzkit/governance/trust_audits/pointer_integrity_claims.py:190 | safeguard (negative control) | yes |
| E129 | `tidy-breach-exits-three` | tidy-clean-exits-zero | gzkit/commands/tidy_claims.py:146 | safeguard (negative control) | yes |
| E130 | `tidy-clean-exits-zero` | none | gzkit/commands/tidy_claims.py:154 | safeguard (negative control) | yes |
| E131 | `waiver-identity-new-entry-refused` | waiver-identity-reviewed-admitted | gzkit/governance/trust_audits/waiver_identity_claims.py:160 | safeguard (negative control) | yes |
| E132 | `waiver-identity-reviewed-admitted` | none | gzkit/governance/trust_audits/waiver_identity_claims.py:172 | safeguard (negative control) | yes |
| E133 | `gate-population-enrollment` | gate-population-disclosed | gzkit/governance/trust_audits/gate_population_claims.py:92 | safeguard (negative control) | yes |
| E134 | `gate-population-disclosed` | none | gzkit/governance/trust_audits/gate_population_claims.py:106 | safeguard (negative control) | yes |

### 5b. `GATE5_INVARIANTS` (`src/gzkit/mx/invariants.py:26-34`), 5 members

| member | where it is enforced in code | how it holds under an open marker | live NC |
|---|---|---|---|
| `gate5-attestation` | pre-commit guard G5.5 (guards.py:549); `gz obpi complete` attestation-text refusal (obpi_complete.py:1283-1291) and the field validator `_validate_obpi_human_attestation_fields` (adr_audit.py:899) | pinned CRITICAL by name in `checkpoint.resolve` (checkpoint.py:27-28) wherever it is routed. `gz obpi complete` reads no marker at all | `gate5-attestation-absence` (invariants.py:109) |
| `secrets` | none bound. `gitleaks` (G15) scans, outside the checkpoint | n/a (gitleaks never reads the marker) | **none**: named-not-enforced (`_GATE5_NAMED_NOT_ENFORCED`, invariants.py:57) |
| `operator-pii` | none bound by name. The narrower `authorship` check is pinned CRITICAL by level (validate_cmd.py:213-215; quality.py:139) | `authorship` never demotes | **none** by name: named-not-enforced (invariants.py:57). `authorship-policy` covers the proxy |
| `ledger` | `validate --ledger` scope (validate_cmd.py:160); pre-commit guard G5.2 (guards.py:546) | pinned by name | `gate5-ledger` (invariants.py:80), which exercises `validate_ledger` |
| `grader-gaming` | `mx/proxy_reality.scan` (proxy_reality.py:66). **No production caller** outside its own NC (grep of `src/`) | n/a | `grader-gaming` (proxy_reality.py:134) |

### 5c. Guard canaries (`src/gzkit/guard_canary.py`; registry `data/guard_canaries.json`)

- 38 canaries. Each binds one reviewed mutant to one claim. All 38 are `reviewed_by: g0`.
- The other **96 claims** are disclosed on `data/guard_canary_grandfather.json`, and 38 + 96 = 134.
- **Kill** (live, on a copy of the tree): `sweep_main` (guard_canary.py:420). The only dispatcher
  is the *Guard canary sweep* step (quality.py:2009-2020). The `change` and `cross-platform`
  scopes skip it, so it runs under `full` only (CI Linux).
- **Binding** (static hash check): `check_canaries` (guard_canary.py:229). Its only caller is the
  unit test module `tests/governance/test_guard_canaries.py`. The `full` scope runs it through
  *Test*; the `change` scope runs it only when *Test (changed)* selects it.
- **Review recording:** `gz canary` (src/gzkit/commands/canary.py:6 imports `record_review`).
- No part reads the MX signal.

Claims with a canary: `arb-receipt-red-run-refused`, `arb-receipt-green-run-admitted`,
`adversarial-refutation-loops`, `adversarial-clean-verdict-admitted`,
`validate-json-exit-classified`, `validate-json-exit-clean-passes`,
`support-citation-declared-only`, `support-citation-declared-admitted`, the four `pointer-*`
claims, `tidy-breach-exits-three`, `tidy-clean-exits-zero`, `waiver-identity-new-entry-refused`,
`waiver-identity-reviewed-admitted`, `gate-population-enrollment`, `gate-population-disclosed`,
`gate-enrollment`, `gate-enrollment-disclosed`, `completion-scope-outside-allowed-paths`,
`completion-scope-records-admitted`, `guard-canary-sweep`, `brief-size`,
`brief-size-grandfathered`, `mx-hardening`, `identity-seam`, `identity-seam-baselined`,
`astral-discipline`, `astral-discipline-baselined`, `astral-discipline-deferred-annotations`,
`complexity-ceiling`, `requirements-catalog`, `requirements-catalog-edges`,
`requirements-catalog-coverage`, `requirements-catalog-bdd`, `requirements-catalog-forward-rule`,
`lint`.

## 6. CI workflows (`.github/workflows/`, 6 files)

No workflow reads `.gzkit/mx.json` explicitly (grep for `mx`/`safe` in the workflows: no hits).
The marker is tracked in git, though, so every `gz check` run in CI reads it through the
checkpoint.

| # | workflow / job / step | trigger | lines | runs | role | MX today | self-test |
|---|---|---|---|---|---|---|---|
| CI1 | `ci.yml` `check` (ubuntu) | push to main (paths-ignore: handoffs, insights, ledger), pull_request | ci.yml:9-24, :95-97 | `uv run gz check --full` (73 steps) | tripwire | indirect: the tracked marker (`mode: safe` at HEAD) demotes every rc-3 non-CRITICAL step | per step (section 3) |
| CI2 | `ci.yml` `check` (windows) | same | ci.yml:107-109 | `uv run gz check --cross-platform` (71 steps) | tripwire | indirect, as CI1 | per step |
| CI3 | `docs.yml` `build` + `deploy-vps` verify | release, workflow_dispatch | docs.yml:39-40, :103-108 | `mkdocs build --strict`; compare served `build-info.json` | tripwire | none | none |
| CI4 | `docs-freshness.yml` `check` | daily cron `17 6 * * *` | docs-freshness.yml:5-31 | served tag vs latest release; `::error` + exit 1 | alarm | none | none |
| CI5 | `queue-hygiene.yml` | monthly cron `0 7 1 * *` | queue-hygiene.yml:12-41 | `gz chores advise ghi-cross-reference-staleness` | monitor | none | the chore script has a `--self-test` arm |
| CI6 | `release.yml` `release` "Decide what this tag still needs" | tag push, dispatch | release.yml:132-175 | refuses to touch a release whose tag is not main's declared version | safeguard | none | none |
| CI7 | `release.yml` `dist` | tag push, dispatch | release.yml:223-233, :249-251 | tag must equal `uv version`; smoke-test the wheel and sdist with `gz --help` | tripwire | none | none |
| CI8 | `unit-tier-profile.yml` | push to main on paths; dispatch | unit-tier-profile.yml:16-65 | profile the unit tier and upload the record | monitor | none | none |

## 7. CLI-internal fail-closed checks (sampled)

| # | command / site | file:line | refuses when | role | MX today |
|---|---|---|---|---|---|
| C1 | `gz obpi complete` resolve/validate | obpi_complete.py:868-964 (called :1098): already Completed :893; status-write refusal :903-909 (`frontmatter_coherence.obpi_status_write_refusal`, frontmatter_coherence.py:221); not in ledger | brief/ledger state wrong | gate | no |
| C2 | `gz obpi complete` reconcile-receipt gate | obpi_complete.py:771 (called :1104) | Stage-5 reconcile receipt absent/stale | gate | no |
| C3 | `gz obpi complete` scope gate | obpi_complete.py:1000 (called :1120) | changed files outside Allowed Paths (GHI #1181) | gate | no |
| C4 | `gz obpi complete` would-be content | obpi_complete.py:1143-1151 (`_validate_would_be_content` :1915 → `obpi_completion_fence.completion_blockers`) | brief content invalid | gate | no |
| C5 | `gz obpi complete` security review gate | obpi_complete.py:183 (called :1158) | `sensitivity: security` without its receipt/checklist | gate / safeguard | no |
| C6 | `gz obpi complete` attestation receipt gate | obpi_complete.py:329 (called :1205) | heavy/foundation receipts missing (ADR-0.0.24) | gate | no |
| C7 | `gz obpi complete` REQ-coverage gate | obpi_complete.py:607 (called :1242); waiver pairing :1218-1235; `_reject_behavior_waivers` :508 | BEHAVIOR REQ uncovered | gate | no |
| C8 | `gz obpi complete` task-envelope gate | obpi_complete.py:1015 (called :1263) | Signature-(b) divergence (GHI #590) | gate | no |
| C9 | `gz obpi complete` human attestation text | obpi_complete.py:1282-1291 | empty `--attestation-text` | gate (GATE5 `gate5-attestation`) | no |
| C10 | `gz obpi complete` adversarial closure | obpi_complete.py:1038 (called :1367) | unresolved adversary findings (GHI #676) | gate | no |
| C11 | `gz obpi precomplete` | obpi_precomplete.py:217-830 (13 `_check_*`, e.g. lock held :414, ARB receipts :491, plan-audit receipt :538, operator block :744) | any check fails | gate | no |
| C12 | `gz obpi lock claim` | obpi_lock.py:66-91 (exit 1) | another agent holds the lock, expired included | safeguard | no |
| C13 | `gz obpi lock release` | obpi_lock.py:240-264 (exit 3) | no exchange record | safeguard | no |
| C14 | `gz obpi withdraw` / `block` / `supersede` | obpi_cmd.py:114-120, :189, :244-249 | empty attestor / reason / next action | gate | no |
| C15 | `gz obpi repudiate` | obpi_cmd.py:338-345 | empty attestor or reason | gate | no |
| C16 | `gz obpi pipeline` stage advance | obpi_stages.py:270-273, :344-353 (exit 3) → `acceptance_store.acceptance_blockers` :448 | acceptance blockers at stage 2/review | gate | no |
| C17 | `gz task` transitions | task.py:504-536 and others | invalid REQ id or transition | gate | no |
| C18 | `gz attest` | attest.py:58-80 (incomplete OBPIs unless `--force`), :97-128 inputs | ADR has incomplete OBPIs | gate | no |
| C19 | `gz closeout` hangar refusal | closeout.py:679-682 (exit 3) → `mx/hardening.normal_release_blocked` | marker present | gate | **yes**: emits CRITICAL when `marker.is_active` (hardening.py:215-216) |
| C20 | `gz closeout` attestation selection | closeout.py:225-249 | partial/dropped without a reason | gate | no |
| C21 | `gz closeout --ceremony` | closeout_ceremony.py:190 and :432-516 | readiness blockers; ceremony state | gate | no |
| C22 | `gz patch release` hangar refusal | patch_release.py:1006-1009 (exit 3) | marker present | gate | **yes** (as C19) |
| C23 | `gz implement` / Gate 2 | gates.py:357-365 | test command fails | gate | no |
| C24 | `gz adr audit-check` / `covers-check` | adr_audit.py:306-387, :392-438 | audit or covers check fails | gate | no |
| C25 | `gz mx enter` | mx_cmd.py:280-322 | empty reason/attestor; bad mode; marker already present; session lock held | safeguard | yes (it writes the signal) |
| C26 | `gz mx exit` | mx_cmd.py:400-433 (exit 3); runner `_default_run_guards` :378-381 | any guard red in the re-run | gate | yes: marks the marker `exiting`, so nothing demotes. The re-run is **`uv run gz check`, the `change` scope** (:380) |
| C27 | sync preflight | sync_guard.py:20-29 | canonical skills state corrupt | tripwire | no |
| C28 | `gz git-sync` | sync.py:774-862 | not a repo/branch; gate failure | gate | no |
| C29 | content landing/ownership/composer | content/landing.py:376, :948, :991; content/ownership.py:241-2330 (12 `_refuse_*`); content/composer.py:113, :297, :359, :406, :439 | corpus/canon integrity breaches | safeguard | no |
| C30 | `gz airlock in/out`, `gz permitted-entry` | airlock.py:11 (downgraded from exit 3 to warning), :91, :161; `airlock/enter.build_refusal` :195 | usage only (diagnostic otherwise) | alarm | no |
| C31 | lock reaper | lock_manager.py:355-395 | n/a (reaps expired locks) | monitor / safeguard | **yes**: leaves the hangar session lock while `marker.is_valid` (:383) |
| C32 | preflight session-lock classification | preflight.py:170 | n/a | monitor | **yes** (`mx_marker.is_valid`) |
| C33 | slug rename | governance/obpi_slug_rename.py:70 | rename refusals | safeguard | no |
| C34 | acceptance approval | acceptance_grounds.py:118 `refuse_uncited_approval`; acceptance_store.py:163 | uncited approval / inadequate replay | gate | no |
| C35 | adversary workspace | adversary_workspace.py:104 | git step failure | other | no |
| C36 | pipeline position rebuild | pipeline_position.py:748 | rebuild refusal | gate | no |
| C37 | pipeline stage fence (shared logic) | pipeline_stage_fence.py:75, :87 (used by H9 and G5.4) | production write/commit past Stage 2 | gate | via its callers only (H9 demotes; G5.4 pinned) |

### 7a. MX-internal guards (`src/gzkit/mx/hardening.py`)

| # | guard name | line | emitted | role | MX | dispatched by |
|---|---|---|---|---|---|---|
| M1 | `mx-ttl-max-open` | hardening.py:161-203 | CRITICAL/WARNING/INFO | alarm | `checkpoint.resolve` :191 | `mx_hardening_findings` (validator `mx_hardening`, step *MX hardening*, orientation H1) |
| M2 | `mx-normal-release` | hardening.py:206-221 | CRITICAL if marker present, else INFO | gate | :215-216 | C19, C22 |
| M3 | `mx-debt-aging` | hardening.py:263-294 | WARNING/NOTICE/INFO | alarm | :281 | as M1 |
| M4 | `mx-dangling-state` | hardening.py:296-317 | ERROR if sessions open and no marker | safeguard | :306-310 | as M1 |

## 8. Chore scripts (executable parts of chores; 8 scripts in `.gzkit/chores/`)

The chore runner (`gz chores advise|execute`, src/gzkit/commands/chores.py) runs each chore's
`acceptance.json` criteria. Places of call beyond the runner are noted.

| # | script | other places of call | exit on breach | role | MX | built-in self-test |
|---|---|---|---|---|---|---|
| K1 | module-sloc-cap-radon/check_module_size.py | step S4 | 3 (:229, :255) | tripwire | no | yes `--self-test` |
| K2 | decommission-tautological-tests/check_debt_target.py | step S5 | 3 (:110, :153) | tripwire | no | yes |
| K3 | control-surface-validator-reachability/check_reachability.py | step S60, hook G8 | 3 | safeguard | **yes** (checkpoint :483-495) | yes |
| K4 | ledger-vocabulary-inertness/check_ledger_inertness.py | step S61, hook G9 | 3 (:166, :209) | safeguard | **yes** (:289-301) | yes |
| K5 | ghi-cross-reference-staleness/check_cross_reference_staleness.py | CI5 | 1 (:155) | alarm | no | yes |
| K6 | control-surface-rule-conflicts/check_evidence.py | chore acceptance only | 3 (:448, :453) | safeguard | no | yes |
| K7 | memory-hygiene/check_memory_drift.py | chore acceptance only | 1 (:67, :85) | alarm | no | no |
| K8 | pythonic-design-pattern-detection/scan.py | chore acceptance only | 1/2 (:919, :946) | monitor | no | yes |

## 9. Every caller of the MX signal (`gzkit.mx.checkpoint`, `hangar_demotes`, `marker`, `alarms`)

| caller | file:line | what it reads | effect |
|---|---|---|---|
| pre-commit guards | src/gzkit/hooks/guards.py:562-564, :586-588 | `checkpoint.blocks`, `demote_notice` | demote G5.3; pin the other five |
| `gz validate` aggregate path | src/gzkit/commands/validate_cmd.py:931-947 | `checkpoint.blocks`, `demote_notice` | demote 93 scopes; pin `ledger`, `authorship` |
| `gz check` seam | src/gzkit/commands/quality.py:186-202 (+ :1470 for rendering) | `checkpoint.resolve`, `demote_notice`, `disposition.grounds` | demote rc-3 steps |
| alarms wrapper | src/gzkit/mx/alarms.py:24-39 | `marker.is_active`, `marker.read` (mode safe) | skip 6 hooks (G6-G9, G17, G18) |
| Claude verifier-pipe gate | .claude/hooks/verifier-pipe-gate.py:31-39 (generator src/gzkit/hooks/scripts/quality.py:54-61) | `alarms_off` | allow everything in safe mode |
| Claude pipeline gate | .claude/hooks/pipeline-gate.py:131-136 (generator src/gzkit/hooks/scripts/routing.py:218-224) | `checkpoint.is_advisory` | allow with notice in hangar or safe mode |
| Claude MX awareness | .claude/hooks/mx-awareness.py:31, :70 (generator src/gzkit/hooks/scripts/mx.py:52, :91) | marker / `awareness.get_banner` | banner injection |
| session orientation | scripts/session_orientation.py:1143-1154 | `mx.lease.book_lease_expiries`, `mx_hardening_findings` | books expiries; renders findings |
| rendition audits | governance/trust_audits/rendition_freshness.py:131, rendition_floor_coherence.py:76, rendition_lineage.py:481 | `checkpoint.resolve` | fail-closed vs warn-only inside the audit |
| MX hardening | src/gzkit/mx/hardening.py:191, :215-216, :281, :306-310; governance/trust_audits/mx_hardening.py | `checkpoint.resolve`, `marker.is_active` | M1-M4 |
| release funnels | src/gzkit/commands/closeout.py:679; patch_release.py:1006 | `hardening.normal_release_blocked` | refuse a release while the marker is present |
| `gz mx` | src/gzkit/commands/mx_cmd.py:296, :406-417, :483 | `marker.is_active/read/write` | enter/exit/renew |
| lock reaper | src/gzkit/lock_manager.py:368-383 | `marker.SESSION_LOCK_KEY`, `marker.is_valid` | spare the hangar lock |
| preflight | src/gzkit/commands/preflight.py:170 | `marker.is_valid` | classify the session lock |
| contract booking | src/gzkit/hooks/commit_ledger.py:273 → src/gzkit/mx/contract.py:76, :114 | `marker.read`, `is_valid` | book `mx_contract_amended` |
| ledger producer probe | src/gzkit/ledger_producer_probe.py:215-224 | `marker.is_valid` on a disposable root | probe only |
| instructions-files budget | governance/trust_audits/instructions_files_budget.py:46, :170 | `awareness.get_banner` | measures banner bytes; not a mode read |
| reachability ratchet | .gzkit/chores/control-surface-validator-reachability/check_reachability.py:483-495 | `checkpoint.blocks`, `demote_notice` | demote its own finding |
| ledger inertness ratchet | .gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py:289-301 | same | same |
| enforcement registry | src/gzkit/enforcement.py:765-766, :818 | `mx.invariants`, `mx.proxy_reality` (registration and enumeration only) | **does not read the marker** |

---

## 10. Summary

### 10a. Counts by kind and role

| kind | rows | tripwire | alarm | monitor | safeguard | gate | other | dispatcher |
|---|---|---|---|---|---|---|---|---|
| git hook (18 config ids + post-commit.legacy + 6 inner guards; dormant G20 excluded) | 25 | 7 | 1 | 1 | 7 | 2 | 5 (producer 1, fixers 4) | 2 (G5, G17) |
| Claude/Codex hook (17 Claude entries, 4 permission controls, 2 Codex entries) | 23 | 4 | 4 | 7 | 4 | 3 | 1 (router) | 0 |
| `gz check` step (73 + *Test (changed)*) | 74 | 39 | 0 | 0 | 29 | 6 | 0 | 0 |
| validator (106 registry + V107, V108) | 108 | 59 | 1 | 0 | 34 | 13 | 0 | 1 |
| enforcement claim | 134 | 0 | 0 | 0 | 134 (NCs) | 0 | 0 | 0 |
| CI | 8 | 4 | 1 | 2 | 1 | 0 | 0 | 0 |
| CLI refusal (sampled) | 37 | 1 | 1 | 2 (C31, C32) | 5 | 27 | 1 (C35) | 0 |
| MX-internal guard | 4 | 0 | 2 | 0 | 1 | 1 | 0 | 0 |
| chore script | 8 | 2 | 2 | 1 | 3 | 0 | 0 | 0 |
| **total** | **421** | 116 | 12 | 13 | 218 | 52 | 7 | 3 |

Also counted: `GATE5_INVARIANTS` has 5 members, 2 of them named-not-enforced. There are 38 guard
canaries and 96 grandfathered claims. Two hook scripts are on disk but unregistered.

Each row with a mixed reading was counted under its first-named role: G5.5 "gate / safeguard"
counts as gate, C5 counts as gate, C31 counts as monitor, and CI7 counts as tripwire.

### 10b. Distinct places of call (dispatchers) and what each dispatches

| # | dispatcher | file:line | controls dispatched |
|---|---|---|---|
| D1 | pre-commit framework, `pre-commit` stage | .pre-commit-config.yaml | 15 hook ids |
| D2 | pre-commit framework, `prepare-commit-msg` | .pre-commit-config.yaml:21-26 | 1 |
| D3 | pre-commit framework, `pre-push` | .pre-commit-config.yaml:155-172 | 1 (→ D9) |
| D4 | pre-commit framework, `manual` | .pre-commit-config.yaml:179-209 | 1 |
| D5 | post-commit shim → `post-commit.legacy` | .git/hooks/post-commit.legacy | 1 (2 recorders) |
| D6 | `gzkit.hooks.guards.run_guards` | guards.py:569-589 | 6 |
| D7 | `gzkit.mx.alarms.main` wrapper | alarms.py:30-39 | 6 |
| D8 | Claude Code harness | .claude/settings.json:49-182 | 17 entries (15 scripts); plus 42 deny rules and 1 mode flag at :2-48 |
| D9 | `gz check` → `_run_check_steps` / `_seam` | commands/quality.py:942, :934 | 73 (`full`), 69 (`change`), 71 (`cross-platform`) |
| D10 | `gz validate` → `_run_scope_checks` | validate_cmd.py:923 | 95 registry scopes |
| D11 | `gz validate` → `_dispatch_early_return_scopes` | validate_cmd.py:1339 | 11 solo scopes + `--audits` (8 members) + `--attestation-receipts` |
| D12 | `enforcement.run_meta_validator` | enforcement.py:842 (callers quality.py:1637, guards.py:500 via quality, closeout_proof.py:154) | 134 claims + floor enrollment |
| D13 | `guard_canary.sweep_main` | guard_canary.py:420 (via quality.py:2009) | 38 canary kills |
| D14 | Codex harness | .codex/hooks.json | 2 |
| D15 | GitHub Actions | .github/workflows/*.yml | 8 job/step controls in 6 workflows |
| D16 | `gz obpi complete` | obpi_complete.py:1066 | 10 gates (C1-C10) |
| D17 | `gz obpi precomplete` | obpi_precomplete.py:217 | 13 checks |
| D18 | `gz mx exit` | mx_cmd.py:384 | 1 re-run of D9 at `change` scope |
| D19 | release funnels (`gz closeout`, `gz patch release`) | closeout.py:679, patch_release.py:1006 | 1 each (M2) |
| D20 | `gz chores advise/execute` | commands/chores.py | 8 chore scripts (plus prose criteria) |
| D21 | `mx_hardening_findings` | governance/trust_audits/mx_hardening.py:139 | 3 (M1, M3, M4) |
| D22 | other single-site CLI commands (lock, task, attest, withdraw/repudiate, pipeline stages, sync, implement, adr audit/covers, content, airlock) | section 7 | 1 to a few each |

### 10c. MX-aware against not

"MX-aware" means the control's code path reads `.gzkit/mx.json` today, whether directly, through
the checkpoint, or through the alarms wrapper.

| kind | consults the signal | does not | notes |
|---|---|---|---|
| git hook (25) | 15: G5 and its 6 guards, G6-G9, G17, G18 (alarms), G16 (pinned, never demotes), G19 (contract booking) | 10: G1-G4, G10-G15 | of the 15, only G5.3 and the 6 alarm hooks actually relax |
| Claude/Codex (23) | 6: H1, H3, H5, H9, H16, H22 | 17 (H23, the Codex twin of H5, included) | H5 is switched off in safe mode only; H9 relaxes in both modes |
| `gz check` step (74) | 74 pass the seam | 0 | effective relaxation: **59** (rc 3); **13** do not relax because they fail with rc≠3; **2** are pinned CRITICAL |
| validator (108) | 95 (93 demote; `ledger` and `authorship` pinned) | 13: the 11 solo scopes, V107, V108 | the 3 rendition audits and `mx_hardening` also read it internally |
| enforcement claim (134) | 0 | 134 | the runner is never demoted (CRITICAL at both gate callers) |
| CI (8) | 2 indirectly (CI1, CI2, through the tracked marker) | 6 | |
| CLI refusal (37, sampled) | 6: C19, C22, C25, C26, C31, C32 | 31 | `gz obpi complete` reads no marker |
| MX-internal (4) | 4 | 0 | |
| chore script (8) | 2: K3, K4 | 6 | |
| **total (421)** | **204** | **217** | |

### 10d. Surprises and gaps (facts, no recommendation)

1. **The marker is tracked in git, and HEAD carries `mode: safe`** (header, *State observed on this date*). Because
   `hangar_demotes` reads presence only (`marker.is_active`), CI's `gz check --full` and
   `--cross-platform` run with every rc-3, non-CRITICAL step demoted. That holds for every clone.
2. **In safe mode no `gz check` runs at push**: G17 is alarm-wrapped (`.pre-commit-config.yaml:169`,
   `alarms.py:36-38`).
3. **The step seam demotes only exit 3** (quality.py:197). Lint, Format, Typecheck, Test, Behave,
   Docs build (rc 1), Skill audit, Parity check, Readiness audit, CLI audit, Preflight, Smoke-tier
   test failure and Test (changed) still block under an open marker. The pre-commit G2 and G4 also
   stay on, by the comment at `.pre-commit-config.yaml:14-17`.
4. **`gz mx exit` re-runs the `change` scope, not `--full`** (mx_cmd.py:380). Test, Behave, Docs
   build, Preflight and the Guard canary sweep are not part of the exit's "every guard at full
   strength" re-run (docstring :391-398).
5. **11 solo validator scopes bypass the checkpoint** when invoked directly (validate_cmd.py:1339-1474).
   Nine of them are demoted only at the `gz check` seam.
6. **Twin controls read the signal differently.** H5 (Claude verifier gate) honours safe mode, and
   H23 (Codex) does not. H9 (Claude pipeline gate) demotes, while its commit-time twin G5.4 is pinned
   CRITICAL. H10 (Claude completion validator) reads no marker, while its twin G5.5 is a pinned floor
   member.
7. **Two readings of "open".** The checkpoint demotes in both `mx` and `safe` mode, and on an
   unreadable marker (checkpoint.py:47-50). The alarms wrapper switches off only in `safe` mode.
   Neither reading checks `marker.is_valid` (ledger binding). Only the lock reaper and preflight do.
8. **Two GATE5 floor members have no enforcement** (`secrets`, `operator-pii`; invariants.py:57).
   The working secrets scanner (gitleaks) sits outside the checkpoint and has no claim. The
   `grader-gaming` detector (`proxy_reality.scan`) has no production caller outside its NC.
9. **The GATE5 NCs exercise a sibling, not the commit-time guard.** `gate5-ledger` exercises
   `validate_ledger`, not G5.2. `gate5-attestation-absence` exercises the `gz obpi complete`
   validators, not G5.5. No NC was found for any of the six pre-commit guards.
10. **The enforcement floor runs at pre-commit**, on every commit (G5.6, `stages: [pre-commit]`),
    although its docstring calls it a pre-push guard (guards.py:497).
11. **96 of 134 claims have no canary, and 55 claims leave `exempts` undeclared.** The canary
    binding check runs only inside a unit test, so the `change` scope runs it only when *Test (changed)*
    selects it.
12. **The hook inventory has drifted.** `.claude/hooks/ceremony-step-gate.py` is neither generated
    nor registered. `control-surface-sync.py` is generated but not registered. The README lists the
    absent `session-start-advisement.py`. The registered count is 17 entries across 7 events (15
    scripts). `docs/rnd/contractor-kit.md`'s reframe entry records "10 entries across 7 events"
    (the decision entry at :2208-2224).
13. **Built-in self-tests exist only in 7 chore scripts** (`--self-test`: K1-K6, K8). Four of them
    run inside `gz check` before their ratchet (quality.py:1981, :2003, :2081). No hook, validator or
    CLI gate carries a self-test of its own. Their negative controls live outside them, as
    `@enforces` claims.
14. **Out-of-check validators.** 40 registry scopes are outside `gz check`. 36 of them have no NC
    found, and their only place of call is the `gz validate` flag (plus a chore acceptance criterion
    for `skill_alignment` and `router_tables`, and pre-commit G7 for three surface-fidelity scopes).
15. **`check-todos-fixmes` (G10) can never fail** (`|| true`).
