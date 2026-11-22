# Sweep report: CI, ARB receipts, test runners and gate recording

Research subagent report, read-only, returned 2026-11-22 to the session that opened this run
(`e870dccc-bfdb-48be-baa8-a327a1e81cb8`), landed verbatim as delivered. A subagent's claim is
not evidence until re-derived (`.gzkit/rules/model-selection.md` claim 5); the claims this run
relies on are re-read in the record's `source` entries.

---

## Where a check that never ran reports as passed: CI, ARB receipts, test runners, gate recording

The same class turns up on my track in two forms:
- **"Did not run" is coded as exit 3.** `gz check` treats exit 3 as a policy breach, and while the hangar is open it demotes any exit-3 step to success. A test tier that ran nothing therefore passes `gz check --full` in CI today.
- **Exit 0 is trusted as "ran".** Behave, the changed-test step, `gz test --obpi` and ARB step receipts only look at the exit code. The one execution judge that exists (`unit_run_provenance.py`) is wired into only some callers.

The marker is committed and the condition is on: `.gzkit/mx.json` has been in safe mode since 2026-10-20, and the CI log of run 45035389959 prints `✓ All checks passed (full sweep). — 3 guards demoted by the MX hangar`.

### Findings, most dangerous first

| # | Where | Cause | What the operator sees | Did-not-run distinguishable from passed? | Documented? |
|---|---|---|---|---|---|
| 1 | `src/gzkit/quality.py:645-659` (`run_tests`); `src/gzkit/commands/quality.py:182-219` (`_apply_mx_seam`); `"Test"` at ERROR, `commands/quality.py:70` | `run_tests` refuses a zero-exit run with exit 3 when it ran 0 tests, skipped every test, or collected fewer than the `data/unit_collection_floor.json` floor (11000). Under the marker the seam turns any exit 3 from a step not pinned CRITICAL into `success=True, returncode=0`. The same applies to the Guard canary sweep's "canary produced no run" (`guard_canary.py:533-536`, exit 3), the mkdocs validation-floor refusal (`quality.py:~1132-1141`) and the supply audit with no `uv.lock` (exit 3). All are ERROR-level. | `✓ Test`, a "Demoted by the open MX hangar" section, and the guard named on the pass line. CI's `check` job is green. | Partly. The demoted section, the pass-line suffix and the JSON `demoted` map show it, but JSON `checks.Test` reads `true`. `record_verified` (`check_fingerprint.py:175-197`) stores no demotion, so the pre-push reuse prints "already passed this check" with no mention of it. | **No.** `mx-mode.md` says every non-floor guard drops to advisory. Nothing says that a test tier which never ran demotes along with real breaches. Found by reading code, not by running it. |
| 2 | `.github/workflows/ci.yml:117-146`, job `full-strength-report` | `continue-on-error: true` with `GZKIT_MX_FULL_STRENGTH=1`. | The run is green while this job fails. In 60 of 60 sampled green CI runs (2026-11-10 to 11-22) it concluded `failure`: Tautological debt, Validate default scopes (141 errors, mostly `sensitivity-floor-violation`, plus a 4-error scope), and the tautological test audit. The `check` job shows these as "3 guards demoted". | Only in the job list. Run status says passed. | **Yes**, `ci.yml:120`: *"Operator ruling, 2026-10-26, verbatim: "report only, decide within #1273"."* |
| 3 | `commands/quality.py:1414-1465` (`_run_changed_tests`, step `Test (changed)`) | It calls `run_command` directly, with no `judge_unit_run`. I observed `unittest-parallel -k zz_no_such_test_zz` print `Ran 0 test`, `OK`, exit 0. When no module is selected it returns `success=True` with stdout "This is a SELECTION result, never a pass". | `✓ Test (changed)`. The "never a pass" text is never printed: output of passing steps is only shown for `gz validate` advisory lines (`commands/quality.py:1569-1601`). The change scope is `records_verified: true`, so the fingerprint is minted and the pre-push gate reuses it. | No. | Partly. The no-selection case is a deliberate heuristic per the docstring. The 0-run / all-skipped case is not documented. |
| 4 | Behave everywhere except OBPI completion: the `gz check` Behave step (`quality.py:661-704`, shard fold `814-840`), `gz test --bdd` (`commands/quality.py:483-494`), Gate 4 in `gz closeout` (`closeout.py:385-420`, runs `uv run -m behave features/`), `gz gates` (`gates.py:251-277`), and `gz test --obpi X --bdd` (`commands/quality.py:425-444`) | Behave exits 0 when all scenarios are skipped or a tag selects none. `judge_behave_run` (`unit_run_provenance.py:169`) is called only at `obpi_complete.py:506`. | `✓ Behave`, `Gate 4 (BDD): PASS`, and a ledger `gate_checked` with status `pass`. | No. Only the raw output says it. | **No.** |
| 5 | `gates.py:316-348` (`_run_eval_delta`, inside Gate 2 of `gz implement` and `gz gates`) | When there are no datasets or no baselines it writes `gate_checked` with status `"pass"` and evidence `"skipped: …"`. `data/eval/` has datasets but there is no `baselines/` directory, so this fires on every run. | `↳ Eval delta: skipped (no baselines)` (dim). The ledger reads `pass`. | Only through the free-text `evidence` field. The status itself says pass. | In code only ("REQ-2: graceful skip"). |
| 6 | `commands/quality.py:407-422` (`gz test --obpi`, pipeline Stage 3 per `gz-check/SKILL.md:29`) | No `@covers` tests: a yellow note and exit 0. Every test skipped: stdlib unittest exits 0 and it prints "passed (N tests)", where N is the number of names selected, not the number run. | Exit 0 and a green "passed". | The no-tests case only by the yellow prose. The all-skipped case not at all. | No. |
| 7 | `arb/step_reporter.py:116-167`; resolver `governance/trust_audits/attestation_receipts.py:126-141` | A step receipt records the raw return code with no execution judgment. `gz arb step --name unittest -- <canonical command>` over an empty or fully skipped suite writes `exit_status: 0`, and the attestation resolver accepts it as `resolved`. | A receipt ID that resolves "ok" as Gate-5 evidence. | Only by reading `stdout_tail` for `Ran 0` or `skipped=`. | No. Lesser points: `arb/advisor.py:131` counts a receipt with no `exit_status` as not failed. `--soft-fail` stays honest (the receipt keeps the real status; only the CLI returns 0). |
| 8 | `commands/arb.py:34,72,126-139`; `commit_witness.py:510-592` | RED commit verdicts `inconclusive` and `no-production-hunks` exit 0 and write `exit_status: 0`, the same as `driven`. | stderr `RED WITNESS INCONCLUSIVE…`, exit 0. | Yes, through the receipt's `verdict` field and stderr. Not through the exit code. `arb-red-*` IDs fall outside the attestation resolver's pattern (`attestation_receipts.py:28`), so they cannot satisfy Gate-5 receipt binding. | **Yes**, `ghi-close/SKILL.md:321`: *"`inconclusive` is about the run; cite its reason instead of a verdict."* |
| 9 | Skips meant for adopter projects: `run_mkdocs` with no `mkdocs.yml` (`quality.py:1124-1130`); a projectLocal chore that is absent (`quality.py:2468-2475`); the canary sweep with no registry (`guard_canary.py:520-522`); a registry with zero canaries, which prints "0 canary mutant(s) killed", exit 0 | Absence returns `success=True` with stdout starting `skipped:`. | `✓ <step>`. | No. The `skipped:` stdout of a passing step is never printed. | Yes, in docstrings ("failing a tree for a gate it was never delivered would make `gz check` unadoptable"). This is latent in gzkit itself, where all these files exist. |
| 10 | `release.yml` (no test job) | A tag push builds and publishes to PyPI with no `gz check` in the workflow. The sweep runs only inside `gz patch release` (`patch_release.py:900-921`), which refuses while the hangar is open (`:1071`). A hand-pushed tag skips both. | A green Release run. | The run makes no test claim, but `AGENTS.md`'s "at every release" is not enforced by CI. | Only in part: the header points to `docs/developer/release_process.md`. |
| 11 | Other CI skips that are deliberate and documented | `ci.yml:21-24` `paths-ignore` for handoffs, insights and the ledger. `ci.yml:39-41` cancels superseded runs. Windows runs `--cross-platform` and prints "Scoped checks passed … not run; this does NOT satisfy the pre-push gate". `docs.yml:80` and `docs-freshness.yml:15` skip when `VPS_HOST` is unset. `unit-tier-profile.yml` gates nothing. | A skipped job or a green run. | Yes. Each one is announced or shows as skipped. | Yes, each with a ruling or rationale in the file (for example `ci.yml:38`: *"cancel superseded runs is fine"*). No `\|\| true` anywhere in the workflows. |

