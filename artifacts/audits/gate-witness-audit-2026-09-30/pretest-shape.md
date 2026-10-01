# Pre-fix test shape for nine GHIs (measured record, 2026-09-30)

Method: I found each fix commit with `git log v0.34.7..HEAD -E --grep="#N([^0-9]|$)"`, leaving out git-sync, chore and handoff commits. I read the tests at `<sha>^` with `git show <sha>^:<file>` and `git grep <symbol> <sha>^ -- tests`. Every line number below is a line in the file at the PARENT commit.

Classes: NO-TEST, HAPPY-ONLY, ABSENCE-ONLY-NEGATIVE, PROXY-BLESSED, DEFECT-PINNED, OTHER.

---

## #959: the chokepoint must require a resolution for `refuted-with-caveats`

Fix `ac57c15a8`. It changed one test file: `tests/test_adversarial_validation_gate.py`. The fix changed the guard from `verdict == "refuted" and not resolution` to `verdict in REFUTATION_VERDICTS and not resolution`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| ac57c15a8 | tests/test_adversarial_validation_gate.py:83 | `verdict=None` | SystemExit (block) | negative with an absent field | `verdict="refuted-with-caveats", resolution=None` → SystemExit |
| | :87 | `adversary=None` | SystemExit | negative with an absent field | |
| | :92 | `verdict="refuted", resolution=None` | SystemExit | negative with an absent field; only ONE member of the refutation class | |
| | :97 | `verdict="refuted", resolution="membership assertions added; mutation now FAILS"` | passes | positive | |
| | :100 / :105 | `degraded-human-only` / `not-refuted` | passes | positive | |
| | :124 | `refuted`, resolution None, JSON | error names `--adversary-resolution` | message check | |

**Classification: OTHER (set-subset), plus ABSENCE-ONLY-NEGATIVE.**

- **OTHER (set-subset).** The refutation class has two members. The chokepoint tests fed only `"refuted"`. `"refuted-with-caveats"` appears in the chokepoint test file only in the vocabulary-equality test at :77.
- **ABSENCE-ONLY-NEGATIVE.** Every negative in this file fed a `None` field.
- **The other layer did test this input.** The advisory pre-flight tested it: `tests/commands/test_obpi_precomplete.py:720` feeds `"**Verdict: REFUTED-WITH-CAVEATS** - two findings deferred."` and asserts `assertFalse(result.ok)`. So the correct input was tested in the bypassable layer and missing in the layer that fails closed.

---

## #960: a refutation loops and never completes, even with a resolution

