# Sweep report: git hooks

Research subagent report, read-only, returned 2026-11-22 to the session that opened this run
(`e870dccc-bfdb-48be-baa8-a327a1e81cb8`), landed verbatim as delivered. A subagent's claim is
not evidence until re-derived (`.gzkit/rules/model-selection.md` claim 5); the claims this run
relies on are re-read in the record's `source` entries.

---

## Git-hook track: places where a hook exits 0 (or shows Passed/Skipped) without doing its check

I made no edits. I read `.pre-commit-config.yaml`, the installed shims in `.git/hooks/` (pre-commit 4.6.2), pre-commit's own `hook_impl.py`, `run.py` and `git.py`, and every script these hooks run.

**Live state, checked read-only:** `marker.condition()` reads `on`, level `drydock`. `alarms_off()` returns True, and so does `hangar_demotes()`. Running `gzkit.mx.alarms gz-check-pre-push -- false` printed `[safe mode] gz-check-pre-push is off until gz mx exit` and returned exit 0.

**Why none of this shows:** pre-commit prints a hook's output only when it exits non-zero, modifies files, or runs verbose (`run.py:217`). No hook in the config sets `verbose`. So any stderr or stdout notice from a hook that exits 0 is NOT visible.

| # | Hook id | Exit path (file:line) | Class | Visible? | Documented? | One-line fix |
|---|---|---|---|---|---|---|
| 1 | gz-check-pre-push (also `validator-reachability-ratchet`, `ledger-vocabulary-inertness`, `unittest`) | `src/gzkit/mx/alarms.py:49-51` | a | No: shows "Passed" | Deliberate (alarms.py docstring; config:14-15 "skips it while .gzkit/mx.json carries `mode: safe`"), but the display contradicts it | Set `verbose: true` on every alarm-wrapped hook, or exit with a distinct code that pre-commit shows |
| 2 | forbid-pytest (`skill-sync-drift` guard, ERROR) and both chore scripts | `src/gzkit/hooks/guards.py:664-665`; `check_ledger_inertness.py:341-343`; `check_reachability.py:553-555` | a | No | Deliberate, and the intent is defeated. guards.py:648-650: "A demoted finding is ANNOUNCED, never discarded… an operator otherwise cannot tell a clean run from a hangar run". The announcement goes to output pre-commit suppresses | Same as #1: the demote notice has to reach a surface pre-commit shows |
| 3 | gz-check-pre-push (`--reuse-verified`) and lint-pre-push | `src/gzkit/commands/quality.py:1505`; `src/gzkit/check_fingerprint.py:124-168` (fingerprint is the INDEX tree) | c, d | No | Undocumented | Fingerprint and test `PRE_COMMIT_TO_REF`'s tree, not the index |
| 4 | authorship | `src/gzkit/governance/trust_audits/authorship.py:83-97, 112-116` | c | No | Undocumented: the comment describes the mechanism, not the gap | Check `%ae`/`%ce` of the pushed commits at pre-push |
| 5 | Every pre-commit-stage hook without `always_run` (forbid-pytest, gitleaks, authorship, ruff, ty, the validators) | pre-commit `git.py:135-143` (`--diff-filter=ACMRTUXB` drops D); `run.py:168-180` | c | Shown as "(no files to check) Skipped", with nothing marking it as a hazard | Undocumented | Set `always_run: true` on forbid-pytest and authorship |
| 6 | ty-check, complexity-ceiling | `.pre-commit-config.yaml:57-61, 77-81` (`types: [python]`, `pass_filenames: false`) | c | "Skipped" | Undocumented | Drop `types:` or add pyproject.toml to `files:`, so the whole-tree check triggers on config edits and deletions |
| 7 | complexity-advisor-auto-chain (dormant; installed by `python -m gzkit.hooks.install_complexity_advisor`, which the gz-complexity-advisor skill offers) | `.gzkit/hooks/pre-commit-complexity-advisor:11-23`; `install_complexity_advisor.py:55-88, 93-106` | b, e | Partly (timeout warning goes to stderr, so hidden) | Timeout fail-open is documented ("commit proceeding (fail-open)"). The rest is not | `exit $GATE_EXIT` whenever the advisor finds no block |
| 8 | closing-keywords, lint-pre-push, gz-check-pre-push | pre-commit `hook_impl.py:128-174` | c | No: no output at all | Undocumented in repo | Write a repo-side pre-push that loops over every stdin ref |
| 9 | lint-pre-push, gz-check-pre-push | config:164-172, 185-202 (no `always_run`) | c | "Skipped" | Undocumented | Add `always_run: true` to gz-check-pre-push |
| 10 | forbid-pytest (`ledger` and `gate5-attestation` guards) | `guards.py:184-200` (`_run_git` returns "" on failure or non-zero exit); `216-218`; `221-231`; `524-525, 532` | b | No | Undocumented | Use `--no-color --no-ext-diff` and fail closed when git exits non-zero |
| 11 | gz-check-pre-push ("Test (changed)" step) | `quality.py:1449-1458`; `1437-1446` | c, a | No | The heuristic is documented in the docstring; the hiding is not | Render the selection-only result as a skipped step and refuse to record the fingerprint |
| 12 | gz-check-pre-push (reuse) | `check_fingerprint.py:124-168`; `quality.py:1225-1245` | d | No | Partly (GHI #1017 covers trailers only) | Hash the non-tree inputs into the fingerprint, or list the steps that read them in `_unfingerprinted_findings` |
| 13 | task-trailer-stamp | `.gzkit/hooks/prepare-commit-msg-task-trailers:23-25, 70-71` | b | No | Deliberate: "Every failure path is a silent no-op… caught downstream by `gz validate --commit-trailers` anyway" | Correct the comment, or keep commit-trailers out of the alarm-wrapped hook |
| 14 | check-todos-fixmes | config:104-111 (`|| true`) | e | No, never | Labelled "informational", but "flagged" is false | Add `verbose: true` or delete the hook |
| 15 | complexity-ceiling (audit) | `src/gzkit/governance/trust_audits/complexity_ceiling.py:257-261`; `244-246` | b | No | Shipped-only scope is documented ("Hold the Python the wheel ships"); the empty-set pass is not | Treat an empty shipped set as a finding |
| 16 | forbid-pytest (`skill-sync-drift`) | `guards.py:292-297` | b | No | Deliberate: "a pre-commit guard that aborts the commit because the project config is absent or unparseable would be a worse failure…" | — |
| 17 | forbid-pytest (`post-authoring-src-commits`) | `src/gzkit/pipeline_stage_fence.py:61-63, 70-77`, consumed at `guards.py` around line 470 | b | No | Deliberate: "None is permissive by design… an unreadable marker is a separate defect with its own guard" | — |
| 18 | post-commit recorder (`post-commit.legacy` → `src/gzkit/hooks/commit_ledger.py`) | `commit_ledger.py:280-291, 302-306`; pre-commit `hook_impl.py:40-42` | b | Failures are visible (legacy output is not captured). A non-executable legacy hook is silent | Deliberate: "never let a recorder break a commit" | — |
| 19 | surface-fidelity-cheap (`bullet_retention`) | `bullet_retention.py:700-704, 748-751` | b | No | Absence is partly covered by the pinned-identity check (`_pins_identities`) | Not fully traced |
| 20 | All hooks (git level) | `default_install_hook_types` (config:11) | c | `--no-verify`: invisible. `SKIP=`: shows "Skipped". `PRE_COMMIT_ALLOW_NO_CONFIG`: prints | AGENTS.md forbids `--no-verify`; the rest is undocumented | — |
| 21 | unittest | config:239 (`stages: [manual]`) | a | n/a | Deliberate ("CI-only by default") | — |

**Detail behind the rows:**

- **#1:** this is live now. It turns off the only local run at push of the validators, the trailer checks, the changed tests and ty.
- **#2:** it also applies at hangar level, and to `gz validate` demotions printed to stderr (`src/gzkit/commands/validate_cmd.py:1063-1066`). The `gz check` demoted-guard suffix (`quality.py:1290-1310`) is likewise unseen through pre-commit.
- **#3:** pre-commit stashes unstaged changes at pre-push too (`run.py:344, 421`). So the gate checks HEAD plus whatever is staged, never the pushed ref. Commit A (broken), stage fix B, `gz check` passes and records tree(B), then `git push` sends A with "skipped — already passed" or a real pass over B.
- **#4:** it reads `git config user.email`, never the commit's author or committer. So `--author`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_EMAIL` and amend or cherry-pick of a commit that already carries the personal email all pass. `git grep` for `%ae|%ce|GIT_AUTHOR_EMAIL` in src and .github found nothing, so no other check reads commit identity.
- **#5:** a deletion-only or empty commit stages no files, so every such hook is skipped. `git rm .gzkit/ledger.jsonl` alone skips the ledger guard that is "never relaxed". The downstream `gz check` is alarm-off.
- **#6:** a commit that only edits `[tool.ty]` or `max-complexity` in pyproject.toml, or only deletes a module, skips both checks. ty's only push-time run is `gz check`, which is off in safe mode.
- **#7:** the shell script throws away the gate's exit code. A ceiling failure passes when no non-deleted .py is staged (lines 17-18). Otherwise the verdict is the advisor's, which fails only on a `block` band of a different table. A missing rule file or an engine-init failure returns 0. Intrinsic attestations skip functions. The skill text says "failing the commit on a block crossing" and never says that other gate failures pass.
- **#8:** `_pre_push_ns` returns on the first ref with new commits, so in a multi-ref push only that ref is checked. A ref whose commits are already on a remote counts as "nothing to push", and no hook runs.
- **#9:** a pushed range that changes no files (empty commits) is skipped, so the trailer steps inside `gz check` never read those commits.
- **#10:** if git fails, the ledger guard returns 0 (`216-218`). It parses raw `git diff --cached` with no `--no-color`/`--no-ext-diff`, so `color.diff=always` or `diff.external` hides the "-" lines (`221-231`). Neither is set in this clone today; I checked. The gate5 guard `continue`s on an empty `git show` or an unparsed OBPI id (`524-525, 532`).
- **#11:** when no tests are selected, the step returns `success=True`. Its stdout says "This is a SELECTION result, never a pass", but that text is never rendered: only passing `gz validate` steps have their output shown (`_bears_advisories`, `quality.py:1571`). The pass is still recorded as verified. Setting `GZKIT_IN_CHANGED_TESTS` in the environment skips the run.
- **#12:** the fingerprint hashes only tracked tree content. Inputs outside it are reused unread: gitignored `.gzkit/locks/` and `.gzkit/cache/`, `.git/hooks`, the upstream ref `Test (changed)` diffs against, and tool versions. Only the trailer and task-envelope steps are excluded from reuse.
- **#13:** the "downstream" backstop it relies on, `gz validate --commit-trailers`, sits inside gz-check-pre-push, which is off in safe mode.
- **#15:** if `wheel_shipped_files(missing_ok=True)` finds nothing, the audit returns `[]`. The cognitive leg silently skips when `.gzkit.json` has no `cognitive_ceiling`.

**Adjacent finding (reachability ratchet).** The ratchet counts a scope as gated wherever the text `gz validate --x` appears under `.pre-commit*` or `.claude/hooks/` (`check_reachability.py:100-114, 255-273`). It ignores the alarm wrapper, `stages: [manual]` and comments. Scopes reachable only through the alarm-off `gz check` also count as gated (tier A) in safe mode.

**Pointer outside my track:** CI checks out the committed `.gzkit/mx.json`. Only the `full-strength-report` job sets `GZKIT_MX_FULL_STRENGTH`, and it only reports. So the CI backstop that #6, #11 and #13 rely on is likely demoted too. I did not verify the CI workflow.

**What passes cleanly:** I traced these and found no silent pass:
- `closing_keywords` (`check=True` raises, so it fails closed).
- `gz lint` (a Ruff or baseline error returns 2; a missing baseline fails every finding).
- `forbid_pytest`'s file scan (git failure falls back to a walk; an unreadable file is a violation).
- The guard checkpoint (`_guard_grounds` fails closed).
- The work-package fence (an unreadable fence holds).
- The alarm wrapper's own import and resolve errors (they crash non-zero).
- The pre-commit validate scopes, which are all pinned CRITICAL.
- The formatters and fixers, uv-lock and check-merge-conflict.
- gitleaks: it runs with `--verbose`, and `.gitleaksignore` holds only two ledger fingerprints.

**How I know the list is complete, and what I left out.** I went through all 19 hooks in `.pre-commit-config.yaml`, the five installed shims in `.git/hooks/` including `post-commit.legacy`, both scripts in `.gzkit/hooks/`, and each module a hook runs. I also read the pre-commit code that decides Passed, Skipped and output display. Two areas are not finished:
- **Not covered:** the roughly 60 individual `gz check` steps beyond the reuse, changed-test and demotion logic (that is the gz-check track), and every early return inside `bullet_retention`, `pointer_integrity` and `surface_weight`. I sampled those but did not trace them.
- **Out of my track:** `.claude/hooks/` and `src/gzkit/hooks/scripts/` are harness hooks, not git hooks. No git hook runs them, so I did not audit them.

My claims about which git operations skip pre-commit-stage hooks (clean `git merge`, cherry-pick, rebase) come from git's documented behaviour. I did not run them, because they write.