### What I checked live
- CI run 45035389959: per-job conclusions and log lines.
- The `full-strength-report` conclusion across 60 green CI runs.
- `unittest-parallel` with zero tests selected (exit 0).
- `uv audit` actually runs (74 packages, exit 0).
- The marker file contents and the collection floor file.

### Coverage
Read in full or in the relevant regions:
- all 7 workflows
- the `gz check` pipeline in `commands/quality.py` (scope selection, seam, runner, rendering, recording, changed tests, `gz test`)
- `quality.py` (`run_tests`, Behave and shards, mkdocs, supply audit, chore ratchet)
- `mx/checkpoint.py`, `check_fingerprint.py`, `unit_run_provenance.py`, `canonical_steps.py`
- `arb/step_reporter.py`, `arb/red_reporter.py`, `commands/arb.py`, `attestation_receipts.py`, and part of `arb/advisor.py`
- `gates.py`, the gate path in `closeout.py`, the covering-test judges in `obpi_complete.py`
- `guard_canary.sweep_main`

Not read:
- `arb/validator.py` (receipt provenance), the `ruff_reporter` baseline judge, `arb/coverage.py`
- `_gate4_na_reason`: whether an N/A Gate 4 writes a ledger row
- the smoke-tier runner and the roughly 75 individual validator steps
- `sync.py:200`, and the `obpi_audit_cmd._run_tests` caller's handling of a 0 count
- `gz validate`'s own in-process demotion
- pre-commit, which is outside my track

Finding 1 comes from reading the code and was not reproduced by running it. A targeted test would be: feed `_apply_mx_seam` a `run_tests`-style result with exit 3 and "Unit tier refused" under an open marker. Its existing sibling is `tests/mx/test_check_step_checkpoint_seam.py:52`.

### Not yet tracked
Finding 1 is the closest relative of the operator's original finding. By the PRIME DIRECTIVE, findings 1, 3, 4, 6 and 7 need GHIs or an insight; I filed nothing because this was a read-only pass. GHI #1154 is open and is the nearest prior art for 3, 4, 6 and 7. Its fix added `judge_unit_run`/`judge_executed`/`judge_behave_run` but wired them into only some callers.