Fix `edbab5ae4`. Its parent is `ac57c15a8` (#959). It changed one test file: `tests/test_adversarial_validation_gate.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| edbab5ae4 | tests/test_adversarial_validation_gate.py:97 `test_refuted_with_resolution_passes` | `verdict="refuted", resolution="membership assertions added; mutation now FAILS"` | passes (no exit) | DEFECT-PINNED | `verdict="refuted", resolution="membership assertions added; mutation FAILS"` → SystemExit |
| | :114 `test_refuted_with_caveats_with_resolution_passes` | `verdict="refuted-with-caveats", resolution="regression test added for the injected-only path; adversary re-ran it"` | passes | DEFECT-PINNED | caveats with resolution in `(None, "regression test added; …")` → SystemExit for both |
| | :92, :100 | refuted or caveats, resolution None | SystemExit | negative (still true after the fix) | message must contain "Stage 2" and "not-refuted" |

**Classification: DEFECT-PINNED.** Two parent tests asserted a pass on exactly the input the fix blocks. The fix deleted both tests.

Caveat: "defect" here comes from a later ruling. The operator's ruling of 2026-09-04 is quoted in the commit: "refuted is an outcome, but it is an input into if(4a && 4b) pass; else: loop". The test at :114 was added one commit earlier by #959's own fix, as its "false-positive arm". So the pinning test was authored deliberately, on the same day, under the doctrine that was current then.

---

## #888: a SUPPORT REQ's proof channel was inferred by substring search

Fix `f289bd483`. It changed two test files: `tests/test_req_kind_support_channel.py` and `tests/governance/test_closeout_proof_view.py`.

| fix sha | test file:line at parent | input fed (REQ text) | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| f289bd483 | tests/test_req_kind_support_channel.py:256 `test_no_path_citation_falls_back_to_type_only` | `"manpage updated — artifact_edited ledger event + gz validate --documents"`, ledger `[_ev("artifact_edited", None)]`, scope patched True | `"pass"` | DEFECT-PINNED | same string, same ledger, same patch → `"undeclared-support"` (`test_an_undeclared_req_resolves_undeclared_never_pass`) |
| | :38 `test_pass_when_event_found_and_scope_exits_zero` | `"manpage updated — artifact_edited ledger event + gz validate --documents (doc-tree structural validator)"` | `"pass"` | DEFECT-PINNED (free text is the inference path) | |
| | :130, :167, :201, :274, :290, :369 | affirmative citation text; the ledger or validator side is varied (wrong path, event type never emitted, ledger missing, validator non-zero) | `unproven-support` / not pass | negatives on the ledger and validator axes only | |
| | :353 `test_unproven_when_citation_unparseable` | `"rule file exists and is correct"` (no event name at all) | not pass | ABSENCE-ONLY-NEGATIVE on the text axis | `"The ledger carries NO corpus_entry_retired event for these ids — measured 0 of 8. …"` → `parse_support_citation` returns `None` |
| | :239 `test_scope_prefers_non_recursion_fence_validator` | the body names a fence scope as its subject | `scope == "documents"` | the only non-affirmative text test; it covers scope, not event | an unrelated mention of `artifact_edited` → `None` |

**Classification: DEFECT-PINNED and ABSENCE-ONLY-NEGATIVE (text axis).**

- **DEFECT-PINNED.** At :256, input that the fix makes resolve `undeclared-support` was asserted `"pass"` under identical ledger and patch conditions.
- **ABSENCE-ONLY-NEGATIVE.** On the REQ-text axis, the only negative lacked the event name entirely. No parent test fed a denial of the event or an unrelated mention of it.

---

## #932: back-pointer matching (`"<!-- lifted-from:" not in dest_content`)

Fix `a2a952959`, a joint fix with #931. It changed one test file: `tests/governance/test_pointer_integrity.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| a2a952959 | tests/governance/test_pointer_integrity.py:184 `test_missing_back_pointer_emits_error` | destination `"# Rationale\n\n## My Section\n\nbody\n"` (no lifted-from comment) | 1 error, mentions `lifted-from` | ABSENCE-ONLY-NEGATIVE | destination `"## H\n\nbody\n\n<!-- lifted-from: totally/unrelated.md#nothing -->\n"` → 1 error naming `AGENTS.md#h` |
| | :201 `test_back_pointer_anywhere_in_destination_is_accepted` | `"…<!-- lifted-from: AGENTS.md#h -->\n"` (a MATCHING comment, at the end) | `errors == []` | positive, true input | `<!-- lifted-from: AGENTS.md#some-other-anchor -->` → 1 error |
| | :60, :80, :93, :108 | matching back-pointers | `[]` | positive, true input | one destination with two incoming sources and one comment → 1 error |

**Classification: ABSENCE-ONLY-NEGATIVE.** The only negative fed a destination with no comment at all.

- **:201 does not pin the defect.** The commit message says :201 "asserted the defect as intended behavior". Measured: its input is a correct, matching back-pointer, its assertion still holds after the fix, and the fix only renamed it (to `test_matching_back_pointer_anywhere_…`). The defect is carried by the test's name, not by its input or assertion.
- **Side finding (#931, not in the nine).** :93 `test_resolved_pointer_in_rules_dir` fed root-relative `(docs/r.md#foo-bar)` from `.claude/rules/` and asserted `[]`. The fix changed that input to `../../docs/r.md`. That test is DEFECT-PINNED for #931.

---

## #933: Invariant 3's reverse arm (orphaned `lifted-from` declarations)

Fix `82f8ab453`. It changed one test file: `tests/governance/test_pointer_integrity.py`, adding `TestReverseArmOrphanedBackPointer` with 12 tests.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| 82f8ab453 | none | — | — | NO-TEST | origin `"## Section\n\nThe pointer that used to be here is gone.\n"` and destination `docs/governance/r.md` = `"# R\n\n<!-- lifted-from: AGENTS.md#h -->\n## H\n\nbody\n"` → 1 error at `docs/governance/r.md:3` |

**Classification: NO-TEST.**

- The arm did not exist before the fix.
- At the parent, `git show 82f8ab453^:tests/governance/test_pointer_integrity.py | grep -c docs/governance` returns 0: no fixture placed a declaration inside the reverse arm's scope.
- The other parent files that mention pointer_integrity don't exercise the reverse arm. `test_gate_caller_scope.py` only counts callers. `test_surface_fidelity_composite.py` mocks the validator, with `mock_pointer.return_value = []`.

---

## #851: the session-green gate's delivery arm read only `pre-push`

Fix `1edf9dc1b`, a joint fix with #1007. It changed `tests/test_session_green_gate_validator.py` and `tests/commands/test_init_hook_delivery.py`, and added `tests/governance/test_session_green_gate_delivery_control.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| 1edf9dc1b | tests/test_session_green_gate_validator.py:197 `test_declared_and_installed_passes` | config `_HOOK_WITH_PRE_PUSH` (no `default_install_hook_types`); `.git/hooks/pre-push` shim only; NO `pre-commit` hook | `== []` | PROXY-BLESSED (a subset of the hooks installed) | config `default_install_hook_types: [pre-commit, pre-push]`, installed `["pre-push"]` → 1 error, artifact contains `pre-commit` |
| | :222 `test_hooks_path_redirect_is_followed` | the redirected dir holds `pre-push` only | `== []` | PROXY-BLESSED (same subset) | |
| | :186 | declared, nothing installed | 1 error "not installed" | absence negative | |
| | :210 | `pre-push` = `"#!/bin/sh\nexit 0\n"` (present but foreign) | 1 error | present-but-wrong negative | |
| | :248 `test_delivery_arm_is_off_by_default` | declared, not installed, `check_delivery` omitted | `== []` | positive by design (unchanged by the fix) | |
| | registered negative control `_qc_negative_controls.py:173` plus `_qc_nc_entrypoints.py:453` | a `pre-push` hook whose entry is `gz check-config-paths` | caught | the NC reaches the DECLARATION arm only: its entrypoint is `return audit_session_green_gate(root)`, with no `check_delivery` | NC population = every declared hook type; patching `_declared_hook_types` to `["pre-push"]` → FACADE naming `pre-commit` |

**Classification: PROXY-BLESSED and OTHER.**

- **PROXY-BLESSED.** After the fix, `_declared_hook_types` returns `list(_PRE_COMMIT_DEFAULT_TYPES) + ["pre-push"]` = `["pre-commit", "pre-push"]` when the config has no list. So the parent's :197 input, `pre-push` alone, is a subset that the fix makes fail. The fix had to add `(hooks / "pre-commit").write_text(...)` to the `_worktree` helper to keep :197 green.
- **OTHER.** Every parent fixture declared a single hook type, and the registered NC never reached the delivery arm.
- The negatives are not absence-only: :210 feeds a present-but-wrong hook.

---

## #1007: a negative control for a set-shaped claim plants only one member

Fix `1edf9dc1b`. It added `tests/governance/test_enforcement_population.py` and `tests/governance/test_population_controls.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| 1edf9dc1b | tests/governance/test_enforcement_meta_validator.py:96 `test_pass_when_entrypoint_returns_truthy_list` | one fixture with one planted violation; the entrypoint catches it | PASS | single-plant positive | population `("alpha","beta","gamma")`, the witness sees `{"alpha","beta"}` → FACADE, message names `gamma` |
| | :125 `test_facade_when_entrypoint_returns_falsy` | the entrypoint returns falsy | FACADE | negative | a witness that always returns a generic error → FACADE (the finding must name the member) |
| | :136 / :147 | the fixture raises / the entrypoint raises | TEST_BUG | negative | an empty population → TEST_BUG |
| | tests/governance/test_enforcement_nc_discrimination.py:154 / :166 | one finding matching `expect` / one finding with an unrelated message (`"Missing \`.gitattributes\`"`) | PASS / FACADE | present-but-wrong negative | |

**Classification: OTHER.** The population axis was never varied: every runner test fed one planted violation. No parent test fed a witness that covers a strict subset of a declared set, and the `population=` parameter did not exist.

This is not HAPPY-ONLY and not ABSENCE-ONLY-NEGATIVE. Negatives exist, and :166 feeds a present-but-wrong finding.

---

## #1124: `gz tidy` exited 0 on findings

Fix `1a5317c89`. It added `tests/commands/test_tidy_verdict.py` (12 tests; the commit reports 7 RED) and changed `tests/unit/test_runtime_presentation.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| 1a5317c89 | tests/unit/test_runtime_presentation.py:167 (call at :194) | `validate_all` → `errors=[SimpleNamespace(type="demo", message="broken fixture")]`; `tidy.tidy(check_only=False, fix=True, dry_run=True)` | the call returns normally (a raise would error the test); asserts `"⚠"` and `"→"` in the output | DEFECT-PINNED (implicit) | `_run(errors=[SimpleNamespace(type="header", message="broken")])` → exit code 3, `"Project is tidy"` absent |
| | same test, second half (:198–:213) | `errors=[]`; `vault_status` NOT stubbed (the host's real vault) | `"✓"` present | positive; the vault input is uncontrolled | `_run(vault=DRIFTED / ABSENT / RECOVERABLE)` → 3 and the success line absent |
| | tests/commands/test_sync_preflight_guard.py:80 / :107 | `tidy --fix` on corrupt / clean canon | non-zero / 0 | a different gate (sync preflight) | `tidy --check --fix` → parse exit 2 |

**Classification: DEFECT-PINNED (implicit).**

- The only parent test that fed tidy a finding required it to return without `SystemExit`. The fix had to wrap that same call in `self.assertRaises(SystemExit)`.
- No parent test asserted tidy's exit code on a finding.

---

## #803: `mkdocs.yml` `links.not_found: ignore` hid dead links under `--strict`

Fix `d266be9ff`. It changed `tests/test_quality.py` (adding `TestDocsBuildValidationFloor`, 11 tests) and `tests/governance/test_bullet_retention.py`.

| fix sha | test file:line at parent | input fed | asserted outcome | classification | fix's RED input |
|---|---|---|---|---|---|
| d266be9ff | tests/test_quality.py:630 `test_docs_build_in_check_steps` | none (step-list introspection) | `"Docs build"` in the step names | wiring only | `"site_name: p\nvalidation:\n  links:\n    not_found: ignore\n"` → `success False`, returncode 3, `run_command` not called |
| | :640 `test_docs_build_is_skipped_when_the_project_has_no_docs_site` | an empty tmp dir (no mkdocs.yml) | `result.success` True, returncode 0 | positive (absence → pass, by design) | same with `not_found: info`; `nav.not_found: info`; an INHERIT-chain downgrade |
| | :656 `test_docs_build_runs_strict_when_a_docs_site_exists` | `"site_name: probe\n"`; `run_command` mocked to success | `assertIn("--strict", invoked)` | proxy assertion: the flag string stands in for "dead links fail closed" | `test_this_repositorys_mkdocs_config_meets_the_floor` (the live config) |

**Classification: HAPPY-ONLY and OTHER (a flag-string proxy).**

- **HAPPY-ONLY.** No parent test fed `run_mkdocs` an input expected to fail: no dead link, and no config with a downgraded validation level.
- **OTHER.** :656 asserted only that `--strict` was in the command. The live parent `mkdocs.yml:228-229` read `links:\n    not_found: ignore`, which cancels `--strict` for dead links.
- No parent test read the repository's own `mkdocs.yml`: `git grep mkdocs.yml d266be9ff^ -- tests` hits only prose and the `"site_name: probe"` fixture.

---

## Summary

| GHI | fix | classification |
|---|---|---|
| #960 | edbab5ae4 | DEFECT-PINNED (under a later ruling; the pinning test was added by #959) |
| #959 | ac57c15a8 | OTHER (set-subset: one of two class members fed) + ABSENCE-ONLY-NEGATIVE |
| #888 | f289bd483 | DEFECT-PINNED + ABSENCE-ONLY-NEGATIVE (text axis) |
| #932 | a2a952959 | ABSENCE-ONLY-NEGATIVE |
| #933 | 82f8ab453 | NO-TEST |
| #851 | 1edf9dc1b | PROXY-BLESSED (a subset of the hooks installed → pass) + OTHER (single-member population; the NC never reached the delivery arm) |
| #1007 | 1edf9dc1b | OTHER (a single planted violation; the population axis never varied) |
| #1124 | 1a5317c89 | DEFECT-PINNED (implicit: a finding fed, a normal return required) |
| #803 | d266be9ff | HAPPY-ONLY + OTHER (a `--strict` flag-string proxy) |

Count per classification across the nine (a GHI can have more than one): NO-TEST 1, HAPPY-ONLY 1, ABSENCE-ONLY-NEGATIVE 3, PROXY-BLESSED 1, DEFECT-PINNED 3, OTHER 4.

Only #803 fits "happy paths only" in the literal sense. The dominant shape is a test set whose negatives, or whose population, never included the specific wrong-but-present input: a second class member, a denial, a non-matching comment, a subset population, a downgraded config.
