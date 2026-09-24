# gzkit test-suite integrity audit — 2026-09-24

Dated diagnostic at commit `5d9885a08c438b0aa546716b20a181c55342612e`. Persona: main-session, acting as an auditor. The operator authorized one report in the repository; this report is the only repository artifact written by this audit. No fixes, dependency changes, commits, ledger events, or applied ADR edits are part of the audit. Other sessions advanced the working checkout during execution; all measurements use the pinned copy.

**Read these limits first.** Semantic review covered all 600 selected pilot test methods and a seeded sample of 300 other methods, plus targeted adjacent comparisons. Mutation covered nine modules and their declared test commands, not all production code. All generated survivors are listed; most have not received semantic equivalence review. Coverage excludes arbitrary child processes. Git establishes committed order, not within-commit TDD order. The complete exclusions and omitted validator scopes are in section 11.

Navigation: [Controls](#3-controls) · [Measurements](#4-numbers) · [Twenty tests](#5-the-twenty-worst-confirmed-tests) · [All survivors](#6-survived-mutants--complete-list) · [Dispositions](#7-dispositions-and-bloat) · [History](#8-process-findings) · [Unapplied proposal](#9-pool-adr-proposal--unapplied-unified-diff) · [Proposed gates](#10-proposed-scriptable-gates) · [Limits](#11-not-examined-and-inference-limits).

## 1. Verdict

A green run is insufficient evidence that gzkit’s required behavior is protected. The canonical run reports “Ran 10747 tests” and “OK (skipped=4),” yet the suite contains a constant assertion, a vacuous scanner assertion, an exemption test with no specimen, redundant tests, and a weakened command-count oracle. The selected requirement-coverage tests also let two behavior-changing mutants survive. Separately, the completion coverage gate warns instead of stopping a lite feature with missing BEHAVIOR proof, and the waiver ratchet measures a different quantity from its consumer. These are demonstrated gaps, not conclusions drawn from suite size or weak-looking syntax. The evidence does not justify claiming that every survivor marks an untested line or that most tests verify nothing; the random sample’s confirmed defect rate is 1/300 (0.33%). Receipts follow in sections 3–8.

## 2. Starting facts

| Fact | Observed pinned result |
|---|---|
| 1: 654 files/about10,500 tests | Corrected:675 `test_*.py` files;706 Python files under tests;10,751 syntactically defined `test*` methods in classes. Use the full-suite run for discovered/executed tests. |
| 2:224,940 test/155,043 production lines | Corrected:230,591 physical lines in tests Python files;229,504 in `test_*.py`;157,212 in515 production Python files. |
| 3:40% floor;branches off | Confirmed as declared chore policy: `src/gzkit/chores/coverage-40pct/acceptance.json:15` runs `coverage report --fail-under=40`;`pyproject.toml:266` says `branch=false`. Correct the implication that this floor gates ordinary CI: no coverage step exists in `gz check`;CI only invokes `gz check --full`. |
| 4:4,724 literals in354 files | Corrected:4,718 exact `@covers(` occurrences in350 files.325 files lack that exact spelling;47 of those still contain another `@covers` spelling/token.278 lack `@covers` entirely. Raw occurrences include fixture strings and are not resolved proof counts. |
| 5:280 baseline ops,August15 | Confirmed:280 operations;generated_at `2026-08-15T22:54:14.922215+00:00`. |
| 6:filesystem scanner,not D1–D8 | Confirmed with scope correction:tautological scanner combines filesystem-shaped operations with assertions and exempts production calls/source fences;test-shape adds render-surface assertions. Neither implements a general D1/D2/D3/D4/D5/D6/D7/D8 semantic detector. Some D6/D8 instances can overlap the filesystem heuristic; do not erase the entire class. The validate scope also owns a wall-clock-fixture detector since GHI#865 (`tautological_tests.py:585`). |
| 7:one production caller of mutation sweep | Confirmed:`acceptance_execution.py:362`;definition `mutation_witness.py:335`. |
| 8:no general mutation tool | Confirmed for project manifests and inspected project venv:neither cosmic-ray nor mutmut is declared in pyproject/uv.lock or installed in that environment. Global environments were not inventoried. |
| 9:117 no-assert/822 weak-only | Different present crude census:215 no direct assertion call/bare assert and827 weak-only among10,751 class method definitions. These are candidate counts, not confirmed defects:helpers,fixture classes,exception or mutation outcomes must be resolved. The older scanner's exact algorithm was not provided, so this does not establish like-for-like growth. |

An additional AST pass distinguishes annotation syntax from raw text: 4,613 covers decorator expressions occur in 342 files; 333 files have none. Of those 333, 27 still contain REQ references accepted by the canonical comment/docstring scanner. Appendix B classifies all 333 and identifies that distinction. Fifteen files use local identity decorators deliberately supported by the syntax scanner; those are not discarded as fake annotations.

```text
$ uv run --no-project --python <audit-interpreter> python controls/finalize_actual_covers.py
{
  "pinned_commit": "5d9885a08c438b0aa546716b20a181c55342612e",
  "files": 675,
  "raw_exact_covers_paren_occurrences": 4718,
  "files_with_raw_exact_covers_paren": 350,
  "files_with_raw_covers_token": 397,
  "ast_decorator_occurrences": 4613,
  "files_with_actual_ast_decorators": 342,
  "files_without_actual_ast_decorators": 333,
  "files_without_raw_covers_token": 278,
  "additional_unannotated_files_exposed_by_ast": 55,
  "files_with_nonnested_test_decorator": 341,
  "categories": {
    "behavioral test": 272,
    "structural fence": 36,
    "output-form fixture": 14,
    "SUPPORT proof": 11
  },
  "method": "AST FunctionDef/AsyncFunctionDef/ClassDef decorator expressions; covers names and imported aliases resolved syntactically. Strings, docstrings and comments excluded. Nested fixture decorators retained and flagged; this is syntax inventory, not proof of discovered passing REQ bindings.",
  "files_without_decorator_with_canonical_scanner_hits": 27,
  "nonfixture_files_without_decorator_with_canonical_scanner_hits": 25,
  "files_without_decorator_or_canonical_scanner_hit": 306,
  "local_covers_definition_files": 15,
  "local_covers_decorator_occurrences": 483,
  "decorated_files_without_nonnested_test_decorator": [
    "tests/commands/test_init_update.py"
  ]
}
```

The refined AST census identifies 10,747 explicit unittest methods, excluding four methods in nested specimen classes. An ancestry pass resolves all 10,747 to unittest.TestCase, and the canonical runner independently reports the same count. “Test files” means test_*.py; physical line counts include blank lines and comments.

Run from the pinned clone (substitute its dependency-bearing interpreter if needed):

```sh
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/controls/uv-cache uv run --no-project --python /Users/jeff/Documents/Code/gzkit/.venv/bin/python /private/tmp/gzkit-test-audit-20260924/controls/census.py
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/controls/uv-cache uv run --no-project --python /Users/jeff/Documents/Code/gzkit/.venv/bin/python /private/tmp/gzkit-test-audit-20260924/controls/extend.py
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/controls/uv-cache uv run --no-project --python /Users/jeff/Documents/Code/gzkit/.venv/bin/python /private/tmp/gzkit-test-audit-20260924/controls/control_probes.py
```

The recorded outputs are `census.log`, `extend.log`, and `control_probes.log` in that scratch directory. The census reads physical Python lines, not SLOC. `test_*.py` includes fixture files; the syntactic method count includes methods in nested fixture classes and is not a substitute for the canonical runner's runtime count. For REQs, it uses the repository's acceptance-section parser and kind reader, excludes ledger-withdrawn/on-disk withdrawn/abandoned/superseded/deprecated/archived briefs, and applies the completion gate's legacy default of BEHAVIOR to untagged REQs. It does not claim that untagged legacy requirements were authored explicitly BEHAVIOR. Receipt-file availability and ledger event history are counted separately.

```text
$ uv run --no-project --python <audit-interpreter> python controls/census.py
{
  "commit": "5d9885a08c438b0aa546716b20a181c55342612e",
  "test_files": 675,
  "all_test_python_files": 706,
  "defined_test_methods_in_classes": 10751,
  "test_lines_all_py": 230591,
  "test_lines_test_py": 229504,
  "production_files": 515,
  "production_lines": 157212,
  "literal_covers_paren_occurrences": 4718,
  "test_files_literal_covers_paren": 350,
  "files_no_covers_token": 278,
  "crude_no_assert_call": 215,
  "crude_only_weak_asserts": 827,
  "nonwithdrawn_briefs": 538,
  "behavior_req_items": 2775,
  "unique_behavior_reqs": 2775,
  "explicit_behavior_req_items": 548,
  "implicit_behavior_req_items": 2227,
  "behavior_reqs_with_red_receipt_file": 23,
  "behavior_reqs_with_red_receipt_share": 0.008288288288288289,
  "red_receipt_files": 43,
  "red_receipt_unique_reqs": 23,
  "red_receipt_failure_class": {
    "error": 41,
    "assertion": 1,
    "none": 1
  },
  "red_parity_errors": [],
  "check_registered_steps": 63,
  "check_change_steps": 61
}
```

## 3. Controls

“Stops” means the configured invocation actually returns failure. Commit and pre-push are separate moments. The unittest pre-commit-config entry is manual-only (`.pre-commit-config.yaml:199`);the pre-push entry invokes `gz check --reuse-verified` (`:154`). CI invokes `gz check --full` (`.github/workflows/ci.yml:66`). No listed test-quality control is a pre-commit hook. Cheap lint/typecheck/policy hooks can independently stop a commit.

| Control | What it checks | Failure effect | Editable by implementation agent? |
|---|---|---|---|
| `gz covers` /Stage3 parity | Traceability references,then per-kind proof status;it does not execute tests. | `covers_cmd` reports gaps without nonzero exit (`commands/covers.py:182,234`).Stage3 skill requires inspecting uncovered count and holding Stage4 (`.gzkit/skills/gz-obpi-pipeline/SKILL.md:600-618`).No direct commit/CI parity invocation. Actual completion gate executes covering tests and fails heavy/foundation,but only warns lite/feature (`commands/obpi_complete.py:663-705`). | Code,briefs,annotations,grandfather caches and pipeline skill are repository-controlled;technically editable in ordinary implementation scope.Policy does not authorize changing their doctrine to clear a gate.This audit prohibits every such edit. |
| `gz arb red` | Runs covering tests against a base withholding production changes;classifies assertion/error/none/not-applicable and records provenance. | Direct command returns1 for none,no-cover;0 for not-applicable and reconstructed-base inconclusive errors (`commands/arb.py:74-148`).Not run by commit/CI;separate `--red-parity` is a `gz check` step and blocks push/CI only for post-cutover completed heavy briefs.A working-tree error is accepted weak RED;semantic assertion adequacy is not established. | `red_witness.py`,arb code,red-parity code and threshold/CUTOVER code are writable project source.Ledger policy allows writes only via gz;technical access is not permission. |
| `gz test-shape` | Filesystem operation disposition and undeclared render assertion inventory. | Always0;stops nothing (`commands/test_shape.py:63,82,90`).An advisory is a recorded open review item,not automatically a proved defective test. | Scanner and marker declarations are source/test content;adding an output marker changes declared classification without strengthening a test. |
| `gz validate --tautological-test-audit` | Newly unmatched filesystem-shaped operations plus wall-clock fixture defects. | Policy breach exit3;bound `gz check` step blocks pre-push/CI.Default baseline/waivers allow existing ops (`tautological_tests.py:609-650`;`commands/quality.py:632`).No direct commit hook. | Scanner,baseline,waivers and their ratchet registry are project files.The ratchet constrains data,but has reproduced counting gaps below. |
| 40% coverage | Line coverage threshold when explicit chore acceptance/report command runs. | Stops that chore/report command,not configured commit,pre-push or CI.No coverage measurement or threshold step in63 registered check steps.`gz arb coverage` defaults to measurement argv,not report threshold (`commands/arb.py:208-222`). | Chore acceptance JSON,canonical command and pyproject config are project files.Threshold changes need recorded governance rationale,not routine unilateral edits. |
| `gz validate --commit-trailers` | HEAD commit touching src/tests needs Task trailer;rule commits closing eval-feedback issue need source trailer when issue labels resolve. | Default validator tier since GHI#1017;blocks pre-push/CI,not current commit (`commands/validate_cmd.py:181-193`).Checks HEAD only (`commands/validate_commit_trailers.py:24-40,52-73`),not every commit in pushed range. | Validator,tasks parser,hook and config are repo-controlled;ordinary technical write access offers no independent immutable enforcement boundary. |

### Reproduced gaps and enforcement boundaries

1. **Lite feature completion can return through the coverage gate with a missing BEHAVIOR proof.** The same synthetic brief and missing tests produce `lite_feature_missing_cover: RETURNED_NORMALLY` versus `heavy_feature_missing_cover: EXIT 3`. Receipt:`control_probes.log:4-11`;cause:`commands/obpi_complete.py:663,701`. This is the isolated coverage gate's behavior,not a claim every later completion guard is bypassed. It conflicts with AGENTS's universal coverage obligation.
2. **The waiver ratchet counts files rather than waived operations.** Current2 files hold3 slots;adding a fourth slot inside an existing file yields0 ratchet errors. Receipt:`control_probes.log:2`;cause:`waiver_ratchet.py:71-74` takes `len(dict)`,while `tautological_tests.py:625` counts each file's list length as waiver capacity;registry binds `file_waivers` at `data/waiver_ratchet_registry.json:34-39`. This is a concrete mismatch between protection and consumer.
3. **The baseline ratchet permits regrowth below its fixed cap.** Current280 operations,configured cap290;synthetic281 yields0 errors. Receipt:`control_probes.log:3`;cause:`waiver_ratchet.py:157-190`. The implementation checks a ceiling,not monotonic decrease from the immediately preceding committed count. No filesystem mutation was needed for either probe.
4. **A green configured CI run does not establish the40% floor.** Registered-step census has no coverage step;unit step's canonical argv omits coverage;CI only runs `gz check --full`. Receipts:`check_steps.json`, `quality.py:427`, `.github/workflows/ci.yml:66`, `coverage-40pct/acceptance.json:15`.
5. **Commit trailer guard observes only HEAD.** It does not inspect earlier commits in a multi-commit push;this is a source-scoped limitation,not a reproduced bad push. Receipt:`commands/validate_commit_trailers.py:24-40,52-73`.

The conflict is literal. AGENTS.md:134 says: “REQ-coverage gate: every BEHAVIOR REQ needs a passing `@covers` test before `gz obpi complete`; this cannot be waived. SUPPORT and STRUCTURAL-FENCE REQs use their declared proof channels.” The implemented branch prints “REQ-coverage gate reported gaps (lite-non-foundation; warn-only)” at commands/obpi_complete.py:701–703. This audit records the disagreement and changes neither rule nor implementation.

```text
$ uv run --no-project --python <audit-interpreter> python controls/control_probes.py
WARN `--no-project` was provided, but no project was found
{"waiver_existing_files": 2, "original_operation_slots": 3, "perturbed_operation_slots": 4, "ratchet_errors_after_adding_slot": 0}
{"original_baseline_operation_count": 280, "perturbed_baseline_operation_count": 281, "configured_baseline_limit": 290, "ratchet_errors_after_growth": 0}
Warning: REQ-coverage gate reported gaps (lite-non-foundation; warn-only):
  - uncovered: REQ-9.9.9-01-01
lite_feature_missing_cover: RETURNED_NORMALLY
Error: OBPI completion REQ-coverage gate failed (heavy/foundation policy).
  - uncovered: REQ-9.9.9-01-01
Recovery: add a `@covers(REQ-X.Y.Z-NN-MM)` test for each gap, or fix the failing
covering tests, then re-run completion.
heavy_feature_missing_cover: EXIT 3
```

### Canonical unit run

```text
$ uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
Running 672 test suites (10747 total tests) across 10 workers
----------------------------------------------------------------------
Ran 10747 tests in 145.450s

OK (skipped=4)
arb step name=unittest exit_status=0 receipt=/private/tmp/gzkit-test-audit-20260924/baseline/artifacts/receipts/arb-step-unittest-0c611c24cac541fa809066856795e6a7.json
```

Command wall time: 159.241 seconds; runner time: 145.450 seconds. ARB exit_status=0. The receipt is copied into this report’s evidence appendix. The first attempted launch was invalidated after fixture uv sync replaced a shared external environment. A later completed run had six setup-dependent failures; fixing scratch Git identity removed one, and routing uvx tools into the writable scratch tool directory removed the remaining module-size negative-control failures. No repository code was fixed to obtain green. Those earlier failures are not reported as suite defects. The final coverage run uses the corrected environment.

### Every registered gz check step

Extracted from `commands/quality.py:_build_check_steps`;63 registered,61 default. The full scope includes Behave and Preflight;default drops these two only. Execution partitions writers/readers and may run readers concurrently;this is registration order,not a claim every step executes serially. A failed result makes aggregate exit1 (`commands/quality.py:1201-1214,1221-1232`).

1. Lint — `run_lint` (`commands/quality.py:588`).
2. Format — `run_format_check` (`commands/quality.py:589`).
3. Typecheck — `run_typecheck` (`commands/quality.py:590`).
4. Module size — `run_module_size_audit` (`commands/quality.py:591`).
5. Test — `run_tests` (`commands/quality.py:592`).
6. Behave — `run_behave` (`commands/quality.py:593`) **full-only**.
7. Docs build — `run_mkdocs` (`commands/quality.py:594`).
8. Validate default scopes — `run_validate_default_scopes` (`commands/quality.py:595`).
9. Skill audit — `run_skill_audit` (`commands/quality.py:596`).
10. Parity check — `run_parity_check` (`commands/quality.py:597`).
11. Readiness audit — `run_readiness_audit` (`commands/quality.py:598`).
12. CLI audit — `run_cli_audit` (`commands/quality.py:599`).
13. Unscoped rules — `run_unscoped_rules_audit` (`commands/quality.py:600`).
14. Python version pins — `run_python_version_pins_audit` (`commands/quality.py:601`).
15. ADR status freshness — `run_adr_status_fresh_audit` (`commands/quality.py:602`).
16. Advisory scorecard coverage — `run_advisory_scorecard_audit` (`commands/quality.py:603`).
17. OBPI lifecycle coherence — `run_obpi_lifecycle_coherence_audit` (`commands/quality.py:604`).
18. Adversarial validation — `run_adversarial_validation_audit` (`commands/quality.py:605`).
19. RED parity — `run_red_parity_audit` (`commands/quality.py:606`).
20. Producer field parity — `run_producer_fields_audit` (`commands/quality.py:607`).
21. Rendition freshness — `run_rendition_freshness_audit` (`commands/quality.py:608`).
22. Rendition floor coherence — `run_rendition_floor_coherence_audit` (`commands/quality.py:609`).
23. Rendition lineage — `run_rendition_lineage_audit` (`commands/quality.py:610`).
24. Invariant coherence — `run_invariant_coherence_audit` (`commands/quality.py:611`).
25. Corpus retirement witness — `run_corpus_retirement_witness_audit` (`commands/quality.py:612`).
26. Wheel path literals — `run_wheel_path_literals_audit` (`commands/quality.py:613`).
27. Doc code citations — `run_doc_code_citations_audit` (`commands/quality.py:614`).
28. Brief structure — `run_brief_structure_audit` (`commands/quality.py:615`).
29. Session green gate — `run_session_green_gate_audit` (`commands/quality.py:616`).
30. Closeout proof — `run_closeout_proof_audit` (`commands/quality.py:617`).
31. Kind invariance — `run_kind_invariance_audit` (`commands/quality.py:618`).
32. Persona witness — `run_persona_witness_audit` (`commands/quality.py:619`).
33. Interview transcripts — `run_interviews_audit` (`commands/quality.py:620`).
34. Pool interview schema — `run_pool_interview_audit` (`commands/quality.py:621`).
35. Receipt shape — `run_receipt_shape_audit` (`commands/quality.py:622`).
36. Orientation freshness — `run_orientation_freshness_audit` (`commands/quality.py:623`).
37. Insights shape — `run_insights_shape_audit` (`commands/quality.py:624`).
38. Instructions files budget — `run_instructions_files_budget_audit` (`commands/quality.py:625`).
39. AGENTS.md map conformance — `run_agents_md_map_conformance_audit` (`commands/quality.py:626`).
40. Complexity-doctrine links — `run_complexity_doctrine_links_audit` (`commands/quality.py:627`).
41. Complexity-thresholds — `run_complexity_thresholds_audit` (`commands/quality.py:628`).
42. REQ kind discipline — `run_req_kind_discipline_audit` (`commands/quality.py:629`).
43. Status writer coverage — `run_status_writer_coverage_audit` (`commands/quality.py:630`).
44. Transcribed ADR counts — `run_transcribed_adr_counts_audit` (`commands/quality.py:631`).
45. tautological test audit — `run_tautological_test_audit` (`commands/quality.py:632`).
46. Task envelope coherence — `run_task_envelope_coherence_audit` (`commands/quality.py:633`).
47. Lock-exchange coupling — `run_lock_exchange_coupling_audit` (`commands/quality.py:634`).
48. QC binding — `run_qc_binding_audit` (`commands/quality.py:635`).
49. Fidelity presence — `run_fidelity_presence_audit` (`commands/quality.py:636`).
50. Waiver ratchet — `run_waiver_ratchet_audit` (`commands/quality.py:637`).
51. Config registry — `run_config_registry_audit` (`commands/quality.py:638`).
52. Gate callers — `run_gate_callers_audit` (`commands/quality.py:639`).
53. Exemption controls — `run_exemption_controls_audit` (`commands/quality.py:640`).
54. Population controls — `run_population_controls_audit` (`commands/quality.py:641`).
55. Handoff documents — `run_handoff_document_audit` (`commands/quality.py:642`).
56. Preflight — `run_preflight` (`commands/quality.py:643`) **full-only**.
57. Surface fidelity — `run_surface_fidelity_audit` (`commands/quality.py:644`).
58. Line endings — `run_line_endings_audit` (`commands/quality.py:645`).
59. Authorship policy — `run_authorship_audit` (`commands/quality.py:646`).
60. Smoke tier — `run_smoke_tier` (`commands/quality.py:647`).
61. Dispatch absorption marker — `run_dispatch_absorption_marker_audit` (`commands/quality.py:648`).
62. Enforcement floor — `run_enforcement_floor_audit` (`commands/quality.py:649`).
63. ADR taxonomy — `run_taxonomy_audit` (`commands/quality.py:652`).

The “Validate default scopes” step expands to:`manifest`, `surfaces`, `ledger`, `instructions`, `briefs`, `documents`, `personas`, `frontmatter`, `version`, `taxonomy`, `invariant_coherence`, `commit_trailers`, `rule_version_markers`, `invariant_witness`, `wheel_path_literals`, `corpus_retirement_witness`, `doc_code_citations`. Source:`commands/validate_cmd.py:150-428`.

## 4. Numbers

### Requirement and RED evidence

Across538 nonwithdrawn briefs there are2775 distinct BEHAVIOR REQs under the completion parser:548 explicit and2,227 legacy-default. The local receipt store has43 `arb-red-*` files covering23/2,775=0.8288%;the ledger retains235 RED events for122 REQs,117 of which remain in the denominator:117/2,775=4.2162%. These are different evidence populations,not interchangeable totals. Receipt:`counts.json`,`extended_counts.json`.

The configured RED gate reaches23 terminal heavy briefs/111 BEHAVIOR REQs,and `audit_red_parity` returned `[]`. The remaining population is not a configured failure merely for lacking RED. Current usable witnesses among all current BEHAVIOR REQs are97 errors,16 assertions,1 none;21 historical none events are preserved below. The local none receipt is an additional historical execution with no matching event in the pinned ledger. Passing on a selected base establishes failure to distinguish that base;it does not mathematically prove the test can never fail.

| Ledger line | Receipt ID | REQ | Date |
|---|---|---|---|
| `.gzkit/ledger.jsonl:12513` | `arb-red-REQ-0.0.8-03-01-422aa899677f4a63b0f953e174d970f3` | `REQ-0.0.8-03-01` | 2026-07-09T10:55:31.459234+00:00 |
| `.gzkit/ledger.jsonl:12514` | `arb-red-REQ-0.0.8-03-01-885f76e2132445e9a3bb7d60bd2e42e5` | `REQ-0.0.8-03-01` | 2026-07-09T10:57:02.969886+00:00 |
| `.gzkit/ledger.jsonl:13615` | `arb-red-REQ-0.34.0-02-01-440b77328b104c818654aab29a0ac9a6` | `REQ-0.34.0-02-01` | 2026-07-20T11:01:41.765987+00:00 |
| `.gzkit/ledger.jsonl:13616` | `arb-red-REQ-0.34.0-02-02-24d54bc4ebda42e0b84a7f504a26171a` | `REQ-0.34.0-02-02` | 2026-07-20T11:01:46.735473+00:00 |
| `.gzkit/ledger.jsonl:13617` | `arb-red-REQ-0.34.0-02-03-cbf2f81754574f5c84cc52d9b91e3f74` | `REQ-0.34.0-02-03` | 2026-07-20T11:01:52.105264+00:00 |
| `.gzkit/ledger.jsonl:13618` | `arb-red-REQ-0.34.0-02-04-e0f249f2f42b4f0285b20643b029eda2` | `REQ-0.34.0-02-04` | 2026-07-20T11:01:57.402439+00:00 |
| `.gzkit/ledger.jsonl:13619` | `arb-red-REQ-0.34.0-02-05-b8cc8cdc926f46d4afb269b5c3762c87` | `REQ-0.34.0-02-05` | 2026-07-20T11:02:02.498297+00:00 |
| `.gzkit/ledger.jsonl:14430` | `arb-red-REQ-0.34.0-05-01-323f5e22297c4907aa11456a4527faf1` | `REQ-0.34.0-05-01` | 2026-07-30T10:44:18.625189+00:00 |
| `.gzkit/ledger.jsonl:15155` | `arb-red-REQ-0.35.0-09-05-263ccffbbe324442ac365bcd0db4b323` | `REQ-0.35.0-09-05` | 2026-08-18T01:23:44.964863+00:00 |
| `.gzkit/ledger.jsonl:15156` | `arb-red-REQ-0.35.0-09-05-3514d7f3d01c489f90a69b24476da857` | `REQ-0.35.0-09-05` | 2026-08-18T01:24:41.702887+00:00 |
| `.gzkit/ledger.jsonl:15223` | `arb-red-REQ-0.35.0-09-01-aea9b84f08fd49afa3f6d76185049f14` | `REQ-0.35.0-09-01` | 2026-08-21T01:10:26.119810+00:00 |
| `.gzkit/ledger.jsonl:15224` | `arb-red-REQ-0.35.0-09-02-b7455fab380e4f73b8326d27a6ae3edb` | `REQ-0.35.0-09-02` | 2026-08-21T01:10:33.835368+00:00 |
| `.gzkit/ledger.jsonl:15225` | `arb-red-REQ-0.35.0-09-03-2519825d0562496390c30780fff4c079` | `REQ-0.35.0-09-03` | 2026-08-21T01:10:40.177167+00:00 |
| `.gzkit/ledger.jsonl:15226` | `arb-red-REQ-0.35.0-09-04-f99bae9c8f8f494da1c77b5cac95132a` | `REQ-0.35.0-09-04` | 2026-08-21T01:10:46.810391+00:00 |
| `.gzkit/ledger.jsonl:15227` | `arb-red-REQ-0.35.0-09-05-f6d5d7a299f54083bbba4e23622583f0` | `REQ-0.35.0-09-05` | 2026-08-21T01:10:53.721042+00:00 |
| `.gzkit/ledger.jsonl:15228` | `arb-red-REQ-0.35.0-09-06-4fbe01d2bb9b440c95683a47764341a9` | `REQ-0.35.0-09-06` | 2026-08-21T01:10:59.820250+00:00 |
| `.gzkit/ledger.jsonl:15229` | `arb-red-REQ-0.35.0-09-08-f3f97ec1dc024177bb9546eb395f98ba` | `REQ-0.35.0-09-08` | 2026-08-21T01:11:06.534822+00:00 |
| `.gzkit/ledger.jsonl:15230` | `arb-red-REQ-0.35.0-09-09-076818081c374310b89dc8a8ab6c1370` | `REQ-0.35.0-09-09` | 2026-08-21T01:11:13.373138+00:00 |
| `.gzkit/ledger.jsonl:15231` | `arb-red-REQ-0.35.0-09-10-ce0157d84aa641de88eed36e10888c82` | `REQ-0.35.0-09-10` | 2026-08-21T01:11:19.681960+00:00 |
| `.gzkit/ledger.jsonl:15232` | `arb-red-REQ-0.35.0-09-11-2fad49c817444fecb4157fa73079a4e1` | `REQ-0.35.0-09-11` | 2026-08-21T01:11:26.352756+00:00 |
| `.gzkit/ledger.jsonl:15454` | `arb-red-REQ-0.35.0-02-06-55a37c3e78e44ed29e4606f1225a05a1` | `REQ-0.35.0-02-06` | 2026-08-25T01:54:51.290507+00:00 |

Local-file none:`artifacts/receipts/arb-red-REQ-0.35.0-09-01-f59c0f83d5044b8fad0470af415a9202.json:1`;2026-09-06T15:25:30Z;two covering tests in `TestAgentContractPlaybackConsumer`,both passed against77402bdf. The historical ledger none for09-01 was followed by an error witness;the current red gate has no finding for it. Do not report these historical rows as21 currently defective tests.

```text
$ uv run --no-project --python <audit-interpreter> python controls/extend.py
{
  "ledger_red_raw_events": 235,
  "ledger_red_evidence_events": 235,
  "ledger_red_unique_reqs": 122,
  "behavior_reqs_with_ledger_red": 117,
  "ledger_red_by_class": {
    "none": 21,
    "error": 169,
    "assertion": 39,
    "not-applicable": 6
  },
  "none_ledger_rows": [
    {
      "line": 12513,
      "id": "arb-red-REQ-0.0.8-03-01-422aa899677f4a63b0f953e174d970f3",
      "req": "REQ-0.0.8-03-01",
      "ts": "2026-07-09T10:55:31.459234+00:00",
      "base": "79d19482bb4efee21a932d0b3fd76e510179ade7"
    },
    {
      "line": 12514,
      "id": "arb-red-REQ-0.0.8-03-01-885f76e2132445e9a3bb7d60bd2e42e5",
      "req": "REQ-0.0.8-03-01",
      "ts": "2026-07-09T10:57:02.969886+00:00",
      "base": "79d19482bb4efee21a932d0b3fd76e510179ade7"
    },
    {
      "line": 13615,
      "id": "arb-red-REQ-0.34.0-02-01-440b77328b104c818654aab29a0ac9a6",
      "req": "REQ-0.34.0-02-01",
      "ts": "2026-07-20T11:01:41.765987+00:00",
      "base": "9fff4e7eff80153a29b3f4aa1ac0881aa8dd9032"
    },
    {
      "line": 13616,
      "id": "arb-red-REQ-0.34.0-02-02-24d54bc4ebda42e0b84a7f504a26171a",
      "req": "REQ-0.34.0-02-02",
      "ts": "2026-07-20T11:01:46.735473+00:00",
      "base": "9fff4e7eff80153a29b3f4aa1ac0881aa8dd9032"
    },
    {
      "line": 13617,
      "id": "arb-red-REQ-0.34.0-02-03-cbf2f81754574f5c84cc52d9b91e3f74",
      "req": "REQ-0.34.0-02-03",
      "ts": "2026-07-20T11:01:52.105264+00:00",
      "base": "9fff4e7eff80153a29b3f4aa1ac0881aa8dd9032"
    },
    {
      "line": 13618,
      "id": "arb-red-REQ-0.34.0-02-04-e0f249f2f42b4f0285b20643b029eda2",
      "req": "REQ-0.34.0-02-04",
      "ts": "2026-07-20T11:01:57.402439+00:00",
      "base": "9fff4e7eff80153a29b3f4aa1ac0881aa8dd9032"
    },
    {
      "line": 13619,
      "id": "arb-red-REQ-0.34.0-02-05-b8cc8cdc926f46d4afb269b5c3762c87",
      "req": "REQ-0.34.0-02-05",
      "ts": "2026-07-20T11:02:02.498297+00:00",
      "base": "9fff4e7eff80153a29b3f4aa1ac0881aa8dd9032"
    },
    {
      "line": 14430,
      "id": "arb-red-REQ-0.34.0-05-01-323f5e22297c4907aa11456a4527faf1",
      "req": "REQ-0.34.0-05-01",
      "ts": "2026-07-30T10:44:18.625189+00:00",
      "base": "a4fc44759a226aa2fae3d405d1f8ff7a6b246c11"
    },
    {
      "line": 15155,
      "id": "arb-red-REQ-0.35.0-09-05-263ccffbbe324442ac365bcd0db4b323",
      "req": "REQ-0.35.0-09-05",
      "ts": "2026-08-18T01:23:44.964863+00:00",
      "base": "d69f17aec719424dd3e6875cbd5c72a4d3b79ff3"
    },
    {
      "line": 15156,
      "id": "arb-red-REQ-0.35.0-09-05-3514d7f3d01c489f90a69b24476da857",
      "req": "REQ-0.35.0-09-05",
      "ts": "2026-08-18T01:24:41.702887+00:00",
      "base": "422aecad2"
    },
    {
      "line": 15223,
      "id": "arb-red-REQ-0.35.0-09-01-aea9b84f08fd49afa3f6d76185049f14",
      "req": "REQ-0.35.0-09-01",
      "ts": "2026-08-21T01:10:26.119810+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15224,
      "id": "arb-red-REQ-0.35.0-09-02-b7455fab380e4f73b8326d27a6ae3edb",
      "req": "REQ-0.35.0-09-02",
      "ts": "2026-08-21T01:10:33.835368+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15225,
      "id": "arb-red-REQ-0.35.0-09-03-2519825d0562496390c30780fff4c079",
      "req": "REQ-0.35.0-09-03",
      "ts": "2026-08-21T01:10:40.177167+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15226,
      "id": "arb-red-REQ-0.35.0-09-04-f99bae9c8f8f494da1c77b5cac95132a",
      "req": "REQ-0.35.0-09-04",
      "ts": "2026-08-21T01:10:46.810391+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15227,
      "id": "arb-red-REQ-0.35.0-09-05-f6d5d7a299f54083bbba4e23622583f0",
      "req": "REQ-0.35.0-09-05",
      "ts": "2026-08-21T01:10:53.721042+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15228,
      "id": "arb-red-REQ-0.35.0-09-06-4fbe01d2bb9b440c95683a47764341a9",
      "req": "REQ-0.35.0-09-06",
      "ts": "2026-08-21T01:10:59.820250+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15229,
      "id": "arb-red-REQ-0.35.0-09-08-f3f97ec1dc024177bb9546eb395f98ba",
      "req": "REQ-0.35.0-09-08",
      "ts": "2026-08-21T01:11:06.534822+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15230,
      "id": "arb-red-REQ-0.35.0-09-09-076818081c374310b89dc8a8ab6c1370",
      "req": "REQ-0.35.0-09-09",
      "ts": "2026-08-21T01:11:13.373138+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15231,
      "id": "arb-red-REQ-0.35.0-09-10-ce0157d84aa641de88eed36e10888c82",
      "req": "REQ-0.35.0-09-10",
      "ts": "2026-08-21T01:11:19.681960+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15232,
      "id": "arb-red-REQ-0.35.0-09-11-2fad49c817444fecb4157fa73079a4e1",
      "req": "REQ-0.35.0-09-11",
      "ts": "2026-08-21T01:11:26.352756+00:00",
      "base": "558e80996df7a948a0c52491f5972c781c729ee9"
    },
    {
      "line": 15454,
      "id": "arb-red-REQ-0.35.0-02-06-55a37c3e78e44ed29e4606f1225a05a1",
      "req": "REQ-0.35.0-02-06",
      "ts": "2026-08-25T01:54:51.290507+00:00",
      "base": "b9761789054dd19bbe04c74af39f5bc4e2e72c13"
    }
  ],
  "current_valid_witness_class": {
    "none": 1,
    "error": 97,
    "assertion": 16
  },
  "red_gate_scoped_briefs": 23,
  "red_gate_scoped_behavior_reqs": 111,
  "red_gate_scoped_req_ids": [
    "REQ-0.0.65-02-01",
    "REQ-0.0.65-02-02",
    "REQ-0.0.65-02-03",
    "REQ-0.0.65-02-04",
    "REQ-0.0.65-02-05",
    "REQ-0.0.65-02-07",
    "REQ-0.0.65-02-08",
    "REQ-0.0.65-03-01",
    "REQ-0.0.65-03-02",
    "REQ-0.0.65-03-03",
    "REQ-0.0.65-04-01",
    "REQ-0.0.65-04-02",
    "REQ-0.0.65-04-03",
    "REQ-0.0.65-05-01",
    "REQ-0.0.65-05-02",
    "REQ-0.0.65-05-03",
    "REQ-0.0.65-05-04",
    "REQ-0.0.65-05-05",
    "REQ-0.0.72-03-01",
    "REQ-0.0.72-03-02",
    "REQ-0.0.72-03-05",
    "REQ-0.0.72-04-01",
    "REQ-0.0.72-04-02",
    "REQ-0.0.72-04-03",
    "REQ-0.0.72-04-05",
    "REQ-0.33.0-02-01",
    "REQ-0.33.0-02-02",
    "REQ-0.33.0-02-03",
    "REQ-0.33.0-02-04",
    "REQ-0.33.0-02-05",
    "REQ-0.33.0-02-06",
    "REQ-0.33.0-03-01",
    "REQ-0.33.0-03-02",
    "REQ-0.33.0-03-03",
    "REQ-0.33.0-03-04",
    "REQ-0.33.0-03-05",
    "REQ-0.33.0-04-01",
    "REQ-0.33.0-04-02",
    "REQ-0.33.0-04-03",
    "REQ-0.33.0-04-04",
    "REQ-0.33.0-05-01",
    "REQ-0.33.0-05-02",
    "REQ-0.33.0-05-03",
    "REQ-0.33.0-05-04",
    "REQ-0.33.0-05-05",
    "REQ-0.33.0-05-06",
    "REQ-0.34.0-01-01",
    "REQ-0.34.0-01-02",
    "REQ-0.34.0-01-03",
    "REQ-0.34.0-01-04",
    "REQ-0.34.0-02-01",
    "REQ-0.34.0-02-02",
    "REQ-0.34.0-02-03",
    "REQ-0.34.0-02-04",
    "REQ-0.34.0-02-05",
    "REQ-0.34.0-03-01",
    "REQ-0.34.0-03-02",
    "REQ-0.34.0-03-03",
    "REQ-0.34.0-03-04",
    "REQ-0.34.0-04-01",
    "REQ-0.34.0-04-03",
    "REQ-0.34.0-05-02",
    "REQ-0.34.0-05-03",
    "REQ-0.34.0-05-04",
    "REQ-0.35.0-01-01",
    "REQ-0.35.0-01-02",
    "REQ-0.35.0-01-03",
    "REQ-0.35.0-01-04",
    "REQ-0.35.0-01-05",
    "REQ-0.35.0-01-06",
    "REQ-0.35.0-01-07",
    "REQ-0.35.0-01-08",
    "REQ-0.35.0-02-01",
    "REQ-0.35.0-02-02",
    "REQ-0.35.0-02-03",
    "REQ-0.35.0-02-04",
    "REQ-0.35.0-02-05",
    "REQ-0.35.0-02-06",
    "REQ-0.35.0-02-07",
    "REQ-0.35.0-04-01",
    "REQ-0.35.0-04-02",
    "REQ-0.35.0-04-03",
    "REQ-0.35.0-04-04",
    "REQ-0.35.0-04-05",
    "REQ-0.35.0-04-06",
    "REQ-0.35.0-04-07",
    "REQ-0.35.0-05-01",
    "REQ-0.35.0-05-02",
    "REQ-0.35.0-05-03",
    "REQ-0.35.0-05-04",
    "REQ-0.35.0-05-05",
    "REQ-0.35.0-05-06",
    "REQ-0.35.0-05-07",
    "REQ-0.35.0-05-08",
    "REQ-0.35.0-05-09",
    "REQ-0.35.0-06-01",
    "REQ-0.35.0-06-02",
    "REQ-0.35.0-06-03",
    "REQ-0.35.0-06-04",
    "REQ-0.35.0-06-05",
    "REQ-0.35.0-06-06",
    "REQ-0.35.0-09-01",
    "REQ-0.35.0-09-02",
    "REQ-0.35.0-09-03",
    "REQ-0.35.0-09-04",
    "REQ-0.35.0-09-05",
    "REQ-0.35.0-09-06",
    "REQ-0.35.0-09-08",
    "REQ-0.35.0-09-09",
    "REQ-0.35.0-09-10",
    "REQ-0.35.0-09-11"
  ],
  "installed_cosmic_ray": false,
  "installed_mutmut": false,
  "live_tautological_scan_operations": 232,
  "test_quality_audit_errors": []
}
```

### Baseline and waiver history

The baseline fell overall782→280,but not monotonically:70→290 accompanied the August3 scanner correction. A lower baseline count alone cannot prove tests were strengthened;it can also follow scope correction. The history includes both additions and their explicit reverts.

| File | Commit | Date | Operations | Waiver files | Waiver slots |
|---|---|---|---|---|---|
| `data/tautological_test_baseline.json` | `32e031448dd5` | 2026-05-26 | 782 | 0 | 0 |
| `data/tautological_test_baseline.json` | `3119a3b37fcd` | 2026-05-27 | 765 | 0 | 0 |
| `data/tautological_test_baseline.json` | `625d5f8ccb45` | 2026-05-31 | 91 | 0 | 0 |
| `data/tautological_test_baseline.json` | `bf3cf4c6162b` | 2026-07-09 | 70 | 0 | 0 |
| `data/tautological_test_baseline.json` | `b456f4a21b47` | 2026-08-03 | 290 | 0 | 0 |
| `data/tautological_test_baseline.json` | `8016db3eb3b3` | 2026-08-15 | 290 | 0 | 0 |
| `data/tautological_test_baseline.json` | `d1862cdf1f82` | 2026-08-15 | 280 | 0 | 0 |
| `data/tautological_test_baseline.json` | `65001830f74b` | 2026-08-29 | 280 | 0 | 0 |
| `data/tautological_test_waivers.json` | `32e031448dd5` | 2026-05-26 | 0 | 0 | 0 |
| `data/tautological_test_waivers.json` | `3119a3b37fcd` | 2026-05-27 | 0 | 2 | 3 |
| `data/tautological_test_waivers.json` | `e2c569c894b1` | 2026-09-05 | 0 | 3 | 6 |
| `data/tautological_test_waivers.json` | `9a104b91c1d0` | 2026-09-05 | 0 | 2 | 3 |
| `data/tautological_test_waivers.json` | `c13fda33fffe` | 2026-09-12 | 0 | 3 | 5 |
| `data/tautological_test_waivers.json` | `4eba5489d315` | 2026-09-12 | 0 | 2 | 3 |

### AST and manual measurements

Read all 600 source test methods in 26 pilot test modules (ledger-corrections whole file read by the controls reviewer), then read the final random sample of300 other method bodies plus helper/subject context needed to certify findings. Source census:10,747 explicitly declared methods; inherited unittest executions are a different count. Pilot closure combines AST imports (including constant import_module calls) and four command-facade selector modules. It is not a proof that every indirect importer in the repository was found.

Sample protocol: original Random(20260924).sample(sorted eligible frame,300); after adding4 pilot modules, remove6 overlapping sample methods and fill6 using Random(20260925).sample(sorted remaining eligible frame excluding retained294). Final eligible frame10,147. Manifest stores every method, both seeds, both frame hashes and source digests. This produces a uniform final sample on the expanded eligible frame.

Confirmed sample defect rate: 1/300 = 0.33% (sample n=300). This is the rate of certified D1-D8 defects found during this review, not an estimate that all unflagged methods are effective and not a mutation score.

- tests/test_adversarial_validation_gate.py:731 `TestCrossVendorClaimRequiresReceipt.test_human_degraded_floor_remains_exempt` — D7: Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:201 `TestStep4bTierBindingGate.test_human_floor_needs_no_fallback_reason`.

`tautological_tests.py` already recognizes filesystem-shaped content echo operations and literal assertions against that content (partial D6), then baseline/waiver drift. Those already-detected operation classes are excluded from the new semantic defect count. It is not a generic literal-mirroring detector. `test_shape.py` inventories output-form tests lacking a declared disposition and can surface some surface-only tests; it does not prove their semantic quality. D1,D2,D3,D4,D5,D7,D8 remain. No new D6 claim is made from merely matching text.

Command: `UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/env/bin/python python /private/tmp/gzkit-test-audit-20260924/manual/refine_ast.py`

```json
{
  "source_test_methods": 10747,
  "d3_only_weak_assertion_syntax": 823,
  "d4_no_direct_assertion": 189,
  "d4_resolved_local_assertion_helpers": 111,
  "d4_no_direct_or_resolved_local_helper": 78,
  "d5_any_controlled_assertion": 878,
  "d5_if_try_except_assertion": 109,
  "d5_after_return_assertion_methods": 0,
  "d5_skip_decorated_methods": 20,
  "d5_runtime_skip_methods": 7,
  "setup_more_than_20_one_direct_assertion": 148
}
```

`ast_refined.log`, `ast_refined.json`, and D3/D4/D5 candidate JSON files retain full file:line/name inventories. The scoped pass excludes nested specimen functions and recognizes self.fail. D4 resolves same-module helpers recursively, including local base classes; imported assertion helpers remain unresolved candidates. An allowed non-raising call or successful schema validation is an implicit behavior oracle, so absence of an assert spelling alone is not a defect. Conditions, loops, skips and try blocks are reviewed as control flow, never assumed to be vacuous.

The comparable crude scan counted826 weak-only methods and212 methods with no assert-prefixed call; it counts nested assertions and misses self.fail. Those are different definitions from the refined823/189. The historical822/117 figures therefore cannot be carried forward unchanged.

Command: `UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python /private/tmp/gzkit-test-audit-20260924/manual/probes.py`

Full output: `manual/probes.log` and `manual/probes.json`. Output: constant test success with0 production calls; empty-result scanner substitution success with1 replacement call; waiver fixture paths=[] and success. The later report/exception probes in that log changed unrelated behavior and do not support defects; their candidate findings were withdrawn. Matched-interface probes in manual/d8_reassessment_probes.json show baseline success and one assertion failure for each of the four tests when its actual public contract changes. These targeted runtime fault injections are additional audit experiments, not cosmic-ray mutants and not included in its score.

```text
$ uv run --no-project --python <audit-interpreter> python manual/finalize.py
{
  "confirmed_defective_tests": 21,
  "confirmed_by_primary_class": {
    "D3": 1,
    "D5": 1,
    "fixture": 1,
    "D7": 18
  },
  "duplicate_groups": 18,
  "sample_n": 300,
  "sample_confirmed_defects": 1,
  "sample_defect_rate_percent": 0.3333333333333333,
  "pilot_read_methods": 600,
  "pilot_read_files": 26
}
```

The manual findings comprise 18 D7 duplicates, one D3 constant assertion, one D5 vacuous assertion, and one empty fixture outside D1–D8. The historical/current command-count finding adds one independently demonstrated weakened oracle: 22 disposition rows in total. There are no certified D8 defects after reviewing the governing contracts; no D8 deletion is recommended. Counts of syntax candidates are not added to these semantic findings.

### Test-shape advisories

```text
$ uv run gz test-shape --json
{
  "tautological_operations": 232,
  "by_disposition": {
    "convert": 193,
    "replace-with-ledger": 13,
    "fold-to-validator": 26
  },
  "output_assertions": 1175,
  "undeclared_count": 1112,
  "exit_status": 0
}
```

There are 232 operation advisories and 1,112 undeclared output assertions among 1,175 output assertions. They stop nothing. Appendix E records every open advisory item. These are open classification/review defects against the declaration policy, not 1,344 proved ineffective tests: an operation is not a test, items overlap, and missing metadata does not prove a missing behavioral oracle. This is a deliberate correction to the request’s proposed inference.

### Coverage with branches enabled

```text
$ uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-branch --coverage-source src/gzkit
Running 672 test suites (10747 total tests) across 10 workers
Ran 10747 tests in 205.382s
FAILED (failures=1, skipped=4)
TOTAL                                                                           54554   6348  18922   2478    86%
```

Coverage test-command exit_status=1; elapsed=225.707 seconds. Scratch COVERAGE_RCFILE changes branch=false to branch=true; repository configuration is unchanged. Export: `uv run coverage json -o <scratch>/branch-coverage.json`, exit 0. Percentages below use separate line and branch denominators; coverage.py’s combined percent is not labeled line coverage.

This instrumented run is not green. `tests.governance.test_stage4_packet.TestExitStatus.test_a_sequenced_verifier_is_refused_on_this_surface_too` failed at line 330: it expected an “exit status” blocker, but received `Command timed out after 120s: uv run gz check > log 2>&1; tail -6 log`. The production verifier replays before classifying blockers (`src/gzkit/governance/stage4_packet.py:368–399`). The measurement ran alongside mutation workers; concurrency causation was not proved. The failure and coverage are retained as observed, without claiming a production defect or silently treating export exit 0 as test success. The earlier canonical ARB run is the green unit result.

| Scope | Lines hit / statements | Line % | Branches hit / total | Branch % |
|---|---|---|---|---|
| ALL | 48206/54554 | 88.36 | 15076/18922 | 79.67 |
| (root) | 11712/12656 | 92.54 | 3710/4330 | 85.68 |
| airlock | 217/220 | 98.64 | 23/24 | 95.83 |
| arb | 618/710 | 87.04 | 175/242 | 72.31 |
| chores | 617/942 | 65.50 | 212/402 | 52.74 |
| cli | 1644/1698 | 96.82 | 152/180 | 84.44 |
| commands | 14775/17809 | 82.96 | 4813/6594 | 72.99 |
| complexity | 1053/1161 | 90.70 | 232/296 | 78.38 |
| content | 1586/1642 | 96.59 | 461/498 | 92.57 |
| core | 445/474 | 93.88 | 101/124 | 81.45 |
| doc_coverage | 523/577 | 90.64 | 202/250 | 80.80 |
| eval | 429/460 | 93.26 | 81/96 | 84.38 |
| flags | 256/259 | 98.84 | 72/74 | 97.30 |
| foundation | 501/603 | 83.08 | 165/226 | 73.01 |
| governance | 8658/9561 | 90.56 | 3053/3574 | 85.42 |
| hooks | 1065/1226 | 86.87 | 419/524 | 79.96 |
| insights | 283/328 | 86.28 | 60/74 | 81.08 |
| justify | 625/747 | 83.67 | 186/260 | 71.54 |
| knowledge | 66/71 | 92.96 | 10/12 | 83.33 |
| models | 230/234 | 98.29 | 33/36 | 91.67 |
| mx | 455/489 | 93.05 | 90/118 | 76.27 |
| ontology | 654/702 | 93.16 | 138/174 | 79.31 |
| personas | 230/258 | 89.15 | 97/118 | 82.20 |
| reporter | 78/80 | 97.50 | 26/28 | 92.86 |
| rules | 379/420 | 90.24 | 160/192 | 83.33 |
| schemas | 12/12 | 100.00 | 0/0 | N/A |
| skills | 191/217 | 88.02 | 58/80 | 72.50 |
| templates | 101/104 | 97.12 | 29/30 | 96.67 |
| validate_pkg | 614/695 | 88.35 | 264/306 | 86.27 |
| validators | 189/199 | 94.97 | 54/60 | 90.00 |

Packages are first directories below src/gzkit; root modules are grouped as (root). unittest-parallel instruments discovery and worker processes, but arbitrary CLI subprocesses have no automatic coverage startup hook. Missing measured lines are therefore not proof no test reaches them. Executed lines are not proof of an assertion about their result.

### Mutation pilot

Cosmic Ray 8.7.0 ran under Python 3.13.15 with the locked gzkit dependencies in a scratch environment. Installed CLI help, config and runner source were read, alongside the [official introduction](https://cosmic-ray.readthedocs.io/en/latest/tutorials/intro/) and [concepts](https://cosmic-ray.readthedocs.io/en/latest/concepts.html). Installed-version behavior governs this audit: a test-command timeout is stored as KILLED with output "timeout", so this report separates it as timed out. No pytest or mutmut was run.

All nine original baselines and every shard baseline passed before mutation. Original jobs were paused, then pending jobs partitioned across isolated copies; original job identities and specs were retained. The test command is unittest on direct AST importers, literal dynamic importers, plus explicit command-facade selectors. Each process imports the target from its own copy. No .pyc files were present in checked copies. The scratch sitecustomize redirects unittest stderr to stdout because this Cosmic Ray runner retains stdout only; it changes no production behavior or assertions.

| Module | Mutants | Tests | Killed | Survived | Incompetent | Timed out | Survival % (n) | FAIL without ERROR |
|---|---|---|---|---|---|---|---|---|
| covers | 247 | 134 | 163 | 84 | 0 | 0 | 34.01% (n=247) | 48 |
| mutation_witness | 336 | 43 | 245 | 90 | 0 | 1 | 26.79% (n=336) | 164 |
| red_parity | 164 | 121 | 114 | 50 | 0 | 0 | 30.49% (n=164) | 67 |
| red_witness | 355 | 44 | 204 | 151 | 0 | 0 | 42.54% (n=355) | 98 |
| req_coverage | 46 | 24 | 28 | 18 | 0 | 0 | 39.13% (n=46) | 11 |
| tautological_tests | 580 | 65 | 239 | 341 | 0 | 0 | 58.79% (n=580) | 78 |
| test_shape | 117 | 13 | 50 | 67 | 0 | 0 | 57.26% (n=117) | 22 |
| validate_commit_trailers | 59 | 46 | 38 | 19 | 2 | 0 | 32.20% (n=59) | 27 |
| verifier_pipe_gate | 1130 | 110 | 554 | 573 | 0 | 3 | 50.71% (n=1130) | 272 |
| TOTAL | 3034 | 600 | 1635 | 1393 | 2 | 4 | 45.91% (n=3034) | 787 |

Survival denominator is every generated mutant, including separate timeout/incompetent outcomes. Raw killed means nonzero exit, including import errors, syntax errors and test setup failures. “FAIL without ERROR” only classifies unittest output; even such a failure can be an assertion about a failed subprocess import. It is not automatically a semantic guard kill. This is a diagnostic with no score floor and no unreviewed equivalent-mutant exclusions.

Per-test attribution intersects parsed failure IDs with that target’s baseline test IDs, excluding nested fixture-run names. The last outer unittest summary supplies the error count. Two incompetent trailer mutants failed inside Cosmic Ray’s ExceptionReplacer before test execution (`AttributeError: PythonNode has no attribute value`, source lines 47 and 139); they are mutation-application failures, not evidence for or against the tests.

```text
{
  "outside_annotations": {
    "killed": 1613,
    "survived": 568,
    "timed_out": 4,
    "incompetent": 2
  },
  "postponed_annotation_overlap": {
    "survived": 825,
    "killed": 11
  },
  "annotation_overlap": {
    "killed": 11
  }
}
```

Annotation overlap is measured against original AST spans. Many survivors alter postponed type annotations; overlap alone neither proves equivalence nor proves missing tests. The complete list marks these cases for review rather than treating them as runtime faults.

### Two reviewed, non-equivalent survivors

The 24 selected req_coverage tests pass both faults. For a file containing decorators for REQs 01, 02 and 03, querying REQ 02 should yield only Case.test_b. Changing `!=` to `<` at req_coverage.py:130 returns test_b and test_c; changing `continue` to `break` at line 131 returns no tests. A separate audit unittest passes the unmodified code and fails each fault. No source or test fix was retained.

| Mutant ID | Receipt | Operator | Baseline / mutant discriminator |
|---|---|---|---|
| e8a831055b894a4a95d00c0f31ea4a72 | [src/gzkit/governance/req_coverage.py:130](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:130) | core/ReplaceComparisonOperator_NotEq_Lt | exit 0 / exit 1; extra Case.test_c |
| 398ef57bf968408593f6aa6d58de0ed3 | [src/gzkit/governance/req_coverage.py:131](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:131) | core/ReplaceContinueWithBreak | exit 0 / exit 1; empty result |

```text
$ uv run --no-project --python <audit-interpreter> python run_discriminator.py
[
  {
    "label": "baseline",
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "python",
      "/private/tmp/gzkit-test-audit-20260924/req_discriminator.py"
    ],
    "exit_status": 0,
    "output": "test_exact_req_filter_keeps_searching_after_unrelated_reference (__main__.RequirementFiltering.test_exact_req_filter_keeps_searching_after_unrelated_reference) ... ok\n\n----------------------------------------------------------------------\nRan 1 test in 0.001s\n\nOK\n"
  },
  {
    "label": "e8a831055b894a4a95d00c0f31ea4a72",
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "python",
      "/private/tmp/gzkit-test-audit-20260924/req_discriminator.py"
    ],
    "exit_status": 1,
    "output": "test_exact_req_filter_keeps_searching_after_unrelated_reference (__main__.RequirementFiltering.test_exact_req_filter_keeps_searching_after_unrelated_reference) ... FAIL\n\n======================================================================\nFAIL: test_exact_req_filter_keeps_searching_after_unrelated_reference (__main__.RequirementFiltering.test_exact_req_filter_keeps_searching_after_unrelated_reference)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/tmp/gzkit-test-audit-20260924/req_discriminator.py\", line 22, in test_exact_req_filter_keeps_searching_after_unrelated_reference\n    self.assertEqual([r.qualified_name for r in actual],['Case.test_b'])\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: Lists differ: ['Case.test_b', 'Case.test_c'] != ['Case.test_b']\n\nFirst list contains 1 additional elements.\nFirst extra element 1:\n'Case.test_c'\n\n- ['Case.test_b', 'Case.test_c']\n+ ['Case.test_b']\n\n----------------------------------------------------------------------\nRan 1 test in 0.002s\n\nFAILED (failures=1)\n"
  },
  {
    "label": "398ef57bf968408593f6aa6d58de0ed3",
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "python",
      "/private/tmp/gzkit-test-audit-20260924/req_discriminator.py"
    ],
    "exit_status": 1,
    "output": "test_exact_req_filter_keeps_searching_after_unrelated_reference (__main__.RequirementFiltering.test_exact_req_filter_keeps_searching_after_unrelated_reference) ... FAIL\n\n======================================================================\nFAIL: test_exact_req_filter_keeps_searching_after_unrelated_reference (__main__.RequirementFiltering.test_exact_req_filter_keeps_searching_after_unrelated_reference)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/tmp/gzkit-test-audit-20260924/req_discriminator.py\", line 22, in test_exact_req_filter_keeps_searching_after_unrelated_reference\n    self.assertEqual([r.qualified_name for r in actual],['Case.test_b'])\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: Lists differ: [] != ['Case.test_b']\n\nSecond list contains 1 additional elements.\nFirst extra element 0:\n'Case.test_b'\n\n- []\n+ ['Case.test_b']\n\n----------------------------------------------------------------------\nRan 1 test in 0.002s\n\nFAILED (failures=1)\n"
  }
]
```

### Full-suite follow-up for two req_coverage survivors

A separate fresh clone pinned to `5d9885a08c438b0aa546716b20a181c55342612e` was prepared to test whether the two confirmed pilot survivors also survive the complete canonical unit selection. `uv sync --frozen` succeeded in its own `.venv`; the installed unittest-parallel CLI accepted the canonical selection flags. The environment removed `VIRTUAL_ENV`, `UV_PROJECT_ENVIRONMENT`, `UV_NO_SYNC`, and inherited `PYTHONPATH`; cache/tool paths were confined to scratch.

The required baseline failed, so **neither mutant was applied or run**. There is no full-suite survivor or kill conclusion. The run/environment cause of the timeout remains unresolved; no load-related cause was established. The experiment was stopped without retry or production changes.

Command, executed in the fresh copy:

```text
uv run unittest-parallel -t . -s tests --buffer
exit_status: 1
elapsed_seconds: 190.665
Ran 10747 tests in 182.683s
FAILED (failures=1, skipped=4)
```

The one failure was `tests.governance.test_stage4_packet.TestExitStatus.test_a_sequenced_verifier_is_refused_on_this_surface_too`, assertion at `tests/governance/test_stage4_packet.py:330`. It expected a blocker containing `exit status`; the observed blocker was:

```text
Command timed out after 120s: uv run gz check > log 2>&1; tail -6 log
```

The pipeline text above is the existing test fixture's command, reproduced as failure evidence. The audit wrapper captured the verifier's complete output and real exit status without a pipe.

Receipts: `/private/tmp/gzkit-test-audit-20260924/full-survivor-check/baseline.log:4` names the test, line10 gives the assertion failure, line13 the test count, and line15 the outcome. `baseline.json` records the command, exit status and elapsed time; `conclusion.json` records zero applied/run mutants. Pending jobs were `e8a831055b894a4a95d00c0f31ea4a72` (line130, NotEq→Lt) and `398ef57bf968408593f6aa6d58de0ed3` (line131, Continue→Break).

Before cleanup, `git diff --exit-code -- src/gzkit/governance/req_coverage.py` returned0. The new repository copy was then deleted; logs and JSON evidence remain outside it. Cleanup receipt: `/private/tmp/gzkit-test-audit-20260924/full-survivor-check/cleanup.log:1`.

### Prior hand-authored sweep claims and the comparison boundary

Read the claims below as dated records, not refreshed test results. The audit read the reachable commit messages and the cited handoffs at `5d9885a08c438b0aa546716b20a181c55342612e`; it did not execute the handoff's mutating example against the source tree. A generated mutant surviving in the same module is not a contradiction by itself. Contradiction requires the same behavioral guard and materially equivalent substitution, comparable tests and source revision, and a valid run. Different operators expose different properties.

| Pilot target | Dated prior claim actually located/read | Guard specificity and comparison allowed |
|---|---|---|
| `src/gzkit/mutation_witness.py` | Commit `df0c238790b3c218450159c240cc21d453254963` (GHI #963); `.gzkit/handoffs/20260906T120509Z-session-close-963-landed-968-filed-888-next.md:307` records `killed=6 survived=0 invalid=0 inconclusive=0 conclusive=True`. | Six named guards: absent-target, no-op, unimportable, attribution, isolation, baseline. That handoff at lines 245–255 also retains an exact executable substitution: `env["PYTHONPYCACHEPREFIX"] = str(pycache_prefix)` → `pass`, expected `test_each_mutation_runs_with_its_own_bytecode_cache`, observed `killed` and `conclusive: True`. Current target is line 223; current test is `tests/test_mutation_witness.py:195`. This is the strongest candidate for an exact comparison. The other five labels are not an exact saved substitution roster. |
| `src/gzkit/verifier_pipe_gate.py` | Commit `772d4348d4a8f9a9ba2d75a5e1c16a5756601592` (GHI #940): 7 killed, 0 survived/invalid/inconclusive, conclusive. Commit `b628d0f1087e2c499b649123c0cbfd161bb6c69f` (#970): 4/0/0/0 conclusive. Commit `6b3e71a7c663fbe533f5e1b16aff97db1120bfde` (#971): 7/0/0/0 conclusive. Commit `7d113edbd05f435a6bd4149168ffc1603ee95ee3` (#1008): 26/0/0/0 conclusive, also `.gzkit/handoffs/20260915T094830Z-fix-1008-grouped-verifier.md:15`. | #940 names first-pass survivors `errexit-operand-too-loose` and `trailing-separator-false-positive`, then says isolating tests were added. #970 names `or-else-arm-removed`, `errexit-escape-too-wide`, `errexit-protects-background-too`, `arm-not-distinguished`. The latter records that two targets became invalid during helper extraction and the sweep was rerun against corrected targets. These labels support a semantic comparison with `_sets_errexit` and `_replacement_arm`; they do not identify the exact replacement bytes. No exact 26-case roster was located in the read commit/handoff. |
| `src/gzkit/red_witness.py` | Commit `ca5670e50c14ef834e2b32bacbb9e50a187ef84d` (GHI #849): witness 4 killed/0 survived; ordering 2/0; all conclusive. `.gzkit/handoffs/20260906T155304Z-session-close-970-849-landed-969-971-open-946-next.md:120` repeats these counts. | Named guards: `error-counts-as-red-on-any-base`, `void-run-reported-as-conclusive`, `landed-work-never-reconstructs`, `base-is-the-introducing-commit-not-its-parent`, `head-tried-before-reconstruction`, `premise-not-rechecked-on-the-reconstructed-base`. The last survived its initial sweep and prompted the test now at `tests/test_red_witness.py:565`. Current corresponding production predicates: `RedWitness.is_red` at 102–104, `is_conclusive` at 116–118, introducing parent at 197, `_resolve_base` at 333–340. Labels support semantic comparison, not exact byte identity. |
| `src/gzkit/governance/trust_audits/red_parity.py` | Same `ca5670e50c14ef834e2b32bacbb9e50a187ef84d` and handoff line 120: parity 2 killed/0 survived, conclusive. | `reconstructed-error-banked-as-witness`, `missing-provenance-read-as-reconstructed`. These map to `_is_void_witness`, current lines 64–68: exclude reconstructed errors; default missing provenance to `working-tree`. Exact source replacements were not retained in the read record. |
| `src/gzkit/test_shape.py` | Commit `bf3cf4c6162b6def5e862cc4b5f511a93fcb9b20` (GHI #571, July 9): four mutants killed after pycache purges. `.gzkit/insights/agent-insights.jsonl:330` records baseline OK / M1–M4 killed / restored OK. | The one exact mutation described in that insight is `_ADVISORY_EXIT = 0` → `= 1` in **`src/gzkit/commands/test_shape.py`**, a different module from this pilot's `src/gzkit/test_shape.py`. The four-case roster is not specified there. Do not claim a contradiction between that CLI exit mutation and survivors in the inventory engine. This predated the GHI #963 harness; the record explicitly describes manual cache purging. |
| `src/gzkit/tautological_tests.py` | No module-specific mutation kill claim located in the read module commit history, relevant tests and mutation-related retained artifact candidates. | Ordinary scans, fixture tests and unrelated mutations mentioned by co-changing commits are not a prior sweep of this target. |
| `src/gzkit/governance/req_coverage.py` | No module-specific mutation kill claim located in the same inspected channels. | Do not substitute passing `@covers` evidence for a mutation result. |
| `src/gzkit/commands/covers.py` | No module-specific mutation kill claim located in the same inspected channels. | Some history mentions production fail-closed regression checks and REQ proof, but not a comparable target mutation roster. |
| `src/gzkit/commands/validate_commit_trailers.py` | No module-specific mutation kill claim located in the same inspected channels. | A cross-platform subprocess edit described as a “sweep” is source maintenance, not mutation-test evidence. |

The three saved ARB receipts cited alongside the September 6 sweeps were read and are **unit-suite receipts**, all `schema=gzkit.arb.step_receipt.v1`, `step.name=unittest`, command `uv run unittest-parallel -t . -s tests --buffer`, `exit_status=0`, `git.dirty=true`:

| Retained receipt | Actual output | What it establishes |
|---|---|---|
| `artifacts/receipts/arb-step-unittest-8b99fd0a838749448542b94483b6739b.json:1` | 9,519 tests, OK (skipped=4), 2026-09-06T11:55:46Z | A green suite on the recorded dirty tree; no mutant roster or per-guard outcomes. |
| `artifacts/receipts/arb-step-unittest-971e5712af4a480a91063ed81ae7f577.json:1` | 9,569 tests, OK (skipped=4), 2026-09-06T15:14:21Z | Same limit. |
| `artifacts/receipts/arb-step-unittest-03001411e89c41d7ba0dae66f4604f95.json:1` | 9,587 tests, OK (skipped=4), 2026-09-06T15:36:49Z | Same limit. |

This is consistent with the **historical** scope disclosure in `docs/governance/advisory-rules-audit.md:200` (row 89): an ad-hoc sweep has no automatic receipt proving that it used the harness. Later acceptance-proof records do retain per-REQ mutation results for their own targets; this audit does not generalize the September 6 disclosure into a claim that no mutation artifacts exist anywhere.

Reproducible search/read procedure: `git log 5d9885a08c438b0aa546716b20a181c55342612e --format='%H%n%B' -- <each of the nine target paths>` followed by full reads of relevant commit messages; `rg -l --hidden -i 'mutation.sweep|run_mutation_sweep|conclusive.*killed|killed.*conclusive' artifacts .gzkit/evidence --glob '*.json' --glob '*.md' --glob '*.txt'` found 45 candidate files; none of those 45 contained any of the nine target name strings. This is a bounded candidate search, not proof that every retained artifact lacks a mutation record. The handoffs, insights and the three receipts above were then read. Source comments and current tests were read to map named guards; no unretained `/tmp` session files or external issue comments were examined.

### Executed pilot versus historical hand-authored sweeps

**No conflict established in the compared cases.** The sole fully specified historical substitution—deleting `env["PYTHONPYCACHEPREFIX"] = str(pycache_prefix)` at current `mutation_witness.py:223`—is absent from all 336 generated specs for that module. There is no job ID for that deletion, so this pilot neither reproduces nor contradicts the historical isolation kill. No extra mutation was run for this comparison.

The rows below compare named behavioral guards with generated changes that break the same property. Because the older records retain guard labels rather than exact replacement bytes, these are **semantic corroborations with different operators, not exact historical replays**. Every listed current job is `worker_outcome=NORMAL`, `test_outcome=KILLED`, and its saved output contains the stated `FAIL` / `AssertionError` witness (not merely a non-zero exit). Some jobs also produced errors in other tests; the listed assertion supplies the relevant witness.

| Earlier named guard | Current job and substitution | Relevant observed assertion | Disposition |
|---|---|---|---|
| GHI #963 no-op guard | `bb02cbb27df04fc282e8ed44e5fd1771`; mutation_witness.py:267; `mutated == original` → `!=` | `test_a_no_op_mutation_is_invalid`: AssertionError: 'inconclusive' != 'invalid' | Same guard exercised; killed; no conflict. |
| GHI #963 baseline guard | `41719699d913423cad6d929461ea09d9`; mutation_witness.py:352; `baseline.returncode == 0` → `!= 0` | `test_a_red_baseline_makes_every_mutation_inconclusive`: AssertionError: True is not false | Same guard exercised; killed; no conflict. |
| GHI #849 error-counts-as-red-on-any-base | `361ce7f4857a473fa95920930e3bdf25`; red_witness.py:104; error/provenance `and` → `or` | `test_an_error_on_a_reconstructed_base_is_void_not_red`: AssertionError: True is not false : an unrelated ImportError is not falsifiability | Same guard exercised; killed; no conflict. |
| GHI #849 void-run-reported-as-conclusive | `59c7bf1ea11e4959a047df2ec5656d54`; red_witness.py:116; negate not-applicable branch condition | `test_a_not_applicable_run_is_never_conclusive`: AssertionError: True is not false | Same guard exercised; killed; no conflict. |
| GHI #849 premise-not-rechecked-on-reconstructed-base | `ab40e6b65f2040c18822f8ccdcc52a00`; red_witness.py:334; reconstructed-present/withheld-premise `and` → `or` | `test_a_test_only_commit_yields_no_verdict_rather_than_a_false_none`: AssertionError: 'none' != 'not-applicable' | Same guard exercised; killed; no conflict. |
| GHI #849 reconstructed-error-banked-as-witness | `a7ff9b4170ab45c2af3b2fae3c7d425f`; red_parity.py:68; provenance `== "reconstructed"` → `!=` | `test_an_error_on_a_reconstructed_base_does_not_satisfy_the_gate`: AssertionError: 0 != 1 | Same guard exercised; killed; no conflict. |
| GHI #970 arm-not-distinguished | `5747d4e97f5b488bae1e76c12025f3f5`; verifier_pipe_gate.py:639; `list_end == _OR_ELSE` → `!=` | `test_the_or_else_arm_names_the_branch_not_the_pipe_or_the_sequence`: AssertionError: wrong recovery prose (“not the last statement”) for the OR-else arm | Same guard exercised; killed; no conflict. |
| GHI #940 errexit-operand-too-loose | `70012d3180ef48099ff54c76bd5f8456`; verifier_pipe_gate.py:369; `_sets_errexit` fallback `False` → `True` | `test_pipefail_alone_does_not_enable_errexit`: AssertionError: None != 'gz check' | Same guard exercised; killed; no conflict. |

| Surviving or otherwise unmatched case | Evidence | Comparison disposition |
|---|---|---|
| Explicit-base provenance inversion | `c763492b17be4e95b6d515f77151b5e5`, `red_witness.py:332`, `base_commit == head` → `!=`, `SURVIVED/NORMAL`, no failing tests. | Different branch from the six historical #849 guards: this handles the caller-supplied explicit base. Does not contradict their kills; merits its own semantic review. |
| Introducing index changes | `59a13def88b94a648a7c959847b3199e`, `red_witness.py:197`, `commits[0]` → `commits[-1]`, `SURVIVED/NORMAL`, no failing tests. | The earlier guard was “introducing commit instead of its parent”; this mutant retains the parent `^` and changes which introducing commit is chosen. Different change; no conflict established. |
| Broader lexical comparison in OR-else classifier | `8250023fc4074006b927b6e73744b872`, `verifier_pipe_gate.py:639`, `== _OR_ELSE` → `>= _OR_ELSE`, `SURVIVED/NORMAL`, no failing tests. | Does not remove the OR-else arm. A generated operator survivor is not evidence that the earlier arm-deletion kill was false. |
| Missing-provenance default | The historical #849 `red_parity` guard changes the line-67 default from `working-tree` to `reconstructed`; the generated roster has no mutation at that line. | No exact comparison available. |
| Test-shape four-mutant record | Only retained exact old substitution is `_ADVISORY_EXIT = 0` → `1` in `src/gzkit/commands/test_shape.py`, while pilot target is `src/gzkit/test_shape.py`. | Different module; not comparable. |
| Other totals and targets | #1008’s 26 kills and #971’s seven kills do not retain exact rosters in the read commit/handoff; no target-specific old sweep claim was located for tautological_tests, req_coverage, covers, or validate_commit_trailers. | Cannot conclude conflict from module-level survivor counts. |

Read-only extraction: SQLite connections use `file:<path>?mode=ro`. Specs/results were joined from each parent `pilot/<module>/session.sqlite` plus matching `shards/<module>-*/session.sqlite`, preserving job IDs. This comparison inspected completed individual results while other jobs were still running; it makes no final-population count claim. Full saved diffs, assertion blocks and DB origins are retained in `history/prior-sweep-comparable-jobs.json`; broader scoped snapshots are `history/prior-sweep-pilot-comparison.json`.

## 5. The twenty worst confirmed tests

These are the twenty highest-priority confirmed cases selected for review, not a numeric severity ranking. A duplicate can assert real behavior; its defect is redundant protection, unlike a constant or vacuous assertion. The full disposition table follows the survivor list.

| # | Test receipt | Class | Defect |
|---|---|---|---|
| 1 | [tests/test_doc_coverage.py:190](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:190) `TestDiscoverCommands.test_total_command_count` | weakened oracle | Accepts a list truncated from 136 discovered commands to 50, dropping 86; its REQ annotation concerns a six-surface CoverageReport rather than a minimum command count. git diff 9e539d0665^ 9e539d0665 -- tests/test_doc_coverage.py src/gzkit/cli/main.py; runtime counterexample in section 8. |
| 2 | [tests/governance/test_tautological_tests.py:29](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:29) `TestTautologicalTestModels.test_models_importable` | D3 | The entire executable body is assertTrue(True); it imports no model and exercises no production behavior. probes.json: constant assertion test passes with gzkit_calls=[]; source assertion at31. |
| 3 | [tests/governance/test_tautological_tests.py:316](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:316) `TestAstScanner.test_scanner_returns_list_of_operation_instances` | D5 | The sole assertion is inside iteration over scanner output; a scanner returning[] for two filesystem-operation fixtures executes zero assertions and passes. probes.json: injected scan_test_tree=[] called once; tests_run1, success=true. Also syntactic D3. |
| 4 | [tests/governance/test_tautological_tests.py:573](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:573) `TestSelfExemption.test_waivers_file_not_counted_in_scan` | fixture | The supposed waivers-file exemption test never writes a waiver file or any other file; it only scans an empty directory. probes.json: paths_present_at_scan=[[]], test passes. This is an unexercised premise, outside the literal D1-D8 classes. |
| 5 | [tests/commands/test_gates_frontmatter.py:141](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:141) `TestGate1FrontmatterIntegration.test_gate1_runs_to_completion` | D7 | Repeats the same behavior and inputs as tests/commands/test_gates_frontmatter.py:58 `TestGate1FrontmatterIntegration.test_gate1_passes_when_no_drift`. Same class, _quick_init/_coherent_adr helpers, argv and exit-code assertion; keep the method carrying both REQ anchors. |
| 6 | [tests/test_red_parity_audit.py:103](/Users/jeff/Documents/Code/gzkit/tests/test_red_parity_audit.py:103) `TestRedParity.test_weak_error_witness_passes` | D7 | Repeats the same behavior and inputs as tests/test_red_parity_audit.py:183 `TestVoidWitnessesDoNotCount.test_an_error_with_no_provenance_still_satisfies_it`. Both inherit _Project, write the same unproven error witness and assert the same parity result. |
| 7 | [tests/commands/test_mx_skill_alignment.py:45](/Users/jeff/Documents/Code/gzkit/tests/commands/test_mx_skill_alignment.py:45) `TestMxSkillAlignment.test_audit_skill_alignment_clean_on_live_tree` | D7 | Repeats the same behavior and inputs as tests/commands/test_skill_alignment_10verbs.py:56 `TestSkillAlignment10Verbs.test_audit_skill_alignment_clean_on_live_tree`. Same audit_skill_alignment function and repository root; same failure formatting; retain anchored 10-verbs test. |
| 8 | [tests/governance/test_brief_structure.py:121](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_structure.py:121) `TestBriefStructureModel.test_tasks_accepts_list_of_strings` | D7 | Repeats the same behavior and inputs as tests/governance/test_brief_structure.py:166 `TestTasksSchemaEnforcement.test_accepts_well_formed_formal_task_id`. Same BriefStructure constructor, _VALID_FIELDS and one identical formal TASK ID; same equality assertion. |
| 9 | [tests/governance/test_handoff_validation.py:190](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:190) `HandoffWorkContinuityScopeTests.test_malformed_adr_id_still_raises_when_supplied` | D7 | Repeats the same behavior and inputs as tests/governance/test_handoff_validation.py:104 `TestHandoffFrontmatter.test_invalid_adr_id_format_raises`. Identical helper payload and validation-error oracle; neither class alters its fixture. |
| 10 | [tests/governance/test_pointer_integrity.py:93](/Users/jeff/Documents/Code/gzkit/tests/governance/test_pointer_integrity.py:93) `TestPointerResolves.test_resolved_pointer_in_rules_dir` | D7 | Repeats the same behavior and inputs as tests/governance/test_pointer_integrity.py:222 `TestPointerResolvesRelativeToSource.test_relative_pointer_from_nested_rule_resolves`. Identical temporary nested rule, pointer, destination and audit/errors-empty assertion. |
| 11 | [tests/governance/test_stage4_packet.py:251](/Users/jeff/Documents/Code/gzkit/tests/governance/test_stage4_packet.py:251) `TestExitStatus.test_a_verdict_idiom_that_discloses_its_branch_is_accepted` | D7 | Repeats the same behavior and inputs as tests/governance/test_stage4_packet.py:428 `TestOrElseConcealment.test_the_verdict_idiom_survives_because_its_left_side_runs_no_verifier`. Same verdict-idiom command and validator helper; no differing setup. |
| 12 | [tests/test_pipeline_dispatch.py:615](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_dispatch.py:615) `TestStage2DispatchLoopContract.test_empty_plan_produces_empty_state` | D7 | Repeats the same behavior and inputs as tests/test_pipeline_dispatch.py:315 `TestCreateDispatchState.test_empty_tasks_creates_empty_state`. Same create_dispatch_state arguments including empty task list, same three field assertions, no differing setup. |
| 13 | [tests/test_config.py:332](/Users/jeff/Documents/Code/gzkit/tests/test_config.py:332) `TestGatesRemoved.test_gates_in_config_rejected` | D7 | Repeats the same behavior and inputs as tests/test_config_gates_removal.py:83 `TestConfigGatesFieldRejected.test_full_test_suite_passes`. Both instantiate the same GzkitConfig with the same forbidden gates field and expect ValidationError; keep anchored method and rename it to the behavior it tests. |
| 14 | [tests/test_manifest_v2.py:121](/Users/jeff/Documents/Code/gzkit/tests/test_manifest_v2.py:121) `TestManifestV2Personas.test_v2_manifest_with_personas_passes_validation` | D7 | Repeats the same behavior and inputs as tests/test_manifest_v2.py:135 `TestManifestV2Validation.test_v2_manifest_passes_validation`. Same generated v2 manifest, tempfile serialization and validation/errors-empty assertion; no persona-specific discriminator in repeated method. |
| 15 | [tests/test_lifecycle.py:22](/Users/jeff/Documents/Code/gzkit/tests/test_lifecycle.py:22) `TestTransitionTables.test_all_expected_content_types_have_tables` | D7 | Repeats the same behavior and inputs as tests/test_core_lifecycle.py:47 `TestCoreTransitionTables.test_all_content_types_present`. Same TRANSITION_TABLES object re-exported by src/gzkit/lifecycle.py:19 and separately identity-tested at tests/test_core_lifecycle.py:81; same six-key expected set. |
| 16 | [tests/test_adr_governance_confirm.py:35](/Users/jeff/Documents/Code/gzkit/tests/test_adr_governance_confirm.py:35) `TestGovernanceSurfaceExists.test_adr_audit_check_importable` | D7 | Repeats the same behavior and inputs as tests/test_adr_audit_ledger_confirm.py:21 `TestAuditLedgerSurfaceExists.test_adr_audit_check_importable`. Same function import and callable predicate with no fixture. Merge the two metadata REQ anchors if retaining the smoke check. |
| 17 | [tests/test_adversarial_validation_gate.py:731](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:731) `TestCrossVendorClaimRequiresReceipt.test_human_degraded_floor_remains_exempt` | D7 | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:201 `TestStep4bTierBindingGate.test_human_floor_needs_no_fallback_reason`. Same _ReceiptFixture, same global _enforce helper and identical degraded-human-only/human/None inputs. Both assert successful non-raising invocation implicitly. |
| 18 | [tests/test_adversarial_validation_gate.py:712](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:712) `TestCrossVendorClaimRequiresReceipt.test_proven_cross_vendor_claim_passes` | D7 | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:244 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_1_with_cross_vendor_name_passes_on_proof`. Same _ReceiptFixture, same _codex_receipt payload and tier1/codex/fallback=None arguments; same non-raising oracle. |
| 19 | [tests/test_adversarial_validation_gate.py:721](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:721) `TestCrossVendorClaimRequiresReceipt.test_tier_2_fallback_remains_usable_without_any_receipt` | D7 | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:266 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_2_with_reason_passes`. Same _ReceiptFixture and tier2/Claude/fallback-reason inputs; same non-raising oracle. |
| 20 | [tests/test_ledger_corrections.py:961](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_corrections.py:961) `TestProducerAuditReadsHelperBuiltPayloads.test_the_runtime_scan_over_this_repository_is_clean` | D7 | Repeats the same behavior and inputs as tests/test_ledger_corrections.py:576 `TestProducerContractParity.test_no_producer_writes_an_undeclared_field`. Controls agent whole-file review: same audit_producer_fields(repository root), same error projection and empty-list assertion; only assertion message differs. |

## 6. Survived mutants — complete list

Each row is a saved successful test-command outcome, keyed by Cosmic Ray job ID. Source line and occurrence belong to the pinned source and operator. This proves only that the declared selected tests did not reject that substitution. It does not prove “no test verifies that line.” `postponed` and `annotation` are source-span overlap flags, not equivalence decisions. Session databases and their hashes are in the evidence inventory; all survivors are printed here without truncation.

### covers — 84 survivors / 247 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| 29be92bb62b74dc290e5a0dae84dacfc | [src/gzkit/commands/covers.py:56](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:56) | core/NumberReplacer | 2 | runtime/source |
| 622e3cb0b4aa4197a66e466b68c4374f | [src/gzkit/commands/covers.py:56](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:56) | core/NumberReplacer | 3 | runtime/source |
| 4f8c5d60ab8548acb1c150666d0101ea | [src/gzkit/commands/covers.py:57](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:57) | core/NumberReplacer | 4 | runtime/source |
| c854c6d0397444128e3e46e1509f804f | [src/gzkit/commands/covers.py:57](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:57) | core/NumberReplacer | 5 | runtime/source |
| c6375baaa56d4c68a3b95018242a9485 | [src/gzkit/commands/covers.py:58](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:58) | core/NumberReplacer | 6 | runtime/source |
| 4e71e918e12a4a839849d5bdc74902be | [src/gzkit/commands/covers.py:58](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:58) | core/NumberReplacer | 7 | runtime/source |
| 5ef5ff07e19a40aa8a9f78ff3273439f | [src/gzkit/commands/covers.py:69](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:69) | core/ZeroIterationForLoop | 0 | runtime/source |
| b98d0364dd96472ab7703e142805d211 | [src/gzkit/commands/covers.py:98](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:98) | core/NumberReplacer | 13 | runtime/source |
| c3acab779363402d983b46d8a77d279d | [src/gzkit/commands/covers.py:98](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:98) | core/AddNot | 2 | runtime/source |
| 2a3f988abf794d2a86a0bcc737e5ad40 | [src/gzkit/commands/covers.py:106](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:106) | core/ReplaceComparisonOperator_Eq_Lt | 0 | runtime/source |
| 8dcee2f3cef74f2683814cb5b574e397 | [src/gzkit/commands/covers.py:106](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:106) | core/ReplaceComparisonOperator_Eq_LtE | 0 | runtime/source |
| 0853a0b0e5234c9087d1b73237175ba9 | [src/gzkit/commands/covers.py:106](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:106) | core/NumberReplacer | 14 | runtime/source |
| d082a69e4da4460097cf7397ea4bac8f | [src/gzkit/commands/covers.py:106](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:106) | core/NumberReplacer | 15 | runtime/source |
| a24123e8677d4e36ad2ac04f0acfbcde | [src/gzkit/commands/covers.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:111) | core/AddNot | 4 | runtime/source |
| 9a9ab18cfc67414e9a234e41eeada591 | [src/gzkit/commands/covers.py:114](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:114) | core/NumberReplacer | 16 | runtime/source |
| d2cb7386b45e458c96e1489d5c4e2ffe | [src/gzkit/commands/covers.py:114](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:114) | core/NumberReplacer | 17 | runtime/source |
| 5f319e66b97946f08d40a67782e18e44 | [src/gzkit/commands/covers.py:115](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:115) | core/ZeroIterationForLoop | 1 | runtime/source |
| 327dbcd9dace48dc83bbb2fd491b6351 | [src/gzkit/commands/covers.py:123](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:123) | core/AddNot | 5 | runtime/source |
| 8fc23f2a09a647d4a961b230761e3934 | [src/gzkit/commands/covers.py:126](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:126) | core/NumberReplacer | 18 | runtime/source |
| 10bd0d2717d54f63924a770d8b40ac31 | [src/gzkit/commands/covers.py:126](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:126) | core/NumberReplacer | 19 | runtime/source |
| 0865dad6d4fa46f2afd3c99611cbcde1 | [src/gzkit/commands/covers.py:127](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:127) | core/ZeroIterationForLoop | 2 | runtime/source |
| fb49e39de4b2407a90e981b92b70b173 | [src/gzkit/commands/covers.py:148](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:148) | core/AddNot | 7 | runtime/source |
| 908d0f1e4bf54ea186bdf54987a73e36 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| 4a53ef68bf784985bbe3165867d605ae | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| d53ce5c07b26413aa63a37c9c87540bf | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| 1a85c83b2e74471c8e1c6d20ce88e8f7 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| eac6cf03c9ce4c4b885bb06b040e28a7 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| 80d938f0c8504ff6a69a63701cb7652e | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 615e8b916c4c412eb46fd3419acb2b43 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| f1781e83224f4fc5901f5183b9a9b8d9 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| f362f81ab57c4593a0297a8bfd4c6520 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| dea63fe9c4d54b019dc0af1ff6464141 | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 97b41acf97b6491d98570ad26f106cea | [src/gzkit/commands/covers.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:172) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| 67e9ede23e944003be0deb3efc619434 | [src/gzkit/commands/covers.py:173](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:173) | core/ReplaceFalseWithTrue | 0 | runtime/source |
| 00f75b76d78d4bb1a726e4f92d88978d | [src/gzkit/commands/covers.py:174](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:174) | core/ReplaceFalseWithTrue | 1 | runtime/source |
| b57b69812ab44027917f7c3db0234ab0 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Add | 1 | postponed |
| b2f6e422fa224761ad9256a7e0aff031 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_BitAnd | 1 | postponed |
| 051dfce75523478991408fdecca3a032 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_BitXor | 1 | postponed |
| 95dc3076afda46f88b4d80c70c49b52a | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Div | 1 | postponed |
| 5457f49769da41f99416b330a08ad779 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 1 | postponed |
| ac2e1eb0ff12450982d9781bd5333e0e | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_LShift | 1 | postponed |
| 43f9642de1d24f76892eefc3b56cd5a5 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Mod | 1 | postponed |
| f73178f6a6e7491ab7ea51ace2b833c1 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Mul | 1 | postponed |
| fa34f3b1c37e46e7ba36c700dc71f96d | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Pow | 1 | postponed |
| 0a6e9dcdf8e645d7bf180476c0a1a904 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_RShift | 1 | postponed |
| ea13d16e2eff47eea5fd4599c7081135 | [src/gzkit/commands/covers.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:175) | core/ReplaceBinaryOperator_BitOr_Sub | 1 | postponed |
| 7a5c7118990f47a3b1cdc9a3824a36e1 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Add | 2 | postponed |
| 25696953dc5649a98c4b50fc25a3c3ff | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_BitAnd | 2 | postponed |
| e185dffd374540fc9e63b4a69ca58871 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_BitXor | 2 | postponed |
| 6992c65407b74d3b9ccc0b3bb14c6e4d | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Div | 2 | postponed |
| 90dd6d3225ab46e189b72a9e5b9fa95a | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 2 | postponed |
| 235ee737e71e4923a3bc59bbca692534 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_LShift | 2 | postponed |
| f3f81b87b5974ed28ba0d67acfb0b1c9 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Mod | 2 | postponed |
| c437959c7e2c4d6e97de97e4aba728a4 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Mul | 2 | postponed |
| 5229226fd252422e9014ffa7a7577249 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Pow | 2 | postponed |
| 69854fe6b00f46098abce485fa3238d6 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_RShift | 2 | postponed |
| b0a660e844314a13842ca3220780ec55 | [src/gzkit/commands/covers.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:176) | core/ReplaceBinaryOperator_BitOr_Sub | 2 | postponed |
| 508bce4042ae4838a41d354cf54c0eee | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Add | 3 | postponed |
| 87d2776870944a9983324d3534a2b2e3 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_BitAnd | 3 | postponed |
| 773d11c8092c4dbe8ec5c8a35f5ff81a | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_BitXor | 3 | postponed |
| f6b55d798f614f539f0ae869f0dc1045 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Div | 3 | postponed |
| 782bab13ac344ea58a95a6600d27e1f6 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 3 | postponed |
| 6480b74aebf749d8aea7cfcc3abf0c56 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_LShift | 3 | postponed |
| e5927612c6d947bca0f750697c6027d8 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Mod | 3 | postponed |
| c0759dd5f1ba4662b46de986cb778be8 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Mul | 3 | postponed |
| bb90333a1572464dac8e7ad5bd41d596 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Pow | 3 | postponed |
| 6ba3bbad25b34691b91dcb8f17a7b918 | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_RShift | 3 | postponed |
| 26bce5c50cc74c449dd216699b0e314a | [src/gzkit/commands/covers.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:177) | core/ReplaceBinaryOperator_BitOr_Sub | 3 | postponed |
| ee4161aac23048cc90f86c345e792d58 | [src/gzkit/commands/covers.py:178](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:178) | core/ReplaceFalseWithTrue | 2 | runtime/source |
| 3d84d15c58554439b799d12823190cb3 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Add | 4 | postponed |
| 13bb5f22081640eea6531b13dbca737c | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_BitAnd | 4 | postponed |
| dbcff37b952f46b4892621cf2ea59836 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_BitXor | 4 | postponed |
| 2ffc9142245e44da8d36dd894ac9764f | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Div | 4 | postponed |
| c5311fc930c249358a74587dab7c6c94 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 4 | postponed |
| 047a98fffa9148a193d0749919bb4e28 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_LShift | 4 | postponed |
| c2e7e4304e7543b3b39b7ded584b21f9 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Mod | 4 | postponed |
| 4831cd1c7fc64cb7afa6f6841517b21b | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Mul | 4 | postponed |
| 9736eb26f0e64784a065ddeb8bc0027e | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Pow | 4 | postponed |
| 32b40810ddb14ae4883dc6f7d18fc564 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_RShift | 4 | postponed |
| b7456ab8483d4642b165a1af309ec2d1 | [src/gzkit/commands/covers.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:180) | core/ReplaceBinaryOperator_BitOr_Sub | 4 | postponed |
| 9de4efb5c5264483beb9235d9242895f | [src/gzkit/commands/covers.py:231](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:231) | core/AddNot | 14 | runtime/source |
| 711d9a9aefac4586916320c5217b5fea | [src/gzkit/commands/covers.py:231](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:231) | core/ReplaceAndWithOr | 2 | runtime/source |
| 3162ece8676e40f7a3e6a8e403b15602 | [src/gzkit/commands/covers.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:235) | core/NumberReplacer | 22 | runtime/source |
| e920e55a6add45f18e5da4f9b6424852 | [src/gzkit/commands/covers.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:235) | core/NumberReplacer | 23 | runtime/source |

### mutation_witness — 90 survivors / 336 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| bb3c6fca3d8f4025b3bef31664782bf1 | [src/gzkit/mutation_witness.py:51](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:51) | core/NumberReplacer | 0 | runtime/source |
| 49ca6f369bb649939bf6c3ce3ae712d0 | [src/gzkit/mutation_witness.py:51](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:51) | core/NumberReplacer | 1 | runtime/source |
| e1a0344f69c142e4bc7c8dbab52d52fe | [src/gzkit/mutation_witness.py:69](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:69) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| 9c231c4060a34b9e975c500471719c02 | [src/gzkit/mutation_witness.py:71](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:71) | core/NumberReplacer | 3 | runtime/source |
| 44653ed049f245f3b1054a7c378ead28 | [src/gzkit/mutation_witness.py:73](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:73) | core/NumberReplacer | 5 | runtime/source |
| 5bee47b9ebee4dbbbbc2e03478c6e7a8 | [src/gzkit/mutation_witness.py:83](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:83) | core/ReplaceTrueWithFalse | 1 | runtime/source |
| 5e19615033c4490f96374a5aeb8331f3 | [src/gzkit/mutation_witness.py:93](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:93) | core/ReplaceFalseWithTrue | 3 | runtime/source |
| 00f619b25cea4fadac07117d5e15e3a0 | [src/gzkit/mutation_witness.py:96](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:96) | core/NumberReplacer | 6 | runtime/source |
| c7493ae7e82d42e5923648574160c330 | [src/gzkit/mutation_witness.py:96](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:96) | core/NumberReplacer | 7 | runtime/source |
| e80d132826c44168b706328b26b406c7 | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/ReplaceUnaryOperator_Delete_USub | 0 | runtime/source |
| 1977b45f87bb4aac86083c447537ee31 | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/ReplaceUnaryOperator_USub_Invert | 0 | runtime/source |
| d6cedd4ac241491ca40354592bd38f7c | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/ReplaceUnaryOperator_USub_Not | 0 | runtime/source |
| 14a690e66f574387b3d37b0d272bf4f1 | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/ReplaceUnaryOperator_USub_UAdd | 0 | runtime/source |
| 782444a2adc64fffabfd0595c5c56419 | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/NumberReplacer | 8 | runtime/source |
| cda3756e02564843869b15293e92aa68 | [src/gzkit/mutation_witness.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:97) | core/NumberReplacer | 9 | runtime/source |
| 8759e9eed9f64d01ae9de9638634178b | [src/gzkit/mutation_witness.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:107) | core/ReplaceTrueWithFalse | 2 | runtime/source |
| 7a3c3a010f8a4e019b8544b9b6795b80 | [src/gzkit/mutation_witness.py:115](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:115) | core/NumberReplacer | 10 | runtime/source |
| 989c30ccf7bb4efa857716e9c040a497 | [src/gzkit/mutation_witness.py:115](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:115) | core/NumberReplacer | 11 | runtime/source |
| 679a2c8f25d34321a44301b08ff8dd6f | [src/gzkit/mutation_witness.py:121](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:121) | core/ReplaceComparisonOperator_Eq_Is | 0 | runtime/source |
| 3f31e6c2c068488db73d7a6647344e99 | [src/gzkit/mutation_witness.py:126](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:126) | core/ReplaceComparisonOperator_Eq_GtE | 1 | runtime/source |
| cb99afca016a491a88af9e35816a16a8 | [src/gzkit/mutation_witness.py:126](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:126) | core/ReplaceComparisonOperator_Eq_Is | 1 | runtime/source |
| b18e3a1f68804ee2aa80ba881b0ea9fd | [src/gzkit/mutation_witness.py:131](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:131) | core/ReplaceComparisonOperator_Eq_Is | 2 | runtime/source |
| 9ac90c427a60417da236c2065bbc327a | [src/gzkit/mutation_witness.py:131](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:131) | core/ReplaceComparisonOperator_Eq_LtE | 2 | runtime/source |
| 79c526e0f3d446309b77d84ec4e8a1f3 | [src/gzkit/mutation_witness.py:136](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:136) | core/NumberReplacer | 18 | runtime/source |
| 7917f84de5e148e0b658885ed99ec0b7 | [src/gzkit/mutation_witness.py:136](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:136) | core/ReplaceComparisonOperator_Eq_Is | 3 | runtime/source |
| d46d9e283a964c49a63f34ad3ba48bb9 | [src/gzkit/mutation_witness.py:136](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:136) | core/ReplaceComparisonOperator_Eq_LtE | 3 | runtime/source |
| 5a32ffaf30db4014970f507ab1ca6408 | [src/gzkit/mutation_witness.py:166](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:166) | core/NumberReplacer | 21 | runtime/source |
| 25587b5d255e4905a8ab0ccbcaec32ad | [src/gzkit/mutation_witness.py:167](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:167) | core/ReplaceComparisonOperator_Lt_IsNot | 0 | runtime/source |
| f6b4f5dd240740009bcc1353644274bf | [src/gzkit/mutation_witness.py:167](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:167) | core/ReplaceComparisonOperator_Lt_NotEq | 0 | runtime/source |
| d8d4b189de0b4ebfa20837315dc740ec | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/ReplaceBinaryOperator_Add_BitOr | 1 | runtime/source |
| 70119c770f9647b4b33328215b9cbb70 | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/ReplaceBinaryOperator_Add_BitXor | 1 | runtime/source |
| 2768400a2e904bb5a1562183193a04c0 | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/ReplaceBinaryOperator_Add_LShift | 2 | runtime/source |
| f52a4818267845499e876e8713939860 | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/NumberReplacer | 24 | runtime/source |
| 2afe249465644da4a3faff8cf035214b | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/ReplaceComparisonOperator_Lt_IsNot | 1 | runtime/source |
| 436b5a144ecb480fb3e5e0930ff51415 | [src/gzkit/mutation_witness.py:168](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:168) | core/ReplaceComparisonOperator_Lt_NotEq | 1 | runtime/source |
| cd20a391c3f54038a5a302fbb9067e9a | [src/gzkit/mutation_witness.py:172](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:172) | core/NumberReplacer | 29 | runtime/source |
| 5ce4f368064640779db3f18f1501bfd2 | [src/gzkit/mutation_witness.py:199](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:199) | core/NumberReplacer | 33 | runtime/source |
| 538e9fb8a9b84ebb92b8badabdf0ebf3 | [src/gzkit/mutation_witness.py:199](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:199) | core/ReplaceComparisonOperator_Eq_GtE | 4 | runtime/source |
| 264fcfd07e83408f9eac7c9383ba5c77 | [src/gzkit/mutation_witness.py:199](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:199) | core/ReplaceComparisonOperator_Eq_LtE | 4 | runtime/source |
| 05ab347d7ad843c3809444561f8d2fe8 | [src/gzkit/mutation_witness.py:199](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:199) | core/NumberReplacer | 36 | runtime/source |
| 7cf5546e1f904ce898481811fa2c0a70 | [src/gzkit/mutation_witness.py:199](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:199) | core/NumberReplacer | 37 | runtime/source |
| 2c0ec45a9c1f40a4a0b1e8b4d416dee7 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| a8bf0cc6478a40bb8a416e286425ed73 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| c8548bf01ffc42faa70e564fe989948e | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| aebd6f2f14dc463aa4b0c4e4eda5d5ed | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| 2185c98c95e24aa6a5ef6994231b0db1 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| d0b3627acd0945f9963ad664848fb04a | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 4cbb0ac359c14820b7aed35c6e31c0e1 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| ac87b24fff3a4510972140e68c756985 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| bcf1a3e11d0b4371b9ef4f01dff51a65 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| 5e2fa15c5ac84bdb8221dcb5d6bec014 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 50846145931745d58de2638ab9aea940 | [src/gzkit/mutation_witness.py:203](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:203) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| 5f75b0210a3f468a8e7df4728159cf20 | [src/gzkit/mutation_witness.py:209](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:209) | core/ReplaceComparisonOperator_Eq_GtE | 5 | runtime/source |
| c78f05512fbc4270884d17313174cb97 | [src/gzkit/mutation_witness.py:211](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:211) | core/NumberReplacer | 38 | runtime/source |
| 3aeefb46bd68449e8c80f27874d69a2a | [src/gzkit/mutation_witness.py:211](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:211) | core/ReplaceUnaryOperator_Delete_USub | 1 | runtime/source |
| 6d2d2d77ec2248f5a2aa771c2ddd9f65 | [src/gzkit/mutation_witness.py:211](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:211) | core/ReplaceUnaryOperator_USub_UAdd | 1 | runtime/source |
| f8dbca4d76c74d56bfe169ca30875baa | [src/gzkit/mutation_witness.py:229](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:229) | core/ReplaceTrueWithFalse | 4 | runtime/source |
| cf9ea2d7b98b4c9493824d9f1830cc25 | [src/gzkit/mutation_witness.py:247](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:247) | core/ReplaceComparisonOperator_Eq_LtE | 7 | runtime/source |
| 262118dfc011413a86b2fc7eebcaf166 | [src/gzkit/mutation_witness.py:252](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:252) | core/ReplaceBinaryOperator_Mul_Div | 0 | runtime/source |
| ef7135105d834076b17dbfdd82e182bb | [src/gzkit/mutation_witness.py:266](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:266) | core/NumberReplacer | 46 | runtime/source |
| 186ce705998d47518aa500696ee377cf | [src/gzkit/mutation_witness.py:267](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:267) | core/ReplaceComparisonOperator_Eq_Is | 6 | runtime/source |
| f85598dda6614bb0b8ddc1de4c962309 | [src/gzkit/mutation_witness.py:272](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:272) | core/ReplaceTrueWithFalse | 5 | runtime/source |
| f69f4c59bfa1465ab8a2543fc316a117 | [src/gzkit/mutation_witness.py:283](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:283) | core/ReplaceTrueWithFalse | 6 | runtime/source |
| bb14a472f72e4ca99c83fb7715ab839e | [src/gzkit/mutation_witness.py:284](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:284) | core/ReplaceTrueWithFalse | 7 | runtime/source |
| cf2cd7a487cb423b9cc35c5219f73426 | [src/gzkit/mutation_witness.py:288](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:288) | core/ReplaceOrWithAnd | 2 | runtime/source |
| 8d236c3d8b354ebdb2187fb76718a04e | [src/gzkit/mutation_witness.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:297) | core/ReplaceTrueWithFalse | 8 | runtime/source |
| dac69e4241f5432c8ba8fedde2598513 | [src/gzkit/mutation_witness.py:298](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:298) | core/ReplaceTrueWithFalse | 9 | runtime/source |
| 7d4e0d2c35614e79b5399878d101d446 | [src/gzkit/mutation_witness.py:299](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:299) | core/ReplaceTrueWithFalse | 10 | runtime/source |
| 0db32628223e4104a348c59082891cd4 | [src/gzkit/mutation_witness.py:308](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:308) | core/ReplaceUnaryOperator_USub_Invert | 2 | runtime/source |
| 2b668c7418a74807bf6b6723f99b20f6 | [src/gzkit/mutation_witness.py:308](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:308) | core/ReplaceUnaryOperator_USub_Not | 2 | runtime/source |
| 54b185c1913d4fae80999a1b7f87baf5 | [src/gzkit/mutation_witness.py:308](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:308) | core/NumberReplacer | 48 | runtime/source |
| 686b2240995548ed9ae5191915ad5b8e | [src/gzkit/mutation_witness.py:308](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:308) | core/NumberReplacer | 49 | runtime/source |
| e8fd6f623f3743738d85adb468ebaa35 | [src/gzkit/mutation_witness.py:316](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:316) | core/ReplaceComparisonOperator_Eq_Lt | 9 | runtime/source |
| 9624f98dcecf4c4fa192923d9ddd04f6 | [src/gzkit/mutation_witness.py:316](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:316) | core/ReplaceComparisonOperator_Eq_LtE | 9 | runtime/source |
| 971bb3ed386c49e0b01339b1ceacbc40 | [src/gzkit/mutation_witness.py:316](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:316) | core/NumberReplacer | 51 | runtime/source |
| 362d00b91d6e46268fa4d4beb0666d31 | [src/gzkit/mutation_witness.py:320](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:320) | core/ReplaceComparisonOperator_Eq_LtE | 10 | runtime/source |
| da31bdbe98714979bacd3be438998363 | [src/gzkit/mutation_witness.py:322](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:322) | core/ReplaceComparisonOperator_NotEq_Gt | 1 | runtime/source |
| 4fafe64221704aa788dade91412b922c | [src/gzkit/mutation_witness.py:322](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:322) | core/ReplaceComparisonOperator_NotEq_IsNot | 0 | runtime/source |
| 58113f0e4ef54eaa89d7e98c44bd6949 | [src/gzkit/mutation_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:350) | core/ReplaceOrWithAnd | 5 | runtime/source |
| 6154e0e550904979a41f6a3404c745c0 | [src/gzkit/mutation_witness.py:352](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:352) | core/ReplaceComparisonOperator_Eq_LtE | 11 | runtime/source |
| 883094d39a4943ec9b628c334833c8b4 | [src/gzkit/mutation_witness.py:352](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:352) | core/ReplaceComparisonOperator_Gt_GtE | 0 | runtime/source |
| 52acaf7902144267a0e322ae63a38e66 | [src/gzkit/mutation_witness.py:352](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:352) | core/ReplaceComparisonOperator_Gt_NotEq | 0 | runtime/source |
| 314839f60d4f4327954c53c32167ae29 | [src/gzkit/mutation_witness.py:352](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:352) | core/NumberReplacer | 57 | runtime/source |
| 5fe08cb7474b45b289a4cb020bc8196b | [src/gzkit/mutation_witness.py:365](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:365) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| 03e5db75d9d84f08bac06122d4a649ce | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/ReplaceUnaryOperator_Delete_USub | 3 | runtime/source |
| a97ac8bc256643079549eb8ea03e59e2 | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/ReplaceUnaryOperator_USub_Invert | 3 | runtime/source |
| de47653e860343a7962de7f7fda2493c | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/ReplaceUnaryOperator_USub_Not | 3 | runtime/source |
| 68eb80ecb7c941fbb4e1acfd0f6599ec | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/ReplaceUnaryOperator_USub_UAdd | 3 | runtime/source |
| f8f1d7b5aed443bfa3cd8c5e66dfcc93 | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/NumberReplacer | 58 | runtime/source |
| 43e806593cf3457aa003e59c70e840ee | [src/gzkit/mutation_witness.py:387](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:387) | core/NumberReplacer | 59 | runtime/source |

### red_parity — 50 survivors / 164 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| b3fecb0d29de40c6b35bbcb7f9ab9cba | [src/gzkit/governance/trust_audits/red_parity.py:30](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:30) | core/AddNot | 0 | runtime/source |
| ab4319cc700542c8b01b505973d56817 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 0 | runtime/source |
| 9def19acf5fe42b4b1d538aedb98b76d | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 1 | runtime/source |
| 6b29e0f926664a7f8929a4b69883f3a4 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 2 | runtime/source |
| f297320ce53649439a3b80bce3d953e6 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 3 | runtime/source |
| c0807bcba9934d43aa9644a1893d249a | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 4 | runtime/source |
| c12d610bbdb1413db784ccaa22c55638 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 5 | runtime/source |
| efba5d91190b4d9da899971510569dd6 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 6 | runtime/source |
| 6ccce4d0efdb49129a5a2e1128b8d7ed | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 7 | runtime/source |
| 035e7ab5a5254c01b4ffb929593b8bd3 | [src/gzkit/governance/trust_audits/red_parity.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:41) | core/NumberReplacer | 8 | runtime/source |
| a93601bcdda84bfc8af5a5d0d22e7e99 | [src/gzkit/governance/trust_audits/red_parity.py:65](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:65) | core/ReplaceComparisonOperator_Eq_Gt | 0 | runtime/source |
| 529a76d8e6fa42cca1bdec70ed31aefc | [src/gzkit/governance/trust_audits/red_parity.py:65](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:65) | core/ReplaceComparisonOperator_Eq_GtE | 0 | runtime/source |
| 5641b02941d04f7cb346096202c9ac0b | [src/gzkit/governance/trust_audits/red_parity.py:65](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:65) | core/ReplaceComparisonOperator_Eq_Is | 0 | runtime/source |
| 1109257e99db4f34b9e3e01750c48db2 | [src/gzkit/governance/trust_audits/red_parity.py:66](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:66) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| 0860ca44840b40d696cf227656ad6f13 | [src/gzkit/governance/trust_audits/red_parity.py:68](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:68) | core/ReplaceComparisonOperator_Eq_GtE | 1 | runtime/source |
| 3051ab1e6d4345c4ba5b1cd7bfb99161 | [src/gzkit/governance/trust_audits/red_parity.py:68](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:68) | core/ReplaceComparisonOperator_Eq_LtE | 2 | runtime/source |
| 9621ef33378a47eea04cc308b6c64ea1 | [src/gzkit/governance/trust_audits/red_parity.py:75](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:75) | core/ExceptionReplacer | 0 | runtime/source |
| 7637dd74cb594118a639d73c99df9d07 | [src/gzkit/governance/trust_audits/red_parity.py:79](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:79) | core/ReplaceContinueWithBreak | 0 | runtime/source |
| 2a33201553d34287b7a2daebae7abd27 | [src/gzkit/governance/trust_audits/red_parity.py:82](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:82) | core/ExceptionReplacer | 1 | runtime/source |
| 7d5dcf5264314ba5bf40a801d982ea0f | [src/gzkit/governance/trust_audits/red_parity.py:83](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:83) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| cb4e1b97ebd54b39afef0787c1c62640 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| 3a79a536d3ea4474b3dfd0dede6a85df | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| b3bc2874dbe4403fb0218ab98919df23 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| 2197704c9bf2461487c730f26115906d | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| ac467c4806d547f6ad6da14a68459db1 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| 6cb9bb8971d84357b642f5d42c5ae3f8 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| b9f5eefc00bd4d1d97718d95a4d8d30e | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| e8565bf4df9f4ba5b9ee80ed43b98fdb | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| d14873c86c124f439d43257b789dc4dd | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| 7c8d6bd741e142b88d56da265fb760d7 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 62d8058f313448b58d5fab4db941cc87 | [src/gzkit/governance/trust_audits/red_parity.py:88](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:88) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| 653f88299da94e2c96615340913c3ef8 | [src/gzkit/governance/trust_audits/red_parity.py:95](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:95) | core/ExceptionReplacer | 2 | runtime/source |
| 8211c0859b7f4575a54461ebba84973a | [src/gzkit/governance/trust_audits/red_parity.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:97) | core/AddNot | 5 | runtime/source |
| 3ce8b0153cbd4b5e83b59eec5b85da60 | [src/gzkit/governance/trust_audits/red_parity.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:110) | core/ReplaceComparisonOperator_Eq_GtE | 3 | runtime/source |
| 8fa09065290d4bf89a2d45a1545307c7 | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_GtE | 4 | runtime/source |
| d1ad4f59484c4bf384bfe194696f6830 | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_IsNot | 4 | runtime/source |
| 79cfbfb230374a698c5905be159d84d9 | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_LtE | 4 | runtime/source |
| 503a58ccd37846d19ed969a30ba0ae87 | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceAndWithOr | 2 | runtime/source |
| d95a9a21765a4292a085103da7078972 | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_GtE | 5 | runtime/source |
| a675200d4c5a4ccfa0c17fcb3381599d | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_IsNot | 5 | runtime/source |
| 4b60408202054196aa94f178856219da | [src/gzkit/governance/trust_audits/red_parity.py:119](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:119) | core/ReplaceComparisonOperator_Eq_LtE | 5 | runtime/source |
| 6ad98f05b173422abd28e621eaffb2bb | [src/gzkit/governance/trust_audits/red_parity.py:122](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:122) | core/ReplaceAndWithOr | 3 | runtime/source |
| e8851b0785bb4adaa556b2d4c0ae0efe | [src/gzkit/governance/trust_audits/red_parity.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:137) | core/ReplaceComparisonOperator_Eq_LtE | 6 | runtime/source |
| 13f0ee38d21443cd8fc27867c032c765 | [src/gzkit/governance/trust_audits/red_parity.py:144](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:144) | core/ReplaceComparisonOperator_NotEq_Gt | 0 | runtime/source |
| 5edeec133fce484e92148251c76dd8b1 | [src/gzkit/governance/trust_audits/red_parity.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:190) | core/ReplaceComparisonOperator_Lt_LtE | 0 | runtime/source |
| 7c3d67b340f84a28ba350145a0f3f06f | [src/gzkit/governance/trust_audits/red_parity.py:191](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:191) | core/ReplaceContinueWithBreak | 2 | runtime/source |
| 610aebf29eb0490f94c8766468ed8fc1 | [src/gzkit/governance/trust_audits/red_parity.py:194](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:194) | core/ExceptionReplacer | 3 | runtime/source |
| fc079291784543d4b0ea2a6091285e42 | [src/gzkit/governance/trust_audits/red_parity.py:195](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:195) | core/ReplaceContinueWithBreak | 3 | runtime/source |
| 0007356acaca4798bcf3a8f9fd287333 | [src/gzkit/governance/trust_audits/red_parity.py:197](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:197) | core/ReplaceContinueWithBreak | 4 | runtime/source |
| e2f1452a6fd44d169ba8a1889f9dd87c | [src/gzkit/governance/trust_audits/red_parity.py:204](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/red_parity.py:204) | core/ReplaceComparisonOperator_Eq_GtE | 7 | runtime/source |

### red_witness — 151 survivors / 355 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| c33ef0cdf19142318fd94e264d0b0bc3 | [src/gzkit/red_witness.py:45](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:45) | core/AddNot | 0 | runtime/source |
| 80c08987713144c1bbdd87eecd30d7fa | [src/gzkit/red_witness.py:66](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:66) | core/NumberReplacer | 0 | runtime/source |
| 75bca70b9d5a47808f39105c4b853c47 | [src/gzkit/red_witness.py:66](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:66) | core/NumberReplacer | 1 | runtime/source |
| fd4123c4994e41c9b56810f74f858b11 | [src/gzkit/red_witness.py:67](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:67) | core/NumberReplacer | 2 | runtime/source |
| 9c479474a9e944469157df8e7431e054 | [src/gzkit/red_witness.py:67](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:67) | core/NumberReplacer | 3 | runtime/source |
| e2ed6025840c4247a2c6cbfc0e8fe8f5 | [src/gzkit/red_witness.py:73](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:73) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| 75735ec399df40f58c2dcfb1b7c3c564 | [src/gzkit/red_witness.py:75](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:75) | core/NumberReplacer | 4 | runtime/source |
| cea707afb7b1453d9b7aef8f09d113fc | [src/gzkit/red_witness.py:75](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:75) | core/NumberReplacer | 5 | runtime/source |
| fb5aa7a15710422595e8c5584b9408ec | [src/gzkit/red_witness.py:76](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:76) | core/NumberReplacer | 6 | runtime/source |
| d231750d4b904f9c9355ddbb7f074f29 | [src/gzkit/red_witness.py:76](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:76) | core/NumberReplacer | 7 | runtime/source |
| 5841beadb9d844dd9a74ddff7c7981ec | [src/gzkit/red_witness.py:102](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:102) | core/ReplaceComparisonOperator_Eq_LtE | 0 | runtime/source |
| 23af9a3a582f465b84c30188a467cb6f | [src/gzkit/red_witness.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:104) | core/ReplaceComparisonOperator_Eq_LtE | 1 | runtime/source |
| 5ed0cafce3d74c59bd3e5ecfa3205304 | [src/gzkit/red_witness.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:104) | core/ReplaceComparisonOperator_Eq_GtE | 2 | runtime/source |
| 051f888b5b91404a81d5daa5d6da884f | [src/gzkit/red_witness.py:116](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:116) | core/ReplaceComparisonOperator_Eq_GtE | 3 | runtime/source |
| 64190c4d02e3406a9e27522a9b79c3a9 | [src/gzkit/red_witness.py:118](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:118) | core/ReplaceComparisonOperator_Eq_LtE | 5 | runtime/source |
| cc013720eb6c4230bc96f383903d7bfe | [src/gzkit/red_witness.py:129](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:129) | core/ReplaceComparisonOperator_Eq_LtE | 6 | runtime/source |
| b5e47ebd7aa34f1fbcf17311ea43ad77 | [src/gzkit/red_witness.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:137) | core/ReplaceComparisonOperator_Gt_GtE | 0 | runtime/source |
| b4a536e4403040d08f88f560c5ececd3 | [src/gzkit/red_witness.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:137) | core/ReplaceComparisonOperator_Gt_NotEq | 0 | runtime/source |
| bf312721d18a43e2ad71ba750c92d4ed | [src/gzkit/red_witness.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:137) | core/NumberReplacer | 13 | runtime/source |
| 42883cf04a824c36a0e297006f52e923 | [src/gzkit/red_witness.py:140](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:140) | core/ReplaceComparisonOperator_Gt_NotEq | 1 | runtime/source |
| 4def2e6871d9426e9e2eaf47dfca9fdd | [src/gzkit/red_witness.py:151](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:151) | core/ReplaceTrueWithFalse | 3 | runtime/source |
| 0eb57b55cd034cf09d2e4eaf1c51e423 | [src/gzkit/red_witness.py:162](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:162) | core/ReplaceComparisonOperator_NotEq_Gt | 0 | runtime/source |
| c77412c5da384fb5a86c9de8007377c0 | [src/gzkit/red_witness.py:162](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:162) | core/ReplaceComparisonOperator_NotEq_Lt | 0 | runtime/source |
| 75617cec31844126825d70d2e47b7aba | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| 079e6d6ff08346229bb2b604aacece2e | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| 7f00709a057844fdbc28712ff109d047 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| 8bd570b596084a5187594ba231b86f7b | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| 53ae1ea90ff647feba01a35a9148c8d3 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| 9092be86bcd547abb8ee73d9248335c5 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 396acd34b4234396a3ad2ce9d182c7cc | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| a1a7e03eb43d4a97a4a0e5963f6a9aa3 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| 4a3f93b10d4b4ef0b3d141d6434cfc04 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| b7adb3b0128a4183a4bf0164188a696c | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 921cd1f1a6c7404e9e216e4a98b950e9 | [src/gzkit/red_witness.py:169](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:169) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| ca26de5e06a74352aa4f902af7b1b0e9 | [src/gzkit/red_witness.py:192](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:192) | core/ReplaceComparisonOperator_NotEq_Gt | 1 | runtime/source |
| 9157a2d5553b44ee99bd378333175d43 | [src/gzkit/red_witness.py:192](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:192) | core/ReplaceComparisonOperator_NotEq_Lt | 1 | runtime/source |
| 59a13def88b94a648a7c959847b3199e | [src/gzkit/red_witness.py:197](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:197) | core/NumberReplacer | 23 | runtime/source |
| c4c4e2b766b14a35b7bdb959e8288d07 | [src/gzkit/red_witness.py:198](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:198) | core/ReplaceComparisonOperator_NotEq_Gt | 2 | runtime/source |
| 7de0fd19441a466e87c66a3d7ec13961 | [src/gzkit/red_witness.py:215](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:215) | core/ReplaceComparisonOperator_Eq_GtE | 7 | runtime/source |
| be8893b3c56042e3983b59035b61ca06 | [src/gzkit/red_witness.py:215](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:215) | core/ReplaceComparisonOperator_Eq_LtE | 7 | runtime/source |
| c890e297407f415d87ee222db2b5c9f3 | [src/gzkit/red_witness.py:218](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:218) | core/ReplaceComparisonOperator_Eq_GtE | 8 | runtime/source |
| e5788eb43e6f472083520033ef055fd2 | [src/gzkit/red_witness.py:218](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:218) | core/ReplaceComparisonOperator_Eq_LtE | 8 | runtime/source |
| eaed50dd4b294119a326077ef11cbce1 | [src/gzkit/red_witness.py:252](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:252) | core/ReplaceComparisonOperator_Eq_GtE | 9 | runtime/source |
| 23f4d6b9aa5b40ed9b224f58058a6c33 | [src/gzkit/red_witness.py:252](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:252) | core/ReplaceComparisonOperator_Eq_LtE | 9 | runtime/source |
| 1bdc743319ab42dbbfc574b9ee9ed8b2 | [src/gzkit/red_witness.py:255](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:255) | core/ReplaceComparisonOperator_Eq_GtE | 10 | runtime/source |
| 7b8235e5bc5f41eda32333d1757f19c4 | [src/gzkit/red_witness.py:255](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:255) | core/ReplaceComparisonOperator_Eq_LtE | 10 | runtime/source |
| 13de2f1d4d074cee96d51f296330e304 | [src/gzkit/red_witness.py:270](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:270) | core/ReplaceComparisonOperator_NotEq_Gt | 3 | runtime/source |
| 8d8ca457874b4ae6abb588d86e364335 | [src/gzkit/red_witness.py:270](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:270) | core/ReplaceComparisonOperator_NotEq_Lt | 3 | runtime/source |
| 4c731677787a46a4bb5cceadca52959c | [src/gzkit/red_witness.py:271](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:271) | core/ReplaceTrueWithFalse | 4 | runtime/source |
| 40afe75b970f45fc8d7f71912a92a9fa | [src/gzkit/red_witness.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:277) | core/ReplaceTrueWithFalse | 5 | runtime/source |
| 7e1ea386c11640d6bbf702729354ec53 | [src/gzkit/red_witness.py:289](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:289) | core/ReplaceContinueWithBreak | 0 | runtime/source |
| e31f9d797d4d45fe8d622a441b01a9cf | [src/gzkit/red_witness.py:291](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:291) | core/ReplaceTrueWithFalse | 6 | runtime/source |
| 44241d13e93c4f63bc8f1814e4f0504e | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Add | 1 | postponed |
| 3c730cb5f0224f65ac16b895b8c96b97 | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_BitAnd | 1 | postponed |
| 964e0648da374f7fbfe6097cde42dad8 | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_BitXor | 1 | postponed |
| 0b602e54f2d749a2bd3d81a3a9bd242a | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Div | 1 | postponed |
| fb23f37789e34485bb29526acc50892b | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 1 | postponed |
| 6f4dba75d1f04ad29629e4c20edf5df7 | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_LShift | 1 | postponed |
| 32af037431e1438682906c6b2913169c | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Mod | 1 | postponed |
| dfcd0357a37e45a7addb396877ed8961 | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Mul | 1 | postponed |
| 91d9d0c5a247490eba289008efcb4df2 | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Pow | 1 | postponed |
| c58211a33c8a4a519a6ad038222f29aa | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_RShift | 1 | postponed |
| 740260129ac74b82b53f17653a878f9e | [src/gzkit/red_witness.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:301) | core/ReplaceBinaryOperator_BitOr_Sub | 1 | postponed |
| 6c132640eb5442c49dfd67e38b458296 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Add | 2 | postponed |
| 6ce15b54a2ae492591ff783c0386313f | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_BitAnd | 2 | postponed |
| 809d60e60a0548548d57e55c97fb8491 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_BitXor | 2 | postponed |
| d052386d6b5348c5a8f2f67b4c57d317 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Div | 2 | postponed |
| e228ec39debf4d23a78cf27aac61569d | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 2 | postponed |
| a85c7f451f9b488995eb0c6241eb00b8 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_LShift | 2 | postponed |
| 2a43b3c6270840f2939ca3c1bba86907 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Mod | 2 | postponed |
| 208e6cb42523467e89b3256832e6428e | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Mul | 2 | postponed |
| 2e181b095ba44049b3c26b30d6767348 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Pow | 2 | postponed |
| 17156722ace84e81912bc5e58298d1d1 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_RShift | 2 | postponed |
| b4e5bd9f93754517a9f752534e393892 | [src/gzkit/red_witness.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:302) | core/ReplaceBinaryOperator_BitOr_Sub | 2 | postponed |
| f6ac334b4da34c328d8a901cbfb77c45 | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/AddNot | 18 | runtime/source |
| 246aab3235bb41c1800e3d20d6ce8b6b | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_Gt | 11 | runtime/source |
| 2d074106a51840bd933a2065b484d7e5 | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_GtE | 11 | runtime/source |
| 62ceea1a3ca4416a8c8fc35a8718ffaf | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_Is | 6 | runtime/source |
| b93cf73f1f314d509d8542636beff938 | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_IsNot | 6 | runtime/source |
| 6798bde5990d42c6ad5ef72a4c041abf | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_Lt | 11 | runtime/source |
| 6277c01ec8814635bf80aa3796f05a65 | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_LtE | 11 | runtime/source |
| c763492b17be4e95b6d515f77151b5e5 | [src/gzkit/red_witness.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:332) | core/ReplaceComparisonOperator_Eq_NotEq | 11 | runtime/source |
| 603ce1b80f11483a8eac1493582e62d2 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Add | 3 | postponed |
| 43f5ece66412455a956f0a520ee02400 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_BitAnd | 3 | postponed |
| bf215077ed4e42e98c4a11ff9cf1bfc6 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_BitXor | 3 | postponed |
| 6a989c25966141e5820249ce743549da | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Div | 3 | postponed |
| 67added853af4666ac7602f1000b1256 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 3 | postponed |
| dbc01e9c4b93419e886e0ee27d47f54b | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_LShift | 3 | postponed |
| f497d1d295634c29a3b82279d6064a47 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Mod | 3 | postponed |
| ffa0646c25d14b5e9eb750682a8b3f41 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Mul | 3 | postponed |
| 36c200d87aae4ca6b64143850abebec8 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Pow | 3 | postponed |
| 71e49e6eac2f4bdaaff80cba21e29282 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_RShift | 3 | postponed |
| 33deae5bafb64e95b87c5c1e4746b185 | [src/gzkit/red_witness.py:348](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:348) | core/ReplaceBinaryOperator_BitOr_Sub | 3 | postponed |
| 346452de78d9495d9f096b13127d3923 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Add | 4 | postponed |
| e0d2e4c08d474e69ada737f7e3af5701 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_BitAnd | 4 | postponed |
| a213740ea57c4b9a9314fbcc6a83a4f4 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_BitXor | 4 | postponed |
| 8098ef6ca4f4414ab9457ec87bf855dc | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Div | 4 | postponed |
| a184357688e845d983f677dfefbfb25b | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 4 | postponed |
| 74b7ca0473f44e9b9c78b835677c2ae3 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_LShift | 4 | postponed |
| a59c59b9114743b4997e58ebc5ddc973 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Mod | 4 | postponed |
| d6e54b52f8a94f58b75acecdecc5e078 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Mul | 4 | postponed |
| 4d121cf5d1ac404f858963a7bc30793b | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Pow | 4 | postponed |
| f1cb758fca8649f9b19be9370547510f | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_RShift | 4 | postponed |
| 27d2800b537740879b6656506cae8a35 | [src/gzkit/red_witness.py:350](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:350) | core/ReplaceBinaryOperator_BitOr_Sub | 4 | postponed |
| e60f5803fb2543929c8ff681907fa713 | [src/gzkit/red_witness.py:370](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:370) | core/NumberReplacer | 36 | runtime/source |
| c80f74947cbd4be19878d73811d6997b | [src/gzkit/red_witness.py:370](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:370) | core/NumberReplacer | 37 | runtime/source |
| 8cb9d97c1b9544a1abecdf8672988ce9 | [src/gzkit/red_witness.py:374](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:374) | core/NumberReplacer | 38 | runtime/source |
| 269fe2eb527c4b20b006afefbcb4cce5 | [src/gzkit/red_witness.py:374](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:374) | core/NumberReplacer | 39 | runtime/source |
| c40ae94de80a478da9b076f193b1ccb7 | [src/gzkit/red_witness.py:384](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:384) | core/AddNot | 23 | runtime/source |
| e937e87f6d1f4e8fac45e9217658f24a | [src/gzkit/red_witness.py:392](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:392) | core/ReplaceTrueWithFalse | 9 | runtime/source |
| 8744efe95eb043b380848e02c6a78b79 | [src/gzkit/red_witness.py:399](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:399) | core/ReplaceOrWithAnd | 3 | runtime/source |
| 897519e7c8a749d9b0c9fcca61fe5957 | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/ReplaceUnaryOperator_Delete_USub | 0 | runtime/source |
| 44f0ecfbbe86405f9d8eb4b8bf80fd92 | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/ReplaceUnaryOperator_USub_Invert | 0 | runtime/source |
| ce7eaed64ac44573ab7d7ea7add094ea | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/ReplaceUnaryOperator_USub_Not | 0 | runtime/source |
| d6cbcc81938f4d2cbcfb5276febe7dc0 | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/ReplaceUnaryOperator_USub_UAdd | 0 | runtime/source |
| 3c3563aadfb745258e5c5115cf3c55d3 | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/NumberReplacer | 40 | runtime/source |
| bddad4def0fc49899f383aa052f0946f | [src/gzkit/red_witness.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:407) | core/NumberReplacer | 41 | runtime/source |
| 324f28ac694b4c888aabe9ad6b683a30 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ZeroIterationForLoop | 1 | runtime/source |
| 9f4231e16de746c499ab1bf58f1eb5e8 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_Add | 3 | runtime/source |
| c6911c7e1e344a9dac825984b56f313b | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_BitAnd | 3 | runtime/source |
| 4cb1659a28304954947a576687476aa6 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_BitOr | 3 | runtime/source |
| 3392a35bde2b419eb206474043b93eda | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_BitXor | 3 | runtime/source |
| e4092918d36a4bc9b3e9f6837f8d0570 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_FloorDiv | 3 | runtime/source |
| d0d73b9eabb44eaf9009a6a168615be3 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_LShift | 3 | runtime/source |
| 944a3db78df14f8f8dbe5f0c9dc870a7 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_Mod | 3 | runtime/source |
| e0666dac2b1b412b8bdd39b9ab6f7898 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_Mul | 3 | runtime/source |
| 30f4ebf34c824279b356f01ab825d099 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_Pow | 3 | runtime/source |
| 749dc39954bd45469f5f9dfe391db8e7 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_RShift | 3 | runtime/source |
| 26bb9f68d5bd4d5cb89c80977c6b4138 | [src/gzkit/red_witness.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:422) | core/ReplaceBinaryOperator_Div_Sub | 3 | runtime/source |
| 6a3b94e922b34430863860c335eeb1e3 | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/AddNot | 24 | runtime/source |
| 4a19512ccf724411bbdf2440922c4026 | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_Eq | 4 | runtime/source |
| 7ea0bbb947cb4336979bd325fe261b8b | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_Gt | 4 | runtime/source |
| 59c0dd4463f84701b5edab4b5e16be99 | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_GtE | 4 | runtime/source |
| 3072847b28854cc19ea8a772ee571e64 | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_Is | 0 | runtime/source |
| 1600d282532f49bfa6d25034c5f067ad | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_IsNot | 0 | runtime/source |
| 2b3bdfd391924d8aadb9bbcd5f2ab0ee | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_Lt | 4 | runtime/source |
| 579267a7b1394d6bb573c3bca3b1491f | [src/gzkit/red_witness.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:423) | core/ReplaceComparisonOperator_NotEq_LtE | 4 | runtime/source |
| 64115226694c4a6f822c60eeaf4692ef | [src/gzkit/red_witness.py:424](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:424) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| 8c75618a0bf64cecb0eeba152864ebf1 | [src/gzkit/red_witness.py:427](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:427) | core/ExceptionReplacer | 0 | runtime/source |
| 73859df9fb1a4f99bb5aac9271ea2e03 | [src/gzkit/red_witness.py:428](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:428) | core/ReplaceContinueWithBreak | 2 | runtime/source |
| 8634bfee45fc4e0c87443ec5554cd1c0 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/AddNot | 25 | runtime/source |
| 4f106aff191b44dcb6f92c7b00921806 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_Eq | 5 | runtime/source |
| 20430323ad07499cb3568424c189cab7 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_Gt | 5 | runtime/source |
| 9e78e3144fb6413facb270be55c5fe3b | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_GtE | 5 | runtime/source |
| 521b4f2b9f94492d87d1054b25f34d21 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_Is | 1 | runtime/source |
| c4471858385f4d07ac154830bd2f571a | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_IsNot | 1 | runtime/source |
| 79ad8fefdbaa4c8f8430f01b5afc61d6 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_Lt | 5 | runtime/source |
| dcf45d06c3e94cb48098109b77ed5487 | [src/gzkit/red_witness.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:429) | core/ReplaceComparisonOperator_NotEq_LtE | 5 | runtime/source |
| fe7e6568e31e46b4a3032e83b49111d3 | [src/gzkit/red_witness.py:430](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:430) | core/ReplaceContinueWithBreak | 3 | runtime/source |
| 480b0a4db20447b79aee4db4f49054b6 | [src/gzkit/red_witness.py:432](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:432) | core/AddNot | 26 | runtime/source |
| a8c709437d764c858d1ca1e940b1771d | [src/gzkit/red_witness.py:432](/Users/jeff/Documents/Code/gzkit/src/gzkit/red_witness.py:432) | core/ReplaceComparisonOperator_IsNot_Is | 2 | runtime/source |

### req_coverage — 18 survivors / 46 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| c45b92f4441c4784964fec3c92f3ce31 | [src/gzkit/governance/req_coverage.py:55](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:55) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| f64665e8425b474e99bf21537cd9d348 | [src/gzkit/governance/req_coverage.py:106](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:106) | core/ReplaceBinaryOperator_Mul_Div | 0 | runtime/source |
| dd7cfee49e96422aaea29b0336d653cc | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| 92224778b880421daeed6b362f187884 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| e4e35ee3d7a04be59e2bafc0d729db4b | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| e60be6b7290944119150f2a12dfb525f | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| bdd6f5b1e29d4543ac74065ff989f644 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| 0835dc1358494687b07ff87846514100 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 5020efc035564521b2f6648fc5b93444 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| daf142a352ba4290ab6ca62d9509d124 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| c1fca15557564c57a9d0b82f2b32faf9 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| e4984bdfe4cb42b0aabc91860e5bce1e | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 9e03a3ec6cbb455ba6cd357859b88877 | [src/gzkit/governance/req_coverage.py:107](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:107) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| e8a831055b894a4a95d00c0f31ea4a72 | [src/gzkit/governance/req_coverage.py:130](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:130) | core/ReplaceComparisonOperator_NotEq_Lt | 0 | runtime/source |
| 398ef57bf968408593f6aa6d58de0ed3 | [src/gzkit/governance/req_coverage.py:131](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:131) | core/ReplaceContinueWithBreak | 0 | runtime/source |
| c760f3303a614913b553488a39635a51 | [src/gzkit/governance/req_coverage.py:133](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:133) | core/NumberReplacer | 0 | runtime/source |
| 7bf83a9041b345b9bafac51bb0c279d1 | [src/gzkit/governance/req_coverage.py:133](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:133) | core/NumberReplacer | 1 | runtime/source |
| e31e0a2c18794937bf7fc0fea95e7e02 | [src/gzkit/governance/req_coverage.py:147](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/req_coverage.py:147) | core/ReplaceTrueWithFalse | 1 | runtime/source |

### tautological_tests — 341 survivors / 580 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| e422b81838f34a3188b0693efd112aa6 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| dd96a1710d1846c3a71e4f08a183e5ab | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| c16365eaf256451a921e8fe4165f9f3b | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| 5711e20b22d342808980ebacf39e2852 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| 4767bbcaf974413581d2f8599341ffbd | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| ddfd9a207e7144b8a6bc9771e933972f | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 2f00015a71c74211a125e11ce1c4e766 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| a725efcbb17d4142b4adf6b4d2efa1a2 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| 17eea0aabb3049809c3557bfc8b2649f | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| 09959a3d5cd54cf2b046c3ff7d061ece | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| 0b50e0530f124cc2b4d19e551656aa00 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| 13bd0442dbc04abcb8ef5f04a88aca9a | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Add | 1 | postponed |
| fc59e08d81e6408797f7eaaf6b20d8ff | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_BitAnd | 1 | postponed |
| 6ed3c2f2fda44c58843a5ce867fbe762 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_BitXor | 1 | postponed |
| b08f171d06e6401182950247489ecadf | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Div | 1 | postponed |
| 0bc31df6fc594e3094ace698c16c34c9 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 1 | postponed |
| aa1e66853d8643da94bfd7e77455f925 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_LShift | 1 | postponed |
| 040651c877bc41b3bd531a02bd7d0633 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Mod | 1 | postponed |
| 244055fe565c4900a995564a491ca355 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Mul | 1 | postponed |
| 001badb58ac24c979a589285b5fd5669 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Pow | 1 | postponed |
| c0480efac4874034b9135d18fd8159cb | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_RShift | 1 | postponed |
| a7e8717516094162bfcb095d02f01415 | [src/gzkit/tautological_tests.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:41) | core/ReplaceBinaryOperator_BitOr_Sub | 1 | postponed |
| e1646def63da40d7941781b5a2c33458 | [src/gzkit/tautological_tests.py:43](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:43) | core/ZeroIterationForLoop | 0 | runtime/source |
| 875d3dc62abf480a893946a39184edaa | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Add | 2 | postponed |
| c3cff6fbe2b54c55bbb38e9b8e3ed4db | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_BitAnd | 2 | postponed |
| 72280f0c0635491b884882729610b24a | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_BitXor | 2 | postponed |
| 89da5829d7864006af0ac03a9473875f | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Div | 2 | postponed |
| 1ce93cf2845d4348b308647988d99c70 | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 2 | postponed |
| 36ef2953deb44a3cbe1cbc235cfb785d | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_LShift | 2 | postponed |
| 04ddc104d23e405090bdeb52c329ffa7 | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Mod | 2 | postponed |
| c444a38485b7426eba225a00efd40c5a | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Mul | 2 | postponed |
| f441c8785ed149aea2a0409233868c30 | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Pow | 2 | postponed |
| bf5ff597dda646b7b7859ac5644b50d6 | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_RShift | 2 | postponed |
| 17610a71a4f74d70a8362ffd4b2c30e4 | [src/gzkit/tautological_tests.py:49](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:49) | core/ReplaceBinaryOperator_BitOr_Sub | 2 | postponed |
| 32d936b377384fe18fd750be24a2dc65 | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_Gt | 0 | runtime/source |
| 85c22bb772974f5a984805941b4a0002 | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_GtE | 0 | runtime/source |
| 1ac61f4450c34103a0a9ab08ee131bcc | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_Is | 0 | runtime/source |
| 5910cad433d34be8bd4de07b1e86bdaf | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_IsNot | 0 | runtime/source |
| bf4d423f9b404fddbc46b68c0466d35f | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_Lt | 0 | runtime/source |
| 6e01eb947f3b47049e6f0954c34d2616 | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_LtE | 0 | runtime/source |
| c9e0ab2da624435ca1c150c6465dc77f | [src/gzkit/tautological_tests.py:63](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:63) | core/ReplaceComparisonOperator_Eq_NotEq | 0 | runtime/source |
| 8bdf33d1d1f34e3385f861503438a181 | [src/gzkit/tautological_tests.py:64](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:64) | core/ReplaceAndWithOr | 3 | runtime/source |
| 092d039d441c4562a759ebea3015ff00 | [src/gzkit/tautological_tests.py:66](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:66) | core/ReplaceTrueWithFalse | 2 | runtime/source |
| 3909157cdc1d468582ddc8c0f69fc952 | [src/gzkit/tautological_tests.py:67](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:67) | core/NumberReplacer | 0 | runtime/source |
| c4aa53f19f3343348ec757ef649177a8 | [src/gzkit/tautological_tests.py:67](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:67) | core/NumberReplacer | 1 | runtime/source |
| 834032029aa34fa6a249eb4c77cd130a | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Add | 3 | postponed |
| 75331d2af74b45d48d5062312492e4c4 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_BitAnd | 3 | postponed |
| 33a9cbaec2a94e0ab18b24dc3fc0d385 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_BitXor | 3 | postponed |
| aa4d7da436364f33a10a6f5277486141 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Div | 3 | postponed |
| 14f5a7214f1b4727a72c2063478ab6be | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 3 | postponed |
| 1d1a698d66f74b1592a5c41a8ea84c83 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_LShift | 3 | postponed |
| 96f901baccf04575a26ef4776dc14d16 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Mod | 3 | postponed |
| e6c974eb760e4470a56547c5324b49dc | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Mul | 3 | postponed |
| 3b99f380b3a6483b93f1455034ee5ab3 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Pow | 3 | postponed |
| dda15079507240fb84db424b6b3dcd8d | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_RShift | 3 | postponed |
| 4ad9e4d8e462432ea61c8822498f41d0 | [src/gzkit/tautological_tests.py:70](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:70) | core/ReplaceBinaryOperator_BitOr_Sub | 3 | postponed |
| e404073a51484c1388d74ce9ac61205c | [src/gzkit/tautological_tests.py:74](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:74) | core/ReplaceTrueWithFalse | 3 | runtime/source |
| f77921680c1a497e89b52a1ba1c2db96 | [src/gzkit/tautological_tests.py:81](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:81) | core/ReplaceFalseWithTrue | 1 | runtime/source |
| 32f399cbb9b845189dedc18283c7aa2b | [src/gzkit/tautological_tests.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:97) | core/ReplaceOrWithAnd | 2 | runtime/source |
| 353a4e98ce004ba4a6c4ccb991dd4a6b | [src/gzkit/tautological_tests.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:97) | core/NumberReplacer | 2 | runtime/source |
| 56f9f5f254b049ee86b33bd32557bc69 | [src/gzkit/tautological_tests.py:97](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:97) | core/NumberReplacer | 3 | runtime/source |
| 9ef58e626d9d4e58be61a3fb37c437b7 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Add | 4 | postponed |
| e144b4b571274434a983a5a7e6ac1476 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_BitAnd | 4 | postponed |
| 535eef2db2d14736a4762be5114f5f4e | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_BitXor | 4 | postponed |
| 34c2037a225f45958ed4ef2284381790 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Div | 4 | postponed |
| fd647428c6ee45ab8ed8541f3417013f | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 4 | postponed |
| 2fbc1ff1b45f40078a1830f31e22ecc9 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_LShift | 4 | postponed |
| dcbc066de1334611bc866ef42d6d1429 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Mod | 4 | postponed |
| 7e97508216434b748a366b6be30732e1 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Mul | 4 | postponed |
| b41cb80afd594e33bb1a507e057e840f | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Pow | 4 | postponed |
| f104ffdbca1b4afa9ce745f0beb00296 | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_RShift | 4 | postponed |
| f66ebe53b0c54c0aa70bdb88ab23a5fa | [src/gzkit/tautological_tests.py:104](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:104) | core/ReplaceBinaryOperator_BitOr_Sub | 4 | postponed |
| 28e4589b8d3e43fa9de2581fbf24aeda | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Add | 5 | postponed |
| a07b459365cd4944af7c416f11eb1a95 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_BitAnd | 5 | postponed |
| 96109fe97ba44ab8b55e59ac313ec9fa | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_BitXor | 5 | postponed |
| d4d51e58b7584a01a86395f85f64010e | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Div | 5 | postponed |
| b67286d2367541ea9ddac4dc5f759902 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 5 | postponed |
| 021aac0b65d545babbc56fd89b07c417 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_LShift | 5 | postponed |
| d525b952354e4c068fa9be2c7b597291 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Mod | 5 | postponed |
| be0f431359be48b589a5ba5831bf0286 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Mul | 5 | postponed |
| 7f595690fc66447991043a1abfa8b1d7 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Pow | 5 | postponed |
| f397819a967d457d85cbf63632175686 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_RShift | 5 | postponed |
| bbcc1d6897c24176819f39e8c63748a6 | [src/gzkit/tautological_tests.py:111](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:111) | core/ReplaceBinaryOperator_BitOr_Sub | 5 | postponed |
| ebd975b6c3ea4832885b1c5a5608cb73 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Add | 6 | postponed |
| 966cd14d2bd04cde946f54abca12912e | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_BitAnd | 6 | postponed |
| f9f88f09e081426f8ed2ea2df50b1883 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_BitXor | 6 | postponed |
| a290a510a2484c59893a4fe6ee987dcd | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Div | 6 | postponed |
| c7bb20ab5e484c63b93397cfe87ac267 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 6 | postponed |
| 860976b8c5624dc8a2b97b4ac8925255 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_LShift | 6 | postponed |
| a78b085ffaff41b093f75a631e22cdbc | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Mod | 6 | postponed |
| e4131c07850f4976a7f7a50aa6292f09 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Mul | 6 | postponed |
| 86ffb48120f14308b66e90056f7023f4 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Pow | 6 | postponed |
| a979d274704446889ae06c6eae6bd155 | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_RShift | 6 | postponed |
| 7ad9b704241a4b57bd21f3bb5de89b1f | [src/gzkit/tautological_tests.py:137](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:137) | core/ReplaceBinaryOperator_BitOr_Sub | 6 | postponed |
| 5a9397a3a9354ad6841b9c675a800214 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Add | 7 | postponed |
| 5306cbf16f664461848e90e8ab8111e7 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_BitAnd | 7 | postponed |
| c8b50dec9dd84e218deed93239ffc982 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_BitXor | 7 | postponed |
| cbd6915c87a5427d98760d18b62daa2e | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Div | 7 | postponed |
| c02c1563708e4148a73a5d7fb23e0172 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 7 | postponed |
| 1ad7eff4ef294f0f826d4b5f1cadb99d | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_LShift | 7 | postponed |
| 0ca4868f4f4542b5b364161e313bf3e6 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Mod | 7 | postponed |
| 96469a8791774beeb047498767f769f0 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Mul | 7 | postponed |
| 7ab977435d5e4f9a92df42fe7fa03449 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Pow | 7 | postponed |
| 7aa99431fbe94343ae9d9db21b11e359 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_RShift | 7 | postponed |
| 5f633b3aeb43455590e7ba0ecd4c005e | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Sub | 7 | postponed |
| b0d0c39fdfce401ea4c831e54df8cd20 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Add | 8 | postponed |
| bb926fc960d4406ba172f2721669947c | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_BitAnd | 8 | postponed |
| 9900d755f76947089b4f885cdee66926 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_BitXor | 8 | postponed |
| c70ff53974a343a088c7ba729a582e9b | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Div | 8 | postponed |
| d8a750beaaf5458ca24ca50ba4927d76 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 8 | postponed |
| 33c22923cdd64ee491a4491da29e5b46 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_LShift | 8 | postponed |
| c63e763a6eab464195c09d850bfd6c06 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Mod | 8 | postponed |
| e347ec6789e24ecfbff32df5b9224738 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Mul | 8 | postponed |
| 5831e31f924341a4822f6a40fb9065f6 | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Pow | 8 | postponed |
| 17552a20c789466aa4beac0c88fe158c | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_RShift | 8 | postponed |
| 4d81ad0ccc92416caef6aebb529bb0ef | [src/gzkit/tautological_tests.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:139) | core/ReplaceBinaryOperator_BitOr_Sub | 8 | postponed |
| 34769e6039574c2f82e1a64aac869e70 | [src/gzkit/tautological_tests.py:140](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:140) | core/NumberReplacer | 4 | runtime/source |
| a34ab9ffabd54a0f9aa099982271e3ca | [src/gzkit/tautological_tests.py:140](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:140) | core/NumberReplacer | 5 | runtime/source |
| d4d7d2a7454f437a912961dfb3ecb12e | [src/gzkit/tautological_tests.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:176) | core/AddNot | 15 | runtime/source |
| 55d3416cb6fc4ce1a393d5f99859c770 | [src/gzkit/tautological_tests.py:176](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:176) | core/ReplaceUnaryOperator_Delete_Not | 1 | runtime/source |
| a20e3a5aeed7475d81f8f4d4b6d822e2 | [src/gzkit/tautological_tests.py:177](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:177) | core/ReplaceFalseWithTrue | 3 | runtime/source |
| dd6689ea714c481d9460d6fdbd7bcd4b | [src/gzkit/tautological_tests.py:178](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:178) | core/ReplaceComparisonOperator_Eq_Is | 1 | runtime/source |
| 3d13f426e6ec42b9b7c9472020af793b | [src/gzkit/tautological_tests.py:178](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:178) | core/ReplaceOrWithAnd | 3 | runtime/source |
| cefa14df6f6b401780478e39387ccc06 | [src/gzkit/tautological_tests.py:179](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:179) | core/ReplaceTrueWithFalse | 6 | runtime/source |
| 7d1d80d984f04d1782301649ca8bf7a5 | [src/gzkit/tautological_tests.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:180) | core/ReplaceAndWithOr | 8 | runtime/source |
| 77ebc50a714a4c18af0aaa7ab0fb7c73 | [src/gzkit/tautological_tests.py:182](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:182) | core/ReplaceAndWithOr | 9 | runtime/source |
| e76cc3d6976e4995b314504ea818ed28 | [src/gzkit/tautological_tests.py:182](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:182) | core/ReplaceAndWithOr | 10 | runtime/source |
| 95aab99554e942fc9c8ac07e4733bed3 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Add | 9 | postponed |
| e5cc100f14f5408a92493e7c88d02a4b | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_BitAnd | 9 | postponed |
| 70ba8c7899e94bf1818b52adc095cc35 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_BitXor | 9 | postponed |
| 09bbefb104d14328bf670a4bbe974670 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Div | 9 | postponed |
| 1512d5baa19744cea2e102a7d26e04ac | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 9 | postponed |
| a9abef4b989244c78e3611d0f2e141e5 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_LShift | 9 | postponed |
| 0604a2b477424e0680752b123ad1d1e1 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Mod | 9 | postponed |
| bcb40a5210cf42b3a47c9b26e7d570a5 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Mul | 9 | postponed |
| ca0d3cd325c44c69b9456b6079b39e00 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Pow | 9 | postponed |
| 99730fecc9aa412f8605f1ca98f32765 | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_RShift | 9 | postponed |
| 18087057b28846eb97beb4af24e9230a | [src/gzkit/tautological_tests.py:188](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:188) | core/ReplaceBinaryOperator_BitOr_Sub | 9 | postponed |
| 8746cbceccc8412a87d35c60775b2147 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Add | 10 | postponed |
| b43d97a20a7a4f9798146a9340ea2042 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_BitAnd | 10 | postponed |
| daca909468fb4bfc974cb5fcc113a1e8 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_BitXor | 10 | postponed |
| 4f6a94b4899242878ac0fa8cab6ac721 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Div | 10 | postponed |
| 2e51bf9ab70e4c9fa57120faf51d2cce | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 10 | postponed |
| c800e99286d54066a61a0dc9d29beab6 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_LShift | 10 | postponed |
| 684d3b5323e443669ca186404c73ce49 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Mod | 10 | postponed |
| 9660274c30b940358b58749417caf7d3 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Mul | 10 | postponed |
| ba6f2363cead439999f62f6d69fb7ddc | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Pow | 10 | postponed |
| ab837f93d6eb45d18f378630b79da79f | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_RShift | 10 | postponed |
| d35cabdb4b064f408c259e544b883d58 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Sub | 10 | postponed |
| 8b1f9222779146a381585a06d8930d35 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Add | 11 | postponed |
| 83e0ce489f894cd8812d71c369c5707b | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_BitAnd | 11 | postponed |
| 7a07b2bcea6e43e09d433bff57e15904 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_BitXor | 11 | postponed |
| aacbf44c10b14c388ec73054d41f131d | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Div | 11 | postponed |
| 57c342af3c5a43fda2d8656ddc835015 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 11 | postponed |
| 974f7e5e3a3d40daa87e5eb0bd2bf31c | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_LShift | 11 | postponed |
| 17c2e9bf88e9490a92ac3d55ec56a4e8 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Mod | 11 | postponed |
| 0104106f10e4450d898255791b813d48 | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Mul | 11 | postponed |
| 7416a08b72e24c3e9878de706b0ae3ed | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Pow | 11 | postponed |
| 396929a54deb44dd8dc1463b598c57dc | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_RShift | 11 | postponed |
| c922489e72fd4cd2ac6003e1433ab36c | [src/gzkit/tautological_tests.py:190](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:190) | core/ReplaceBinaryOperator_BitOr_Sub | 11 | postponed |
| 76f22e1ead4b4f6e870f4f60e33a049d | [src/gzkit/tautological_tests.py:204](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:204) | core/ReplaceOrWithAnd | 4 | runtime/source |
| 1bca2b3a571944deb68b16c8639e65fc | [src/gzkit/tautological_tests.py:204](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:204) | core/ReplaceComparisonOperator_GtE_Eq | 0 | runtime/source |
| ed6af1ae6bd14603a1118c4b24a669e1 | [src/gzkit/tautological_tests.py:204](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:204) | core/ReplaceComparisonOperator_GtE_Gt | 0 | runtime/source |
| fa8092f3eff6437abb585eb53d68551b | [src/gzkit/tautological_tests.py:204](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:204) | core/ReplaceComparisonOperator_GtE_Is | 0 | runtime/source |
| ef38e5b4de154d7a9b55979d040b4f6d | [src/gzkit/tautological_tests.py:205](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:205) | core/ReplaceFalseWithTrue | 4 | runtime/source |
| a3a5d15635a745e581cac9f74675f818 | [src/gzkit/tautological_tests.py:213](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:213) | core/ReplaceComparisonOperator_IsNot_NotEq | 0 | runtime/source |
| 8b46d3a192a048a6918caa27dfc8bf67 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_BitAnd | 0 | runtime/source |
| 3ecf3b00518240e09db9bfaedda2aa76 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_BitOr | 0 | runtime/source |
| c0413831407140d6a18df42b7916059c | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_BitXor | 0 | runtime/source |
| bced0f4faf184a2b84de8a80213b426e | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_Div | 0 | runtime/source |
| 3e057e4bd56a4f1fb667b5fd6c17b5cb | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_FloorDiv | 0 | runtime/source |
| fe9f425a8433445dadb1f1d752db5be2 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_LShift | 0 | runtime/source |
| fd4def0d0d1b42a086303a7c70efc072 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_Mod | 0 | runtime/source |
| a7314eb1f3a742df842f8126e680fd24 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_Mul | 0 | runtime/source |
| 49a70436d72e4668924e1c9ffc858eb8 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_Pow | 0 | runtime/source |
| 4a52fb75a8eb41678020082417544810 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_RShift | 0 | runtime/source |
| ff31356e6ab34a2dbed37a5e725c38c3 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/ReplaceBinaryOperator_Add_Sub | 0 | runtime/source |
| ae090fbdd50a4d00b4352063d45fe923 | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/NumberReplacer | 6 | runtime/source |
| d8589cca870d49fe91faac1ba57e816b | [src/gzkit/tautological_tests.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:214) | core/NumberReplacer | 7 | runtime/source |
| 123c5c4da5f944bab1c91180a6650fed | [src/gzkit/tautological_tests.py:223](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:223) | core/NumberReplacer | 8 | runtime/source |
| c06056fd6ee342ffa6cb5aaadb16c8e7 | [src/gzkit/tautological_tests.py:223](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:223) | core/NumberReplacer | 9 | runtime/source |
| e6a240330128495fa650c23655215e05 | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Add | 12 | postponed |
| 9866020199cf4701b31f0ec5f9d9eefa | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_BitAnd | 12 | postponed |
| 5ecfaae13caf4e50b2ef12d76260591a | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_BitXor | 12 | postponed |
| 2b8e36bec2d745baa1dd1987a50bdd3a | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Div | 12 | postponed |
| 0a28fffba4954bde85e3ade5e088b457 | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 12 | postponed |
| 709cc6d6c90041f29178b064aade710f | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_LShift | 12 | postponed |
| 45a149425d13447abc95f27b1e3c395d | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Mod | 12 | postponed |
| da686315cd7e4636a3d7b2c59593939a | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Mul | 12 | postponed |
| c3d2ac3bb38541018b54cc74b5d9be9c | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Pow | 12 | postponed |
| 30b4cc7c90394464b7067e4231670e81 | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_RShift | 12 | postponed |
| 46739b23505e4ea4828d28e9f571bd19 | [src/gzkit/tautological_tests.py:228](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:228) | core/ReplaceBinaryOperator_BitOr_Sub | 12 | postponed |
| dc1739c00419463d8151f2024d525bb7 | [src/gzkit/tautological_tests.py:232](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:232) | core/AddNot | 22 | runtime/source |
| 804ab9cba3604f5dbdfa4d2fcd060a68 | [src/gzkit/tautological_tests.py:234](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:234) | core/ReplaceAndWithOr | 13 | runtime/source |
| a23bd555e5614fef820d447e249679ca | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_Gt | 2 | runtime/source |
| 34b292320cc14e018810aded825ab054 | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_GtE | 2 | runtime/source |
| 9cf3b4678cd842c29e4f38860c7169f1 | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_Is | 2 | runtime/source |
| 88f130c3b10c43f1b539732f1ad610bc | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_IsNot | 2 | runtime/source |
| 24ddd0d6e58047aba09ae3235021d688 | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_Lt | 2 | runtime/source |
| a0bc2ff4fd454642a9be9cf44ea5288a | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_LtE | 2 | runtime/source |
| 0b9a6b5123b64f0a9882684fb9ebd58d | [src/gzkit/tautological_tests.py:235](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:235) | core/ReplaceComparisonOperator_Eq_NotEq | 2 | runtime/source |
| b88baa0984ce4f4d96c5a6653248a9a4 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Add | 13 | postponed |
| f1ce203f983649bdbe94b0554d23a482 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_BitAnd | 13 | postponed |
| 2bda1568731c4214b4bc93ce984c0825 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_BitXor | 13 | postponed |
| 464906c9287d4be2ae563c07b048eb10 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Div | 13 | postponed |
| d56c50ce585b470188f535e84bc1a5d0 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 13 | postponed |
| 7be52348dd2145ce92d23c4c999289e9 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_LShift | 13 | postponed |
| df1de634c93a4dc4beb2a3d5ecf5487a | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Mod | 13 | postponed |
| f051e0cc32ff4f04b7f06cfe143b7436 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Mul | 13 | postponed |
| b455bb059de14e289e9a134758d1a782 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Pow | 13 | postponed |
| a9ebb0913d3747188dd9fcefae07ab19 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_RShift | 13 | postponed |
| 07099b4f015d4c42a8f05ee96e9174a7 | [src/gzkit/tautological_tests.py:241](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:241) | core/ReplaceBinaryOperator_BitOr_Sub | 13 | postponed |
| 0ed5ed4d33dc4bbf97d954d2b8275c76 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Add | 14 | postponed |
| 14d89207dbfd461895a7d41dc1ff40b2 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_BitAnd | 14 | postponed |
| 08717dd3cbbb4730acc7019387766037 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_BitXor | 14 | postponed |
| 8c95ab86b0474e96a632a345151cf842 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Div | 14 | postponed |
| e7e3535208ec457cba34c6a3e48314a7 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 14 | postponed |
| 50708d36076747549933c369aa8db601 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_LShift | 14 | postponed |
| 63d974dd7fac45a184e3504036ffde66 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Mod | 14 | postponed |
| 8babde1028134274a072ec976b8118a7 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Mul | 14 | postponed |
| 9208350c94724679a4f62848d993d303 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Pow | 14 | postponed |
| 8bd76cae087b427cad1706189100ff93 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_RShift | 14 | postponed |
| deb5af4cf73f4d3e8f5bdfd102e6f762 | [src/gzkit/tautological_tests.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:269) | core/ReplaceBinaryOperator_BitOr_Sub | 14 | postponed |
| 882e1c629382430497ca4f1a076d631f | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Add | 15 | postponed |
| 24bd1b7743c542cda95a0ab4188bbfd7 | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_BitAnd | 15 | postponed |
| 7ed28d52570f477790d893ae8620c39e | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_BitXor | 15 | postponed |
| 8e9fcc6c5df94237a6fcddd6bb307ce7 | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Div | 15 | postponed |
| 1eac5e621e4c45449ad8f80293339a5d | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 15 | postponed |
| 1de1c36efabb45859b546c59f4368157 | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_LShift | 15 | postponed |
| b0601c18739a410fa214d576015e0dbf | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Mod | 15 | postponed |
| f71eff44591343fc9182165513dcf38a | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Mul | 15 | postponed |
| 7ec8b716b6154707afbf3e4112b651b6 | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Pow | 15 | postponed |
| e86a1c579a624925a609424445d9e010 | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_RShift | 15 | postponed |
| ba0c11c32578482f81464a1d170b79fd | [src/gzkit/tautological_tests.py:277](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:277) | core/ReplaceBinaryOperator_BitOr_Sub | 15 | postponed |
| 701a2e1a8fdd49fca97f043f00843f78 | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Add | 16 | postponed |
| 22d4167efca2448e8473dadc2ffa02fa | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_BitAnd | 16 | postponed |
| 0c5efd206cfe42309ab12f9387ed30ff | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_BitXor | 16 | postponed |
| a787b92c899d4262be9c36541806fd3f | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Div | 16 | postponed |
| b31afa535f604050b4fec9846369b8eb | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 16 | postponed |
| c549ad1623fb400b95a6974aea5a3c0f | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_LShift | 16 | postponed |
| 6fda3e3fe56148f68a4a917d712c45c1 | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Mod | 16 | postponed |
| 4ff4aafd795a4522b88530994516ccf7 | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Mul | 16 | postponed |
| e58975b970a446e7beb386dad16a290a | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Pow | 16 | postponed |
| 0683c69f4b694b11b073a1df5667b757 | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_RShift | 16 | postponed |
| 76bee3a2619845d585d4ae52aeaba4ff | [src/gzkit/tautological_tests.py:286](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:286) | core/ReplaceBinaryOperator_BitOr_Sub | 16 | postponed |
| 4e18ff24228c4204ae5fc6091f59c957 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Add | 17 | postponed |
| 6fd2a95f980f4dc2beb65d323e8fd492 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_BitAnd | 17 | postponed |
| f6966c91bc544d6c8c290b6501e29eda | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_BitXor | 17 | postponed |
| 631832fabdc140048da637f2c3e6750b | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Div | 17 | postponed |
| 406339c4e8b94f5085f78bfdc8a5dba1 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 17 | postponed |
| 9d8a4da7e286497bac499981769ea1e3 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_LShift | 17 | postponed |
| b44107b5ad2a43d2902c732d5f10e0ca | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Mod | 17 | postponed |
| 3150ea6431774f8181f74327ab416b28 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Mul | 17 | postponed |
| 0287ce5663ce4eb98bee124d8605a424 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Pow | 17 | postponed |
| 14dfb6f0a7fb4bbdbace9355b570ada7 | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_RShift | 17 | postponed |
| 96937c2813c6422f982434454c6b3f6c | [src/gzkit/tautological_tests.py:292](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:292) | core/ReplaceBinaryOperator_BitOr_Sub | 17 | postponed |
| f2064750ec9b44a3a9bb56f8d65e229a | [src/gzkit/tautological_tests.py:293](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:293) | core/ZeroIterationForLoop | 6 | runtime/source |
| 9d2c91de094f497f98709ba720d1cf12 | [src/gzkit/tautological_tests.py:295](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:295) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| 91a62d1d200548a0a582b2d472602ced | [src/gzkit/tautological_tests.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:301) | core/ReplaceAndWithOr | 19 | runtime/source |
| ec09741da679404693cf1f5ca69de233 | [src/gzkit/tautological_tests.py:305](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:305) | core/AddNot | 25 | runtime/source |
| 74a2d63ba2ae48c1b12d2fa7ccdc866a | [src/gzkit/tautological_tests.py:305](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:305) | core/ReplaceComparisonOperator_Is_IsNot | 0 | runtime/source |
| 4df89dd39a60421bbfbed5952b158fe1 | [src/gzkit/tautological_tests.py:306](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:306) | core/ReplaceContinueWithBreak | 2 | runtime/source |
| 97d254432209427bb30938d9bfa2d55c | [src/gzkit/tautological_tests.py:307](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:307) | core/ZeroIterationForLoop | 7 | runtime/source |
| 6b4543c5d91047d9beef62bf2b907953 | [src/gzkit/tautological_tests.py:308](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:308) | core/AddNot | 26 | runtime/source |
| bb28386c68fc44fba5bf90fd17c332f4 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Add | 18 | postponed |
| 805fe872272e426bbeeebe6464305bcb | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_BitAnd | 18 | postponed |
| 65879f8a6eda41a9ad4e68e914a1da9f | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_BitXor | 18 | postponed |
| 76d8f904d4f349478b7598baf8406740 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Div | 18 | postponed |
| c96c6200bb6246f4a949aeabbfc71908 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 18 | postponed |
| c04e3cee0f694d1d9c36ecd3da378595 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_LShift | 18 | postponed |
| 714b03c2dc4e4a59b3271bbfaae92ea4 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Mod | 18 | postponed |
| dd81dde0a3884cdab72c9c34468d593a | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Mul | 18 | postponed |
| 2fe0b27ef5304c1a9eaf720a7f081e43 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Pow | 18 | postponed |
| 0d8c2bf1e0f04e3b849b155365c2c004 | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_RShift | 18 | postponed |
| 7822fd782b244644a5c615c14182cb7b | [src/gzkit/tautological_tests.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:313) | core/ReplaceBinaryOperator_BitOr_Sub | 18 | postponed |
| 3574d50dd17346e59bc5b76107ce9bab | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_GtE | 3 | runtime/source |
| 01f7e541039340d5817531648c44d28f | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_Is | 3 | runtime/source |
| 2444a4566a154c38b7ceb40b5323e3ad | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_LtE | 3 | runtime/source |
| f5914c2ef8b84cf596c6fe9039d823b9 | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceAndWithOr | 21 | runtime/source |
| df2cb5d7567543a3b5f82f25acbd9c38 | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_GtE | 4 | runtime/source |
| 5223ea5fbd9a493ea438ec8421221eb6 | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_Is | 4 | runtime/source |
| e3b043ea4fe3411298ef726bad0766b9 | [src/gzkit/tautological_tests.py:329](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:329) | core/ReplaceComparisonOperator_Eq_LtE | 4 | runtime/source |
| 587df594ed32401699047cc135090be6 | [src/gzkit/tautological_tests.py:331](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:331) | core/ReplaceAndWithOr | 22 | runtime/source |
| e25d95324fc3467eb0d2dcacd9437be3 | [src/gzkit/tautological_tests.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:332) | core/ReplaceAndWithOr | 23 | runtime/source |
| 6e9693516da54be4a9e68043293b6b0d | [src/gzkit/tautological_tests.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:332) | core/ReplaceAndWithOr | 24 | runtime/source |
| c3b3ea7d7a40428a96181c8218b12fd0 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Add | 19 | postponed |
| 9df64406d44e4d39bd65978dc602a1e5 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_BitAnd | 19 | postponed |
| 7923cb7152fe436892c6b3f710dc6868 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_BitXor | 19 | postponed |
| 082e72e8aa03425ba4029a8d3f5d30d6 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Div | 19 | postponed |
| b6885ad6fc67454fa87318d363e4d881 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 19 | postponed |
| 7e847f5140c04899aea9a32d18c25943 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_LShift | 19 | postponed |
| 270d0f02107f442ab70b575f3d64502b | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Mod | 19 | postponed |
| 69641c0e6b084e3a9e952511b07a45e1 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Mul | 19 | postponed |
| 599ba3bdf3a049c89df1c0ab9800668c | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Pow | 19 | postponed |
| c766966592c244e09705176d44fcbe55 | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_RShift | 19 | postponed |
| 2c714367b02244f08e11c801940e3ddf | [src/gzkit/tautological_tests.py:349](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:349) | core/ReplaceBinaryOperator_BitOr_Sub | 19 | postponed |
| 1be771c63f114462b7a536ce38a39ea2 | [src/gzkit/tautological_tests.py:395](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:395) | core/AddNot | 33 | runtime/source |
| 3bd2c3bac56d4f13bc5863aade3ae279 | [src/gzkit/tautological_tests.py:395](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:395) | core/ReplaceUnaryOperator_Delete_Not | 9 | runtime/source |
| ae6aa6a8c9fb494fb0033e67a89358d4 | [src/gzkit/tautological_tests.py:406](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:406) | core/ReplaceAndWithOr | 29 | runtime/source |
| 268dfd9aa35e49f1b76050e2765e164e | [src/gzkit/tautological_tests.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:407) | core/ReplaceAndWithOr | 30 | runtime/source |
| e8f3b541a71b457294483aef2985f6e7 | [src/gzkit/tautological_tests.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:407) | core/ReplaceComparisonOperator_Eq_GtE | 5 | runtime/source |
| ded62f20f0864c6cb7347e3a8c7a7784 | [src/gzkit/tautological_tests.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:407) | core/ReplaceComparisonOperator_Eq_Is | 5 | runtime/source |
| 8ee3fe66799a427a8cf1772f35d97e35 | [src/gzkit/tautological_tests.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:407) | core/ReplaceComparisonOperator_Eq_LtE | 5 | runtime/source |
| 6c281d2b02aa461cbfed0e0341ecf0e9 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Add | 20 | postponed |
| b0e6d511116c4b3d87a99297e49e2a4c | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_BitAnd | 20 | postponed |
| c9d0deb6a5a44bf48f1a1d07fc485181 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_BitXor | 20 | postponed |
| b0baf3b8284342ab8182dcc4909a8124 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Div | 20 | postponed |
| 24b0ca62e5c14d94b04e50e906980cfc | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 20 | postponed |
| 534838e5be8d4a60a4d584fd7288ef95 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_LShift | 20 | postponed |
| d84d6cde7a8d4476bb874bb3d5fcc126 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Mod | 20 | postponed |
| 3f3d8bd8d6724b9184faca7868af6f8e | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Mul | 20 | postponed |
| 46c419c4c4ac4773bfd0cf3e9a89b6a7 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Pow | 20 | postponed |
| 39a4ff7aa92c47998a6efcd5d0b8299e | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_RShift | 20 | postponed |
| 006de830bd3e489ab7606e8ef4806b12 | [src/gzkit/tautological_tests.py:414](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:414) | core/ReplaceBinaryOperator_BitOr_Sub | 20 | postponed |
| d2f6c943a821475a96ad03f25e357f71 | [src/gzkit/tautological_tests.py:426](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:426) | core/ReplaceComparisonOperator_Eq_GtE | 6 | runtime/source |
| a81326014320408689c783a663bd046e | [src/gzkit/tautological_tests.py:426](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:426) | core/ReplaceComparisonOperator_Eq_Is | 6 | runtime/source |
| 3d7d18deb238424ebc1e692601249ffd | [src/gzkit/tautological_tests.py:426](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:426) | core/ReplaceComparisonOperator_Eq_LtE | 6 | runtime/source |
| c99145cd6b0b4f35825c56da7ec4f2b5 | [src/gzkit/tautological_tests.py:449](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:449) | core/ExceptionReplacer | 0 | runtime/source |
| b95c37742dcc4d2085fb46fd0a11c924 | [src/gzkit/tautological_tests.py:453](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:453) | core/ReplaceComparisonOperator_Eq_Is | 7 | runtime/source |
| 3ba02599a21748b68094ed1e056cb026 | [src/gzkit/tautological_tests.py:453](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:453) | core/ReplaceComparisonOperator_Eq_Lt | 7 | runtime/source |
| 66bf055f63934c8f9e8480141f0759d3 | [src/gzkit/tautological_tests.py:453](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:453) | core/ReplaceComparisonOperator_Eq_LtE | 7 | runtime/source |
| 2f13be8dec4e4cbd97f113612a64eb75 | [src/gzkit/tautological_tests.py:454](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:454) | core/ReplaceContinueWithBreak | 7 | runtime/source |
| f4afd57b3ff04ff8a474a6deed26206a | [src/gzkit/tautological_tests.py:459](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:459) | core/ExceptionReplacer | 1 | runtime/source |
| 096f6340f0564c97b39c15bad97e22ec | [src/gzkit/tautological_tests.py:459](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:459) | core/ExceptionReplacer | 2 | runtime/source |
| e4eb9b10dea84c0aae932218fffeceac | [src/gzkit/tautological_tests.py:460](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:460) | core/ReplaceContinueWithBreak | 8 | runtime/source |
| eb8af7872dd542d89b78387a3011be8b | [src/gzkit/tautological_tests.py:480](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:480) | core/ReplaceContinueWithBreak | 11 | runtime/source |
| 06a4ae172b954374b953b079284475a1 | [src/gzkit/tautological_tests.py:483](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:483) | core/ReplaceContinueWithBreak | 12 | runtime/source |
| 97e61abaab3e47dd94a71bdb94614b41 | [src/gzkit/tautological_tests.py:490](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:490) | core/ReplaceContinueWithBreak | 13 | runtime/source |
| 08769f97d44343098379b28b10acd14f | [src/gzkit/tautological_tests.py:493](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:493) | core/ReplaceContinueWithBreak | 14 | runtime/source |
| d0725438f8a24bf38b97b383b44fe212 | [src/gzkit/tautological_tests.py:502](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:502) | core/ReplaceContinueWithBreak | 15 | runtime/source |
| 5d55f338f1f0430ea90e3df1a5bf9a73 | [src/gzkit/tautological_tests.py:633](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:633) | core/NumberReplacer | 11 | runtime/source |
| fa7bc1f0755944fb9c8bbd63c57c10d9 | [src/gzkit/tautological_tests.py:633](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:633) | core/ReplaceComparisonOperator_Gt_NotEq | 0 | runtime/source |
| 4778577f7d454a30844fde4be2437cf9 | [src/gzkit/tautological_tests.py:634](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:634) | core/NumberReplacer | 14 | runtime/source |
| ef9e83c6db884057b0ee6f7d33368827 | [src/gzkit/tautological_tests.py:634](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:634) | core/NumberReplacer | 15 | runtime/source |
| ebe95264802f4dd0b6ba92779fd247fe | [src/gzkit/tautological_tests.py:636](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:636) | core/NumberReplacer | 17 | runtime/source |
| 8b2996a9ec734c138a57386c569730f4 | [src/gzkit/tautological_tests.py:636](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:636) | core/ReplaceComparisonOperator_Gt_Lt | 1 | runtime/source |
| 3c967daff01a4cc7971723ee650a3d83 | [src/gzkit/tautological_tests.py:636](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:636) | core/ReplaceComparisonOperator_Gt_NotEq | 1 | runtime/source |
| 598e01ab8e554bcdb34d5ad3e4599136 | [src/gzkit/tautological_tests.py:636](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:636) | core/NumberReplacer | 18 | runtime/source |
| 955952021e9642fca52222386016d342 | [src/gzkit/tautological_tests.py:637](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:637) | core/NumberReplacer | 20 | runtime/source |
| c6e019c25c774f6a993893b9a12cc36c | [src/gzkit/tautological_tests.py:637](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:637) | core/NumberReplacer | 21 | runtime/source |
| b7b9afda1185496fb0cea6c8a0358d22 | [src/gzkit/tautological_tests.py:638](/Users/jeff/Documents/Code/gzkit/src/gzkit/tautological_tests.py:638) | core/ReplaceContinueWithBreak | 17 | runtime/source |

### test_shape — 67 survivors / 117 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| 704846ba3aea470cbb08919e17e65df1 | [src/gzkit/test_shape.py:53](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:53) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| 54a2560fafe246de9389e8f481459dd9 | [src/gzkit/test_shape.py:56](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:56) | core/NumberReplacer | 0 | runtime/source |
| ab0a26dad97e4a18bda0329822cd8d60 | [src/gzkit/test_shape.py:56](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:56) | core/NumberReplacer | 1 | runtime/source |
| bf46a1d4427c47bba1598232ddeffbd6 | [src/gzkit/test_shape.py:57](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:57) | core/NumberReplacer | 2 | runtime/source |
| 73add73f7a74457cad864387fdfc698a | [src/gzkit/test_shape.py:57](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:57) | core/NumberReplacer | 3 | runtime/source |
| 9a499c6ea2da4d08ab2648ee5ef032eb | [src/gzkit/test_shape.py:69](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:69) | core/ReplaceTrueWithFalse | 1 | runtime/source |
| 4fa6aad47907452a9e02ae19616dbf2d | [src/gzkit/test_shape.py:81](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:81) | core/ReplaceTrueWithFalse | 2 | runtime/source |
| 07ab816c41554eb1b5d79ec2af3973b3 | [src/gzkit/test_shape.py:95](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:95) | core/RemoveDecorator | 1 | runtime/source |
| 2e49f81816104409b1eaf83b14defb8c | [src/gzkit/test_shape.py:98](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:98) | core/ReplaceUnaryOperator_Delete_Not | 0 | runtime/source |
| 0806dcb1eb674e2199a0ac2b2da14106 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Add | 0 | postponed |
| 4137882b461d4a1eb374409e535fbe63 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_BitAnd | 0 | postponed |
| 3e5721fa5ef14c1ebdd6130eadc8c82d | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_BitXor | 0 | postponed |
| 6f3b609c9ad344648898ea3751e737c8 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Div | 0 | postponed |
| fe156c24a4b64406b261cb475a9d9bc3 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 0 | postponed |
| f9a2f778257448c594e8438c67bb6b25 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_LShift | 0 | postponed |
| 84856fe88a094b548ea1fa80e38d7b46 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Mod | 0 | postponed |
| de4dbcf340a8433d86c0fa0cbbcc4dab | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Mul | 0 | postponed |
| 9446d7a7d9734092aa50d139d6eec98f | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Pow | 0 | postponed |
| 6cf24ddb0e8a4606a19d454a7146c416 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_RShift | 0 | postponed |
| a016b27d65a94fec9287936cbaf46141 | [src/gzkit/test_shape.py:101](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:101) | core/ReplaceBinaryOperator_BitOr_Sub | 0 | postponed |
| 64743e0b6f2c493593ec6444f77aafe9 | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/ReplaceBinaryOperator_Sub_BitAnd | 0 | runtime/source |
| b6fac8bbf1e14b3ebff97107195cac5c | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/ReplaceBinaryOperator_Sub_FloorDiv | 0 | runtime/source |
| fa5acbc7f04542db8e04e200c2ec40c4 | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/ReplaceBinaryOperator_Sub_Mul | 0 | runtime/source |
| 745a1e2a463843c9bbf6e9b3c2c22100 | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/ReplaceBinaryOperator_Sub_Pow | 0 | runtime/source |
| 5b88c3649dd947d7b8fa4d30a3de33cc | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/ReplaceBinaryOperator_Sub_RShift | 0 | runtime/source |
| ab2fb314fb104e80936da64743ab657e | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/NumberReplacer | 4 | runtime/source |
| 7e4be1d999254af0b048e3201d194bf5 | [src/gzkit/test_shape.py:103](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:103) | core/NumberReplacer | 5 | runtime/source |
| 0793711b0ff64cad892c2f0e9a5cd403 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Add | 1 | postponed |
| 82570e04055f4449ad106bd40390a14b | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_BitAnd | 1 | postponed |
| 5bcd75a25d34459f9ef4925d5c49b8db | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_BitXor | 1 | postponed |
| 78105ae91af249c68a6cdd3e875357fa | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Div | 1 | postponed |
| f3b719655e9e46ebb5699e1e010232b0 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 1 | postponed |
| 034c48387392454bb17604fc164e0210 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_LShift | 1 | postponed |
| 7d87c3f33d8d47c8a4c16677f92e5f4a | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Mod | 1 | postponed |
| 6e79cd12014f4f61845f6c75c20e4444 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Mul | 1 | postponed |
| 2be834b5cccc4587994ba3b7d81f89e8 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Pow | 1 | postponed |
| abe0c291cbc14b5cae43d2d039d8604a | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_RShift | 1 | postponed |
| ca9d6d35f5be44288066577a4bc543a7 | [src/gzkit/test_shape.py:110](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:110) | core/ReplaceBinaryOperator_BitOr_Sub | 1 | postponed |
| 413c9769abbb4cb4a39ed465088579cd | [src/gzkit/test_shape.py:117](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:117) | core/ReplaceComparisonOperator_Eq_GtE | 0 | runtime/source |
| 988bd97162b04331acbc79eaba77f750 | [src/gzkit/test_shape.py:117](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:117) | core/ReplaceComparisonOperator_Eq_Is | 0 | runtime/source |
| 08a2b472705c4aeeb0c16d771d0ccc23 | [src/gzkit/test_shape.py:128](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:128) | core/ReplaceTrueWithFalse | 3 | runtime/source |
| 582967d7d3f849ba9d019ce0e1fd0d3f | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Add | 2 | postponed |
| c388cc2bbe234899a4b04d87f878f41c | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_BitAnd | 2 | postponed |
| 03b7d809d8ce4fa69d390a48b96566ec | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_BitXor | 2 | postponed |
| 0666ca6ee39f4bf7ba37911b79081a1a | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Div | 2 | postponed |
| 192187b80a0a4b5fba781f2b908e98f7 | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 2 | postponed |
| 8380bb34bb0c4feaae5f88150502ff26 | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_LShift | 2 | postponed |
| 59e1d68566084c02856a2cb329834550 | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Mod | 2 | postponed |
| ebdb4bc9f87049ada88b21ee9255789a | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Mul | 2 | postponed |
| 72982f8d9a634423ae535ce2b2345df7 | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Pow | 2 | postponed |
| dcacd61e0962444294d5d35396fed54b | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_RShift | 2 | postponed |
| e3f1e9dfdc28486face7de067c414850 | [src/gzkit/test_shape.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:138) | core/ReplaceBinaryOperator_BitOr_Sub | 2 | postponed |
| f34287ae08e4438ea13443f8dfdec4c9 | [src/gzkit/test_shape.py:147](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:147) | core/ExceptionReplacer | 0 | runtime/source |
| 73c0eace8bea444d80afc9ce78c1a62d | [src/gzkit/test_shape.py:147](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:147) | core/ExceptionReplacer | 1 | runtime/source |
| 63c3415118ea4249997ca8f109e70d30 | [src/gzkit/test_shape.py:160](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:160) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| 4ccddb71684846159982a32bd11612ea | [src/gzkit/test_shape.py:163](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:163) | core/ReplaceContinueWithBreak | 2 | runtime/source |
| fd05fccd9cd24bc9909a0770f6a369f4 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_Add | 0 | runtime/source |
| f526bd863c7945e48fad15b5c7a2da75 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_BitAnd | 0 | runtime/source |
| c37bd01092eb4166954a8adf15fb4456 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_BitOr | 0 | runtime/source |
| 0079fa13dbab434fa39a2dabc37d7583 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_BitXor | 0 | runtime/source |
| 9405090aee14445ab59dea6363549939 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_FloorDiv | 0 | runtime/source |
| 5997db13b35c48cd952f135b2ef633f9 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_LShift | 0 | runtime/source |
| 3b47d1b76bbb42c9b7c370ea1078ea44 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_Mod | 0 | runtime/source |
| 3e897a41c6e04fa68a51d0072540c05b | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_Mul | 0 | runtime/source |
| fb36568866e7457486937993c2634144 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_Pow | 0 | runtime/source |
| 6ba744b6c8a84e9e89d8dce9bc7b8b94 | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_RShift | 0 | runtime/source |
| 423c3aa808934814bfce0f9365304a5e | [src/gzkit/test_shape.py:193](/Users/jeff/Documents/Code/gzkit/src/gzkit/test_shape.py:193) | core/ReplaceBinaryOperator_Div_Sub | 0 | runtime/source |

### validate_commit_trailers — 19 survivors / 59 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| 794fd9709525446f85f007d4dcc8b2cc | [src/gzkit/commands/validate_commit_trailers.py:32](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:32) | core/ReplaceTrueWithFalse | 0 | runtime/source |
| e2e93ad4ff9241e1a089334026aff6de | [src/gzkit/commands/validate_commit_trailers.py:34](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:34) | core/ReplaceTrueWithFalse | 2 | runtime/source |
| 037198930e474587b6499db307453a25 | [src/gzkit/commands/validate_commit_trailers.py:41](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:41) | core/ReplaceTrueWithFalse | 3 | runtime/source |
| 063e94eba66b4b25ba79ccb59053a342 | [src/gzkit/commands/validate_commit_trailers.py:43](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:43) | core/ReplaceTrueWithFalse | 5 | runtime/source |
| 42f43e440e124aa5b3a5defe015321fa | [src/gzkit/commands/validate_commit_trailers.py:81](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:81) | core/ReplaceFalseWithTrue | 0 | runtime/source |
| 3fe91c1ba2cc45389bf337c8fc19369f | [src/gzkit/commands/validate_commit_trailers.py:83](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:83) | core/ReplaceTrueWithFalse | 7 | runtime/source |
| d7c0867facae411ca09b66f8387f7dbf | [src/gzkit/commands/validate_commit_trailers.py:90](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:90) | core/ReplaceOrWithAnd | 0 | runtime/source |
| 2a5d3a00c7c04ef0b551928273a93c58 | [src/gzkit/commands/validate_commit_trailers.py:121](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:121) | core/ReplaceFalseWithTrue | 1 | runtime/source |
| 57737d82f4ee4ea8a2f89de22995b440 | [src/gzkit/commands/validate_commit_trailers.py:125](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:125) | core/ReplaceTrueWithFalse | 8 | runtime/source |
| d37db08505644436b662a1af43a29576 | [src/gzkit/commands/validate_commit_trailers.py:126](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:126) | core/ReplaceTrueWithFalse | 9 | runtime/source |
| be3c93e3decc4ad082a85db077f0ec0c | [src/gzkit/commands/validate_commit_trailers.py:129](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:129) | core/ReplaceFalseWithTrue | 2 | runtime/source |
| 70f078e0013d4cc281dc27a9cf65f77a | [src/gzkit/commands/validate_commit_trailers.py:132](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:132) | core/ReplaceComparisonOperator_Eq_GtE | 0 | runtime/source |
| e86a565283da4e10b7c3f429ecac6a73 | [src/gzkit/commands/validate_commit_trailers.py:132](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:132) | core/ReplaceComparisonOperator_Eq_LtE | 0 | runtime/source |
| 30fdac893cf8478d8874f495f8b81d7b | [src/gzkit/commands/validate_commit_trailers.py:138](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:138) | core/ReplaceBreakWithContinue | 0 | runtime/source |
| d758c785c83b42359a5b7ceda6768215 | [src/gzkit/commands/validate_commit_trailers.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:139) | core/ExceptionReplacer | 3 | runtime/source |
| 98aa82aee79b4daaa6f739aa7ce4e45f | [src/gzkit/commands/validate_commit_trailers.py:148](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:148) | core/ReplaceFalseWithTrue | 3 | runtime/source |
| e0665bceb794450c8ca95856047bfcbc | [src/gzkit/commands/validate_commit_trailers.py:149](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:149) | core/ReplaceTrueWithFalse | 11 | runtime/source |
| 811469dbb36643d28e47b9967f878dc6 | [src/gzkit/commands/validate_commit_trailers.py:150](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:150) | core/ReplaceTrueWithFalse | 12 | runtime/source |
| ed0880e1fbb74009a4febc08f621a122 | [src/gzkit/commands/validate_commit_trailers.py:157](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:157) | core/ReplaceOrWithAnd | 1 | runtime/source |

### verifier_pipe_gate — 573 survivors / 1130 mutants

| Job ID | Source | Operator | Occurrence | Span |
|---|---|---|---|---|
| 0201685c63284c9a81732f59e03d3e49 | [src/gzkit/verifier_pipe_gate.py:269](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:269) | core/ReplaceTrueWithFalse | 1 | runtime/source |
| ea4b2e622ba74425a2db88cfa21a2f78 | [src/gzkit/verifier_pipe_gate.py:291](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:291) | core/ReplaceContinueWithBreak | 0 | runtime/source |
| 706a2843b92442fea5d69d50004c4c22 | [src/gzkit/verifier_pipe_gate.py:294](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:294) | core/ReplaceContinueWithBreak | 1 | runtime/source |
| ba59b47b68804b17b0b1c810ee28d3eb | [src/gzkit/verifier_pipe_gate.py:296](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:296) | core/ReplaceComparisonOperator_Eq_Is | 0 | runtime/source |
| 53bd2ee8f9db4d42beec060cef04e45f | [src/gzkit/verifier_pipe_gate.py:296](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:296) | core/ReplaceComparisonOperator_Eq_Lt | 0 | runtime/source |
| 026b594ae41b46dc8290f6dcec978e3c | [src/gzkit/verifier_pipe_gate.py:296](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:296) | core/ReplaceComparisonOperator_Eq_LtE | 0 | runtime/source |
| 842850077a7946ee9a8891d3c88bc9ef | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/AddNot | 3 | runtime/source |
| dd89f2cd581740598d4558af8b13980f | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/ReplaceComparisonOperator_Gt_Eq | 0 | runtime/source |
| 71176c47ee5d45eaa13e1b3c43d67f20 | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/ReplaceComparisonOperator_Gt_GtE | 0 | runtime/source |
| 63c4bd22acc24425a69f2186386783c5 | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/ReplaceComparisonOperator_Gt_Lt | 0 | runtime/source |
| 50f07ab4fd0a44efba53e9bd02def94d | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/ReplaceComparisonOperator_Gt_LtE | 0 | runtime/source |
| 19d1d5af9e3046f4868c2028a672dc9a | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/ReplaceComparisonOperator_Gt_NotEq | 0 | runtime/source |
| 1e6e850b76814856881591a9924ac41a | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/NumberReplacer | 2 | runtime/source |
| 3cd8f5dc2aa648b382f048cce116c52e | [src/gzkit/verifier_pipe_gate.py:297](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:297) | core/NumberReplacer | 3 | runtime/source |
| 3b8196c8634448cfaa788fd679d11ec5 | [src/gzkit/verifier_pipe_gate.py:298](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:298) | core/NumberReplacer | 4 | runtime/source |
| 0109c4bcc4fd401abdd60e11471dd5e2 | [src/gzkit/verifier_pipe_gate.py:298](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:298) | core/NumberReplacer | 5 | runtime/source |
| 2e6ef7469872460aa32b18361b12ccdb | [src/gzkit/verifier_pipe_gate.py:299](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:299) | core/ReplaceContinueWithBreak | 2 | runtime/source |
| d98df3757bd84d9f842c7ce5852cba34 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/AddNot | 4 | runtime/source |
| 7cf79fb3c8e64a948e9554eee996c54f | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceAndWithOr | 0 | runtime/source |
| 1119a778ad1140caa8e87321e21cbe15 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 6 | runtime/source |
| 0cf25144d76f4e679ed3ed9dfb49e35c | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 7 | runtime/source |
| 138f8065a3524f50b1b0131d8f13b8a5 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 8 | runtime/source |
| 083b74fb70a94ab6a93929db266e37a1 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 9 | runtime/source |
| 73c47073ac2d446d8642e609b48e02b1 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_Gt | 1 | runtime/source |
| 25296e2450be46e0b6d93de4395879ba | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_GtE | 1 | runtime/source |
| ce88323285e6439da2bbf190f922efdb | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_Is | 1 | runtime/source |
| 53afbbcdd53a4dbab7ba0590ce789332 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_IsNot | 1 | runtime/source |
| c190eeeaad134ce8a0767bfcfa097cd2 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_Lt | 1 | runtime/source |
| 33e12718340240abb061071e3a5749b7 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_LtE | 1 | runtime/source |
| 120312c0019548d297f2865443b792df | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Eq_NotEq | 1 | runtime/source |
| a286c10d65db4b8eb114026365d3b10c | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Gt_Eq | 1 | runtime/source |
| 5c21a31206cf4a0b80fd6f14a035d8c7 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Gt_GtE | 1 | runtime/source |
| f3b62b7ef1c8474fbfe3cb78f1edcd68 | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Gt_Lt | 1 | runtime/source |
| 7621ae4906a24dbb8d12fd7c0984ba6a | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Gt_LtE | 1 | runtime/source |
| 3b8f8b48695747578ff8e5f1a6aa4ace | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/ReplaceComparisonOperator_Gt_NotEq | 1 | runtime/source |
| e31308c659b04533b3749a720bacefab | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 10 | runtime/source |
| aa30dbfca3bb4f869757fff1e7ddf97d | [src/gzkit/verifier_pipe_gate.py:301](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:301) | core/NumberReplacer | 11 | runtime/source |
| c046849d9b99491382e549a0906deec1 | [src/gzkit/verifier_pipe_gate.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:302) | core/NumberReplacer | 12 | runtime/source |
| 57366676367b4a14a8466592e7ec06f4 | [src/gzkit/verifier_pipe_gate.py:302](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:302) | core/NumberReplacer | 13 | runtime/source |
| 9f1170891948404a9a31dca1d5c420d9 | [src/gzkit/verifier_pipe_gate.py:303](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:303) | core/ReplaceContinueWithBreak | 3 | runtime/source |
| 6ab6070610e749df9f3cd580656f875e | [src/gzkit/verifier_pipe_gate.py:315](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:315) | core/ReplaceTrueWithFalse | 2 | runtime/source |
| a70bd49e67684bf7b642a5a308a48ab5 | [src/gzkit/verifier_pipe_gate.py:324](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:324) | core/ReplaceComparisonOperator_Lt_Gt | 0 | runtime/source |
| 495795d833194a4a8dd3d916c16e66f0 | [src/gzkit/verifier_pipe_gate.py:324](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:324) | core/ReplaceComparisonOperator_Lt_IsNot | 0 | runtime/source |
| 3c4363d44ae046e58afc290d46357874 | [src/gzkit/verifier_pipe_gate.py:324](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:324) | core/ReplaceComparisonOperator_Lt_NotEq | 0 | runtime/source |
| cf6a7a9b7eb64669b701b1d339020404 | [src/gzkit/verifier_pipe_gate.py:326](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:326) | core/AddNot | 6 | runtime/source |
| a25f77833bbd4098bceff46f7b9207e4 | [src/gzkit/verifier_pipe_gate.py:328](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:328) | core/NumberReplacer | 16 | runtime/source |
| 9b92eaa5889442b8a834d7d74f0ea431 | [src/gzkit/verifier_pipe_gate.py:341](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:341) | core/ReplaceComparisonOperator_Eq_GtE | 2 | runtime/source |
| 5999d8ff7ebc4407afb808f1ba653260 | [src/gzkit/verifier_pipe_gate.py:341](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:341) | core/NumberReplacer | 20 | runtime/source |
| a177ac97d2f745358f096720d54b7f8b | [src/gzkit/verifier_pipe_gate.py:341](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:341) | core/NumberReplacer | 21 | runtime/source |
| fb57c7d3da364142b6979bdd5a9b947c | [src/gzkit/verifier_pipe_gate.py:362](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:362) | core/ReplaceComparisonOperator_NotEq_Gt | 0 | runtime/source |
| 19fb08fc50a8456b859943a8af187fed | [src/gzkit/verifier_pipe_gate.py:362](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:362) | core/ReplaceComparisonOperator_NotEq_Is | 0 | runtime/source |
| 3f98137ce09f4366b319c4af51d36b35 | [src/gzkit/verifier_pipe_gate.py:362](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:362) | core/ReplaceComparisonOperator_NotEq_Lt | 0 | runtime/source |
| 86fd07f277174a2a9fc19ab7c4cea480 | [src/gzkit/verifier_pipe_gate.py:364](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:364) | core/NumberReplacer | 25 | runtime/source |
| 5533717bb3be4dfe92daa5ecf6c90e58 | [src/gzkit/verifier_pipe_gate.py:367](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:367) | core/NumberReplacer | 27 | runtime/source |
| 7b679b67c291473a87691cea3df12435 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Add | 1 | postponed |
| 6ab37c9f164d4856831af06f2bd689aa | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_BitAnd | 1 | postponed |
| c73c261988cc4b7493ee3f1067b5dc5e | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_BitXor | 1 | postponed |
| 264ac03b34364be19be836ed5bba5249 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Div | 1 | postponed |
| 803eb9098885473fbc3e3d15bc757e4c | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 1 | postponed |
| 4ce1fd7f46e448edae08104e46d5d620 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_LShift | 1 | postponed |
| afa2b87d21ea43d98732e0b06e438016 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Mod | 1 | postponed |
| 63d1ecf91503452588bb2f81093e9123 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Mul | 1 | postponed |
| 06242e59e59a4d7690596665501b00d0 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Pow | 1 | postponed |
| ba0b66321c8c4d2eb3e67a4f2542aa2a | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_RShift | 1 | postponed |
| 81c799b5fd824b27bdfc2c2e3e732c4d | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Sub | 1 | postponed |
| 39360fe10394440390569111c040a098 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Add | 2 | postponed |
| 4b9a5666930247debef4cab3017b0ae9 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_BitAnd | 2 | postponed |
| d5afcd6ea09e4552b500b549e4e6f4fe | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_BitXor | 2 | postponed |
| babffee10bc04e5ab17c4f75ce724663 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Div | 2 | postponed |
| 1777d1e2538a41fab699e5e09e200726 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 2 | postponed |
| 7073087d035c461ba52d1e3c755195c4 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_LShift | 2 | postponed |
| c93522580d2846eea598795badd9d945 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Mod | 2 | postponed |
| 032a1633361846c885513a1df66fd040 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Mul | 2 | postponed |
| 03451df88ec8432d9a0e124f32780a46 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Pow | 2 | postponed |
| 96edd3b3bce6449d8d88aecb219a7e62 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_RShift | 2 | postponed |
| 4b61d25fcecd4dd4aea5a48e487ece77 | [src/gzkit/verifier_pipe_gate.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:377) | core/ReplaceBinaryOperator_BitOr_Sub | 2 | postponed |
| 472c80dd4b134615826eb7bda6ee3931 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Add | 3 | postponed |
| 86703e10f33f4f0eb640b735f0335b65 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_BitAnd | 3 | postponed |
| 7c89198aab2140e5b756b6ae312e4004 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_BitXor | 3 | postponed |
| 40987a6b1a174ae5975b781e8e94b1f0 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Div | 3 | postponed |
| ff81ecffb85f40bebe5e5b50155e6a2e | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 3 | postponed |
| 3dfc9b9f28fb4f65853e93c8027e9d55 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_LShift | 3 | postponed |
| 8c49d543b5fc4f4a95f7371e40c5bb46 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Mod | 3 | postponed |
| d57650eb27bb465db78df0faf6c9a40b | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Mul | 3 | postponed |
| a478edb354aa4fb48dadc0cfec468484 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Pow | 3 | postponed |
| 47f0f2df976549778856b70adf4871c9 | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_RShift | 3 | postponed |
| f53297ac42924e6385651cd6c1bf5f8f | [src/gzkit/verifier_pipe_gate.py:388](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:388) | core/ReplaceBinaryOperator_BitOr_Sub | 3 | postponed |
| 1a5e7b21df674b499e7815c1c503613b | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Add | 4 | postponed |
| 81678191979e44359494ef166f088e4b | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_BitAnd | 4 | postponed |
| 6798e13a6ddf4561a2b7bb445c88f72b | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_BitXor | 4 | postponed |
| 93e768923c684d5eb247f63979339d6f | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Div | 4 | postponed |
| df940ac9e93343a59e944502a926f648 | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 4 | postponed |
| 3a8df11dd8914525bae455c7d4258bf9 | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_LShift | 4 | postponed |
| c578c441ed9d47f3b32950b0a0697362 | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Mod | 4 | postponed |
| fb43f1a781564576bfd107426305b429 | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Mul | 4 | postponed |
| 5b51c783db89493682ea40e669438ffd | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Pow | 4 | postponed |
| d667b6727286417b8c7e46e324658a63 | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_RShift | 4 | postponed |
| 3ce23ce0de024a4787e0a0c2631ed11e | [src/gzkit/verifier_pipe_gate.py:396](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:396) | core/ReplaceBinaryOperator_BitOr_Sub | 4 | postponed |
| db1d4da1f6fe4184bc8ac2933e07aa3d | [src/gzkit/verifier_pipe_gate.py:400](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:400) | core/ReplaceContinueWithBreak | 4 | runtime/source |
| 30bcc756221248acb38825594844bc13 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Add | 5 | postponed |
| 0712d95d33ac4b789ba90b6a2c158b4a | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_BitAnd | 5 | postponed |
| df08ea7836294f068750aebf6e8064e4 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_BitXor | 5 | postponed |
| 6e51911860914dc4a90551f7fd783e3d | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Div | 5 | postponed |
| f2769a8b897340c4940aa394779481f0 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 5 | postponed |
| 051b5ade004749af86c8e88f7a7f9234 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_LShift | 5 | postponed |
| 7b21f052cdbe4ce4b9377830f6e88762 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Mod | 5 | postponed |
| 9018f013d723406aa20182413a06d807 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Mul | 5 | postponed |
| 747c5a70b5a4471ab3fa9d4937d45519 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Pow | 5 | postponed |
| 3c3e598f236c432f885f0fa07908a040 | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_RShift | 5 | postponed |
| 1f05eb8538d54cca82a72ad2b97a87cd | [src/gzkit/verifier_pipe_gate.py:405](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:405) | core/ReplaceBinaryOperator_BitOr_Sub | 5 | postponed |
| cfa3712f44d84307b348faf19308a062 | [src/gzkit/verifier_pipe_gate.py:417](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:417) | core/ReplaceComparisonOperator_Eq_LtE | 4 | runtime/source |
| 0636c419c94c4e95803f4813c5c4c0c6 | [src/gzkit/verifier_pipe_gate.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:423) | core/ReplaceComparisonOperator_Eq_GtE | 5 | runtime/source |
| 2adeaa20fcb9423f8b95f267697dbe44 | [src/gzkit/verifier_pipe_gate.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:423) | core/ReplaceComparisonOperator_Eq_IsNot | 5 | runtime/source |
| 78fddb2781464e27948a53f5c9eb1fd5 | [src/gzkit/verifier_pipe_gate.py:423](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:423) | core/ReplaceComparisonOperator_Eq_LtE | 5 | runtime/source |
| 3c269a2ca58447069e1ab960c5be6ce5 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Add | 6 | postponed |
| 4eb0b693e34241ec868f9bb75a1037cc | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_BitAnd | 6 | postponed |
| bd76260131be4718ac7db2600fa59c68 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_BitXor | 6 | postponed |
| bcccb06c67314ec591a9db29c12dcdc0 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Div | 6 | postponed |
| 97dfc969db034fce9593f09ebc458e54 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 6 | postponed |
| cb69e2f95e044ab4ae9829d040a36b6f | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_LShift | 6 | postponed |
| 73c5d93361b5476fbdd67cec56b25899 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Mod | 6 | postponed |
| 67190644b449440a814b416cdb7b4f91 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Mul | 6 | postponed |
| 30ff51adecf449d2b146c38f5cad77d6 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Pow | 6 | postponed |
| 537002af4b634ff084d49321c0bad10f | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_RShift | 6 | postponed |
| 6f1c6da33d6c448091158af8cfeb5c38 | [src/gzkit/verifier_pipe_gate.py:429](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:429) | core/ReplaceBinaryOperator_BitOr_Sub | 6 | postponed |
| 6815d4ac769743a0856627de494738d1 | [src/gzkit/verifier_pipe_gate.py:452](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:452) | core/ReplaceComparisonOperator_LtE_IsNot | 0 | runtime/source |
| 48ebdcfce08d4d2196c0d815b8e248e8 | [src/gzkit/verifier_pipe_gate.py:452](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:452) | core/ReplaceComparisonOperator_LtE_Lt | 0 | runtime/source |
| 81f1117d6c584f33aa23fbae5ea408d1 | [src/gzkit/verifier_pipe_gate.py:452](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:452) | core/ReplaceComparisonOperator_LtE_NotEq | 0 | runtime/source |
| 876e22a262f54745ab433cbe6db58bc7 | [src/gzkit/verifier_pipe_gate.py:452](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:452) | core/ReplaceAndWithOr | 6 | runtime/source |
| a98f3b916bc049e4ae778ea2eb258bfc | [src/gzkit/verifier_pipe_gate.py:479](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:479) | core/ReplaceComparisonOperator_Eq_Is | 7 | runtime/source |
| 33a0bb6b885e449bbd20dc05dc2453b1 | [src/gzkit/verifier_pipe_gate.py:485](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:485) | core/ReplaceComparisonOperator_LtE_Lt | 1 | runtime/source |
| b985b25e1956440ea3904b781481b6d4 | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_Gt | 8 | runtime/source |
| 2129bdcdcf8b495d8f06cca75ea359d4 | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_GtE | 8 | runtime/source |
| 48e5c2f2a20c46b781a4b5f43f142daf | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_Is | 8 | runtime/source |
| efc8c009a522447cbe837eeed5d5dfc7 | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_IsNot | 8 | runtime/source |
| df30cac905e84ad2b3b814f7c7e844fe | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_LtE | 8 | runtime/source |
| 5b407c1b2ac3447f9693e524ece8d847 | [src/gzkit/verifier_pipe_gate.py:488](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:488) | core/ReplaceComparisonOperator_Eq_NotEq | 8 | runtime/source |
| 0488289eb59f43609afdaa56ba1888c0 | [src/gzkit/verifier_pipe_gate.py:491](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:491) | core/ReplaceComparisonOperator_Gt_GtE | 2 | runtime/source |
| 0c0da67442474201a03bbfc700b1066b | [src/gzkit/verifier_pipe_gate.py:491](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:491) | core/ReplaceComparisonOperator_Gt_NotEq | 2 | runtime/source |
| e4f0bd97466f4a3abf73c004fd4431ed | [src/gzkit/verifier_pipe_gate.py:491](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:491) | core/NumberReplacer | 45 | runtime/source |
| 3a86ef99387c4c7da1a89b175f9413ce | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Add | 7 | postponed |
| 8af27801699447be9a803a5b112f957d | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_BitAnd | 7 | postponed |
| fbc92122f9984252b751d51da963f964 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_BitXor | 7 | postponed |
| 617bf8e2669645a3a02e29a479b477bf | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Div | 7 | postponed |
| 26754a01252147f9b736ee0d1d69ea09 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 7 | postponed |
| 66219d46a45747b384102876febd3799 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_LShift | 7 | postponed |
| 61b43e4e230b43a38786541a49b382d9 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Mod | 7 | postponed |
| b9dec1653e51430286df145d88e495c2 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Mul | 7 | postponed |
| 9d124c429f1a4b21951d737eda8f84ba | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Pow | 7 | postponed |
| 443427eacbee4eeeb59d4fd72fc5ef0c | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_RShift | 7 | postponed |
| f00ce6648d5145318f99df7af37296d5 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Sub | 7 | postponed |
| 9d8ede792b384f2ea64c1ff5e0a0606f | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Add | 8 | postponed |
| e7d8d07009364d5cbd2692c690cd97f7 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_BitAnd | 8 | postponed |
| 6c600dbcd7104239b858c98d69c421f3 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_BitXor | 8 | postponed |
| bea853e787e34bcfa63369d99f8015ac | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Div | 8 | postponed |
| 7053145d515b42b6957bfb41bf28c95a | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 8 | postponed |
| f87223f7088b4c979dd78a7dc749d8c0 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_LShift | 8 | postponed |
| 0e98141b7459438980600730994817a1 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Mod | 8 | postponed |
| 6aa57232aed44b948a560c86dfbe7ae7 | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Mul | 8 | postponed |
| c9fde6cba6944fb5aed86785efdb703a | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Pow | 8 | postponed |
| 483dacde34894df291db7254ca4774ed | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_RShift | 8 | postponed |
| b5930c56d8b142b7866f646d5371a2cb | [src/gzkit/verifier_pipe_gate.py:496](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:496) | core/ReplaceBinaryOperator_BitOr_Sub | 8 | postponed |
| a6f6b8e060e5469badc3baa6960992fa | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Add | 9 | postponed |
| 3f0157f0646c4f0ebd66df190d1d75b6 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_BitAnd | 9 | postponed |
| e2a83f391547449c97c82ad1bfae1e06 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_BitXor | 9 | postponed |
| c3f2d071c809440aacb4b1ba27274623 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Div | 9 | postponed |
| 7852210ba3d3441f8cd617c3a15db0d9 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 9 | postponed |
| 6a73ee070f2048b1ac2a3b6a6bbed896 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_LShift | 9 | postponed |
| 4eed9d7a0166426a870f45c4f4107f55 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Mod | 9 | postponed |
| 76dd4e9115804726b2a28a325bbe17bc | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Mul | 9 | postponed |
| 373dbdc3adbc4f52b5862c6a7f0c79c4 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Pow | 9 | postponed |
| 03f5d130eca54aaf85a2ab3e746b003d | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_RShift | 9 | postponed |
| 407a329d9c9447c69f44989b7ebdb2ba | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Sub | 9 | postponed |
| 24929e80a3494450b5c4b3c08e58ae03 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Add | 10 | postponed |
| f644283e06c34e6da4c06545d7d945e4 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_BitAnd | 10 | postponed |
| beae82c125d84b199205e79c20ef87a3 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_BitXor | 10 | postponed |
| ff3d939e27bd4a31b788768b65026163 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Div | 10 | postponed |
| 3cca701a133d440e82c71b53b64ef0ba | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 10 | postponed |
| 4214d823464b45c6bbd99f1c8d0449e5 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_LShift | 10 | postponed |
| 35bdfd2265b3402cb4fd697c68e82280 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Mod | 10 | postponed |
| 07186aa7815245ebb8ec946f20684d49 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Mul | 10 | postponed |
| f17ade6a657e4119ba4a2b0c3ebbdd60 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Pow | 10 | postponed |
| 607446a33ebf485b824fe80a254ad422 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_RShift | 10 | postponed |
| 4a1b3ed946ed4890b236d4d4ecf43128 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceBinaryOperator_BitOr_Sub | 10 | postponed |
| a1b8d4b6509747de94a295ef51f1ac01 | [src/gzkit/verifier_pipe_gate.py:505](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:505) | core/ReplaceFalseWithTrue | 3 | runtime/source |
| c515b6ebc61148b4ad989386c768114a | [src/gzkit/verifier_pipe_gate.py:512](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:512) | core/ReplaceComparisonOperator_NotEq_Gt | 1 | runtime/source |
| f0b1f72dc9cc4273abfc744c64075a56 | [src/gzkit/verifier_pipe_gate.py:512](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:512) | core/ReplaceComparisonOperator_NotEq_GtE | 1 | runtime/source |
| 0cd67d3a8749472da35ba294c28c9c69 | [src/gzkit/verifier_pipe_gate.py:512](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:512) | core/ReplaceComparisonOperator_NotEq_IsNot | 1 | runtime/source |
| 1d7dc055ec7f42c7b78faa57b3f1ea1b | [src/gzkit/verifier_pipe_gate.py:518](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:518) | core/ReplaceFalseWithTrue | 4 | runtime/source |
| 26cfa60d40b9478688c0f9aa5888eb5b | [src/gzkit/verifier_pipe_gate.py:520](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:520) | core/ReplaceComparisonOperator_Eq_Is | 9 | runtime/source |
| eb5a3221e35b4840a7e2ddc3bdfd66e2 | [src/gzkit/verifier_pipe_gate.py:521](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:521) | core/ReplaceComparisonOperator_NotEq_Gt | 2 | runtime/source |
| 2464fde83ade4591a00354a147a3b74b | [src/gzkit/verifier_pipe_gate.py:521](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:521) | core/ReplaceComparisonOperator_NotEq_IsNot | 2 | runtime/source |
| a0f661b3f5e946689a51161af7336632 | [src/gzkit/verifier_pipe_gate.py:521](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:521) | core/ReplaceComparisonOperator_NotEq_Lt | 2 | runtime/source |
| a5302b0e3d93469288866d8e411d9635 | [src/gzkit/verifier_pipe_gate.py:525](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:525) | core/ReplaceUnaryOperator_USub_Not | 1 | runtime/source |
| de3e2d925aa84dde9294f5955e46fdde | [src/gzkit/verifier_pipe_gate.py:525](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:525) | core/NumberReplacer | 49 | runtime/source |
| d2210468012a46afae673865c67aff33 | [src/gzkit/verifier_pipe_gate.py:525](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:525) | core/ReplaceComparisonOperator_Eq_Is | 10 | runtime/source |
| c48935e6812143e4a37ad27a3cf481c6 | [src/gzkit/verifier_pipe_gate.py:525](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:525) | core/ReplaceComparisonOperator_Eq_LtE | 10 | runtime/source |
| 1bd0ad10f3014d23b4c0b18cf13788f1 | [src/gzkit/verifier_pipe_gate.py:528](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:528) | core/ReplaceFalseWithTrue | 5 | runtime/source |
| d5f430a75acb4fffb8bdeb1cee3398cc | [src/gzkit/verifier_pipe_gate.py:530](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:530) | core/ReplaceComparisonOperator_Eq_Is | 11 | runtime/source |
| ed7760f41c894e6d9b3359b12199c8d0 | [src/gzkit/verifier_pipe_gate.py:533](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:533) | core/ReplaceComparisonOperator_Eq_Gt | 12 | runtime/source |
| 0af2af08f1ca46578017cd5890e8f2ae | [src/gzkit/verifier_pipe_gate.py:533](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:533) | core/ReplaceComparisonOperator_Eq_GtE | 12 | runtime/source |
| 890df9ae2ba3473abb2f9945f66b28f4 | [src/gzkit/verifier_pipe_gate.py:533](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:533) | core/ReplaceComparisonOperator_Eq_Is | 12 | runtime/source |
| 3a6d4289109245b6ae47dcc40d665b28 | [src/gzkit/verifier_pipe_gate.py:534](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:534) | core/NumberReplacer | 53 | runtime/source |
| 7dd6a96cb50249dd8bd404a20c0753ae | [src/gzkit/verifier_pipe_gate.py:534](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:534) | core/ReplaceComparisonOperator_Eq_GtE | 13 | runtime/source |
| 56974c898b1544ddbced997df06c5dad | [src/gzkit/verifier_pipe_gate.py:534](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:534) | core/ReplaceComparisonOperator_Eq_LtE | 13 | runtime/source |
| c20dc9f4ec57410086fd3128eb36f7f1 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Add | 11 | postponed |
| 6ef43748ff74438887f6d65d7a28c762 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_BitAnd | 11 | postponed |
| dcf4046f73dd42f5bb208e6dc7798806 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_BitXor | 11 | postponed |
| f3b1af44e56944e4aca8880d4dbf9f7b | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Div | 11 | postponed |
| 3f6deeed38c34ecb9e4f33d90b1b4b3b | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 11 | postponed |
| 54005e5256b8487ea72bec4020f2d7d1 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_LShift | 11 | postponed |
| 52a98bdd39cf45ceac50a1049a6c96fe | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Mod | 11 | postponed |
| fecc2c4f29f14f8d8feac4d288c67f70 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Mul | 11 | postponed |
| 6c74288b5acd482e970d4656f2180661 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Pow | 11 | postponed |
| db452086888942188fd6154ae00bf6b1 | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_RShift | 11 | postponed |
| 0d074464e9764553868b877e4f1ed52c | [src/gzkit/verifier_pipe_gate.py:537](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:537) | core/ReplaceBinaryOperator_BitOr_Sub | 11 | postponed |
| 4ac7fa1dfc0246fa9ce5ac2645d2ba8d | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Add | 12 | postponed |
| adb237f7ca4d48a9878e12651e0756a2 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_BitAnd | 12 | postponed |
| 0e72931952924beaa0f92293b98655bb | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_BitXor | 12 | postponed |
| 4c33e177cfb145e5a42cee3fe085ddef | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Div | 12 | postponed |
| 9e28662ce1734c278d69a3db1ce5cae1 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 12 | postponed |
| a2cd048b5d5a4dbc8cfbf8618ceabfa6 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_LShift | 12 | postponed |
| 6ef41f95e795458fab5dbf8981cb2ebe | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Mod | 12 | postponed |
| f48aa8da43be4d89906b7c0caf9d86b7 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Mul | 12 | postponed |
| c54a25109b104de68eb87b9a46ae2e25 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Pow | 12 | postponed |
| b46c217c69ad4216a1331d2622e90f8d | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_RShift | 12 | postponed |
| e8e0311c938f42d18c1f95d0e685b816 | [src/gzkit/verifier_pipe_gate.py:542](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:542) | core/ReplaceBinaryOperator_BitOr_Sub | 12 | postponed |
| f284ccdec3d7479cbbe4ee50ad951649 | [src/gzkit/verifier_pipe_gate.py:544](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:544) | core/NumberReplacer | 59 | runtime/source |
| a6f052c034a0434aa2c473c0e64862d8 | [src/gzkit/verifier_pipe_gate.py:545](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:545) | core/NumberReplacer | 61 | runtime/source |
| 7966d62a225b40f182d512fc96302f82 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Add | 13 | postponed |
| d47cf3b91ca44fba806e16b3a76654a7 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_BitAnd | 13 | postponed |
| 6302cdae4dab4c4aaba63c7e7e74721f | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_BitXor | 13 | postponed |
| ce82ac07ec1e4ad5ab733ce3956e5a44 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Div | 13 | postponed |
| 9df07b8852f74c2fa4c95286944ae64c | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 13 | postponed |
| 58b7acfcf1b1413ba6c3acd8b64b7cee | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_LShift | 13 | postponed |
| 1728d8f4767947e0a82f86eb27e473a0 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Mod | 13 | postponed |
| 02cc910ae9e94d0a9744c868f1a76822 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Mul | 13 | postponed |
| 42986168c9e3439d9baae44a75e02469 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Pow | 13 | postponed |
| 3bb431a4d37c4c179d4fd0d31f417f95 | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_RShift | 13 | postponed |
| 13b6376d0fe1445f899014632827432c | [src/gzkit/verifier_pipe_gate.py:549](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:549) | core/ReplaceBinaryOperator_BitOr_Sub | 13 | postponed |
| 647900339e014b9cb008d2787c1aceb2 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Add | 14 | postponed |
| e8230615189a48a3ae60f1a995730b23 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_BitAnd | 14 | postponed |
| 42687f67f3e04331ab42430ce07868c7 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_BitXor | 14 | postponed |
| af6e6e94e0ab4857b43d130bdaf6e89b | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Div | 14 | postponed |
| ae9c24e82f5a4d7098bfea0d809b8ea6 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 14 | postponed |
| bfb2360f44da42a7bcd3f7106851c431 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_LShift | 14 | postponed |
| 9ef5471867784acda5c831520bd249bd | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Mod | 14 | postponed |
| eeed8affb1a6419897f1265cd4581c57 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Mul | 14 | postponed |
| 59e0d4e0e2344f038f7e043f339487f4 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Pow | 14 | postponed |
| 6523ecf296b248b7bd0fe992cdd3c71a | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_RShift | 14 | postponed |
| 0deed1fd19284cf8aabbf491ddc36b91 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Sub | 14 | postponed |
| f59713b43a1547d49c9731ba488b507f | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Add | 15 | postponed |
| 536d6fe78cfb4f29bb629089ceff3880 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_BitAnd | 15 | postponed |
| eb8016f6ef8e453fb6cdbf50c300d3d6 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_BitXor | 15 | postponed |
| 0ee74e410799472c8ccca06fcb20a65e | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Div | 15 | postponed |
| 33920b4ecbf74ffaa5d51dee6f88ea14 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 15 | postponed |
| 36bcaf80c1874c95b21c9d2ee63f5f8f | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_LShift | 15 | postponed |
| 2ced0f4cc97744a3a851a0acb56edccd | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Mod | 15 | postponed |
| c3e5458ddb2248c588305e5fde29c200 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Mul | 15 | postponed |
| 0977e8ba7d0d4ef3b84415c1f1604fce | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Pow | 15 | postponed |
| b5d1521db9334df2a526956a9cc821f8 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_RShift | 15 | postponed |
| c7c62cc7bb684da6a24b4ce4f5894436 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_BitOr_Sub | 15 | postponed |
| b98f180b66704f8db4f39a3dd9cfa5a7 | [src/gzkit/verifier_pipe_gate.py:558](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:558) | core/ReplaceBinaryOperator_Mul_Div | 0 | runtime/source |
| 9f31a56b54784d68a2c6846e76567aff | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Add | 16 | postponed |
| 528de00634284edba109659d38c7ae89 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_BitAnd | 16 | postponed |
| 790f71438a7943b39dc19aa72c131245 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_BitXor | 16 | postponed |
| c6a08634b80b4a9283b711742d9d1756 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Div | 16 | postponed |
| 65b5125de61a4ac780c26a4f20c3b8b5 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 16 | postponed |
| 269a26ddd15b41c0817dbb490a683578 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_LShift | 16 | postponed |
| a45869208dfc4db98b4fcb8d7638df39 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Mod | 16 | postponed |
| 371fde2054cb48d98cddb51f2b6cb47b | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Mul | 16 | postponed |
| 4ca32e1c6e92426faa8ebf7065f43c13 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Pow | 16 | postponed |
| 03b3c163324d45f3b443f49301c96872 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_RShift | 16 | postponed |
| fe5148359db345748684eadd5db6d4a9 | [src/gzkit/verifier_pipe_gate.py:559](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:559) | core/ReplaceBinaryOperator_BitOr_Sub | 16 | postponed |
| 1264bc840cd8402e894f959e89d54a76 | [src/gzkit/verifier_pipe_gate.py:565](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:565) | core/ReplaceComparisonOperator_Lt_Gt | 1 | runtime/source |
| 97eee4a86b754f49a0980b3c7dfed9aa | [src/gzkit/verifier_pipe_gate.py:565](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:565) | core/ReplaceComparisonOperator_Lt_NotEq | 1 | runtime/source |
| c2f8a0a7de424cbe85c2458682e7e85c | [src/gzkit/verifier_pipe_gate.py:565](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:565) | core/NumberReplacer | 65 | runtime/source |
| cffbec7ea92a4d9ba92464e278664a3d | [src/gzkit/verifier_pipe_gate.py:569](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:569) | core/ReplaceUnaryOperator_Delete_USub | 2 | runtime/source |
| 5c50621c3d744e3cbb402e064955eccf | [src/gzkit/verifier_pipe_gate.py:569](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:569) | core/ReplaceUnaryOperator_USub_UAdd | 2 | runtime/source |
| f39c47f8164345dc8b3a57793c7d7b3d | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Add | 17 | postponed |
| 8088d0c7d7564b4fb04a47f61af39dac | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_BitAnd | 17 | postponed |
| 5a065bc4035646bf9b162e72003380fc | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_BitXor | 17 | postponed |
| 3dfe4f8b31964736b7d0d76830096a5f | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Div | 17 | postponed |
| 3b84dad3f2944f248a5020308d09be26 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 17 | postponed |
| c8ea36477b124a49a1059d418a25a86d | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_LShift | 17 | postponed |
| 1d64b0c86f06448cadd206cf88b89d3b | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Mod | 17 | postponed |
| 6a9f240b34a94c42bf20adca3debc806 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Mul | 17 | postponed |
| 98b9c9dbe18242eba7945e4033669940 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Pow | 17 | postponed |
| 87f306ebf51543ba93d8f44d751eea58 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_RShift | 17 | postponed |
| 0c4cccabe95a40cd98f4e7c43ead9cd0 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Sub | 17 | postponed |
| a101eea965904e2d9d6a1962d6240602 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_Mul_Div | 1 | runtime/source |
| dd534d2af2cf40a08e14c01c3a941d2a | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Add | 18 | postponed |
| f0d33fcf59fc411088b2351fe3c59d96 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_BitAnd | 18 | postponed |
| bbfdf3268adb45ce9fa7252faa363e78 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_BitXor | 18 | postponed |
| 4cf2917edcc141ed9a653aeec8ee3f9b | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Div | 18 | postponed |
| 1fd1b12bebf24ffcb64ce98183c6eb8c | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 18 | postponed |
| 148cd106df0d4e00b682609b023fae75 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_LShift | 18 | postponed |
| 0c91d95ac90b4ab2801dca78cd244c16 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Mod | 18 | postponed |
| ee3f549b17704f1ba5c1dd9424b842d4 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Mul | 18 | postponed |
| 9784ccac45ed453399dcc5f4598e7157 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Pow | 18 | postponed |
| a7142b529cd341e593777269b6e3dfcc | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_RShift | 18 | postponed |
| dde7274ab9e944c1a8ffe5fb0cd34108 | [src/gzkit/verifier_pipe_gate.py:572](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:572) | core/ReplaceBinaryOperator_BitOr_Sub | 18 | postponed |
| 81c023e9175e46fea784d2820f69b36c | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Add | 19 | postponed |
| dccb8c25c2df4261b261080c27d4f5f3 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_BitAnd | 19 | postponed |
| acdcd23c1a8440da947116dc1e307582 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_BitXor | 19 | postponed |
| fa2171c2c2c34ef7a4a0c71d4e732ee3 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Div | 19 | postponed |
| 16c8c795beec4000ac7848d356cc9912 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 19 | postponed |
| 65a235abac7e4f9cba288d78fba0207f | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_LShift | 19 | postponed |
| 65e03705896e4b94aa64589625ff4f3d | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Mod | 19 | postponed |
| a639d523fde64de08cf4f921c85c6687 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Mul | 19 | postponed |
| 51b0106b43c64c65a6dc62ce8f7179e7 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Pow | 19 | postponed |
| f060cb8f99b843d5918409e93dd95cb0 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_RShift | 19 | postponed |
| 81a64157165a49c683812e489f2c6ce4 | [src/gzkit/verifier_pipe_gate.py:584](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:584) | core/ReplaceBinaryOperator_BitOr_Sub | 19 | postponed |
| 67369a577ff041fb8ce485807409ad2d | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Add | 20 | postponed |
| db9942acd4e547149a17ebb71f475be8 | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_BitAnd | 20 | postponed |
| 18f99596696a423287410405f90b5f5a | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_BitXor | 20 | postponed |
| b27d9d17af9a4297bfe7b7829e1991d4 | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Div | 20 | postponed |
| 9da5f9facb354e18a9b85ae434986119 | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 20 | postponed |
| d753662d1793450bac87290e0f89d186 | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_LShift | 20 | postponed |
| bf3c982797f34a4f99ce1c66a53e653b | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Mod | 20 | postponed |
| bdc44aea8a8f401b9f8904a58bd1682c | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Mul | 20 | postponed |
| 39d7529563934bbf9004637c9f493ca7 | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Pow | 20 | postponed |
| 0c7cf38202684961b1aaba1c0d2138dd | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_RShift | 20 | postponed |
| ce0c6004735b48048593bfeaa36f850d | [src/gzkit/verifier_pipe_gate.py:585](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:585) | core/ReplaceBinaryOperator_BitOr_Sub | 20 | postponed |
| 9f0f19458e7c4a59af35f08e65ddb15b | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Add | 21 | postponed |
| 29e54ae9ead54574b47ccb0b9635474d | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_BitAnd | 21 | postponed |
| 18ed8f8528a24d45b431ddc806d68256 | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_BitXor | 21 | postponed |
| 69ba50143ba74d138a7ae97f2e31613e | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Div | 21 | postponed |
| f8c5b223909446ffa6b4c9a3e9d9bd5d | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 21 | postponed |
| 12d43ada211f4eeeb65a6bd52e9d10fb | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_LShift | 21 | postponed |
| e133fad2e0fc426e807d40dacf4c13c0 | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Mod | 21 | postponed |
| 00eebc098b724c60a62ad85de10a8c82 | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Mul | 21 | postponed |
| 8f2e9679d30a4d6fa14ddcd300907749 | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Pow | 21 | postponed |
| 02fb07177dbb475e9d64e72b1d9489ba | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_RShift | 21 | postponed |
| 10ad6f31c7174f3da8e5884e9fe0d23d | [src/gzkit/verifier_pipe_gate.py:586](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:586) | core/ReplaceBinaryOperator_BitOr_Sub | 21 | postponed |
| 127c1be6d7e34a01b88a729c33f90ce3 | [src/gzkit/verifier_pipe_gate.py:587](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:587) | core/ReplaceBinaryOperator_Mul_Div | 2 | runtime/source |
| 852da9694aff4aa290868d8c33297caf | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Add | 22 | postponed |
| bf2da00d67654c949ecb520330fa1f9c | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_BitAnd | 22 | postponed |
| fea748a155aa428895e0c3c353453207 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_BitXor | 22 | postponed |
| 059820a47e814a3494a97dca92ba28cf | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Div | 22 | postponed |
| 37b52343ec5d40c69630df70105a5549 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 22 | postponed |
| cba19974b5604e308ba24fb77ac2e187 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_LShift | 22 | postponed |
| d3f451f8374e405298ac49cbd7972d96 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Mod | 22 | postponed |
| fe1e8ebb18224fb2bc90b7919b621332 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Mul | 22 | postponed |
| ff290e05924541cba6dfc1be09c2fab7 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Pow | 22 | postponed |
| a5de54ec62bd4edb99b10f10f9cf8335 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_RShift | 22 | postponed |
| e532a9e802c34e0fb4074f857a085ef2 | [src/gzkit/verifier_pipe_gate.py:591](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:591) | core/ReplaceBinaryOperator_BitOr_Sub | 22 | postponed |
| bf2c9740d6cc4dcabcf67feced1b406a | [src/gzkit/verifier_pipe_gate.py:617](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:617) | core/ReplaceComparisonOperator_Gt_NotEq | 3 | runtime/source |
| 50659943643441acad3aea1897c5b99d | [src/gzkit/verifier_pipe_gate.py:628](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:628) | core/ReplaceComparisonOperator_Eq_Is | 14 | runtime/source |
| 81419a4e06d24aea9ef357804b6950bf | [src/gzkit/verifier_pipe_gate.py:628](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:628) | core/ReplaceComparisonOperator_Eq_LtE | 15 | runtime/source |
| 10ed039f5e8549adad9525111c6e0ce8 | [src/gzkit/verifier_pipe_gate.py:633](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:633) | core/ReplaceComparisonOperator_NotEq_Gt | 3 | runtime/source |
| 6edca085ba7945b7bcff184aff24635a | [src/gzkit/verifier_pipe_gate.py:633](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:633) | core/ReplaceComparisonOperator_NotEq_IsNot | 3 | runtime/source |
| b26198c0bb8d42a2bce81f457677fc18 | [src/gzkit/verifier_pipe_gate.py:635](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:635) | core/ReplaceComparisonOperator_Eq_Is | 15 | runtime/source |
| e12f4f0bb9324a98ad0bfdaadd7bc903 | [src/gzkit/verifier_pipe_gate.py:635](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:635) | core/ReplaceComparisonOperator_Eq_LtE | 16 | runtime/source |
| 8250023fc4074006b927b6e73744b872 | [src/gzkit/verifier_pipe_gate.py:639](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:639) | core/ReplaceComparisonOperator_Eq_GtE | 17 | runtime/source |
| 5ee84cc3f202485c95920b282c9c596e | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Add | 23 | postponed |
| 57dedb1517be4efd9bebf49b32c4cae4 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_BitAnd | 23 | postponed |
| 8308cf0ab90a48df965d1ae410bbfb32 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_BitXor | 23 | postponed |
| c5eb50697cfc45ccba6df480186cb296 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Div | 23 | postponed |
| 6efc829699894550b10b55d776054e5d | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 23 | postponed |
| c9744d03e32743bfb051c287cce0c0e2 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_LShift | 23 | postponed |
| a389c34d3c924ec1a06565e4c3a95d7b | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Mod | 23 | postponed |
| c6e8026c8afa4bc2bc13fab6d4080e30 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Mul | 23 | postponed |
| bb17ee1bce3d416e8d50a62797da3520 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Pow | 23 | postponed |
| af57236735cd495e83f29298bfc82501 | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_RShift | 23 | postponed |
| 5669fa840b3d4620aeeb8c50e9cfdd4a | [src/gzkit/verifier_pipe_gate.py:645](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:645) | core/ReplaceBinaryOperator_BitOr_Sub | 23 | postponed |
| f0fa7a5c333d4cb6b01fd8ba70651bda | [src/gzkit/verifier_pipe_gate.py:646](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:646) | core/ReplaceBinaryOperator_Mul_Div | 3 | runtime/source |
| f365441f3c01420c97cffac84cac3e7f | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Add | 24 | postponed |
| 9081221c0c8540f883247791b837f8d8 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_BitAnd | 24 | postponed |
| a6352c7cd56040b88e97ddd4dec6895b | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_BitXor | 24 | postponed |
| 7197a89ba8d8466db8b56c4d09b103e3 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Div | 24 | postponed |
| fd0074c67cfc4447bf46485d076c289c | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 24 | postponed |
| 9d4a4861dd5d474c955e9b0349858bd4 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_LShift | 24 | postponed |
| e53c3f09fe8f45daa55c845950d36d49 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Mod | 24 | postponed |
| c923f1258ed54b9ca23cbd6e01bd0dc4 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Mul | 24 | postponed |
| 43196631425b4f81a74441d658e29db7 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Pow | 24 | postponed |
| c64d14eaa42d4689a9db2cf0bcf1b16a | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_RShift | 24 | postponed |
| 1237066783544f588bdfac53e005e108 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Sub | 24 | postponed |
| 29cfd850494d443fa4c72e3f6b4b2112 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Add | 25 | postponed |
| 4c25e04de48b4322841c71c675b95980 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_BitAnd | 25 | postponed |
| 34e9aae400794dfa875e2e227f47d3b0 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_BitXor | 25 | postponed |
| b192d86c101d4f949551cc91476edaa9 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Div | 25 | postponed |
| c6a4b8877c3c412eb49c25069f421d39 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 25 | postponed |
| d56c6f5375b7409bb550547a153cbc52 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_LShift | 25 | postponed |
| 3b6821f9332e4c1791f17c430584710d | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Mod | 25 | postponed |
| 29ae5d1a41d34440a976dd8c5131de78 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Mul | 25 | postponed |
| 878da00a7df54c60a0c3b768e8e80612 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Pow | 25 | postponed |
| 5a6976ab0be14442b214cf865cdb261c | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_RShift | 25 | postponed |
| f79f658ab3ea4c028104225e29702d83 | [src/gzkit/verifier_pipe_gate.py:650](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:650) | core/ReplaceBinaryOperator_BitOr_Sub | 25 | postponed |
| 0d05fc629eb7431ba6864e224c8a04a5 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Add | 26 | postponed |
| d8c0769f4c0440be876b5fb5c850f5f5 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_BitAnd | 26 | postponed |
| 868e6a53a048474491bcde237461722b | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_BitXor | 26 | postponed |
| f3d2cb55287d47eea8ff660a966b09fc | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Div | 26 | postponed |
| 0fcec6b1362a4fda823272d8c3e1e6e9 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 26 | postponed |
| 3607097aa8a04a898428f5b33a820418 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_LShift | 26 | postponed |
| d52ac4dc2c1f42fcbdf1009abdc55f5d | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Mod | 26 | postponed |
| c0f6ef2250e240b289d20e19df615e5d | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Mul | 26 | postponed |
| 519253c9e948493ab7c27c7c9816af94 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Pow | 26 | postponed |
| 6f7105ece9e840a9a444cfbade9c5e4c | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_RShift | 26 | postponed |
| fb132ee42cae4107806528477fda98cf | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Sub | 26 | postponed |
| 63df5af7f3c249b2a37f3d3cbcf5eb71 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Add | 27 | postponed |
| 5d98142b10b945ba87400bb5e5979487 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_BitAnd | 27 | postponed |
| 03b8bfe0d04e47c3bc1f101da9fc8538 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_BitXor | 27 | postponed |
| 21965ccdae99401db130f289fddbe245 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Div | 27 | postponed |
| 9632267fe4ed47c2977e319b4ffd6dd9 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 27 | postponed |
| a9af811f6d47476290919ad7f4864c42 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_LShift | 27 | postponed |
| a9ca2b6c4b3e45e28d80a95456559124 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Mod | 27 | postponed |
| 1db9861d37c84afd858cb511638090bf | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Mul | 27 | postponed |
| 72718beb6f004bc3ac05ca49ace934cd | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Pow | 27 | postponed |
| 34c9a19f84ed446f8328e51b62e7e184 | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_RShift | 27 | postponed |
| 3a121edc72954ee1b39ac06fd20e1f7f | [src/gzkit/verifier_pipe_gate.py:652](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:652) | core/ReplaceBinaryOperator_BitOr_Sub | 27 | postponed |
| 9eceaaaeaa5d4f06a5cc58ce9f5837cf | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Add | 28 | postponed |
| 978ab0a324624492a2ecbcb36ad84892 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_BitAnd | 28 | postponed |
| 7d39c8c699004ff1b9aa5d7777cc5bdd | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_BitXor | 28 | postponed |
| 452ab4de0c0748d4a7a85bc3ba1cdcbb | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Div | 28 | postponed |
| 650d194111bc4f31bc3c66eddf4872c7 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 28 | postponed |
| abefea4d9a9b45c7868d708ea47abfef | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_LShift | 28 | postponed |
| 1481356984e848f4a5f257fbbd64361c | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Mod | 28 | postponed |
| 9f68b80fd7ac40dd9bd047ecd6a9f652 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Mul | 28 | postponed |
| 74318c2c7b7541e18014b41af778256b | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Pow | 28 | postponed |
| 41595cd75fec49b6a28de87dba57916b | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_RShift | 28 | postponed |
| 9c655a66915c4acfbbaa9722358e878d | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Sub | 28 | postponed |
| c5e03b070de44260ab0d72b87893add5 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Add | 29 | postponed |
| 0ecb88343f3d40679ecfefaa4bf15a11 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_BitAnd | 29 | postponed |
| 8812af25d33e463f92ac046b5dfcf63a | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_BitXor | 29 | postponed |
| d93a764968054595910e36c45fdf576a | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Div | 29 | postponed |
| e6a8edf752214c769c6a93acd11d3f9a | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 29 | postponed |
| 6daee9b0f9ae4bb0ae63ba0dc88f3c09 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_LShift | 29 | postponed |
| 6a6c8ce5af3b468fb93580538db70cb1 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Mod | 29 | postponed |
| c02631f7299a43ccb9190a602d2081e4 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Mul | 29 | postponed |
| e9ad246d46a14078afb554d49f25818a | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Pow | 29 | postponed |
| d8c7285266f340139ab662db5d94d706 | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_RShift | 29 | postponed |
| 0019692c0d1e4a9fa5b9b7fd115df11f | [src/gzkit/verifier_pipe_gate.py:669](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:669) | core/ReplaceBinaryOperator_BitOr_Sub | 29 | postponed |
| 1469b25e080e471097b3de4bb843545f | [src/gzkit/verifier_pipe_gate.py:676](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:676) | core/NumberReplacer | 81 | runtime/source |
| 745f0e5ae61e4821b0d48a4b638f12e9 | [src/gzkit/verifier_pipe_gate.py:676](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:676) | core/NumberReplacer | 83 | runtime/source |
| c471ecc5d8f244a3bcbd40fc36321ea2 | [src/gzkit/verifier_pipe_gate.py:676](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:676) | core/NumberReplacer | 85 | runtime/source |
| 01182351f5844e65a806035327df4651 | [src/gzkit/verifier_pipe_gate.py:680](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:680) | core/ReplaceComparisonOperator_Eq_LtE | 18 | runtime/source |
| b006738d424e450382f5c24a5aff41b5 | [src/gzkit/verifier_pipe_gate.py:681](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:681) | core/ReplaceComparisonOperator_NotEq_IsNot | 4 | runtime/source |
| 9e314a0b6201401da53bed92bfa6478d | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Add | 30 | postponed |
| 666e1e506c2044878cd67270f88ae68b | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_BitAnd | 30 | postponed |
| 9e6ba9dc3a304b69959292f19420d252 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_BitXor | 30 | postponed |
| 6da26bc355444eb2aa649858b15ea749 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Div | 30 | postponed |
| de6a32581d0a4686bdd9abb67e510fc2 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 30 | postponed |
| 4f7a767341b24edc96069b3880aca06a | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_LShift | 30 | postponed |
| cb8a537c31e247c79047e9292e13e268 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Mod | 30 | postponed |
| 17678e9466bc4d30841ce454a02b3754 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Mul | 30 | postponed |
| d7bbb136868e40c2a79e9b03a56586b8 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Pow | 30 | postponed |
| a3e90e3046b242beb61dfc9e4d6ca1a5 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_RShift | 30 | postponed |
| a5388cd510f94c478c229f351fa6f591 | [src/gzkit/verifier_pipe_gate.py:686](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:686) | core/ReplaceBinaryOperator_BitOr_Sub | 30 | postponed |
| a6652c99c9674f3f99313eaf587c5cbd | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Add | 31 | postponed |
| c0085ff37d3c41289a4d81c9c94b05ef | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_BitAnd | 31 | postponed |
| 7a81e5f214b346a3974772bc15164c3e | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_BitXor | 31 | postponed |
| 5a231697ad2f46e38aafcb1f1cd8dd2a | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Div | 31 | postponed |
| 319aed0b85ec4969bd571bbab9bdcbc4 | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 31 | postponed |
| eaaa1ed06f6242e89130a661027ea4a7 | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_LShift | 31 | postponed |
| 51e9f3230eb247c0b41bde16c8f8d0cf | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Mod | 31 | postponed |
| bcf3b86b01824c4693c201e08cddf045 | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Mul | 31 | postponed |
| aa664ff5a6774e92817c4cc226c088de | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Pow | 31 | postponed |
| 8f884ccaddd840cbb61e4fc86c6fb7d7 | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_RShift | 31 | postponed |
| d81fd5a1ec8745b8a35ad806723f07f3 | [src/gzkit/verifier_pipe_gate.py:687](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:687) | core/ReplaceBinaryOperator_BitOr_Sub | 31 | postponed |
| ce44d76581a04a7a948a0014a221ee62 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Add | 32 | postponed |
| b924e25eb8b249afa80b249cc6a80dbb | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_BitAnd | 32 | postponed |
| c07d560bf0a544cc8d90f45f5126246e | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_BitXor | 32 | postponed |
| 7822ce08f32641878cd895fe81b10194 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Div | 32 | postponed |
| 5fb53b2b37ff4fe6be89e65549f8d599 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 32 | postponed |
| 2fc5807e396545b0b2a96c0a5dce60bb | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_LShift | 32 | postponed |
| 0483aad9f4a941988238e099ccd9a377 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Mod | 32 | postponed |
| e21f0a10e850434ca2d230116d798e67 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Mul | 32 | postponed |
| 4355f09541d84170b2e4d3e9acaa14c1 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Pow | 32 | postponed |
| 5480c7c7769542daa756c330a5b4d496 | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_RShift | 32 | postponed |
| 6e00f2cbe666491da9091a6d75ad1c5e | [src/gzkit/verifier_pipe_gate.py:688](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:688) | core/ReplaceBinaryOperator_BitOr_Sub | 32 | postponed |
| 603bd040268b461bb48aa9758121228c | [src/gzkit/verifier_pipe_gate.py:689](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:689) | core/ReplaceBinaryOperator_Mul_Div | 4 | runtime/source |
| dcfe4c1961364b5ebfe015ce2fb658be | [src/gzkit/verifier_pipe_gate.py:709](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:709) | core/NumberReplacer | 93 | runtime/source |
| 214ab9864828471188dffc48a53c5387 | [src/gzkit/verifier_pipe_gate.py:709](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:709) | core/NumberReplacer | 95 | runtime/source |
| 7956d8ec79d64eea83625ebdd71ed974 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Add | 33 | postponed |
| e2c806147c8f42f6a53224da787e157f | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_BitAnd | 33 | postponed |
| a6eefcb32b7d47638a0bed4009907ec5 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_BitXor | 33 | postponed |
| 70b92c9802424fbe8bd9d29a4075c8d1 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Div | 33 | postponed |
| a196b7ba79d44a23aebb061411d6a57c | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 33 | postponed |
| 9eb5a0896fcf45c7b7b691b2531252b3 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_LShift | 33 | postponed |
| d40134566b074f6b9f0d14e5a455f4c6 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Mod | 33 | postponed |
| 798c93e3e3664d7eadf7c6fe4573cb99 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Mul | 33 | postponed |
| ec83d0ac5d6b4353bd3e0cda4cf56a5d | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Pow | 33 | postponed |
| d70c9f53d19d435d8cde549376ed77a1 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_RShift | 33 | postponed |
| 2bf6ad94eb3d4a2c8fcb47d2e4845a06 | [src/gzkit/verifier_pipe_gate.py:739](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:739) | core/ReplaceBinaryOperator_BitOr_Sub | 33 | postponed |
| 0e32b92942044661921867c9e7a32656 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Add | 34 | postponed |
| c9d07be13a85487488818477cc5493d9 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_BitAnd | 34 | postponed |
| 42a56b9e5a484352a23af9a781c57f37 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_BitXor | 34 | postponed |
| 0685de979daa4c85b0946d079772728c | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Div | 34 | postponed |
| 53d97cba82034a83954f5e5889df10ae | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 34 | postponed |
| 5934b20ef59b497dbc13b1856574217e | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_LShift | 34 | postponed |
| 7e157fb4ec9e4412aa55ff89cd5e5276 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Mod | 34 | postponed |
| f414c0fbbf044d4eb578ebee2657f169 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Mul | 34 | postponed |
| c15936a228be428cbda858202b8baaf0 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Pow | 34 | postponed |
| 048ed7bccade4fd4abbb9fd2301b82c8 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_RShift | 34 | postponed |
| f26c4bbb040449efa428f558d74eb719 | [src/gzkit/verifier_pipe_gate.py:740](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:740) | core/ReplaceBinaryOperator_BitOr_Sub | 34 | postponed |
| 7632d7801fc8462c8e78e2ba5d5a16cc | [src/gzkit/verifier_pipe_gate.py:741](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:741) | core/ReplaceBinaryOperator_Mul_Div | 5 | runtime/source |
| 3459a901f0174bd2ac7d4d7230b60f92 | [src/gzkit/verifier_pipe_gate.py:749](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:749) | core/ReplaceComparisonOperator_Eq_Is | 17 | runtime/source |
| e6eb5b49de6a48c7a69c86b7f2e465ba | [src/gzkit/verifier_pipe_gate.py:750](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:750) | core/ReplaceComparisonOperator_Eq_Is | 18 | runtime/source |
| 6bdb09498ec048d7bc02a5750d5027d3 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Add | 35 | postponed |
| e43e849165a74c76b8ac3bf3b4480071 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_BitAnd | 35 | postponed |
| c02c8320517e475aa1c1b0c0929b7686 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_BitXor | 35 | postponed |
| 4dbb05a5fd97409abc1f23611ce7cf24 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Div | 35 | postponed |
| 4e13475faaa04a3f9be54bd4863e2065 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 35 | postponed |
| 8406d7cb1b8642e5aec992b001cb86b8 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_LShift | 35 | postponed |
| b388682a006b4312a1a3505a57b16426 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Mod | 35 | postponed |
| f97b7042a3244d768eeee0b5b49c858d | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Mul | 35 | postponed |
| 6df108b4b4714551b34268ff9812c870 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Pow | 35 | postponed |
| 8438e2119ce84f2da541a030148716a3 | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_RShift | 35 | postponed |
| 32d5db8db8274133938074ea063bc04b | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_BitOr_Sub | 35 | postponed |
| 1864ba6705774b8099401cac0a72490b | [src/gzkit/verifier_pipe_gate.py:757](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:757) | core/ReplaceBinaryOperator_Mul_Div | 6 | runtime/source |
| b98d9e9925794f4583ae2516d2e6f610 | [src/gzkit/verifier_pipe_gate.py:765](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:765) | core/NumberReplacer | 97 | runtime/source |
| d9ae93ca64ae4c7bbfb2a4cf67426ac0 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Add | 36 | postponed |
| 0d4525c075c34ce3b45fd8b563732096 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_BitAnd | 36 | postponed |
| cc3b0d064b0e44b98157b8dcb56e1b14 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_BitXor | 36 | postponed |
| 5405ff23c36d4c19b58498e0c013e546 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Div | 36 | postponed |
| c59814fd45464791b218335fb7364cb9 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 36 | postponed |
| 37b875d2e1e4403ab4d68506f4e77765 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_LShift | 36 | postponed |
| 076249b7b3c5480ca33a0afebac59570 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Mod | 36 | postponed |
| 3024f96e22c9496cb61203bfd912e42b | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Mul | 36 | postponed |
| 178e68efd8b24fea84274e2eb627fea4 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Pow | 36 | postponed |
| 7a139b03b76b49c8b7aa762828f0423f | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_RShift | 36 | postponed |
| ccf9d8f701a648d9902da8a8175d9fb3 | [src/gzkit/verifier_pipe_gate.py:791](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:791) | core/ReplaceBinaryOperator_BitOr_Sub | 36 | postponed |
| b455b6062a1b49d2a3302f1fd14dd382 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Add | 37 | postponed |
| a27df538cfa740419ee5e654e13c7be0 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_BitAnd | 37 | postponed |
| 871c331dcc2e45119383de9b4dabb887 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_BitXor | 37 | postponed |
| b6323ea997874471baee532081fda8d3 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Div | 37 | postponed |
| 93225e859b3a4fe3b189bd0197a0b5e3 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 37 | postponed |
| fd4c5c42aa5c45528dea49b770866f76 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_LShift | 37 | postponed |
| a280d0b3392247248a7c4d004a1d8d28 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Mod | 37 | postponed |
| 016a9d233a3442e1aeeec7f0d51a7161 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Mul | 37 | postponed |
| 3609a6d8254540849fa06ee770089c5d | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Pow | 37 | postponed |
| 8e0b26dc126844029d49a6d89960e08a | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_RShift | 37 | postponed |
| 293dec0076a24293876476606f3dccc0 | [src/gzkit/verifier_pipe_gate.py:817](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:817) | core/ReplaceBinaryOperator_BitOr_Sub | 37 | postponed |
| ac26ccae22804b7f89512152c3ec3df0 | [src/gzkit/verifier_pipe_gate.py:844](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:844) | core/ReplaceComparisonOperator_Eq_Is | 19 | runtime/source |
| 7605e27edd854eaab7f625a04a0c6d46 | [src/gzkit/verifier_pipe_gate.py:867](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:867) | core/ReplaceComparisonOperator_Eq_Is | 20 | runtime/source |
| 2557521b2647464ca32a90ec6fe3b38f | [src/gzkit/verifier_pipe_gate.py:887](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:887) | core/ReplaceComparisonOperator_Eq_Is | 21 | runtime/source |
| bf369255e4cf47bd8b6e673112a57289 | [src/gzkit/verifier_pipe_gate.py:887](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:887) | core/ReplaceComparisonOperator_Eq_LtE | 23 | runtime/source |
| dac58ccd727b41269025ad97a1d14688 | [src/gzkit/verifier_pipe_gate.py:904](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:904) | core/ReplaceComparisonOperator_Eq_Is | 22 | runtime/source |
| 53c75662471845d5857a0d1bfd2d4ce9 | [src/gzkit/verifier_pipe_gate.py:904](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:904) | core/ReplaceComparisonOperator_Eq_LtE | 24 | runtime/source |
| 6cfd0080bc1c4db2a78472f83d660a8a | [src/gzkit/verifier_pipe_gate.py:921](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:921) | core/ReplaceComparisonOperator_Eq_GtE | 25 | runtime/source |
| a84c2521ba454404980a54465d7a397a | [src/gzkit/verifier_pipe_gate.py:921](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:921) | core/ReplaceComparisonOperator_Eq_Is | 23 | runtime/source |
| b14f82822ee447188a5c3c3b90e9dc6e | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Add | 38 | postponed |
| 852f02f14d5d499bb324cebec6f7d415 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_BitAnd | 38 | postponed |
| 525ed010a1474428a1eece0b332ae614 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_BitXor | 38 | postponed |
| b1f11d401fed4095a9b4ea2e7b21b13e | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Div | 38 | postponed |
| 0ba3b11b98b64634bbf3ee431f6ae109 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_FloorDiv | 38 | postponed |
| 5fcfa4997a864648a5bcd29ac01675ca | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_LShift | 38 | postponed |
| 36dcdb00158a4674be951ec1e430cc21 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Mod | 38 | postponed |
| 052b1281d5c249188a518f86480a2116 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Mul | 38 | postponed |
| 3bbc8ee0367c4ff9b6f3b436830f4315 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Pow | 38 | postponed |
| 2b3a6e6f738d4a7e9af12b26deec86bd | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_RShift | 38 | postponed |
| 6331f32fd56a42bdb15ed1933f52da59 | [src/gzkit/verifier_pipe_gate.py:965](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:965) | core/ReplaceBinaryOperator_BitOr_Sub | 38 | postponed |
| 1ec61864459a4d7884256a99d9c0b2a6 | [src/gzkit/verifier_pipe_gate.py:971](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:971) | core/ReplaceComparisonOperator_NotEq_Gt | 5 | runtime/source |
| 60ed73bcf7d548cfb90de136749d5032 | [src/gzkit/verifier_pipe_gate.py:971](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:971) | core/ReplaceComparisonOperator_NotEq_IsNot | 5 | runtime/source |
| e27e73901db34512b49205051adab548 | [src/gzkit/verifier_pipe_gate.py:971](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:971) | core/ReplaceComparisonOperator_NotEq_Lt | 5 | runtime/source |
| c60141272f89428dac6883f440959be7 | [src/gzkit/verifier_pipe_gate.py:1031](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1031) | core/ReplaceUnaryOperator_Delete_Not | 14 | runtime/source |
| fe1919eb6d6245f4be8e41b2ba3d41a3 | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/NumberReplacer | 100 | runtime/source |
| 8657c9b27e394f8f8ab6fba392a0a2e9 | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/NumberReplacer | 101 | runtime/source |
| 645c7fe1190d4c60a5cccda913190f5f | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/AddNot | 71 | runtime/source |
| b2c591c3ee1a4d21b9bc1868fe373caf | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/ReplaceAndWithOr | 27 | runtime/source |
| b2290ca286ea4a91b31e674107c38900 | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/NumberReplacer | 102 | runtime/source |
| 83905ed6c84242d7be5d94efb33de6b2 | [src/gzkit/verifier_pipe_gate.py:1032](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1032) | core/NumberReplacer | 103 | runtime/source |
| f629a2d99df74156a1cb060dbb2104bd | [src/gzkit/verifier_pipe_gate.py:1052](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1052) | core/ReplaceAndWithOr | 28 | runtime/source |
| 4e58ede4bf7241d19e7c05411effe3ac | [src/gzkit/verifier_pipe_gate.py:1052](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1052) | core/NumberReplacer | 106 | runtime/source |
| d9ef3b3a698e4c70bb00387fdbc420e3 | [src/gzkit/verifier_pipe_gate.py:1052](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1052) | core/NumberReplacer | 107 | runtime/source |
| 5fbd740e73be49e9910c32b16af8da73 | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_BitAnd | 39 | runtime/source |
| 5c7d723cf7e6462aa26e9cd548bca0dd | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_BitXor | 39 | runtime/source |
| b3613091a26c44c7bdebb77aabfbe1a8 | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_Sub | 39 | runtime/source |
| 5663f359de644012a6ba829e0e470d7b | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_BitAnd | 40 | runtime/source |
| 83a8406e0285414e9dc8faa46664cbee | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_BitXor | 40 | runtime/source |
| 2baaf05a0dde4702964b7e4e06e3e234 | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_Sub | 40 | runtime/source |
| a613ab3100c44c64adb2ba17bfb67f1f | [src/gzkit/verifier_pipe_gate.py:1079](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:1079) | core/ReplaceBinaryOperator_BitOr_BitXor | 41 | runtime/source |

### Incompetent and timed-out mutants

| Job ID | Source | Operator | Outcome |
|---|---|---|---|
| ce3da1a2d73347d795bb47cf8a62fd93 | [src/gzkit/mutation_witness.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/mutation_witness.py:175) | core/NumberReplacer | timed_out |
| 9c14b62a49ea49c7af76d8342650705a | [src/gzkit/commands/validate_commit_trailers.py:47](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:47) | core/ExceptionReplacer | incompetent |
| 84be5b5d585442c487f190e80f7752ff | [src/gzkit/commands/validate_commit_trailers.py:139](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_commit_trailers.py:139) | core/ExceptionReplacer | incompetent |
| 95a6f3c549e749f6bc43dfec7954aa18 | [src/gzkit/verifier_pipe_gate.py:327](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:327) | core/ReplaceBreakWithContinue | timed_out |
| 1fc913bfe8614cd997002627a3bafb2b | [src/gzkit/verifier_pipe_gate.py:328](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:328) | core/NumberReplacer | timed_out |
| 2acd9f9f19794b2b81dca35ed6721950 | [src/gzkit/verifier_pipe_gate.py:613](/Users/jeff/Documents/Code/gzkit/src/gzkit/verifier_pipe_gate.py:613) | core/NumberReplacer | timed_out |

## 7. Dispositions and bloat

| Test receipt | Class | Disposition | Evidence / reason |
|---|---|---|---|
| [tests/test_doc_coverage.py:190](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:190) `TestDiscoverCommands.test_total_command_count` | weakened oracle | rewrite | Accepts a list truncated from 136 discovered commands to 50, dropping 86; its REQ annotation concerns a six-surface CoverageReport rather than a minimum command count. git diff 9e539d0665^ 9e539d0665 -- tests/test_doc_coverage.py src/gzkit/cli/main.py; runtime counterexample in section 8. |
| [tests/governance/test_tautological_tests.py:29](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:29) `TestTautologicalTestModels.test_models_importable` | D3 | delete | The entire executable body is assertTrue(True); it imports no model and exercises no production behavior. probes.json: constant assertion test passes with gzkit_calls=[]; source assertion at31. |
| [tests/governance/test_tautological_tests.py:316](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:316) `TestAstScanner.test_scanner_returns_list_of_operation_instances` | D5 | rewrite | The sole assertion is inside iteration over scanner output; a scanner returning[] for two filesystem-operation fixtures executes zero assertions and passes. probes.json: injected scan_test_tree=[] called once; tests_run1, success=true. Also syntactic D3. |
| [tests/governance/test_tautological_tests.py:573](/Users/jeff/Documents/Code/gzkit/tests/governance/test_tautological_tests.py:573) `TestSelfExemption.test_waivers_file_not_counted_in_scan` | fixture | rewrite | The supposed waivers-file exemption test never writes a waiver file or any other file; it only scans an empty directory. probes.json: paths_present_at_scan=[[]], test passes. This is an unexercised premise, outside the literal D1-D8 classes. |
| [tests/commands/test_gates_frontmatter.py:141](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:141) `TestGate1FrontmatterIntegration.test_gate1_runs_to_completion` | D7 | merge | Repeats the same behavior and inputs as tests/commands/test_gates_frontmatter.py:58 `TestGate1FrontmatterIntegration.test_gate1_passes_when_no_drift`. Same class, _quick_init/_coherent_adr helpers, argv and exit-code assertion; keep the method carrying both REQ anchors. |
| [tests/test_red_parity_audit.py:103](/Users/jeff/Documents/Code/gzkit/tests/test_red_parity_audit.py:103) `TestRedParity.test_weak_error_witness_passes` | D7 | merge | Repeats the same behavior and inputs as tests/test_red_parity_audit.py:183 `TestVoidWitnessesDoNotCount.test_an_error_with_no_provenance_still_satisfies_it`. Both inherit _Project, write the same unproven error witness and assert the same parity result. |
| [tests/commands/test_mx_skill_alignment.py:45](/Users/jeff/Documents/Code/gzkit/tests/commands/test_mx_skill_alignment.py:45) `TestMxSkillAlignment.test_audit_skill_alignment_clean_on_live_tree` | D7 | merge | Repeats the same behavior and inputs as tests/commands/test_skill_alignment_10verbs.py:56 `TestSkillAlignment10Verbs.test_audit_skill_alignment_clean_on_live_tree`. Same audit_skill_alignment function and repository root; same failure formatting; retain anchored 10-verbs test. |
| [tests/governance/test_brief_structure.py:121](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_structure.py:121) `TestBriefStructureModel.test_tasks_accepts_list_of_strings` | D7 | merge | Repeats the same behavior and inputs as tests/governance/test_brief_structure.py:166 `TestTasksSchemaEnforcement.test_accepts_well_formed_formal_task_id`. Same BriefStructure constructor, _VALID_FIELDS and one identical formal TASK ID; same equality assertion. |
| [tests/governance/test_handoff_validation.py:190](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:190) `HandoffWorkContinuityScopeTests.test_malformed_adr_id_still_raises_when_supplied` | D7 | merge | Repeats the same behavior and inputs as tests/governance/test_handoff_validation.py:104 `TestHandoffFrontmatter.test_invalid_adr_id_format_raises`. Identical helper payload and validation-error oracle; neither class alters its fixture. |
| [tests/governance/test_pointer_integrity.py:93](/Users/jeff/Documents/Code/gzkit/tests/governance/test_pointer_integrity.py:93) `TestPointerResolves.test_resolved_pointer_in_rules_dir` | D7 | merge | Repeats the same behavior and inputs as tests/governance/test_pointer_integrity.py:222 `TestPointerResolvesRelativeToSource.test_relative_pointer_from_nested_rule_resolves`. Identical temporary nested rule, pointer, destination and audit/errors-empty assertion. |
| [tests/governance/test_stage4_packet.py:251](/Users/jeff/Documents/Code/gzkit/tests/governance/test_stage4_packet.py:251) `TestExitStatus.test_a_verdict_idiom_that_discloses_its_branch_is_accepted` | D7 | merge | Repeats the same behavior and inputs as tests/governance/test_stage4_packet.py:428 `TestOrElseConcealment.test_the_verdict_idiom_survives_because_its_left_side_runs_no_verifier`. Same verdict-idiom command and validator helper; no differing setup. |
| [tests/test_pipeline_dispatch.py:615](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_dispatch.py:615) `TestStage2DispatchLoopContract.test_empty_plan_produces_empty_state` | D7 | merge | Repeats the same behavior and inputs as tests/test_pipeline_dispatch.py:315 `TestCreateDispatchState.test_empty_tasks_creates_empty_state`. Same create_dispatch_state arguments including empty task list, same three field assertions, no differing setup. |
| [tests/test_config.py:332](/Users/jeff/Documents/Code/gzkit/tests/test_config.py:332) `TestGatesRemoved.test_gates_in_config_rejected` | D7 | merge | Repeats the same behavior and inputs as tests/test_config_gates_removal.py:83 `TestConfigGatesFieldRejected.test_full_test_suite_passes`. Both instantiate the same GzkitConfig with the same forbidden gates field and expect ValidationError; keep anchored method and rename it to the behavior it tests. |
| [tests/test_manifest_v2.py:121](/Users/jeff/Documents/Code/gzkit/tests/test_manifest_v2.py:121) `TestManifestV2Personas.test_v2_manifest_with_personas_passes_validation` | D7 | merge | Repeats the same behavior and inputs as tests/test_manifest_v2.py:135 `TestManifestV2Validation.test_v2_manifest_passes_validation`. Same generated v2 manifest, tempfile serialization and validation/errors-empty assertion; no persona-specific discriminator in repeated method. |
| [tests/test_lifecycle.py:22](/Users/jeff/Documents/Code/gzkit/tests/test_lifecycle.py:22) `TestTransitionTables.test_all_expected_content_types_have_tables` | D7 | merge | Repeats the same behavior and inputs as tests/test_core_lifecycle.py:47 `TestCoreTransitionTables.test_all_content_types_present`. Same TRANSITION_TABLES object re-exported by src/gzkit/lifecycle.py:19 and separately identity-tested at tests/test_core_lifecycle.py:81; same six-key expected set. |
| [tests/test_adr_governance_confirm.py:35](/Users/jeff/Documents/Code/gzkit/tests/test_adr_governance_confirm.py:35) `TestGovernanceSurfaceExists.test_adr_audit_check_importable` | D7 | merge | Repeats the same behavior and inputs as tests/test_adr_audit_ledger_confirm.py:21 `TestAuditLedgerSurfaceExists.test_adr_audit_check_importable`. Same function import and callable predicate with no fixture. Merge the two metadata REQ anchors if retaining the smoke check. |
| [tests/test_adversarial_validation_gate.py:731](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:731) `TestCrossVendorClaimRequiresReceipt.test_human_degraded_floor_remains_exempt` | D7 | merge | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:201 `TestStep4bTierBindingGate.test_human_floor_needs_no_fallback_reason`. Same _ReceiptFixture, same global _enforce helper and identical degraded-human-only/human/None inputs. Both assert successful non-raising invocation implicitly. |
| [tests/test_adversarial_validation_gate.py:712](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:712) `TestCrossVendorClaimRequiresReceipt.test_proven_cross_vendor_claim_passes` | D7 | merge | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:244 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_1_with_cross_vendor_name_passes_on_proof`. Same _ReceiptFixture, same _codex_receipt payload and tier1/codex/fallback=None arguments; same non-raising oracle. |
| [tests/test_adversarial_validation_gate.py:721](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:721) `TestCrossVendorClaimRequiresReceipt.test_tier_2_fallback_remains_usable_without_any_receipt` | D7 | merge | Repeats the same behavior and inputs as tests/test_adversarial_validation_gate.py:266 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_2_with_reason_passes`. Same _ReceiptFixture and tier2/Claude/fallback-reason inputs; same non-raising oracle. |
| [tests/test_ledger_corrections.py:961](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_corrections.py:961) `TestProducerAuditReadsHelperBuiltPayloads.test_the_runtime_scan_over_this_repository_is_clean` | D7 | merge | Repeats the same behavior and inputs as tests/test_ledger_corrections.py:576 `TestProducerContractParity.test_no_producer_writes_an_undeclared_field`. Controls agent whole-file review: same audit_producer_fields(repository root), same error projection and empty-list assertion; only assertion message differs. |
| [tests/test_traceability.py:58](/Users/jeff/Documents/Code/gzkit/tests/test_traceability.py:58) `TestCoversFormatValidation.test_valid_req_format_accepted` | D7 | merge | Repeats the same behavior and inputs as tests/test_traceability.py:198 `TestCoversMetadataOnly.test_return_value_preserved`. Both reset registry/set same _TEST_REQS in setUp, clear in tearDown, decorate identical inner function with same REQ and assert return42. Retain metadata-preservation method carrying REQ anchor. |
| [tests/governance/test_agents_md_map_doctrine_application.py:136](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:136) `BudgetJsonFinalized.test_configured_budgets_are_met` | D7 | merge | Repeats the same behavior and inputs as tests/governance/test_agents_md_map_doctrine_application.py:206 `ConformanceValidatorGreen.test_the_budget_scope_is_green`. Both invoke audit_instructions_files_budget on the same root and assert[]; same class-independent context. Retain accurately named advisory-scope check; migrate any anchor explicitly. |

### Duplicate groups: preserve this test when merging

These are D7 source/fixture equivalence findings. They are not a measured claim of no lost mutant kills: per-test kill attribution belongs to the pilot, and must be cited separately before making that stronger claim. Preserve REQ anchors when merging.

| Keep | Merge repeated method | Evidence |
|---|---|---|
| tests/commands/test_gates_frontmatter.py:58 `TestGate1FrontmatterIntegration.test_gate1_passes_when_no_drift` | tests/commands/test_gates_frontmatter.py:141 `TestGate1FrontmatterIntegration.test_gate1_runs_to_completion` | Same class, _quick_init/_coherent_adr helpers, argv and exit-code assertion; keep the method carrying both REQ anchors. |
| tests/test_red_parity_audit.py:183 `TestVoidWitnessesDoNotCount.test_an_error_with_no_provenance_still_satisfies_it` | tests/test_red_parity_audit.py:103 `TestRedParity.test_weak_error_witness_passes` | Both inherit _Project, write the same unproven error witness and assert the same parity result. |
| tests/commands/test_skill_alignment_10verbs.py:56 `TestSkillAlignment10Verbs.test_audit_skill_alignment_clean_on_live_tree` | tests/commands/test_mx_skill_alignment.py:45 `TestMxSkillAlignment.test_audit_skill_alignment_clean_on_live_tree` | Same audit_skill_alignment function and repository root; same failure formatting; retain anchored 10-verbs test. |
| tests/governance/test_brief_structure.py:166 `TestTasksSchemaEnforcement.test_accepts_well_formed_formal_task_id` | tests/governance/test_brief_structure.py:121 `TestBriefStructureModel.test_tasks_accepts_list_of_strings` | Same BriefStructure constructor, _VALID_FIELDS and one identical formal TASK ID; same equality assertion. |
| tests/governance/test_handoff_validation.py:104 `TestHandoffFrontmatter.test_invalid_adr_id_format_raises` | tests/governance/test_handoff_validation.py:190 `HandoffWorkContinuityScopeTests.test_malformed_adr_id_still_raises_when_supplied` | Identical helper payload and validation-error oracle; neither class alters its fixture. |
| tests/governance/test_pointer_integrity.py:222 `TestPointerResolvesRelativeToSource.test_relative_pointer_from_nested_rule_resolves` | tests/governance/test_pointer_integrity.py:93 `TestPointerResolves.test_resolved_pointer_in_rules_dir` | Identical temporary nested rule, pointer, destination and audit/errors-empty assertion. |
| tests/governance/test_stage4_packet.py:428 `TestOrElseConcealment.test_the_verdict_idiom_survives_because_its_left_side_runs_no_verifier` | tests/governance/test_stage4_packet.py:251 `TestExitStatus.test_a_verdict_idiom_that_discloses_its_branch_is_accepted` | Same verdict-idiom command and validator helper; no differing setup. |
| tests/test_pipeline_dispatch.py:315 `TestCreateDispatchState.test_empty_tasks_creates_empty_state` | tests/test_pipeline_dispatch.py:615 `TestStage2DispatchLoopContract.test_empty_plan_produces_empty_state` | Same create_dispatch_state arguments including empty task list, same three field assertions, no differing setup. |
| tests/test_config_gates_removal.py:83 `TestConfigGatesFieldRejected.test_full_test_suite_passes` | tests/test_config.py:332 `TestGatesRemoved.test_gates_in_config_rejected` | Both instantiate the same GzkitConfig with the same forbidden gates field and expect ValidationError; keep anchored method and rename it to the behavior it tests. |
| tests/test_manifest_v2.py:135 `TestManifestV2Validation.test_v2_manifest_passes_validation` | tests/test_manifest_v2.py:121 `TestManifestV2Personas.test_v2_manifest_with_personas_passes_validation` | Same generated v2 manifest, tempfile serialization and validation/errors-empty assertion; no persona-specific discriminator in repeated method. |
| tests/test_core_lifecycle.py:47 `TestCoreTransitionTables.test_all_content_types_present` | tests/test_lifecycle.py:22 `TestTransitionTables.test_all_expected_content_types_have_tables` | Same TRANSITION_TABLES object re-exported by src/gzkit/lifecycle.py:19 and separately identity-tested at tests/test_core_lifecycle.py:81; same six-key expected set. |
| tests/test_adr_audit_ledger_confirm.py:21 `TestAuditLedgerSurfaceExists.test_adr_audit_check_importable` | tests/test_adr_governance_confirm.py:35 `TestGovernanceSurfaceExists.test_adr_audit_check_importable` | Same function import and callable predicate with no fixture. Merge the two metadata REQ anchors if retaining the smoke check. |
| tests/test_adversarial_validation_gate.py:201 `TestStep4bTierBindingGate.test_human_floor_needs_no_fallback_reason` | tests/test_adversarial_validation_gate.py:731 `TestCrossVendorClaimRequiresReceipt.test_human_degraded_floor_remains_exempt` | Same _ReceiptFixture, same global _enforce helper and identical degraded-human-only/human/None inputs. Both assert successful non-raising invocation implicitly. |
| tests/test_adversarial_validation_gate.py:244 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_1_with_cross_vendor_name_passes_on_proof` | tests/test_adversarial_validation_gate.py:712 `TestCrossVendorClaimRequiresReceipt.test_proven_cross_vendor_claim_passes` | Same _ReceiptFixture, same _codex_receipt payload and tier1/codex/fallback=None arguments; same non-raising oracle. |
| tests/test_adversarial_validation_gate.py:266 `TestDeclaredTierGovernsOverNameInference.test_declared_tier_2_with_reason_passes` | tests/test_adversarial_validation_gate.py:721 `TestCrossVendorClaimRequiresReceipt.test_tier_2_fallback_remains_usable_without_any_receipt` | Same _ReceiptFixture and tier2/Claude/fallback-reason inputs; same non-raising oracle. |
| tests/test_ledger_corrections.py:576 `TestProducerContractParity.test_no_producer_writes_an_undeclared_field` | tests/test_ledger_corrections.py:961 `TestProducerAuditReadsHelperBuiltPayloads.test_the_runtime_scan_over_this_repository_is_clean` | Controls agent whole-file review: same audit_producer_fields(repository root), same error projection and empty-list assertion; only assertion message differs. |
| tests/test_traceability.py:198 `TestCoversMetadataOnly.test_return_value_preserved` | tests/test_traceability.py:58 `TestCoversFormatValidation.test_valid_req_format_accepted` | Both reset registry/set same _TEST_REQS in setUp, clear in tearDown, decorate identical inner function with same REQ and assert return42. Retain metadata-preservation method carrying REQ anchor. |
| tests/governance/test_agents_md_map_doctrine_application.py:206 `ConformanceValidatorGreen.test_the_budget_scope_is_green` | tests/governance/test_agents_md_map_doctrine_application.py:136 `BudgetJsonFinalized.test_configured_budgets_are_met` | Both invoke audit_instructions_files_budget on the same root and assert[]; same class-independent context. Retain accurately named advisory-scope check; migrate any anchor explicitly. |

### Foreign-subject candidates rejected after contract review

- A boolean assertion against a real predicate can fail and is not a defect solely because it is assertTrue. Schema frozen/extra-forbid tests verify authored gzkit configuration, so they are not automatically foreign-subject tests.
- No-raise positive control methods (e.g. test_release_not_found and the adversarial gate acceptance paths) are valid implicit assertions. Repeated no-raise cases can still be D7 duplicates.
- A condition of the form if errors: self.fail(...) is an effective assertion, not a cannot-fail defect.
- Two independently produced artifacts compared for coherence are not automatically a circular expectation. Audit baselines generated from scanner output were not certified D1 because the drift test exercises equality of baseline/current state.
- Exact-body duplicate candidates with different decorators, fixture setups, or imported functions were rejected.39 normalized-body groups were candidates; only18 groups are certified here, including the controls reviewer's non-identical-message pair.
- There is no test-by-test whole-repository semantic review. Nonpilot/non-sample source methods were examined only when they were relevant duplicate partners or scanner candidates. No all-suite D1,D2,D6,D7,D8 absence claim is supported.
- Per-test mutant kill attribution, the canonical suite, line/branch coverage and command/control tracing are separate parent audit work. A survivor is not automatically an unverified line: equivalence and operator semantics require triage.

The four initial D8 candidates were withdrawn after independent claim review. No deletion recommendation remains for them. The scanner-disabled and exit-code probes changed a subject those tests do not claim to cover; their survival established scope, not a defect.

| Test | Decision and receipt |
|---|---|
| tests/test_doc_coverage.py:406 `TestModels.test_report_passed_when_fully_covered` | TestModels explicitly declares model-contract scope (tests/test_doc_coverage.py:359); the owning OBPI REQ-0.0.6-01-02 requires a typed CoverageReport, and model field retention is an authored contract. Not invoking scanner computation limits scope but does not prove this model test is defective. A changed passed readback causes one assertion failure in each test. manual/d8_reassessment_probes.json; docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/obpis/OBPI-0.0.6-01-ast-scanner.md:52 and132; src/gzkit/doc_coverage/models.py:43-55 |
| tests/test_doc_coverage.py:412 `TestModels.test_report_failed_when_gaps_exist` | TestModels explicitly declares model-contract scope (tests/test_doc_coverage.py:359); the owning OBPI REQ-0.0.6-01-02 requires a typed CoverageReport, and model field retention is an authored contract. Not invoking scanner computation limits scope but does not prove this model test is defective. A changed passed readback causes one assertion failure in each test. manual/d8_reassessment_probes.json; docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/obpis/OBPI-0.0.6-01-ast-scanner.md:52 and132; src/gzkit/doc_coverage/models.py:43-55 |
| tests/test_doc_coverage.py:425 `TestModels.test_report_failed_when_orphans_exist` | TestModels explicitly declares model-contract scope (tests/test_doc_coverage.py:359); the owning OBPI REQ-0.0.6-01-02 requires a typed CoverageReport, and model field retention is an authored contract. Not invoking scanner computation limits scope but does not prove this model test is defective. A changed passed readback causes one assertion failure in each test. manual/d8_reassessment_probes.json; docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/obpis/OBPI-0.0.6-01-ast-scanner.md:52 and132; src/gzkit/doc_coverage/models.py:43-55 |
| tests/test_core_exceptions.py:69 `TestExceptionUsability.test_gz_error_message` | Preserving the supplied message is a legitimate public exception contract even when inherited from stdlib. Changing unrelated exit_code did not test that contract. Replacing GzError.__str__ with a changed message causes one assertion failure. manual/d8_reassessment_probes.json; docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-03-exception-hierarchy.md:24; tests/test_core_exceptions.py:66-71 |

Reassessment command: `UV_CACHE_DIR=/private/tmp/gzkit-test-audit-20260924/uv-cache PYTHONDONTWRITEBYTECODE=1 uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python /private/tmp/gzkit-test-audit-20260924/manual/reassess_d8.py`. Output: each of4 baselines passed1 test; changing the actual interface contract produced1 assertion failure and0 errors in each. Full output: manual/d8_reassessment_probes.log and.json.


AST ancestry check: `uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python /private/tmp/gzkit-test-audit-20260924/manual/testcase_ancestry.py` produced `source_methods=10747, proven_TestCase_methods=10747, unresolved=[]`; every source method in the census traces through actual local/imported base declarations to unittest.TestCase. Full receipt: `manual/testcase_ancestry.log`.

### Test-to-production physical line ratios

```text
$ uv run --no-project --python <audit-interpreter> python measurement_summary.py
test_lines=230591 production_lines=157212 ratio=1.466752
```

| Directory | Test lines | Production lines | Ratio |
|---|---|---|---|
| (root) | 77978 | 37233 | 2.0943 |
| adr | 2479 | 0 | N/A |
| airlock | 0 | 751 | 0.0 |
| arb | 2807 | 1639 | 1.7126 |
| chores | 1655 | 3438 | 0.4814 |
| cli | 2300 | 7601 | 0.3026 |
| commands | 48955 | 46417 | 1.0547 |
| complexity | 4077 | 3331 | 1.224 |
| content | 10873 | 5845 | 1.8602 |
| core | 0 | 1285 | 0.0 |
| distribution | 128 | 0 | N/A |
| doc_coverage | 0 | 1310 | 0.0 |
| eval | 1214 | 1270 | 0.9559 |
| fixtures | 25 | 0 | N/A |
| flags | 0 | 708 | 0.0 |
| foundation | 0 | 1523 | 0.0 |
| governance | 60060 | 26705 | 2.249 |
| hooks | 2924 | 5596 | 0.5225 |
| insights | 0 | 852 | 0.0 |
| justify | 1445 | 1604 | 0.9009 |
| knowledge | 663 | 281 | 2.3594 |
| models | 876 | 742 | 1.1806 |
| mx | 2939 | 1422 | 2.0668 |
| ontology | 0 | 2004 | 0.0 |
| personas | 0 | 613 | 0.0 |
| policy | 1916 | 0 | N/A |
| reporter | 0 | 182 | 0.0 |
| rules | 0 | 1138 | 0.0 |
| schemas | 0 | 49 | 0.0 |
| scripts | 2110 | 0 | N/A |
| skills | 2676 | 662 | 4.0423 |
| templates | 0 | 365 | 0.0 |
| tools | 245 | 0 | N/A |
| unit | 1309 | 0 | N/A |
| validate_pkg | 301 | 2199 | 0.1369 |
| validators | 636 | 447 | 1.4228 |

This table pairs physical directory names, not causal ownership. Many root tests exercise subpackages and many integration tests exercise several modules. A zero in a package test directory does not mean its production package is untested, and moving test files changes this ratio without changing any proof.

### Tests with no observed mutant detection; removal bounds

Of the 600 selected tests, 344 have no observed assertion-failure kill and 323 have neither an assertion failure nor an error detection across their assigned module’s mutants. Appendix C prints every selected test and both counts. These are finite-matrix observations, not a general deletion list: tests can protect non-mutated code, enforce structural contracts, or influence shared setup. The constant assertTrue(True) method is a direct deletion candidate; it has no executable behavior besides that constant assertion. Duplicate merges preserve the named test and all applicable REQ anchors. No blanket deletion of the zero-detection list is authorized or justified.

Finite-matrix removal evidence from `finalize_evidence.py` (unittest FAIL/ERROR job sets, not coverage):

| Candidate | Detected jobs | Retained duplicate | Jobs lacking that retained witness |
|---|---:|---|---:|
| `tests.governance.test_tautological_tests.TestTautologicalTestModels.test_models_importable` | 0 | `None` | 0 |
| `tests.test_red_parity_audit.TestRedParity.test_weak_error_witness_passes` | 44 | `tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_an_error_with_no_provenance_still_satisfies_it` | 0 |
| `tests.test_adr_governance_confirm.TestGovernanceSurfaceExists.test_adr_audit_check_importable` | 0 | `tests.test_adr_audit_ledger_confirm.TestAuditLedgerSurfaceExists.test_adr_audit_check_importable` | 0 |
| `tests.test_ledger_corrections.TestProducerAuditReadsHelperBuiltPayloads.test_the_runtime_scan_over_this_repository_is_clean` | 0 | `tests.test_ledger_corrections.TestProducerContractParity.test_no_producer_writes_an_undeclared_field` | 0 |
| `tests.test_traceability.TestCoversFormatValidation.test_valid_req_format_accepted` | 0 | `tests.test_traceability.TestCoversMetadataOnly.test_return_value_preserved` | 0 |

A zero in the last column preserves this candidate’s attributed detection set in the recorded matrix, provided the named retained method remains. The constant test has no detection set. These are the named finite-pilot no-loss candidates; no deletion replay was performed, so shared-state/order effects and faults outside the generated population are not ruled out. Duplicates outside the selected tests have source-equivalence receipts but no measured pilot no-loss claim.

### More than 20 arrange/act lines before one direct assertion

Definition: physical nonblank/noncomment lines after the leading method docstring and before its sole directly executed assertion node; multi-line fixture literal lines count. It includes construction and exercise because AST alone cannot reliably separate arrange from act. Inherited setUp/helper bodies are not expanded. This is a bloat review inventory, not148 certified redundant tests. Full rows: `manual/long_setup.json`.

| Test receipt | Setup/exercise lines before the single assertion |
|---|---|
| tests/adr/test_patch_release.py:120 `TestDiscoverGhis.test_returns_only_ghis_referenced_in_range` | 26 |
| tests/adr/test_patch_release.py:201 `TestDiscoverGhis.test_gh_view_failure_skips_ghi` | 30 |
| tests/adr/test_state_doctrine.py:177 `TestStateRepairIdempotency.test_repair_withdrawn_obpi` | 21 |
| tests/chores/test_eval_feedback_cluster.py:305 `TestEvalFeedbackCluster.test_readonly_no_writes_outside_proofs` | 26 |
| tests/chores/test_session_correction_mining.py:127 `TestRealTranscriptShape.test_meta_sidechain_and_tag_injected_messages_do_not_count` | 22 |
| tests/commands/test_adr_demote_parks_obpis.py:105 `TestDemoteParksChildObpis.test_already_terminal_obpis_are_not_parked` | 23 |
| tests/commands/test_complexity_advise_ad_hoc.py:94 `TestAdHocPresenter.test_adhoc_includes_source_line_snippets` | 21 |
| tests/commands/test_foundation_kind_closed.py:510 `TestFoundationKindClosedAtAuthoringTime.test_adr_promote_feature_kind_still_passes_unchanged` | 21 |
| tests/commands/test_justify_cmd.py:240 `TestDeterminism.test_identical_inputs_produce_identical_outputs` | 25 |
| tests/commands/test_justify_validate.py:242 `TestFixtureDriftGuard.test_complete_fixture_matches_fresh_render` | 36 |
| tests/commands/test_obpi_precomplete.py:1120 `TestPrecompleteOperatorBlockCheck.test_passes_again_once_the_operator_has_ruled` | 21 |
| tests/commands/test_parsers.py:10 `TestNewCommandParsers.test_new_commands_help` | 30 |
| tests/commands/test_plan.py:734 `FoundationMembraneSeatedAtTheSharedWriter.test_grandfathered_foundation_still_books` | 22 |
| tests/commands/test_skills.py:373 `TestSkillCommands.test_check_command_passes_with_non_blocking_skill_audit_warning` | 21 |
| tests/commands/test_upgrade.py:256 `TestUpgradeForce.test_force_overwrites_edited_artifact` | 23 |
| tests/commands/test_upgrade.py:481 `TestUpgradeIdempotent.test_second_run_exits_0` | 29 |
| tests/commands/test_upgrade.py:715 `TestUpgradeHonorsPackageOnlyCarveout.test_templates_skills_subdir_filtered` | 22 |
| tests/commands/test_validate_cmds.py:227 `TestValidateCommand.test_validate_interviews_skips_waived_adr` | 24 |
| tests/commands/test_validate_cmds.py:378 `TestValidateCommand.test_validate_commit_trailers_passes_with_trailer` | 23 |
| tests/commands/test_validate_cmds.py:445 `TestValidateCommand.test_validate_commit_trailers_accepts_slug_form_task_trailer` | 31 |
| tests/commands/test_validate_cmds.py:485 `TestValidateCommand.test_validate_commit_trailers_skips_non_code_commits` | 23 |
| tests/complexity/authoring/test_engine.py:164 `TestEngineCleanFile.test_warn_band_crossing_excluded` | 24 |
| tests/complexity/authoring/test_engine.py:238 `TestPrecedenceBandClassification.test_no_warn_band_returns_approaching` | 39 |
| tests/complexity/test_aggregator.py:135 `TestAggregateCrossProject.test_inter_project_variance_matches_statistics_variance` | 21 |
| tests/content/test_composer.py:402 `TestByteEvidenceAccounting.test_emission_attribution_counts_only_attributed_entries` | 28 |
| tests/content/test_lineage.py:55 `TestSaveCandidateLineageShape.test_writes_bare_adr_decision_5_shape` | 24 |
| tests/content/test_ownership.py:1519 `TestRecordUnownedTotalIsTransactional.test_the_declaration_write_and_its_witness_both_happen_inside_the_lock` | 22 |
| tests/content/test_ownership.py:3352 `TestRatchetLinkThatChangesTheMapIsAttested.test_a_map_invariant_ratchet_row_owes_no_attestation` | 22 |
| tests/governance/test_adr_status_index.py:188 `ComputeDriftTests.test_missing_adr_row_is_detected` | 24 |
| tests/governance/test_adr_status_index.py:222 `ComputeDriftTests.test_field_drift_in_title_is_detected` | 22 |
| tests/governance/test_agent_contract_fold.py:80 `TestAgentContractFold.test_agents_md_contains_migrated_invariants` | 23 |
| tests/governance/test_attestation_receipt_validator.py:200 `AttestationReceiptCliSmokeTest.test_cli_reports_resolved_receipt` | 26 |
| tests/governance/test_audit_absorption_duplicates.py:137 `CrossAdrDuplicateFiresTests.test_three_cross_adr_briefs_without_pairing_fires_on_each` | 27 |
| tests/governance/test_audit_check_covers_backfill.py:598 `TestLegitimateAuthoringExemption.test_pre_trailer_subject_marker_exempts_legitimate_authoring` | 23 |
| tests/governance/test_audit_check_covers_backfill.py:715 `TestBlockCreationAndOverlayMarker.test_same_commit_block_creation_in_existing_file_exempt` | 33 |
| tests/governance/test_audit_check_covers_backfill.py:754 `TestBlockCreationAndOverlayMarker.test_same_commit_block_creation_with_same_commit_receipt_still_flagged` | 42 |
| tests/governance/test_audit_check_covers_backfill.py:806 `TestBlockCreationAndOverlayMarker.test_same_commit_block_creation_with_later_ceremony_receipt_exempt` | 42 |
| tests/governance/test_audit_check_covers_backfill.py:865 `TestBlockCreationAndOverlayMarker.test_inline_audit_exempt_marker_exempts_decorator` | 34 |
| tests/governance/test_audit_check_covers_backfill.py:908 `TestBlockCreationAndOverlayMarker.test_inline_audit_exempt_marker_requires_reason_text` | 44 |
| tests/governance/test_audit_check_covers_backfill.py:957 `TestBlockCreationAndOverlayMarker.test_inline_audit_exempt_marker_must_be_on_decorator_line` | 45 |
| tests/governance/test_audit_check_covers_backfill.py:1098 `TestAmbiguousAttributionBlameReanchor.test_blame_reanchor_exempts_cross_paired_decorator` | 44 |
| tests/governance/test_audit_check_covers_backfill.py:1150 `TestAmbiguousAttributionBlameReanchor.test_blame_agreement_keeps_finding` | 48 |
| tests/governance/test_audit_check_covers_backfill.py:1203 `TestAmbiguousAttributionBlameReanchor.test_blame_failure_keeps_finding` | 43 |
| tests/governance/test_audit_check_covers_backfill.py:1252 `TestAmbiguousAttributionBlameReanchor.test_reanchor_to_receipt_commit_still_flagged` | 54 |
| tests/governance/test_audit_insights_shape.py:110 `InsightShapeAuditTests.test_clean_file_passes` | 22 |
| tests/governance/test_brief_path_validity_wiring.py:168 `TestAdrPromoteCheckScaffoldObpisPathValidity.test_brief_creates_marker_exempts_net_new_in_promotion` | 24 |
| tests/governance/test_brief_structure.py:181 `TestTasksSchemaEnforcement.test_pydantic_and_json_schema_readers_agree` | 21 |
| tests/governance/test_distribution_audit.py:577 `TestSurfaceDomainIsNotSelfSupplied.test_package_root_py_file_is_modelled_as_shipped` | 22 |
| tests/governance/test_eval_feedback_trailer.py:103 `TestEvalFeedbackTrailerValidation.test_passes_rule_edit_closing_eval_feedback_ghi_with_trailer` | 25 |
| tests/governance/test_eval_feedback_trailer.py:134 `TestEvalFeedbackTrailerValidation.test_eval_feedback_source_additive_with_task_passes_code_commit` | 32 |
| tests/governance/test_handoff_ruling_store.py:218 `HandoffCarriesPointerNotCorpusTests.test_legacy_prose_ancestor_still_contributes_its_corpus` | 25 |
| tests/governance/test_handoff_ruling_store.py:353 `OwnRulingsBookedAtAuthoringTests.test_linked_handoff_books_its_own_new_ruling_not_only_inherited_ones` | 23 |
| tests/governance/test_historical_waiver_integration.py:67 `TestHistoricalWaiverIntegration.test_waivered_pre_cutoff_receipt_passes` | 25 |
| tests/governance/test_justify_binding_gate.py:294 `TestSubjectIdentity.test_a_different_subject_never_binds` | 39 |
| tests/governance/test_kind_invariance_docs.py:151 `TestKindInvarianceArtifacts.test_closeout_evidence_cites_arb_receipts` | 24 |
| tests/governance/test_lock_exchange_coupling_validator.py:417 `TestLockHandoffCouplingReclaimAndReap.test_abandon_then_reclaim_same_agent_no_false_error` | 21 |
| tests/governance/test_lock_exchange_coupling_validator.py:443 `TestLockHandoffCouplingReclaimAndReap.test_cross_agent_reap_no_false_error` | 22 |
| tests/governance/test_promoted_advisory_audits.py:143 `PromotedAdvisoryAudits.test_behave_req_tags_kind_aware_exempts_covers_and_fence` | 22 |
| tests/governance/test_promoted_advisory_audits.py:908 `TaxonomyAuditNegativeCases.test_audit_never_mutates_files` | 22 |
| tests/governance/test_session_exit.py:379 `TestExitBeatIsIntentionalAboutBookmarks.test_a_staged_bookmark_rides_the_next_commit` | 25 |
| tests/governance/test_task_envelope_coherence.py:76 `TestSignatureA.test_worklog_without_task_id_under_active_task_fails` | 38 |
| tests/governance/test_task_envelope_coherence.py:123 `TestSignatureA.test_worklog_with_task_id_under_active_task_passes` | 41 |
| tests/governance/test_task_envelope_coherence.py:194 `TestSignatureA.test_historical_worklog_before_enforcement_epoch_is_clean` | 30 |
| tests/governance/test_task_envelope_coherence.py:229 `TestSignatureA.test_terminal_event_clears_task_under_divergent_obpi_id_spelling` | 59 |
| tests/governance/test_task_envelope_coherence.py:311 `TestSignatureA.test_meta_receipt_bind_ceremony_event_excluded_from_signature_a` | 30 |
| tests/governance/test_task_envelope_coherence.py:357 `TestSignatureA.test_non_ceremony_audit_receipt_under_active_task_still_fails` | 28 |
| tests/governance/test_task_envelope_coherence.py:399 `TestSignatureA.test_composition_rendered_telemetry_excluded_from_signature_a` | 31 |
| tests/governance/test_task_envelope_coherence.py:445 `TestSignatureA.test_commit_locus_artifact_edited_excluded_from_signature_a` | 30 |
| tests/governance/test_task_envelope_coherence.py:496 `TestSignatureA.test_tool_locus_artifact_edited_cannot_trip_signature_a` | 30 |
| tests/governance/test_task_envelope_coherence.py:560 `TestSignatureA.test_attested_without_task_id_still_trips_signature_a` | 28 |
| tests/governance/test_task_envelope_coherence.py:612 `TestSignatureA.test_obpi_brief_reflection_edit_under_active_task_is_clean` | 33 |
| tests/governance/test_task_envelope_coherence.py:650 `TestSignatureA.test_brief_authoring_edit_before_own_pipeline_is_clean` | 36 |
| tests/governance/test_task_envelope_coherence.py:698 `TestSignatureA.test_pool_adr_edit_under_active_task_is_clean` | 31 |
| tests/governance/test_task_envelope_coherence.py:739 `TestSignatureA.test_adr_decision_doc_edit_under_active_task_is_clean` | 46 |
| tests/governance/test_task_envelope_coherence.py:795 `TestSignatureA.test_support_manpage_edit_under_active_task_is_clean` | 38 |
| tests/governance/test_task_envelope_coherence.py:845 `TestSignatureA.test_uncovered_accept_with_req_id_under_active_task_is_clean` | 33 |
| tests/governance/test_task_envelope_coherence.py:887 `TestSignatureB.test_obpi_all_seq01_no_req_atomic_fails` | 30 |
| tests/governance/test_task_envelope_coherence.py:922 `TestSignatureB.test_obpi_all_seq01_req_atomic_covers_all_reqs_passes` | 31 |
| tests/governance/test_task_envelope_coherence.py:958 `TestSignatureB.test_obpi_seq02_exists_no_violation` | 40 |
| tests/governance/test_task_envelope_coherence.py:1003 `TestSignatureB.test_completed_full_slug_sees_short_form_seq02` | 36 |
| tests/governance/test_task_envelope_coherence.py:1046 `TestSignatureB.test_completed_full_slug_does_not_activate_short_only_legacy_channel` | 28 |
| tests/governance/test_task_envelope_coherence.py:1081 `TestSignatureB.test_historical_completed_obpi_before_enforcement_epoch_is_clean` | 30 |
| tests/governance/test_task_envelope_coherence.py:1120 `TestSignatureC.test_layer_drift_frontmatter_vs_ledger_fails` | 24 |
| tests/governance/test_task_envelope_coherence.py:1151 `TestSignatureC.test_same_task_id_all_channels_passes` | 25 |
| tests/governance/test_task_envelope_coherence.py:1181 `TestSignatureC.test_only_one_channel_populated_no_drift` | 24 |
| tests/governance/test_task_envelope_coherence.py:1245 `TestSignatureD.test_divergent_obpi_id_across_lifecycle_fails` | 30 |
| tests/governance/test_task_envelope_coherence.py:1280 `TestSignatureD.test_same_lineage_divergence_before_regression_cutover_passes` | 26 |
| tests/governance/test_task_envelope_coherence.py:1313 `TestSignatureD.test_consistent_obpi_id_passes` | 30 |
| tests/governance/test_task_envelope_coherence.py:1348 `TestSignatureD.test_grandfathered_historical_divergence_passes` | 30 |
| tests/governance/test_task_envelope_coherence.py:1903 `TestPendingObpiSigB.test_full_slug_brief_sees_short_form_subdivision_events` | 24 |
| tests/governance/test_task_envelope_coherence.py:1944 `TestPendingObpiAllSignatures.test_sig_a_unattributed_labor_flagged` | 28 |
| tests/governance/test_task_envelope_coherence.py:1985 `TestPendingObpiAllSignatures.test_sig_a_attributed_labor_is_clean` | 30 |
| tests/governance/test_tautological_tests.py:316 `TestAstScanner.test_scanner_returns_list_of_operation_instances` | 21 |
| tests/governance/test_tautological_tests.py:518 `TestDriftGate.test_no_drift_when_current_equals_baseline` | 33 |
| tests/mx/test_proxy_reality.py:114 `TestScan.test_scan_counts_multiple_fabrication_events` | 39 |
| tests/scripts/test_backfill_adr_taxonomy.py:263 `TestBackfillLedgerSafety.test_does_not_touch_ledger` | 22 |
| tests/skills/test_gz_justify_skill.py:141 `TestGzJustifyOutputContract.test_justify_first_line_is_frontmatter_or_h1` | 24 |
| tests/skills/test_skill_surface_sync_justify.py:272 `TestTestsDoNotMutateLivePaths.test_tests_do_not_mutate_live_repo_paths` | 36 |
| tests/test_ceremony_data_extraction.py:545 `TestRenderStep2WithPairingTable.test_step2_falls_back_to_prose_when_no_bullets` | 24 |
| tests/test_doc_coverage.py:97 `TestDiscoverCommands.test_discovers_nested_two_level_commands` | 31 |
| tests/test_flag_service.py:332 `TestRegistryIntegration.test_service_from_load_registry` | 25 |
| tests/test_foundation_limbo_gate.py:145 `TestFoundationLimboGate.test_a_witnessless_event_does_not_clear_the_finding` | 23 |
| tests/test_foundation_triage_rubric.py:119 `TestGatherFoundationIdsHandlesCanonicalSlug.test_gather_returns_canonical_slug_id` | 21 |
| tests/test_hooks.py:2336 `TestObpiCompletionValidatorHook.test_allows_completion_when_audit_evidence_keyed_by_full_slug` | 40 |
| tests/test_ledger.py:1876 `TestNestedEvidenceModels.test_evidence_models_are_frozen` | 41 |
| tests/test_ledger_correction_consumers.py:305 `LockCouplingAuditReadsEvidence.test_a_discharged_release_still_owes_its_exchange_record` | 31 |
| tests/test_ledger_correction_consumers.py:344 `LockCouplingAuditReadsEvidence.test_a_voided_release_owes_nothing` | 25 |
| tests/test_ledger_corrections.py:483 `TestRedParityConsumesCorrections.test_a_voided_witness_is_not_selected` | 32 |
| tests/test_ledger_durability.py:386 `TestTheBarrierRunsInsideTheTransaction.test_the_row_is_made_durable_before_the_lock_is_released` | 27 |
| tests/test_ledger_producer_probe.py:89 `ProducerProbeTests.test_typed_but_wrong_contract_cannot_receive_credit` | 26 |
| tests/test_manifest_v2.py:144 `TestManifestV2Validation.test_v1_manifest_still_passes` | 34 |
| tests/test_manifest_v2.py:182 `TestManifestV2Validation.test_invalid_schema_version_rejected` | 30 |
| tests/test_mutation_witness.py:389 `TestBehavioralFailure.test_setup_assertion_is_not_a_behavioral_kill` | 26 |
| tests/test_mutation_witness.py:418 `TestBehavioralFailure.test_unknown_and_ambiguous_nominations_are_inconclusive` | 22 |
| tests/test_obpi_complete_cmd.py:1190 `TestAuthenticityGateUnit.test_attest_exact_match_passes` | 22 |
| tests/test_obpi_complete_cmd.py:1285 `TestAgentRelayedEscapePath.test_non_tty_with_attestor_present_and_marker_returns_agent_relayed` | 22 |
| tests/test_obpi_prefix_match.py:202 `TestResolveObpiAmbiguityIsLoud.test_phantom_sibling_resolves_instead_of_raising` | 28 |
| tests/test_obpi_validator.py:572 `TestObpiValidator.test_authored_validation_flags_unregistered_gz_command_in_brief` | 26 |
| tests/test_obpi_validator.py:614 `TestObpiValidator.test_authored_validation_passes_when_all_gz_commands_resolve` | 31 |
| tests/test_obpi_validator.py:653 `TestObpiValidator.test_speculative_marker_suppresses_inline_gz_chain` | 25 |
| tests/test_obpi_validator.py:697 `TestObpiValidator.test_speculative_marker_suppresses_fenced_block` | 30 |
| tests/test_obpi_validator.py:796 `TestObpiValidator.test_authored_validation_passes_substantive_draft` | 32 |
| tests/test_obpi_validator.py:836 `TestObpiValidator.test_validate_clean_tree_passes_with_ledger_completion_evidence` | 32 |
| tests/test_persona_portability.py:155 `TestPortableValidationEndToEnd.test_custom_persona_validates_if_schema_compliant` | 22 |
| tests/test_pipeline_runtime.py:652 `TestValidateBriefForPipeline.test_authored_brief_returns_no_errors` | 41 |
| tests/test_pipeline_runtime.py:699 `TestValidateBriefForPipeline.test_thin_non_scaffold_brief_still_returns_authored_errors` | 26 |
| tests/test_pipeline_runtime.py:1228 `TestCheckReconcileReceiptGate.test_gate_does_not_block_on_req_count_only_drift` | 28 |
| tests/test_pipeline_runtime.py:1273 `TestCheckReconcileReceiptGate.test_gate_passes_when_receipt_fresh_and_clean` | 28 |
| tests/test_plan_audit_cmd.py:882 `TestPlanCreatesPathsSuppression.test_suppresses_existence_gap_for_declared_net_new_path` | 29 |
| tests/test_plan_audit_cmd.py:962 `TestPlanCreatesPathsSuppression.test_suppresses_existence_gap_for_brief_declared_create_path` | 28 |
| tests/test_quality.py:326 `TestCanonicalQualityPath.test_run_all_checks_fails_when_cli_audit_fails` | 24 |
| tests/test_quality.py:355 `TestCanonicalQualityPath.test_run_all_checks_fails_when_preflight_fails` | 24 |
| tests/test_red_witness.py:241 `TestRunRedWitness.test_worktree_is_removed_after_the_run` | 22 |
| tests/test_red_witness.py:298 `TestResolveIntroducingBase.test_it_resolves_the_parent_of_the_introducing_commit` | 22 |
| tests/test_req_kind_support_channel.py:398 `TestSupportChannelLegacyRegression.test_legacy_path_yields_advisory_support` | 23 |
| tests/test_rules.py:754 `TestRulesLayoutDualSurface.test_public_symbol_reexports_resolve` | 36 |
| tests/test_skill_body_audit.py:103 `TestSkillAuditWarningRendering.test_success_displays_warning_code_path_and_reason` | 21 |
| tests/test_skills_audit.py:219 `TestSkillAuditMirrorContracts.test_unknown_metadata_keys_are_allowed` | 27 |
| tests/test_sunset_migrate.py:928 `TestApplyIsPreflightedAndIdempotent.test_rerunning_apply_does_not_duplicate_witnesses` | 25 |
| tests/test_sunset_migrate.py:1549 `TestConcurrentApplyFailsClosed.test_a_renamed_demotion_with_unparked_children_is_reported` | 28 |
| tests/test_sync.py:946 `TestSyncControlSurfaces.test_canonical_sync_preflight_blocks_unsupported_transition` | 22 |
| tests/test_sync.py:1030 `TestSyncControlSurfaces.test_find_stale_mirror_paths_includes_retired_skill_mirrors` | 35 |
| tests/test_sync_surfaces.py:114 `TestAgentsPersonaReference.test_persona_references_survive_regeneration` | 28 |
| tests/test_validate.py:127 `TestValidateDocument.test_valid_adr` | 34 |
| tests/test_validate.py:675 `TestValidateManifest.test_valid_manifest` | 59 |
| tests/test_validate.py:751 `TestValidateLedger.test_valid_ledger` | 75 |
| tests/test_validate.py:975 `TestValidateLedger.test_invalid_obpi_req_proof_inputs_rejected` | 27 |
| tests/validators/test_unscoped_rules.py:388 `TestReadOnlyContract.test_module_source_has_no_destructive_calls` | 22 |

## 8. Process findings

**Boundary:** this audit examined commit history reachable from `5d9885a08c438b0aa546716b20a181c55342612e`, not another session's later commits. `git rev-parse --is-shallow-repository` returned `false`. It can establish what arrived in each commit. It cannot establish whether an author wrote a test before its implementation inside that commit. A batch commit is not proof of horizontal test authoring, and these histories cannot certify one observed RED per increment.

The ten selected closed OBPIs are the ten most recent still-completed identities in the ledger, including the five most recent. The ledger selects the sample; git history supplies the process evidence. The first five table rows are the five most recent completions. Selection receipt: `.gzkit/ledger.jsonl` lines `16348, 16171, 15855, 15808, 15505, 15433, 15246, 14462, 14403, 14159`, respectively. Read `receipt_event=completed` and `obpi_completion=attested_completed`, not the receipt's prose narrative.

| Closed OBPI | Completion | First commit of this OBPI's production change | First commit carrying its covering tests | Initial committed test batch | Ordering established by git |
|---|---|---|---|---|---|
| OBPI-0.35.0-06-validate-rendition-lineage | 2026-09-12 | `efb59b181e` | `efb59b181e` | 12 test methods, REQs 01–06 | Together; within-commit order unknown |
| OBPI-0.35.0-05-corpus-candidate-generator | 2026-09-11 | `edb52f1048` | `edb52f1048` | 17 test methods, REQs 01–09 | Together; within-commit order unknown |
| OBPI-0.35.0-03-retire-duplicate-invariant-entries | 2026-09-05 | N/A: corpus/brief work | N/A: no BEHAVIOR REQs | No covering test batch | Not a source/test increment; three SUPPORT REQs and one fence |
| OBPI-0.35.0-04-section-ownership-and-ratchet | 2026-09-05 | `79a1f6f037` | `79a1f6f037` | 22 test methods, REQs 01–07 | Together; within-commit order unknown |
| OBPI-0.35.0-02-content-withdraw-verb | 2026-08-26 | `d3fa949dcc` | `d3fa949dcc` | 25 test methods, REQs 01–07 | Together; within-commit order unknown |
| OBPI-0.35.0-01-corpus-tombstone-schema-and-fold | 2026-08-24 | `1bc7196bd2` | `1bc7196bd2` | 37 test methods, REQs 01–08 | Together; within-commit order unknown |
| OBPI-0.35.0-09-codex-playback-wiring | 2026-08-21 | `32e13d11f0` | `32e13d11f0` | 5 test methods for REQs 08/09; 9 more tagged methods at `521decc75a` cover 01–06/10/11 | Multiple batches; first production and first tests together; remaining REQ tests arrive later |
| OBPI-0.34.0-05-activate-standing-taxonomy-gate | 2026-07-31 | `c3b644992f` | `c3b644992f` | 18 test methods, REQs 02–04 | Together; within-commit order unknown |
| OBPI-0.34.0-04-execute-migration-populate-and-resense | 2026-07-30 | `b15d586da7` | `b15d586da7` | 5 test methods, REQs 01/03 | Together; within-commit order unknown |
| OBPI-0.34.0-03-terminal-partition-gate-and-doctrine-retirement | 2026-07-29 | `be26cef183` | `be26cef183` | 19 test methods, REQs 01–04 | Together; within-commit order unknown |

The production column identifies the behavior increment, not the birthday of an existing module. For example, the retire command and its test file both existed at `0222dd51fd` (2026-07-22); `d3fa949dcc` adds the OBPI's attestor/liveness behavior. `composer.py` and its test file existed at `3a7364155d` (2026-06-14); `edb52f1048` adds `generate_candidate`. Counting a pre-existing file as this OBPI's implementation would misdate the work.

Receipts for the table use `git log 5d9885a08c438b0aa546716b20a181c55342612e --reverse --format='%H %cs %s' -G 'REQ-<OBPI-prefix>-' -- tests`, followed by AST inspection of actual `@covers` decorators and `git diff <first>^ <first> -- src/gzkit tests`. Do not treat a REQ name in a fixture string as a test binding. The following source symbols and test files are present in the first diffs:

| Commit | Production evidence | Covering test evidence |
|---|---|---|
| `efb59b181e` | new `governance/trust_audits/rendition_lineage.py`, including `validate_rendition_lineage` | new `tests/governance/test_rendition_lineage.py` |
| `edb52f1048` | `content/composer.py::generate_candidate`, new `content/lineage.py` | `tests/content/test_composer.py`, `tests/content/test_lineage.py`, `tests/commands/test_content_compose.py` |
| `79a1f6f037` | new `content/ownership.py`, `commands/content/unown.py` | new `tests/content/test_ownership.py`, `tests/commands/test_content_unown.py` |
| `d3fa949dcc` | `commands/content/retire.py::_is_named`, `_floor_liveness_delta`, extended command | `tests/commands/test_content_retire.py` |
| `1bc7196bd2` | `content/models/corpus.py::validate_tombstone_algebra`, `_liveness`, replaced `effective_corpus` | `tests/content/test_corpus_model.py` |
| `32e13d11f0` | `governance/compose.py::agent_contract_consumer`, `render_agents_md` consumer parameter; `sync_surfaces.py` routing | `tests/content/test_vendor_manifest.py` |
| `c3b644992f` | `quality.py::run_taxonomy_audit`, check step and registration guards | `tests/governance/test_standing_taxonomy_gate.py`, `test_registration_membrane.py` |
| `b15d586da7` | new `foundation/sunset_migrate.py`, `commands/adr_demote.py` preservation | `tests/test_sunset_migrate.py` |
| `be26cef183` | `governance/trust_audits/taxonomy.py::_grandfathered_event_ids`, `_limbo_error` | `tests/test_foundation_limbo_gate.py`, `test_foundation_doctrine_retirement.py` |

A full-history path/diff scan produced this output:

```text
command: uv run --no-project --python <existing-interpreter> python history/full_history_scan.py
pinned_head: 5d9885a08c438b0aa546716b20a181c55342612e
shallow: false
commits_touching_src_or_tests: 1884
commits_touching_production_python_and_test_python: 1235
cochange_commits_with_assertion_removal_lines: 267
removed_assertion_lines: 1934
added_assertion_lines_in_those_commits: 6374
script_exit=0
```

The script executes `git log <pin> --format='@@COMMIT %H' --name-only -- src/gzkit tests`, then `git diff <sha>^ <sha> --unified=0 -- <changed-test-paths>`. These are **candidate diff-line counts**, not counts of defective tests: moves, rewritten assertions, comments containing assertion text, and unrelated source changes all enter this first pass. Every cochange and candidate line is retained in the audit data. An AST follow-up compared assertion calls within matching class/method identities across all 267 candidate commits and found four comparator-change pairs; two change the accepted contract, one preserves the stricter platform check, and one loosens a command-count assertion.

| Commit; test; receipt | Observed change | Disposition of the observation |
|---|---|---|
| `9e539d0665ebcc1f5567ab1c0348a2243b94ce79`; `TestDiscoverCommands.test_total_command_count`; `git diff 9e539d0665^ 9e539d0665 -- tests/test_doc_coverage.py src/gzkit/cli/main.py` | `assertEqual(len(self.commands), 53)` becomes `assertGreaterEqual(len(self.commands), 50)` while the same commit adds the covers CLI. | **Loosened.** The old assertion rejected missing commands below 53; the new one accepts 50–52 and any excess. The fixed minimum remains at baseline `tests/test_doc_coverage.py:190–196`. This test also claims REQ-0.0.6-01-02, which requires checking six documentation surfaces and producing a `CoverageReport` (its brief:132), neither exercised by this count. Rewrite against the required behavior. |
| `c9e62790732c8a87f740c788a5e13dec9ea7a4cd`; `TestTrailingFragmentRecovery.test_a_killed_writer_leaves_a_store_the_next_writer_can_use`; `git diff c9e6279073^ c9e6279073 -- tests/test_ledger_transaction_boundary.py` | Unconditional `returncode == -9` becomes nonzero plus conditional equality to `-signal.SIGKILL`; Windows fallback explicitly calls `os._exit(137)`. | This is not an established weakening on POSIX: exact SIGKILL remains asserted. The changed source files in that commit are other modules, so do not claim the test and its ledger implementation co-evolved merely because both src/ and tests/ changed. |
| `b6c26750fdc943fce5e605c94daf1c032979718e`; `TestObpiValidator.test_recorder_appends_receipt_to_ledger`; `git diff b6c26750fd^ b6c26750fd -- tests/test_obpi_validator.py src/gzkit/hooks/obpi.py` | Expected commit anchor changes from `== "0000000"` to `!= "0000000"` as fixture Git history and real-anchor production handling are introduced. | Changed expected contract; not evidence that a failing behavior was hidden. |
| `deedcdbb66969dc5fabd748d02c837ece3eedb39`; `TestGitSyncCommand.test_git_sync_dry_run_in_git_repo`; `git diff deedcdbb66^ deedcdbb66 -- tests/test_cli.py src/gzkit/cli.py` | Removed `sync-repo` alias changes from exit 0 to nonzero plus `"invalid choice"`. | Changed expected contract paired with alias removal, not a blanket weakening. |
| `428eb35d01dacc2eaef9ee2b34cd99a24d942569`; `tests/commands/test_content_unown.py`, old hunk `@@ -1897,14 +1940,134 @@` | Removes `if landed:` around the only `assertNotIn("nothing written", ...)`; adds an unconditional `len(landed) == 1` and unconditional prose assertion. | Historical D5 defect repaired. Before this commit, absent witness production could skip the assertion. Do not count the repaired version as an open D5 defect. |
| `2c32d6de81ca57edb720ce8aaab0af6e3f643dac`; `tests/content/test_composer.py`, old hunks at 617 and 873 | Removes tuple/type/length-only span assertions and expected spans computed with production `iter_section_boundaries`; adds explicit contract-derived candidate bytes and offsets. | Historical weak/circular oracles repaired. Removing assertions here strengthened the behavior proof. |
| `3d4f06acd99bec40b0aa35f0c4353a31a0362809`; `tests/content/test_ownership.py`, old hunks at 718, 745, 2100 | Changes generic REQ-id / `"999"` / `"prior"` text assertions to specific missing-pointer, floor-equality and missing-prior failure assertions with fixtures reaching the intended guard. | Historical false-positive error assertions repaired; the old event id itself contained `"prior"`. |
| `25afe7a246bdb3ce98d06df2a63600e709aa221d`; `tests/commands/test_content_unown.py`, old hunks at 6505 and 6542 | Recovery expectations change `exit 0 → exit 2`; `len(minted) == 2` becomes exact existing witness list `[attested]`; wrong predecessor message becomes chain-tip refusal. | Expected values change with a repair preventing replay from minting a second row off a stale floor; this narrows accepted behavior. |
| `18454c9066d54c8d14f61c5e43ff3241a45ee757`; `tests/commands/test_content_unown.py`, old hunk at 5592 | Deletes the test accepting unsupported directory fsync with exit 0 and deleted recovery material; replaces it with explicit preservation tests across journal-present/absent states. | Expected policy tightened to preserve evidence. The deletions are not proof of weakened protection. |
| `32e13d11f0c469537e8b3859e89b9bc5ab05dca3`; `tests/governance/test_setpoint_coherence.py:38` in its diff | Expected uncovered route changes `"codex" → "root"` with the AgentContract routing collapse. | Literal changed with the declared routing contract. |

The command-count defect is observable without editing any source file: in the pinned scratch copy, initialize `TestDiscoverCommands`, invoke `test_total_command_count`, then replace that test instance's `commands` input with its first 50 elements and invoke the same method again. This is an input counterexample, not a Cosmic Ray mutant and not an assertion about the whole suite:

```text
discovered_commands= 136 test=PASS
retained_commands= 50 discarded_commands= 86 test=PASS
counterexample_exit=0
```

### Phase 5 limitations

The full history was enumerated and all 267 assertion-removal candidate commits were scanned by AST, but every semantic change in every historical test was not manually adjudicated. Renames, helper rewrites, and multiline expected-value edits are not exhausted by comparator pairing. The table reports verified examples and the nine selected implementation beginnings. It does not claim that the complete history has only one weakening, that every cochange couples a test to the changed source, or that co-committed tests were authored horizontally. Local uncommitted RED/GREEN ordering cannot be recovered from git.

## 9. Pool ADR proposal — unapplied unified diff

```text
command: uv run --no-project --python <existing-interpreter> python history/pool_verify.py
pin: 5d9885a08c438b0aa546716b20a181c55342612e
frontmatter_status: Pool
body_status: Proposed
recorded_date_added: 2026-03-21
body_semver_reservation: 0.31.0
decomposition_rows: 10
pending_rows: 9
withdrawn_rows: 1
current_dead_id_brief_paths: []
markdown_documents_with_dead_id: 3
matching_markdown_lines: 10
```

1. **Corrected:** the pool frontmatter is `Pool`, but body status says `Proposed`. It records Date Added 2026-03-21. Nine rows are Pending and one is Withdrawn, rather than every row being Pending. Receipts: `docs/design/adr/pool/ADR-pool.new-cli-command-absorption.md:3`, `:21–24`, `:82–93`.
2. **Confirmed collision:** the body reserves 0.31.0, while `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md:2–6` uses that ID and semver for the validated feature.
3. **Confirmed missing-current-brief claim:** pool lines 95–97 assert `obpis/OBPI-0.31.0-*.md` and one brief per row. `git ls-tree -r --name-only <pin>` contains no filename beginning `OBPI-0.31.0-07`. The brief did historically exist: `git log <pin> -- '**/OBPI-0.31.0-07*'` includes its removal at `993a16c11` (2026-05-23) and earlier commits back to `e3c2c6d85` (2026-03-21). The defect is stale booking, not proof the brief never existed.
4. **Confirmed stale booking:** the appraisal says `OBPI-0.31.0-07-mutate` is booked at lines 35, 57, 87, 154. The last is a broken current link into the removed feature package.
5. **Confirmed diagnostic boundary:** `docs/governance/enforcement-claim-nc-audit-2026-07-18.md:208–216` disqualifies mutmut's pytest runner and recommends Cosmic Ray on enforcement modules as a diagnostic, with no repository-wide score floor.

The proposal follows `docs/governance/pool-curation.md:27` and `docs/user/concepts/adr-taxonomy.md`'s pool section: flat pool identity, no reserved semver or kind field; deliberate promotion with sponsor, acceptance criteria, settled dependencies and capacity. This is only a proposed diff. It does not create an ADR, book an OBPI, write the ledger, or authorize promotion.

All tracked Markdown documents citing the dead identifier were found with `git grep -n 'OBPI-0\.31\.0-07' <pin> -- '*.md'`. Corrected sentences/routes for all three documents:

| Document and original line(s) | Proposed correction |
|---|---|
| Pool ADR:90, with mapping assertion:95–97 | “`mutate`, `test-quality`, and `test-times` are proposed for ADR-pool.test-integrity-tooling under local keys TI-01–03; no current brief is claimed. The remaining seven historical command rows use local CLI keys and retain the withdrawn complexity row.” |
| Appraisal:35 | “Targeted mutation experiments exist in `src/gzkit/mutation_witness.py`; the general Cosmic Ray CLI port remains pool intent. The former brief was removed by the 2026-05-23 demotion and is not a current work order; the test audit proposes ADR-pool.test-integrity-tooling, TI-01.” |
| Appraisal:57 | “Mutation tooling was demoted with its former package on 2026-05-23; the 2026-09-24 audit proposes pool item TI-01, without assuming a validator scope or a score floor.” |
| Appraisal:87 | Replace the obsolete Wave-1 booking with “mutation tooling (historical Wave 1; proposed current home: ADR-pool.test-integrity-tooling, TI-01)”. |
| Appraisal:154 | “Proposed backlog home for general mutation tooling: ADR-pool.test-integrity-tooling, TI-01; no active OBPI is booked.” |
| 2026-04-26 improvement-plan handoff:28 | Preserve the historical TASK/lock account and precede it with a dated correction: those identifiers name the former package, demoted 2026-05-23, and prescribe no current work. Rewriting a historical lock as a lock that never existed would fabricate history. |
| Same handoff:55 | “General mutation tooling (historical Wave 1 proposal) — pool intent; no current OBPI. The former brief was removed at demotion; a future promotion must decide the tool and diagnostic contract, with no inherited kill-rate gate.” |
| Same handoff:121 | “General mutation tooling — consider the proposed ADR-pool.test-integrity-tooling, TI-01; do not resume the removed OBPI or claim its historical identifier.” |
| Same handoff:132 | “Historical 2026-04-26 lock record for OBPI-0.31.0-07-mutate: released then; not a current lock or work order.” |
| Same handoff:133 | “Historical 2026-04-26 pipeline record for OBPI-0.31.0-07-mutate: cleared then; this account prescribes no current pipeline action.” |

Proposed promotion-discussion trigger: at least one green-baseline enforcement module with at least one conclusive reviewed non-equivalent mutant and a reviewed non-equivalent survivor share greater than zero. The minimum conclusive population is one because one confirmed undetected guard fault establishes the gap; this is not a comparative efficacy estimate or a statistical confidence claim. Exclude and separately report equivalent/unreviewed/incompetent/timed-out outcomes. Script evaluation does not replace the operator's promotion decision. The dependency decision belongs to the future feature ADR; the stdlib route is the current mutation harness plus `ast`, `unittest`, `subprocess`, `tempfile`, `sqlite3`, and the external-engine alternative is justified by a maintained general operator/source-rewriting/session engine rather than falsely asserting that Python cannot implement one.

The unified diff is in the report's proposed-change block; its syntax/applicability was checked without applying it:

```text
command: git apply --check /private/tmp/gzkit-test-audit-20260924/history/pool-proposal-final.diff
proposal_apply_check_exit=0
applied=false
```

```json
{
  "command": [
    "git",
    "apply",
    "--check",
    "/private/tmp/gzkit-test-audit-20260924/history/pool-proposal-final.diff"
  ],
  "exit_status": 0,
  "stdout": "",
  "stderr": "",
  "applied": false
}
```

```diff
--- a/docs/design/adr/pool/ADR-pool.new-cli-command-absorption.md
+++ b/docs/design/adr/pool/ADR-pool.new-cli-command-absorption.md
@@ -1,172 +1,77 @@
 ---
 id: ADR-pool.new-cli-command-absorption
 status: Pool
-lane: heavy
 parent: PRD-GZKIT-1.0.0
 ---

-<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->
-
-# ADR-pool.new-cli-command-absorption: New CLI Command Absorption
-
-## Tidy First Plan
-
-- Prep tidyings (behavior-preserving):
-  1. Audit opsdev's quality tooling commands to catalog every command, its arguments, output format, and line count.
-  1. Audit gzkit's existing CLI surface to confirm these 10 commands have no equivalent in gzkit today.
-  1. Create a portability matrix assessing each command's governance-generality vs project-specificity.
+# ADR-pool.new-cli-command-absorption: Remaining CLI Command Absorption

 **Date Added:** 2026-03-21
-**Date Closed:**
-**Status:** Proposed
-**SemVer:** 0.31.0
-**Area:** CLI Commands --- Companion Absorption (Quality Tooling)
-
-## Agent Context Frame --- MANDATORY
-
-**Role:** Absorption evaluator --- porting quality tooling commands from opsdev to gzkit, adapting each to gzkit's CLI conventions (argparse, exit codes, --json/--plain output).
-
-**Purpose:** When this ADR is complete, gzkit owns 10 quality tooling commands that exist in opsdev but have no gzkit equivalent: SLOC analysis, cyclomatic complexity checking, per-test duration tracking, AST-based test quality metrics, code quality violation scanning, continuous monitoring, mutation testing, manpage validation, docstring sync, and docstring coverage. Each command has been ported with gzkit CLI conventions, unit tests, and documentation.
-
-**Goals:**
-
-- All 10 quality tooling commands are ported from opsdev to gzkit
-- Each ported command follows gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output
-- Each ported command has unit tests with >= 40% coverage
-- Each ported command has manpage documentation
-- The subtraction test holds: opsdev's quality tooling after porting contains only project-specific wrappers
-
-**Critical Constraint:** All 10 commands must be ported. These are genuinely generic quality tools (SLOC, complexity, test metrics, mutation testing, manpage validation) --- none are airline-specific. The question is not whether they belong in gzkit, but how to adapt them to gzkit's CLI conventions.
-
-**Anti-Pattern Warning:** A failed implementation looks like: porting commands verbatim from opsdev without adapting them to gzkit's CLI conventions. Each ported command must use argparse (not click), return proper exit codes (0/1/2/3), support --json/--plain output, and include help text with examples. Equally bad: declaring a command "ported" without tests or documentation.
-
-**Integration Points:**
-
-- `src/gzkit/commands/` --- new command modules
-- `src/gzkit/config.py` --- configuration consumed by quality tooling (depends on ADR-0.30.0)
-- `docs/user/manpages/` --- manpage documentation for each ported command
-- `tests/` --- unit tests for each ported command
-
----
-
-## Feature Checklist --- Appraisal of Completeness
-
-- Scope and surface
-  - External contract will change (Heavy lane) --- 10 new CLI commands
-- Tests
-  - Each ported command must have unit tests; coverage >= 40%
-- Docs
-  - Each ported command must have manpage documentation and help text with examples
-- OBPI mapping
-  - Each numbered checklist item maps to one brief; 10 items = 10 briefs
+**Status:** Pool
+**SemVer:** Unassigned; allocate only at promotion.

 ## Intent

-opsdev contains quality tooling commands that are genuinely governance-generic --- SLOC analysis (radon), cyclomatic complexity checking (xenon), per-test duration tracking, AST-based test quality metrics, code quality violation scanning, continuous monitoring, mutation testing (Cosmic Ray), manpage structure validation, docstring synchronization, and docstring coverage (interrogate). None of these are airline-specific or project-specific --- they are the kind of quality tooling that every gzkit-governed project should have access to. This ADR governs the porting of all 10 commands, adapting each to gzkit's CLI conventions.
+Evaluate the remaining opsdev quality-tooling ports independently of the three
+test-integrity candidates. This is backlog intent, not an active work order.

-## Decision
+## Proposed split — 2026-09-24

-- Each of the 10 opsdev quality commands gets individual OBPI examination and porting
-- For each command: read the implementation, adapt to gzkit CLI conventions, write tests, create documentation
-- All commands must support: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples
-- Ported commands must follow gzkit conventions: Pydantic models, pathlib.Path, UTF-8 encoding, no bare except
+Move `mutate`, `test-quality`, and `test-times` to
+[ADR-pool.test-integrity-tooling](ADR-pool.test-integrity-tooling.md), allowing
+that scope to be considered for promotion on its own. Retain the other seven
+original command rows here, including the already-withdrawn complexity row.
+This proposal promotes neither entry and reserves no release number.

-## Interfaces
+`ADR-0.31.0-obpi-state-machine` holds SemVer 0.31.0. The former absorption
+package was demoted at `993a16c11` on 2026-05-23, removing its briefs. Its
+old numbered OBPI references are historical identities, not current briefs.

-- **CLI (external contract):** `uv run gz {command}` --- 10 new commands
-- **Config keys consumed (read-only):** `.gzkit/manifest.json`, config files from ADR-0.30.0
-- **Internal APIs:** New modules in `src/gzkit/commands/` providing quality tooling
+## Target Scope

-## OBPI Decomposition --- Work Breakdown Structure (Level 1)
+The keys below are document-local candidate keys, not OBPI identifiers.
+At promotion, reassess each candidate against the then-current CLI, allocate
+one feature ADR, and author one OBPI brief per accepted checklist item.

-| # | OBPI | Specification Summary | Lane | Status |
-|---|------|----------------------|------|--------|
-| 1 | OBPI-0.31.0-01 | Port `sloc-scan` (159 lines) --- radon-based SLOC analysis | Heavy | Pending |
-| 2 | OBPI-0.31.0-02 | ~~Port `complexity-check` (122 lines) --- xenon cyclomatic complexity~~ → **subsumed by [ADR-0.0.29](../../foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md)** | Heavy | Withdrawn (2026-04-25) |
-| 3 | OBPI-0.31.0-03 | Port `test-times` (87 lines) --- per-test duration tracking | Heavy | Pending |
-| 4 | OBPI-0.31.0-04 | Port `test-quality` (495 lines) --- AST-based test quality metrics | Heavy | Pending |
-| 5 | OBPI-0.31.0-05 | Port `metrics scan` (429 lines) --- code quality violation scanning | Heavy | Pending |
-| 6 | OBPI-0.31.0-06 | Port `metrics report/watch` (429 lines) --- continuous monitoring and reporting | Heavy | Pending |
-| 7 | OBPI-0.31.0-07 | Port `mutate` (450 lines) --- Cosmic Ray mutation testing | Heavy | Pending |
-| 8 | OBPI-0.31.0-08 | Port `validate-manpages` (473 lines) --- manpage structure validation | Heavy | Pending |
-| 9 | OBPI-0.31.0-09 | Port `sync-manpage-docstrings` (473 lines) --- docstring synchronization | Heavy | Pending |
-| 10 | OBPI-0.31.0-10 | Port `interrogate` (wrapper) --- docstring coverage integration | Heavy | Pending |
+| Key | Original row | Candidate | Disposition |
+|---|---:|---|---|
+| CLI-01 | 1 | `sloc-scan`: SLOC analysis | Pending evaluation |
+| CLI-02 | 2 | `complexity-check`: cyclomatic complexity | Withdrawn 2026-04-25; subsumed by [ADR-0.0.29](../foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md) |
+| CLI-05 | 5 | `metrics scan`: code quality violation scanning | Pending evaluation |
+| CLI-06 | 6 | `metrics report/watch`: monitoring and reporting | Pending evaluation |
+| CLI-08 | 8 | `validate-manpages`: manpage structure validation | Pending evaluation |
+| CLI-09 | 9 | `sync-manpage-docstrings`: docstring synchronization | Pending evaluation |
+| CLI-10 | 10 | `interrogate`: docstring coverage integration | Pending evaluation |

-**Briefs location:** `obpis/OBPI-0.31.0-*.md`
+**Briefs:** This flat pool entry has no current OBPI package. These rows do not
+claim a corresponding brief exists. Briefs are authored at promotion, using
+the promoted ADR's newly allocated identifier.

-**WBS Completeness Rule:** Every row in this table has a corresponding brief file.
+## Promotion decisions

-**Lane definitions:**
-
-- **Heavy** --- All OBPIs are Heavy because each introduces a new CLI command (external contract change)
-
----
-
-## Rationale
-
-opsdev's quality tooling represents approximately 3,100+ lines of governance-generic code that every project benefits from. SLOC analysis, complexity checking, test quality metrics, mutation testing, and manpage validation are not airline-specific --- they are fundamental code quality tools. gzkit as a governance framework must own these tools so that any gzkit-governed project gets quality tooling out of the box, rather than each project reimplementing these capabilities. This ADR depends on ADR-0.25.0 (core infrastructure) and ADR-0.30.0 (config schema) because ported commands consume infrastructure and configuration provided by those ADRs.
-
-## Comparator Uplift (2026-05-07)
-
-Front-door improvements need command surfaces operators can discover. This ADR
-should bias new commands toward witnessed entry points such as `workspace`,
-`workflow inspect`, `vendor matrix`, `skill feedback-report`, and `uat`, with
-manpage examples bound to captured output where ADR-0.46.0 applies.
+- Establish that a proposed command adds a capability the current gzkit CLI
+  does not already supply; the original port inventory is a dated proposal.
+- Choose the supported input, output, failure, and configuration contracts.
+- Resolve actual capability dependencies; the old references to ADR-0.25.0
+  and ADR-0.30.0 must not be treated as current dependencies by number alone.
+- Use stdlib first. Any dependency needs an explicit promoted ADR/OBPI
+  rationale naming the capability stdlib cannot supply and its maintenance cost.
+- Follow [pool curation](../../../governance/pool-curation.md): sponsor,
+  acceptance criteria, settled dependencies, capacity, and operator promotion.

 ## Consequences

-- gzkit gains 10 new CLI commands, significantly expanding its quality tooling surface
-- Every gzkit-governed project gets access to SLOC, complexity, test quality, and mutation testing
-- Manpage validation and docstring sync enforce documentation quality programmatically
-- opsdev can replace its implementations with gzkit equivalents, reducing its own codebase
-- New dependencies may be required (radon, xenon, cosmic-ray, interrogate) --- these must be managed as optional dependencies
+The test-integrity decision can be considered without committing to the six
+remaining pending ports. The withdrawn row stays in the historical inventory.
+No CLI, dependency, validator, release, ledger event, or execution commitment
+is introduced by this pool proposal.

-## Evidence (Four Gates)
+## Evidence

-- **ADR:** this document
-- **TDD (required):** `tests/test_cmd_*.py` --- unit tests for each ported command
-- **BDD (Heavy):** `features/quality_tooling.feature` --- smoke tests for new CLI commands
-- **Docs:** Manpages in `docs/user/manpages/`, help text with examples in each command
-
----
-
-## Evidence Ledger (authoritative summary)
-
-### Provenance
-
-- **Git tag:** `adr-0.31.0`
-- **Dependencies:** ADR-0.25.0, ADR-0.30.0
-
-### Source & Contracts
-
-- opsdev source: quality tooling commands (~3,100+ lines total)
-- gzkit target: `src/gzkit/commands/` --- 10 new command modules
-
-### Tests
-
-- Unit: `tests/test_cmd_*.py` (per ported command)
-
-### Docs
-
-- Manpages: `docs/user/manpages/` (per ported command)
-- Governance: this ADR
-- Decision rationale: per OBPI brief in `obpis/`
-
----
-
-## Completion Checklist --- Post-Ship Tidy (Human Sign-Off)
-
-| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
-|---------------|-------|-------------------|----------|-------|
-| `src/gzkit/commands/` | M | All 10 commands ported | Test output | |
-| `tests/` | M | All ported commands tested | `uv run gz test` | |
-| `docs/user/manpages/` | P | All ported commands documented | Manpage review | |
-| `obpis/` | P | All 10 OBPIs have evidence documented | Brief review | |
-
-### SIGN-OFF --- Post-Ship Tidy
-
-Human Approver: ___________________________
-
-Date: _________________________
-
-Decision: Accept | Request Changes
+- Original inventory dated 2026-03-21; retained by git history.
+- Demotion commit `993a16c11` removed the former feature package and briefs.
+- Audit baseline `5d9885a08c438b0aa546716b20a181c55342612e`, measured
+  2026-09-24: this pool frontmatter says Pool while its former body said
+  Proposed, reserved 0.31.0, and claimed every numbered row had a brief.
+- The test-integrity pilot and proposed promotion trigger belong in the
+  [split entry](ADR-pool.test-integrity-tooling.md).
--- /dev/null
+++ b/docs/design/adr/pool/ADR-pool.test-integrity-tooling.md
@@ -0,0 +1,125 @@
+---
+id: ADR-pool.test-integrity-tooling
+status: Pool
+parent: PRD-GZKIT-1.0.0
+---
+
+# ADR-pool.test-integrity-tooling: Test Integrity Tooling
+
+**Date Added:** 2026-09-24 (proposed by the test audit; not yet adopted)
+**Status:** Pool
+**SemVer:** Unassigned; allocate only at operator-authorized promotion.
+
+## Intent
+
+Make test sensitivity measurable for enforcement code: establish which
+specified faults an independently checked unittest command detects, surface
+weak test structure, and measure the cost of that evidence. Preserve the
+separation between executing a line and asserting the behavior on that line.
+
+## Target Scope
+
+These are local candidate keys, not OBPI identifiers or existing briefs.
+At promotion, author a feature ADR and one brief per accepted checklist item.
+
+- **TI-01 — `mutate`:** reproducible mutation diagnostics for explicitly named
+  enforcement modules. Run a clean baseline, isolate every mutant, invoke
+  `python -m unittest` on declared tests, enforce timeouts, and retain distinct
+  killed, survived, incompetent, and timed-out outcomes. A nonzero exit is not
+  automatically a semantic kill; classify import, setup and infrastructure
+  errors separately. Retain mutant identity, actual diff, source commit,
+  dependency versions, command, test outcomes, and raw output as CI artifacts.
+- **TI-02 — `test-quality`:** AST measurements with stated detection limits;
+  distinguish scan candidates from confirmed defects, account for inherited
+  assertion helpers, and do not grade a test's semantics from its shape alone.
+- **TI-03 — `test-times`:** per-test unittest duration measurements with test
+  identity and run metadata, used to size the diagnostic and review redundant
+  work; timing by itself does not justify deleting a behavior proof.
+
+## Pilot evidence — 2026-09-24
+
+Baseline source commit: `5d9885a08c438b0aa546716b20a181c55342612e`.
+
+| Module | Mutants | Killed | Survived | Incompetent | Timed out | Survival |
+|---|---:|---:|---:|---:|---:|---:|
+| covers | 247 | 163 | 84 | 0 | 0 | 34.01% (n=247) |
+| mutation_witness | 336 | 245 | 90 | 0 | 1 | 26.79% (n=336) |
+| red_parity | 164 | 114 | 50 | 0 | 0 | 30.49% (n=164) |
+| red_witness | 355 | 204 | 151 | 0 | 0 | 42.54% (n=355) |
+| req_coverage | 46 | 28 | 18 | 0 | 0 | 39.13% (n=46) |
+| tautological_tests | 580 | 239 | 341 | 0 | 0 | 58.79% (n=580) |
+| test_shape | 117 | 50 | 67 | 0 | 0 | 57.26% (n=117) |
+| validate_commit_trailers | 59 | 38 | 19 | 2 | 0 | 32.20% (n=59) |
+| verifier_pipe_gate | 1130 | 554 | 573 | 0 | 3 | 50.71% (n=1130) |
+
+All nine selected baselines passed. The pilot generated 3,034 mutants across
+nine modules and selected 600 distinct unittest methods. Raw kills include
+nonzero error exits; the audit separately distinguishes assertion output.
+Two reviewed non-equivalent survivors in req_coverage.py (comparison at line
+130 and continue at line 131) pass the selected 24 tests and fail an independent
+exact-filter discriminator. The attempted full-suite replay stopped on its
+clean-baseline timeout before either mutation, so full-suite survival is not
+established. See docs/evals/test-suite-integrity-audit-2026-09-24.md for every
+outcome, source/test command, equivalence limits and machine-readable identities.
+
+This is a scoped diagnostic. It establishes no repository-wide mutation score
+floor and does not establish that a survivor is non-equivalent merely because
+it survived. Evidence is keyed to a mutant and test command, not to a line
+alone. A script must reject missing, baseline-failing, or unclassified runs.
+
+## Proposed machine-decidable trigger for promotion consideration
+
+Recommend a promotion discussion when at least one enforcement module has:
+(a) a passing baseline, (b) at least one conclusive, reviewed non-equivalent
+mutant, and (c) a reviewed non-equivalent survival rate greater than **0%**.
+Compute `survived_non_equivalent / (killed_non_equivalent + survived_non_equivalent)`
+from retained records; no denominator means INSUFFICIENT_EVIDENCE, not 0%.
+Timed-out, incompetent, equivalent and unreviewed cases are reported separately.
+Bind each review disposition to the mutant diff and source commit so an
+unreviewed survivor cannot satisfy the predicate.
+
+The threshold is a diagnostic trigger, not a score floor: one confirmed
+undetected enforcement fault establishes the gap without rewarding tests that
+kill irrelevant mutants. It does not authorize promotion or execution. Sponsor,
+clear acceptance criteria, settled dependencies, capacity, campaign order and
+explicit operator initiation still govern under the pool-curation policy.
+
+## Decision required at promotion — Stdlib-First
+
+First evaluate the existing `mutation_witness` harness with stdlib `ast`,
+`unittest`, `subprocess`, `tempfile`, and `sqlite3`. That path supports bounded,
+hand-authored fault experiments and may be enough for the required contract.
+Python can implement a general mutator; do not claim otherwise. The stdlib
+has no supplied general mutation-operator catalog, source mutation engine, and
+persistent mutation-session scheduler. Building those would make gzkit their
+maintainer.
+
+The promoted ADR must choose whether the measured breadth and repeatability
+of Cosmic Ray justify adopting and maintaining that external engine instead.
+Name its pinned version, transitive dependency and platform costs, runtime
+budget, and retained-evidence contract. If adopted, approve it explicitly as
+optional test tooling, retain unittest as the test runner, and keep it out of
+gzkit's runtime dependency set unless a separately justified contract requires
+otherwise. The present audit installs nothing in gzkit.
+
+## Alternatives and tradeoff
+
+1. Continue stdlib-only, hand-authored mutation experiments. Small dependency
+   surface, but operator selection and experiment implementation remain work.
+2. Adopt Cosmic Ray as scoped optional tooling. General fault generation and
+   reproducible sessions, with new dependency, execution and triage costs.
+3. Require a repository-wide kill score. Rejected as this proposal's design:
+   equivalent or irrelevant mutants would reward implementation-pinning tests.
+
+## Promotion criteria and evidence boundaries
+
+The operator cannot promote now. This pool records the proposed split and
+measurement, with no active OBPI, reserved semver, or automatic promotion.
+The promoted design must also evaluate the three pool-worthiness conditions:
+reversal cost, context-dependent decision, and a named losing alternative.
+
+The 2026-07-18 enforcement audit recommends Cosmic Ray scoped to enforcement
+modules as a diagnostic with no repository-wide score floor; this proposal
+preserves that boundary. See
+[enforcement-claim-nc-audit-2026-07-18.md](../../../governance/enforcement-claim-nc-audit-2026-07-18.md)
+and [pool-curation.md](../../../governance/pool-curation.md).
--- a/docs/governance/harness-engineering-appraisal.md
+++ b/docs/governance/harness-engineering-appraisal.md
@@ -32,7 +32,7 @@
 ## Where gzkit Can Improve

 - **No in-session sidecar.** Sensors are gated at commit, OBPI completion, or `gz check`. There is no live process watching edits and feeding deltas back to the agent during a session — the most distinctive thing in Böckeler's experiment. The OBPI pipeline is ceremony, not continuous quality feedback. This is a real gap; agents work blind between gate transitions.
-- **Mutation testing is absent.** Coverage floor (40%) is a weak signal — exactly the failure mode Böckeler demonstrated (100% statement coverage, zero unit tests, missing assertions). gzkit's own Invariant 6f names this problem; the mechanical defense is missing. `cosmic-ray` (cross-platform; `mutmut` requires `fork()` and is Unix-only) is the natural fit. Already booked as `OBPI-0.31.0-07-mutate` (port from airlineops `src/opsdev/commands/mutation_tools.py`).
+- **Mutation scope correction, 2026-09-24.** Targeted mutation experiments exist in `src/gzkit/mutation_witness.py`; the general Cosmic Ray CLI port remains pool intent. The former `OBPI-0.31.0-07-mutate` brief was removed by the 2026-05-23 demotion and is not a current work order. The test audit proposes [ADR-pool.test-integrity-tooling](../design/adr/pool/ADR-pool.test-integrity-tooling.md), item TI-01, as its independently promotable home; no promotion or score floor is implied.
 - **Property-based testing is absent.** `hypothesis` would catch logic gaps in the kind of derivation code gzkit has (semver/lifecycle/REQ-ID resolution, ledger event derivation, ARB receipt parsing). The `unittest`-over-`pytest` decision in STDLIB-FIRST DOCTRINE is principled but eliminates one path to property testing without acknowledging the cost.
 - **Fuzz testing is absent.** Less critical for gzkit's surface but worth naming as a gap.
 - **Inferential sensors are deliberately suppressed but not replaced.** `quality-reviewer` and `spec-reviewer` exist as subagents but aren't part of any pipeline stage. The anti-vibing posture is principled, but the article's point is that LLM-judges are good for *fuzzy* dimensions where deterministic checks can't reach. Foregoing them entirely cedes coverage of architectural-smell, naming-quality, abstraction-leakage failure classes. The "Third confirming thesis" subsection below catalogs Every Inc.'s 20+ specialized reviewer agents as a concrete inventory of what an inferential-sensor expansion might look like in published practice.
@@ -54,7 +54,7 @@

 The article's framing is that **guides anticipate, sensors observe**. gzkit invests massively in both. If you read `AGENTS.md` and the rules together, the outer harness here is *very* thick — among the thickest I've seen. The cost is paid every turn; the payoff is real (the GHI ledger shows defects caught the surface previously missed). But until gzkit can show *which* guides are still load-bearing in the presence of the current validator surface, the contract is heavier than it has to be on at least one axis. That's the highest-leverage place to look — not adding more, but proving (or disproving) that some current guide is now reachable from sensors alone, then deleting it.

-The two concrete additions that emerged as highest-priority from this appraisal: **mutation testing as a `gz validate --mutation` scope** (closes the Invariant 6f gap mechanically) and **an in-session sensor sidecar** that streams `gz validate` deltas to the agent during edits. Both are on the [improvement plan](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md) — mutation testing in Wave 1 (already booked as `OBPI-0.31.0-07-mutate`), sidecar in Wave 2 (planned as `ADR-pool.harness-sidecar` but never drafted to disk — reconciled 2026-06-12; the Stop-hook turn-end sensor landed by **ADR-0.0.70** is the cheap down-payment whose block telemetry now funds that decision with evidence).
+The 2026-04-26 appraisal proposed general mutation tooling and an in-session sensor sidecar. Mutation tooling was demoted with its former package on 2026-05-23; the 2026-09-24 audit proposes pool item TI-01 in [ADR-pool.test-integrity-tooling](../design/adr/pool/ADR-pool.test-integrity-tooling.md), without assuming a validator scope or a score floor. The sidecar remains the separate Wave-2 topic in the [improvement plan](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md); the Stop-hook turn-end sensor landed under ADR-0.0.70 is its recorded down-payment.

 ## External Validation — Greyling on Claude Code (recursive case)

@@ -84,7 +84,7 @@

 ### What this triangulation does NOT change

-Greyling's analysis reinforces the existing Böckeler-derived improvement plan; it does not unlock new mechanical promotion candidates beyond what's already tracked in the advisory scorecard. The honest output of this triangulation is doctrinal clarity (the recursive framing) and external validation (two independent published theses converge), not new validator scopes. The Böckeler-identified concrete additions — mutation testing (Wave 1, `OBPI-0.31.0-07-mutate`) and in-session sensor sidecar (Wave 2, planned as `ADR-pool.harness-sidecar`, never drafted; see the 2026-06-12 reconciliation under § The Sharpest Tension) — remain the highest-priority structural moves; the Greyling axis adds an external second-opinion that they are correct, not a third item.
+Greyling's analysis reinforces the existing Böckeler-derived improvement plan; it does not unlock new mechanical promotion candidates beyond what's already tracked in the advisory scorecard. The honest output of this triangulation is doctrinal clarity (the recursive framing) and external validation (two independent published theses converge), not new validator scopes. The Böckeler-identified concrete additions — mutation tooling (historical Wave 1; proposed current home: ADR-pool.test-integrity-tooling, TI-01) and in-session sensor sidecar (Wave 2, planned as `ADR-pool.harness-sidecar`, never drafted; see the 2026-06-12 reconciliation under § The Sharpest Tension) — remain the highest-priority structural moves; the Greyling axis adds an external second-opinion that they are correct, not a third item.

 ### Third confirming thesis — Every Inc. "Compound Engineering" plugin

@@ -151,5 +151,5 @@
 - Compound Engineering source: <https://github.com/EveryInc/compound-engineering-plugin> and <https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents>
 - Buetow axis source: Beyond Coding Podcast (2026-06-10) + <https://cracking-ai-engineering.com>; adoption: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/`
 - Improvement plan handoff: [`.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md`](../../.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md)
-- Booked work: [`OBPI-0.31.0-07-mutate`](../design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/obpis/OBPI-0.31.0-07-mutate.md)
+- Proposed backlog home for general mutation tooling: [ADR-pool.test-integrity-tooling, TI-01](../design/adr/pool/ADR-pool.test-integrity-tooling.md); no active OBPI is booked.
 - Doctrine roots cited: `AGENTS.md` §§ MAKE LLM STOCHASTIC VIBES INERT, STDLIB-FIRST DOCTRINE, OPERATOR ECONOMY OF EFFORT, Attestation; `.claude/rules/tests.md` § Invariant 6f; `docs/governance/advisory-rules-audit.md`; `docs/governance/state-doctrine.md`
--- a/.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md
+++ b/.gzkit/handoffs/2026-04-26-harness-engineering-improvement-plan.md
@@ -22,6 +22,15 @@
      transcript on Martin Fowler's site. Operator confirmed all three
      waves; this artifact captures the design output for further
      action across multiple subsequent sessions. -->
+
+## Correction — 2026-09-24
+
+This is a dated 2026-04-26 account. `OBPI-0.31.0-07-mutate` and its
+probe TASK/lock/marker references below name the historical absorption package,
+which was demoted at `993a16c11` on 2026-05-23. The brief no longer exists;
+these references do not authorize a lock, pipeline, or implementation today.
+The test audit proposes ADR-pool.test-integrity-tooling, item TI-01, as the
+backlog home; SemVer 0.31.0 belongs to ADR-0.31.0-obpi-state-machine.

 ## Current State Summary

@@ -52,7 +61,7 @@

 | Item | Type | Status / Route |
 |---|---|---|
-| **F-5 / S-2** Drive `OBPI-0.31.0-07-mutate` to completion (port airlineops mutation testing → `gz mutate`) | Existing OBPI (heavy lane, status Pending) | Brief at `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/obpis/OBPI-0.31.0-07-mutate.md`. Source: `../airlineops/src/opsdev/commands/mutation_tools.py` (451 lines). Adaptation notes captured in the originating session's implementer dispatch (size caps, Pydantic models, ASCII-only console, exit codes 0/1/2/3, `--min-kill-rate FLOAT` for new policy-breach gate, mocked unit tests). |
+| **F-5 / S-2** General mutation tooling (historical Wave 1 proposal) | Pool intent; no current OBPI | The former brief was removed by the 2026-05-23 demotion; the 2026-09-24 audit proposes ADR-pool.test-integrity-tooling, TI-01. A future operator-authorized promotion must decide the tool and its diagnostic contract; no kill-rate gate is inherited from this dated dispatch. |
 | **S-6** Author `dependency-freshness-sweep` chore | New chore | Layout: `src/gzkit/chores/dependency-freshness-sweep/` (canonical) + `.gzkit/chores/dependency-freshness-sweep/` (project overlay) per ADR-0.0.21. Computational tier: parse `pyproject.toml` + `uv.lock`, fetch PyPI versions, emit age-in-days. Optional inferential tier: subagent flags deprecation/abandonment via web research. Cadence: monthly via `/schedule`. |
 | **B-6** Doctrine fold for `hypothesis` as named-future-departure | Small AGENTS.md edit | Extend `AGENTS.md § STDLIB-FIRST DOCTRINE § Existing canonical applications` to name `hypothesis` as a future named departure contingent on Wave 2's S-3 landing. Documents the property-testing tradeoff explicitly. |

@@ -118,7 +127,7 @@
 The next session resumes work on this plan via one of the following entry points (operator-routed):

 1. **Wave 1 — pick a starting item:**
-   - `OBPI-0.31.0-07-mutate` — re-claim lock, restart pipeline, dispatch implementer (full brief preserved in originating session transcript)
+   - General mutation tooling — consider the proposed ADR-pool.test-integrity-tooling, TI-01; do not resume the removed OBPI or claim its historical identifier.
    - `dependency-freshness-sweep` chore — author via `gz-chore-runner` skill
    - `hypothesis` doctrine fold — small AGENTS.md edit
 2. **Wave 2 — pick one pool ADR to draft first.** Recommendation: `ADR-pool.harness-sidecar` (highest-leverage gap from the article; unlocks several downstream invariants). Route: `/gz-design ADR-pool.harness-sidecar`.
@@ -129,7 +138,7 @@
 ## Outstanding Session Artifacts

 - Probe TASK in ledger: `TASK-0.31.0-07-01-01` (started + completed, harmless, used only to confirm TASK lifecycle is implicit)
-- OBPI lock for `OBPI-0.31.0-07-mutate`: released
-- Pipeline markers for `OBPI-0.31.0-07-mutate`: cleared via `gz obpi pipeline --clear-stale`
+- Historical 2026-04-26 lock record for `OBPI-0.31.0-07-mutate`: released then; not a current lock or work order.
+- Historical 2026-04-26 pipeline record for `OBPI-0.31.0-07-mutate`: cleared then; this account prescribes no current pipeline action.
 - No source files modified
 - No commits authored
```

## 10. Proposed scriptable gates

These are proposals for operator disposition, not enabled controls. Each CI check reads the checkout, uses tempfile locations outside it for processes and artifacts, writes results only to the CI artifact directory, and returns 0 for pass / 1 for fail. Missing or malformed evidence fails; it is never converted to an empty successful result. A generated review candidate is not itself a semantic defect verdict.

| Gate | Stdlib path first | Deterministic verdict | Dependency / authorization |
|---|---|---|---|
| Unit execution and exit provenance | subprocess.run without shell pipelines; require successful discovery and retain actual return code/test counts. | Fail on nonzero, missing summary, unexpected collection drop against reviewed manifest, or all-selected-tests skipped. | Existing unittest runner; no new runtime dependency. |
| REQ proof parity across every lane | Existing REQ parser and unittest discovery/result capture; resolve actual decorated tests and kind-specific channels. | Fail a BEHAVIOR REQ with no resolved test, failed covering test or zero executed non-skipped tests; retain SUPPORT/fence distinctions. | Corrective decision under existing REQ doctrine; no new dependency. |
| Witness sufficiency | json/hashlib plus subprocess/unittest against isolated current/base copies. | Fail when a required witness is none, baseline invalid, unrelated import/setup failure, or mismatched source/test identity; require designated behavior discriminator to fail. | Any broadening beyond currently scoped RED policy requires an explicit doctrine decision. |
| Waiver/baseline monotonicity | json and subprocess git show compare approved base and head; count each operation slot. | Fail unexplained new operation fingerprints, added waiver slots or raised limit; accept only a separately reviewed explicit authorization record tied to the delta. | No dependency. Must define renamed/moved-operation identity and authorized scope changes. |
| Constant/vacuous test regression | ast plus a small explicit catalog: literal unconditional true assertions; known empty-premise checks use targeted negative controls. | Fail newly introduced unconditional assertTrue(True) methods; for selected scanners require nonempty independent fixture expectations and rejected zero-result fault. | No dependency. Do not fail merely on assertIsInstance, absent assert spelling, or a conditional assertion. |
| Commit range provenance | subprocess git rev-list base..head and existing trailer parser. | Fail any relevant commit in the actual CI range missing its required trailer, rather than checking HEAD alone. | No dependency; range and shallow-history behavior must be specified. |
| Reviewed guard mutation canaries | Existing mutation_witness plus unittest, tempfile, subprocess and explicit exact substitutions. | Each canary must apply once, clean baseline must pass, designated assertion must fail, timeout/error/incompetent must fail the diagnostic. | No new dependency for bounded guards; bind diff/hash/REQ so changing a test cannot silently erase its canary. |
| General mutation diagnostic completeness | Prototype with ast/tokenize, sqlite3, subprocess and unittest; report all outcomes without global kill floor. | Fail missing jobs, failed baseline, wrong import origin or unclassified outcomes. A reviewed non-equivalent survivor triggers the pool’s promotion-discussion predicate; raw survivor percentage alone does not fail quality. | Cosmic Ray option requires operator-promoted successor of ADR-pool.test-integrity-tooling and an explicit Stdlib-First dependency decision. Pool proposal itself grants no dependency authorization. |
| Coverage measurement integrity | stdlib trace can inventory executed lines, but does not supply equivalent branch measurement; use existing locked coverage.py if adopted for the CI contract. | Require passing unit run, fresh measured data and explicit child-process policy. Enforce the existing authored line-floor policy only after deciding its CI binding; propose no new branch or mutation score floor here. | Existing test dependency, no addition; CI binding and coverage exemptions require recorded policy. |
| Pool references and identity | pathlib, re, json and current registered artifact IDs. | Fail active-work references to absent briefs and reserved pool semver collisions; allow explicitly dated historical accounts. | No dependency; distinguish historical citations from current bookings. |

## 11. Not examined and inference limits

The audit did not manually read every test in the suite or prove every reviewed test effective. The random sample supports only its stated observed defect rate. D1/D2/D6 semantic detection is not exhausted by syntax; imported assertion helpers remain candidates. No issue was filed and no insight/ledger event was written because the audit explicitly forbids those writes; findings are tracked in this report for operator disposition.

The pilot did not mutate every fail-closed validator or the complete completion command. It selected the five requested engines, requirement parity and two additional validator scopes. In particular, commands/obpi_complete.py, commands/arb.py, commands/validate_cmd.py, governance/waiver_ratchet.py, schema/model validation, the remaining trust audits and hooks were traced where relevant but not all mutation-tested. The complete registered validation-scope complement is listed below; breadth was bounded so every selected target could receive a clean baseline, full generated run and per-mutant evidence. Omitted is not passed.

| Registered scope not directly mutation-targeted | Registration receipt | Tier |
|---|---|---|
| manifest | [src/gzkit/commands/validate_cmd.py:150](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:150) | default |
| surfaces | [src/gzkit/commands/validate_cmd.py:156](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:156) | default |
| ledger | [src/gzkit/commands/validate_cmd.py:157](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:157) | default |
| instructions | [src/gzkit/commands/validate_cmd.py:163](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:163) | default |
| briefs | [src/gzkit/commands/validate_cmd.py:164](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:164) | default |
| documents | [src/gzkit/commands/validate_cmd.py:165](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:165) | default |
| personas | [src/gzkit/commands/validate_cmd.py:166](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:166) | default |
| frontmatter | [src/gzkit/commands/validate_cmd.py:167](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:167) | default |
| version | [src/gzkit/commands/validate_cmd.py:173](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:173) | default |
| taxonomy | [src/gzkit/commands/validate_cmd.py:174](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:174) | default |
| invariant_coherence | [src/gzkit/commands/validate_cmd.py:175](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:175) | default |
| interviews | [src/gzkit/commands/validate_cmd.py:178](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:178) | explicit |
| decomposition | [src/gzkit/commands/validate_cmd.py:179](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:179) | explicit |
| requirements | [src/gzkit/commands/validate_cmd.py:180](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:180) | explicit |
| type_ignores | [src/gzkit/commands/validate_cmd.py:194](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:194) | explicit |
| cli_alignment | [src/gzkit/commands/validate_cmd.py:195](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:195) | explicit |
| event_handlers | [src/gzkit/commands/validate_cmd.py:205](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:205) | explicit |
| event_schemas | [src/gzkit/commands/validate_cmd.py:206](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:206) | explicit |
| producer_fields | [src/gzkit/commands/validate_cmd.py:207](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:207) | explicit |
| validator_fields | [src/gzkit/commands/validate_cmd.py:208](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:208) | explicit |
| authorship | [src/gzkit/commands/validate_cmd.py:211](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:211) | explicit |
| python_version_pins | [src/gzkit/commands/validate_cmd.py:214](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:214) | explicit |
| utf8_prefix | [src/gzkit/commands/validate_cmd.py:220](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:220) | explicit |
| line_endings | [src/gzkit/commands/validate_cmd.py:221](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:221) | explicit |
| test_tiers | [src/gzkit/commands/validate_cmd.py:222](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:222) | explicit |
| pydantic_models | [src/gzkit/commands/validate_cmd.py:223](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:223) | explicit |
| class_size | [src/gzkit/commands/validate_cmd.py:224](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:224) | explicit |
| version_release | [src/gzkit/commands/validate_cmd.py:225](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:225) | explicit |
| pool_adr_isolation | [src/gzkit/commands/validate_cmd.py:226](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:226) | explicit |
| pool_interview | [src/gzkit/commands/validate_cmd.py:229](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:229) | explicit |
| behave_req_tags | [src/gzkit/commands/validate_cmd.py:232](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:232) | explicit |
| skill_alignment | [src/gzkit/commands/validate_cmd.py:233](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:233) | explicit |
| advisory_scorecard | [src/gzkit/commands/validate_cmd.py:234](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:234) | explicit |
| complexity_doctrine_links | [src/gzkit/commands/validate_cmd.py:237](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:237) | explicit |
| complexity_thresholds | [src/gzkit/commands/validate_cmd.py:243](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:243) | explicit |
| reconcile_freshness | [src/gzkit/commands/validate_cmd.py:249](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:249) | explicit |
| insights_shape | [src/gzkit/commands/validate_cmd.py:252](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:252) | explicit |
| instructions_files_budget | [src/gzkit/commands/validate_cmd.py:253](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:253) | explicit |
| agents_md_map_conformance | [src/gzkit/commands/validate_cmd.py:272](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:272) | explicit |
| adr_status_fresh | [src/gzkit/commands/validate_cmd.py:278](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:278) | explicit |
| obpi_lifecycle_coherence | [src/gzkit/commands/validate_cmd.py:281](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:281) | explicit |
| adversarial_validation | [src/gzkit/commands/validate_cmd.py:287](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:287) | explicit |
| session_green_gate | [src/gzkit/commands/validate_cmd.py:294](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:294) | explicit |
| orientation_freshness | [src/gzkit/commands/validate_cmd.py:300](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:300) | explicit |
| brief_headings | [src/gzkit/commands/validate_cmd.py:306](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:306) | explicit |
| brief_cross_references | [src/gzkit/commands/validate_cmd.py:307](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:307) | explicit |
| brief_demo_section | [src/gzkit/commands/validate_cmd.py:313](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:313) | explicit |
| chores_layout | [src/gzkit/commands/validate_cmd.py:316](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:316) | explicit |
| unscoped_rules | [src/gzkit/commands/validate_cmd.py:317](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:317) | explicit |
| rule_version_markers | [src/gzkit/commands/validate_cmd.py:318](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:318) | default |
| invariant_witness | [src/gzkit/commands/validate_cmd.py:321](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:321) | default |
| sensitivity | [src/gzkit/commands/validate_cmd.py:322](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:322) | explicit |
| doc_surface_parity | [src/gzkit/commands/validate_cmd.py:323](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:323) | explicit |
| absorption_duplicates | [src/gzkit/commands/validate_cmd.py:326](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:326) | explicit |
| orphaned_implementation | [src/gzkit/commands/validate_cmd.py:332](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:332) | explicit |
| evaluation_justify_binding | [src/gzkit/commands/validate_cmd.py:338](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:338) | explicit |
| qc_binding | [src/gzkit/commands/validate_cmd.py:352](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:352) | explicit |
| fidelity_presence | [src/gzkit/commands/validate_cmd.py:353](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:353) | explicit |
| waiver_ratchet | [src/gzkit/commands/validate_cmd.py:356](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:356) | explicit |
| config_registry | [src/gzkit/commands/validate_cmd.py:357](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:357) | explicit |
| gate_callers | [src/gzkit/commands/validate_cmd.py:358](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:358) | explicit |
| exemption_controls | [src/gzkit/commands/validate_cmd.py:359](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:359) | explicit |
| population_controls | [src/gzkit/commands/validate_cmd.py:362](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:362) | explicit |
| intrinsic_attestation | [src/gzkit/commands/validate_cmd.py:365](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:365) | explicit |
| advisor_proof_binding | [src/gzkit/commands/validate_cmd.py:371](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:371) | explicit |
| lock_exchange_coupling | [src/gzkit/commands/validate_cmd.py:377](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:377) | explicit |
| distribution | [src/gzkit/commands/validate_cmd.py:383](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:383) | explicit |
| wheel_path_literals | [src/gzkit/commands/validate_cmd.py:384](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:384) | default |
| changelog | [src/gzkit/commands/validate_cmd.py:390](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:390) | explicit |
| bullet_retention | [src/gzkit/commands/validate_cmd.py:391](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:391) | explicit |
| surface_weight | [src/gzkit/commands/validate_cmd.py:394](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:394) | explicit |
| pointer_anchors | [src/gzkit/commands/validate_cmd.py:395](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:395) | explicit |
| surface_fidelity | [src/gzkit/commands/validate_cmd.py:398](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:398) | explicit |
| vendor_manifest | [src/gzkit/commands/validate_cmd.py:401](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:401) | explicit |
| setpoint_coherence | [src/gzkit/commands/validate_cmd.py:404](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:404) | explicit |
| rendition_freshness | [src/gzkit/commands/validate_cmd.py:407](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:407) | explicit |
| rendition_floor_coherence | [src/gzkit/commands/validate_cmd.py:410](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:410) | explicit |
| rendition_lineage | [src/gzkit/commands/validate_cmd.py:416](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:416) | explicit |
| corpus_retirement_witness | [src/gzkit/commands/validate_cmd.py:422](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:422) | default |
| doc_code_citations | [src/gzkit/commands/validate_cmd.py:428](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:428) | default |
| kind_invariance | [src/gzkit/commands/validate_cmd.py:434](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:434) | explicit |
| persona_witness | [src/gzkit/commands/validate_cmd.py:435](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:435) | explicit |
| receipt_shape | [src/gzkit/commands/validate_cmd.py:436](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:436) | explicit |
| brief_reconcile | [src/gzkit/commands/validate_cmd.py:437](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:437) | explicit |
| brief_structure | [src/gzkit/commands/validate_cmd.py:440](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:440) | explicit |
| router_tables | [src/gzkit/commands/validate_cmd.py:443](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:443) | explicit |
| req_kind_discipline | [src/gzkit/commands/validate_cmd.py:444](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:444) | explicit |
| status_writer_coverage | [src/gzkit/commands/validate_cmd.py:447](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:447) | explicit |
| transcribed_adr_counts | [src/gzkit/commands/validate_cmd.py:453](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:453) | explicit |
| ontology_purity | [src/gzkit/commands/validate_cmd.py:459](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:459) | explicit |
| brief_command_shape | [src/gzkit/commands/validate_cmd.py:460](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:460) | explicit |
| task_envelope_coherence | [src/gzkit/commands/validate_cmd.py:469](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:469) | explicit |
| closeout_proof | [src/gzkit/commands/validate_cmd.py:475](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:475) | explicit |
| okf_conformance | [src/gzkit/commands/validate_cmd.py:476](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:476) | explicit |
| deprecated_verb_prescription | [src/gzkit/commands/validate_cmd.py:477](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/validate_cmd.py:477) | explicit |

Most survivors were not independently proven non-equivalent. Timeout cases were not automatically called killed. Mutation results apply to each recorded selected test command; other suite tests may detect those faults. No statement of arbitrary test deletion safety follows from zero observed kills. The attempted independent full-suite replay stopped on its clean-baseline timeout before either substitution. No historical within-commit authoring order was reconstructed; the full-history diff scan does not semantically adjudicate every change. No hosted CI job, bypass permissions, branch protection or global machine Python environments were audited. No BDD mutation pilot ran; unit/BDD line overlap is not used as a redundancy argument.

## Appendix A. Exact pilot commands, baselines, timeouts and receipts

### covers

```toml
[cosmic-ray]
module-path = "src/gzkit/commands/covers.py"
timeout = 30.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.governance.test_req_coverage_record tests.test_adr_governance_confirm tests.test_req_kind_fence_channel tests.test_req_kind_grandfathering_cache tests.test_traceability"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/covers/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/covers/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.99
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/covers/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/covers/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.38
  }
}
```

### mutation_witness

```toml
[cosmic-ray]
module-path = "src/gzkit/mutation_witness.py"
timeout = 58.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.test_acceptance_execution tests.test_mutation_witness"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 9.702
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.429
  }
}
```

### red_parity

```toml
[cosmic-ray]
module-path = "src/gzkit/governance/trust_audits/red_parity.py"
timeout = 180.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.test_ledger_corrections tests.test_red_parity_audit"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_parity/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_parity/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 2.159
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_parity/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_parity/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.34
  }
}
```

### red_witness

```toml
[cosmic-ray]
module-path = "src/gzkit/red_witness.py"
timeout = 37.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.arb.test_red_witness_void_experiment tests.arb.test_writer_validator_lockstep tests.test_red_witness"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_witness/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_witness/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 6.089
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_witness/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/red_witness/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.409
  }
}
```

### req_coverage

```toml
[cosmic-ray]
module-path = "src/gzkit/governance/req_coverage.py"
timeout = 30.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.commands.test_obpi_complete_behave_coverage tests.commands.test_obpi_complete_coverage_kind_aware tests.governance.test_covers_kind_coherence tests.governance.test_req_coverage tests.governance.test_req_kind_tag_emphasis"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 2.302
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.3
  }
}
```

### tautological_tests

```toml
[cosmic-ray]
module-path = "src/gzkit/tautological_tests.py"
timeout = 30.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.governance.test_shipped_executable_fence tests.governance.test_tautological_tests tests.governance.test_wall_clock_fixtures_audit"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.961
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.521
  }
}
```

### test_shape

```toml
[cosmic-ray]
module-path = "src/gzkit/test_shape.py"
timeout = 30.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.test_test_shape"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/test_shape/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/test_shape/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.786
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/test_shape/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/test_shape/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.337
  }
}
```

### validate_commit_trailers

```toml
[cosmic-ray]
module-path = "src/gzkit/commands/validate_commit_trailers.py"
timeout = 180.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.commands.test_validate_cmds tests.governance.test_commit_trailers_is_gated tests.governance.test_eval_feedback_trailer"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 2.639
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.33
  }
}
```

### verifier_pipe_gate

```toml
[cosmic-ray]
module-path = "src/gzkit/verifier_pipe_gate.py"
timeout = 30.0
excluded-modules = []
test-command = "uv run --no-project --python /private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python python -m unittest -v tests.arb.test_canonical_steps_leaf_import tests.hooks.test_verifier_pipe_gate"

[cosmic-ray.distributor]
name = "local"
```

```text
{
  "baseline": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "--verbosity",
      "INFO",
      "baseline",
      "/private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/config.toml",
      "--session-file",
      "/private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/baseline.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 1.629
  },
  "init": {
    "command": [
      "uv",
      "run",
      "--no-project",
      "--python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/python",
      "/private/tmp/gzkit-test-audit-20260924/pilot-env/bin/cosmic-ray",
      "init",
      "/private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/config.toml",
      "/private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/session.sqlite"
    ],
    "exit_status": 0,
    "elapsed_seconds": 0.605
  }
}
```

Execution used `cosmic-ray exec <config.toml> <session.sqlite>` and retained every outcome in SQLite. Completed original jobs were retained when the original parallel controller was interrupted; only pending jobs were resumed, each in a fresh checked clone. The following shard command outputs establish successful completion:

| Shard | Jobs | Baseline exit | Execution exit | Baseline seconds | Execution seconds |
|---|---|---|---|---|---|
| mutation_witness-0 | 74 | 0 | 0 | 17.46 | 1113.494 |
| mutation_witness-1 | 74 | 0 | 0 | 17.577 | 1102.072 |
| mutation_witness-2 | 74 | 0 | 0 | 17.741 | 1095.098 |
| mutation_witness-3 | 73 | 0 | 0 | 18.01 | 1094.106 |
| red_witness-0 | 75 | 0 | 0 | 11.403 | 823.873 |
| red_witness-1 | 75 | 0 | 0 | 11.472 | 827.139 |
| red_witness-2 | 74 | 0 | 0 | 11.247 | 807.177 |
| red_witness-3 | 74 | 0 | 0 | 11.181 | 795.825 |
| covers-0 | 58 | 0 | 0 | 2.321 | 87.812 |
| red_parity-0 | 164 | 0 | 0 | 5.903 | 896.743 |
| tautological_tests-0 | 88 | 0 | 0 | 1.743 | 125.12 |
| tautological_tests-1 | 88 | 0 | 0 | 1.749 | 254.664 |
| validate_commit_trailers-0 | 59 | 0 | 0 | 5.071 | 275.827 |
| verifier_pipe_gate-0 | 306 | 0 | 0 | 1.657 | 306.697 |
| verifier_pipe_gate-1 | 306 | 0 | 0 | 1.371 | 239.817 |

```text
$ uv run --no-project --python <audit-interpreter> python summarize_pilot.py
{
  "total": {
    "total": 3034,
    "completed": 3034,
    "killed": 1635,
    "survived": 1393,
    "assertion_only_kills": 787,
    "non_assertion_only_exits": 848,
    "timed_out": 4,
    "incompetent": 2
  },
  "selected_tests": 600,
  "without_assertion_kill": 344,
  "without_any_detection": 323
}
```

```json
{
  "mutants": 3034,
  "unique_job_ids": 3034,
  "pending": 0,
  "baseline_modules_passed": [
    "covers",
    "mutation_witness",
    "red_parity",
    "red_witness",
    "req_coverage",
    "tautological_tests",
    "test_shape",
    "validate_commit_trailers",
    "verifier_pipe_gate"
  ],
  "shards": 15,
  "all_shard_baselines_passed": true,
  "all_shard_exec_commands_exit_zero": true,
  "per_test_baseline_population": 600,
  "sum_all_outcomes": 3034
}
```

### Independent final mutation harness review

Observed 2026-09-24T08:04:50.442535+00:00; pinned commit `5d9885a08c438b0aa546716b20a181c55342612e`.

Independent read-only checks confirmed **3,034 unique jobs**, zero duplicate specs, zero pending jobs, and **600 baseline and attributed test IDs**. All 15 shard baselines and executions exited 0; every shard result matches its parent result exactly. All 24 cloned target source files match HEAD, all clone HEADs match the audit pin, and no `.pyc` files were present. The nine observed pilot import origins resolve to their own clone's `src` paths.

| Result | Count |
|---|---|
| Killed exits | 1635 |
| Assertion-only killed exits | 787 |
| Other killed exits | 848 |
| Survived | 1393 |
| Incompetent / mutation-application errors | 2 |
| Timed out | 4 |

The revised parser intersects FAIL/ERROR IDs with each target’s baseline IDs and reads the last complete outer runner summary. The nested-output regression now retains its two foreign fixture IDs only as diagnostics; neither enters the 600-test population. Its final `failures=2` summary is correctly classified as assertion-only.

Annotation census against the identical results snapshot: 825 survivors overlap postponed annotations; 568 survivors fall outside annotations. Eleven postponed-annotation mutants and eleven non-postponed-annotation mutants were killed. This is overlap evidence, not a declaration of equivalence.

Both incompetent jobs are Cosmic Ray `ExceptionReplacer` application failures on qualified exception types at `validate_commit_trailers.py:47` and `:139`; tests were not run for them.

Limits: the 600 tests form a purposive target selection. Assertion-only describes runner evidence rather than semantic test adequacy. Per-test assertion credit can include mixed failure/error runs. Timeout and tool-error outcomes are separate. Coverage does not automatically capture arbitrary CLI subprocesses. Import probes verify current resolution, not every historical subprocess import.

Receipts: `final_harness_review.json`, `harness_review.json`, `pilot_outcome_diagnostics.json`, and `annotation_overlap.json` in this directory. All checks: {'all3034_unique': True, 'none_pending': True, 'test_population_exact600': True, 'attribution_in_baseline': True, 'all_shards_green_complete_exactly_merged': True, 'all_target_sources_restored': True, 'all_clone_heads_pinned': True, 'no_pycache': True, 'same_annotation_snapshot': True, 'nested_pseudoids_excluded': True}.

Canonical ARB receipt: `arb-step-unittest-0c611c24cac541fa809066856795e6a7.json`; SHA-256 `c597b65cd63e660c8dabd0e96a9d828511f21140862062d539418a876a401660`.

```json
{
  "duration_ms": 157056,
  "exit_status": 0,
  "git": {
    "branch": "main",
    "commit": "5d9885a08c438b0aa546716b20a181c55342612e",
    "dirty": false
  },
  "run_id": "arb-step-unittest-0c611c24cac541fa809066856795e6a7",
  "schema": "gzkit.arb.step_receipt.v1",
  "stderr_tail": "----------------------------------------------------------------------\nRan 10747 tests in 145.450s\n\nOK (skipped=4)",
  "stderr_truncated": true,
  "stdout_tail": "",
  "stdout_truncated": false,
  "step": {
    "command": [
      "uv",
      "run",
      "unittest-parallel",
      "-t",
      ".",
      "-s",
      "tests",
      "--buffer"
    ],
    "name": "unittest"
  },
  "timestamp_utc": "2026-09-24T07:43:42Z"
}
```

### Evidence inventory

| Scratch evidence | Bytes | SHA-256 |
|---|---|---|
| /private/tmp/gzkit-test-audit-20260924/pilot/covers/session.sqlite | 6463488 | e40976c6c51125d46ec25c02bc718fa03def91401b9d8a9fed8735de2eee05c2 |
| /private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/session.sqlite | 6709248 | d76381e5f2e5e34f2b48c09dab9ea5a356349428d1e42626a0423716fee72b04 |
| /private/tmp/gzkit-test-audit-20260924/pilot/red_parity/session.sqlite | 5668864 | 87da5c4e352172358ab4d6df997407c44f444af3ab2a1e2522058e24d56620a2 |
| /private/tmp/gzkit-test-audit-20260924/pilot/red_witness/session.sqlite | 4669440 | 1dadb513639e0f112291339eaff89b7c103e301623b04b3d9b9f22ebce4496bf |
| /private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/session.sqlite | 335872 | f40c583f79870981cd6c153c4e686e93588b145b0ae7d66080b18d8d5cf85d13 |
| /private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/session.sqlite | 9883648 | b48844009500ba54f1b585ccffb21cf3aaf652d0e60117c5682348035a489c1b |
| /private/tmp/gzkit-test-audit-20260924/pilot/test_shape/session.sqlite | 839680 | 24ca6287eba6f47babd7004d1db9532509d481ddfd0c40168cae2fbcf6bba8e9 |
| /private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/session.sqlite | 700416 | 8903d4e405cf2c86d1c3ded2aad098b3255dfa5e54e29cf6c76d325bed626d1f |
| /private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/session.sqlite | 53399552 | 2af625993b8dac7371f932839a7f1f4d799426c2c1f800bd777f1df7be73777b |
| /private/tmp/gzkit-test-audit-20260924/branch-coverage.json | 5158389 | fc329866f261a0b23e63617f048311627190d77d71750cfe155c902e04935ab6 |
| /private/tmp/gzkit-test-audit-20260924/manual/manifest.json | 360131 | 07dcf19f6f37f317e1e4ac170c4add3fe732b6cf96a8cd66891cf956437a7167 |
| /private/tmp/gzkit-test-audit-20260924/controls/counts.json | 973 | 2ab4c0cd8b6b578d1b73b9a6c9816c04508f3b25af0ee099170a3b8284788f5a |
| /private/tmp/gzkit-test-audit-20260924/controls/extended_counts.json | 8398 | f69540cdb76b6b989bc68db236de3a633f6a709723c221de78f64b65296978ec |
| /private/tmp/gzkit-test-audit-20260924/history/process-data.json | 185739 | 303b1f69945ae12e0e487421c3549bb0c6ffd17e10904eaf4211fb6ad5cd4578 |
| /private/tmp/gzkit-test-audit-20260924/history/pool-proposal-final.diff | 31813 | aae9990aace4f2f73d8cc318abbb19791e6919de77d434dadc1df4956ecd1907 |

The scratch repository copies are deleted after the pilot and final verification; source references remain resolvable with git show at the pinned commit. Databases/logs/scripts are execution evidence outside the repository, not separate report deliverables. Essential counts, outcomes, survivor identities and source receipts are included in this single report.

```json
{
  "command": "uv run --no-project --python <scratch-pilot-interpreter> python cleanup_copies.py",
  "completed_at_utc": "2026-09-24T08:06:40.855893+00:00",
  "pinned_repository_copies_deleted": 25,
  "deleted_copies": [
    "/private/tmp/gzkit-test-audit-20260924/pilot/covers/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/mutation_witness/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/red_parity/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/red_witness/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/req_coverage/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/tautological_tests/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/test_shape/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/validate_commit_trailers/repo",
    "/private/tmp/gzkit-test-audit-20260924/pilot/verifier_pipe_gate/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/covers-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/mutation_witness-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/mutation_witness-1/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/mutation_witness-2/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/mutation_witness-3/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/red_parity-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/red_witness-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/red_witness-1/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/red_witness-2/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/red_witness-3/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/tautological_tests-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/tautological_tests-1/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/validate_commit_trailers-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/verifier_pipe_gate-0/repo",
    "/private/tmp/gzkit-test-audit-20260924/shards/verifier_pipe_gate-1/repo",
    "/private/tmp/gzkit-test-audit-20260924/baseline"
  ],
  "remaining_requested_copy_paths": [],
  "evidence_databases_logs_and_scripts_retained_outside_repository": true,
  "full_suite_followup_copy": "separately deleted; full-survivor-check/cleanup.log"
}
```

## Appendix B. Every file without an actual @covers decorator

# AST covers inventory and full file-purpose classification

Pinned commit: `5d9885a08c438b0aa546716b20a181c55342612e`. This expands the earlier raw-token-free inventory; it does not replace supported comment/docstring annotations with a decorator-only rule.

| Measure | Count |
|---|---|
| Test-pattern files | 675 |
| Exact raw `@covers(` literals / files | 4718 / 350 |
| Files containing raw `@covers` token | 397 |
| Actual AST decorator expressions / files | 4613 / 342 |
| Files with no actual AST decorator | 333 |
| Of these, source hits accepted by canonical REQ-reference scanner | 27 (25 outside fixture paths) |
| Files with neither actual decorator nor canonical scanner hit | 306 |

`src/gzkit/traceability.py:50` explicitly supports comment/docstring forms and masks ordinary fixture strings. Therefore, "no decorator" is not "unannotated". AST nested-fixture decorators are also syntax, not established discovered test bindings. The full JSON preserves owner/nesting, token location channels, source receipts, and scanner hits.

15 files define local `covers` functions and contain 483 decorator expressions; these remain real decorators. For example, `tests/governance/test_lock_exchange_coupling_validator.py:23` explicitly explains its local identity decorator and syntax-based proof scanning. No runtime registration inference is made.

The fifth category, behavioral test, is necessary: ordinary regression tests can have a clear behavioral purpose without a REQ decorator. Categories are primary-purpose triage, not formal REQ-kind assignment or per-test strength judgments. Missing annotations alone are not defects.

| Primary purpose | Files |
|---|---|
| SUPPORT proof | 11 |
| behavioral test | 272 |
| output-form fixture | 14 |
| structural fence | 36 |

| File | Primary purpose | Declared subject / source receipt |
|---|---|---|
| `tests/adr/test_patch_release.py` | behavioral test | Tests for gz patch release: GHI discovery, cross-validation, version sync, and manifests.; `tests/adr/test_patch_release.py:34` |
| `tests/adr/test_state_doctrine.py` | behavioral test | Tests for gz state --repair (OBPI-0.0.9-03: State Repair Command).; `tests/adr/test_state_doctrine.py:29` |
| `tests/adr/test_storage_tiers.py` | structural fence | Storage tier verification for ADR-0.0.10.; `tests/adr/test_storage_tiers.py:50` |
| `tests/arb/test_advisor.py` | behavioral test | Tests for gzkit.arb.advisor.; `tests/arb/test_advisor.py:34` |
| `tests/arb/test_arb_archive.py` | behavioral test | ARB receipt retention — move-not-delete archive semantics (GHI #594).; `tests/arb/test_arb_archive.py:58` |
| `tests/arb/test_canonical_steps_leaf_import.py` | behavioral test | ``CANONICAL_STEP_COMMANDS`` must be reachable without the ARB validator chain.; `tests/arb/test_canonical_steps_leaf_import.py:36` |
| `tests/arb/test_coverage_runner_lockstep.py` | behavioral test | The full-suite coverage run uses the parallel runner, spelled once (GHI #1027).; `tests/arb/test_coverage_runner_lockstep.py:61` |
| `tests/arb/test_paths.py` | behavioral test | Tests for gzkit.arb.paths.; `tests/arb/test_paths.py:15` |
| `tests/arb/test_patterns.py` | behavioral test | Tests for gzkit.arb.patterns.; `tests/arb/test_patterns.py:28` |
| `tests/arb/test_red_witness_void_experiment.py` | behavioral test | The RED witness must not report a verdict when its experiment never ran (GHI #839).; `tests/arb/test_red_witness_void_experiment.py:80` |
| `tests/arb/test_ruff_reporter.py` | behavioral test | Tests for gzkit.arb.ruff_reporter.; `tests/arb/test_ruff_reporter.py:68` |
| `tests/arb/test_schemas.py` | structural fence | Tests for ARB receipt JSON schemas.; `tests/arb/test_schemas.py:21` |
| `tests/arb/test_step_output_cli.py` | output-form fixture | GHI #987: retain review output through the real ARB CLI and persisted receipt.; `tests/arb/test_step_output_cli.py:65` |
| `tests/arb/test_step_reporter.py` | behavioral test | Tests for gzkit.arb.step_reporter.; `tests/arb/test_step_reporter.py:57` |
| `tests/arb/test_typecheck_scope_lockstep.py` | behavioral test | The typecheck scope is one value, not four agreeing copies (GHI #199 class).; `tests/arb/test_typecheck_scope_lockstep.py:52` |
| `tests/arb/test_unittest_runner_lockstep.py` | behavioral test | The unit-test invocation is one value, not three agreeing copies (GHI #856).; `tests/arb/test_unittest_runner_lockstep.py:76` |
| `tests/arb/test_validator.py` | behavioral test | Tests for gzkit.arb.validator.; `tests/arb/test_validator.py:55` |
| `tests/arb/test_validator_provenance.py` | behavioral test | Tests for ARB receipt provenance checking (GHI #199 follow-up).; `tests/arb/test_validator_provenance.py:59` |
| `tests/arb/test_writer_validator_lockstep.py` | behavioral test | Every ARB receipt gzkit writes must validate under ``gz arb validate`` (GHI #1026).; `tests/arb/test_writer_validator_lockstep.py:58` |
| `tests/chores/test_failure_class_index.py` | behavioral test | Tests for the failure-class index (chore: failure-class-index).; `tests/chores/test_failure_class_index.py:48` |
| `tests/chores/test_ledger_vocabulary_inertness.py` | behavioral test | The never-fired disclosure is a shrink-ratchet, and the code must say so (GHI #611).; `tests/chores/test_ledger_vocabulary_inertness.py:105` |
| `tests/chores/test_module_size_ratchet.py` | behavioral test | Ratchet-direction tests for the module-size gate (GHI #853).; `tests/chores/test_module_size_ratchet.py:58` |
| `tests/chores/test_repo_content_walks.py` | behavioral test | Repo-content scanners read git's file list, never the raw filesystem (GHI #902).; `tests/chores/test_repo_content_walks.py:83` |
| `tests/cli/test_color_env.py` | output-form fixture | Color-decision env semantics honor NO_COLOR / FORCE_COLOR conventions.; `tests/cli/test_color_env.py:29` |
| `tests/cli/test_error_boundary_markup.py` | output-form fixture | The CLI error boundary prints a GzkitError's message as text, never as markup.; `tests/cli/test_error_boundary_markup.py:32` |
| `tests/cli/test_errors_reach_stderr.py` | output-form fixture | The entrypoint reports a failed command on stderr, never stdout (cli-standards-v3.md).; `tests/cli/test_errors_reach_stderr.py:46` |
| `tests/cli/test_exit_code_claims.py` | behavioral test | Negative control for `.gzkit/rules/cli.md` § Exit Codes code 2 (GHI #1001).; `tests/cli/test_exit_code_claims.py:30` |
| `tests/cli/test_handler_manifest_resolves.py` | structural fence | Resolution guard for the lazy CLI handler manifests (GHI #617).; `tests/cli/test_handler_manifest_resolves.py:90` |
| `tests/cli/test_help_path_imports.py` | structural fence | Import-cost guard for the ``gz --help`` path (GHI #180).; `tests/cli/test_help_path_imports.py:129` |
| `tests/cli/test_json_stdout_log_isolation.py` | output-form fixture | `--json` stdout carries only JSON; logs go to stderr (GHI #1010).; `tests/cli/test_json_stdout_log_isolation.py:54` |
| `tests/cli/test_log_level_claims.py` | behavioral test | Negative control for `.gzkit/rules/cli.md` § Flag Conventions verbosity rows.; `tests/cli/test_log_level_claims.py:45` |
| `tests/cli/test_smoke_tier.py` | behavioral test | Build-verification members of the smoke/BVT tier (GHI #724).; `tests/cli/test_smoke_tier.py:39` |
| `tests/cli/test_validate_dispatch_consistency.py` | structural fence | Consistency fence over the `gz validate` dispatch surfaces (#618).; `tests/cli/test_validate_dispatch_consistency.py:72` |
| `tests/cli/test_validate_registry_parity.py` | structural fence | Per-cut parity proof for the ``VALIDATOR_REGISTRY`` collapse (#618, step 2).; `tests/cli/test_validate_registry_parity.py:320` |
| `tests/cli/test_validate_solo_scope_refusal.py` | behavioral test | Solo-only validate scopes refuse combination instead of silently dropping.; `tests/cli/test_validate_solo_scope_refusal.py:79` |
| `tests/commands/test_adr_audit_covers_scope.py` | behavioral test | Covers-location collection excludes withdrawn OBPIs (GHI #695).; `tests/commands/test_adr_audit_covers_scope.py:27` |
| `tests/commands/test_adr_demote.py` | behavioral test | Unit tests for ``gz adr demote`` — the inverse of ``gz adr promote``.; `tests/commands/test_adr_demote.py:90` |
| `tests/commands/test_adr_demote_parks_obpis.py` | behavioral test | Demotion must transact over its child OBPIs (GHI #584).; `tests/commands/test_adr_demote_parks_obpis.py:50` |
| `tests/commands/test_adr_promote.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_adr_promote.py:56` |
| `tests/commands/test_adr_resolution.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_adr_resolution.py:12` |
| `tests/commands/test_arb_cmd.py` | behavioral test | Tests for gzkit.commands.arb dispatchers.; `tests/commands/test_arb_cmd.py:50` |
| `tests/commands/test_attest.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_attest.py:17` |
| `tests/commands/test_audit.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_audit.py:272` |
| `tests/commands/test_check_advisory_rendering.py` | output-form fixture | Behavior tests for advisory-line rendering in the `gz check` aggregator (GHI #713).; `tests/commands/test_check_advisory_rendering.py:47` |
| `tests/commands/test_check_diagnostics.py` | behavioral test | Regression test: `gz check` must surface a failing step's captured output.; `tests/commands/test_check_diagnostics.py:25` |
| `tests/commands/test_chores_declaration.py` | behavioral test | Chore class declaration in the registry (GHI #999).; `tests/commands/test_chores_declaration.py:66` |
| `tests/commands/test_chores_staleness.py` | behavioral test | Staleness bands for `gz chores status` (GHI #936).; `tests/commands/test_chores_staleness.py:85` |
| `tests/commands/test_chores_status.py` | behavioral test | `gz chores status` — the chore staleness indicator (GHI #936).; `tests/commands/test_chores_status.py:84` |
| `tests/commands/test_cli_audit.py` | behavioral test | Tests for CLI audit command with cross-coverage integration.; `tests/commands/test_cli_audit.py:46` |
| `tests/commands/test_common_fixtures.py` | behavioral test | Contract tests for the shared test-fixture helpers in ``tests.commands.common``.; `tests/commands/test_common_fixtures.py:50` |
| `tests/commands/test_constitute.py` | behavioral test | Tests for ``gz constitute`` — scaffolder must round-trip through validator.; `tests/commands/test_constitute.py:20` |
| `tests/commands/test_content_reconcile_retirements.py` | behavioral test | gz content reconcile-retirements tests — Layer-2 repair for orphaned tombstones.; `tests/commands/test_content_reconcile_retirements.py:62` |
| `tests/commands/test_dry_run.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_dry_run.py:15` |
| `tests/commands/test_gates.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_gates.py:11` |
| `tests/commands/test_init_hook_delivery.py` | behavioral test | The pre-push gate must be scaffolded, activated, and verified for adopters (GHI #715).; `tests/commands/test_init_hook_delivery.py:53` |
| `tests/commands/test_interview_cmd.py` | behavioral test | Tests for ``gz interview adr`` ADR scaffolding (GHI #505).; `tests/commands/test_interview_cmd.py:47` |
| `tests/commands/test_json_document_rendering.py` | behavioral test | A `--json` document reaches stdout byte-exact, never console-rendered (GHI #1010).; `tests/commands/test_json_document_rendering.py:34` |
| `tests/commands/test_l3_gate_independence.py` | behavioral test | Tests proving gate checks pass regardless of Layer 3 artifact state.; `tests/commands/test_l3_gate_independence.py:39` |
| `tests/commands/test_lint.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_lint.py:11` |
| `tests/commands/test_migrate_semver.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_migrate_semver.py:16` |
| `tests/commands/test_mx_skill_alignment.py` | behavioral test | Skill-alignment regression for the gz mx verbs after gz-mx landed.; `tests/commands/test_mx_skill_alignment.py:30` |
| `tests/commands/test_obpi_acceptance_cli.py` | behavioral test | Acceptance exit codes cross the real process boundary (GHI #988).; `tests/commands/test_obpi_acceptance_cli.py:114` |
| `tests/commands/test_obpi_block_cmd.py` | behavioral test | `gz obpi block` / `gz obpi unblock` end-to-end (GHI #887).; `tests/commands/test_obpi_block_cmd.py:37` |
| `tests/commands/test_obpi_complete_coverage_kind_aware.py` | behavioral test | REQ-coverage gate is ADR-0.0.59 kind-aware (loosening pass, 2026-06-04).; `tests/commands/test_obpi_complete_coverage_kind_aware.py:63` |
| `tests/commands/test_obpi_complete_subprocess_decode.py` | behavioral test | Decode-robustness tests for the OBPI-completion REQ-coverage subprocesses.; `tests/commands/test_obpi_complete_subprocess_decode.py:20` |
| `tests/commands/test_obpi_complete_task_envelope_gate.py` | behavioral test | Tests for the task-envelope Signature-(b) chokepoint gate in ``gz obpi complete`` (GHI #590).; `tests/commands/test_obpi_complete_task_envelope_gate.py:71` |
| `tests/commands/test_obpi_complete_ts_order.py` | behavioral test | Ledger ts-order across the rows one completion writes (GHI #842).; `tests/commands/test_obpi_complete_ts_order.py:120` |
| `tests/commands/test_obpi_precomplete.py` | behavioral test | Tests for `gz obpi precomplete` (GHI #196).; `tests/commands/test_obpi_precomplete.py:68` |
| `tests/commands/test_obpi_validate_cmd.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_obpi_validate_cmd.py:35` |
| `tests/commands/test_parsers.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_parsers.py:10` |
| `tests/commands/test_pipeline_baseline_verification.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_pipeline_baseline_verification.py:25` |
| `tests/commands/test_pipeline_verification_multiline.py` | behavioral test | Verify-stage extractor joins multi-line Verification commands (GHI #569, BI-1).; `tests/commands/test_pipeline_verification_multiline.py:28` |
| `tests/commands/test_prd.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_prd.py:12` |
| `tests/commands/test_preflight.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_preflight.py:14` |
| `tests/commands/test_preflight_receipt_archive.py` | behavioral test | Plan ownership and FAIL-receipt preservation in preflight (GHI #967).; `tests/commands/test_preflight_receipt_archive.py:40` |
| `tests/commands/test_readiness.py` | behavioral test | Readiness audit discovery-based checks (GHI #135).; `tests/commands/test_readiness.py:27` |
| `tests/commands/test_reference_checker.py` | behavioral test | BEHAVIOR tests for the ``gh`` adapter behind the ``ReferenceChecker`` port.; `tests/commands/test_reference_checker.py:49` |
| `tests/commands/test_register_adrs.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_register_adrs.py:13` |
| `tests/commands/test_runtime.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_runtime.py:131` |
| `tests/commands/test_specify.py` | behavioral test | No module docstring; see method names and production calls in JSON; `tests/commands/test_specify.py:15` |
| `tests/commands/test_state.py` | output-form fixture | Tests for the gz state command surface (GHI #319).; `tests/commands/test_state.py:31` |
| `tests/commands/test_status_obpi.py` | output-form fixture | Tests for `gz obpi status` runtime-state rendering and repudiation handling.; `tests/commands/test_status_obpi.py:45` |
| `tests/commands/test_status_obpi_inspect.py` | behavioral test | Tests for tracked-defect state resolution in the OBPI status view (GHI #966).; `tests/commands/test_status_obpi_inspect.py:42` |
| `tests/commands/test_sync_hook_diagnosis.py` | output-form fixture | Tests that `gz git-sync` keeps a refusing hook's diagnosis (GHI #816).; `tests/commands/test_sync_hook_diagnosis.py:121` |
| `tests/commands/test_sync_pull_ordering.py` | behavioral test | Tests for git-sync pull-verb selection across the auto-commit (GHI #720).; `tests/commands/test_sync_pull_ordering.py:90` |
| `tests/commands/test_sync_sweep_guard.py` | behavioral test | Tests for the git-sync ceremony sweep guard (GHI #708).; `tests/commands/test_sync_sweep_guard.py:38` |
| `tests/commands/test_validate_json_exit.py` | behavioral test | `gz validate --json` reports the same exit status as plain mode (GHI #995).; `tests/commands/test_validate_json_exit.py:59` |
| `tests/commands/test_validate_output_rendering.py` | output-form fixture | Rendering tests for `gz validate` operator output (GHI #944).; `tests/commands/test_validate_output_rendering.py:64` |
| `tests/commands/test_validate_ownership_declarations.py` | behavioral test | Tests for the `.gzkit/ownership/*.json` validator in `gz validate --documents`.; `tests/commands/test_validate_ownership_declarations.py:48` |
| `tests/commands/test_validate_task_envelope_encoding.py` | behavioral test | Regression: the task-envelope git-log subprocess must decode output as UTF-8.; `tests/commands/test_validate_task_envelope_encoding.py:43` |
| `tests/content/test_corpus_store.py` | behavioral test | Append-only corpus store tests — OBPI-0.0.37-19.; `tests/content/test_corpus_store.py:45` |
| `tests/distribution/test_baseline_manifest.py` | structural fence | Unit tests for the distribution baseline manifest (OBPI-0.0.32-06).; `tests/distribution/test_baseline_manifest.py:35` |
| `tests/eval/test_datasets.py` | behavioral test | Tests for eval dataset loading and schema validation.; `tests/eval/test_datasets.py:40` |
| `tests/eval/test_delta_gates.py` | behavioral test | Tests for eval-delta release gates.; `tests/eval/test_delta_gates.py:34` |
| `tests/eval/test_harness.py` | behavioral test | Tests for eval harness scoring and runner.; `tests/eval/test_harness.py:26` |
| `tests/eval/test_regression.py` | behavioral test | Tests for regression detection — OBPI-0.0.5-04.; `tests/eval/test_regression.py:61` |
| `tests/fixtures/adr_audit_covers_backfill/legitimate_evolution/test_decorator.py` | SUPPORT proof | Synthetic test file for the legitimate-evolution fixture (do not collect).; `tests/fixtures/adr_audit_covers_backfill/legitimate_evolution/test_decorator.py:1` |
| `tests/fixtures/adr_audit_covers_backfill/same_commit_backfill/test_decorator.py` | SUPPORT proof | Synthetic test file for the same-commit-backfill fixture (do not collect).; `tests/fixtures/adr_audit_covers_backfill/same_commit_backfill/test_decorator.py:1` |
| `tests/governance/test_active_campaign_registry.py` | SUPPORT proof | The campaign registry is the authority, and the plans' prose must agree.; `tests/governance/test_active_campaign_registry.py:83` |
| `tests/governance/test_adr_audit_advisory_kind.py` | behavioral test | REQ-kind partition of the audit-check uncovered-REQ advisory (GHI #701).; `tests/governance/test_adr_audit_advisory_kind.py:27` |
| `tests/governance/test_adr_status_index.py` | behavioral test | Tests for ADR status index regenerator and freshness audit (GHI #322).; `tests/governance/test_adr_status_index.py:89` |
| `tests/governance/test_adversary_workspace.py` | behavioral test | The Step-4b adversary's disposable writable checkout and replay bar (GHI #961).; `tests/governance/test_adversary_workspace.py:101` |
| `tests/governance/test_advisory_scorecard_coverage.py` | behavioral test | Clause-coverage enforcement for the advisory scorecard (GHI #754).; `tests/governance/test_advisory_scorecard_coverage.py:79` |
| `tests/governance/test_advisory_scorecard_summary.py` | behavioral test | The scorecard's Summary roll-up is fenced against the rows it summarizes.; `tests/governance/test_advisory_scorecard_summary.py:67` |
| `tests/governance/test_audit_absorption_duplicates.py` | behavioral test | Fixture-level tests for ``audit_absorption_duplicates`` (GHI #376).; `tests/governance/test_audit_absorption_duplicates.py:55` |
| `tests/governance/test_audit_insights_shape.py` | behavioral test | Fixture-level tests for ``audit_insights_shape`` (GHI #358).; `tests/governance/test_audit_insights_shape.py:25` |
| `tests/governance/test_audit_instructions_files_budget.py` | behavioral test | Fixture-level tests for ``audit_instructions_files_budget`` (GHI #373).; `tests/governance/test_audit_instructions_files_budget.py:48` |
| `tests/governance/test_audit_line_endings.py` | behavioral test | Fixture-level tests for ``audit_line_endings`` (GHI #570).; `tests/governance/test_audit_line_endings.py:59` |
| `tests/governance/test_audit_utf8_prefix.py` | behavioral test | Fixture-level tests for ``audit_utf8_prefix`` extended scope (GHI #275).; `tests/governance/test_audit_utf8_prefix.py:34` |
| `tests/governance/test_authorship_policy.py` | behavioral test | Commit authorship must be provable inside the repo it protects (GHI #725).; `tests/governance/test_authorship_policy.py:33` |
| `tests/governance/test_bdd_tier_stderr_hygiene.py` | behavioral test | A passing BDD run must not emit failure-shaped prose (GHI #726).; `tests/governance/test_bdd_tier_stderr_hygiene.py:47` |
| `tests/governance/test_behave_cli_alignment.py` | SUPPORT proof | Every ``gz <verb>`` in features and operator docs must resolve (GHI #198).; `tests/governance/test_behave_cli_alignment.py:21` |
| `tests/governance/test_behave_scenario_isolation.py` | behavioral test | A scenario's `mock.patch` must not outlive the scenario (CI red, 2026-08-29).; `tests/governance/test_behave_scenario_isolation.py:67` |
| `tests/governance/test_behave_sharding.py` | behavioral test | Behave shards across processes; the gate's answer must not change (GHI #906).; `tests/governance/test_behave_sharding.py:88` |
| `tests/governance/test_brief_path_validity.py` | behavioral test | Brief allowed-path validity primitives (GHI #419).; `tests/governance/test_brief_path_validity.py:31` |
| `tests/governance/test_brief_path_validity_wiring.py` | behavioral test | Integration tests for GHI #419 wirings.; `tests/governance/test_brief_path_validity_wiring.py:25` |
| `tests/governance/test_brief_reconcile_pending_upstream.py` | behavioral test | Unstarted-brief Discovery scoping narrows by predicate, never by exemption (GHI #615).; `tests/governance/test_brief_reconcile_pending_upstream.py:53` |
| `tests/governance/test_check_registry_coherence.py` | structural fence | The reachability ratchet and the `gz check` pipeline must agree (GHI #787).; `tests/governance/test_check_registry_coherence.py:67` |
| `tests/governance/test_check_scope_parity.py` | structural fence | `gz check` membership is declared, not accidental (GHI #744).; `tests/governance/test_check_scope_parity.py:162` |
| `tests/governance/test_check_step_concurrency.py` | structural fence | Every `gz check` step must declare its concurrency class (GHI #835).; `tests/governance/test_check_step_concurrency.py:37` |
| `tests/governance/test_check_step_timing.py` | behavioral test | `gz check` measures each step's cost in-gate, as a byproduct of the run (GHI #1077).; `tests/governance/test_check_step_timing.py:94` |
| `tests/governance/test_check_step_writer_overlap.py` | behavioral test | One measured reader may overlap the writer lane; nothing else may (GHI #904).; `tests/governance/test_check_step_writer_overlap.py:84` |
| `tests/governance/test_chore_control_surface_rule_conflicts_evidence.py` | behavioral test | Acceptance-gate enforcement for the control-surface-rule-conflicts chore.; `tests/governance/test_chore_control_surface_rule_conflicts_evidence.py:64` |
| `tests/governance/test_chore_metadata_authority.py` | behavioral test | Chore metadata has one authority: its JSON (GHI #1002).; `tests/governance/test_chore_metadata_authority.py:60` |
| `tests/governance/test_chore_readme_class_contract.py` | SUPPORT proof | The chores authoring contract names the classes and rungs the code enforces (GHI #999 step 4).; `tests/governance/test_chore_readme_class_contract.py:39` |
| `tests/governance/test_chore_rung_conformance.py` | behavioral test | A chore's workflow may not reach past its declared rung (GHI #999 step 3).; `tests/governance/test_chore_rung_conformance.py:58` |
| `tests/governance/test_chore_suppression.py` | behavioral test | A chore never discharges a finding by suppression (GHI #999 step 6).; `tests/governance/test_chore_suppression.py:53` |
| `tests/governance/test_cli_alignment_scope.py` | behavioral test | `--cli-alignment` must see the surfaces its rule declares (GHI #745).; `tests/governance/test_cli_alignment_scope.py:45` |
| `tests/governance/test_codex_delivery_witness.py` | behavioral test | Behavior tests for the observed-delivery witness (GHI #962).; `tests/governance/test_codex_delivery_witness.py:86` |
| `tests/governance/test_commit_trailers_is_gated.py` | structural fence | The commit-trailer obligation is reached by a gate, not only by hand (GHI #1017).; `tests/governance/test_commit_trailers_is_gated.py:40` |
| `tests/governance/test_config_derivation.py` | behavioral test | The two axes `--config-registry` declares exhaustive but does not reach (GHI #1066).; `tests/governance/test_config_derivation.py:53` |
| `tests/governance/test_config_registry.py` | behavioral test | Config-registry declaration gate (GHI #929).; `tests/governance/test_config_registry.py:65` |
| `tests/governance/test_corpus_retirement_witness.py` | behavioral test | Tests for the corpus retirement-witness gate (GHI #885, GHI #878).; `tests/governance/test_corpus_retirement_witness.py:86` |
| `tests/governance/test_covers_fence_scope.py` | behavioral test | The `@covers` fence's subject must stay "tests for this scope" (GHI #944).; `tests/governance/test_covers_fence_scope.py:39` |
| `tests/governance/test_covers_kind_coherence.py` | structural fence | Guard: `@covers` may only decorate a BEHAVIOR REQ (GHI #711).; `tests/governance/test_covers_kind_coherence.py:52` |
| `tests/governance/test_deprecated_verb_prescription.py` | behavioral test | Tests for `gz validate --deprecated-verb-prescription` (GHI #705).; `tests/governance/test_deprecated_verb_prescription.py:34` |
| `tests/governance/test_doc_code_citations.py` | behavioral test | Governance prose citing a `src/gzkit/` module must cite one that exists (GHI #1083).; `tests/governance/test_doc_code_citations.py:54` |
| `tests/governance/test_doc_surface_parity.py` | behavioral test | Doc-surface parity audit (GHI #418).; `tests/governance/test_doc_surface_parity.py:15` |
| `tests/governance/test_drift_proof_channel_scope.py` | behavioral test | Drift's unlinked-spec set is scoped to the @covers proof channel (GHI #729).; `tests/governance/test_drift_proof_channel_scope.py:61` |
| `tests/governance/test_enforcement_nc_discrimination.py` | behavioral test | Negative controls must discriminate the claim they name (GHI #699).; `tests/governance/test_enforcement_nc_discrimination.py:31` |
| `tests/governance/test_enforcement_population.py` | behavioral test | BEHAVIOR tests for population-declared enforcement claims (GHI #1007).; `tests/governance/test_enforcement_population.py:64` |
| `tests/governance/test_exemption_controls.py` | behavioral test | BEHAVIOR tests for the exemption-control inventory (GHI #797).; `tests/governance/test_exemption_controls.py:46` |
| `tests/governance/test_fidelity_self_reference.py` | behavioral test | Self-referential fidelity-assertion guard (GHI #702).; `tests/governance/test_fidelity_self_reference.py:33` |
| `tests/governance/test_gate_caller_scope.py` | behavioral test | Uncalled-gate inventory and disclosure (GHI #785).; `tests/governance/test_gate_caller_scope.py:64` |
| `tests/governance/test_generated_surface_line_endings.py` | behavioral test | Every generated-surface writer pins `newline="\n"` (GHI #681).; `tests/governance/test_generated_surface_line_endings.py:58` |
| `tests/governance/test_handoff_floor_bookmark_transparency.py` | behavioral test | A floor bookmark must not sink the settled-ruling corpus (commit 02ca03ee).; `tests/governance/test_handoff_floor_bookmark_transparency.py:78` |
| `tests/governance/test_handoff_multi_parent_lineage.py` | behavioral test | Multi-parent handoff lineage (GHI #790).; `tests/governance/test_handoff_multi_parent_lineage.py:60` |
| `tests/governance/test_handoff_resume_gate.py` | behavioral test | BEHAVIOR tests for handoff-resume selection and booking coupling.; `tests/governance/test_handoff_resume_gate.py:103` |
| `tests/governance/test_handoff_ruling_store.py` | behavioral test | The settled-ruling corpus is transported by reference, not by copied prose (GHI #838).; `tests/governance/test_handoff_ruling_store.py:99` |
| `tests/governance/test_handoff_rulings_count.py` | behavioral test | The Settled Rulings pointer states the count the store actually holds (GHI #838).; `tests/governance/test_handoff_rulings_count.py:92` |
| `tests/governance/test_handoff_selection.py` | behavioral test | The handoff SELECTION readers must not drift apart (GHI #758).; `tests/governance/test_handoff_selection.py:79` |
| `tests/governance/test_hook_stage_claims.py` | SUPPORT proof | Governed prose may not claim a hook runs at a stage the config does not declare.; `tests/governance/test_hook_stage_claims.py:141` |
| `tests/governance/test_invariant_witness.py` | behavioral test | Every registered invariant's structural_witness must resolve to a real command (GHI #623).; `tests/governance/test_invariant_witness.py:46` |
| `tests/governance/test_ledger_derived_stream_cache.py` | behavioral test | Derived ledger streams are computed once per instance, not once per call (GHI #1080).; `tests/governance/test_ledger_derived_stream_cache.py:80` |
| `tests/governance/test_ledger_duplicate_rows.py` | behavioral test | A row appearing twice in the ledger is detected, not silent (GHI #1075).; `tests/governance/test_ledger_duplicate_rows.py:76` |
| `tests/governance/test_ledger_event_handler_coverage.py` | structural fence | Every ledger event type must be claimed by the graph builder (GHI #193 class).; `tests/governance/test_ledger_event_handler_coverage.py:21` |
| `tests/governance/test_ledger_event_schema_coverage.py` | structural fence | Every ledger event type must have a paired ``schemas/ledger.json`` entry (GHI #374 class).; `tests/governance/test_ledger_event_schema_coverage.py:29` |
| `tests/governance/test_ledger_reader_parity.py` | behavioral test | gzkit's two canonical ledger readers must reach the same verdict (GHI #883).; `tests/governance/test_ledger_reader_parity.py:142` |
| `tests/governance/test_ledger_ts_is_not_stated.py` | structural fence | No production ledger-event constructor states its own `ts` (GHI #1074).; `tests/governance/test_ledger_ts_is_not_stated.py:143` |
| `tests/governance/test_lifecycle_pointers.py` | behavioral test | Tests for the lifecycle-pointer audit (GHI #846).; `tests/governance/test_lifecycle_pointers.py:37` |
| `tests/governance/test_lock_ttl_canon.py` | behavioral test | The lock TTL default must equal the token-block canon, with no drift across sites.; `tests/governance/test_lock_ttl_canon.py:25` |
| `tests/governance/test_mandated_tier1_dispatch.py` | behavioral test | The mandated tier-1 dispatch registry is the authority the wrapper set must cover.; `tests/governance/test_mandated_tier1_dispatch.py:84` |
| `tests/governance/test_manpage_alignment.py` | behavioral test | Operator-doc references to manpages must use the <verb>.md convention (GHI #532).; `tests/governance/test_manpage_alignment.py:37` |
| `tests/governance/test_manpage_dir_single_source.py` | structural fence | Regression test for hardcoded manpage path construction (GHI #425).; `tests/governance/test_manpage_dir_single_source.py:118` |
| `tests/governance/test_mock_leakage.py` | structural fence | No test may leave a ``Mock`` bolted onto a gzkit module (GHI #857).; `tests/governance/test_mock_leakage.py:43` |
| `tests/governance/test_nc_fixture_cleanup_guard.py` | behavioral test | The NC runner removes only the private workspace it created (GHI #920).; `tests/governance/test_nc_fixture_cleanup_guard.py:42` |
| `tests/governance/test_obpi_complete_lock_release.py` | behavioral test | Unit tests for the token-block exit edge: mechanical lock-surrender + handoff; `tests/governance/test_obpi_complete_lock_release.py:71` |
| `tests/governance/test_obpi_rename_coherence.py` | behavioral test | A renamed OBPI is not a vanished OBPI (the subject arm of the orphan census).; `tests/governance/test_obpi_rename_coherence.py:42` |
| `tests/governance/test_obpi_slug_rename.py` | behavioral test | The slug-correction repair refuses every shape that is not a live rename.; `tests/governance/test_obpi_slug_rename.py:30` |
| `tests/governance/test_obpi_status_monitor.py` | behavioral test | The single monitor every OBPI-brief ``status:`` writer consults (GHI #669).; `tests/governance/test_obpi_status_monitor.py:29` |
| `tests/governance/test_operator_block_gate.py` | behavioral test | The pipeline must refuse to launch against an OBPI awaiting a human (GHI #887).; `tests/governance/test_operator_block_gate.py:40` |
| `tests/governance/test_operator_block_state.py` | behavioral test | An OBPI awaiting a human ruling must be representable in Layer 2 (GHI #887).; `tests/governance/test_operator_block_state.py:51` |
| `tests/governance/test_orientation_freshness.py` | behavioral test | Tests for SessionStart orientation freshness audit (GHI #341).; `tests/governance/test_orientation_freshness.py:91` |
| `tests/governance/test_orphaned_implementation.py` | behavioral test | Orphaned-implementation trust audit (GHI #438).; `tests/governance/test_orphaned_implementation.py:117` |
| `tests/governance/test_park_coherence.py` | behavioral test | Park state must agree with where the parent ADR actually lives (GHI #774).; `tests/governance/test_park_coherence.py:52` |
| `tests/governance/test_path_separator_portability.py` | structural fence | Regression test for non-POSIX ``relative_to`` rendering (GHI #383).; `tests/governance/test_path_separator_portability.py:92` |
| `tests/governance/test_persona_witness.py` | behavioral test | Tests for audit_persona_witness validator scope (GHI #741).; `tests/governance/test_persona_witness.py:79` |
| `tests/governance/test_pool_interview_schema.py` | behavioral test | Pool ADR interview JSON schema enforcement (GHI #719).; `tests/governance/test_pool_interview_schema.py:63` |
| `tests/governance/test_population_controls.py` | behavioral test | BEHAVIOR tests for the enforcement-claim population inventory (GHI #1007).; `tests/governance/test_population_controls.py:38` |
| `tests/governance/test_proof_freshness_date_format.py` | output-form fixture | Date-rendering semantics for the control-surface proof-freshness gate.; `tests/governance/test_proof_freshness_date_format.py:48` |
| `tests/governance/test_python_version_pins.py` | behavioral test | Interpreter-pin coherence audit (`gz validate --python-version-pins`).; `tests/governance/test_python_version_pins.py:23` |
| `tests/governance/test_release_workflow_guard.py` | structural fence | The release workflow must never rewrite a release that is already served.; `tests/governance/test_release_workflow_guard.py:128` |
| `tests/governance/test_rename_fold.py` | behavioral test | One fold answers "where is this artifact now" for both readers.; `tests/governance/test_rename_fold.py:38` |
| `tests/governance/test_replay_review_import.py` | behavioral test | Dispatch-to-import: a replay claim survives ingestion only if it replayed (GHI #961).; `tests/governance/test_replay_review_import.py:96` |
| `tests/governance/test_req_kind_tag_emphasis.py` | behavioral test | Every reader of the ADR-0.0.59 kind-tag syntax tolerates emphasis (GHI #809).; `tests/governance/test_req_kind_tag_emphasis.py:59` |
| `tests/governance/test_router_tables_validator.py` | behavioral test | Tests for `gz validate --router-tables` validator (OBPI-0.27.0-03).; `tests/governance/test_router_tables_validator.py:40` |
| `tests/governance/test_rule_delivery_scoping.py` | behavioral test | Rules delivered to adopters scope to paths an adopter can have (GHI #911).; `tests/governance/test_rule_delivery_scoping.py:68` |
| `tests/governance/test_scan_interval_gate.py` | behavioral test | Wall-clock currency gate for chores whose staleness is externally driven.; `tests/governance/test_scan_interval_gate.py:62` |
| `tests/governance/test_schema_sensitivity.py` | behavioral test | JSON schema validation for the `sensitivity` field (ADR-0.0.22, OBPI-0.0.22-01).; `tests/governance/test_schema_sensitivity.py:56` |
| `tests/governance/test_scorecard_silent_dropout.py` | behavioral test | A scorecard row that looks scored must actually be scored.; `tests/governance/test_scorecard_silent_dropout.py:53` |
| `tests/governance/test_security_surfaces_registry.py` | behavioral test | Registry-level tests for the security-surface registry (ADR-0.0.22, OBPI-0.0.22-02).; `tests/governance/test_security_surfaces_registry.py:46` |
| `tests/governance/test_session_exit.py` | behavioral test | Tests for the session-exit floor bookmark (GHI #756).; `tests/governance/test_session_exit.py:43` |
| `tests/governance/test_session_green_gate_delivery_control.py` | behavioral test | Negative control for the session-green gate's delivery arm (GHI #851, GHI #1007).; `tests/governance/test_session_green_gate_delivery_control.py:28` |
| `tests/governance/test_session_start.py` | behavioral test | Tests for the session-start handoff advisement (GHI #757).; `tests/governance/test_session_start.py:50` |
| `tests/governance/test_settings_local_vault_outside_repo.py` | behavioral test | Regression test for the settings.local backup vault escaping the repo (GHI #1071).; `tests/governance/test_settings_local_vault_outside_repo.py:45` |
| `tests/governance/test_settings_vault_awareness.py` | behavioral test | The settings vault has a witness, and gzkit agrees with the hook (GHI #1072).; `tests/governance/test_settings_vault_awareness.py:47` |
| `tests/governance/test_settled_ruling_integrity.py` | behavioral test | A settled ruling must reach the chain head whole, and exactly once.; `tests/governance/test_settled_ruling_integrity.py:116` |
| `tests/governance/test_shipped_executable_fence.py` | behavioral test | The tautological audit exempts fences over shipped executables (GHI #730).; `tests/governance/test_shipped_executable_fence.py:36` |
| `tests/governance/test_skill_code_citations.py` | behavioral test | Skill prose citing a `src/gzkit/` module must cite one that exists (GHI #896).; `tests/governance/test_skill_code_citations.py:54` |
| `tests/governance/test_skill_delivery_scoping.py` | behavioral test | Skills delivered to adopters exclude those only gzkit can run (GHI #915).; `tests/governance/test_skill_delivery_scoping.py:73` |
| `tests/governance/test_stage4_evidence.py` | behavioral test | Tests for tool-generated, fail-closed Stage-4 evidence (GHI #643).; `tests/governance/test_stage4_evidence.py:27` |
| `tests/governance/test_stage4_packet.py` | behavioral test | Tests for Step-4a packet transcript verification (GHI #942).; `tests/governance/test_stage4_packet.py:41` |
| `tests/governance/test_status_writer_coverage.py` | behavioral test | Writer-coverage audit for frontmatter ``status:`` writes (GHI #669).; `tests/governance/test_status_writer_coverage.py:39` |
| `tests/governance/test_step_module_dead_helpers.py` | structural fence | No step module keeps a private helper nothing calls (GHI #918).; `tests/governance/test_step_module_dead_helpers.py:28` |
| `tests/governance/test_subprocess_errors_replace.py` | behavioral test | Recurrence guard for text-mode subprocess reads missing ``errors=`` (GHI #582).; `tests/governance/test_subprocess_errors_replace.py:50` |
| `tests/governance/test_surface_weight_recalibrate.py` | behavioral test | Tests for the surface-weight recalibration emitter (GHI #791).; `tests/governance/test_surface_weight_recalibrate.py:102` |
| `tests/governance/test_test_fixture_encoding.py` | structural fence | Regression test for fixture I/O without ``encoding="utf-8"`` (GHI #384).; `tests/governance/test_test_fixture_encoding.py:77` |
| `tests/governance/test_test_fixture_line_endings.py` | behavioral test | A test asserting exact bytes builds its fixture byte-exactly (GHI #1069).; `tests/governance/test_test_fixture_line_endings.py:155` |
| `tests/governance/test_theater_signature_scan.py` | behavioral test | Tests for the static theater-signature analyzer (ADR-0.0.73 channel 1, GHI #657).; `tests/governance/test_theater_signature_scan.py:38` |
| `tests/governance/test_transcribed_counts.py` | behavioral test | Live ADR OBPI counts are refused; dated records are not (GHI #768).; `tests/governance/test_transcribed_counts.py:51` |
| `tests/governance/test_type_ignore_syntax.py` | behavioral test | Forbid ``# type: ignore[<code>]`` directives naming no ty rule (GHI #197).; `tests/governance/test_type_ignore_syntax.py:56` |
| `tests/governance/test_validator_graph_field_coverage.py` | structural fence | Every validator-read graph field must have a graph-writer (GHI #193 class).; `tests/governance/test_validator_graph_field_coverage.py:21` |
| `tests/governance/test_verb_references.py` | behavioral test | One `gz <verb>` extractor, shared by every governed verb-checker (GHI #748).; `tests/governance/test_verb_references.py:41` |
| `tests/governance/test_wall_clock_fixtures_audit.py` | behavioral test | Detector for wall-clock-sensitive test fixtures (GHI #865, arm 1).; `tests/governance/test_wall_clock_fixtures_audit.py:41` |
| `tests/governance/test_wheel_path_literals.py` | behavioral test | Regression fence for machine-local path literals in wheel-shipped instructions (GHI #900).; `tests/governance/test_wheel_path_literals.py:61` |
| `tests/hooks/test_commit_locus_ledger_recorder.py` | behavioral test | The ledger must see a governance edit whatever tool wrote it (GHI #847).; `tests/hooks/test_commit_locus_ledger_recorder.py:113` |
| `tests/hooks/test_formatter_failure_visibility.py` | behavioral test | A formatter that could not run must not read as one that ran (GHI #914).; `tests/hooks/test_formatter_failure_visibility.py:65` |
| `tests/hooks/test_ghi_triage_chat_silence.py` | behavioral test | Unit tests for the ghi-triage chat-silence backstop hook (GHI #424).; `tests/hooks/test_ghi_triage_chat_silence.py:67` |
| `tests/hooks/test_hook_emitter_root_binding.py` | behavioral test | Hook emitters derive their bytes from the root they are handed (GHI #909).; `tests/hooks/test_hook_emitter_root_binding.py:74` |
| `tests/hooks/test_obpi_completion_commit_guard.py` | behavioral test | The completion gate must observe the commit, not the tool that wrote it (GHI #847).; `tests/hooks/test_obpi_completion_commit_guard.py:120` |
| `tests/hooks/test_verifier_pipe_gate.py` | behavioral test | Verification exit-code integrity gate — the clause's teeth (GHI #589).; `tests/hooks/test_verifier_pipe_gate.py:31` |
| `tests/knowledge/test_active_campaign_resolution.py` | behavioral test | The knowledge bundle's active-campaign source follows the registry.; `tests/knowledge/test_active_campaign_resolution.py:43` |
| `tests/models/test_frontmatter_sensitivity.py` | behavioral test | Pydantic frontmatter tests for the `sensitivity` field (ADR-0.0.22, OBPI-0.0.22-01).; `tests/models/test_frontmatter_sensitivity.py:48` |
| `tests/models/test_security_surface_entry.py` | behavioral test | Pydantic model tests for SecuritySurfaceEntry (ADR-0.0.22, OBPI-0.0.22-02).; `tests/models/test_security_surface_entry.py:37` |
| `tests/mx/test_authorship_floor_pin.py` | structural fence | The authorship guard enforces a floor concern and must never demote (GHI #852).; `tests/mx/test_authorship_floor_pin.py:50` |
| `tests/mx/test_gate5_enrollment.py` | structural fence | Gate5 floor enrollment-completeness enumeration (GHI #648).; `tests/mx/test_gate5_enrollment.py:48` |
| `tests/mx/test_mx_lock_lifecycle.py` | behavioral test | Tests for the MX session-lock lifecycle (GHI #848).; `tests/mx/test_mx_lock_lifecycle.py:66` |
| `tests/mx/test_precommit_checkpoint_surface.py` | structural fence | The pre-commit enforcement surface honors the MX checkpoint (GHI #843).; `tests/mx/test_precommit_checkpoint_surface.py:115` |
| `tests/policy/test_cli_consistency.py` | structural fence | CLI consistency and convention enforcement tests.; `tests/policy/test_cli_consistency.py:104` |
| `tests/policy/test_env_usage.py` | structural fence | Policy tests: env-var usage enforcement via AST scanning.; `tests/policy/test_env_usage.py:125` |
| `tests/policy/test_import_boundaries.py` | structural fence | Policy tests: architectural import boundary enforcement via AST scanning.; `tests/policy/test_import_boundaries.py:238` |
| `tests/policy/test_naming_conventions.py` | structural fence | Policy tests: snake_case naming convention enforcement.; `tests/policy/test_naming_conventions.py:72` |
| `tests/policy/test_rich_markup_escaping.py` | structural fence | Policy test: data interpolated into Rich markup must not be parsed as markup.; `tests/policy/test_rich_markup_escaping.py:350` |
| `tests/scripts/test_adherence_probe.py` | behavioral test | Unit tests for scripts/adherence_probe.py.; `tests/scripts/test_adherence_probe.py:66` |
| `tests/scripts/test_backfill_adr_taxonomy.py` | behavioral test | Unit tests for scripts/backfill_adr_taxonomy.py (OBPI-0.0.17-05).; `tests/scripts/test_backfill_adr_taxonomy.py:63` |
| `tests/skills/test_ghi_author_brief_ownership.py` | SUPPORT proof | ghi-author Step 0 must see work-owning OBPI briefs (GHI #864).; `tests/skills/test_ghi_author_brief_ownership.py:39` |
| `tests/skills/test_ghi_triage_blocker_freshness.py` | behavioral test | ghi-triage blocker-freshness contract.; `tests/skills/test_ghi_triage_blocker_freshness.py:70` |
| `tests/skills/test_ghi_triage_deliverable.py` | behavioral test | ghi-triage v4 deliverable contract — GHI #324.; `tests/skills/test_ghi_triage_deliverable.py:77` |
| `tests/skills/test_namespace_router_surface_sync.py` | structural fence | Tests for router surface sync parity (OBPI-0.27.0-02).; `tests/skills/test_namespace_router_surface_sync.py:39` |
| `tests/skills/test_namespace_routers.py` | structural fence | Tests for namespace-router skills (OBPI-0.27.0-01).; `tests/skills/test_namespace_routers.py:45` |
| `tests/skills/test_router_coverage_completion.py` | structural fence | Tests for namespace-router coverage completion (OBPI-0.27.0-04).; `tests/skills/test_router_coverage_completion.py:78` |
| `tests/test_acceptance.py` | behavioral test | Acceptance preserves contract obligations through independent repair review.; `tests/test_acceptance.py:63` |
| `tests/test_acceptance_context.py` | behavioral test | The real response schema and captured context reach review ingestion together.; `tests/test_acceptance_context.py:21` |
| `tests/test_acceptance_execution.py` | behavioral test | Executable acceptance proof checks use contract literals and real subprocess controls.; `tests/test_acceptance_execution.py:93` |
| `tests/test_acceptance_grounds.py` | behavioral test | A reviewer that cannot execute must cite what it read to approve (GHI #994).; `tests/test_acceptance_grounds.py:112` |
| `tests/test_acceptance_integration.py` | behavioral test | Real acceptance history governs pipeline transitions (GHI #985).; `tests/test_acceptance_integration.py:51` |
| `tests/test_acceptance_store.py` | behavioral test | Durable acceptance proof and closure survive review-history edits.; `tests/test_acceptance_store.py:76` |
| `tests/test_adversarial_validation_audit.py` | behavioral test | Tests for the Step-4b adversarial-validation trust audit (GHI #676).; `tests/test_adversarial_validation_audit.py:108` |
| `tests/test_adversarial_validation_event.py` | behavioral test | REQ-derived tests for the adversarial_validation ledger event (GHI #676).; `tests/test_adversarial_validation_event.py:34` |
| `tests/test_adversarial_validation_gate.py` | behavioral test | Tests for the Step-4b adversarial-validation completion gate (GHI #676).; `tests/test_adversarial_validation_gate.py:77` |
| `tests/test_airlock_events.py` | SUPPORT proof | Advisory round-trip coverage for the airlock L2 ledger event types.; `tests/test_airlock_events.py:19` |
| `tests/test_attestation_verdict_classifier.py` | behavioral test | Semantics + single-source guard for the ceremony attestation-verdict classifier.; `tests/test_attestation_verdict_classifier.py:20` |
| `tests/test_check_fingerprint.py` | behavioral test | The gate must not re-run over a tree it already passed (GHI #835).; `tests/test_check_fingerprint.py:60` |
| `tests/test_chores_project_local.py` | behavioral test | Project-local chores stay out of the wheel and out of adopters (GHI #728).; `tests/test_chores_project_local.py:77` |
| `tests/test_chores_runtime_state_prune.py` | behavioral test | Sync CONVERGES the package chores tree; it does not only add to it (GHI #783).; `tests/test_chores_runtime_state_prune.py:104` |
| `tests/test_chores_surface_level_files.py` | behavioral test | Files directly under the chores surface belong to no slug (GHI #1005).; `tests/test_chores_surface_level_files.py:66` |
| `tests/test_closeout_ceremony_consumption.py` | behavioral test | Tests for ceremony-attestation consumption by the closeout pipeline (GHI #351).; `tests/test_closeout_ceremony_consumption.py:66` |
| `tests/test_codex_config_surface.py` | behavioral test | Codex config control-surface validation.; `tests/test_codex_config_surface.py:33` |
| `tests/test_codex_hooks.py` | behavioral test | Interim Codex delivery: native registration, recovery, and shared decisions.; `tests/test_codex_hooks.py:18` |
| `tests/test_codex_roles.py` | behavioral test | Native role delivery must carry canonical governance instructions.; `tests/test_codex_roles.py:37` |
| `tests/test_config.py` | behavioral test | Tests for gzkit configuration.; `tests/test_config.py:13` |
| `tests/test_configured_path_consumers.py` | behavioral test | Configured source and manifest identities survive their shared consumers.; `tests/test_configured_path_consumers.py:23` |
| `tests/test_decomposition.py` | behavioral test | Tests for deterministic ADR decomposition helpers.; `tests/test_decomposition.py:17` |
| `tests/test_efficacy.py` | behavioral test | Efficacy channel — a capability must report its reach, not just its numerator.; `tests/test_efficacy.py:28` |
| `tests/test_file_lock.py` | behavioral test | Cross-platform advisory file lock — the shared primitive (GHI #945).; `tests/test_file_lock.py:68` |
| `tests/test_forcing_functions_alignment.py` | behavioral test | Forcing functions must have a channel end to end (GHI #719).; `tests/test_forcing_functions_alignment.py:46` |
| `tests/test_frontmatter.py` | behavioral test | Ingress matrix for the shared tri-state frontmatter reader (GHI #736).; `tests/test_frontmatter.py:27` |
| `tests/test_git_spawn_boundary.py` | behavioral test | ``gzkit.git_spawn_boundary`` — the predicate behind the git-fixture-isolation fence.; `tests/test_git_spawn_boundary.py:23` |
| `tests/test_hooks_guards.py` | behavioral test | Tests for gzkit.hooks.guards — pytest usage scanner.; `tests/test_hooks_guards.py:31` |
| `tests/test_hooks_guards_ledger_sync.py` | behavioral test | Tests for ledger and skill-sync guards added under GHIs #207 / #210.; `tests/test_hooks_guards_ledger_sync.py:36` |
| `tests/test_instruction_eval.py` | behavioral test | Tests for gzkit.instruction_eval — instruction architecture eval suite.; `tests/test_instruction_eval.py:75` |
| `tests/test_instruction_frontmatter_validate.py` | behavioral test | Validator parses instruction frontmatter on line 1 (GHI #368).; `tests/test_instruction_frontmatter_validate.py:37` |
| `tests/test_interview.py` | behavioral test | Tests for gzkit interview module.; `tests/test_interview.py:16` |
| `tests/test_ledger_correction_consumers.py` | behavioral test | Which QUESTION each ledger consumer asks, and which stream answers it (GHI #611).; `tests/test_ledger_correction_consumers.py:118` |
| `tests/test_ledger_corrections.py` | behavioral test | Append-only corrective-action primitive over any ledger event (GHI #611).; `tests/test_ledger_corrections.py:110` |
| `tests/test_ledger_durability.py` | behavioral test | ``Ledger.append`` does not return until the row is durable (GHI #952).; `tests/test_ledger_durability.py:97` |
| `tests/test_ledger_merge.py` | behavioral test | Tests for the append-only JSONL three-way merge (GHI #811).; `tests/test_ledger_merge.py:16` |
| `tests/test_ledger_merge_driver.py` | behavioral test | Tests for the git-facing merge-driver adapter (GHI #811).; `tests/test_ledger_merge_driver.py:29` |
| `tests/test_ledger_producer_probe.py` | behavioral test | A fresh real producer must persist the canonical subject before receiving credit.; `tests/test_ledger_producer_probe.py:15` |
| `tests/test_ledger_transaction_boundary.py` | behavioral test | ``Ledger.append`` is one transaction across writers and across a crash (GHI #953).; `tests/test_ledger_transaction_boundary.py:164` |
| `tests/test_lifecycle.py` | behavioral test | Tests for the content lifecycle state machine.; `tests/test_lifecycle.py:22` |
| `tests/test_lifecycle_auto_fix.py` | behavioral test | Tests for OBPI-0.0.9-04: Lifecycle auto-fix of brief frontmatter status.; `tests/test_lifecycle_auto_fix.py:24` |
| `tests/test_mutation_witness.py` | behavioral test | Mutation-sweep witness with a four-way verdict (GHI #963).; `tests/test_mutation_witness.py:61` |
| `tests/test_obpi_audit_prior_state.py` | behavioral test | Tests for OBPI audit prior state reading (GHI #97).; `tests/test_obpi_audit_prior_state.py:17` |
| `tests/test_obpi_dispatch_channel.py` | behavioral test | Tests for the Stage-2 dispatch channel (GHI #845).; `tests/test_obpi_dispatch_channel.py:46` |
| `tests/test_obpi_prefix_match.py` | behavioral test | Tests for OBPI short-form prefix matching in resolve_obpi.; `tests/test_obpi_prefix_match.py:21` |
| `tests/test_ontology_source_roots.py` | behavioral test | Configured source populations, with default/override controls (GHI #1054).; `tests/test_ontology_source_roots.py:42` |
| `tests/test_parser_arb.py` | structural fence | Parser registration tests for gz arb.; `tests/test_parser_arb.py:33` |
| `tests/test_persona_portability.py` | behavioral test | Cross-project persona portability integration tests — OBPI-0.0.13-06.; `tests/test_persona_portability.py:44` |
| `tests/test_persona_scaffolding.py` | behavioral test | Tests for persona scaffolding — OBPI-0.0.13-02.; `tests/test_persona_scaffolding.py:34` |
| `tests/test_pipeline_integration.py` | behavioral test | Tests for OBPI-0.18.0-05 dispatch tracking, aggregation, and agent validation.; `tests/test_pipeline_integration.py:29` |
| `tests/test_pipeline_launch_status.py` | behavioral test | Launching a pipeline advances its brief out of Draft (GHI #992).; `tests/test_pipeline_launch_status.py:35` |
| `tests/test_pipeline_stage_fence.py` | behavioral test | Tests for the post-Stage-2 production-write fence (GHI #844).; `tests/test_pipeline_stage_fence.py:28` |
| `tests/test_plan_audit_cmd.py` | behavioral test | Tests for the gz plan-audit CLI command.; `tests/test_plan_audit_cmd.py:32` |
| `tests/test_plan_audit_scope.py` | behavioral test | GHI #1057: plan containment must reach the CLI verdict and receipt.; `tests/test_plan_audit_scope.py:18` |
| `tests/test_pyinstaller_spec.py` | structural fence | Regression tests for PyInstaller packaging paths.; `tests/test_pyinstaller_spec.py:25` |
| `tests/test_quality.py` | behavioral test | Tests for gzkit quality module.; `tests/test_quality.py:26` |
| `tests/test_red_parity_audit.py` | behavioral test | Tests for the RED-parity trust audit (GHI #642).; `tests/test_red_parity_audit.py:83` |
| `tests/test_red_witness.py` | behavioral test | Tests for the base-tree RED falsifiability witness (GHI #642).; `tests/test_red_witness.py:50` |
| `tests/test_registries.py` | behavioral test | The single read seam for `data/` config registries (GHI #1067).; `tests/test_registries.py:36` |
| `tests/test_registry.py` | behavioral test | Tests for the content type registry.; `tests/test_registry.py:17` |
| `tests/test_report_publication.py` | behavioral test | Publication preserves interpretations and books only durable reports.; `tests/test_report_publication.py:30` |
| `tests/test_reporter.py` | output-form fixture | Unit tests for gzkit.reporter presets and panels.; `tests/test_reporter.py:26` |
| `tests/test_req_kind_grandfathering_cache.py` | behavioral test | Tests for the req-kind grandfathering cache loader (GHI #544).; `tests/test_req_kind_grandfathering_cache.py:22` |
| `tests/test_req_kind_support_proof_grandfather.py` | behavioral test | Tests for the SUPPORT-channel grandfather cache loader (GHI #660).; `tests/test_req_kind_support_proof_grandfather.py:19` |
| `tests/test_review_capability.py` | behavioral test | Reviewer capability disclosure and verdict isolation (GHI #941).; `tests/test_review_capability.py:56` |
| `tests/test_roles_cli.py` | output-form fixture | Tests for the gz roles CLI command.; `tests/test_roles_cli.py:27` |
| `tests/test_skill_body_audit.py` | behavioral test | Countable skill-body authoring contracts (GHI #1037).; `tests/test_skill_body_audit.py:12` |
| `tests/test_skill_manpage_coverage.py` | SUPPORT proof | Skill manpage coverage contract (GHI #138).; `tests/test_skill_manpage_coverage.py:38` |
| `tests/test_skill_naming.py` | SUPPORT proof | Skill naming contract tests.; `tests/test_skill_naming.py:36` |
| `tests/test_skills_audit.py` | behavioral test | Tests for skill mirror identity contract enforcement.; `tests/test_skills_audit.py:69` |
| `tests/test_smoke_gate.py` | behavioral test | The smoke tier's budget must be enforced by something (GHI #724).; `tests/test_smoke_gate.py:29` |
| `tests/test_surface_write_idempotence.py` | behavioral test | Generated control surfaces are written only when their bytes change (GHI #890).; `tests/test_surface_write_idempotence.py:67` |
| `tests/test_sync.py` | behavioral test | Tests for gzkit sync module.; `tests/test_sync.py:93` |
| `tests/test_sync_parity_runtime_cache.py` | behavioral test | Sync parity ignores Python runtime cache files.; `tests/test_sync_parity_runtime_cache.py:15` |
| `tests/test_sync_skill_capture.py` | behavioral test | Skill preview must record copy intent without mutating mirrors.; `tests/test_sync_skill_capture.py:13` |
| `tests/test_task_frontmatter_stamp.py` | behavioral test | Producer-stamp the brief `tasks:` frontmatter channel (GHI #752).; `tests/test_task_frontmatter_stamp.py:66` |
| `tests/test_task_obpi_id_canonicalization.py` | behavioral test | `gz task start --req` must emit the canonical full OBPI slug (GHI #653).; `tests/test_task_obpi_id_canonicalization.py:119` |
| `tests/test_task_trailer_autostamp.py` | behavioral test | Auto-stamp `Task:` trailers from the active TASK set (GHI #731).; `tests/test_task_trailer_autostamp.py:49` |
| `tests/test_template_render_strictness.py` | behavioral test | Tests for the two-path template render contract (GHI #741 follow-up).; `tests/test_template_render_strictness.py:38` |
| `tests/test_test_shape.py` | behavioral test | Tests for the advisory test-shape inventory (GHI #571).; `tests/test_test_shape.py:37` |
| `tests/test_uncovered_accept_kind_gate.py` | behavioral test | BEHAVIOR REQs cannot be accepted-uncovered at the completion layer (GHI #537).; `tests/test_uncovered_accept_kind_gate.py:48` |
| `tests/test_validate.py` | behavioral test | Tests for gzkit validation engine.; `tests/test_validate.py:52` |
| `tests/test_validate_changelog.py` | behavioral test | Tests for the hermetic changelog structural validator (GHI #685).; `tests/test_validate_changelog.py:41` |
| `tests/test_validate_sync_parity.py` | behavioral test | Sync parity validation for generated control surfaces (GHI #134).; `tests/test_validate_sync_parity.py:160` |
| `tests/test_version_sync.py` | behavioral test | Tests for version sync helpers used during ADR closeout.; `tests/test_version_sync.py:17` |
| `tests/test_wbs_parser.py` | behavioral test | Tests for WBS table parsing and ADR content extraction in gz specify.; `tests/test_wbs_parser.py:79` |
| `tests/test_wheel_includes.py` | structural fence | Tests for wheel build configuration (OBPI-0.0.32-06 REQ-0.0.32-06-02).; `tests/test_wheel_includes.py:17` |
| `tests/tools/test_health_profiler.py` | SUPPORT proof | Test health profiler for the test-health-audit chore.; `tests/tools/test_health_profiler.py:1` |
| `tests/unit/test_progress_indication.py` | output-form fixture | Tests for progress indication (OBPI-0.0.4-09).; `tests/unit/test_progress_indication.py:67` |
| `tests/validate_pkg/test_absent_frontmatter_finding.py` | behavioral test | A canonical ADR with no frontmatter is a finding, not a pass (GHI #742).; `tests/validate_pkg/test_absent_frontmatter_finding.py:64` |
| `tests/validate_pkg/test_document_scope_guards.py` | behavioral test | Pinning tests for the two `--documents` scope guards landed under GHI #480.; `tests/validate_pkg/test_document_scope_guards.py:76` |
| `tests/validators/test_rule_version_markers.py` | behavioral test | Behavior tests for the rule-version-marker validator.; `tests/validators/test_rule_version_markers.py:95` |

## Appendix C. Every selected pilot test and observed mutant detections

A = distinct raw-killed mutant jobs with a unittest FAIL attributed to this method. E = distinct raw-killed mutant jobs with a unittest ERROR attributed to it. A and E can coexist on one job. Zero A and E means no observed detection in this pilot; import-time failures without a method ID are not credited to individual tests. These counts come from saved per-mutant stdout after stderr capture, not from coverage inference.

| Test ID | Target group | A | E |
|---|---|---|---|
| tests.arb.test_canonical_steps_leaf_import.CanonicalStepsLeafImportTests.test_leaf_import_pulls_no_heavy_dependency | verifier_pipe_gate | 0 | 0 |
| tests.arb.test_canonical_steps_leaf_import.CanonicalStepsLeafImportTests.test_validator_reexports_the_same_object | verifier_pipe_gate | 0 | 0 |
| tests.arb.test_canonical_steps_leaf_import.CanonicalStepsLeafImportTests.test_verifier_pipe_gate_reads_the_same_object | verifier_pipe_gate | 0 | 0 |
| tests.arb.test_red_witness_void_experiment.TestVoidExperimentIsNotAVerdict.test_landed_work_reports_not_applicable | red_witness | 0 | 20 |
| tests.arb.test_red_witness_void_experiment.TestVoidExperimentIsNotAVerdict.test_not_applicable_is_neither_red_nor_hollow | red_witness | 11 | 0 |
| tests.arb.test_red_witness_void_experiment.TestWithheldProductionFiles.test_landed_work_withholds_nothing | red_witness | 0 | 7 |
| tests.arb.test_red_witness_void_experiment.TestWithheldProductionFiles.test_modified_production_is_withheld | red_witness | 7 | 7 |
| tests.arb.test_red_witness_void_experiment.TestWithheldProductionFiles.test_uncommitted_tests_alone_still_withhold_nothing | red_witness | 2 | 7 |
| tests.arb.test_red_witness_void_experiment.TestWithheldProductionFiles.test_untracked_production_is_withheld | red_witness | 7 | 7 |
| tests.arb.test_writer_validator_lockstep.TestAdvisorVerdictReceiptsValidate.test_a_recorded_verdict_is_valid | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestAdvisorVerdictReceiptsValidate.test_a_verdict_without_its_explanation_is_rejected | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestAdvisorVerdictReceiptsValidate.test_fresh_import_orders_can_record_and_validate | red_witness | 0 | 12 |
| tests.arb.test_writer_validator_lockstep.TestProvenanceRemedyIsRunnable.test_the_remedy_is_the_canonical_step_invocation | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestRedReceiptsValidate.test_a_receipt_carrying_base_provenance_is_valid | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestRedReceiptsValidate.test_an_undeclared_property_is_still_rejected | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestRedReceiptsValidate.test_an_unknown_provenance_value_is_rejected | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestSignalKilledStepReceiptsValidate.test_a_negative_exit_status_is_valid | red_witness | 0 | 0 |
| tests.arb.test_writer_validator_lockstep.TestSignalKilledStepReceiptsValidate.test_a_non_integer_exit_status_is_still_rejected | red_witness | 0 | 0 |
| tests.commands.test_obpi_complete_behave_coverage.TestBehaveRefPasses.test_failing_marks_failing_cover | req_coverage | 0 | 0 |
| tests.commands.test_obpi_complete_behave_coverage.TestBehaveRefPasses.test_passes_for_passing_scenario | req_coverage | 0 | 0 |
| tests.commands.test_obpi_complete_coverage_kind_aware.TestCoverageGateKindAware.test_behavior_kind_uncovered_req_still_fails_closed | req_coverage | 2 | 0 |
| tests.commands.test_obpi_complete_coverage_kind_aware.TestCoverageGateKindAware.test_parse_brief_req_kinds_reads_inline_tags | req_coverage | 2 | 0 |
| tests.commands.test_obpi_complete_coverage_kind_aware.TestCoverageGateKindAware.test_support_and_structural_fence_reqs_do_not_require_covers | req_coverage | 2 | 2 |
| tests.commands.test_validate_cmds.TestFrontmatterCoherence.test_frontmatter_coherent_passes | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestFrontmatterCoherence.test_id_drift_detected_for_obpi | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestFrontmatterCoherence.test_json_output_includes_frontmatter_errors | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestFrontmatterCoherence.test_lane_drift_detected | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestFrontmatterCoherence.test_parent_drift_detected | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_after_init | validate_commit_trailers | 5 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_all_includes_ledger_checks | validate_commit_trailers | 5 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_briefs_does_not_require_live_scope_for_completed_history | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_briefs_tolerates_legacy_noncompleted_brief_shape | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_accepts_slug_form_task_trailer | validate_commit_trailers | 3 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_flag_accepted | validate_commit_trailers | 3 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_flags_src_change_without_task_trailer | validate_commit_trailers | 8 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_passes_with_trailer | validate_commit_trailers | 3 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_rejects_ceremony_alone_for_src | validate_commit_trailers | 8 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_commit_trailers_skips_non_code_commits | validate_commit_trailers | 3 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_decomposition_detects_count_mismatch | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_decomposition_draft_adr_still_requires_scorecard | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_decomposition_flag_accepted | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_decomposition_skips_validated_legacy_adr_shape | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_interviews_detects_missing_qa_transcript | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_interviews_flag_accepted | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_interviews_passes_with_embedded_qa_transcript | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_interviews_skips_waived_adr | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_ledger_flag_fails_on_invalid_ledger | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_requirements_detects_bare_requirements_section | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_requirements_flag_accepted | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_requirements_passes_when_req_ids_present | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateCommand.test_validate_requirements_skips_briefs_without_requirements_section | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateDocumentsNestedIteration.test_bare_id_in_nested_package_fails_closed | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateDocumentsNestedIteration.test_slug_id_in_nested_package_produces_no_id_error | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateDocumentsSkipsObpiCorpus.test_adr_validation_still_fires | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateDocumentsSkipsObpiCorpus.test_historical_obpi_brief_produces_no_documents_errors | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateScopeResolution.test_closeout_proof_flag_resolves_to_closeout_proof_only | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateScopeResolution.test_default_validate_scope_list_includes_frontmatter | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateScopeResolution.test_distribution_flag_resolves_to_distribution_only | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateScopeResolution.test_every_execution_scope_is_reportable | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateScopeResolution.test_frontmatter_flag_resolves_to_frontmatter_only | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateTaxonomyFlag.test_validate_taxonomy_detects_missing_kind | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateTaxonomyFlag.test_validate_taxonomy_detects_pool_kind_frontmatter | validate_commit_trailers | 0 | 0 |
| tests.commands.test_validate_cmds.TestValidateTaxonomyFlag.test_validate_taxonomy_flag_clean_on_empty_tree | validate_commit_trailers | 0 | 0 |
| tests.governance.test_commit_trailers_is_gated.CommitTrailersGatedTests.test_commit_trailers_is_in_the_default_tier | validate_commit_trailers | 0 | 0 |
| tests.governance.test_commit_trailers_is_gated.CommitTrailersGatedTests.test_the_scope_is_still_registered_and_runnable | validate_commit_trailers | 0 | 0 |
| tests.governance.test_covers_kind_coherence.TestCoversDecoratesOnlyBehaviorReqs.test_no_covers_on_non_behavior_req | req_coverage | 0 | 0 |
| tests.governance.test_eval_feedback_trailer.TestEvalFeedbackTrailerValidation.test_eval_feedback_source_additive_with_task_passes_code_commit | validate_commit_trailers | 3 | 0 |
| tests.governance.test_eval_feedback_trailer.TestEvalFeedbackTrailerValidation.test_eval_feedback_source_alone_rejected_for_src_commit | validate_commit_trailers | 8 | 0 |
| tests.governance.test_eval_feedback_trailer.TestEvalFeedbackTrailerValidation.test_fails_rule_edit_closing_eval_feedback_ghi_without_trailer | validate_commit_trailers | 18 | 0 |
| tests.governance.test_eval_feedback_trailer.TestEvalFeedbackTrailerValidation.test_passes_rule_edit_closing_eval_feedback_ghi_with_trailer | validate_commit_trailers | 3 | 0 |
| tests.governance.test_req_coverage.TestDiscoverCoversAstSafety.test_skips_unparseable_file_keeps_valid_match | req_coverage | 8 | 3 |
| tests.governance.test_req_coverage.TestDiscoverCoversBddFeatureTree.test_bdd_ref_not_returned_without_features_root | req_coverage | 0 | 3 |
| tests.governance.test_req_coverage.TestDiscoverCoversBddFeatureTree.test_missing_features_root_returns_empty | req_coverage | 0 | 0 |
| tests.governance.test_req_coverage.TestDiscoverCoversBddFeatureTree.test_returns_ref_for_bdd_scenario_tag | req_coverage | 9 | 0 |
| tests.governance.test_req_coverage.TestDiscoverCoversFinds.test_returns_empty_when_no_match | req_coverage | 5 | 3 |
| tests.governance.test_req_coverage.TestDiscoverCoversFinds.test_returns_empty_when_tests_root_missing | req_coverage | 0 | 3 |
| tests.governance.test_req_coverage.TestDiscoverCoversFinds.test_returns_ref_for_matching_decorator | req_coverage | 9 | 3 |
| tests.governance.test_req_coverage.TestDiscoverCoversMultiple.test_two_tests_decorated_for_same_req | req_coverage | 7 | 3 |
| tests.governance.test_req_coverage.TestParseBriefReqs.test_extracts_canonical_req_rows | req_coverage | 2 | 0 |
| tests.governance.test_req_coverage.TestParseBriefReqs.test_returns_empty_when_brief_path_missing | req_coverage | 0 | 2 |
| tests.governance.test_req_coverage.TestParseBriefReqs.test_returns_empty_when_no_acceptance_criteria_section | req_coverage | 0 | 0 |
| tests.governance.test_req_coverage.TestParseBriefReqs.test_skips_malformed_req_lines | req_coverage | 2 | 0 |
| tests.governance.test_req_coverage.TestParseBriefReqs.test_stops_at_next_h2_section | req_coverage | 2 | 0 |
| tests.governance.test_req_coverage_record.TestBypassFlagLedgerEvent.test_bypass_emits_bypass_used_ledger_event | covers | 0 | 22 |
| tests.governance.test_req_coverage_record.TestBypassFlagLedgerEvent.test_bypass_flag_requires_bypass_reason | covers | 4 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_behavior_covered_req_has_pass_status | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_behavior_uncovered_req_has_fail_status | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_grandfathering_cache_naming_no_kind_fails_closed | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_grandfathering_cache_overrides_inference | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_legacy_untagged_req_inferred_as_grandfathered | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_structural_fence_req_no_project_root_is_unproven_fence | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestComputeThreeChannelCoverage.test_support_req_is_advisory_not_fail_closed | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_entry_has_ledger_event_ids_field | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_entry_has_parent_adr_anchor_field | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_entry_has_proof_channel_field | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_entry_has_proof_status_field | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_entry_has_taxonomy_kind_field | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_rollup_has_behavior_uncovered_reqs | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestCoverageEntryExtendedFields.test_coverage_rollup_has_grandfathered_reqs | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestGrandfatheringCacheFile.test_grandfathering_json_exists | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestGrandfatheringCacheFile.test_grandfathering_json_is_valid_json | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_artifact_edited_text_infers_support | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_boundary_invariants_text_infers_structural_fence | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_default_inference_is_behavior | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_denied_paths_text_infers_structural_fence | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_gz_validate_text_infers_support | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_remains_inside_scope_infers_structural_fence | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestInferReqKind.test_structural_fence_beats_support_on_denied_paths | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestReqEntityTaxonomyKind.test_behavior_tag_stored_on_req_entity | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestReqEntityTaxonomyKind.test_structural_fence_tag_stored_on_req_entity | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestReqEntityTaxonomyKind.test_support_tag_stored_on_req_entity | covers | 0 | 0 |
| tests.governance.test_req_coverage_record.TestReqEntityTaxonomyKind.test_untagged_req_has_none_taxonomy_kind | covers | 0 | 0 |
| tests.governance.test_req_kind_tag_emphasis.TestKindTagEmphasisAcrossReaders.test_coverage_reader_reads_emphasised_tags_as_tagged | req_coverage | 2 | 0 |
| tests.governance.test_req_kind_tag_emphasis.TestKindTagEmphasisAcrossReaders.test_discipline_validator_reads_emphasised_tags_as_tagged | req_coverage | 0 | 0 |
| tests.governance.test_req_kind_tag_emphasis.TestKindTagEmphasisAcrossReaders.test_plain_tags_still_read | req_coverage | 2 | 0 |
| tests.governance.test_req_kind_tag_emphasis.TestKindTagEmphasisAcrossReaders.test_triangle_reader_tolerates_emphasis | req_coverage | 0 | 0 |
| tests.governance.test_req_kind_tag_emphasis.TestKindTagEmphasisAcrossReaders.test_trust_audit_readers_tolerate_emphasis | req_coverage | 0 | 0 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableFence.test_bare_gzkit_path_is_not_a_fence | tautological_tests | 2 | 3 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableFence.test_function_with_no_string_constants_is_not_a_fence | tautological_tests | 1 | 3 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableFence.test_governance_doc_assertion_is_not_a_fence | tautological_tests | 2 | 3 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableFence.test_hook_path_assertion_is_a_fence | tautological_tests | 4 | 3 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableFence.test_partial_prefix_does_not_match | tautological_tests | 2 | 3 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableRootsAreReal.test_no_root_is_missing_from_disk | tautological_tests | 0 | 0 |
| tests.governance.test_shipped_executable_fence.TestShippedExecutableRootsAreReal.test_roots_are_directory_prefixes | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_correct_function_name | tautological_tests | 0 | 84 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_detects_open_with_assertion | tautological_tests | 42 | 44 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_detects_path_read_text | tautological_tests | 41 | 46 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_exempts_fixture_methods | tautological_tests | 1 | 9 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_exempts_production_code_calls | tautological_tests | 6 | 19 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_flags_pure_static_grep | tautological_tests | 40 | 46 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_returns_empty_for_no_cooccurrence | tautological_tests | 5 | 13 |
| tests.governance.test_tautological_tests.TestAstScanner.test_scanner_returns_list_of_operation_instances | tautological_tests | 0 | 44 |
| tests.governance.test_tautological_tests.TestCheckStepRegistration.test_runner_importable | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestCheckStepRegistration.test_step_registered_in_build_check_steps | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_asserting_only_that_an_operation_raises_exempts | tautological_tests | 2 | 31 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_covers_decorator_does_not_exempt_a_content_echo | tautological_tests | 41 | 45 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_production_call_through_a_same_module_helper_exempts | tautological_tests | 16 | 34 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_production_symbol_used_as_a_value_exempts | tautological_tests | 7 | 22 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_real_production_call_in_body_still_exempts | tautological_tests | 6 | 19 |
| tests.governance.test_tautological_tests.TestDecoratorsAreNotBehavior.test_undecorated_equivalent_is_flagged_identically | tautological_tests | 40 | 46 |
| tests.governance.test_tautological_tests.TestDispositionEngine.test_default_disposition_is_convert | tautological_tests | 3 | 1 |
| tests.governance.test_tautological_tests.TestDispositionEngine.test_disposition_returns_one_of_four_values | tautological_tests | 0 | 1 |
| tests.governance.test_tautological_tests.TestDispositionEngine.test_ledger_path_disposition | tautological_tests | 2 | 0 |
| tests.governance.test_tautological_tests.TestDispositionEngine.test_schema_path_disposition | tautological_tests | 5 | 0 |
| tests.governance.test_tautological_tests.TestDispositionEngine.test_setup_method_disposition | tautological_tests | 1 | 0 |
| tests.governance.test_tautological_tests.TestDriftGate.test_clean_state_no_errors | tautological_tests | 0 | 44 |
| tests.governance.test_tautological_tests.TestDriftGate.test_drift_detected_when_current_exceeds_baseline | tautological_tests | 47 | 94 |
| tests.governance.test_tautological_tests.TestDriftGate.test_drift_errors_include_file_path_and_disposition | tautological_tests | 47 | 94 |
| tests.governance.test_tautological_tests.TestDriftGate.test_no_drift_when_current_equals_baseline | tautological_tests | 7 | 88 |
| tests.governance.test_tautological_tests.TestEventModel.test_event_discriminator_literal | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestEventModel.test_event_importable | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestEventModel.test_event_in_typed_ledger_event_union | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestEventModel.test_factory_creates_parseable_event | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_audit_drift_identity_reports_actual_new_op | tautological_tests | 55 | 97 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_module_backed_exemption_requires_importlib_signal | tautological_tests | 44 | 44 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_module_backed_self_attr_exempted | tautological_tests | 21 | 50 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_real_doc_echo_tautology_still_flagged | tautological_tests | 40 | 46 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_source_fence_ast_parse_exempted | tautological_tests | 15 | 36 |
| tests.governance.test_tautological_tests.TestGhi632ScannerCorrectnessAndDrift.test_source_fence_rglob_py_exempted | tautological_tests | 6 | 37 |
| tests.governance.test_tautological_tests.TestSelfExemption.test_self_exemption_constant_exists | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestSelfExemption.test_waivers_file_not_counted_in_scan | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_baseline_extra_forbidden | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_baseline_frozen | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_models_importable | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_proposed_disposition_has_four_values | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_proposed_disposition_values | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_tautological_test_operation_extra_forbidden | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_tautological_test_operation_frozen | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_waiver_extra_forbidden | tautological_tests | 0 | 0 |
| tests.governance.test_tautological_tests.TestTautologicalTestModels.test_waiver_frozen | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestFoldedIntoTheTestQualityScope.test_test_quality_scope_includes_the_wall_clock_detector | tautological_tests | 0 | 68 |
| tests.governance.test_wall_clock_fixtures_audit.TestPredicateRequiresBothHalves.test_absolute_timestamp_without_a_verdict_is_inert | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestPredicateRequiresBothHalves.test_both_halves_together_are_flagged | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestPredicateRequiresBothHalves.test_the_repo_is_clean_under_this_predicate | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestPredicateRequiresBothHalves.test_verdict_without_an_absolute_timestamp_is_inert | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_clean_tree_returns_no_errors | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_clean_when_the_seam_supplies_the_clock | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_clean_when_the_timestamp_is_computed | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_far_past_expiry_fixture_is_not_flagged | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_flags_an_absolute_claimed_at | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_message_names_the_seam_not_just_the_problem | tautological_tests | 0 | 0 |
| tests.governance.test_wall_clock_fixtures_audit.TestWallClockFixtureAudit.test_only_scans_the_tests_tree | tautological_tests | 0 | 0 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_chain_caught_by_a_later_statement_is_masked | verifier_pipe_gate | 54 | 40 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_chain_that_runs_to_the_end_of_the_command_is_permitted | verifier_pipe_gate | 1 | 45 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_pipeline_under_pipefail_carries_the_status_to_its_terminator | verifier_pipe_gate | 63 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_pipeline_under_pipefail_keeps_both_escapes | verifier_pipe_gate | 48 | 49 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_status_read_after_a_background_separator_does_not_protect | verifier_pipe_gate | 61 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_a_status_read_inside_the_chain_does_not_protect_the_list_end | verifier_pipe_gate | 60 | 32 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_errexit_does_not_rescue_a_chain | verifier_pipe_gate | 62 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_errexit_still_protects_a_verifier_that_ends_its_chain | verifier_pipe_gate | 26 | 47 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_reading_the_status_right_after_the_chain_is_preserved | verifier_pipe_gate | 13 | 39 |
| tests.hooks.test_verifier_pipe_gate.TestAndOrListMasking.test_without_pipefail_an_upstream_verifier_is_still_the_pipe_arm | verifier_pipe_gate | 46 | 23 |
| tests.hooks.test_verifier_pipe_gate.TestArmSpecificRecovery.test_both_arms_carry_all_three_guardrail_parts | verifier_pipe_gate | 76 | 33 |
| tests.hooks.test_verifier_pipe_gate.TestArmSpecificRecovery.test_the_pipe_arm_recommends_pipefail | verifier_pipe_gate | 85 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestArmSpecificRecovery.test_the_sequence_arm_names_the_verifier_not_the_pipe | verifier_pipe_gate | 94 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestArmSpecificRecovery.test_the_sequence_arm_recommends_errexit_not_pipefail | verifier_pipe_gate | 101 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestArmSpecificRecovery.test_the_sequence_arm_says_pipefail_will_not_help | verifier_pipe_gate | 101 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestCanonicalRegistryCoherence.test_every_runnable_canonical_step_command_is_detected | verifier_pipe_gate | 61 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestDecideContract.test_a_masked_verifier_blocks | verifier_pipe_gate | 60 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestDecideContract.test_an_unparseable_command_is_not_this_gates_call | verifier_pipe_gate | 1 | 4 |
| tests.hooks.test_verifier_pipe_gate.TestDecideContract.test_block_prose_carries_all_three_parts | verifier_pipe_gate | 77 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestDecideContract.test_non_bash_tools_are_out_of_scope | verifier_pipe_gate | 1 | 0 |
| tests.hooks.test_verifier_pipe_gate.TestEscapesMustBeUsedNotNamedTests.test_a_filename_containing_the_marker_does_not_disarm_the_gate | verifier_pipe_gate | 51 | 36 |
| tests.hooks.test_verifier_pipe_gate.TestEscapesMustBeUsedNotNamedTests.test_a_flag_value_containing_the_marker_does_not_disarm_the_gate | verifier_pipe_gate | 47 | 36 |
| tests.hooks.test_verifier_pipe_gate.TestEscapesMustBeUsedNotNamedTests.test_echoing_the_word_does_not_disarm_the_gate | verifier_pipe_gate | 49 | 36 |
| tests.hooks.test_verifier_pipe_gate.TestEscapesMustBeUsedNotNamedTests.test_grepping_for_the_word_does_not_disarm_the_gate | verifier_pipe_gate | 56 | 36 |
| tests.hooks.test_verifier_pipe_gate.TestEscapesMustBeUsedNotNamedTests.test_pipefail_set_after_the_pipeline_does_not_protect_it | verifier_pipe_gate | 52 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_a_backgrounded_verifier_gets_its_own_arm | verifier_pipe_gate | 64 | 27 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_a_caught_chain_gets_its_own_arm | verifier_pipe_gate | 74 | 32 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_every_pasteable_prefix_correction_is_admitted | verifier_pipe_gate | 145 | 45 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_the_background_correction_is_admitted | verifier_pipe_gate | 82 | 44 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_the_chain_corrections_are_admitted | verifier_pipe_gate | 91 | 43 |
| tests.hooks.test_verifier_pipe_gate.TestEveryArmsCorrectionIsAdmitted.test_the_new_arms_carry_all_three_guardrail_parts | verifier_pipe_gate | 62 | 36 |
| tests.hooks.test_verifier_pipe_gate.TestExemptionControlIsRegisteredAndCatches.test_the_exemption_control_catches_a_named_but_unused_escape | verifier_pipe_gate | 118 | 0 |
| tests.hooks.test_verifier_pipe_gate.TestExemptionControlIsRegisteredAndCatches.test_the_rule_claim_declares_which_control_covers_its_exemption | verifier_pipe_gate | 2 | 26 |
| tests.hooks.test_verifier_pipe_gate.TestExitPreservingEscapes.test_pipefail_permits_the_pipeline | verifier_pipe_gate | 14 | 27 |
| tests.hooks.test_verifier_pipe_gate.TestExitPreservingEscapes.test_pipestatus_permits_the_pipeline | verifier_pipe_gate | 11 | 38 |
| tests.hooks.test_verifier_pipe_gate.TestExitPreservingEscapes.test_set_with_combined_flags_still_sets_pipefail | verifier_pipe_gate | 13 | 27 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_group_followed_by_a_replacing_statement_is_masked_by_that_arm | verifier_pipe_gate | 153 | 88 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_group_that_runs_no_verifier_is_not_this_gates_business | verifier_pipe_gate | 1 | 80 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_group_whose_status_is_the_verifiers_is_permitted | verifier_pipe_gate | 10 | 94 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_group_written_against_an_operator_is_still_read | verifier_pipe_gate | 129 | 79 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_pipestatus_read_inside_a_later_group_is_preserved | verifier_pipe_gate | 14 | 64 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_statement_after_the_verifier_inside_the_group_masks_it | verifier_pipe_gate | 111 | 90 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_status_read_after_a_backgrounded_group_does_not_protect | verifier_pipe_gate | 93 | 67 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_status_read_by_the_first_statement_of_a_following_group_is_preserved | verifier_pipe_gate | 120 | 76 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_substitution_closed_against_a_separator_no_longer_hides_the_next_verifier | verifier_pipe_gate | 113 | 46 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_verifier_backgrounded_at_the_end_of_a_group_is_masked_by_what_follows | verifier_pipe_gate | 113 | 79 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_a_verifier_errexit_aborts_on_is_still_the_groups_status_outside | verifier_pipe_gate | 114 | 66 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_errexit_does_not_reach_into_a_group_inside_an_and_or_list | verifier_pipe_gate | 92 | 65 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_errexit_does_not_rescue_a_grouped_verifier_in_a_chain | verifier_pipe_gate | 98 | 67 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_errexit_reaches_into_a_group_that_ends_its_list | verifier_pipe_gate | 29 | 87 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_non_grouping_parens_do_not_stop_a_later_group_being_read | verifier_pipe_gate | 125 | 75 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_parentheses_that_are_not_a_grouping_are_not_read_as_one | verifier_pipe_gate | 2 | 60 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_pipefail_reaches_a_grouped_pipeline_stage | verifier_pipe_gate | 128 | 68 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_prose_parens_in_a_heredoc_body_keep_their_lexing | verifier_pipe_gate | 20 | 43 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_reading_the_status_right_after_the_group_or_inside_it_is_preserved | verifier_pipe_gate | 19 | 76 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_shell_state_set_in_a_brace_group_statement_does_leak_out | verifier_pipe_gate | 81 | 81 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_shell_state_set_in_a_subshell_does_not_leak_out | verifier_pipe_gate | 122 | 82 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecognition.test_unbalanced_parens_keep_the_ungrouped_reading | verifier_pipe_gate | 51 | 53 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecovery.test_a_sequence_errexit_cannot_reach_gets_its_own_arm | verifier_pipe_gate | 121 | 64 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecovery.test_the_errexit_suppressed_correction_is_admitted | verifier_pipe_gate | 144 | 76 |
| tests.hooks.test_verifier_pipe_gate.TestGroupedVerifierRecovery.test_the_sequence_prefix_correction_is_admitted_for_a_group | verifier_pipe_gate | 172 | 91 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_a_bare_verifier_is_permitted | verifier_pipe_gate | 1 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_a_later_pipeline_does_not_taint_the_verifier_but_the_sequence_masks_it | verifier_pipe_gate | 53 | 47 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_a_non_verifier_piped_into_a_filter_is_permitted | verifier_pipe_gate | 2 | 29 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_a_quoted_pipe_is_data_not_an_operator | verifier_pipe_gate | 1 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_a_verifier_in_the_final_segment_is_permitted | verifier_pipe_gate | 2 | 27 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_logical_or_is_not_a_pipe | verifier_pipe_gate | 61 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_masking_is_the_pipe_not_the_filter_identity | verifier_pipe_gate | 54 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_the_clause_prescribed_redirect_form_is_permitted | verifier_pipe_gate | 1 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestMaskedVerifierDetection.test_the_three_filters_the_clause_names_are_refused | verifier_pipe_gate | 47 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_a_non_verifier_verdict_idiom_is_not_this_gates_business | verifier_pipe_gate | 1 | 37 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_an_or_else_branch_masks_the_verifier | verifier_pipe_gate | 49 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_errexit_does_not_protect_a_backgrounded_verifier | verifier_pipe_gate | 52 | 27 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_errexit_does_not_protect_an_or_else | verifier_pipe_gate | 53 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_errexit_still_protects_the_sequence_it_does_abort | verifier_pipe_gate | 25 | 40 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_it_is_not_keyed_to_what_the_branch_says | verifier_pipe_gate | 49 | 33 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseArm.test_reading_the_status_in_the_branch_is_preserved | verifier_pipe_gate | 13 | 42 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseRecovery.test_the_or_else_arm_carries_all_three_guardrail_parts | verifier_pipe_gate | 55 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseRecovery.test_the_or_else_arm_names_the_branch_not_the_pipe_or_the_sequence | verifier_pipe_gate | 65 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseRecovery.test_the_or_else_arm_recommends_reading_the_status_in_the_branch | verifier_pipe_gate | 70 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestOrElseRecovery.test_the_or_else_arm_says_errexit_will_not_help | verifier_pipe_gate | 65 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_long_form_errexit_operand_is_honored | verifier_pipe_gate | 23 | 40 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_newline_separated_sequence_masks_the_same_way | verifier_pipe_gate | 53 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_non_verifier_sequence_is_not_this_gates_business | verifier_pipe_gate | 1 | 37 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_status_read_after_an_intervening_statement_does_not_protect | verifier_pipe_gate | 56 | 30 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_trailing_separator_does_not_make_the_verifier_non_final | verifier_pipe_gate | 9 | 55 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_verifier_followed_by_a_filter_statement_is_masked | verifier_pipe_gate | 53 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_a_verifier_in_the_final_statement_is_not_masked | verifier_pipe_gate | 2 | 45 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_and_and_propagates_failure_so_it_is_not_masking | verifier_pipe_gate | 1 | 39 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_errexit_protects_the_statements_that_follow_it | verifier_pipe_gate | 25 | 40 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_masking_does_not_depend_on_the_trailing_statement_being_a_filter | verifier_pipe_gate | 53 | 33 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_naming_errexit_without_setting_it_does_not_disarm_the_gate | verifier_pipe_gate | 52 | 41 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_pipefail_alone_does_not_enable_errexit | verifier_pipe_gate | 63 | 31 |
| tests.hooks.test_verifier_pipe_gate.TestSequenceFormMasking.test_reading_the_status_immediately_after_is_preserved | verifier_pipe_gate | 13 | 42 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_a_non_verifier_gz_verb_is_not_a_verifier | verifier_pipe_gate | 1 | 29 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_a_verifier_name_as_a_quoted_argument_is_not_an_invocation | verifier_pipe_gate | 1 | 29 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_an_absolute_path_invocation_is_recognized | verifier_pipe_gate | 49 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_the_coverage_wrapper_form_is_recognized | verifier_pipe_gate | 49 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_the_dash_m_module_form_is_recognized | verifier_pipe_gate | 47 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestVerifierInvocationForms.test_the_python_dash_m_form_is_recognized | verifier_pipe_gate | 57 | 18 |
| tests.hooks.test_verifier_pipe_gate.TestVerifiersThatLeftTheCanonicalTable.test_a_scoped_module_run_is_still_protected | verifier_pipe_gate | 47 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestVerifiersThatLeftTheCanonicalTable.test_both_runners_are_protected_at_once | verifier_pipe_gate | 72 | 16 |
| tests.hooks.test_verifier_pipe_gate.TestVerifiersThatLeftTheCanonicalTable.test_naming_a_runner_is_not_running_one | verifier_pipe_gate | 10 | 29 |
| tests.hooks.test_verifier_pipe_gate.TheRecoveryIsTheCallersOwnCommandTests.test_a_multi_statement_command_is_handed_back_whole | verifier_pipe_gate | 81 | 36 |
| tests.hooks.test_verifier_pipe_gate.TheRecoveryIsTheCallersOwnCommandTests.test_the_cheap_route_is_named_before_the_expensive_one | verifier_pipe_gate | 5 | 95 |
| tests.hooks.test_verifier_pipe_gate.TheRecoveryIsTheCallersOwnCommandTests.test_the_file_capture_route_survives_as_the_alternative | verifier_pipe_gate | 69 | 16 |
| tests.hooks.test_verifier_pipe_gate.TheRecoveryIsTheCallersOwnCommandTests.test_the_next_step_hands_back_the_command_with_pipefail_prepended | verifier_pipe_gate | 77 | 16 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_a_reviewed_input_still_invalidates_under_a_changed_environment | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_configured_source_root_is_included | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_declared_execution_condition_changes_claim_without_changing_artifact | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_digest_components_name_the_two_reviewed_terms | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_history_changes_preserve_digest_but_contract_changes_invalidate | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_missing_requirement_declaration_cannot_shrink_obligations | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_nonmatching_frontmatter_roster_is_refused | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_obligation_comes_from_contract_not_historical_analysis | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_parent_contract_change_invalidates_and_history_does_not | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_producer_claim_ignores_run_timing_but_retains_actual_results | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_source_addition_change_and_removal_invalidate_without_git | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_test_file_cannot_be_used_as_semantic_production_control | mutation_witness | 1 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_unrelated_environment_does_not_invalidate_the_reviewed_inputs | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.AcceptanceInputTests.test_wrong_covering_selector_is_rejected_before_execution | mutation_witness | 1 | 0 |
| tests.test_acceptance_execution.ExecutedBehaviorTests.test_always_refusing_implementation_cannot_satisfy_positive_baseline | mutation_witness | 6 | 43 |
| tests.test_acceptance_execution.ExecutedBehaviorTests.test_hollow_test_passing_broken_production_is_invalid_proof | mutation_witness | 75 | 56 |
| tests.test_acceptance_execution.ExecutedBehaviorTests.test_mutant_side_effect_invalidates_even_when_required_assertion_kills_it | mutation_witness | 83 | 65 |
| tests.test_acceptance_execution.ExecutedBehaviorTests.test_real_semantic_counterexample_is_killed_and_original_behavior_restored | mutation_witness | 104 | 64 |
| tests.test_acceptance_execution.ExecutedBehaviorTests.test_runtime_error_in_nominated_test_is_not_semantic_proof | mutation_witness | 24 | 57 |
| tests.test_acceptance_execution.ExistingProofChannelTests.test_missing_fence_anchor_does_not_generate_valid_proof | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.ExistingProofChannelTests.test_structural_fence_uses_anchored_parent_resolver_without_mutating | mutation_witness | 0 | 0 |
| tests.test_acceptance_execution.ExistingProofChannelTests.test_undeclared_support_witness_is_invalid | mutation_witness | 0 | 0 |
| tests.test_adr_governance_confirm.TestGovernanceSurfaceExists.test_adr_audit_check_importable | covers | 0 | 0 |
| tests.test_adr_governance_confirm.TestGovernanceSurfaceExists.test_compute_coverage_importable | covers | 0 | 0 |
| tests.test_adr_governance_confirm.TestGovernanceSurfaceExists.test_confirm_decision_no_absorption_needed | covers | 0 | 0 |
| tests.test_adr_governance_confirm.TestGovernanceSurfaceExists.test_scan_test_tree_importable | covers | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_reinstatement_with_a_non_string_parent_cannot_revive | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_reinstatement_with_no_schema_tag_cannot_revive | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_reinstatement_with_no_timestamp_cannot_revive | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_string_parent_is_still_accepted | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_valid_reinstatement_still_revives_its_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_valid_void_still_reaches_every_reader | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_void_with_a_non_string_parent_is_inert_in_the_tolerant_reader | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_void_with_no_schema_tag_is_inert_in_every_reader | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_a_void_with_no_timestamp_is_inert_in_every_reader | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_an_authored_event_still_gets_its_defaults | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_both_readers_reach_the_same_verdict_on_the_same_bytes | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_equal_timestamps_in_valid_append_order_are_still_accepted | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestAStoredRowsEnvelopeIsNeverManufactured.test_repeated_corrections_still_resolve_to_the_last | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionAttributionIsTypeStrict.test_a_genuine_string_attribution_still_applies | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionAttributionIsTypeStrict.test_a_non_string_attribution_is_not_well_formed | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionAttributionIsTypeStrict.test_a_non_string_attribution_leaves_the_subject_live | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionAttributionIsTypeStrict.test_the_ledger_validator_refuses_the_same_rows | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_empty_attestor_fails_closed | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_empty_reason_fails_closed | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_empty_subject_reference_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_gz_validate_ledger_accepts_a_well_formed_correction | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_gz_validate_ledger_rejects_a_correction_missing_its_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_parses_through_the_typed_union | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_unknown_cause_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionEventFailsClosed.test_unknown_disposition_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_a_whitespace_attestor_makes_the_correction_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_an_empty_attestor_makes_the_correction_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_an_empty_reason_makes_the_correction_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_an_unknown_cause_makes_the_correction_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_an_unknown_disposition_makes_the_correction_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_the_factory_refuses_to_mint_an_invalid_correction | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestCorrectionsAreValidatedAtTheReplayBoundary.test_the_factory_still_mints_a_valid_correction | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestEveryGoverningConsumerReadsTheCorrectedStream.test_a_correction_is_never_an_artifacts_latest_event | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestEveryGoverningConsumerReadsTheCorrectedStream.test_a_discharged_blocker_reopens_the_trailer_channel | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestEveryGoverningConsumerReadsTheCorrectedStream.test_a_voided_gate_pass_stops_counting_as_a_pass | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestEveryGoverningConsumerReadsTheCorrectedStream.test_an_earlier_gate_result_resurfaces_when_the_later_one_is_voided | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestEveryGoverningConsumerReadsTheCorrectedStream.test_raw_history_stays_reachable_for_the_readers_that_need_it | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestFactoryProducesAValidRow.test_factory_round_trips_through_the_typed_union | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestInvalidCorrectionsCannotChangeDerivedState.test_a_valid_reinstatement_still_revives_it | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestInvalidCorrectionsCannotChangeDerivedState.test_no_invalid_reinstatement_revives_a_voided_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestInvalidCorrectionsCannotChangeDerivedState.test_no_invalid_void_removes_its_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestLedgerConsumers.test_a_later_legitimate_launch_still_counts | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestLedgerConsumers.test_a_sibling_blocker_is_untouched | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestLedgerConsumers.test_discharging_a_task_block_returns_the_task_to_in_progress | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestLedgerConsumers.test_history_is_preserved_by_read_history | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestLedgerConsumers.test_voiding_the_launch_returns_the_obpi_to_pending | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_a_correction_naming_an_unhashable_subject_is_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_an_unhashable_cause_is_inert_rather_than_fatal | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_an_unhashable_correction_is_inert_through_a_real_ledger | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_an_unhashable_disposition_is_inert_rather_than_fatal | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_an_unhashable_identity_validates_to_findings_not_an_exception | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestMalformedContainersAreRejectedNotFatal.test_the_tolerant_reader_survives_an_unhashable_identity | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_a_chain_resolves_by_last_correction_wins | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_a_correction_naming_a_correction_is_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_an_unresolvable_correction_nets_nothing | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_correction_rows_are_never_themselves_derived_state | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_discharged_leaves_the_evidentiary_reading_intact | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_reinstated_returns_the_row_to_both_readings | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_repeated_identical_corrections_are_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestNettingSemantics.test_void_is_dropped_from_both_readings | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsHelperBuiltPayloads.test_a_declared_helper_field_is_not_reported | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsHelperBuiltPayloads.test_a_helper_payload_merged_into_a_named_dict_is_scanned | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsHelperBuiltPayloads.test_a_helper_returned_payload_is_scanned | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsHelperBuiltPayloads.test_the_runtime_scan_over_this_repository_is_clean | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsTheRealAirlockProducer.test_removing_any_declaration_the_real_producer_writes_is_reported | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsTheRealAirlockProducer.test_the_declared_airlock_in_fields_are_the_ones_the_producer_writes | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerAuditReadsTheRealAirlockProducer.test_the_real_producer_is_clean_against_the_shipped_schema | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerContractParity.test_gz_validate_ledger_accepts_the_aborted_exit_row | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerContractParity.test_no_producer_writes_an_undeclared_field | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestProducerContractParity.test_the_aborted_airlock_exit_row_parses | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestRedParityConsumesCorrections.test_a_discharged_witness_is_still_evidence | red_parity | 0 | 28 |
| tests.test_ledger_corrections.TestRedParityConsumesCorrections.test_a_voided_witness_is_not_selected | red_parity | 0 | 28 |
| tests.test_ledger_corrections.TestSubjectIdentityIsTypeStrict.test_a_numeric_subject_id_does_not_match_a_string_artifact_id | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestSubjectIdentityIsTypeStrict.test_the_matching_string_subject_id_still_matches | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestSubjectResolution.test_an_unresolvable_reference_selects_nothing | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestSubjectResolution.test_resolves_the_named_row_only | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestSubjectResolution.test_same_id_different_ts_is_a_different_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheAirlockOverrideProducerIsDeclared.test_a_revoked_override_round_trips_as_revoked | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheAirlockOverrideProducerIsDeclared.test_the_emitted_row_passes_the_ledger_validator | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheAirlockOverrideProducerIsDeclared.test_the_emitted_row_replays_through_the_typed_union | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheAirlockOverrideProducerIsDeclared.test_the_payload_survives_the_round_trip_intact | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheAirlockOverrideProducerIsDeclared.test_the_producer_really_writes_the_three_override_fields | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheFactoryRefusesBlankAttribution.test_a_real_attribution_still_mints | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheFactoryRefusesBlankAttribution.test_a_whitespace_attestor_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheFactoryRefusesBlankAttribution.test_a_whitespace_reason_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTheFactoryRefusesBlankAttribution.test_a_whitespace_subject_reference_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestTypedAndRawShapesAgree.test_both_serialization_shapes_net_the_same | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidateLedgerEnforcesTheCommandsContract.test_a_correction_naming_another_correction_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidateLedgerEnforcesTheCommandsContract.test_a_correction_preceding_its_subject_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidateLedgerEnforcesTheCommandsContract.test_a_dangling_subject_reference_is_refused | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidateLedgerEnforcesTheCommandsContract.test_a_well_formed_correction_is_still_accepted | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidateLedgerEnforcesTheCommandsContract.test_the_validator_shares_the_replay_contract | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_a_correction_preceding_its_subject_is_reported_and_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_a_foreign_schema_tag_is_reported_and_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_a_legitimate_void_is_accepted_by_both_paths | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_a_reinstatement_preceding_its_subject_cannot_revive_it | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_a_reinstatement_restores_its_subject | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_an_empty_row_id_is_reported_and_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_an_equal_timestamp_inversion_is_reported_and_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_an_invalid_reinstatement_cannot_revive_a_voided_row | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_an_unparseable_timestamp_is_reported_and_inert | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_equal_timestamps_in_valid_order_are_accepted | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_intervening_work_between_subject_and_correction_is_untouched | red_parity | 0 | 0 |
| tests.test_ledger_corrections.TestValidationAndReplayRefuseTheSameCorrections.test_repeated_corrections_resolve_to_the_last | red_parity | 0 | 0 |
| tests.test_mutation_witness.TestActivation.test_a_mutant_that_cannot_import_is_invalid_never_a_kill | mutation_witness | 34 | 44 |
| tests.test_mutation_witness.TestActivation.test_a_no_op_mutation_is_invalid | mutation_witness | 33 | 43 |
| tests.test_mutation_witness.TestActivation.test_an_absent_target_is_invalid_never_a_kill | mutation_witness | 29 | 43 |
| tests.test_mutation_witness.TestBaseline.test_a_red_baseline_makes_every_mutation_inconclusive | mutation_witness | 7 | 44 |
| tests.test_mutation_witness.TestBehavioralFailure.test_full_test_identity_selects_semantic_failure | mutation_witness | 83 | 65 |
| tests.test_mutation_witness.TestBehavioralFailure.test_import_failure_and_mutant_skip_are_not_conclusive | mutation_witness | 56 | 57 |
| tests.test_mutation_witness.TestBehavioralFailure.test_missing_selector_does_not_prove_survival | mutation_witness | 24 | 56 |
| tests.test_mutation_witness.TestBehavioralFailure.test_named_runtime_error_does_not_kill_mutation | mutation_witness | 60 | 57 |
| tests.test_mutation_witness.TestBehavioralFailure.test_setup_assertion_is_not_a_behavioral_kill | mutation_witness | 20 | 55 |
| tests.test_mutation_witness.TestBehavioralFailure.test_source_bytes_are_restored_without_newline_translation | mutation_witness | 87 | 65 |
| tests.test_mutation_witness.TestBehavioralFailure.test_unknown_and_ambiguous_nominations_are_inconclusive | mutation_witness | 19 | 57 |
| tests.test_mutation_witness.TestBehavioralFailure.test_witness_reports_executed_ids_and_exact_source_digests | mutation_witness | 46 | 65 |
| tests.test_mutation_witness.TestBehavioralFailure.test_zero_and_skipped_baselines_do_not_grade_mutations | mutation_witness | 4 | 33 |
| tests.test_mutation_witness.TestDocumentedTestsAreObservable.test_a_documented_baseline_reads_green_and_still_yields_an_assertion_kill | mutation_witness | 96 | 64 |
| tests.test_mutation_witness.TestDocumentedTestsAreObservable.test_a_documented_skip_is_not_counted_as_executed | mutation_witness | 23 | 63 |
| tests.test_mutation_witness.TestFailureCause.test_a_kill_by_unrelated_tests_is_inconclusive | mutation_witness | 55 | 65 |
| tests.test_mutation_witness.TestFailureCause.test_a_kill_names_the_tests_that_failed | mutation_witness | 87 | 65 |
| tests.test_mutation_witness.TestFailureCause.test_a_surviving_mutation_is_reported_as_survived | mutation_witness | 74 | 54 |
| tests.test_mutation_witness.TestIsolation.test_each_mutation_runs_with_its_own_bytecode_cache | mutation_witness | 42 | 59 |
| tests.test_mutation_witness.TestIsolation.test_the_source_is_restored_after_the_sweep | mutation_witness | 0 | 43 |
| tests.test_mutation_witness.TestSweepReporting.test_the_summary_separates_run_verdicts_from_guard_verdicts | mutation_witness | 124 | 64 |
| tests.test_red_parity_audit.TestRedParity.test_assertion_witness_passes | red_parity | 15 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_brief_without_a_completion_receipt_is_out_of_scope | red_parity | 0 | 25 |
| tests.test_red_parity_audit.TestRedParity.test_failure_class_none_is_flagged_as_unfalsifiable | red_parity | 63 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_lite_lane_is_exempt | red_parity | 8 | 23 |
| tests.test_red_parity_audit.TestRedParity.test_non_terminal_brief_is_not_yet_gated | red_parity | 3 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_post_cutover_behavior_req_without_witness_is_flagged | red_parity | 48 | 26 |
| tests.test_red_parity_audit.TestRedParity.test_pre_cutover_completion_needs_no_witness | red_parity | 5 | 22 |
| tests.test_red_parity_audit.TestRedParity.test_structural_fence_req_is_exempt_by_proof_channel | red_parity | 4 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_support_req_is_exempt_by_proof_channel | red_parity | 4 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_untagged_req_defaults_to_behavior_and_is_gated | red_parity | 48 | 26 |
| tests.test_red_parity_audit.TestRedParity.test_weak_error_witness_passes | red_parity | 20 | 24 |
| tests.test_red_parity_audit.TestRedParity.test_witness_for_a_different_req_does_not_satisfy_this_one | red_parity | 48 | 26 |
| tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_a_void_rerun_cannot_erase_an_earlier_genuine_witness | red_parity | 14 | 24 |
| tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_a_void_rerun_cannot_erase_an_earlier_hollow_finding_either | red_parity | 72 | 24 |
| tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_an_assertion_on_a_reconstructed_base_does_satisfy_it | red_parity | 20 | 24 |
| tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_an_error_on_a_reconstructed_base_does_not_satisfy_the_gate | red_parity | 58 | 26 |
| tests.test_red_parity_audit.TestVoidWitnessesDoNotCount.test_an_error_with_no_provenance_still_satisfies_it | red_parity | 20 | 24 |
| tests.test_red_witness.TestChangedTestFiles.test_modified_test_file_is_detected | red_witness | 6 | 7 |
| tests.test_red_witness.TestChangedTestFiles.test_non_python_files_are_ignored | red_witness | 0 | 7 |
| tests.test_red_witness.TestChangedTestFiles.test_untracked_new_test_file_is_detected | red_witness | 6 | 7 |
| tests.test_red_witness.TestClassifyFailure.test_assertion_failure_is_strong_red | red_witness | 12 | 4 |
| tests.test_red_witness.TestClassifyFailure.test_error_is_weak_red | red_witness | 5 | 2 |
| tests.test_red_witness.TestClassifyFailure.test_errors_dominate_failures | red_witness | 10 | 2 |
| tests.test_red_witness.TestClassifyFailure.test_exit_zero_is_no_red | red_witness | 6 | 0 |
| tests.test_red_witness.TestClassifyFailure.test_nonzero_without_a_unittest_summary_is_an_error | red_witness | 5 | 2 |
| tests.test_red_witness.TestClassifyFailure.test_zero_failures_and_zero_errors_but_nonzero_exit_is_an_error | red_witness | 10 | 4 |
| tests.test_red_witness.TestErrorMeansDifferentThingsByProvenance.test_a_not_applicable_run_is_never_conclusive | red_witness | 18 | 0 |
| tests.test_red_witness.TestErrorMeansDifferentThingsByProvenance.test_an_assertion_is_a_strong_red_on_either_base | red_witness | 17 | 0 |
| tests.test_red_witness.TestErrorMeansDifferentThingsByProvenance.test_an_error_in_flight_is_a_weak_red | red_witness | 19 | 0 |
| tests.test_red_witness.TestErrorMeansDifferentThingsByProvenance.test_an_error_on_a_reconstructed_base_is_void_not_red | red_witness | 21 | 0 |
| tests.test_red_witness.TestLandedWorkStillWitnesses.test_a_hollow_test_is_still_caught_on_a_reconstructed_base | red_witness | 57 | 64 |
| tests.test_red_witness.TestLandedWorkStillWitnesses.test_a_landed_req_falls_back_to_the_reconstructed_base | red_witness | 51 | 67 |
| tests.test_red_witness.TestLandedWorkStillWitnesses.test_in_flight_work_still_uses_the_working_tree_base | red_witness | 22 | 71 |
| tests.test_red_witness.TestReconstructedPremiseIsRecheckedNotAssumed.test_a_test_only_commit_yields_no_verdict_rather_than_a_false_none | red_witness | 11 | 15 |
| tests.test_red_witness.TestResolveIntroducingBase.test_a_req_that_never_appears_resolves_to_nothing | red_witness | 0 | 3 |
| tests.test_red_witness.TestResolveIntroducingBase.test_an_introducing_root_commit_resolves_to_nothing | red_witness | 4 | 3 |
| tests.test_red_witness.TestResolveIntroducingBase.test_it_resolves_the_parent_of_the_introducing_commit | red_witness | 15 | 2 |
| tests.test_red_witness.TestRunRedWitness.test_changed_behavior_yields_a_strong_assertion_red | red_witness | 38 | 73 |
| tests.test_red_witness.TestRunRedWitness.test_new_symbol_yields_a_weak_error_red | red_witness | 22 | 71 |
| tests.test_red_witness.TestRunRedWitness.test_no_covering_tests_raises | red_witness | 2 | 0 |
| tests.test_red_witness.TestRunRedWitness.test_production_hunks_are_never_grafted | red_witness | 9 | 68 |
| tests.test_red_witness.TestRunRedWitness.test_test_that_passes_without_its_implementation_is_not_red | red_witness | 35 | 68 |
| tests.test_red_witness.TestRunRedWitness.test_witness_records_the_base_commit_it_ran_against | red_witness | 0 | 19 |
| tests.test_red_witness.TestRunRedWitness.test_worktree_is_removed_after_the_run | red_witness | 0 | 19 |
| tests.test_red_witness.TestUnrelatedDirtDoesNotFakeThePremise.test_a_landed_req_ignores_unrelated_dirt_and_reconstructs | red_witness | 48 | 69 |
| tests.test_red_witness.TestUnrelatedDirtDoesNotFakeThePremise.test_an_in_flight_req_whose_test_is_unlanded_still_uses_head | red_witness | 22 | 71 |
| tests.test_req_kind_fence_channel.TestCoversCmdPassesProjectRoot.test_covers_cmd_forwards_project_root_to_enricher | covers | 1 | 83 |
| tests.test_req_kind_fence_channel.TestFenceChannelHeadingButNoObpiAnchor.test_heading_present_but_no_obpi_anchor_is_unproven | covers | 0 | 0 |
| tests.test_req_kind_fence_channel.TestFenceChannelHeadingButNoObpiAnchor.test_obpi_anchor_present_is_pass | covers | 0 | 0 |
| tests.test_req_kind_fence_channel.TestFenceChannelNoAnchor.test_fence_no_anchor_is_unproven | covers | 0 | 0 |
| tests.test_req_kind_fence_channel.TestFenceChannelNoProjectRoot.test_fence_no_project_root_is_unproven | covers | 0 | 0 |
| tests.test_req_kind_fence_channel.TestFenceChannelWithAnchor.test_fence_with_anchor_is_proven | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestCoversCmdSurfacesMalformedCache.test_covers_cmd_raises_gz_cli_error_on_malformed_cache | covers | 1 | 73 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_hyphenated_fence_kind_round_trips | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_kind_value_case_is_normalised_not_rejected | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_kind_value_outside_the_taxonomy_raises | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_malformed_json_raises_instead_of_silently_emptying | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_missing_file_returns_empty_cache | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_non_string_kind_value_raises | covers | 0 | 0 |
| tests.test_req_kind_grandfathering_cache.TestLoadReqKindGrandfatheringCache.test_valid_json_returns_parsed_cache | covers | 0 | 0 |
| tests.test_test_shape.TestAdvisoryContract.test_by_disposition_rolls_up_the_dispositions | test_shape | 1 | 0 |
| tests.test_test_shape.TestAdvisoryContract.test_command_always_exits_zero | test_shape | 0 | 0 |
| tests.test_test_shape.TestCarveOutDeclaration.test_an_unrelated_class_name_does_not_declare | test_shape | 2 | 25 |
| tests.test_test_shape.TestCarveOutDeclaration.test_class_name_suffix_declares_the_carve_out | test_shape | 4 | 25 |
| tests.test_test_shape.TestCarveOutDeclaration.test_marker_outside_the_function_span_does_not_declare | test_shape | 3 | 25 |
| tests.test_test_shape.TestCarveOutDeclaration.test_output_contract_marker_declares_the_carve_out | test_shape | 8 | 25 |
| tests.test_test_shape.TestOutputAssertionDetection.test_assert_regex_is_flagged | test_shape | 5 | 27 |
| tests.test_test_shape.TestOutputAssertionDetection.test_assertion_on_result_output_is_flagged | test_shape | 20 | 13 |
| tests.test_test_shape.TestOutputAssertionDetection.test_assertion_without_output_source_is_not_flagged | test_shape | 8 | 11 |
| tests.test_test_shape.TestOutputAssertionDetection.test_fixture_methods_are_skipped | test_shape | 0 | 5 |
| tests.test_test_shape.TestOutputAssertionDetection.test_function_without_an_assertion_is_not_flagged | test_shape | 5 | 7 |
| tests.test_test_shape.TestOutputAssertionDetection.test_getvalue_is_flagged | test_shape | 1 | 27 |
| tests.test_test_shape.TestOutputAssertionDetection.test_non_test_files_are_not_scanned | test_shape | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_all_covered_returns_empty_uncovered | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_bdd_feature_tag_counts_as_coverage | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_coverage_does_not_block_audit | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_includes_per_obpi_data | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_invalid_adr_returns_empty | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_nonexistent_adr_returns_empty | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_returns_coverage_for_adr | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverage.test_uncovered_reqs_listed | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverageDocProofChannels.test_decision_doc_covers_doc_reqs_without_at_covers | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverageDocProofChannels.test_doc_req_without_any_proof_is_uncovered | covers | 0 | 0 |
| tests.test_traceability.TestComputeAdrCoverageDocProofChannels.test_product_proof_command_doc_covers_doc_reqs | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_covering_tests_listed | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_deterministic_computation | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_doc_kind_excluded_by_default | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_doc_kind_included_when_flag_set | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_empty_inputs | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_no_linkages | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_overall_coverage_percentage | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_per_adr_rollup | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_per_obpi_rollup | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_per_req_entries | covers | 0 | 0 |
| tests.test_traceability.TestComputeCoverage.test_report_is_pydantic_model | covers | 0 | 0 |
| tests.test_traceability.TestCoversCLIHelp.test_help_exits_zero | covers | 0 | 0 |
| tests.test_traceability.TestCoversCLIHelp.test_help_shows_description | covers | 0 | 0 |
| tests.test_traceability.TestCoversCLIHelp.test_help_shows_examples | covers | 0 | 0 |
| tests.test_traceability.TestCoversCLIOutput.test_exit_code_always_zero | covers | 50 | 0 |
| tests.test_traceability.TestCoversCLIOutput.test_filter_by_adr | covers | 4 | 41 |
| tests.test_traceability.TestCoversCLIOutput.test_filter_by_obpi | covers | 4 | 42 |
| tests.test_traceability.TestCoversCLIOutput.test_filter_nonexistent_adr_returns_empty | covers | 3 | 37 |
| tests.test_traceability.TestCoversCLIOutput.test_human_shows_summary | covers | 55 | 0 |
| tests.test_traceability.TestCoversCLIOutput.test_include_doc_flag_surfaces_doc_only_obpi | covers | 1 | 40 |
| tests.test_traceability.TestCoversCLIOutput.test_json_output_valid | covers | 39 | 1 |
| tests.test_traceability.TestCoversCLIOutput.test_json_shows_coverage_data | covers | 2 | 40 |
| tests.test_traceability.TestCoversCLIOutput.test_plain_one_record_per_line | covers | 45 | 0 |
| tests.test_traceability.TestCoversExistenceValidation.test_known_req_does_not_raise | covers | 0 | 0 |
| tests.test_traceability.TestCoversExistenceValidation.test_no_orphan_linkage_on_unknown | covers | 0 | 0 |
| tests.test_traceability.TestCoversExistenceValidation.test_unknown_req_raises_value_error | covers | 0 | 0 |
| tests.test_traceability.TestCoversFormatValidation.test_empty_string_raises_value_error | covers | 0 | 0 |
| tests.test_traceability.TestCoversFormatValidation.test_invalid_format_raises_value_error | covers | 0 | 0 |
| tests.test_traceability.TestCoversFormatValidation.test_obpi_format_raises_value_error | covers | 0 | 0 |
| tests.test_traceability.TestCoversFormatValidation.test_partial_format_raises_value_error | covers | 0 | 0 |
| tests.test_traceability.TestCoversFormatValidation.test_valid_req_format_accepted | covers | 0 | 0 |
| tests.test_traceability.TestCoversLinkageRegistration.test_linkage_record_structure | covers | 0 | 0 |
| tests.test_traceability.TestCoversLinkageRegistration.test_linkage_source_includes_file_info | covers | 0 | 0 |
| tests.test_traceability.TestCoversLinkageRegistration.test_multiple_covers_register_multiple_linkages | covers | 0 | 0 |
| tests.test_traceability.TestCoversLinkageRegistration.test_single_covers_registers_one_linkage | covers | 0 | 0 |
| tests.test_traceability.TestCoversMetadataOnly.test_arguments_passed_through | covers | 0 | 0 |
| tests.test_traceability.TestCoversMetadataOnly.test_function_identity_preserved | covers | 0 | 0 |
| tests.test_traceability.TestCoversMetadataOnly.test_return_value_preserved | covers | 0 | 0 |
| tests.test_traceability.TestCoversWithStandaloneFunction.test_standalone_function_registration | covers | 0 | 0 |
| tests.test_traceability.TestCoversWithTestCase.test_unittest_method_registration | covers | 0 | 0 |
| tests.test_traceability.TestExtractAdrSemver.test_adr_with_suffix | covers | 0 | 0 |
| tests.test_traceability.TestExtractAdrSemver.test_invalid_format_returns_none | covers | 0 | 0 |
| tests.test_traceability.TestExtractAdrSemver.test_pool_adr_returns_none | covers | 0 | 0 |
| tests.test_traceability.TestExtractAdrSemver.test_simple_adr_id | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_comment_form | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_decorator_double_quotes | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_decorator_single_quotes | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_decorator_with_space_before_paren | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_docstring_form | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_does_not_match_malformed_req | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_does_not_match_unrelated_decorator | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_empty_source | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_function_docstring_covers_reference_still_returned | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_module_docstring_covers_reference_still_returned | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_multiple_hits_track_line_numbers | covers | 0 | 0 |
| tests.test_traceability.TestFindCoversInSource.test_string_literal_fixture_content_is_not_returned_as_covers_hit | covers | 0 | 0 |
| tests.test_traceability.TestGlobalRegistry.test_get_registry_returns_copy | covers | 0 | 0 |
| tests.test_traceability.TestGlobalRegistry.test_registry_accumulates_across_decorators | covers | 0 | 0 |
| tests.test_traceability.TestGlobalRegistry.test_reset_clears_registry | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_compute_coverage_merges_unit_and_behave | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_feature_level_req_tag_attaches_to_feature | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_missing_directory_returns_empty | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_multiple_req_tags_on_one_scenario | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_scenario_level_req_tags_are_discovered | covers | 0 | 0 |
| tests.test_traceability.TestScanFeatureTree.test_untagged_scenarios_produce_no_records | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_captures_line_numbers | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_decorator_and_docstring_dedup_by_line | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_deterministic_output | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_discovers_annotations_across_files | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_discovers_class_method_annotations | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_empty_directory | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_multiple_covers_on_same_function | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_no_execution_of_test_files | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_picks_up_docstring_form_covers | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_scans_subdirectories | covers | 0 | 0 |
| tests.test_traceability.TestScanTestTree.test_skips_malformed_req | covers | 0 | 0 |

## Appendix D. Seeded sample manifest

```json
{
  "seed": 20260924,
  "sampling_frame_sha256": "6c3bb3d9fd670a46a1760f33e278d51fd57d1128ffdf8a9b4766acbcf602c5b9",
  "sample_replacement_seed": 20260925,
  "sampling_frame_final_sha256": "dff4af05bc2509adca57bccfcd1c22e61fcd8eb7d74c5e10d17ca31b4a7ad6b3",
  "sampling_frame_final_n": 10147
}
```

| # | Method receipt |
|---|---|
| 1 | [tests/chores/test_failure_class_index.py:212](/Users/jeff/Documents/Code/gzkit/tests/chores/test_failure_class_index.py:212) `TestSummary.test_rate_is_declaring_over_indexed_not_over_all_records` |
| 2 | [tests/test_review_protocol.py:515](/Users/jeff/Documents/Code/gzkit/tests/test_review_protocol.py:515) `TestReviewHasCriticalFindings.test_one_critical_finding_returns_true` |
| 3 | [tests/content/test_ownership.py:301](/Users/jeff/Documents/Code/gzkit/tests/content/test_ownership.py:301) `TestIterSectionBoundaries.test_empty_and_heading_free_documents_return_no_boundaries` |
| 4 | [tests/test_schemas.py:701](/Users/jeff/Documents/Code/gzkit/tests/test_schemas.py:701) `TestUnownedRatchetUpdatedOwningArm.test_the_schema_declares_every_owning_field_the_model_carries` |
| 5 | [tests/test_sunset_migrate.py:1522](/Users/jeff/Documents/Code/gzkit/tests/test_sunset_migrate.py:1522) `TestConcurrentApplyFailsClosed.test_a_second_apply_cannot_claim_an_existing_journal` |
| 6 | [tests/commands/test_content_unown.py:5842](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:5842) `TestEntryBoundarySweepIsNotClaimedAway.test_the_unknown_section_refusal_does_not_deny_the_sweep_that_preceded_it` |
| 7 | [tests/test_flag_registry.py:187](/Users/jeff/Documents/Code/gzkit/tests/test_flag_registry.py:187) `TestRealRegistry.test_real_registry_loads` |
| 8 | [tests/governance/test_pointer_integrity.py:248](/Users/jeff/Documents/Code/gzkit/tests/governance/test_pointer_integrity.py:248) `TestPointerResolvesRelativeToSource.test_root_surface_pointer_still_resolves` |
| 9 | [tests/skills/test_ghi_triage_deliverable.py:143](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_triage_deliverable.py:143) `TestRankInputStructuralSchema.test_action_field_rejected` |
| 10 | [tests/test_handoff_frontmatter_coherence.py:185](/Users/jeff/Documents/Code/gzkit/tests/test_handoff_frontmatter_coherence.py:185) `TestHandoffFrontmatterCoherence.test_shape_awareness_does_not_weaken_session_handoffs` |
| 11 | [tests/test_reporter.py:93](/Users/jeff/Documents/Code/gzkit/tests/test_reporter.py:93) `TestStatusTable.test_empty_state` |
| 12 | [tests/hooks/test_obpi_completion_commit_guard.py:170](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_obpi_completion_commit_guard.py:170) `TestGuardIsScopedToTheTransition.test_unrelated_file_is_ignored` |
| 13 | [tests/models/test_security_surface_entry.py:52](/Users/jeff/Documents/Code/gzkit/tests/models/test_security_surface_entry.py:52) `TestSecuritySurfaceEntryRejection.test_unknown_category_rejected` |
| 14 | [tests/test_handoff_cli.py:188](/Users/jeff/Documents/Code/gzkit/tests/test_handoff_cli.py:188) `TestHandoffResume.test_resume_json_classifies_ancient_handoff_as_very_stale` |
| 15 | [tests/test_req_kind_support_channel.py:143](/Users/jeff/Documents/Code/gzkit/tests/test_req_kind_support_channel.py:143) `TestSupportProofPathAware.test_path_cited_and_event_cites_path_passes` |
| 16 | [tests/governance/test_handoff_archive.py:476](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_archive.py:476) `ArchiveGuardUsesTheProductionResolverTests.test_bare_pointer_protects_target` |
| 17 | [tests/commands/test_content_unown.py:4130](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:4130) `TestRecoveryArtifactsAreIgnored.test_git_ignores_every_artifact_the_raise_path_writes` |
| 18 | [tests/governance/test_ledger_duplicate_rows.py:76](/Users/jeff/Documents/Code/gzkit/tests/governance/test_ledger_duplicate_rows.py:76) `TestDuplicateRowsAreDetected.test_a_repeated_row_is_reported` |
| 19 | [tests/governance/test_chore_metadata_authority.py:146](/Users/jeff/Documents/Code/gzkit/tests/governance/test_chore_metadata_authority.py:146) `TestCriteria.test_a_criterion_command_the_json_does_not_run_is_refused` |
| 20 | [tests/governance/test_ledger_ts_is_not_stated.py:164](/Users/jeff/Documents/Code/gzkit/tests/governance/test_ledger_ts_is_not_stated.py:164) `TestNoProductionConstructorStatesTs.test_every_allowlist_entry_carries_a_reason` |
| 21 | [tests/commands/test_chores_status.py:183](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_status.py:183) `TestGitSurfaceHistory.test_scan_record_change_reads_its_commit_or_its_uncommitted_edit` |
| 22 | [tests/commands/test_obpi_supersede_cmd.py:134](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_supersede_cmd.py:134) `TestObpiSupersedeHappyPath.test_valid_supersede_emits_one_event_with_both_ids` |
| 23 | [tests/test_templates.py:395](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:395) `TestTemplatesLayoutDualSurface.test_dual_surface_byte_parity` |
| 24 | [tests/skills/test_gz_complexity_distill.py:211](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:211) `TestOutputContract.test_output_contract_names_destination_artifact_directory` |
| 25 | [tests/test_lifecycle_auto_fix.py:76](/Users/jeff/Documents/Code/gzkit/tests/test_lifecycle_auto_fix.py:76) `TestAutoFixObpiBriefFrontmatter.test_terminal_withdrawn_status_not_clobbered_to_completed` |
| 26 | [tests/governance/test_transcribed_counts.py:129](/Users/jeff/Documents/Code/gzkit/tests/governance/test_transcribed_counts.py:129) `StructuralProgressFormsAreRefused.test_at_n_of_m_beside_an_adr_id_is_flagged` |
| 27 | [tests/commands/test_mx_enter.py:76](/Users/jeff/Documents/Code/gzkit/tests/commands/test_mx_enter.py:76) `TestMxEnterSetsMarkerAndEvent.test_enter_captures_inspection_scope_in_marker` |
| 28 | [tests/governance/test_handoff_validation.py:520](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:520) `TestValidateReferencedFiles.test_path_never_in_history_is_still_reported` |
| 29 | [tests/test_ledger_correction_consumers.py:124](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_correction_consumers.py:124) `DischargedLockReleaseStillProtectsItsHandoff.test_a_discharged_release_still_protects_the_handoff` |
| 30 | [tests/governance/test_deprecated_verb_prescription.py:49](/Users/jeff/Documents/Code/gzkit/tests/governance/test_deprecated_verb_prescription.py:49) `TestDeprecatedVerbPrescription.test_skill_prescribing_deprecated_verb_is_flagged` |
| 31 | [tests/test_persona_drift.py:126](/Users/jeff/Documents/Code/gzkit/tests/test_persona_drift.py:126) `TestGovernanceActivityProxy.test_fail_when_no_events` |
| 32 | [tests/test_ontology_corpus.py:207](/Users/jeff/Documents/Code/gzkit/tests/test_ontology_corpus.py:207) `TestCorpusRebuildFidelity.test_acceptance_factory_preserves_payload_and_refuses_unknown_record_kind` |
| 33 | [tests/test_ledger.py:1392](/Users/jeff/Documents/Code/gzkit/tests/test_ledger.py:1392) `TestHasAdrCreated.test_detects_direct_adr_created_event` |
| 34 | [tests/test_identity_surfaces.py:52](/Users/jeff/Documents/Code/gzkit/tests/test_identity_surfaces.py:52) `TestObpiId.test_parse_valid` |
| 35 | [tests/test_formatters.py:29](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:29) `TestOutputFormatterInit.test_all_valid_modes_accepted` |
| 36 | [tests/test_hooks.py:1445](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1445) `TestPipelineRouterHook.test_allows_silently_when_receipt_has_no_obpi` |
| 37 | [tests/governance/test_pointer_integrity.py:267](/Users/jeff/Documents/Code/gzkit/tests/governance/test_pointer_integrity.py:267) `TestBackPointerMustMatch.test_back_pointer_naming_a_different_source_is_rejected` |
| 38 | [tests/commands/test_complexity_advise.py:319](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_advise.py:319) `TestComplexityAdviseBehavior.test_directory_walks_python_files` |
| 39 | [tests/test_schemas.py:891](/Users/jeff/Documents/Code/gzkit/tests/test_schemas.py:891) `TestSkillSchemaAlignment.test_all_schema_properties_have_model_fields` |
| 40 | [tests/governance/test_adr_eval_truth_binding.py:166](/Users/jeff/Documents/Code/gzkit/tests/governance/test_adr_eval_truth_binding.py:166) `TestStructuralCompletenessNotSubstance.test_keyword_stuffing_does_not_manufacture_structure_dim2` |
| 41 | [tests/test_reviewer_agent.py:332](/Users/jeff/Documents/Code/gzkit/tests/test_reviewer_agent.py:332) `TestStoreReviewerAssessment.test_artifact_contains_docs_quality` |
| 42 | [tests/test_audit_pipeline.py:430](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:430) `TestAuditMdEvidenceLinks.test_closeout_form_listed_when_present` |
| 43 | [tests/test_triangle.py:79](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:79) `TestReqIdParsing.test_extra_fields_forbidden` |
| 44 | [tests/test_config_paths.py:403](/Users/jeff/Documents/Code/gzkit/tests/test_config_paths.py:403) `TestModuleDeclaredAuditSubjects.test_declaring_a_parent_does_not_exempt_its_children` |
| 45 | [tests/test_persona_loading.py:112](/Users/jeff/Documents/Code/gzkit/tests/test_persona_loading.py:112) `TestVendorFallback.test_unknown_vendor_returns_raw_markdown` |
| 46 | [tests/governance/test_operator_block_gate.py:74](/Users/jeff/Documents/Code/gzkit/tests/governance/test_operator_block_gate.py:74) `TestOperatorBlockGate.test_a_sibling_brief_is_not_blocked_by_this_ones_block` |
| 47 | [tests/governance/test_advisory_scorecard_summary.py:527](/Users/jeff/Documents/Code/gzkit/tests/governance/test_advisory_scorecard_summary.py:527) `MechanicalRowsCitingWitnessPaths.test_a_judgment_row_may_cite_a_missing_surface` |
| 48 | [tests/test_instruction_eval.py:103](/Users/jeff/Documents/Code/gzkit/tests/test_instruction_eval.py:103) `TestBaselineCases.test_unique_case_ids` |
| 49 | [tests/test_pipeline_integration.py:191](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_integration.py:191) `TestDispatchStatePersistence.test_load_no_marker_returns_empty` |
| 50 | [tests/test_sync.py:1259](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:1259) `TestSyncControlSurfaces.test_sync_claude_rules_skips_readme_and_non_instruction_files` |
| 51 | [tests/test_doc_coverage.py:406](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:406) `TestModels.test_report_passed_when_fully_covered` |
| 52 | [tests/test_persona_schema.py:90](/Users/jeff/Documents/Code/gzkit/tests/test_persona_schema.py:90) `TestNegativeCoverage.test_empty_traits_list` |
| 53 | [tests/governance/test_gate_caller_scope.py:71](/Users/jeff/Documents/Code/gzkit/tests/governance/test_gate_caller_scope.py:71) `TestUncalledGateFailsClosed.test_accepted_scope_is_not_flagged` |
| 54 | [tests/cli/test_validate_sensitivity_flag.py:100](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_sensitivity_flag.py:100) `TestSensitivityExplain.test_explain_accepts_comma_and_newline_separated` |
| 55 | [tests/test_obpi_lock_cmd.py:225](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:225) `TestLockManagerIO.test_reap_expired_locks_removes_expired` |
| 56 | [tests/governance/test_doc_code_citations.py:83](/Users/jeff/Documents/Code/gzkit/tests/governance/test_doc_code_citations.py:83) `DocCodeCitationBehavior.test_marked_item_is_exempt` |
| 57 | [tests/test_templates.py:39](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:39) `TestLoadTemplate.test_load_obpi_template` |
| 58 | [tests/governance/test_rendition_floor_coherence.py:148](/Users/jeff/Documents/Code/gzkit/tests/governance/test_rendition_floor_coherence.py:148) `TestFloorViolation.test_a_consumer_routed_for_another_content_type_is_not_graded_here` |
| 59 | [tests/test_core_lifecycle.py:81](/Users/jeff/Documents/Code/gzkit/tests/test_core_lifecycle.py:81) `TestCoreReExports.test_lifecycle_reexports_transition_tables` |
| 60 | [tests/commands/test_status.py:367](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:367) `TestStatusCommand.test_obpi_status_json_includes_runtime_fields` |
| 61 | [tests/complexity/test_baseline.py:125](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_baseline.py:125) `TestBaselineSchemaRejection.test_baseline_schema_rejects_unknown_field` |
| 62 | [tests/test_help_text_completeness.py:56](/Users/jeff/Documents/Code/gzkit/tests/test_help_text_completeness.py:56) `TestHelpTextCompleteness.test_all_arguments_have_help` |
| 63 | [tests/content/test_corpus_model.py:305](/Users/jeff/Documents/Code/gzkit/tests/content/test_corpus_model.py:305) `TestDerivationIdentity.test_every_field_is_classified` |
| 64 | [tests/commands/test_adr_demote.py:674](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:674) `TestAdrDemoteCommand.test_on_collision_fail_is_default` |
| 65 | [tests/chores/test_eval_feedback_cluster.py:198](/Users/jeff/Documents/Code/gzkit/tests/chores/test_eval_feedback_cluster.py:198) `TestEvalFeedbackCluster.test_walkthrough_template_text_is_not_confusion` |
| 66 | [tests/governance/test_standing_taxonomy_gate.py:105](/Users/jeff/Documents/Code/gzkit/tests/governance/test_standing_taxonomy_gate.py:105) `TestTaxonomyStepWiring.test_taxonomy_runner_propagates_failure` |
| 67 | [tests/test_codex_roles.py:207](/Users/jeff/Documents/Code/gzkit/tests/test_codex_roles.py:207) `TestCodexRoleSync.test_absent_registry_does_not_claim_native_roles` |
| 68 | [tests/governance/test_brief_path_validity.py:122](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_path_validity.py:122) `TestAllowedPathResolves.test_flag_token_treated_as_resolvable` |
| 69 | [tests/test_adr_eval.py:252](/Users/jeff/Documents/Code/gzkit/tests/test_adr_eval.py:252) `TestAdrDimensionScoring.test_all_eight_dimensions_scored` |
| 70 | [tests/test_rules.py:429](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:429) `TestRuleFrontmatter.test_extra_forbid` |
| 71 | [tests/test_verification_dispatch.py:467](/Users/jeff/Documents/Code/gzkit/tests/test_verification_dispatch.py:467) `TestAggregateVerificationResults.test_all_pass` |
| 72 | [tests/mx/test_levels.py:26](/Users/jeff/Documents/Code/gzkit/tests/mx/test_levels.py:26) `TestLadderReusesStdlib.test_ladder_rungs_equal_logging_constants` |
| 73 | [tests/test_sync_surfaces.py:42](/Users/jeff/Documents/Code/gzkit/tests/test_sync_surfaces.py:42) `TestAgentsPersonaSection.test_agents_persona_references_control_surface` |
| 74 | [tests/test_obpi_lock_cmd.py:826](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:826) `TestClaimReleaseSafetyPrimitives.test_claim_race_exactly_one_winner` |
| 75 | [tests/governance/test_covers_fence_scope.py:39](/Users/jeff/Documents/Code/gzkit/tests/governance/test_covers_fence_scope.py:39) `TestCoversFenceScope.test_shared_files_are_scoped_per_method_in_the_roster` |
| 76 | [tests/test_obpi_state_machine.py:160](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_state_machine.py:160) `TestSchemaCoherence.test_committed_schema_equals_model_projection` |
| 77 | [tests/governance/test_deprecated_verb_prescription.py:75](/Users/jeff/Documents/Code/gzkit/tests/governance/test_deprecated_verb_prescription.py:75) `TestDeprecatedVerbPrescription.test_escape_marker_suppresses_the_finding` |
| 78 | [tests/test_acceptance.py:383](/Users/jeff/Documents/Code/gzkit/tests/test_acceptance.py:383) `TestAcceptance.test_missing_proof_review_does_not_allow_unexplained_empty_scope` |
| 79 | [tests/commands/test_content_unown.py:2177](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2177) `TestSurfaceWriteScanner.test_a_json_target_is_exempt_even_when_the_name_contains_md` |
| 80 | [tests/test_product_proof.py:530](/Users/jeff/Documents/Code/gzkit/tests/test_product_proof.py:530) `TestObpiProofStatus.test_has_proof_command_doc` |
| 81 | [tests/governance/test_stage4_evidence.py:130](/Users/jeff/Documents/Code/gzkit/tests/governance/test_stage4_evidence.py:130) `TestExtractDemoCommandsMultiLine.test_interior_blank_line_is_preserved` |
| 82 | [tests/test_adr_audit_ledger_confirm.py:42](/Users/jeff/Documents/Code/gzkit/tests/test_adr_audit_ledger_confirm.py:42) `TestAuditLedgerSurfaceExists.test_confirm_decision_no_absorption_needed` |
| 83 | [tests/test_sync.py:841](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:841) `TestSyncControlSurfaces.test_canonical_sync_preflight_allows_unknown_metadata_keys` |
| 84 | [tests/cli/test_justify_manpage.py:114](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:114) `GzJustifyManpageContract.test_options_section_names_every_cli_flag` |
| 85 | [tests/commands/test_sync_cmds.py:909](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:909) `TestDetectStrandedCommitMessage.test_returns_none_when_editmsg_subject_matches_head` |
| 86 | [tests/test_validate.py:120](/Users/jeff/Documents/Code/gzkit/tests/test_validate.py:120) `TestValidateDocument.test_missing_file` |
| 87 | [tests/governance/test_handoff_ruling_store.py:266](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_ruling_store.py:266) `HandoffCarriesPointerNotCorpusTests.test_pointer_section_is_not_parsed_back_as_a_ruling` |
| 88 | [tests/test_obpi_lock_cmd.py:520](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:520) `TestLockRelease.test_release_not_found` |
| 89 | [tests/governance/test_surface_weight.py:271](/Users/jeff/Documents/Code/gzkit/tests/governance/test_surface_weight.py:271) `TestRedBand.test_red_band_exits_3_even_with_active_waiver` |
| 90 | [tests/test_cli_parser.py:117](/Users/jeff/Documents/Code/gzkit/tests/test_cli_parser.py:117) `TestNoHyphenBreaksFormatter.test_split_lines_preserves_hyphenated_tokens` |
| 91 | [tests/skills/test_router_coverage_completion.py:134](/Users/jeff/Documents/Code/gzkit/tests/skills/test_router_coverage_completion.py:134) `TestLiveCanonicalRouterTablesClean.test_audit_router_tables_returns_zero_errors_against_live_canonical` |
| 92 | [tests/test_persona_schema.py:226](/Users/jeff/Documents/Code/gzkit/tests/test_persona_schema.py:226) `TestExemplarValidation.test_exemplar_implementer_validates` |
| 93 | [tests/adr/test_patch_release.py:708](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:708) `TestClassifyGhi.test_diff_only_warning_text` |
| 94 | [tests/content/test_ownership.py:2120](/Users/jeff/Documents/Code/gzkit/tests/content/test_ownership.py:2120) `TestWindowsDirectoryBarrier.test_pending_flush_waits_then_checks_the_completion_status` |
| 95 | [tests/governance/test_retire_ln_surface.py:90](/Users/jeff/Documents/Code/gzkit/tests/governance/test_retire_ln_surface.py:90) `TestRetireLnSurface.test_ln_field_forbidden_on_brief_structure` |
| 96 | [tests/cli/test_validate_evaluation_justify_binding_exit.py:96](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_evaluation_justify_binding_exit.py:96) `TestSoloHandlerExitCodeContract.test_solo_handler_exits_0_when_clean` |
| 97 | [tests/commands/test_reference_checker.py:575](/Users/jeff/Documents/Code/gzkit/tests/commands/test_reference_checker.py:575) `TestCitationsResolveThroughPrefixesTheProseActuallyWrites.test_a_unique_adr_prefix_resolves` |
| 98 | [tests/governance/test_rename_fold.py:93](/Users/jeff/Documents/Code/gzkit/tests/governance/test_rename_fold.py:93) `RenameChainTargetUsesTheFold.test_it_reads_the_nested_event_shape_too` |
| 99 | [tests/test_triangle.py:993](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:993) `TestScanCoversReferences.test_scan_skips_non_python_files` |
| 100 | [tests/governance/test_closeout_proof_view.py:598](/Users/jeff/Documents/Code/gzkit/tests/governance/test_closeout_proof_view.py:598) `TestCloseoutProofExemptions.test_non_exempt_uncovered_req_still_flagged` |
| 101 | [tests/commands/test_sync_cmds.py:626](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:626) `TestSyncCommand.test_agent_sync_dry_run_does_not_mutate_disk` |
| 102 | [tests/test_pipeline_dispatch.py:912](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_dispatch.py:912) `TestPrepareStage3Verification.test_empty_brief_returns_sequential` |
| 103 | [tests/content/models/test_fields.py:132](/Users/jeff/Documents/Code/gzkit/tests/content/models/test_fields.py:132) `TestSemanticStructureValidators.test_handoff_session_id_rejects_empty` |
| 104 | [tests/commands/test_content_unown.py:6036](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6036) `TestUnavailableBarrierPreservesRecoveryMaterial.test_a_transient_barrier_fault_still_refuses_and_offers_a_reachable_remedy` |
| 105 | [tests/test_validate.py:309](/Users/jeff/Documents/Code/gzkit/tests/test_validate.py:309) `TestValidateDocument.test_checklist_tick_is_rejected` |
| 106 | [tests/test_roles.py:41](/Users/jeff/Documents/Code/gzkit/tests/test_roles.py:41) `TestRoleTaxonomy.test_each_role_has_artifacts` |
| 107 | [tests/commands/test_adr_promote.py:87](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:87) `TestAdrPromoteCommand.test_adr_promote_writes_files_and_ledger_rename` |
| 108 | [tests/governance/test_session_green_gate_delivery_control.py:28](/Users/jeff/Documents/Code/gzkit/tests/governance/test_session_green_gate_delivery_control.py:28) `SessionGreenGateDeliveryControlTests.test_the_population_is_every_hook_type_the_project_declares` |
| 109 | [tests/mx/test_disposition.py:80](/Users/jeff/Documents/Code/gzkit/tests/mx/test_disposition.py:80) `TestUnderMarkerDemotion.test_gate5_invariant_pins_critical_route` |
| 110 | [tests/commands/test_justify_cmd.py:143](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:143) `TestHappyPaths.test_save_writes_artifacts_justify_auto_path` |
| 111 | [tests/commands/test_complexity_advise_attest_intrinsic.py:268](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_advise_attest_intrinsic.py:268) `TestComplexityAdviseAttestIntrinsic.test_attest_intrinsic_refuses_headless_invocation` |
| 112 | [tests/test_persona_composition.py:166](/Users/jeff/Documents/Code/gzkit/tests/test_persona_composition.py:166) `TestVendorPersonaTrailingNewline.test_registered_vendor_renders_end_with_single_newline` |
| 113 | [tests/commands/test_ontology.py:424](/Users/jeff/Documents/Code/gzkit/tests/commands/test_ontology.py:424) `TestUnifiedFidelityConfession.test_present_source_with_unparseable_unit_confesses_incomplete` |
| 114 | [tests/governance/test_config_derivation.py:237](/Users/jeff/Documents/Code/gzkit/tests/governance/test_config_derivation.py:237) `DirectDataReachIsRostered.test_rostered_module_is_permitted` |
| 115 | [tests/test_templates.py:164](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:164) `TestAgentsTemplateSemantic.test_pipeline_runtime_is_canonical` |
| 116 | [tests/governance/test_invariant_witness.py:140](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_witness.py:140) `TestInvariantWitnessScopeIsReachable.test_registered_runner_fails_closed_on_a_vapor_witness` |
| 117 | [tests/test_skill_naming.py:36](/Users/jeff/Documents/Code/gzkit/tests/test_skill_naming.py:36) `TestSkillNaming.test_skill_dirs_and_frontmatter_names_are_kebab_case` |
| 118 | [tests/governance/test_behave_sharding.py:109](/Users/jeff/Documents/Code/gzkit/tests/governance/test_behave_sharding.py:109) `TestShardPlanner.test_no_shard_is_empty_when_files_outnumber_shards` |
| 119 | [tests/commands/test_status.py:1477](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1477) `TestLifecycleStatusSemantics.test_adr_status_legacy_semver_id_still_resolves` |
| 120 | [tests/commands/test_obpi_complete_reconcile_gate.py:472](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_complete_reconcile_gate.py:472) `TestReconcileGateEscapeHatchEmitsEvent.test_escape_hatch_universal_across_lanes` |
| 121 | [tests/test_product_proof.py:116](/Users/jeff/Documents/Code/gzkit/tests/test_product_proof.py:116) `TestCheckCommandDocProof.test_existing_doc_with_content` |
| 122 | [tests/test_templates.py:348](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:348) `TestObpiTemplateDemoSection.test_template_includes_demo_section_heading` |
| 123 | [tests/commands/test_content_unown.py:6529](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6529) `TestDeclarationRolledBackUnderAPendingJournal.test_replaying_a_planted_journal_cannot_make_the_stale_state_authoritative` |
| 124 | [tests/test_persona_loading.py:41](/Users/jeff/Documents/Code/gzkit/tests/test_persona_loading.py:41) `TestRenderPersonaClaude.test_contains_traits_as_behavioral_instructions` |
| 125 | [tests/governance/test_reconcile_freshness.py:129](/Users/jeff/Documents/Code/gzkit/tests/governance/test_reconcile_freshness.py:129) `TestIsReceiptFresh.test_glob_pattern_expands_correctly` |
| 126 | [tests/arb/test_unittest_runner_lockstep.py:268](/Users/jeff/Documents/Code/gzkit/tests/arb/test_unittest_runner_lockstep.py:268) `TestPipelineBaselineMatchesCanon.test_stage3_unittest_step_runs_the_canonical_argv` |
| 127 | [tests/mx/test_marker.py:77](/Users/jeff/Documents/Code/gzkit/tests/mx/test_marker.py:77) `TestMarkerPresence.test_marker_module_imports_no_gzkit_internals` |
| 128 | [tests/test_obpi_prefix_match.py:69](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_prefix_match.py:69) `TestResolveObpiSymmetricExpansion.test_short_form_brief_id_matches_full_slug_graph` |
| 129 | [tests/test_adr_eval_dispatch.py:160](/Users/jeff/Documents/Code/gzkit/tests/test_adr_eval_dispatch.py:160) `TestDispatchChannel.test_partial_dispatch_is_still_single_driver` |
| 130 | [tests/commands/test_sync_cmds.py:811](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:811) `TestBuildSyncCommitMessage.test_empty_sync_carries_ceremony_trailer` |
| 131 | [tests/test_identity_surfaces.py:137](/Users/jeff/Documents/Code/gzkit/tests/test_identity_surfaces.py:137) `TestEvidenceId.test_roundtrip` |
| 132 | [tests/test_formatters.py:205](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:205) `TestQuietMode.test_print_with_err_flag_outputs` |
| 133 | [tests/test_formatters.py:346](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:346) `TestModeFromFlags.test_quiet_flag` |
| 134 | [tests/test_adversarial_validation_gate.py:559](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:559) `TestReceiptProvesCrossVendorFromArgv.test_a_vendor_named_only_in_the_prompt_does_not_prove_cross_vendor` |
| 135 | [tests/scripts/test_session_orientation.py:861](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_session_orientation.py:861) `TestCollectObpiLocks.test_expired_lock_is_reaped_with_audit_trail` |
| 136 | [tests/validators/test_unscoped_rules.py:67](/Users/jeff/Documents/Code/gzkit/tests/validators/test_unscoped_rules.py:67) `TestUnscopedAllowlistEntryModel.test_tracking_ref_pattern_enforced` |
| 137 | [tests/test_obpi_validator.py:247](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_validator.py:247) `TestObpiValidator.test_validate_heavy_completed_valid_attestation` |
| 138 | [tests/eval/test_regression.py:267](/Users/jeff/Documents/Code/gzkit/tests/eval/test_regression.py:267) `TestFirstRunHandling.test_no_baseline_reports_no_prior` |
| 139 | [tests/test_hooks_guards.py:184](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:184) `TestScanFileSpecialCases.test_requirements_dev_txt_flagged` |
| 140 | [tests/commands/test_content_unown.py:6386](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6386) `TestDeclarationRolledBackUnderAPendingJournal.test_a_blank_attestation_authorizes_nothing_and_keeps_its_own_exit` |
| 141 | [tests/test_adversarial_validation_gate.py:356](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:356) `TestGateIsWiredIntoCompletion.test_obpi_complete_cmd_invokes_the_gate_before_writing` |
| 142 | [tests/governance/test_token_block_discipline.py:177](/Users/jeff/Documents/Code/gzkit/tests/governance/test_token_block_discipline.py:177) `TestDegenerateHandoffWriter.test_release_abandon_rejects_unregistered_category` |
| 143 | [tests/governance/test_foundation_invariance_skill_enrichment.py:61](/Users/jeff/Documents/Code/gzkit/tests/governance/test_foundation_invariance_skill_enrichment.py:61) `TestSkillInvarianceTestEnrichment.test_gz_adr_create_has_invariance_test` |
| 144 | [tests/governance/test_pointer_integrity.py:60](/Users/jeff/Documents/Code/gzkit/tests/governance/test_pointer_integrity.py:60) `TestPointerResolves.test_resolved_pointer_with_backpointer_is_clean` |
| 145 | [tests/knowledge/test_active_campaign_resolution.py:97](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_active_campaign_resolution.py:97) `TestResolverSelection.test_a_registry_naming_a_missing_plan_falls_back` |
| 146 | [tests/complexity/advisor/test_timeout.py:159](/Users/jeff/Documents/Code/gzkit/tests/complexity/advisor/test_timeout.py:159) `TestAdvisorConfig.test_default_timeout_30s` |
| 147 | [tests/test_ledger.py:153](/Users/jeff/Documents/Code/gzkit/tests/test_ledger.py:153) `TestEventFactories.test_obpi_created_event` |
| 148 | [tests/content/test_round_trip_agent_contract.py:106](/Users/jeff/Documents/Code/gzkit/tests/content/test_round_trip_agent_contract.py:106) `TestReconcileInvariant.test_reconcile_bullet_round_trips_via_model_dump` |
| 149 | [tests/commands/test_preflight.py:22](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:22) `TestPreflightCommand.test_detects_stale_pipeline_marker` |
| 150 | [tests/content/test_tui_affordances.py:102](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:102) `TestTableRendererTUI.test_list_non_tty_produces_no_ansi` |
| 151 | [tests/test_obpi_skill_migration.py:48](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_skill_migration.py:48) `TestPipelineStage1LockClaim.test_pipeline_references_gz_obpi_lock_claim` |
| 152 | [tests/test_surface_write_idempotence.py:282](/Users/jeff/Documents/Code/gzkit/tests/test_surface_write_idempotence.py:282) `HookStagingOrderTest.test_claude_hooks_second_sync_writes_nothing` |
| 153 | [tests/commands/test_obpi_precomplete.py:556](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_precomplete.py:556) `TestPrecompleteCliEndToEnd.test_json_output_shape` |
| 154 | [tests/governance/test_handoff_validation.py:353](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:353) `TestValidatePlaceholders.test_ignores_placeholders_in_html_comments` |
| 155 | [tests/test_formatters.py:155](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:155) `TestJsonMode.test_err_goes_to_stderr_in_json_mode` |
| 156 | [tests/test_skills_audit.py:273](/Users/jeff/Documents/Code/gzkit/tests/test_skills_audit.py:273) `TestSkillAuditMirrorContracts.test_stale_mirror_directory_is_non_blocking_warning` |
| 157 | [tests/governance/test_qc_binding_scope.py:184](/Users/jeff/Documents/Code/gzkit/tests/governance/test_qc_binding_scope.py:184) `TestExitCodeBehavior.test_audit_qc_binding_clean_when_all_bound_steps_wired` |
| 158 | [tests/governance/test_settings_local_vault_outside_repo.py:77](/Users/jeff/Documents/Code/gzkit/tests/governance/test_settings_local_vault_outside_repo.py:77) `SettingsLocalVaultTests.test_distinct_roots_do_not_share_a_vault` |
| 159 | [tests/test_codex_roles.py:37](/Users/jeff/Documents/Code/gzkit/tests/test_codex_roles.py:37) `TestShippedRoleRendering.test_rendering_canon_into_shipped_toml_is_a_no_op` |
| 160 | [tests/governance/test_task_envelope_coherence.py:1625](/Users/jeff/Documents/Code/gzkit/tests/governance/test_task_envelope_coherence.py:1625) `TestDiagnoseDriftAgreesWithTheValidator.test_a_nested_subset_is_not_drift_in_either_consumer` |
| 161 | [tests/governance/test_adr_status_index.py:172](/Users/jeff/Documents/Code/gzkit/tests/governance/test_adr_status_index.py:172) `ComputeDriftTests.test_fresh_index_has_no_drift` |
| 162 | [tests/chores/test_failure_class_index.py:237](/Users/jeff/Documents/Code/gzkit/tests/chores/test_failure_class_index.py:237) `TestFailSoft.test_malformed_snapshot_yields_empty_corpus` |
| 163 | [tests/chores/test_session_correction_mining.py:198](/Users/jeff/Documents/Code/gzkit/tests/chores/test_session_correction_mining.py:198) `TestScrubbing.test_scrub_caps_quote_to_one_line` |
| 164 | [tests/test_sync.py:976](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:976) `TestSyncControlSurfaces.test_collect_skills_catalog_reads_category_from_frontmatter` |
| 165 | [tests/chores/test_eval_feedback_cluster.py:265](/Users/jeff/Documents/Code/gzkit/tests/chores/test_eval_feedback_cluster.py:265) `TestEvalFeedbackCluster.test_idempotent_rerun` |
| 166 | [tests/content/test_corpus_model.py:700](/Users/jeff/Documents/Code/gzkit/tests/content/test_corpus_model.py:700) `TestEffectiveCorpusUnRetirement.test_a_fourth_row_can_retire_the_restored_entry_again` |
| 167 | [tests/test_verification_dispatch.py:212](/Users/jeff/Documents/Code/gzkit/tests/test_verification_dispatch.py:212) `TestPartitionIndependentGroups.test_no_overlaps_all_independent` |
| 168 | [tests/test_sync.py:378](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:378) `TestExtractArtifactId.test_extract_adr_id` |
| 169 | [tests/governance/test_brief_path_validity_wiring.py:25](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_path_validity_wiring.py:25) `TestRelativeMirrorPaths.test_brief_and_plan_creates_cannot_exempt_relative_mirrors` |
| 170 | [tests/commands/test_runtime.py:893](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:893) `TestAdrRuntimeCommands.test_obpi_emit_receipt_lite_obpi_under_heavy_parent_requires_human_attestation` |
| 171 | [tests/test_tasks.py:781](/Users/jeff/Documents/Code/gzkit/tests/test_tasks.py:781) `TestResolveTaskChain.test_resolve_chain_different_ids` |
| 172 | [tests/governance/test_task_envelope_coherence.py:2155](/Users/jeff/Documents/Code/gzkit/tests/governance/test_task_envelope_coherence.py:2155) `TestSignatureE.test_composite_includes_signature_e` |
| 173 | [tests/test_adr_eval_dispatch.py:102](/Users/jeff/Documents/Code/gzkit/tests/test_adr_eval_dispatch.py:102) `TestDispatchIsNeverInferred.test_dispatch_without_a_receipt_id_does_not_credit` |
| 174 | [tests/test_core_exceptions.py:69](/Users/jeff/Documents/Code/gzkit/tests/test_core_exceptions.py:69) `TestExceptionUsability.test_gz_error_message` |
| 175 | [tests/governance/test_promoted_advisory_audits.py:615](/Users/jeff/Documents/Code/gzkit/tests/governance/test_promoted_advisory_audits.py:615) `BriefCrossReferencesAuditNegativeCases.test_skip_marker_suppresses` |
| 176 | [tests/test_formatters.py:34](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:34) `TestOutputFormatterInit.test_invalid_mode_raises_value_error` |
| 177 | [tests/commands/test_context_cmd.py:328](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:328) `TestContextCmdSlim.test_slim_delta_is_only_governance_section` |
| 178 | [tests/governance/test_adr_eval_truth_binding.py:141](/Users/jeff/Documents/Code/gzkit/tests/governance/test_adr_eval_truth_binding.py:141) `TestStructuralCompletenessNotSubstance.test_structurally_complete_intent_scores_high` |
| 179 | [tests/governance/test_bullet_retention.py:473](/Users/jeff/Documents/Code/gzkit/tests/governance/test_bullet_retention.py:473) `TestInvariantTierVerbatimContract.test_unknown_tier_falls_back_to_invariant_verbatim` |
| 180 | [tests/governance/test_exemplar_corpus.py:214](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:214) `TestPoolStubExistence.test_each_pool_stub_cites_obpi_02_as_booking_event` |
| 181 | [tests/scripts/test_session_orientation.py:1301](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_session_orientation.py:1301) `TestExitBookmarkSensemakingSection.test_nothing_renders_when_there_is_nothing_to_say` |
| 182 | [tests/governance/test_brief_path_validity.py:129](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_path_validity.py:129) `TestExtractAllowedPaths.test_extracts_backtick_tokens_from_bullets` |
| 183 | [tests/test_lock_manager.py:186](/Users/jeff/Documents/Code/gzkit/tests/test_lock_manager.py:186) `TestResolveAgent.test_fallback_unknown` |
| 184 | [tests/test_doc_coverage.py:279](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:279) `TestCheckSurfaces.test_governance_runbook_reference` |
| 185 | [tests/test_review_protocol.py:440](/Users/jeff/Documents/Code/gzkit/tests/test_review_protocol.py:440) `TestParseReviewResult.test_no_json_block_returns_none` |
| 186 | [tests/test_sync.py:946](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:946) `TestSyncControlSurfaces.test_canonical_sync_preflight_blocks_unsupported_transition` |
| 187 | [tests/governance/test_enforcement_meta_validator.py:98](/Users/jeff/Documents/Code/gzkit/tests/governance/test_enforcement_meta_validator.py:98) `TestRunSingleClaim.test_pass_when_entrypoint_returns_truthy_list` |
| 188 | [tests/commands/test_init_update.py:150](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:150) `TestCanonicalVersionMarkerContract.test_marker_pattern_rejects_rule_version_body_marker` |
| 189 | [tests/test_foundation_triage_rubric.py:293](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_rubric.py:293) `TestJsonSchema.test_schema_file_exists` |
| 190 | [tests/governance/test_gate_caller_scope.py:95](/Users/jeff/Documents/Code/gzkit/tests/governance/test_gate_caller_scope.py:95) `TestGzCheckHalfIsDelegated.test_unreadable_membership_fails_closed` |
| 191 | [tests/commands/test_justify_cmd.py:172](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:172) `TestHappyPaths.test_related_passed_through_as_list` |
| 192 | [tests/governance/test_task_envelope_coherence.py:1313](/Users/jeff/Documents/Code/gzkit/tests/governance/test_task_envelope_coherence.py:1313) `TestSignatureD.test_consistent_obpi_id_passes` |
| 193 | [tests/hooks/test_formatter_failure_visibility.py:136](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_formatter_failure_visibility.py:136) `TestFormatterFailureIsObservable.test_an_absent_directory_is_not_a_failure` |
| 194 | [tests/governance/test_drift_proof_channel_scope.py:110](/Users/jeff/Documents/Code/gzkit/tests/governance/test_drift_proof_channel_scope.py:110) `TestTerminalBriefScoping.test_terminal_status_match_tolerates_corpus_spelling` |
| 195 | [tests/commands/test_skills.py:145](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:145) `TestSkillCommands.test_skill_list` |
| 196 | [tests/test_tasks.py:433](/Users/jeff/Documents/Code/gzkit/tests/test_tasks.py:433) `TestTaskBlockedEvent.test_discriminated_union_parses_task_blocked` |
| 197 | [tests/test_obpi_validator.py:909](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_validator.py:909) `TestShouldUseSealedScope.test_repudiated_with_sealed_evidence_uses_sealed` |
| 198 | [tests/skills/test_ghi_triage_deliverable.py:329](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_triage_deliverable.py:329) `TestFamilySignalIsCandidateEvidence.test_silence_is_not_evidence_of_non_membership` |
| 199 | [tests/test_doc_coverage.py:166](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:166) `TestDiscoverCommands.test_extracts_handler_names` |
| 200 | [tests/justify/test_walkthrough.py:273](/Users/jeff/Documents/Code/gzkit/tests/justify/test_walkthrough.py:273) `TestRenderScaffold.test_builds_eight_sections_with_placeholders` |
| 201 | [tests/test_ledger.py:883](/Users/jeff/Documents/Code/gzkit/tests/test_ledger.py:883) `TestLedger.test_normalize_req_proof_inputs_preserves_scope_and_gap_reason` |
| 202 | [tests/governance/test_brief_path_validity_wiring.py:168](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_path_validity_wiring.py:168) `TestAdrPromoteCheckScaffoldObpisPathValidity.test_brief_creates_marker_exempts_net_new_in_promotion` |
| 203 | [tests/governance/test_closeout_proof_view.py:477](/Users/jeff/Documents/Code/gzkit/tests/governance/test_closeout_proof_view.py:477) `TestCloseoutProofSupportGrandfatherMalformed.test_malformed_grandfather_file_reported_not_raised` |
| 204 | [tests/governance/test_frontmatter_coherence.py:387](/Users/jeff/Documents/Code/gzkit/tests/governance/test_frontmatter_coherence.py:387) `ReconciliationLogicTests.test_partial_failure_receipt_shows_completed_entries` |
| 205 | [tests/test_report_publication.py:39](/Users/jeff/Documents/Code/gzkit/tests/test_report_publication.py:39) `TestReportPublication.test_rotation_retains_prior_report_and_links_predecessor` |
| 206 | [tests/commands/test_obpi_complete_coverage_gate.py:946](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_complete_coverage_gate.py:946) `TestEnforceUncoveredAcceptanceConfirmationOperatorVerbatim.test_headless_no_attestor_present_returns_operator_verbatim` |
| 207 | [tests/test_quality.py:692](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:692) `TestModuleSizeInCheckPipeline.test_self_test_failure_short_circuits_before_the_band_run` |
| 208 | [tests/test_codex_config_surface.py:213](/Users/jeff/Documents/Code/gzkit/tests/test_codex_config_surface.py:213) `TestCodexConfigGeneration.test_sync_writes_codex_config_lf_byte_identical_to_render` |
| 209 | [tests/adr/test_patch_release.py:620](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:620) `TestGhiHasSrcCommits.test_commits_touching_src` |
| 210 | [tests/test_product_proof.py:234](/Users/jeff/Documents/Code/gzkit/tests/test_product_proof.py:234) `TestCheckGovernanceArtifactProof.test_existing_artifact_with_content` |
| 211 | [tests/governance/test_security_surfaces_registry.py:131](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:131) `TestRegistryContents.test_governance_readme_exists` |
| 212 | [tests/test_ledger.py:2002](/Users/jeff/Documents/Code/gzkit/tests/test_ledger.py:2002) `ParseFrontmatterValueBomTolerance.test_leading_bom_does_not_hide_the_block` |
| 213 | [tests/commands/test_content_commit.py:154](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:154) `TestContentCommitCmd.test_commit_fails_closed_on_absent_candidate` |
| 214 | [tests/eval/test_regression.py:237](/Users/jeff/Documents/Code/gzkit/tests/eval/test_regression.py:237) `TestComparisonEngine.test_report_model_forbids_extra` |
| 215 | [tests/knowledge/test_concept_frontmatter_model.py:82](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_concept_frontmatter_model.py:82) `TestConceptFrontmatterModel.test_json_schema_mirror_loads_and_matches_posture` |
| 216 | [tests/test_obpi_lock_cmd.py:133](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:133) `TestLockDataModel.test_rejects_extra_fields` |
| 217 | [tests/test_agent_sync.py:152](/Users/jeff/Documents/Code/gzkit/tests/test_agent_sync.py:152) `TestRenderRulesToDir.test_copilot_rendering_writes_files` |
| 218 | [tests/commands/test_adr_audit_covers_scope.py:45](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_audit_covers_scope.py:45) `TestCoversLocationCollectionExcludesWithdrawnObpis.test_empty_active_set_is_noop_backward_compatible` |
| 219 | [tests/governance/test_surface_delivery_witness.py:189](/Users/jeff/Documents/Code/gzkit/tests/governance/test_surface_delivery_witness.py:189) `DeliveryCapIsObservedNeverGated.test_headroom_is_reported_with_byte_distance` |
| 220 | [tests/test_pipeline_integration.py:118](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_integration.py:118) `TestDispatchAggregation.test_model_usage_per_role` |
| 221 | [tests/distribution/test_baseline_manifest.py:35](/Users/jeff/Documents/Code/gzkit/tests/distribution/test_baseline_manifest.py:35) `TestManifestSchemaValidation.test_schema_version_is_1_0` |
| 222 | [tests/test_pipeline_integration.py:92](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_integration.py:92) `TestDispatchAggregation.test_fix_cycles_from_duplicate_task_ids` |
| 223 | [tests/test_triangle.py:1481](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:1481) `TestTaxonomyKindIsSchemaEnforced.test_non_covers_kinds_are_derived_from_the_proof_channel_map` |
| 224 | [tests/commands/test_obpi_block_cmd.py:37](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_block_cmd.py:37) `TestObpiBlockCommand.test_block_writes_the_event_with_both_payload_fields` |
| 225 | [tests/commands/test_status.py:1779](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1779) `TestLifecycleStatusSemantics.test_adr_status_json_validated` |
| 226 | [tests/test_plan_audit_cmd.py:553](/Users/jeff/Documents/Code/gzkit/tests/test_plan_audit_cmd.py:553) `TestPlanAuditCmdFail.test_fail_exits_1_when_no_plan` |
| 227 | [tests/test_formatters.py:140](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:140) `TestJsonMode.test_table_suppressed_in_json_mode` |
| 228 | [tests/chores/test_failure_class_index.py:243](/Users/jeff/Documents/Code/gzkit/tests/chores/test_failure_class_index.py:243) `TestFailSoft.test_non_list_snapshot_yields_empty_corpus` |
| 229 | [tests/commands/test_state.py:72](/Users/jeff/Documents/Code/gzkit/tests/commands/test_state.py:72) `TestStateFullOutputForm.test_state_full_renders_rich_table_with_artifact_state_title` |
| 230 | [tests/test_flag_registry.py:130](/Users/jeff/Documents/Code/gzkit/tests/test_flag_registry.py:130) `TestSchemaValidation.test_missing_registry_file_rejected` |
| 231 | [tests/complexity/test_thresholds.py:348](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_thresholds.py:348) `LoaderIntegration.test_real_data_file_parses_with_twelve_metrics` |
| 232 | [tests/governance/test_advisor_proof_binding_validator.py:273](/Users/jeff/Documents/Code/gzkit/tests/governance/test_advisor_proof_binding_validator.py:273) `TestCliIntegration.test_collect_errors_dispatches_advisor_proof_binding` |
| 233 | [tests/test_parser_arb.py:37](/Users/jeff/Documents/Code/gzkit/tests/test_parser_arb.py:37) `TestArbParserRegistration.test_arb_exposes_canonical_verbs` |
| 234 | [tests/test_sync.py:1505](/Users/jeff/Documents/Code/gzkit/tests/test_sync.py:1505) `TestSyncClaudeSettingsPreservesUserPhases.test_gzkit_phases_refresh_after_tampering` |
| 235 | [tests/test_instruction_eval.py:230](/Users/jeff/Documents/Code/gzkit/tests/test_instruction_eval.py:230) `TestExtensibility.test_suite_accepts_extended_case_list` |
| 236 | [tests/test_review_protocol.py:292](/Users/jeff/Documents/Code/gzkit/tests/test_review_protocol.py:292) `TestComposeQualityReviewPrompt.test_contains_test_coverage_criterion` |
| 237 | [tests/test_config.py:170](/Users/jeff/Documents/Code/gzkit/tests/test_config.py:170) `TestArbConfig.test_frozen` |
| 238 | [tests/test_obpi_lock_cmd.py:425](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:425) `TestLockClaim.test_claim_exits_1_on_conflict` |
| 239 | [tests/governance/test_attestation_fold.py:169](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:169) `TestAttestationFold.test_arb_middleware_doc_exists_with_five_sections` |
| 240 | [tests/test_pipeline_runtime.py:1135](/Users/jeff/Documents/Code/gzkit/tests/test_pipeline_runtime.py:1135) `TestCheckReconcileReceiptGate.test_gate_blocks_when_no_receipt` |
| 241 | [tests/adr/test_patch_release.py:729](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:729) `TestClassifyGhiOpenUpstream.test_open_ghi_downgrades_from_qualified` |
| 242 | [tests/content/test_tier_policy.py:130](/Users/jeff/Documents/Code/gzkit/tests/content/test_tier_policy.py:130) `TestRetirementLeavesTheFloor.test_retirement_relaxes_a_previously_unsatisfiable_floor` |
| 243 | [tests/test_persona_drift.py:99](/Users/jeff/Documents/Code/gzkit/tests/test_persona_drift.py:99) `TestTraitProxyRegistry.test_plan_traits_mapped` |
| 244 | [tests/test_ontology_corpus.py:136](/Users/jeff/Documents/Code/gzkit/tests/test_ontology_corpus.py:136) `TestCorpusTypedRelationEdges.test_supersedes_becomes_node_to_node_typed_edge` |
| 245 | [tests/test_adversarial_validation_gate.py:731](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:731) `TestCrossVendorClaimRequiresReceipt.test_human_degraded_floor_remains_exempt` |
| 246 | [tests/governance/test_status_vocab.py:92](/Users/jeff/Documents/Code/gzkit/tests/governance/test_status_vocab.py:92) `StatusVocabMappingTests.test_every_canonical_value_is_in_ledger_set` |
| 247 | [tests/commands/test_pipeline_baseline_verification.py:238](/Users/jeff/Documents/Code/gzkit/tests/commands/test_pipeline_baseline_verification.py:238) `TestSyncStageStepBuilder.test_complete_command_carries_attestation_text_flag` |
| 248 | [tests/governance/test_behave_sharding.py:88](/Users/jeff/Documents/Code/gzkit/tests/governance/test_behave_sharding.py:88) `TestShardPlanner.test_every_feature_file_lands_in_exactly_one_shard` |
| 249 | [tests/governance/test_enforcement_meta_validator.py:341](/Users/jeff/Documents/Code/gzkit/tests/governance/test_enforcement_meta_validator.py:341) `TestRunnerResultFields.test_claim_run_result_has_required_fields` |
| 250 | [tests/test_tasks.py:188](/Users/jeff/Documents/Code/gzkit/tests/test_tasks.py:188) `TestTaskEntity.test_transition_blocked_to_in_progress` |
| 251 | [tests/governance/test_brief_reconcile.py:759](/Users/jeff/Documents/Code/gzkit/tests/governance/test_brief_reconcile.py:759) `TestCoverageAttributionIsByCoversNotSubstring.test_covers_decorated_test_still_attributes_imports` |
| 252 | [tests/cli/test_log_level_claims.py:53](/Users/jeff/Documents/Code/gzkit/tests/cli/test_log_level_claims.py:53) `TestLogLevelsFollowSpecControl.test_control_restores_process_logging_state` |
| 253 | [tests/test_closeout_pipeline.py:94](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:94) `TestCloseoutPipelineGates.test_gate_failure_halts_pipeline` |
| 254 | [tests/skills/test_complexity_guide.py:261](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:261) `TestNoOperatorPersonalEmail.test_test_module_contains_no_personal_email_addresses` |
| 255 | [tests/test_personas.py:40](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:40) `TestPersonasLayoutDualSurface.test_persona_files_retained_at_authored_source` |
| 256 | [tests/governance/test_transcribed_counts.py:183](/Users/jeff/Documents/Code/gzkit/tests/governance/test_transcribed_counts.py:183) `DatedRecordsAreLeftAlone.test_the_historical_section_closes_at_a_same_depth_heading` |
| 257 | [tests/commands/test_content_retire.py:1517](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1517) `TestContentRetireAttestation.test_unknown_entry_recovery_prose_carries_all_three_parts` |
| 258 | [tests/commands/test_mx_enter.py:149](/Users/jeff/Documents/Code/gzkit/tests/commands/test_mx_enter.py:149) `TestMxEnterFailsClosedOnEmpty.test_empty_reason_writes_no_marker_or_event` |
| 259 | [tests/skills/test_router_coverage_completion.py:78](/Users/jeff/Documents/Code/gzkit/tests/skills/test_router_coverage_completion.py:78) `TestChoresRouterSkillFile.test_gz_chores_file_exists_with_required_frontmatter` |
| 260 | [tests/governance/test_invariant_coherence.py:342](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:342) `TestGzCheckDefault.test_invariant_coherence_in_gz_check_pipeline` |
| 261 | [tests/test_persona_scaffolding.py:79](/Users/jeff/Documents/Code/gzkit/tests/test_persona_scaffolding.py:79) `TestScaffoldDefaultPersonas.test_creates_personas_directory` |
| 262 | [tests/test_lint_parents.py:114](/Users/jeff/Documents/Code/gzkit/tests/test_lint_parents.py:114) `TestParentsPatternLint.test_missing_src_dir_passes` |
| 263 | [tests/commands/test_obpi_stages.py:61](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_stages.py:61) `TestVerifyStageCommandShapeClassification.test_shell_less_verification_commands_pass_through` |
| 264 | [tests/governance/test_facade_regression_corpus.py:105](/Users/jeff/Documents/Code/gzkit/tests/governance/test_facade_regression_corpus.py:105) `TestFacadeRegressionCorpus.test_every_signature_has_a_fixture` |
| 265 | [tests/test_hooks.py:152](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:152) `TestIsGovernanceArtifact.test_test_file` |
| 266 | [tests/governance/test_promoted_advisory_audits.py:781](/Users/jeff/Documents/Code/gzkit/tests/governance/test_promoted_advisory_audits.py:781) `BriefDemoSectionAuditNegativeCases.test_skip_marker_suppresses` |
| 267 | [tests/commands/test_validate.py:18](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate.py:18) `TestKindInvarianceFlag.test_kind_invariance_flag_registered` |
| 268 | [tests/governance/test_enforcement_floor_wiring.py:36](/Users/jeff/Documents/Code/gzkit/tests/governance/test_enforcement_floor_wiring.py:36) `TestGzCheckStepWiring.test_enforcement_floor_step_returns_quality_result` |
| 269 | [tests/skills/test_ghi_triage_deliverable.py:102](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_triage_deliverable.py:102) `TestRankDeliverableIsByteStable.test_render_rank_includes_severity_route_and_title` |
| 270 | [tests/governance/test_agents_md_matrix.py:96](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:96) `TestAgentsMdMatrixCollapse.test_lane_kind_axes_retained_for_gate_firing_scope` |
| 271 | [tests/commands/test_obpi_acceptance_cli.py:176](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:176) `TestAcceptanceProcessExit.test_recording_refutation_succeeds_while_readiness_stays_blocked` |
| 272 | [tests/commands/test_content_import.py:77](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:77) `TestContentImportCmd.test_import_malformed_input_exits_nonzero` |
| 273 | [tests/governance/test_lock_exchange_coupling_validator.py:443](/Users/jeff/Documents/Code/gzkit/tests/governance/test_lock_exchange_coupling_validator.py:443) `TestLockHandoffCouplingReclaimAndReap.test_cross_agent_reap_no_false_error` |
| 274 | [tests/test_hooks_guards_ledger_sync.py:198](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards_ledger_sync.py:198) `TestForbidSkillSyncDrift.test_canonical_skill_rename_with_mirror_renames_returns_zero` |
| 275 | [tests/governance/test_audit_check_covers_backfill.py:234](/Users/jeff/Documents/Code/gzkit/tests/governance/test_audit_check_covers_backfill.py:234) `TestFindCoversDecoratorIntroductions.test_empty_stdout_yields_unresolvable` |
| 276 | [tests/commands/test_complexity_distill_cmd.py:67](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_distill_cmd.py:67) `TestComplexityDistillBehavior.test_writes_dated_distilled_characteristics_under_output_dir` |
| 277 | [tests/content/test_ownership.py:1307](/Users/jeff/Documents/Code/gzkit/tests/content/test_ownership.py:1307) `TestRecordUnownedTotalRatchet.test_a_total_greater_than_the_floor_is_refused_and_nothing_is_persisted` |
| 278 | [tests/test_flag_diagnostics.py:77](/Users/jeff/Documents/Code/gzkit/tests/test_flag_diagnostics.py:77) `TestGetStaleFlags.test_flag_past_review_by_is_stale` |
| 279 | [tests/commands/test_content_unown.py:5079](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:5079) `TestRecoveryStagingInspectionFailures.test_unknown_orphan_family_cannot_exempt_new_transaction_cleanup` |
| 280 | [tests/test_flag_service.py:109](/Users/jeff/Documents/Code/gzkit/tests/test_flag_service.py:109) `TestPrecedenceChain.test_env_var_overrides_registry_default` |
| 281 | [tests/test_foundation_limbo_gate.py:400](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_limbo_gate.py:400) `TestFoundationLimboProse.test_prose_states_it_reads_the_ledger_not_frontmatter` |
| 282 | [tests/test_triangle.py:156](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:156) `TestVertexTypes.test_vertex_type_count` |
| 283 | [tests/governance/test_session_exit.py:293](/Users/jeff/Documents/Code/gzkit/tests/governance/test_session_exit.py:293) `TestExitBeatIsIntentionalAboutBookmarks.test_a_staged_bookmark_does_not_block_the_next_skip` |
| 284 | [tests/scripts/test_session_orientation.py:426](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_session_orientation.py:426) `TestCollectRemoteState.test_git_unavailable_returns_none` |
| 285 | [tests/test_lint_parents.py:83](/Users/jeff/Documents/Code/gzkit/tests/test_lint_parents.py:83) `TestParentsPatternLint.test_parent_without_bracket_allowed` |
| 286 | [tests/commands/test_foundation_kind_closed.py:287](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:287) `TestFoundationKindClosedAtAuthoringTime.test_render_adr_by_kind_still_renders_feature` |
| 287 | [tests/test_lock_manager.py:473](/Users/jeff/Documents/Code/gzkit/tests/test_lock_manager.py:473) `TestReapExpiredLocks.test_mixed_reaps_only_expired` |
| 288 | [tests/commands/test_knowledge.py:74](/Users/jeff/Documents/Code/gzkit/tests/commands/test_knowledge.py:74) `TestKnowledgeRefresh.test_refresh_is_idempotent` |
| 289 | [tests/arb/test_validator_provenance.py:132](/Users/jeff/Documents/Code/gzkit/tests/arb/test_validator_provenance.py:132) `ProvenanceChecking.test_canonical_mkdocs_command_validates` |
| 290 | [tests/mx/test_gate5_invariants_live_nc.py:62](/Users/jeff/Documents/Code/gzkit/tests/mx/test_gate5_invariants_live_nc.py:62) `TestGate5NamedNotEnforced.test_secrets_is_named_not_enforced` |
| 291 | [tests/chores/test_eval_feedback_cluster.py:74](/Users/jeff/Documents/Code/gzkit/tests/chores/test_eval_feedback_cluster.py:74) `TestEvalFeedbackCluster.test_zero_evidence_no_proposals` |
| 292 | [tests/test_acceptance_store.py:356](/Users/jeff/Documents/Code/gzkit/tests/test_acceptance_store.py:356) `AcceptanceStoreTests.test_reinitialization_cannot_erase_prior_history` |
| 293 | [tests/hooks/test_stop_turn_feedback.py:211](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:211) `TestClaimGrounding.test_unbacked_claim_blocks_with_three_part_prose` |
| 294 | [tests/governance/test_gate_caller_scope.py:180](/Users/jeff/Documents/Code/gzkit/tests/governance/test_gate_caller_scope.py:180) `TestAcceptanceEntryShape.test_entry_without_reason_is_flagged` |
| 295 | [tests/models/test_exemplar.py:76](/Users/jeff/Documents/Code/gzkit/tests/models/test_exemplar.py:76) `TestExemplarProjectFrozenContract.test_excluded_path_model_config_frozen` |
| 296 | [tests/content/test_composer.py:1584](/Users/jeff/Documents/Code/gzkit/tests/content/test_composer.py:1584) `TestOverlappingInvariantsInCarriedForwardAreAccepted.test_rendered_partition_is_measured_not_derived_from_the_population` |
| 297 | [tests/test_product_proof.py:277](/Users/jeff/Documents/Code/gzkit/tests/test_product_proof.py:277) `TestCheckGovernanceArtifactProof.test_docs_governance_artifact_with_content_post_440` |
| 298 | [tests/complexity/advisor/test_engine.py:348](/Users/jeff/Documents/Code/gzkit/tests/complexity/advisor/test_engine.py:348) `RecommendedMoveProvenanceTest.test_matched_rule_path_recommended_move_from_distilled_not_fabricated` |
| 299 | [tests/test_hooks.py:1101](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1101) `TestPlanAuditGateHook.test_blocks_when_receipt_obpi_does_not_match` |
| 300 | [tests/test_tasks.py:469](/Users/jeff/Documents/Code/gzkit/tests/test_tasks.py:469) `TestTaskEscalatedEvent.test_reason_required` |

## Appendix E. Complete open test-shape advisory inventory

### Filesystem-shaped operation advisories

| Source | Function | Operation | Disposition suggested by scanner |
|---|---|---|---|
| [tests/adr/test_storage_tiers.py:74](/Users/jeff/Documents/Code/gzkit/tests/adr/test_storage_tiers.py:74) | test_tier_b_rebuild_and_gz_state | exists | convert |
| [tests/arb/test_ruff_reporter.py:59](/Users/jeff/Documents/Code/gzkit/tests/arb/test_ruff_reporter.py:59) | _assert_valid_receipt | read_text | replace-with-ledger |
| [tests/arb/test_schemas.py:23](/Users/jeff/Documents/Code/gzkit/tests/arb/test_schemas.py:23) | test_lint_schema_exists_and_is_valid | exists | replace-with-ledger |
| [tests/arb/test_schemas.py:36](/Users/jeff/Documents/Code/gzkit/tests/arb/test_schemas.py:36) | test_step_schema_exists_and_is_valid | exists | replace-with-ledger |
| [tests/arb/test_schemas.py:49](/Users/jeff/Documents/Code/gzkit/tests/arb/test_schemas.py:49) | test_lint_receipt_shape_matches_schema | read_text | replace-with-ledger |
| [tests/arb/test_schemas.py:72](/Users/jeff/Documents/Code/gzkit/tests/arb/test_schemas.py:72) | test_step_receipt_shape_matches_schema | read_text | replace-with-ledger |
| [tests/chores/test_eval_feedback_cluster.py:351](/Users/jeff/Documents/Code/gzkit/tests/chores/test_eval_feedback_cluster.py:351) | test_chore_registered_in_registry | exists | convert |
| [tests/cli/test_justify_manpage.py:60](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:60) | test_manpage_file_exists | is_file | convert |
| [tests/cli/test_justify_manpage.py:302](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:302) | test_manpage_path_is_valid_markdown_for_mkdocs | read_text | convert |
| [tests/cli/test_justify_manpage.py:310](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:310) | test_doc_coverage_manifest_marks_justify_as_governance_relevant | read_text | convert |
| [tests/cli/test_justify_manpage.py:330](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:330) | test_commands_index_lists_justify | read_text | convert |
| [tests/commands/test_brief_reconcile.py:459](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:459) | test_manpage_has_required_sections | read_text | convert |
| [tests/commands/test_foundation_kind_closed.py:473](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:473) | test_kind_enum_still_lists_foundation_seal_not_delete | read_text | convert |
| [tests/commands/test_frontmatter_reconcile.py:46](/Users/jeff/Documents/Code/gzkit/tests/commands/test_frontmatter_reconcile.py:46) | test_chore_registered_as_heavy_lane_in_production_config | read_text | fold-to-validator |
| [tests/commands/test_init.py:603](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:603) | test_init_manpage_mentions_rules | exists | convert |
| [tests/commands/test_init.py:611](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:611) | test_skill_surface_sync_rule_has_gz_init_bootstrap_note | exists | convert |
| [tests/commands/test_issue_cmd.py:340](/Users/jeff/Documents/Code/gzkit/tests/commands/test_issue_cmd.py:340) | test_features_file_carries_required_scenario_tags | read_text | convert |
| [tests/commands/test_justify_cmd.py:286](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:286) | test_justify_command_doc_and_index_exist | read_text | convert |
| [tests/commands/test_plan.py:631](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:631) | test_concept_page_documents_why_foundation_tier_convention | read_text | convert |
| [tests/commands/test_plan.py:650](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:650) | test_runbook_cross_references_why_foundation_tier_convention | read_text | convert |
| [tests/commands/test_skills.py:243](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:243) | test_init_scaffolds_adr_create_and_removes_adr_manager | exists | convert |
| [tests/commands/test_skills.py:258](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:258) | test_init_scaffolds_git_sync_skill_with_canonical_body | read_text | convert |
| [tests/commands/test_upgrade_resources.py:67](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade_resources.py:67) | test_skills_resource_is_directory | is_dir | convert |
| [tests/commands/test_upgrade_resources.py:75](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade_resources.py:75) | test_rules_resource_is_directory | is_dir | convert |
| [tests/complexity/advisor/test_timeout.py:144](/Users/jeff/Documents/Code/gzkit/tests/complexity/advisor/test_timeout.py:144) | test_no_subprocess_spawned | read_text | convert |
| [tests/complexity/test_baseline.py:178](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_baseline.py:178) | test_measure_corpus_writes_files_under_output_dir | is_file | fold-to-validator |
| [tests/complexity/test_citation.py:125](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:125) | test_body_marker_and_block_quote_agree | read_text | convert |
| [tests/complexity/test_citation.py:147](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:147) | test_schema_file_present_and_constrains_three_fields | exists | convert |
| [tests/complexity/test_citation.py:192](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:192) | test_canonical_rule_body_present_in_each_vendor_mirror | read_text | convert |
| [tests/complexity/test_citation.py:241](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:241) | test_personal_email_absent_from_authored_surfaces | read_text | convert |
| [tests/complexity/test_measurement.py:62](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:62) | test_measure_corpus_smoke | read_text | convert |
| [tests/complexity/test_measurement.py:247](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:247) | test_pyproject_declares_three_deps_with_pins | read_text | convert |
| [tests/complexity/test_measurement.py:258](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:258) | test_pyproject_cites_stdlib_first_named_departure | read_text | convert |
| [tests/complexity/test_measurement.py:284](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:284) | test_module_size_discipline | read_text | convert |
| [tests/complexity/test_measurement.py:337](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:337) | test_no_shell_true_in_measurement_source | read_text | convert |
| [tests/complexity/test_measurement.py:342](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:342) | test_subprocess_calls_use_list_form_in_source | read_text | convert |
| [tests/complexity/test_thresholds.py:392](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_thresholds.py:392) | test_schema_file_exists_and_loads | is_file | convert |
| [tests/distribution/test_baseline_manifest.py:69](/Users/jeff/Documents/Code/gzkit/tests/distribution/test_baseline_manifest.py:69) | _assert_entries_resolve | is_file | convert |
| [tests/eval/test_datasets.py:41](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:41) | test_schema_file_exists | is_file | fold-to-validator |
| [tests/eval/test_datasets.py:44](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:44) | test_schema_is_valid_json | read_text | convert |
| [tests/eval/test_datasets.py:59](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:59) | test_all_fixtures_valid_json | read_text | fold-to-validator |
| [tests/eval/test_datasets.py:71](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:71) | test_no_duplicate_case_ids_within_dataset | read_text | fold-to-validator |
| [tests/eval/test_datasets.py:144](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:144) | test_no_timestamps_in_fixtures | read_text | fold-to-validator |
| [tests/eval/test_datasets.py:155](/Users/jeff/Documents/Code/gzkit/tests/eval/test_datasets.py:155) | test_no_random_seeds | read_text | fold-to-validator |
| [tests/governance/test_agent_contract_fold.py:71](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:71) | test_agent_contract_rule_file_deleted | exists | convert |
| [tests/governance/test_agent_contract_fold.py:100](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:100) | test_agents_md_contains_migrated_invariants | read_text | replace-with-ledger |
| [tests/governance/test_agent_contract_fold.py:147](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:147) | test_claude_md_carries_10a_and_agents_md_does_not | read_text | convert |
| [tests/governance/test_agent_contract_fold.py:188](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:188) | test_rationale_md_has_three_named_sections | read_text | convert |
| [tests/governance/test_agent_contract_fold.py:221](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:221) | test_manifest_allowlist_removes_agent_contract_entry | read_text | fold-to-validator |
| [tests/governance/test_agent_contract_fold.py:293](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:293) | test_vendor_mirrors_of_agent_contract_were_removed_by_sync | exists | convert |
| [tests/governance/test_agent_contract_fold.py:336](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agent_contract_fold.py:336) | test_no_new_deps_shell_true_or_dataclass | read_text | convert |
| [tests/governance/test_agents_md_map_doctrine.py:158](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine.py:158) | test_doctrine_doc_exists_with_canonical_anchors | read_text | convert |
| [tests/governance/test_agents_md_map_doctrine.py:279](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine.py:279) | test_scorecard_entry_mechanical_with_judgment_note | read_text | convert |
| [tests/governance/test_agents_md_map_doctrine.py:318](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine.py:318) | test_obpi02_lift_targets_present_after_obpi02_landed | exists | convert |
| [tests/governance/test_agents_md_map_doctrine_application.py:97](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:97) | test_model_selection_rationale_expansion_doc_exists | is_file | convert |
| [tests/governance/test_agents_md_map_doctrine_application.py:106](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:106) | test_skill_surface_sync_rationale_expansion_doc_exists | is_file | convert |
| [tests/governance/test_agents_md_map_doctrine_application.py:114](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:114) | test_model_selection_has_see_link_to_expansion | read_text | convert |
| [tests/governance/test_agents_md_map_doctrine_application.py:124](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:124) | test_skill_surface_sync_has_see_link_to_expansion | read_text | convert |
| [tests/governance/test_agents_md_map_doctrine_application.py:157](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine_application.py:157) | test_agents_md_fits_the_codex_project_doc_cap | read_text | fold-to-validator |
| [tests/governance/test_agents_md_matrix.py:43](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:43) | test_self_closeable_phrase_is_absent | read_text | convert |
| [tests/governance/test_agents_md_matrix.py:66](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:66) | test_universal_attestation_binding_rule_present | read_text | convert |
| [tests/governance/test_agents_md_matrix.py:104](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:104) | test_lane_kind_axes_retained_for_gate_firing_scope | read_text | convert |
| [tests/governance/test_agents_md_matrix.py:153](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:153) | test_amendment_cites_ghi_and_adr_inline | read_text | convert |
| [tests/governance/test_agents_md_matrix.py:185](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_matrix.py:185) | test_mirrors_reflect_amended_canon | read_text | convert |
| [tests/governance/test_attestation_fold.py:87](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:87) | test_attestation_rule_file_deleted | exists | convert |
| [tests/governance/test_attestation_fold.py:184](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:184) | test_arb_middleware_doc_exists_with_five_sections | read_text | replace-with-ledger |
| [tests/governance/test_attestation_fold.py:233](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:233) | test_manifest_allowlist_removes_attestation_enrichment_entry | read_text | fold-to-validator |
| [tests/governance/test_attestation_fold.py:315](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:315) | test_vendor_mirrors_of_attestation_rule_were_removed_by_sync | exists | convert |
| [tests/governance/test_attestation_fold.py:376](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_fold.py:376) | test_no_arb_schema_change_and_no_new_deps | read_text | replace-with-ledger |
| [tests/governance/test_complexity_doctrine_links.py:311](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_links.py:311) | test_validate_command_doc_documents_flag | read_text | convert |
| [tests/governance/test_complexity_doctrine_rule.py:167](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:167) | test_advisory_scorecard_classifies_rule_mechanical | read_text | convert |
| [tests/governance/test_complexity_doctrine_rule.py:202](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:202) | test_vendor_mirrors_carry_rule_version_marker | is_file | convert |
| [tests/governance/test_complexity_doctrine_rule.py:218](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:218) | test_vendor_mirror_body_contains_key_canonical_content | read_text | convert |
| [tests/governance/test_complexity_thresholds_rule.py:311](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:311) | test_advisory_scorecard_classifies_rule_mechanical | read_text | convert |
| [tests/governance/test_complexity_thresholds_rule.py:347](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:347) | test_vendor_mirrors_carry_rule_version_marker | is_file | convert |
| [tests/governance/test_complexity_thresholds_validator.py:285](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_validator.py:285) | test_command_doc_documents_flag | read_text | convert |
| [tests/governance/test_complexity_thresholds_validator.py:292](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_validator.py:292) | test_runbook_lists_complexity_thresholds_verb | read_text | convert |
| [tests/governance/test_defect_fix_routing_fold.py:76](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:76) | test_defect_fix_routing_rule_file_deleted | exists | convert |
| [tests/governance/test_defect_fix_routing_fold.py:100](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:100) | test_agents_md_has_defect_fix_routing_section | read_text | fold-to-validator |
| [tests/governance/test_defect_fix_routing_fold.py:171](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:171) | test_governance_doc_exists_with_three_sections | read_text | convert |
| [tests/governance/test_defect_fix_routing_fold.py:216](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:216) | test_manifest_allowlist_no_longer_contains_defect_fix_routing | read_text | fold-to-validator |
| [tests/governance/test_defect_fix_routing_fold.py:290](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:290) | test_vendor_mirrors_of_defect_fix_routing_rule_were_removed_by_sync | exists | convert |
| [tests/governance/test_defect_fix_routing_fold.py:330](/Users/jeff/Documents/Code/gzkit/tests/governance/test_defect_fix_routing_fold.py:330) | test_no_new_deps_no_shell_true_no_dataclass | read_text | convert |
| [tests/governance/test_distribution_invariant_catalog.py:30](/Users/jeff/Documents/Code/gzkit/tests/governance/test_distribution_invariant_catalog.py:30) | test_catalog_exists_with_three_required_sections | exists | convert |
| [tests/governance/test_distribution_invariant_catalog.py:138](/Users/jeff/Documents/Code/gzkit/tests/governance/test_distribution_invariant_catalog.py:138) | test_catalog_well_formed_for_validate_and_mkdocs_strict | exists | replace-with-ledger |
| [tests/governance/test_evaluation_event.py:98](/Users/jeff/Documents/Code/gzkit/tests/governance/test_evaluation_event.py:98) | test_schema_entry_exists | exists | convert |
| [tests/governance/test_evaluation_event.py:106](/Users/jeff/Documents/Code/gzkit/tests/governance/test_evaluation_event.py:106) | test_schema_has_required_fields | read_text | convert |
| [tests/governance/test_exemplar_corpus.py:192](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:192) | test_all_six_cluster_pool_stubs_exist | is_file | convert |
| [tests/governance/test_exemplar_corpus.py:201](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:201) | test_each_pool_stub_carries_canonical_id_frontmatter | read_text | convert |
| [tests/governance/test_exemplar_corpus.py:219](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:219) | test_each_pool_stub_cites_obpi_02_as_booking_event | read_text | convert |
| [tests/governance/test_exemplar_corpus.py:236](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:236) | test_corpus_text_contains_no_personal_email | read_text | convert |
| [tests/governance/test_foundation_grandfather_manifest.py:129](/Users/jeff/Documents/Code/gzkit/tests/governance/test_foundation_grandfather_manifest.py:129) | test_guard_accepts_a_byte_identical_copy | read_text | convert |
| [tests/governance/test_foundation_invariance_skill_enrichment.py:149](/Users/jeff/Documents/Code/gzkit/tests/governance/test_foundation_invariance_skill_enrichment.py:149) | _assert_mirror_parity | read_bytes | convert |
| [tests/governance/test_handoff_migration.py:156](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_migration.py:156) | test_skill_canon_has_no_per_adr_write_path | read_text | convert |
| [tests/governance/test_historical_waiver_integration.py:273](/Users/jeff/Documents/Code/gzkit/tests/governance/test_historical_waiver_integration.py:273) | test_documentation_published_and_cites_lineage | read_text | convert |
| [tests/governance/test_invariant_coherence.py:259](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:259) | test_composition_rendered_event_defined_in_schema | exists | convert |
| [tests/governance/test_invariant_coherence.py:273](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:273) | test_composition_drift_detected_event_defined_in_schema | read_text | convert |
| [tests/governance/test_invariant_coherence.py:286](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:286) | test_composition_rendered_required_fields_present | read_text | convert |
| [tests/governance/test_invariant_coherence.py:301](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:301) | test_composition_drift_required_fields_present | read_text | convert |
| [tests/governance/test_invariant_coherence.py:368](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:368) | test_scorecard_entry_present | read_text | convert |
| [tests/governance/test_invariant_coherence.py:377](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariant_coherence.py:377) | test_scorecard_row_cites_validator_module | read_text | convert |
| [tests/governance/test_invariants.py:78](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariants.py:78) | test_schema_file_exists | exists | convert |
| [tests/governance/test_invariants.py:82](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariants.py:82) | test_schema_additional_properties_false | read_text | convert |
| [tests/governance/test_invariants.py:87](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariants.py:87) | test_schema_structural_witness_min_items_one | read_text | convert |
| [tests/governance/test_invariants.py:94](/Users/jeff/Documents/Code/gzkit/tests/governance/test_invariants.py:94) | test_schema_required_keys_present | read_text | convert |
| [tests/governance/test_kind_invariance_docs.py:131](/Users/jeff/Documents/Code/gzkit/tests/governance/test_kind_invariance_docs.py:131) | test_behave_scenario_tagged_with_req | read_text | convert |
| [tests/governance/test_kind_invariance_docs.py:139](/Users/jeff/Documents/Code/gzkit/tests/governance/test_kind_invariance_docs.py:139) | test_manpage_documents_kind_invariance | read_text | convert |
| [tests/governance/test_kind_invariance_docs.py:147](/Users/jeff/Documents/Code/gzkit/tests/governance/test_kind_invariance_docs.py:147) | test_runbook_cross_references_kind_invariance | read_text | convert |
| [tests/governance/test_kind_invariance_docs.py:209](/Users/jeff/Documents/Code/gzkit/tests/governance/test_kind_invariance_docs.py:209) | test_validator_tests_assert_semantics_not_strings | read_text | convert |
| [tests/governance/test_req_coverage_record.py:407](/Users/jeff/Documents/Code/gzkit/tests/governance/test_req_coverage_record.py:407) | test_grandfathering_json_exists | exists | fold-to-validator |
| [tests/governance/test_req_coverage_record.py:413](/Users/jeff/Documents/Code/gzkit/tests/governance/test_req_coverage_record.py:413) | test_grandfathering_json_is_valid_json | read_text | fold-to-validator |
| [tests/governance/test_req_kind_discipline.py:305](/Users/jeff/Documents/Code/gzkit/tests/governance/test_req_kind_discipline.py:305) | test_obpi_specify_skill_has_req_kind_authoring_section | read_text | convert |
| [tests/governance/test_schema_sensitivity.py:120](/Users/jeff/Documents/Code/gzkit/tests/governance/test_schema_sensitivity.py:120) | test_existing_artifacts_lack_sensitivity_or_match_enum | read_text | convert |
| [tests/governance/test_security_sensitivity_rule.py:139](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_sensitivity_rule.py:139) | test_agents_md_matrix_cites_rule_and_lists_every_cell | read_text | convert |
| [tests/governance/test_security_sensitivity_rule.py:163](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_sensitivity_rule.py:163) | test_advisory_scorecard_classifies_rule_mechanical | read_text | convert |
| [tests/governance/test_security_surfaces_registry.py:104](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:104) | test_registry_file_exists | is_file | convert |
| [tests/governance/test_security_surfaces_registry.py:132](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:132) | test_governance_readme_exists | is_file | convert |
| [tests/governance/test_security_surfaces_registry.py:135](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:135) | test_governance_readme_documents_contract | read_text | convert |
| [tests/governance/test_security_surfaces_registry.py:140](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:140) | test_governance_readme_records_bootstrap_exception | read_text | convert |
| [tests/governance/test_security_surfaces_registry.py:220](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:220) | test_validate_sensitivity_scope_not_authored | is_file | convert |
| [tests/governance/test_security_surfaces_registry.py:230](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:230) | test_security_review_attestation_authored_at_named_path | is_file | convert |
| [tests/governance/test_security_surfaces_registry.py:242](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_surfaces_registry.py:242) | test_security_sensitivity_rule_authored_at_named_path | read_text | convert |
| [tests/governance/test_skill_self_close_drift.py:131](/Users/jeff/Documents/Code/gzkit/tests/governance/test_skill_self_close_drift.py:131) | test_canon_skill_files_have_no_self_close | read_text | convert |
| [tests/governance/test_skill_self_close_drift.py:169](/Users/jeff/Documents/Code/gzkit/tests/governance/test_skill_self_close_drift.py:169) | test_canon_rule_files_have_no_self_close | read_text | convert |
| [tests/governance/test_skill_self_close_drift.py:223](/Users/jeff/Documents/Code/gzkit/tests/governance/test_skill_self_close_drift.py:223) | test_edited_skills_have_bumped_version | read_text | replace-with-ledger |
| [tests/governance/test_skill_self_close_drift.py:271](/Users/jeff/Documents/Code/gzkit/tests/governance/test_skill_self_close_drift.py:271) | test_vendor_mirrors_match_canonical_post_sync | read_text | convert |
| [tests/governance/test_skill_self_close_drift.py:304](/Users/jeff/Documents/Code/gzkit/tests/governance/test_skill_self_close_drift.py:304) | test_pipeline_and_closeout_skills_cross_reference_dead_letter | read_text | convert |
| [tests/governance/test_surface_fidelity_composite.py:174](/Users/jeff/Documents/Code/gzkit/tests/governance/test_surface_fidelity_composite.py:174) | test_precommit_cheap_subset_registration | read_text | fold-to-validator |
| [tests/governance/test_surface_fidelity_composite.py:216](/Users/jeff/Documents/Code/gzkit/tests/governance/test_surface_fidelity_composite.py:216) | test_validate_manpage_documents_surface_fidelity | read_text | convert |
| [tests/hooks/test_complexity_advisor_auto_chain.py:349](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:349) | test_tests_use_tempfile_and_covers | read_text | convert |
| [tests/hooks/test_stop_turn_feedback.py:183](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:183) | test_block_appends_exactly_one_json_line | read_text | convert |
| [tests/hooks/test_stop_turn_feedback.py:201](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:201) | test_over_cap_log_is_rewritten_keeping_newest_lines | read_text | convert |
| [tests/hooks/test_stop_turn_feedback.py:332](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:332) | test_settings_json_wires_stop_hook_to_existing_script | read_text | convert |
| [tests/knowledge/test_content_boundary_doctrine.py:51](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_content_boundary_doctrine.py:51) | test_doctrine_file_exists | exists | convert |
| [tests/knowledge/test_content_boundary_doctrine.py:134](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_content_boundary_doctrine.py:134) | test_relocation_candidate_docs_still_present_and_nonempty | exists | convert |
| [tests/knowledge/test_progressive_disclosure_path.py:38](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_progressive_disclosure_path.py:38) | test_all_tracer_slice_concepts_reachable | read_text | convert |
| [tests/knowledge/test_progressive_disclosure_path.py:79](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_progressive_disclosure_path.py:79) | test_concept_doc_names_bundle_root | read_text | convert |
| [tests/models/test_exemplar.py:396](/Users/jeff/Documents/Code/gzkit/tests/models/test_exemplar.py:396) | test_schema_declares_draft_2020_12 | read_text | convert |
| [tests/models/test_exemplar.py:423](/Users/jeff/Documents/Code/gzkit/tests/models/test_exemplar.py:423) | test_schema_commit_sha_pattern | read_text | convert |
| [tests/models/test_exemplar.py:430](/Users/jeff/Documents/Code/gzkit/tests/models/test_exemplar.py:430) | test_schema_additional_properties_false_on_all_objects | read_text | convert |
| [tests/policy/test_naming_conventions.py:74](/Users/jeff/Documents/Code/gzkit/tests/policy/test_naming_conventions.py:74) | test_src_root_exists | is_dir | convert |
| [tests/scripts/test_backfill_adr_taxonomy.py:89](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:89) | test_classifies_foundation_and_feature_by_semver | read_text | convert |
| [tests/scripts/test_backfill_adr_taxonomy.py:102](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:102) | test_records_error_for_missing_semver | read_text | replace-with-ledger |
| [tests/scripts/test_backfill_adr_taxonomy.py:142](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:142) | test_preserves_other_frontmatter_fields_and_inserts_kind_after_status | read_text | convert |
| [tests/scripts/test_backfill_adr_taxonomy.py:200](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:200) | test_dry_run_does_not_mutate | read_text | convert |
| [tests/scripts/test_backfill_adr_taxonomy.py:256](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:256) | test_emits_receipt_with_required_fields | read_text | replace-with-ledger |
| [tests/scripts/test_backfill_adr_taxonomy.py:273](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_backfill_adr_taxonomy.py:273) | test_does_not_touch_ledger | read_text | replace-with-ledger |
| [tests/scripts/test_session_orientation.py:327](/Users/jeff/Documents/Code/gzkit/tests/scripts/test_session_orientation.py:327) | test_orientation_source_has_no_dual_scan_markers | read_text | convert |
| [tests/skills/test_complexity_advisor.py:241](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:241) | test_each_vendor_mirror_matches_canonical | read_bytes | convert |
| [tests/skills/test_complexity_advisor.py:274](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:274) | test_test_module_contains_no_personal_email_addresses | read_text | convert |
| [tests/skills/test_complexity_guide.py:229](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:229) | test_each_vendor_mirror_matches_canonical | read_bytes | convert |
| [tests/skills/test_complexity_guide.py:262](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:262) | test_test_module_contains_no_personal_email_addresses | read_text | convert |
| [tests/skills/test_ghi_triage_deliverable.py:239](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_triage_deliverable.py:239) | test_cache_dir_auto_created_when_missing | exists | convert |
| [tests/skills/test_gz_complexity_distill.py:303](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:303) | test_each_vendor_mirror_matches_canonical | read_bytes | convert |
| [tests/skills/test_gz_complexity_distill.py:337](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:337) | test_test_module_contains_no_personal_email_addresses | read_text | convert |
| [tests/skills/test_gz_justify_complexity_amendment.py:121](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_justify_complexity_amendment.py:121) | test_vendor_mirrors_byte_identical | read_text | convert |
| [tests/skills/test_namespace_router_surface_sync.py:46](/Users/jeff/Documents/Code/gzkit/tests/skills/test_namespace_router_surface_sync.py:46) | test_each_router_byte_equivalent_in_every_vendor_mirror | is_file | convert |
| [tests/skills/test_namespace_router_surface_sync.py:70](/Users/jeff/Documents/Code/gzkit/tests/skills/test_namespace_router_surface_sync.py:70) | test_each_router_byte_equivalent_in_wheel_pkg_copy | is_file | convert |
| [tests/skills/test_namespace_routers.py:50](/Users/jeff/Documents/Code/gzkit/tests/skills/test_namespace_routers.py:50) | test_all_six_router_files_exist_under_canonical_skills_root | is_file | convert |
| [tests/skills/test_router_coverage_completion.py:205](/Users/jeff/Documents/Code/gzkit/tests/skills/test_router_coverage_completion.py:205) | test_gz_chores_byte_equivalent_in_pkg_and_every_vendor_mirror | read_bytes | convert |
| [tests/test_adr_audit_predicates.py:154](/Users/jeff/Documents/Code/gzkit/tests/test_adr_audit_predicates.py:154) | test_agents_md_matrix_names_third_axis | read_text | convert |
| [tests/test_adr_management_confirm.py:43](/Users/jeff/Documents/Code/gzkit/tests/test_adr_management_confirm.py:43) | test_final_decision_recorded_in_brief | read_text | convert |
| [tests/test_adr_management_confirm.py:98](/Users/jeff/Documents/Code/gzkit/tests/test_adr_management_confirm.py:98) | test_no_absorbed_adr_module_introduced | exists | convert |
| [tests/test_chores.py:38](/Users/jeff/Documents/Code/gzkit/tests/test_chores.py:38) | test_classifier_section_in_rule | read_text | convert |
| [tests/test_chores.py:171](/Users/jeff/Documents/Code/gzkit/tests/test_chores.py:171) | test_no_runtime_state_relocation | is_dir | convert |
| [tests/test_doc_coverage.py:753](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:753) | test_real_manifest_validates_against_schema | exists | fold-to-validator |
| [tests/test_doc_coverage.py:952](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:952) | test_doc_coverage_in_chore_registry | read_text | fold-to-validator |
| [tests/test_doc_coverage.py:958](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:958) | test_doc_coverage_chore_frequency | read_text | fold-to-validator |
| [tests/test_doc_coverage.py:964](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:964) | test_doc_coverage_chore_dir_exists | is_dir | convert |
| [tests/test_doc_coverage.py:971](/Users/jeff/Documents/Code/gzkit/tests/test_doc_coverage.py:971) | test_doc_coverage_schema_exists | exists | fold-to-validator |
| [tests/test_foundation_doctrine_retirement.py:163](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_doctrine_retirement.py:163) | test_record_remains_on_disk | is_file | convert |
| [tests/test_foundation_doctrine_retirement.py:176](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_doctrine_retirement.py:176) | test_superseded_marker_is_seated_at_the_guidance | read_text | convert |
| [tests/test_foundation_doctrine_retirement.py:209](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_doctrine_retirement.py:209) | test_decision_text_is_preserved_not_redacted | read_text | convert |
| [tests/test_foundation_doctrine_retirement.py:228](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_doctrine_retirement.py:228) | test_gz_design_kind_question_enumerates_feature_and_pool_only | read_text | convert |
| [tests/test_foundation_triage_e2e.py:153](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_e2e.py:153) | test_foundation_triage_skill_doc_exists_with_template_form | read_text | convert |
| [tests/test_foundation_triage_e2e.py:169](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_e2e.py:169) | test_foundation_kind_example_in_plan_create_manpage | read_text | convert |
| [tests/test_foundation_triage_e2e.py:184](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_e2e.py:184) | test_both_runbooks_contain_foundation_triage_section | read_text | convert |
| [tests/test_foundation_triage_e2e.py:197](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_e2e.py:197) | test_skill_doc_example_contains_real_output_not_placeholder | read_text | convert |
| [tests/test_foundation_triage_rubric.py:277](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_rubric.py:277) | test_governance_triage_vocabulary_exists | read_text | convert |
| [tests/test_foundation_triage_rubric.py:285](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_rubric.py:285) | test_feature_unblocking_count_term_registered | read_text | convert |
| [tests/test_foundation_triage_rubric.py:302](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_rubric.py:302) | test_schema_file_exists | exists | convert |
| [tests/test_foundation_triage_skill.py:45](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:45) | test_skill_md_exists_at_canonical_path | exists | convert |
| [tests/test_foundation_triage_skill.py:93](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:93) | test_triage_run_leaves_governance_surfaces_untouched | exists | convert |
| [tests/test_foundation_triage_skill.py:165](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:165) | test_wheel_copy_byte_equals_canonical | exists | convert |
| [tests/test_foundation_triage_skill.py:173](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:173) | test_claude_mirror_byte_equals_canonical | exists | convert |
| [tests/test_foundation_triage_skill.py:189](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:189) | test_every_rendered_vendor_mirror_byte_equals_canonical | exists | convert |
| [tests/test_foundation_triage_skill.py:197](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:197) | test_agents_mirror_byte_equals_canonical | exists | convert |
| [tests/test_hooks.py:506](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:506) | test_all_hook_commands_anchor_to_project_dir | read_text | fold-to-validator |
| [tests/test_hooks.py:539](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:539) | test_all_hook_commands_anchor_to_git_toplevel | read_text | fold-to-validator |
| [tests/test_packaging.py:135](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:135) | test_pyproject_uses_hatchling_native_syntax | open | fold-to-validator |
| [tests/test_packaging.py:174](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:174) | test_pyproject_preserves_packages_declaration | open | convert |
| [tests/test_packaging.py:193](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:193) | test_importlib_resources_lists_chore_slugs | is_dir | convert |
| [tests/test_packaging.py:210](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:210) | test_importlib_resources_resolves_registry_json | read_text | fold-to-validator |
| [tests/test_packaging.py:228](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:228) | test_gz_spec_extends_datas_with_chores | read_text | fold-to-validator |
| [tests/test_packaging.py:254](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:254) | test_pyinstaller_dependency_remains_declared | open | convert |
| [tests/test_personas.py:42](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:42) | test_persona_files_retained_at_authored_source | is_dir | convert |
| [tests/test_personas.py:53](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:53) | test_persona_files_present_in_package_surface | is_dir | convert |
| [tests/test_personas.py:72](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:72) | test_dual_surface_byte_parity | read_bytes | convert |
| [tests/test_personas.py:81](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:81) | test_package_init_exists | is_file | convert |
| [tests/test_personas.py:93](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:93) | test_pyproject_has_personas_wheel_include | read_text | convert |
| [tests/test_personas.py:134](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:134) | test_vendor_mirrors_remain_transformed_renders | is_file | convert |
| [tests/test_personas.py:238](/Users/jeff/Documents/Code/gzkit/tests/test_personas.py:238) | test_manpage_and_runbook_mention_personas_scaffolding | read_text | convert |
| [tests/test_plan_command.py:35](/Users/jeff/Documents/Code/gzkit/tests/test_plan_command.py:35) | test_skill_version_bumped_to_6_5_or_higher | read_text | convert |
| [tests/test_plan_command.py:48](/Users/jeff/Documents/Code/gzkit/tests/test_plan_command.py:48) | test_last_reviewed_bumped_to_landing_date_or_later | read_text | convert |
| [tests/test_plan_command.py:61](/Users/jeff/Documents/Code/gzkit/tests/test_plan_command.py:61) | test_claude_mirror_is_byte_equivalent_to_canonical | read_bytes | convert |
| [tests/test_rules.py:686](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:686) | test_rules_py_does_not_exist | exists | convert |
| [tests/test_rules.py:694](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:694) | test_rules_init_exists | exists | convert |
| [tests/test_rules.py:805](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:805) | test_req06_pyproject_has_rules_wheel_include | read_text | convert |
| [tests/test_rules.py:1085](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:1085) | test_pyproject_includes_rules_json | open | fold-to-validator |
| [tests/test_rules.py:1109](/Users/jeff/Documents/Code/gzkit/tests/test_rules.py:1109) | test_sync_surfaces_has_rules_classifier_integration | read_text | convert |
| [tests/test_skill_naming.py:41](/Users/jeff/Documents/Code/gzkit/tests/test_skill_naming.py:41) | test_skill_dirs_and_frontmatter_names_are_kebab_case | exists | convert |
| [tests/test_skills.py:181](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:181) | test_skill_files_present_in_package_surface | exists | convert |
| [tests/test_skills.py:186](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:186) | test_skill_files_retained_at_authored_source | is_dir | convert |
| [tests/test_skills.py:240](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:240) | test_all_skill_md_files_have_frontmatter | read_text | convert |
| [tests/test_skills.py:247](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:247) | test_skills_count_is_full | is_dir | convert |
| [tests/test_skills.py:258](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:258) | test_pyproject_includes_skills_package_data | read_text | convert |
| [tests/test_skills.py:454](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:454) | test_skill_surface_sync_rule_documents_bootstrap_semantics | read_text | convert |
| [tests/test_skills.py:478](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:478) | test_init_manpage_documents_skills_scaffolding | read_text | convert |
| [tests/test_skills.py:554](/Users/jeff/Documents/Code/gzkit/tests/test_skills.py:554) | test_skills_package_not_flat_module | exists | convert |
| [tests/test_sync_surfaces.py:529](/Users/jeff/Documents/Code/gzkit/tests/test_sync_surfaces.py:529) | test_manifest_records_skills_control_surface | exists | fold-to-validator |
| [tests/test_sync_surfaces.py:580](/Users/jeff/Documents/Code/gzkit/tests/test_sync_surfaces.py:580) | test_agent_sync_feature_has_req_tagged_scenario | read_text | convert |
| [tests/test_sync_surfaces.py:591](/Users/jeff/Documents/Code/gzkit/tests/test_sync_surfaces.py:591) | test_skill_surface_sync_rule_documents_broadened_sync | read_text | convert |
| [tests/test_taxonomy_validator_nominal.py:75](/Users/jeff/Documents/Code/gzkit/tests/test_taxonomy_validator_nominal.py:75) | test_adr_0017_contains_amendment_block | read_text | convert |
| [tests/test_taxonomy_validator_nominal.py:95](/Users/jeff/Documents/Code/gzkit/tests/test_taxonomy_validator_nominal.py:95) | test_adr_0018_contains_amendment_block | read_text | convert |
| [tests/test_taxonomy_validator_nominal.py:112](/Users/jeff/Documents/Code/gzkit/tests/test_taxonomy_validator_nominal.py:112) | test_trust_audits_audit_annotation_present | read_text | convert |
| [tests/test_taxonomy_validator_nominal.py:130](/Users/jeff/Documents/Code/gzkit/tests/test_taxonomy_validator_nominal.py:130) | test_no_existing_foundation_adr_was_renamed | is_dir | convert |
| [tests/test_templates.py:384](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:384) | test_authored_canonical_surface_populated | is_dir | convert |
| [tests/test_templates.py:399](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:399) | test_dual_surface_byte_parity | is_dir | convert |
| [tests/test_templates.py:436](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:436) | test_skills_subdir_retained | is_dir | convert |
| [tests/test_templates.py:444](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:444) | test_pyproject_includes_template_markdown | read_text | convert |
| [tests/test_templates.py:681](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:681) | test_init_manpage_has_templates_scaffolding_section | read_text | convert |
| [tests/test_templates.py:691](/Users/jeff/Documents/Code/gzkit/tests/test_templates.py:691) | test_runbook_has_templates_section | read_text | convert |

### Undeclared output assertions

| Source | Test/helper | Output source |
|---|---|---|
| [tests/adr/test_patch_release.py:930](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:930) | TestPatchReleaseDryRun.test_dry_run_shows_all_statuses | getvalue |
| [tests/adr/test_patch_release.py:1078](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:1078) | TestPatchReleaseParserRegistration.test_help_exits_zero | stdout |
| [tests/adr/test_patch_release.py:1094](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:1094) | TestPatchReleaseParserRegistration.test_help_contains_flags_and_example | getvalue,stdout |
| [tests/adr/test_patch_release.py:1160](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:1160) | TestPatchReleaseDryRunVersion.test_dry_run_shows_version_no_sync | getvalue |
| [tests/adr/test_patch_release.py:1348](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:1348) | TestPatchReleaseNoVersion.test_no_version_dry_run_still_works | getvalue |
| [tests/adr/test_patch_release.py:2019](/Users/jeff/Documents/Code/gzkit/tests/adr/test_patch_release.py:2019) | TestPatchReleaseFoundationCloseoutsDryRun.test_dry_run_rich_renders_foundation_section | getvalue |
| [tests/adr/test_storage_tiers.py:70](/Users/jeff/Documents/Code/gzkit/tests/adr/test_storage_tiers.py:70) | TestGitCloneRecovery.test_tier_b_rebuild_and_gz_state | stderr,stdout |
| [tests/arb/test_canonical_steps_leaf_import.py:36](/Users/jeff/Documents/Code/gzkit/tests/arb/test_canonical_steps_leaf_import.py:36) | CanonicalStepsLeafImportTests.test_leaf_import_pulls_no_heavy_dependency | stdout |
| [tests/arb/test_step_output_cli.py:24](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:24) | TestStepOutputRetentionCli.invoke | stderr,stdout |
| [tests/arb/test_step_output_cli.py:65](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:65) | TestStepOutputRetentionCli.test_negative_limit_retains_complete_stdout_and_stderr | stderr,stdout |
| [tests/arb/test_step_output_cli.py:72](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:72) | TestStepOutputRetentionCli.test_omitted_limit_preserves_eight_thousand_character_tails | stderr,stdout |
| [tests/arb/test_step_output_cli.py:79](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:79) | TestStepOutputRetentionCli.test_finite_limit_retains_exact_requested_suffix | stderr,stdout |
| [tests/arb/test_step_output_cli.py:93](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:93) | TestStepOutputRetentionCli.test_larger_limit_keeps_shorter_output_without_truncation | stderr,stdout |
| [tests/arb/test_step_output_cli.py:100](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:100) | TestStepOutputRetentionCli.test_unbounded_capture_preserves_failing_commands_exit_status | stderr,stdout |
| [tests/arb/test_step_output_cli.py:112](/Users/jeff/Documents/Code/gzkit/tests/arb/test_step_output_cli.py:112) | TestLongReviewReceiptImport.test_complete_long_review_json_imports_from_the_emitted_run_id | stderr,stdout |
| [tests/arb/test_writer_validator_lockstep.py:78](/Users/jeff/Documents/Code/gzkit/tests/arb/test_writer_validator_lockstep.py:78) | TestAdvisorVerdictReceiptsValidate.test_fresh_import_orders_can_record_and_validate | stderr,stdout |
| [tests/chores/test_ledger_vocabulary_inertness.py:145](/Users/jeff/Documents/Code/gzkit/tests/chores/test_ledger_vocabulary_inertness.py:145) | TheBaselineOnlyEverDecreases.test_current_failed_execution_blocks_despite_previous_report | getvalue |
| [tests/chores/test_session_correction_mining.py:394](/Users/jeff/Documents/Code/gzkit/tests/chores/test_session_correction_mining.py:394) | TestDryRun.test_dry_run_writes_nothing_anywhere | getvalue |
| [tests/cli/test_error_boundary_markup.py:32](/Users/jeff/Documents/Code/gzkit/tests/cli/test_error_boundary_markup.py:32) | TestErrorBoundaryPreservesBracketedText.test_bracketed_spans_in_an_error_message_reach_the_operator | output |
| [tests/cli/test_justify_manpage.py:104](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:104) | GzJustifyManpageContract.test_exit_status_documents_all_codes | assertRegex |
| [tests/cli/test_justify_manpage.py:185](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:185) | GzJustifyCommandDocContract.test_exit_code_table_lists_zero_one_two | assertRegex |
| [tests/cli/test_justify_manpage.py:251](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:251) | GzJustifyGovernanceRunbookContract.test_governance_runbook_cites_invariant_11 | assertRegex |
| [tests/cli/test_justify_manpage.py:284](/Users/jeff/Documents/Code/gzkit/tests/cli/test_justify_manpage.py:284) | GzJustifyGovernanceRunbookContract.test_governance_runbook_5b_subsection_under_create_promote | assertRegex |
| [tests/cli/test_log_level_claims.py:78](/Users/jeff/Documents/Code/gzkit/tests/cli/test_log_level_claims.py:78) | TestLogLevelsFollowSpecControl.test_control_fails_when_logs_reach_stdout | stdout |
| [tests/cli/test_validate_sensitivity_flag.py:72](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_sensitivity_flag.py:72) | TestSensitivityExplain.test_explain_prints_prediction_and_exits_0 | getvalue |
| [tests/cli/test_validate_sensitivity_flag.py:100](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_sensitivity_flag.py:100) | TestSensitivityExplain.test_explain_accepts_comma_and_newline_separated | getvalue |
| [tests/cli/test_validate_sensitivity_flag.py:131](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_sensitivity_flag.py:131) | TestSensitivityJson.test_json_records_have_required_fields | getvalue |
| [tests/cli/test_validate_solo_scope_refusal.py:95](/Users/jeff/Documents/Code/gzkit/tests/cli/test_validate_solo_scope_refusal.py:95) | TestSoloScopeCombinationRefused.test_refusal_names_the_offending_scope_and_a_next_step | getvalue |
| [tests/commands/test_adr_demote.py:90](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:90) | CollisionWithRetainedIntake.test_take_demoted_writes_the_evolved_content_to_pool | output |
| [tests/commands/test_adr_demote.py:126](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:126) | CollisionWithRetainedIntake.test_keep_pool_still_preserves_the_intake | output |
| [tests/commands/test_adr_demote.py:159](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:159) | CollisionWithRetainedIntake.test_promoted_from_does_not_survive_demotion | output |
| [tests/commands/test_adr_demote.py:207](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:207) | CollisionWithRetainedIntake.test_live_covers_into_deleted_briefs_blocks_the_demotion | output |
| [tests/commands/test_adr_demote.py:236](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:236) | CollisionWithRetainedIntake.test_force_overrides_the_covers_block | output |
| [tests/commands/test_adr_demote.py:276](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:276) | TestAdrDemoteCommand.test_dry_run_reports_plan_without_writes | output |
| [tests/commands/test_adr_demote.py:309](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:309) | TestAdrDemoteCommand.test_apply_moves_file_strips_frontmatter_deletes_briefs | output |
| [tests/commands/test_adr_demote.py:347](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:347) | TestAdrDemoteCommand.test_apply_emits_artifact_renamed_with_pool_demotion_payload | output |
| [tests/commands/test_adr_demote.py:392](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:392) | TestAdrDemoteCommand.test_json_output_emits_structured_payload | output |
| [tests/commands/test_adr_demote.py:423](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:423) | TestAdrDemoteCommand.test_rejects_pool_adr_input | output |
| [tests/commands/test_adr_demote.py:440](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:440) | TestAdrDemoteCommand.test_rejects_collision_with_existing_pool_file | output |
| [tests/commands/test_adr_demote.py:467](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:467) | TestAdrDemoteCommand.test_blocks_demotion_when_children_reference_parent | output |
| [tests/commands/test_adr_demote.py:504](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:504) | TestAdrDemoteCommand.test_force_overrides_children_block | output |
| [tests/commands/test_adr_demote.py:541](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:541) | TestAdrDemoteCommand.test_on_collision_keep_pool_deletes_source_and_leaves_pool | output |
| [tests/commands/test_adr_demote.py:587](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:587) | TestAdrDemoteCommand.test_on_collision_keep_pool_reverses_stale_promotion_markers | output |
| [tests/commands/test_adr_demote.py:635](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:635) | TestAdrDemoteCommand.test_on_collision_keep_pool_ignores_unrelated_promoted_to | output |
| [tests/commands/test_adr_demote.py:674](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:674) | TestAdrDemoteCommand.test_on_collision_fail_is_default | output |
| [tests/commands/test_adr_demote.py:704](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:704) | TestAdrDemoteCommand.test_argparse_requires_ghi | output |
| [tests/commands/test_adr_demote.py:731](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:731) | PoolH1Coherence._demote | output |
| [tests/commands/test_adr_demote.py:852](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote.py:852) | PoolKindInvalidSections._demote_with | output |
| [tests/commands/test_adr_demote_parks_obpis.py:50](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote_parks_obpis.py:50) | TestDemoteParksChildObpis.test_apply_emits_one_park_event_per_live_child_obpi | output |
| [tests/commands/test_adr_demote_parks_obpis.py:138](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote_parks_obpis.py:138) | TestDemoteParksChildObpis.test_dry_run_reports_park_plan_without_writing_events | output |
| [tests/commands/test_adr_demote_parks_obpis.py:164](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote_parks_obpis.py:164) | TestDemoteParksChildObpis.test_demotion_with_no_child_obpis_emits_no_park_events | output |
| [tests/commands/test_adr_demote_parks_obpis.py:182](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_demote_parks_obpis.py:182) | TestParkIsReversible.test_promoting_the_pool_adr_unparks_its_obpis | output |
| [tests/commands/test_adr_promote.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:56) | TestAdrPromoteCommand.test_adr_promote_dry_run_reports_actions | output |
| [tests/commands/test_adr_promote.py:87](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:87) | TestAdrPromoteCommand.test_adr_promote_writes_files_and_ledger_rename | output |
| [tests/commands/test_adr_promote.py:145](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:145) | TestAdrPromoteCommand.test_adr_promote_fails_without_target_scope | output |
| [tests/commands/test_adr_promote.py:193](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:193) | TestAdrPromoteCommand.test_adr_promote_rejects_non_pool_source | output |
| [tests/commands/test_adr_promote.py:213](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:213) | TestAdrPromoteCommand.test_adr_promote_reports_non_go_eval_after_applying | output |
| [tests/commands/test_adr_promote.py:379](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:379) | TestAdrPromoteKindFlag.test_help_shows_kind_choices | output |
| [tests/commands/test_adr_promote.py:392](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:392) | TestAdrPromoteKindFlag.test_missing_kind_exits_one_with_recovery | output |
| [tests/commands/test_adr_promote.py:407](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:407) | TestAdrPromoteKindFlag.test_kind_pool_rejected_with_exit_one | output |
| [tests/commands/test_adr_promote.py:429](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:429) | TestAdrPromoteKindFlag.test_foundation_rejects_non_zero_zero_semver | output |
| [tests/commands/test_adr_promote.py:467](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:467) | TestAdrPromoteKindFlag.test_feature_rejects_zero_zero_semver | output |
| [tests/commands/test_adr_promote.py:494](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:494) | TestAdrPromoteKindFlag.test_feature_accepts_non_0_0_x_semver_dryrun | output |
| [tests/commands/test_adr_promote.py:516](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:516) | TestAdrPromoteKindFlag.test_validation_failure_writes_nothing | output |
| [tests/commands/test_adr_promote.py:542](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:542) | TestAdrPromoteKindFlag.test_force_does_not_bypass_kind_validation | output |
| [tests/commands/test_adr_promote.py:569](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:569) | TestAdrPromoteKindFlag.test_promoted_frontmatter_carries_kind_feature | output |
| [tests/commands/test_adr_promote.py:593](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:593) | TestAdrPromoteKindFlag.test_promoted_id_loses_pool_prefix | assertRegex,output |
| [tests/commands/test_adr_promote.py:625](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:625) | TestAdrPromoteKindFlag.test_feature_lands_in_pre_release_bucket | output |
| [tests/commands/test_adr_promote.py:652](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:652) | TestAdrPromoteKindFlag.test_ledger_rename_event_includes_kind_and_semver | output |
| [tests/commands/test_adr_promote.py:735](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:735) | TestAdrPromoteTaxonomyRoundtrip.test_promote_to_feature_passes_taxonomy_validator | output |
| [tests/commands/test_adr_promote.py:863](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:863) | TestPromoteObpiAllowedPathsAndTitleNormalization.test_allowed_paths_strips_line_range_suffix | output |
| [tests/commands/test_adr_promote.py:903](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:903) | TestPromoteObpiAllowedPathsAndTitleNormalization.test_obpi_title_is_short_slug_not_full_bullet_body | output |
| [tests/commands/test_adr_promote.py:964](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:964) | TestLegacyNarrativeDeprecation.test_promote_dry_run_warns_on_legacy_format | output |
| [tests/commands/test_adr_promote.py:1012](/Users/jeff/Documents/Code/gzkit/tests/commands/test_adr_promote.py:1012) | TestDecompositionTablePrecedence.test_dry_run_uses_table_slugs_when_table_present | output |
| [tests/commands/test_arb_cmd.py:97](/Users/jeff/Documents/Code/gzkit/tests/commands/test_arb_cmd.py:97) | TestArbCommands.test_arb_validate_cmd_empty_dir_returns_0 | getvalue |
| [tests/commands/test_arb_cmd.py:106](/Users/jeff/Documents/Code/gzkit/tests/commands/test_arb_cmd.py:106) | TestArbCommands.test_arb_validate_cmd_json_output | getvalue |
| [tests/commands/test_arb_cmd.py:116](/Users/jeff/Documents/Code/gzkit/tests/commands/test_arb_cmd.py:116) | TestArbCommands.test_arb_advise_cmd_empty_dir_returns_0 | getvalue |
| [tests/commands/test_arb_cmd.py:125](/Users/jeff/Documents/Code/gzkit/tests/commands/test_arb_cmd.py:125) | TestArbCommands.test_arb_patterns_cmd_empty_dir_returns_0 | getvalue |
| [tests/commands/test_arb_cmd.py:134](/Users/jeff/Documents/Code/gzkit/tests/commands/test_arb_cmd.py:134) | TestArbCommands.test_arb_patterns_cmd_compact_mode | getvalue |
| [tests/commands/test_attest.py:17](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:17) | TestAttestSemantics.test_attest_lite_requires_gate2 | output |
| [tests/commands/test_attest.py:26](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:26) | TestAttestSemantics.test_attest_heavy_requires_gate3 | output |
| [tests/commands/test_attest.py:38](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:38) | TestAttestSemantics.test_attest_heavy_requires_gate4 | output |
| [tests/commands/test_attest.py:51](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:51) | TestAttestSemantics.test_attest_force_bypass_requires_reason | output |
| [tests/commands/test_attest.py:114](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:114) | TestAttestSemantics.test_attest_rejects_pool_adr | output |
| [tests/commands/test_attest.py:149](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:149) | TestAttestSemantics.test_attest_completed_blocks_on_incomplete_obpis | output |
| [tests/commands/test_attest.py:180](/Users/jeff/Documents/Code/gzkit/tests/commands/test_attest.py:180) | TestAttestSemantics.test_attest_completed_force_bypasses_obpi_check | output |
| [tests/commands/test_audit.py:272](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:272) | TestConfigAndCliAuditCommands.test_check_config_paths_passes_for_valid_layout | output |
| [tests/commands/test_audit.py:287](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:287) | TestConfigAndCliAuditCommands.test_check_config_paths_detects_missing_path | output |
| [tests/commands/test_audit.py:306](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:306) | TestConfigAndCliAuditCommands.test_check_config_paths_rejects_legacy_global_obpi_path | output |
| [tests/commands/test_audit.py:319](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:319) | TestConfigAndCliAuditCommands.test_check_config_paths_rejects_legacy_global_obpi_files | output |
| [tests/commands/test_audit.py:330](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:330) | TestConfigAndCliAuditCommands.test_cli_audit_passes_with_synchronized_docs | output |
| [tests/commands/test_audit.py:338](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:338) | TestConfigAndCliAuditCommands.test_cli_audit_reports_cleanly_when_adopter_has_no_manifest | output |
| [tests/commands/test_audit.py:356](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:356) | TestConfigAndCliAuditCommands.test_cli_audit_flags_a_missing_manifest_on_the_framework_tree | output |
| [tests/commands/test_audit.py:376](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:376) | TestConfigAndCliAuditCommands.test_cli_audit_detects_mismatch | output |
| [tests/commands/test_audit.py:387](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:387) | TestConfigAndCliAuditCommands.test_cli_audit_detects_invalid_readme_quickstart_command | output |
| [tests/commands/test_audit.py:411](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:411) | TestConfigAndCliAuditCommands.test_parity_check_passes_when_contract_surfaces_are_present | output |
| [tests/commands/test_audit.py:419](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:419) | TestConfigAndCliAuditCommands.test_parity_check_fails_when_discovery_index_missing | output |
| [tests/commands/test_audit.py:428](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:428) | TestConfigAndCliAuditCommands.test_readiness_audit_passes_for_initialized_repository | output |
| [tests/commands/test_audit.py:438](/Users/jeff/Documents/Code/gzkit/tests/commands/test_audit.py:438) | TestConfigAndCliAuditCommands.test_readiness_audit_fails_when_required_surface_missing | output |
| [tests/commands/test_brief_reconcile.py:201](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:201) | TestBriefReconcileCommand.test_verb_registered_help | output |
| [tests/commands/test_brief_reconcile.py:245](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:245) | TestBriefReconcileCommand.test_apply_without_attestor_errors | output |
| [tests/commands/test_brief_reconcile.py:287](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:287) | TestBriefReconcileCommand.test_apply_dry_run_does_not_write_or_record_applied | output |
| [tests/commands/test_brief_reconcile.py:370](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:370) | TestBriefReconcileCommand.test_terminal_brief_verdict_is_not_rendered_as_clean | output |
| [tests/commands/test_brief_reconcile.py:390](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:390) | TestBriefReconcileCommand.test_live_clean_brief_still_reports_clean | output |
| [tests/commands/test_brief_reconcile.py:444](/Users/jeff/Documents/Code/gzkit/tests/commands/test_brief_reconcile.py:444) | TestBriefReconcileCommand.test_brief_not_found_errors | output |
| [tests/commands/test_check_advisory_rendering.py:47](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:47) | AdvisoryChannelIsMarked.test_emitted_advisory_is_recoverable_from_the_captured_stream | getvalue |
| [tests/commands/test_check_advisory_rendering.py:70](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:70) | PassingStepsStillSpeak.test_advisory_from_a_passing_step_is_rendered | getvalue |
| [tests/commands/test_check_advisory_rendering.py:84](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:84) | PassingStepsStillSpeak.test_ordinary_passing_output_is_not_rendered | getvalue |
| [tests/commands/test_check_advisory_rendering.py:92](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:92) | PassingStepsStillSpeak.test_simulated_findings_from_the_test_step_are_not_attributed | getvalue |
| [tests/commands/test_check_advisory_rendering.py:112](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:112) | PassingStepsStillSpeak.test_rendered_prose_survives_rich_markup_interpretation | getvalue |
| [tests/commands/test_check_advisory_rendering.py:131](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:131) | PassingStepsStillSpeak.test_failing_step_advisories_are_not_duplicated | getvalue |
| [tests/commands/test_check_advisory_rendering.py:150](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_advisory_rendering.py:150) | EmittersReachTheRenderer.test_surface_delivery_witness_output_is_recognized_as_advisory | getvalue |
| [tests/commands/test_check_diagnostics.py:25](/Users/jeff/Documents/Code/gzkit/tests/commands/test_check_diagnostics.py:25) | TestCheckFailingStepDiagnostics.test_failing_step_output_is_surfaced | getvalue |
| [tests/commands/test_chores.py:106](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:106) | TestChoresCommands.test_chores_list_reads_registry | output |
| [tests/commands/test_chores.py:117](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:117) | TestChoresCommands.test_chores_plan_unknown_slug_shows_blockers | output |
| [tests/commands/test_chores.py:127](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:127) | TestChoresCommands.test_chores_rejects_v1_schema | output |
| [tests/commands/test_chores.py:149](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:149) | TestChoresCommands.test_chores_rejects_shell_operators_in_criteria | output |
| [tests/commands/test_chores.py:181](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:181) | TestChoresCommands.test_chores_rejects_missing_acceptance_json | output |
| [tests/commands/test_chores.py:208](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:208) | TestChoresCommands.test_chores_run_executes_criteria_and_writes_log | output |
| [tests/commands/test_chores.py:228](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:228) | TestChoresCommands.test_chores_run_timeout_returns_nonzero | output |
| [tests/commands/test_chores.py:254](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:254) | TestChoresCommands.test_chores_run_nonzero_exit_returns_nonzero | output |
| [tests/commands/test_chores.py:304](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:304) | TestChoresCommands.test_chores_run_missing_executable | output |
| [tests/commands/test_chores.py:323](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:323) | TestChoresCommands.test_chores_audit_reports_log_presence | output |
| [tests/commands/test_chores.py:345](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:345) | TestChoresCommands.test_chores_rejects_medium_lane | output |
| [tests/commands/test_chores.py:362](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:362) | TestChoresCommands.test_chores_rejects_missing_timeout_seconds | output |
| [tests/commands/test_chores.py:396](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:396) | TestChoresCommands.test_chores_vendor_field_parsed_and_displayed | output |
| [tests/commands/test_chores.py:414](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:414) | TestChoresCommands.test_chores_vendor_filtered_when_no_harness | output |
| [tests/commands/test_chores.py:453](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:453) | TestChoresFileExistsCriterion.test_fileExists_parses_without_command | output |
| [tests/commands/test_chores.py:468](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:468) | TestChoresFileExistsCriterion.test_fileExists_missing_path_reports_blocker | output |
| [tests/commands/test_chores.py:494](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:494) | TestChoresFileExistsCriterion.test_fileExists_run_passes_when_file_present | output |
| [tests/commands/test_chores.py:517](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:517) | TestChoresFileExistsCriterion.test_fileExists_run_fails_when_file_missing | output |
| [tests/commands/test_chores.py:639](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:639) | TestChoreResolver.test_gz_chores_list_explain_distinguishes_source | output |
| [tests/commands/test_chores.py:721](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:721) | TestChoreResolver.test_chores_list_default_no_source_column | output |
| [tests/commands/test_chores.py:768](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:768) | TestChoresDoctor.test_doctor_subcommand_registered | output |
| [tests/commands/test_chores.py:778](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:778) | TestChoresDoctor.test_doctor_healthy_tree_is_noop | output |
| [tests/commands/test_chores.py:796](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:796) | TestChoresDoctor.test_doctor_repairs_missing_slug | output |
| [tests/commands/test_chores.py:818](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:818) | TestChoresDoctor.test_doctor_repairs_damaged_slug | output |
| [tests/commands/test_chores.py:844](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:844) | TestChoresDoctor.test_doctor_preserves_proofs | output |
| [tests/commands/test_chores.py:867](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:867) | TestChoresDoctor.test_doctor_untouches_project_local | output |
| [tests/commands/test_chores.py:892](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:892) | TestChoresDoctor.test_doctor_dry_run_makes_no_changes | output |
| [tests/commands/test_chores.py:914](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores.py:914) | TestChoresDoctor.test_doctor_json_output_parses | output |
| [tests/commands/test_chores_declaration.py:277](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_declaration.py:277) | TestMalformedDeclarationIsRefused.test_each_malformed_declaration_blocks_the_registry | output |
| [tests/commands/test_chores_declaration.py:290](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_declaration.py:290) | TestMalformedDeclarationIsRefused.test_a_declared_no_repair_is_accepted | output |
| [tests/commands/test_chores_declaration.py:313](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_declaration.py:313) | TestUndeclaredChoreIsRefused.test_run_refuses_an_undeclared_chore_before_executing_anything | output |
| [tests/commands/test_chores_declaration.py:327](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_declaration.py:327) | TestUndeclaredChoreIsRefused.test_run_of_a_declared_chore_makes_no_announcement | output |
| [tests/commands/test_chores_declaration.py:338](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_declaration.py:338) | TestUndeclaredChoreIsRefused.test_list_counts_the_undeclared_estate | output |
| [tests/commands/test_chores_propose_ghi.py:68](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_propose_ghi.py:68) | TestChoreProposeGhiTtyConfirm.test_tty_confirm_files_ghi | stdout |
| [tests/commands/test_chores_propose_ghi.py:106](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_propose_ghi.py:106) | TestChoreProposeGhiTtyConfirm.test_ghi_title_pattern | stdout |
| [tests/commands/test_chores_propose_ghi.py:163](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_propose_ghi.py:163) | TestChoreProposeGhiTtyConfirm.test_ghi_body_includes_required_fields | stdout |
| [tests/commands/test_chores_propose_ghi.py:224](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_propose_ghi.py:224) | TestChoreProposeGhiHeadless.test_headless_advisory_only | stdout |
| [tests/commands/test_chores_propose_ghi.py:271](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_propose_ghi.py:271) | TestChoreProposeGhiIdempotent.test_refile_idempotent | stdout |
| [tests/commands/test_chores_status.py:84](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_status.py:84) | TestStatusReportsEveryBandWithoutGating.test_json_carries_each_chore_band | output |
| [tests/commands/test_chores_status.py:124](/Users/jeff/Documents/Code/gzkit/tests/commands/test_chores_status.py:124) | TestStatusReportsEveryBandWithoutGating.test_running_no_chore_to_read_the_status | output |
| [tests/commands/test_common_fixtures.py:72](/Users/jeff/Documents/Code/gzkit/tests/commands/test_common_fixtures.py:72) | TestFixtureRepoQuiescence.test_fixture_repo_is_still_usable_after_quiescing | stdout |
| [tests/commands/test_common_fixtures.py:403](/Users/jeff/Documents/Code/gzkit/tests/commands/test_common_fixtures.py:403) | TestFixtureGitIsolation.test_unguarded_fixture_shape_rewrites_the_hosting_repo | stderr |
| [tests/commands/test_common_fixtures.py:484](/Users/jeff/Documents/Code/gzkit/tests/commands/test_common_fixtures.py:484) | TestFixtureGitIsolation.test_importing_the_tests_package_scrubs_the_process_environment | stderr,stdout |
| [tests/commands/test_common_fixtures.py:557](/Users/jeff/Documents/Code/gzkit/tests/commands/test_common_fixtures.py:557) | TestFixtureGitIsolation.test_real_pre_push_hook_from_a_linked_worktree_leaves_the_hosting_repo_untouched | stderr,stdout |
| [tests/commands/test_common_fixtures.py:606](/Users/jeff/Documents/Code/gzkit/tests/commands/test_common_fixtures.py:606) | TestFixtureGitIsolation.test_real_pre_push_hook_exports_git_dir_and_the_raw_shape_corrupts | stderr,stdout |
| [tests/commands/test_complexity_advise_attest_intrinsic.py:168](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_advise_attest_intrinsic.py:168) | TestComplexityAdviseRegistryEnrichment.test_attested_function_renders_attestation_message | getvalue |
| [tests/commands/test_complexity_advise_attest_intrinsic.py:320](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_advise_attest_intrinsic.py:320) | TestComplexityAdviseAttestIntrinsic.test_attest_intrinsic_emits_event_with_tty | getvalue |
| [tests/commands/test_complexity_advise_attest_intrinsic.py:381](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_advise_attest_intrinsic.py:381) | TestIntrinsicComplexityCliPath.test_decorator_registered_function_takes_attestation_path | getvalue |
| [tests/commands/test_complexity_guide.py:153](/Users/jeff/Documents/Code/gzkit/tests/commands/test_complexity_guide.py:153) | TestComplexityGuideBehavior.test_help_flag_exit_0_sections | getvalue |
| [tests/commands/test_constitute.py:20](/Users/jeff/Documents/Code/gzkit/tests/commands/test_constitute.py:20) | TestConstituteCommand.test_constitute_creates_file | output |
| [tests/commands/test_constitute.py:44](/Users/jeff/Documents/Code/gzkit/tests/commands/test_constitute.py:44) | TestConstituteIdCanonicalization.test_kebab_slug_normalizes_to_canonical_id | output |
| [tests/commands/test_constitute.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_constitute.py:56) | TestConstituteIdCanonicalization.test_trailing_semver_is_preserved | output |
| [tests/commands/test_constitute.py:68](/Users/jeff/Documents/Code/gzkit/tests/commands/test_constitute.py:68) | TestConstituteIdCanonicalization.test_already_canonical_id_is_preserved | output |
| [tests/commands/test_constitute.py:76](/Users/jeff/Documents/Code/gzkit/tests/commands/test_constitute.py:76) | TestConstituteIdCanonicalization.test_scaffolder_validator_roundtrip | output |
| [tests/commands/test_content_advise_rendition.py:37](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_advise_rendition.py:37) | TestContentAdviseRenditionCmd.test_records_verdict_and_exits_zero_for_low_score | output |
| [tests/commands/test_content_advise_rendition.py:69](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_advise_rendition.py:69) | TestContentAdviseRenditionCmd.test_records_verdict_and_exits_zero_for_high_score | output |
| [tests/commands/test_content_cli.py:39](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:39) | TestContentCliSubcommands.test_list_emits_table_not_raw_json | output |
| [tests/commands/test_content_cli.py:53](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:53) | TestContentCliSubcommands.test_list_json_flag_emits_valid_json | output |
| [tests/commands/test_content_cli.py:66](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:66) | TestContentCliSubcommands.test_show_emits_prose_summary | output |
| [tests/commands/test_content_cli.py:81](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:81) | TestContentCliSubcommands.test_show_json_flag_emits_valid_json | output |
| [tests/commands/test_content_cli.py:95](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:95) | TestContentCliSubcommands.test_edit_invalid_content_aborts_no_partial_write | output |
| [tests/commands/test_content_cli.py:124](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:124) | TestContentCliSubcommands.test_render_output_matches_render_function | output |
| [tests/commands/test_content_cli.py:143](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_cli.py:143) | TestContentCliSubcommands.test_help_lists_all_subcommands | output |
| [tests/commands/test_content_commit.py:78](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:78) | TestContentCommitCmd.test_commit_promotes_candidate_and_writes_fingerprint | output |
| [tests/commands/test_content_commit.py:107](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:107) | TestContentCommitCmd.test_commit_is_byte_lossless_for_crlf_candidate | output |
| [tests/commands/test_content_commit.py:182](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:182) | TestCommitAttestationGranularity.test_first_commit_still_requires_attestation | output |
| [tests/commands/test_content_commit.py:195](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:195) | TestCommitAttestationGranularity.test_recommit_of_unchanged_canon_needs_no_attestation | output |
| [tests/commands/test_content_commit.py:228](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:228) | TestCommitAttestationGranularity.test_recommit_after_canon_moved_is_fail_closed_again | output |
| [tests/commands/test_content_commit.py:243](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:243) | TestCommitAttestationGranularity.test_explicit_attestation_still_honored_on_the_exempt_path | output |
| [tests/commands/test_content_commit.py:278](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:278) | TestCommitNamesThePlaybackWriter.test_success_output_names_the_playback_writer | output |
| [tests/commands/test_content_commit.py:291](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_commit.py:291) | TestCommitNamesThePlaybackWriter.test_success_output_states_the_rendition_only_scope | output |
| [tests/commands/test_content_compose.py:112](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:112) | TestContentComposeCmd.test_compose_produces_candidate_and_byte_evidence | output |
| [tests/commands/test_content_compose.py:243](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:243) | TestContentComposeCmd.test_compose_does_not_modify_rendered_surfaces | output |
| [tests/commands/test_content_compose.py:271](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:271) | TestContentComposeCmd.test_compose_reads_piped_stdin_when_not_a_tty | output |
| [tests/commands/test_content_compose.py:294](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:294) | TestContentComposeCmd.test_compose_generates_candidate_and_lineage_on_tty_stdin | output |
| [tests/commands/test_content_compose.py:355](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:355) | TestContentComposeCmd.test_generated_candidate_persists_the_bytes_its_lineage_indexes | output |
| [tests/commands/test_content_compose.py:394](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:394) | TestContentComposeCmd.test_compose_generates_candidate_when_stdin_is_empty_and_not_a_tty | output |
| [tests/commands/test_content_compose.py:414](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:414) | TestContentComposeCmd.test_compose_generates_candidate_when_stdin_is_whitespace_only | output |
| [tests/commands/test_content_compose.py:427](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:427) | TestContentComposeCmd.test_compose_generated_path_refuses_off_route_consumer | output |
| [tests/commands/test_content_compose.py:458](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:458) | TestContentComposeCmd.test_compose_persists_candidate_via_write_bytes_never_write_text | output |
| [tests/commands/test_content_compose.py:506](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:506) | TestContentComposeCmd.test_generated_lineage_spans_index_the_PERSISTED_candidate_bytes | output |
| [tests/commands/test_content_compose.py:585](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:585) | TestContentComposeCmd.test_persisted_lineage_matches_contract_derived_offsets_not_just_the_parser | output |
| [tests/commands/test_content_compose.py:670](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:670) | TestContentComposeCmd.test_mixed_owned_unowned_candidate_matches_contract_derived_literals | output |
| [tests/commands/test_content_compose.py:747](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_compose.py:747) | TestContentComposeCmd.test_explicit_candidate_removes_a_stale_generated_lineage | output |
| [tests/commands/test_content_import.py:46](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:46) | TestContentImportCmd.test_import_canonical_rule_emits_json_exits_0 | output |
| [tests/commands/test_content_import.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:56) | TestContentImportCmd.test_import_unknown_type_exits_1 | output |
| [tests/commands/test_content_import.py:67](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:67) | TestContentImportCmd.test_import_missing_file_exits_1 | output |
| [tests/commands/test_content_import.py:77](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:77) | TestContentImportCmd.test_import_malformed_input_exits_nonzero | output |
| [tests/commands/test_content_import.py:88](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:88) | TestContentImportCmd.test_import_write_is_idempotent | output |
| [tests/commands/test_content_import.py:116](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_import.py:116) | TestContentImportCmd.test_import_type_mismatch_exits_1 | output |
| [tests/commands/test_content_own.py:219](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:219) | TestContentOwnReproducesTheMissingTransition.test_the_reproduced_state_is_refused_by_the_loader_and_by_unown | output |
| [tests/commands/test_content_own.py:232](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:232) | TestContentOwnReproducesTheMissingTransition.test_owning_a_covered_section_flips_the_map_and_lowers_the_floor | output |
| [tests/commands/test_content_own.py:250](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:250) | TestContentOwnReproducesTheMissingTransition.test_the_result_reloads_through_the_real_loader | output |
| [tests/commands/test_content_own.py:263](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:263) | TestContentOwnReproducesTheMissingTransition.test_the_witness_records_the_map_the_evidence_and_the_attestation | output |
| [tests/commands/test_content_own.py:286](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:286) | TestContentOwnReproducesTheMissingTransition.test_a_shrunken_remainder_lowers_the_floor_to_what_is_measured | output |
| [tests/commands/test_content_own.py:313](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:313) | TestContentOwnFailsClosed._assert_nothing_written | output |
| [tests/commands/test_content_own.py:335](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:335) | TestContentOwnFailsClosed.test_an_already_owned_section_is_refused | output |
| [tests/commands/test_content_own.py:351](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:351) | TestContentOwnFailsClosed.test_one_uncovered_content_line_is_refused_and_named | output |
| [tests/commands/test_content_own.py:391](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:391) | TestContentOwnFailsClosed.test_owning_cannot_raise_the_floor_when_another_unowned_section_grew | output |
| [tests/commands/test_content_own.py:411](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:411) | TestContentOwnPreservesUnrelatedState.test_only_the_named_section_moves_and_no_stored_content_changes | output |
| [tests/commands/test_content_own.py:444](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:444) | TestContentOwnIsRecoverable.test_a_retry_completes_an_owning_interrupted_at_the_ledger_append | output |
| [tests/commands/test_content_own.py:463](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:463) | TestContentOwnIsRecoverable.test_a_retry_completes_an_owning_interrupted_before_the_declaration_landed | output |
| [tests/commands/test_content_own.py:486](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:486) | TestContentOwnIsRecoverable.test_a_pending_owning_is_refused_until_coverage_is_restored | output |
| [tests/commands/test_content_own.py:516](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:516) | TestContentOwnIsRecoverable.test_a_completed_owning_is_never_applied_twice | output |
| [tests/commands/test_content_own.py:537](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:537) | TestOwnAndUnownShareOneJournal.test_unown_completes_a_pending_owning_and_does_not_start_its_own | output |
| [tests/commands/test_content_own.py:558](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:558) | TestOwnAndUnownShareOneJournal.test_own_completes_a_pending_unowning_and_does_not_start_its_own | output |
| [tests/commands/test_content_own.py:599](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:599) | TestInterruptedOwningIsRecoverableButNotCurrent.test_the_loader_refuses_and_the_retry_lands_exactly_one_witness | output |
| [tests/commands/test_content_own.py:672](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:672) | TestOwningReplayMayNotMintFromAStalePredecessor.test_a_planted_owning_journal_over_a_stale_declaration_writes_nothing | output |
| [tests/commands/test_content_own.py:826](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:826) | TestContentOwnReplayJournalValidation._assert_refused_by | output |
| [tests/commands/test_content_own.py:895](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:895) | TestGrowthRefusalPrescribesAUsableRecovery.test_a_grown_unowned_section_is_recovered_by_own_after_capture | output |
| [tests/commands/test_content_own.py:938](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:938) | TestGrowthRefusalPrescribesAUsableRecovery.test_a_hand_flipped_map_is_recovered_by_restoring_the_tracked_declaration | output |
| [tests/commands/test_content_own.py:1008](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1008) | TestUnownHelpAttributesTheLoweringPath._normalized_help | output |
| [tests/commands/test_content_own.py:1013](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1013) | TestUnownHelpAttributesTheLoweringPath.test_help_names_own_as_the_lowering_move_and_own_lowers_the_floor | output |
| [tests/commands/test_content_own.py:1023](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1023) | TestUnownHelpAttributesTheLoweringPath.test_help_says_remember_never_touches_the_ratchet_and_it_does_not | output |
| [tests/commands/test_content_own.py:1192](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1192) | TestDeclarationDamageRefusalsPrescribeConditionalRecovery.test_a_null_pointer_with_surviving_events_is_recovered_by_restoring | output |
| [tests/commands/test_content_own.py:1304](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1304) | TestDeclarationDamageRefusalsPrescribeConditionalRecovery.test_restoring_over_a_governed_transition_is_refused_naming_the_chain_tip | output |
| [tests/commands/test_content_own.py:1368](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1368) | TestDeclarationDamageRefusalsPrescribeConditionalRecovery.test_restoring_over_a_governed_owning_is_refused_naming_the_chain_tip | output |
| [tests/commands/test_content_own.py:1443](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_own.py:1443) | TestDeclarationDamageRefusalsPrescribeConditionalRecovery.test_a_surface_removed_in_error_is_repaired_by_restoring_the_surface | output |
| [tests/commands/test_content_reconcile_retirements.py:123](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_reconcile_retirements.py:123) | TestReconcileRetirements.test_dry_run_writes_nothing | output |
| [tests/commands/test_content_remember.py:83](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:83) | TestContentRemember.test_appends_one_entry_with_all_addressed_fields | output |
| [tests/commands/test_content_remember.py:114](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:114) | TestContentRemember.test_does_not_modify_the_rendered_surface | output |
| [tests/commands/test_content_remember.py:136](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:136) | TestContentRemember.test_emits_corpus_entry_appended_ledger_event | output |
| [tests/commands/test_content_remember.py:216](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:216) | TestContentRememberDriftWarning.test_append_survives_and_exit_stays_0_when_the_advisory_fires | output |
| [tests/commands/test_content_remember.py:285](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:285) | TestContentRememberDriftWarning.test_malformed_sidecar_never_costs_the_append_or_the_exit_code | output |
| [tests/commands/test_content_remember.py:318](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:318) | TestContentRememberDriftWarning.test_malformed_manifest_never_costs_the_exit_code | output |
| [tests/commands/test_content_remember.py:405](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_remember.py:405) | TestContentRememberRefusesLiveDuplicates.test_refusal_names_the_entry_already_holding_the_text | output |
| [tests/commands/test_content_retire.py:154](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:154) | TestContentRetireDriftWarning._remember | output |
| [tests/commands/test_content_retire.py:189](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:189) | TestContentRetireDriftWarning.test_warns_naming_the_routed_consumer_not_the_retained_record | output |
| [tests/commands/test_content_retire.py:208](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:208) | TestContentRetireDriftWarning.test_advisory_names_exactly_what_the_gates_grade | output |
| [tests/commands/test_content_retire.py:275](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:275) | TestContentRetireDriftWarning.test_does_not_claim_the_floor_gate_is_at_risk | output |
| [tests/commands/test_content_retire.py:291](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:291) | TestContentRetireDriftWarning.test_silent_when_no_rendition_is_committed | output |
| [tests/commands/test_content_retire.py:300](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:300) | TestContentRetireDriftWarning.test_help_states_both_halves_of_the_consequence | output |
| [tests/commands/test_content_retire.py:322](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:322) | TestContentRetireDriftWarning.test_help_does_not_claim_shrink_only_while_also_claiming_growth | output |
| [tests/commands/test_content_retire.py:344](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:344) | TestContentRetireDriftWarning.test_help_names_the_delta_not_the_row_kind | output |
| [tests/commands/test_content_retire.py:390](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:390) | TestContentRetire._remember | output |
| [tests/commands/test_content_retire.py:409](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:409) | TestContentRetire.test_retired_entry_stops_binding_the_invariant_floor | output |
| [tests/commands/test_content_retire.py:537](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:537) | TestContentRetire.test_double_retirement_fails_closed | output |
| [tests/commands/test_content_retire.py:583](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:583) | TestContentRetireAttestation._remember | output |
| [tests/commands/test_content_retire.py:608](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:608) | TestContentRetireAttestation.test_invariant_tier_retirement_without_reason_fails_closed | output |
| [tests/commands/test_content_retire.py:627](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:627) | TestContentRetireAttestation.test_compressible_tier_still_refuses_whitespace_only_attestor | output |
| [tests/commands/test_content_retire.py:647](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:647) | TestContentRetireAttestation._assert_recovery_commands_run | output |
| [tests/commands/test_content_retire.py:711](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:711) | TestContentRetireAttestation.test_every_retirement_emits_a_ledger_event_the_validator_accepts | output |
| [tests/commands/test_content_retire.py:744](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:744) | TestContentRetireAttestation.test_help_documents_the_attestation_gate_it_actually_enforces | output |
| [tests/commands/test_content_retire.py:762](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:762) | TestContentRetireAttestation.test_attestor_option_help_states_liveness_movement_not_target_tier | output |
| [tests/commands/test_content_retire.py:786](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:786) | TestContentRetireAttestation.test_an_invisible_attestor_is_not_a_named_human | output |
| [tests/commands/test_content_retire.py:807](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:807) | TestContentRetireAttestation.test_retiring_a_tombstone_that_revives_a_floor_entry_needs_an_attestor | output |
| [tests/commands/test_content_retire.py:838](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:838) | TestContentRetireAttestation.test_a_two_hop_tombstone_chain_still_needs_an_attestor | output |
| [tests/commands/test_content_retire.py:882](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:882) | TestContentRetireAttestation.test_the_handler_enforces_reason_without_relying_on_argparse | output |
| [tests/commands/test_content_retire.py:907](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:907) | TestContentRetireAttestation.test_a_legacy_format_row_is_normalized_not_preserved_byte_for_byte | output |
| [tests/commands/test_content_retire.py:1097](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1097) | TestContentRetireAttestation.test_reviving_an_invariant_reports_the_floor_growing_not_shrinking | output |
| [tests/commands/test_content_retire.py:1132](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1132) | TestContentRetireAttestation.test_unchanged_delta_needs_no_attestor_and_says_so | output |
| [tests/commands/test_content_retire.py:1152](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1152) | TestContentRetireAttestation.test_shrank_delta_requires_an_attestor_and_says_so | output |
| [tests/commands/test_content_retire.py:1169](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1169) | TestContentRetireAttestation.test_grew_delta_requires_an_attestor_and_says_so | output |
| [tests/commands/test_content_retire.py:1196](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1196) | TestContentRetireAttestation.test_unchanged_via_tombstone_needs_no_attestor_and_says_so | output |
| [tests/commands/test_content_retire.py:1224](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1224) | TestContentRetireAttestation.test_the_printed_retry_actually_recovers_not_merely_parses | output |
| [tests/commands/test_content_retire.py:1261](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1261) | TestContentRetireAttestation.test_invariant_refusal_cites_a_section_that_resolves | output |
| [tests/commands/test_content_retire.py:1275](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1275) | TestContentRetireAttestation.test_unknown_entry_recovery_command_actually_runs | output |
| [tests/commands/test_content_retire.py:1284](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1284) | TestContentRetireAttestation.test_invariant_tier_retirement_without_attestor_fails_closed | output |
| [tests/commands/test_content_retire.py:1299](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1299) | TestContentRetireAttestation.test_whitespace_only_attestor_fails_closed | output |
| [tests/commands/test_content_retire.py:1317](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1317) | TestContentRetireAttestation.test_whitespace_only_reason_fails_closed | output |
| [tests/commands/test_content_retire.py:1335](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1335) | TestContentRetireAttestation.test_compressible_tier_retirement_without_attestor_succeeds | output |
| [tests/commands/test_content_retire.py:1355](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1355) | TestContentRetireAttestation.test_the_event_witnesses_the_delta_that_required_the_attestor | output |
| [tests/commands/test_content_retire.py:1395](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1395) | TestContentRetireAttestation.test_a_routine_retirement_is_distinguishable_from_a_floor_revival | output |
| [tests/commands/test_content_retire.py:1452](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1452) | TestContentRetireAttestation.test_a_shrinking_retirement_is_witnessed_as_shrank | output |
| [tests/commands/test_content_retire.py:1470](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1470) | TestContentRetireAttestation.test_a_visible_reason_without_letters_is_accepted | output |
| [tests/commands/test_content_retire.py:1499](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1499) | TestContentRetireAttestation.test_an_empty_or_whitespace_reason_is_still_refused_accurately | output |
| [tests/commands/test_content_retire.py:1517](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1517) | TestContentRetireAttestation.test_unknown_entry_recovery_prose_carries_all_three_parts | output |
| [tests/commands/test_content_retire.py:1539](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1539) | TestContentRetireAttestation.test_already_retired_recovery_prose_carries_all_three_parts | output |
| [tests/commands/test_content_retire.py:1562](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1562) | TestContentRetireAttestation.test_absent_corpus_store_recovery_prose_carries_all_three_parts | output |
| [tests/commands/test_content_retire.py:1584](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1584) | TestContentRetireAttestation.test_help_exposes_entry_selector_and_no_text_valued_selector | output |
| [tests/commands/test_content_retire.py:1597](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1597) | TestContentRetireAttestation.test_invariant_retirement_grows_raw_log_but_hides_from_effective_corpus | output |
| [tests/commands/test_content_retire.py:1647](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1647) | TestContentRetireAttestation.test_retirement_emits_appended_then_retired_with_tier_and_attestor | output |
| [tests/commands/test_content_retire.py:1683](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_retire.py:1683) | TestContentRetireAttestation.test_dual_events_survive_the_real_validator_both_tiers | output |
| [tests/commands/test_content_unown.py:269](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:269) | TestContentUnownRaisesTheFloor.test_section_becomes_unowned_and_floor_rises_by_its_span | output |
| [tests/commands/test_content_unown.py:283](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:283) | TestContentUnownRaisesTheFloor.test_ledger_event_carries_all_five_required_fields | output |
| [tests/commands/test_content_unown.py:316](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:316) | TestContentUnownAttestedRoundTrip.test_attested_raise_reloads_cleanly_because_its_chain_resolves | output |
| [tests/commands/test_content_unown.py:343](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:343) | TestContentUnownPartialFailure.test_ledger_append_failure_exits_2_with_declaration_persisted | output |
| [tests/commands/test_content_unown.py:475](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:475) | TestContentUnownIsRecoverable.test_a_post_swap_durability_failure_keeps_the_journal_and_says_so | output |
| [tests/commands/test_content_unown.py:541](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:541) | TestContentUnownIsRecoverable.test_replay_refuses_to_complete_into_a_state_the_loader_would_reject | output |
| [tests/commands/test_content_unown.py:586](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:586) | TestContentUnownIsRecoverable.test_a_retry_completes_a_transition_interrupted_at_the_ledger_append | output |
| [tests/commands/test_content_unown.py:623](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:623) | TestContentUnownIsRecoverable.test_a_recovered_transition_raises_the_floor_exactly_once | output |
| [tests/commands/test_content_unown.py:661](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:661) | TestContentUnownIsRecoverable.test_a_failed_declaration_replace_leaves_no_torn_file_and_no_witness | output |
| [tests/commands/test_content_unown.py:737](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:737) | TestContentUnownFailuresSpeakInProse.test_a_failed_declaration_write_names_the_rule_it_is_forbidden_by | output |
| [tests/commands/test_content_unown.py:765](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:765) | TestContentUnownFailuresSpeakInProse.test_a_failed_ledger_append_names_the_rule_it_is_forbidden_by | output |
| [tests/commands/test_content_unown.py:798](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:798) | TestContentUnownFailuresSpeakInProse.test_a_structurally_wrong_journal_is_refused_in_prose_not_a_traceback | output |
| [tests/commands/test_content_unown.py:924](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:924) | TestContentUnownReplayJournalValidation._assert_refused_and_untouched | output |
| [tests/commands/test_content_unown.py:1167](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1167) | TestContentUnownReplayJournalValidation.test_field_complete_journal_missing_ts_is_refused_not_a_keyerror | output |
| [tests/commands/test_content_unown.py:1224](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1224) | TestAlreadyLandedReplayBindsTheLandedMap.test_a_journal_map_disagreeing_with_the_landed_declaration_is_refused | output |
| [tests/commands/test_content_unown.py:1317](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1317) | TestAlreadyLandedReplayBindsTheLandedMap.test_an_existing_row_wearing_the_same_id_must_match_semantically | output |
| [tests/commands/test_content_unown.py:1418](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1418) | TestContentUnownReadsTheSurfaceInsideTheLock.test_a_surface_edited_on_lock_entry_is_refused_not_committed_stale | output |
| [tests/commands/test_content_unown.py:1485](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1485) | TestContentUnownReadsTheSurfaceInsideTheLock.test_a_non_utf8_surface_is_refused_in_governed_prose_not_a_traceback | output |
| [tests/commands/test_content_unown.py:1509](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1509) | TestContentUnownReadsTheSurfaceInsideTheLock.test_a_surface_edited_after_measurement_is_refused_before_either_store | output |
| [tests/commands/test_content_unown.py:1566](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1566) | TestContentUnownJournalFailureProseIsHonest.test_a_post_rename_journal_fsync_failure_does_not_claim_nothing_written | output |
| [tests/commands/test_content_unown.py:1637](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1637) | TestContentUnownBindsTheSurfaceToTheTransaction.test_an_edit_between_the_check_and_the_commit_is_not_reported_as_success | output |
| [tests/commands/test_content_unown.py:1678](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1678) | TestContentUnownBindsTheSurfaceToTheTransaction.test_an_unchanged_surface_still_completes_cleanly | output |
| [tests/commands/test_content_unown.py:1703](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1703) | TestContentUnownBindsTheSurfaceToTheTransaction.test_replay_refuses_when_a_section_was_renamed_under_the_landed_map | output |
| [tests/commands/test_content_unown.py:1781](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1781) | TestContentUnownRound8._interrupt_at_append | output |
| [tests/commands/test_content_unown.py:1795](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1795) | TestContentUnownRound8.test_replay_finalization_also_verifies_the_journalled_surface | output |
| [tests/commands/test_content_unown.py:1833](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1833) | TestContentUnownRound8.test_replay_of_an_unmoved_surface_still_completes | output |
| [tests/commands/test_content_unown.py:1930](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:1930) | TestContentUnownRound8.test_recovering_a_different_section_never_claims_nothing_written | output |
| [tests/commands/test_content_unown.py:2251](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2251) | TestContentUnownRound9.test_a_second_spelling_of_the_surface_witnesses_the_declared_identity | output |
| [tests/commands/test_content_unown.py:2293](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2293) | TestContentUnownRound9.test_a_request_naming_a_different_file_than_the_declaration_is_refused | output |
| [tests/commands/test_content_unown.py:2361](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2361) | TestContentUnownRound9.test_an_unchanged_crlf_surface_completes | output |
| [tests/commands/test_content_unown.py:2402](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2402) | TestContentUnownRound9.test_a_line_ending_conversion_between_measurement_and_commit_is_refused | output |
| [tests/commands/test_content_unown.py:2467](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2467) | TestContentUnownRound9.test_a_journal_naming_a_second_spelling_of_the_surface_is_refused | output |
| [tests/commands/test_content_unown.py:2544](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2544) | TestContentUnownRound9.test_an_identity_swapped_between_resolution_and_the_lock_is_refused | output |
| [tests/commands/test_content_unown.py:2632](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2632) | TestContentUnownRound9.test_a_request_naming_a_surface_that_does_not_exist_says_so | output |
| [tests/commands/test_content_unown.py:2874](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2874) | TestContentUnownRound9.test_an_interrupted_append_still_resumes_when_the_identity_agrees | output |
| [tests/commands/test_content_unown.py:2902](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:2902) | TestContentUnownRound9.test_an_unreadable_declaration_during_replay_says_so | output |
| [tests/commands/test_content_unown.py:3061](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3061) | TestContentUnownRound9._interrupt_at_append | output |
| [tests/commands/test_content_unown.py:3074](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3074) | TestContentUnownRound9._assert_refused_without_transaction_writes | output |
| [tests/commands/test_content_unown.py:3307](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3307) | TestRecoveryProtocolStateB.test_landed_recovery_retries_the_barrier_and_refuses_while_it_fails | output |
| [tests/commands/test_content_unown.py:3427](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3427) | TestRecoveryProtocolStateE._interrupt_at_append | output |
| [tests/commands/test_content_unown.py:3446](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3446) | TestRecoveryProtocolStateE.test_a_changed_source_recovers_from_retained_material_alone | output |
| [tests/commands/test_content_unown.py:3608](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3608) | TestForgedJournalAdviceIsStateDerived._refusal | output |
| [tests/commands/test_content_unown.py:3773](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3773) | TestRecoveryProtocolStateA.test_the_unlanded_branch_refuses_repeatedly_then_recovers | output |
| [tests/commands/test_content_unown.py:3838](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3838) | TestRecoveryProtocolStateA.test_state_a_recovery_writes_through_the_durable_writer | output |
| [tests/commands/test_content_unown.py:3894](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:3894) | TestRecoveryProtocolStateD.test_a_witnessed_transition_only_clears_its_journal | output |
| [tests/commands/test_content_unown.py:4250](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:4250) | TestMovedSurfaceRefusalNamesItsStateAndPaths.test_the_promised_next_step_actually_reaches_a_loadable_state | output |
| [tests/commands/test_content_unown.py:4316](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:4316) | TestRecoveryProtocolStateDPlusE._reach_d_plus_e | output |
| [tests/commands/test_content_unown.py:4377](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:4377) | TestRecoveryProtocolStateDPlusE.test_the_refusal_never_rewrites_the_operators_newer_bytes | output |
| [tests/commands/test_content_unown.py:4628](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:4628) | TestRecoveryCleanupIsItsOwnObligation._reach_state_d | output |
| [tests/commands/test_content_unown.py:5377](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:5377) | TestLegacyJournalStillObservesTheLiveSurface._reach_state_d_with_a_legacy_journal | output |
| [tests/commands/test_content_unown.py:5428](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:5428) | TestLegacyJournalStillObservesTheLiveSurface.test_an_unchanged_surface_under_a_legacy_journal_still_clears_up | output |
| [tests/commands/test_content_unown.py:5812](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:5812) | TestEntryBoundarySweepIsNotClaimedAway._assert_swept_then_refused | output |
| [tests/commands/test_content_unown.py:6137](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6137) | _RolledBackUnderAPendingJournal._rolled_back_state | output |
| [tests/commands/test_content_unown.py:6220](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6220) | TestDeclarationRolledBackUnderAPendingJournal.test_a_valid_journal_prescribes_the_retry_and_does_not_make_the_stale_state_current | output |
| [tests/commands/test_content_unown.py:6284](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6284) | TestDeclarationRolledBackUnderAPendingJournal.test_a_second_attested_transition_is_beyond_one_journal | output |
| [tests/commands/test_content_unown.py:6451](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6451) | TestDeclarationRolledBackUnderAPendingJournal.test_an_unparseable_successor_is_a_governed_refusal_on_the_command_path_too | output |
| [tests/commands/test_content_unown.py:6529](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6529) | TestDeclarationRolledBackUnderAPendingJournal.test_replaying_a_planted_journal_cannot_make_the_stale_state_authoritative | output |
| [tests/commands/test_content_unown.py:6578](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6578) | TestDeclarationRolledBackUnderAPendingJournal.test_a_ledger_row_that_disagrees_with_the_journal_is_not_its_witness | output |
| [tests/commands/test_content_unown.py:6698](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6698) | TestReplayMayNotMintFromAStalePredecessor.test_a_planted_journal_over_a_stale_declaration_writes_nothing | output |
| [tests/commands/test_content_unown.py:6734](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6734) | TestReplayMayNotMintFromAStalePredecessor.test_the_refusals_prescribed_recovery_is_executed_and_reaches_a_working_surface | output |
| [tests/commands/test_content_unown.py:6791](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6791) | TestReplayMayNotMintFromAStalePredecessor.test_more_rows_than_one_journal_accounts_for_are_refused | output |
| [tests/commands/test_content_unown.py:6819](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6819) | TestReplayMayNotMintFromAStalePredecessor.test_a_predecessor_absent_from_the_chain_is_refused | output |
| [tests/commands/test_content_unown.py:6845](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6845) | TestReplayMayNotMintFromAStalePredecessor.test_a_transition_from_the_current_declaration_still_succeeds | output |
| [tests/commands/test_content_unown.py:6877](/Users/jeff/Documents/Code/gzkit/tests/commands/test_content_unown.py:6877) | TestJournalIsClearedOnlyAfterADurableWitness.test_the_ledger_row_reaches_the_device_before_the_journal_is_removed | output |
| [tests/commands/test_context_cmd.py:65](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:65) | TestContextCmdCore.test_help_documents_adr_positional | output |
| [tests/commands/test_context_cmd.py:73](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:73) | TestContextCmdCore.test_resolves_adr_and_exits_zero | output |
| [tests/commands/test_context_cmd.py:85](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:85) | TestContextCmdCore.test_payload_contains_adr_body_verbatim | output |
| [tests/commands/test_context_cmd.py:101](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:101) | TestContextCmdCore.test_payload_contains_all_obpi_briefs | output |
| [tests/commands/test_context_cmd.py:126](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:126) | TestContextCmdCore.test_payload_lists_covers_test_paths_grouped_by_req | output |
| [tests/commands/test_context_cmd.py:166](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:166) | TestContextCmdCore.test_payload_governance_current_gate_derives_from_ledger | output |
| [tests/commands/test_context_cmd.py:250](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:250) | TestContextCmdCore.test_unresolvable_adr_id_exits_nonzero_with_blockers | output |
| [tests/commands/test_context_cmd.py:262](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:262) | TestContextCmdCore.test_payload_is_plain_markdown_no_ansi | output |
| [tests/commands/test_context_cmd.py:281](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:281) | TestContextCmdSlim.test_help_documents_slim_flag | output |
| [tests/commands/test_context_cmd.py:289](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:289) | TestContextCmdSlim.test_slim_omits_governance_section | output |
| [tests/commands/test_context_cmd.py:305](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:305) | TestContextCmdSlim.test_slim_preserves_adr_body_and_obpi_briefs | output |
| [tests/commands/test_context_cmd.py:328](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:328) | TestContextCmdSlim.test_slim_delta_is_only_governance_section | output |
| [tests/commands/test_context_cmd.py:362](/Users/jeff/Documents/Code/gzkit/tests/commands/test_context_cmd.py:362) | TestContextCmdSlim.test_obpi01_default_mode_still_includes_governance_section | output |
| [tests/commands/test_foundation_kind_closed.py:84](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:84) | TestFoundationKindClosedAtAuthoringTime.test_plan_create_foundation_kind_rejected_with_three_part_prose | output |
| [tests/commands/test_foundation_kind_closed.py:124](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:124) | TestFoundationKindClosedAtAuthoringTime.test_plan_create_foundation_kind_rejected_before_semver_binding_check | output |
| [tests/commands/test_foundation_kind_closed.py:152](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:152) | TestFoundationKindClosedAtAuthoringTime.test_adr_promote_foundation_kind_rejected_with_three_part_prose | output |
| [tests/commands/test_foundation_kind_closed.py:203](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:203) | TestFoundationKindClosedAtAuthoringTime.test_adr_promote_foundation_kind_rejected_before_semver_binding_check | output |
| [tests/commands/test_foundation_kind_closed.py:363](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:363) | TestFoundationKindClosedAtAuthoringTime.test_interview_adr_foundation_semver_rejected_with_three_part_prose | output |
| [tests/commands/test_foundation_kind_closed.py:419](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:419) | TestFoundationKindClosedAtAuthoringTime.test_interview_adr_feature_semver_still_passes_unchanged | output |
| [tests/commands/test_foundation_kind_closed.py:479](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:479) | TestFoundationKindClosedAtAuthoringTime.test_plan_create_feature_kind_still_passes_unchanged | output |
| [tests/commands/test_foundation_kind_closed.py:499](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:499) | TestFoundationKindClosedAtAuthoringTime.test_plan_create_pool_kind_still_passes_unchanged | output |
| [tests/commands/test_foundation_kind_closed.py:510](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:510) | TestFoundationKindClosedAtAuthoringTime.test_adr_promote_feature_kind_still_passes_unchanged | output |
| [tests/commands/test_foundation_kind_closed.py:552](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:552) | TestFoundationClosureIsProjectLocal.test_adopter_can_author_a_foundation_adr | output |
| [tests/commands/test_foundation_kind_closed.py:582](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:582) | TestFoundationClosureIsProjectLocal.test_closing_the_kind_restores_the_refusal | output |
| [tests/commands/test_foundation_kind_closed.py:629](/Users/jeff/Documents/Code/gzkit/tests/commands/test_foundation_kind_closed.py:629) | TestFoundationClosureIsProjectLocal.test_gz_init_scaffolds_adopters_with_the_kind_open | output |
| [tests/commands/test_frontmatter_reconcile.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_frontmatter_reconcile.py:56) | TestFrontmatterReconcileCli.test_reconcile_emits_schema_valid_receipt | output |
| [tests/commands/test_frontmatter_reconcile.py:93](/Users/jeff/Documents/Code/gzkit/tests/commands/test_frontmatter_reconcile.py:93) | TestFrontmatterReconcileCli.test_unmapped_status_term_exits_policy_breach | output |
| [tests/commands/test_gates_frontmatter.py:58](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:58) | TestGate1FrontmatterIntegration.test_gate1_passes_when_no_drift | output |
| [tests/commands/test_gates_frontmatter.py:68](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:68) | TestGate1FrontmatterIntegration.test_gate1_blocks_on_status_drift_with_exit_3 | output |
| [tests/commands/test_gates_frontmatter.py:79](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:79) | TestGate1FrontmatterIntegration.test_gate1_drift_listing_names_field_and_values | output |
| [tests/commands/test_gates_frontmatter.py:91](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:91) | TestGate1FrontmatterIntegration.test_gate1_error_names_recovery_command_per_field | output |
| [tests/commands/test_gates_frontmatter.py:103](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:103) | TestGate1FrontmatterIntegration.test_gates_rejects_skip_frontmatter_bypass_flag | output |
| [tests/commands/test_gates_frontmatter.py:114](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:114) | TestGate1FrontmatterIntegration.test_gate1_status_drift_displays_canonical_vocab_term | output |
| [tests/commands/test_gates_frontmatter.py:129](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:129) | TestGate1FrontmatterIntegration.test_gate1_unmapped_status_term_surfaces_as_unmapped | output |
| [tests/commands/test_gates_frontmatter.py:141](/Users/jeff/Documents/Code/gzkit/tests/commands/test_gates_frontmatter.py:141) | TestGate1FrontmatterIntegration.test_gate1_runs_to_completion | output |
| [tests/commands/test_init.py:33](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:33) | TestInitCommand.test_init_creates_codex_config_baseline | output |
| [tests/commands/test_init.py:80](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:80) | TestInitCommand.test_init_rerun_repairs_instead_of_failing | output |
| [tests/commands/test_init.py:93](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:93) | TestInitCommand.test_init_rerun_reports_nothing_to_repair | output |
| [tests/commands/test_init.py:102](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:102) | TestInitCommand.test_init_repair_preserves_operator_codex_config | output |
| [tests/commands/test_init.py:211](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:211) | TestInitProjectSkeleton.test_repair_partial_skeleton_fills_gaps | output |
| [tests/commands/test_init.py:751](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:751) | TestInitLeavesASyncedTree.test_init_leaves_no_sync_parity_drift | output |
| [tests/commands/test_init.py:813](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:813) | TestScaffoldedManifestIsSelfConsistent.test_init_creates_the_readme_its_manifest_names | output |
| [tests/commands/test_init.py:822](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:822) | TestScaffoldedManifestIsSelfConsistent.test_scaffolded_pyproject_names_no_missing_file | output |
| [tests/commands/test_init.py:840](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init.py:840) | TestScaffoldedManifestIsSelfConsistent.test_a_pre_existing_readme_is_left_alone | output |
| [tests/commands/test_init_update.py:140](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:140) | TestCanonicalVersionMarkerContract.test_marker_pattern_matches_documented_form | assertRegex |
| [tests/commands/test_init_update.py:155](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:155) | TestCanonicalVersionMarkerContract.test_marker_composes_with_skill_version_frontmatter | assertRegex |
| [tests/commands/test_init_update.py:181](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:181) | TestInitManpageDocumentsUpdateMode.test_documents_three_modes | assertRegex |
| [tests/commands/test_init_update.py:193](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:193) | TestInitManpageDocumentsUpdateMode.test_documents_marker_contract | assertRegex |
| [tests/commands/test_init_update.py:197](/Users/jeff/Documents/Code/gzkit/tests/commands/test_init_update.py:197) | TestInitManpageDocumentsUpdateMode.test_documents_exit_code_contract | assertRegex |
| [tests/commands/test_insights_cmd.py:34](/Users/jeff/Documents/Code/gzkit/tests/commands/test_insights_cmd.py:34) | TestInsightsRemember.test_appends_one_valid_line_for_improvement_payload | output |
| [tests/commands/test_interview_cmd.py:47](/Users/jeff/Documents/Code/gzkit/tests/commands/test_interview_cmd.py:47) | TestInterviewAdrCanonicalScaffolding.test_bare_adr_id_rejected_before_emission | output |
| [tests/commands/test_interview_cmd.py:81](/Users/jeff/Documents/Code/gzkit/tests/commands/test_interview_cmd.py:81) | TestInterviewAdrCanonicalScaffolding.test_feature_adr_routes_to_pre_release_slug_package | output |
| [tests/commands/test_interview_cmd.py:110](/Users/jeff/Documents/Code/gzkit/tests/commands/test_interview_cmd.py:110) | TestInterviewAdrCanonicalScaffolding.test_adr_created_event_id_derives_from_on_disk_directory | output |
| [tests/commands/test_interview_cmd.py:138](/Users/jeff/Documents/Code/gzkit/tests/commands/test_interview_cmd.py:138) | TestInterviewAdrCanonicalScaffolding.test_rendered_frontmatter_substitutes_kind_placeholder | output |
| [tests/commands/test_issue_cmd.py:176](/Users/jeff/Documents/Code/gzkit/tests/commands/test_issue_cmd.py:176) | TestIssueFileCli.test_help_exits_zero | output |
| [tests/commands/test_issue_cmd.py:185](/Users/jeff/Documents/Code/gzkit/tests/commands/test_issue_cmd.py:185) | TestIssueFileCli.test_dry_run_emits_provenance_trailer | output |
| [tests/commands/test_issue_cmd.py:205](/Users/jeff/Documents/Code/gzkit/tests/commands/test_issue_cmd.py:205) | TestIssueFileCli.test_live_invocation_routes_to_tvproductions_gzkit | output |
| [tests/commands/test_issue_cmd.py:232](/Users/jeff/Documents/Code/gzkit/tests/commands/test_issue_cmd.py:232) | TestIssueFileCli.test_body_without_gzkit_surface_hard_rejects | output |
| [tests/commands/test_json_document_rendering.py:34](/Users/jeff/Documents/Code/gzkit/tests/commands/test_json_document_rendering.py:34) | TestJsonDocumentSurvivesAHostileConsole.test_chores_doctor | output |
| [tests/commands/test_json_document_rendering.py:43](/Users/jeff/Documents/Code/gzkit/tests/commands/test_json_document_rendering.py:43) | TestJsonDocumentSurvivesAHostileConsole.test_ledger_corrections | output |
| [tests/commands/test_json_document_rendering.py:52](/Users/jeff/Documents/Code/gzkit/tests/commands/test_json_document_rendering.py:52) | TestJsonDocumentSurvivesAHostileConsole.test_handoff_rulings_carry_bracketed_rulings_verbatim | getvalue |
| [tests/commands/test_justify_authoring_hints.py:67](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_authoring_hints.py:67) | TestJustifyComplexityHintsIntegration.test_py_paths_with_crossings_injects_hints_heading | getvalue |
| [tests/commands/test_justify_authoring_hints.py:107](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_authoring_hints.py:107) | TestJustifyComplexityHintsIntegration.test_no_py_paths_skips_hints_heading | getvalue |
| [tests/commands/test_justify_authoring_hints.py:146](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_authoring_hints.py:146) | TestJustifyComplexityHintsIntegration.test_py_paths_no_crossings_skips_hints_heading | getvalue |
| [tests/commands/test_justify_authoring_hints.py:185](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_authoring_hints.py:185) | TestJustifyComplexityHintsIntegration.test_engine_failure_fails_open | getvalue |
| [tests/commands/test_justify_cmd.py:84](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:84) | TestAdrRejection.test_exact_message_and_exit_one | getvalue |
| [tests/commands/test_justify_cmd.py:92](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:92) | TestAdrRejection.test_case_insensitive_rejection | getvalue |
| [tests/commands/test_justify_cmd.py:102](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:102) | TestDraftSlugPrecondition.test_draft_with_save_missing_slug_exits_one | getvalue |
| [tests/commands/test_justify_cmd.py:131](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:131) | TestHappyPaths.test_default_emits_scaffold_to_stdout | getvalue |
| [tests/commands/test_justify_cmd.py:182](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:182) | TestOutputPathConflict.test_output_path_exists_exits_one | getvalue |
| [tests/commands/test_justify_cmd.py:206](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:206) | TestExitCodeDiscipline.test_anchor_resolution_error_maps_to_exit_two | getvalue |
| [tests/commands/test_justify_cmd.py:218](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:218) | TestExitCodeDiscipline.test_anchor_value_error_maps_to_exit_one | getvalue |
| [tests/commands/test_justify_cmd.py:230](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:230) | TestExitCodeDiscipline.test_missing_anchor_and_draft_exits_one | getvalue |
| [tests/commands/test_justify_cmd.py:240](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:240) | TestDeterminism.test_identical_inputs_produce_identical_outputs | getvalue |
| [tests/commands/test_justify_cmd.py:292](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_cmd.py:292) | TestHelpSurface.test_help_lists_anchor_and_all_flags | assertRegex,getvalue |
| [tests/commands/test_justify_validate.py:42](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:42) | TestValidateMissingFile.test_missing_file_positional_exits_one | getvalue |
| [tests/commands/test_justify_validate.py:50](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:50) | TestValidateMissingFile.test_nonexistent_file_exits_one | getvalue |
| [tests/commands/test_justify_validate.py:62](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:62) | TestValidateCompleteFixture.test_complete_fixture_exits_zero_with_is_complete | getvalue |
| [tests/commands/test_justify_validate.py:76](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:76) | TestValidateIncompleteFixture.test_incomplete_fixture_exits_one_listing_unfilled_ordinals | getvalue |
| [tests/commands/test_justify_validate.py:95](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:95) | TestValidateMalformedFixture.test_malformed_fixture_exits_two_with_parse_error | getvalue |
| [tests/commands/test_justify_validate.py:108](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:108) | TestValidateJsonOutput.test_json_output_for_complete_fixture_is_parseable | getvalue |
| [tests/commands/test_justify_validate.py:123](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:123) | TestValidateJsonOutput.test_json_output_for_incomplete_fixture_contains_unfilled_ordinals | getvalue |
| [tests/commands/test_justify_validate.py:135](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:135) | TestValidateJsonOutput.test_json_output_for_malformed_fixture_carries_parse_error | getvalue |
| [tests/commands/test_justify_validate.py:150](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:150) | TestValidateHelpSurface.test_help_output_documents_exit_codes_and_examples | stdout |
| [tests/commands/test_justify_validate.py:171](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:171) | TestValidateCmdRoutingEndToEnd.test_justify_cmd_routes_validate_subverb | getvalue |
| [tests/commands/test_justify_validate.py:187](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:187) | TestValidateSubprocessSmoke.test_subprocess_validate_on_complete_fixture | stdout |
| [tests/commands/test_justify_validate.py:200](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:200) | TestValidateSubprocessSmoke.test_subprocess_validate_on_malformed_fixture | stdout |
| [tests/commands/test_justify_validate.py:217](/Users/jeff/Documents/Code/gzkit/tests/commands/test_justify_validate.py:217) | TestCliAuditCoverage.test_cli_audit_exits_zero_after_validate_subverb_lands | stderr,stdout |
| [tests/commands/test_knowledge.py:47](/Users/jeff/Documents/Code/gzkit/tests/commands/test_knowledge.py:47) | TestKnowledgeGenerate.test_knowledge_help_documents_verb | output |
| [tests/commands/test_knowledge.py:74](/Users/jeff/Documents/Code/gzkit/tests/commands/test_knowledge.py:74) | TestKnowledgeRefresh.test_refresh_is_idempotent | output |
| [tests/commands/test_knowledge.py:154](/Users/jeff/Documents/Code/gzkit/tests/commands/test_knowledge.py:154) | TestKnowledgeSmoke.test_cli_smoke_generate_then_refresh | output |
| [tests/commands/test_lint.py:11](/Users/jeff/Documents/Code/gzkit/tests/commands/test_lint.py:11) | TestLintCommand.test_lint_runs | output |
| [tests/commands/test_migrate_semver.py:16](/Users/jeff/Documents/Code/gzkit/tests/commands/test_migrate_semver.py:16) | TestMigrateSemverCommand.test_migrate_semver_renames_status_output | output |
| [tests/commands/test_migrate_semver.py:36](/Users/jeff/Documents/Code/gzkit/tests/commands/test_migrate_semver.py:36) | TestMigrateSemverCommand.test_migrate_semver_renames_release_hardening_to_non_semver_pool_id | output |
| [tests/commands/test_migrate_semver.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_migrate_semver.py:56) | TestMigrateSemverCommand.test_migrate_semver_renames_pool_semver_ids_to_non_semver_ids | output |
| [tests/commands/test_migrate_semver.py:161](/Users/jeff/Documents/Code/gzkit/tests/commands/test_migrate_semver.py:161) | TestMigrateSemverDiskDrift.test_disk_drift_dry_run_reports_without_writing_ledger | output |
| [tests/commands/test_obpi_acceptance_cli.py:88](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:88) | TestAcceptanceProcessExit.initialize | stderr,stdout |
| [tests/commands/test_obpi_acceptance_cli.py:93](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:93) | TestAcceptanceProcessExit.prove | stderr,stdout |
| [tests/commands/test_obpi_acceptance_cli.py:105](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:105) | TestAcceptanceProcessExit.import_review | stderr,stdout |
| [tests/commands/test_obpi_acceptance_cli.py:114](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:114) | TestAcceptanceProcessExit.test_blocked_readiness_exits_three_at_both_stages_and_entrypoints | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:127](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:127) | TestAcceptanceProcessExit.test_rejected_init_cannot_exit_success_or_change_recorded_author | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:137](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:137) | TestAcceptanceProcessExit.test_documented_semantic_proof_exits_zero_and_surviving_control_exits_three | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:149](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:149) | TestAcceptanceProcessExit.test_rejected_proof_request_exits_three | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:154](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:154) | TestAcceptanceProcessExit.test_missing_and_malformed_receipts_exit_three_without_appending | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:166](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:166) | TestAcceptanceProcessExit.test_successful_reviews_and_satisfied_readiness_exit_zero | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:176](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:176) | TestAcceptanceProcessExit.test_recording_refutation_succeeds_while_readiness_stays_blocked | stdout |
| [tests/commands/test_obpi_acceptance_cli.py:190](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_acceptance_cli.py:190) | TestAcceptanceProcessExit.test_human_review_refusal_and_success_reach_the_process_exit | stderr,stdout |
| [tests/commands/test_obpi_audit_cmd.py:45](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_audit_cmd.py:45) | TestObpiAuditCmd.test_single_obpi_produces_criteria_evaluated | output |
| [tests/commands/test_obpi_audit_cmd.py:77](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_audit_cmd.py:77) | TestObpiAuditCmd.test_adr_scope_produces_audits_list | output |
| [tests/commands/test_obpi_block_cmd.py:37](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_block_cmd.py:37) | TestObpiBlockCommand.test_block_writes_the_event_with_both_payload_fields | output |
| [tests/commands/test_obpi_block_cmd.py:72](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_block_cmd.py:72) | TestObpiBlockCommand.test_block_dry_run_writes_nothing | output |
| [tests/commands/test_obpi_block_cmd.py:97](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_block_cmd.py:97) | TestObpiUnblockCommand.test_unblock_writes_the_ruling_verbatim | output |
| [tests/commands/test_obpi_complete_subprocess_decode.py:20](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_complete_subprocess_decode.py:20) | TestObpiCompleteSubprocessDecode.test_run_captured_tolerates_non_utf8_grandchild_stdout | stdout |
| [tests/commands/test_obpi_pipeline.py:152](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:152) | TestObpiPipelineCommand.test_full_launch_accepts_short_id_and_creates_markers | output |
| [tests/commands/test_obpi_pipeline.py:188](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:188) | TestObpiPipelineCommand.test_blocks_when_matching_receipt_verdict_is_fail | output |
| [tests/commands/test_obpi_pipeline.py:213](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:213) | TestObpiPipelineCommand.test_verify_runs_commands_and_preserves_markers | output |
| [tests/commands/test_obpi_pipeline.py:273](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:273) | TestObpiPipelineCommand.test_verify_dispatches_baseline_arb_gates_concurrently | output |
| [tests/commands/test_obpi_pipeline.py:356](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:356) | TestObpiPipelineCommand.test_verify_failure_persists_blockers_and_resume_point | output |
| [tests/commands/test_obpi_pipeline.py:403](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:403) | TestObpiPipelineCommand.test_ceremony_prints_next_steps_and_preserves_markers | output |
| [tests/commands/test_obpi_pipeline.py:459](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:459) | TestObpiPipelineCommand.test_ceremony_lite_parent_requires_human_attestation | output |
| [tests/commands/test_obpi_pipeline.py:491](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:491) | TestObpiPipelineCommand.test_ceremony_foundation_parent_requires_human_attestation | output |
| [tests/commands/test_obpi_pipeline.py:525](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:525) | TestObpiPipelineCommand.test_sync_stage_requires_attestor | output |
| [tests/commands/test_obpi_pipeline.py:539](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:539) | TestObpiPipelineCommand.test_sync_stage_executes_and_clears_markers | output |
| [tests/commands/test_obpi_pipeline.py:604](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:604) | TestObpiPipelineCommand.test_sync_stage_accounting_commit_failure_is_nonfatal | output |
| [tests/commands/test_obpi_pipeline.py:651](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_pipeline.py:651) | TestObpiPipelineCommand.test_blocks_when_obpi_is_ledger_completed | output |
| [tests/commands/test_obpi_precomplete.py:512](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_precomplete.py:512) | TestPrecompleteCliEndToEnd.test_exits_3_when_brief_missing | output |
| [tests/commands/test_obpi_precomplete.py:520](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_precomplete.py:520) | TestPrecompleteCliEndToEnd.test_exits_3_when_preconditions_fail | output |
| [tests/commands/test_obpi_precomplete.py:535](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_precomplete.py:535) | TestPrecompleteCliEndToEnd.test_exits_0_when_all_preconditions_met | output |
| [tests/commands/test_obpi_precomplete.py:556](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_precomplete.py:556) | TestPrecompleteCliEndToEnd.test_json_output_shape | output |
| [tests/commands/test_obpi_stages.py:40](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_stages.py:40) | TestVerifyStageCommandShapeClassification.test_compound_verification_command_raises_before_dispatch | getvalue |
| [tests/commands/test_obpi_validate_cmd.py:35](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_validate_cmd.py:35) | TestObpiValidateCommand.test_obpi_validate_prints_blockers_for_out_of_scope_changes | output |
| [tests/commands/test_obpi_validate_cmd.py:75](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_validate_cmd.py:75) | TestObpiValidateCommand.test_obpi_validate_passes_for_allowlisted_changes | output |
| [tests/commands/test_obpi_validate_cmd.py:130](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_validate_cmd.py:130) | TestObpiValidateCommand.test_obpi_validate_adr_flag_batch_validates | output |
| [tests/commands/test_obpi_validate_cmd.py:173](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_validate_cmd.py:173) | TestObpiValidateCommand.test_obpi_validate_authored_flag_blocks_thin_draft | output |
| [tests/commands/test_obpi_validate_cmd.py:201](/Users/jeff/Documents/Code/gzkit/tests/commands/test_obpi_validate_cmd.py:201) | TestObpiValidateCommand.test_obpi_validate_authored_flag_passes_substantive_draft | output |
| [tests/commands/test_ontology.py:185](/Users/jeff/Documents/Code/gzkit/tests/commands/test_ontology.py:185) | TestResense.test_resense_diffs_against_the_persisted_baseline | getvalue |
| [tests/commands/test_personas_cmd.py:46](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:46) | TestPersonasListCmd.test_personas_list_no_dir | output |
| [tests/commands/test_personas_cmd.py:56](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:56) | TestPersonasListCmd.test_personas_list_empty_dir | output |
| [tests/commands/test_personas_cmd.py:70](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:70) | TestPersonasListCmd.test_personas_list_with_file | output |
| [tests/commands/test_personas_cmd.py:80](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:80) | TestPersonasListCmd.test_personas_list_json_mode | output |
| [tests/commands/test_personas_cmd.py:95](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:95) | TestPersonasListCmd.test_personas_list_malformed_warns | output |
| [tests/commands/test_personas_cmd.py:105](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:105) | TestPersonasListCmd.test_personas_list_json_empty_dir | output |
| [tests/commands/test_personas_cmd.py:127](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:127) | TestPersonasDriftCmd.test_drift_human_output | output |
| [tests/commands/test_personas_cmd.py:137](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:137) | TestPersonasDriftCmd.test_drift_json_output | output |
| [tests/commands/test_personas_cmd.py:150](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:150) | TestPersonasDriftCmd.test_drift_single_persona | output |
| [tests/commands/test_personas_cmd.py:163](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:163) | TestPersonasDriftCmd.test_drift_exit_0_when_no_drift | output |
| [tests/commands/test_personas_cmd.py:178](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:178) | TestPersonasDriftCmd.test_drift_exit_3_on_policy_breach | output |
| [tests/commands/test_personas_cmd.py:198](/Users/jeff/Documents/Code/gzkit/tests/commands/test_personas_cmd.py:198) | TestPersonasDriftCmd.test_drift_help | output |
| [tests/commands/test_plan.py:30](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:30) | TestPlanCommand.test_plan_create_requires_kind_flag | output |
| [tests/commands/test_plan.py:50](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:50) | TestPlanCommand.test_plan_create_feature_rejects_0_0_x_semver | output |
| [tests/commands/test_plan.py:78](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:78) | TestPlanCommand.test_plan_create_pool_routes_to_flat_pool_file_without_kind_field | output |
| [tests/commands/test_plan.py:106](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:106) | TestPlanCommand.test_plan_create_rejection_writes_no_file_no_ledger_event | output |
| [tests/commands/test_plan.py:145](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:145) | TestPlanCommand.test_plan_create_feature_routes_to_pre_release_dir_per_adr_folder | output |
| [tests/commands/test_plan.py:168](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:168) | TestPlanCommand.test_plan_creates_file_with_scorecard | output |
| [tests/commands/test_plan.py:187](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:187) | TestPlanCommand.test_plan_registers_adr_in_ledger | output |
| [tests/commands/test_plan.py:210](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:210) | TestPlanCommand.test_plan_canonicalizes_short_form_adr_parent | output |
| [tests/commands/test_plan.py:264](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:264) | TestPlanCanonicalIdComposition.test_slug_name_produces_canonical_slugged_id | output |
| [tests/commands/test_plan.py:294](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:294) | TestPlanCanonicalIdComposition.test_bare_semver_name_is_rejected | output |
| [tests/commands/test_plan.py:336](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:336) | TestPlanCanonicalIdComposition.test_bare_adr_prefixed_name_is_rejected | output |
| [tests/commands/test_plan.py:380](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:380) | TestPlanCanonicalIdComposition.test_adr_created_id_derives_from_on_disk_directory | output |
| [tests/commands/test_plan.py:425](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:425) | TestPlanIdempotentAdrCreated.test_duplicate_plan_create_emits_single_adr_created | output |
| [tests/commands/test_plan.py:473](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:473) | TestPlanTaxonomyRoundtrip.test_plan_create_feature_kind_passes_taxonomy_validator | output |
| [tests/commands/test_plan.py:593](/Users/jeff/Documents/Code/gzkit/tests/commands/test_plan.py:593) | TestPlanCreateKindFoundation.test_feature_adr_does_not_scaffold_why_foundation_tier_section | output |
| [tests/commands/test_prd.py:39](/Users/jeff/Documents/Code/gzkit/tests/commands/test_prd.py:39) | TestPrdIdCanonicalization.test_kebab_slug_normalizes_to_canonical_id | output |
| [tests/commands/test_prd.py:52](/Users/jeff/Documents/Code/gzkit/tests/commands/test_prd.py:52) | TestPrdIdCanonicalization.test_trailing_semver_is_preserved | output |
| [tests/commands/test_prd.py:65](/Users/jeff/Documents/Code/gzkit/tests/commands/test_prd.py:65) | TestPrdIdCanonicalization.test_already_canonical_id_is_preserved | output |
| [tests/commands/test_prd.py:74](/Users/jeff/Documents/Code/gzkit/tests/commands/test_prd.py:74) | TestPrdIdCanonicalization.test_scaffolder_validator_roundtrip | output |
| [tests/commands/test_preflight.py:14](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:14) | TestPreflightCommand.test_clean_state_exits_zero | output |
| [tests/commands/test_preflight.py:22](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:22) | TestPreflightCommand.test_detects_stale_pipeline_marker | output |
| [tests/commands/test_preflight.py:41](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:41) | TestPreflightCommand.test_detects_expired_lock | output |
| [tests/commands/test_preflight.py:63](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:63) | TestPreflightCommand.test_detects_orphan_receipt | output |
| [tests/commands/test_preflight.py:189](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:189) | TestPreflightCommand.test_json_output | output |
| [tests/commands/test_preflight.py:200](/Users/jeff/Documents/Code/gzkit/tests/commands/test_preflight.py:200) | TestPreflightCommand.test_json_output_survives_a_hostile_console | output |
| [tests/commands/test_readiness.py:61](/Users/jeff/Documents/Code/gzkit/tests/commands/test_readiness.py:61) | ReadinessAuditCLISurfaceTest.test_audit_does_not_flag_legacy_test_cli_filename | getvalue |
| [tests/commands/test_register_adrs.py:13](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:13) | TestRegisterAdrsCommand.test_register_adrs_registers_missing_pool_adr | output |
| [tests/commands/test_register_adrs.py:49](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:49) | TestRegisterAdrsCommand.test_register_adrs_keeps_suffixed_id_and_registers_non_semver_pool | output |
| [tests/commands/test_register_adrs.py:88](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:88) | TestRegisterAdrsCommand.test_register_adrs_all_registers_missing_obpis_for_targeted_adr_only | output |
| [tests/commands/test_register_adrs.py:153](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:153) | TestRegisterAdrsCommand.test_register_adrs_default_includes_versioned | output |
| [tests/commands/test_register_adrs.py:172](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:172) | TestRegisterAdrsCommand.test_register_adrs_pool_only_skips_versioned | output |
| [tests/commands/test_register_adrs.py:191](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:191) | TestRegisterAdrsCommand.test_register_adrs_resolves_short_form_obpi_parent | output |
| [tests/commands/test_register_adrs.py:230](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:230) | TestRegisterAdrsCommand.test_register_adrs_resolves_short_form_adr_parent | output |
| [tests/commands/test_register_adrs.py:281](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:281) | TestRegisterAdrsCommand.test_register_adrs_warns_on_orphan_obpis | output |
| [tests/commands/test_register_adrs.py:327](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:327) | TestRegisterAdrsCommand.test_register_adrs_no_orphan_warning_for_withdrawn | output |
| [tests/commands/test_register_adrs.py:359](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:359) | TestRegisterAdrsCommand.test_register_adrs_does_not_flag_parked_obpi_as_orphan | output |
| [tests/commands/test_register_adrs.py:399](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:399) | TestRegisterAdrsCommand.test_register_adrs_warns_on_stale_promoted_pool_file | output |
| [tests/commands/test_register_adrs.py:449](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:449) | TestRegisterAdrsCommand.test_register_adrs_quiet_on_archived_promoted_pool_file | output |
| [tests/commands/test_register_adrs.py:508](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:508) | TestRegisterAdrsCommand.test_register_adrs_warns_on_unresolvable_parent | output |
| [tests/commands/test_register_adrs.py:556](/Users/jeff/Documents/Code/gzkit/tests/commands/test_register_adrs.py:556) | TestRegisterAdrsIdempotent.test_register_skips_emission_when_bare_id_already_in_ledger | output |
| [tests/commands/test_runtime.py:131](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:131) | TestAdrRuntimeCommands.test_closeout_missing_adr_fails | output |
| [tests/commands/test_runtime.py:140](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:140) | TestAdrRuntimeCommands.test_closeout_records_event | output |
| [tests/commands/test_runtime.py:171](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:171) | TestAdrRuntimeCommands.test_closeout_includes_canonical_attestation_choices | output |
| [tests/commands/test_runtime.py:181](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:181) | TestAdrRuntimeCommands.test_closeout_heavy_includes_bdd_command_when_features_missing | output |
| [tests/commands/test_runtime.py:192](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:192) | TestAdrRuntimeCommands.test_closeout_heavy_includes_bdd_command_when_features_exist | output |
| [tests/commands/test_runtime.py:203](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:203) | TestAdrRuntimeCommands.test_closeout_rejects_pool_adr | output |
| [tests/commands/test_runtime.py:214](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:214) | TestAdrRuntimeCommands.test_closeout_blocks_when_obpi_proof_is_incomplete | output |
| [tests/commands/test_runtime.py:240](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:240) | TestAdrRuntimeCommands.test_closeout_json_includes_obpi_blockers | output |
| [tests/commands/test_runtime.py:269](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:269) | TestAdrRuntimeCommands.test_closeout_blocks_heavy_obpi_missing_required_human_attestation | output |
| [tests/commands/test_runtime.py:305](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:305) | TestAdrRuntimeCommands.test_audit_pre_attestation_fails | output |
| [tests/commands/test_runtime.py:347](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:347) | TestAdrRuntimeCommands.test_audit_rejects_pool_adr | output |
| [tests/commands/test_runtime.py:356](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:356) | TestAdrRuntimeCommands.test_adr_audit_check_passes_for_completed_obpi_with_evidence | output |
| [tests/commands/test_runtime.py:389](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:389) | TestAdrRuntimeCommands.test_adr_audit_check_passes_with_advisory_uncovered_reqs | output |
| [tests/commands/test_runtime.py:466](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:466) | TestAdrRuntimeCommands.test_adr_audit_check_fails_for_incomplete_obpi | output |
| [tests/commands/test_runtime.py:484](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:484) | TestAdrRuntimeCommands.test_adr_audit_check_rejects_pool_adr | output |
| [tests/commands/test_runtime.py:493](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:493) | TestAdrRuntimeCommands.test_adr_covers_check_passes_for_adr_and_linked_obpi | output |
| [tests/commands/test_runtime.py:522](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:522) | TestAdrRuntimeCommands.test_adr_covers_check_fails_when_obpi_cover_missing | output |
| [tests/commands/test_runtime.py:548](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:548) | TestAdrRuntimeCommands.test_adr_covers_check_fails_when_criterion_missing_req_id | output |
| [tests/commands/test_runtime.py:584](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:584) | TestAdrRuntimeCommands.test_adr_emit_receipt_records_event | output |
| [tests/commands/test_runtime.py:607](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:607) | TestAdrRuntimeCommands.test_adr_emit_receipt_invalid_json_fails | output |
| [tests/commands/test_runtime.py:651](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:651) | TestAdrRuntimeCommands.test_adr_audit_begin_writes_per_adr_co_presence_marker | output |
| [tests/commands/test_runtime.py:664](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:664) | TestAdrRuntimeCommands.test_adr_audit_end_removes_marker | output |
| [tests/commands/test_runtime.py:676](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:676) | TestAdrRuntimeCommands.test_adr_audit_end_missing_marker_is_idempotent_soft_warning | output |
| [tests/commands/test_runtime.py:685](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:685) | TestAdrRuntimeCommands.test_adr_emit_validated_records_operator_verbatim_attestation | output |
| [tests/commands/test_runtime.py:714](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:714) | TestAdrRuntimeCommands.test_adr_emit_receipt_rejects_pool_adr | output |
| [tests/commands/test_runtime.py:759](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:759) | TestAdrRuntimeCommands.test_obpi_emit_receipt_invalid_json_fails | output |
| [tests/commands/test_runtime.py:815](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:815) | TestAdrRuntimeCommands.test_obpi_emit_receipt_completed_requires_evidence | output |
| [tests/commands/test_runtime.py:836](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:836) | TestAdrRuntimeCommands.test_obpi_emit_receipt_completed_heavy_requires_human_attestation_evidence | output |
| [tests/commands/test_runtime.py:893](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:893) | TestAdrRuntimeCommands.test_obpi_emit_receipt_lite_obpi_under_heavy_parent_requires_human_attestation | output |
| [tests/commands/test_runtime.py:1005](/Users/jeff/Documents/Code/gzkit/tests/commands/test_runtime.py:1005) | TestAdrRuntimeCommands.test_obpi_emit_receipt_rejects_pool_linked_obpi | output |
| [tests/commands/test_skills.py:145](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:145) | TestSkillCommands.test_skill_list | output |
| [tests/commands/test_skills.py:171](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:171) | TestSkillCommands.test_skill_list_hides_retired_by_default | output |
| [tests/commands/test_skills.py:189](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:189) | TestSkillCommands.test_skill_list_all_shows_retired_with_label | output |
| [tests/commands/test_skills.py:199](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:199) | TestSkillCommands.test_skill_list_json_default_filters_retired | output |
| [tests/commands/test_skills.py:212](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:212) | TestSkillCommands.test_skill_list_json_all_includes_lifecycle | output |
| [tests/commands/test_skills.py:266](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:266) | TestSkillCommands.test_skill_audit_passes_after_init | output |
| [tests/commands/test_skills.py:274](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:274) | TestSkillCommands.test_skill_audit_warning_is_non_blocking_without_strict | assertRegex,output |
| [tests/commands/test_skills.py:291](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:291) | TestSkillCommands.test_skill_audit_strict_fails_on_non_blocking_warnings | output |
| [tests/commands/test_skills.py:301](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:301) | TestSkillCommands.test_skill_audit_json_includes_issue_codes_and_blocking_counts | output |
| [tests/commands/test_skills.py:327](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:327) | TestSkillCommands.test_skill_audit_rejects_non_positive_max_review_age_days | output |
| [tests/commands/test_skills.py:335](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:335) | TestSkillCommands.test_skill_audit_max_review_age_override_relaxes_stale_failure | output |
| [tests/commands/test_skills.py:357](/Users/jeff/Documents/Code/gzkit/tests/commands/test_skills.py:357) | TestSkillCommands.test_skill_audit_manpage_coverage_warns_when_index_exists | output |
| [tests/commands/test_specify.py:58](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:58) | TestSpecifyCommand.test_specify_rejects_pool_parent | output |
| [tests/commands/test_specify.py:70](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:70) | TestSpecifyCommand.test_specify_rejects_out_of_range_item | output |
| [tests/commands/test_specify.py:82](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:82) | TestSpecifyCommand.test_specify_ignores_withdrawn_checklist_items_for_live_target | output |
| [tests/commands/test_specify.py:113](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:113) | TestSpecifyCommand.test_specify_warns_about_template_defaults | output |
| [tests/commands/test_specify.py:133](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:133) | TestSpecifyCommand.test_specify_dry_run_reports_default_lane_source_without_wbs_table | output |
| [tests/commands/test_specify.py:199](/Users/jeff/Documents/Code/gzkit/tests/commands/test_specify.py:199) | TestSpecifyCommand.test_specify_author_creates_authored_ready_brief | output |
| [tests/commands/test_state.py:31](/Users/jeff/Documents/Code/gzkit/tests/commands/test_state.py:31) | TestStateFullFlag.test_state_full_renders_complete_artifact_id | output |
| [tests/commands/test_state.py:50](/Users/jeff/Documents/Code/gzkit/tests/commands/test_state.py:50) | TestStateFullFlag.test_state_full_does_not_ellipsize_long_ids | output |
| [tests/commands/test_status.py:37](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:37) | TestStatusCommand.test_workflow_fronts_follow_registered_campaign_without_changing_ledger_status | output |
| [tests/commands/test_status.py:75](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:75) | TestStatusCommand.test_unavailable_declared_workflow_context_is_visible | output |
| [tests/commands/test_status.py:90](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:90) | TestStatusCommand.test_workflow_fronts_stop_before_other_campaign_sections | output |
| [tests/commands/test_status.py:107](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:107) | TestStatusCommand.test_status_shows_no_adrs | output |
| [tests/commands/test_status.py:116](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:116) | TestStatusCommand.test_status_shows_adr | output |
| [tests/commands/test_status.py:126](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:126) | TestStatusCommand.test_status_show_gates_shows_gate2_pass_from_ledger | output |
| [tests/commands/test_status.py:140](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:140) | TestStatusCommand.test_status_show_gates_shows_gate2_fail_from_ledger | output |
| [tests/commands/test_status.py:155](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:155) | TestStatusCommand.test_status_default_hides_gate_breakdown | output |
| [tests/commands/test_status.py:167](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:167) | TestStatusCommand.test_status_table_shows_adr_status_columns | output |
| [tests/commands/test_status.py:185](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:185) | TestStatusCommand.test_status_table_wraps_long_adr_ids_instead_of_truncating | output |
| [tests/commands/test_status.py:206](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:206) | TestStatusCommand.test_status_table_blocks_ready_on_incomplete_obpis | output |
| [tests/commands/test_status.py:250](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:250) | TestStatusCommand.test_status_json_orders_semver_ids_numerically | output |
| [tests/commands/test_status.py:274](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:274) | TestStatusCommand.test_status_shows_obpi_completion_summary | output |
| [tests/commands/test_status.py:335](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:335) | TestStatusCommand.test_status_excludes_withdrawn_obpi_files_from_adr_summary | output |
| [tests/commands/test_status.py:367](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:367) | TestStatusCommand.test_obpi_status_json_includes_runtime_fields | output |
| [tests/commands/test_status.py:411](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:411) | TestStatusCommand.test_obpi_status_renders_withdrawn_obpi_as_withdrawn | output |
| [tests/commands/test_status.py:440](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:440) | TestStatusCommand.test_obpi_status_json_reports_missing_file | output |
| [tests/commands/test_status.py:457](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:457) | TestStatusCommand.test_obpi_status_json_supports_file_backed_obpi_without_ledger_link | output |
| [tests/commands/test_status.py:482](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:482) | TestStatusCommand.test_obpi_reconcile_json_passes_for_completed_obpi | output |
| [tests/commands/test_status.py:521](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:521) | TestStatusCommand.test_obpi_reconcile_json_reports_reflection_drift_without_blocking | output |
| [tests/commands/test_status.py:565](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:565) | TestStatusCommand.test_obpi_reconcile_fails_closed_when_proof_missing | output |
| [tests/commands/test_status.py:590](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:590) | TestStatusCommand.test_obpi_reconcile_reports_anchor_drift_for_scope_changes | output |
| [tests/commands/test_status.py:669](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:669) | TestStatusCommand.test_obpi_status_json_surfaces_tracked_defects_for_anchor_drift | output |
| [tests/commands/test_status.py:764](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:764) | TestStatusCommand.test_obpi_reconcile_ignores_shared_file_changes_absorbed_by_later_sibling_completion | output,stdout |
| [tests/commands/test_status.py:918](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:918) | TestStatusCommand.test_obpi_status_json_exposes_anchor_fields | output |
| [tests/commands/test_status.py:979](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:979) | TestStatusCommand.test_obpi_status_uses_only_key_proof_section_for_file_reflection | output |
| [tests/commands/test_status.py:1023](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1023) | TestStatusCommand.test_obpi_status_accepts_legacy_verification_section_as_file_reflection | output |
| [tests/commands/test_status.py:1084](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1084) | TestStatusCommand.test_status_json_accepts_legacy_gate_evidence_section_as_file_reflection | output |
| [tests/commands/test_status.py:1146](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1146) | TestStatusCommand.test_obpi_status_accepts_verification_heading_prefix_as_file_reflection | output |
| [tests/commands/test_status.py:1207](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1207) | TestStatusCommand.test_obpi_status_accepts_validation_commands_bullet_as_file_reflection | output |
| [tests/commands/test_status.py:1269](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1269) | TestOrphanedAdrWarning.test_no_false_positive_when_stem_has_slug_but_ledger_has_bare_id | output |
| [tests/commands/test_status.py:1299](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1299) | TestOrphanedAdrWarning.test_no_false_positive_when_stem_is_bare_and_ledger_has_slugged_id | output |
| [tests/commands/test_status.py:1329](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1329) | TestOrphanedAdrWarning.test_genuine_orphan_still_warns | output |
| [tests/commands/test_status.py:1357](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1357) | TestLifecycleStatusSemantics.test_adr_status_default_hides_gate_breakdown | output |
| [tests/commands/test_status.py:1368](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1368) | TestLifecycleStatusSemantics.test_adr_status_renders_shared_table_via_deterministic_renderer | output |
| [tests/commands/test_status.py:1391](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1391) | TestLifecycleStatusSemantics.test_adr_status_discloses_withdrawn_obpis_hidden_from_table | output |
| [tests/commands/test_status.py:1433](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1433) | TestLifecycleStatusSemantics.test_adr_status_accepts_semver_prefix_for_suffixed_adr | output |
| [tests/commands/test_status.py:1455](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1455) | TestLifecycleStatusSemantics.test_adr_status_show_gates_includes_gate_breakdown | output |
| [tests/commands/test_status.py:1465](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1465) | TestLifecycleStatusSemantics.test_adr_status_heavy_features_missing_reports_gate4_pending | output |
| [tests/commands/test_status.py:1477](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1477) | TestLifecycleStatusSemantics.test_adr_status_legacy_semver_id_still_resolves | output |
| [tests/commands/test_status.py:1496](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1496) | TestLifecycleStatusSemantics.test_adr_status_json_completed | output |
| [tests/commands/test_status.py:1511](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1511) | TestLifecycleStatusSemantics.test_adr_status_json_obpi_incomplete_overrides_completed_lifecycle | output |
| [tests/commands/test_status.py:1536](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1536) | TestLifecycleStatusSemantics.test_adr_status_qc_readiness_includes_obpi_completion_blocker | output |
| [tests/commands/test_status.py:1557](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1557) | TestLifecycleStatusSemantics.test_adr_status_surfaces_closeout_blockers | output |
| [tests/commands/test_status.py:1581](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1581) | TestLifecycleStatusSemantics.test_adr_status_closeout_blockers_include_tracked_defect_refs | output |
| [tests/commands/test_status.py:1673](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1673) | TestLifecycleStatusSemantics.test_adr_status_closeout_blocker_renders_live_defect_state | output |
| [tests/commands/test_status.py:1710](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1710) | TestLifecycleStatusSemantics.test_adr_status_unresolvable_defect_renders_unresolved_not_live | output |
| [tests/commands/test_status.py:1743](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1743) | TestLifecycleStatusSemantics.test_status_summary_never_resolves_tracked_defects_live | output |
| [tests/commands/test_status.py:1779](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1779) | TestLifecycleStatusSemantics.test_adr_status_json_validated | output |
| [tests/commands/test_status.py:1795](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1795) | TestLifecycleStatusSemantics.test_adr_status_json_abandoned | output |
| [tests/commands/test_status.py:1809](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1809) | TestLifecycleStatusSemantics.test_obpi_scoped_validated_receipt_does_not_set_validated_lifecycle | output |
| [tests/commands/test_status.py:1835](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1835) | TestLifecycleStatusSemantics.test_status_json_includes_lifecycle_fields | output |
| [tests/commands/test_status.py:1850](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1850) | TestLifecycleStatusSemantics.test_status_json_obpi_incomplete_overrides_completed_lifecycle | output |
| [tests/commands/test_status.py:1876](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1876) | TestLifecycleStatusSemantics.test_status_json_includes_obpi_summary_fields | output |
| [tests/commands/test_status.py:1905](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1905) | TestLifecycleStatusSemantics.test_status_json_completed_status_with_empty_summary_stays_incomplete | output |
| [tests/commands/test_status.py:1955](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1955) | TestLifecycleStatusSemantics.test_adr_status_json_pool_adr_ignores_attestation_for_lifecycle | output |
| [tests/commands/test_status.py:1981](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:1981) | TestLifecycleStatusSemantics.test_status_json_pool_adr_ignores_attestation_for_lifecycle | output |
| [tests/commands/test_status.py:2007](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2007) | TestLifecycleStatusSemantics.test_adr_status_json_includes_obpi_rows | output |
| [tests/commands/test_status.py:2054](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2054) | TestLifecycleStatusSemantics.test_adr_status_json_reports_missing_linked_obpi_file | output |
| [tests/commands/test_status.py:2072](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2072) | TestLifecycleStatusSemantics.test_adr_report_renders_overview_and_obpi_tables | output |
| [tests/commands/test_status.py:2086](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2086) | TestLifecycleStatusSemantics.test_adr_report_shows_obpi_rows | output |
| [tests/commands/test_status.py:2104](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2104) | TestLifecycleStatusSemantics.test_adr_status_json_flags_brief_authored_readiness | output |
| [tests/commands/test_status.py:2218](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2218) | TestLifecycleStatusSemantics.test_adr_report_shows_issues_section | output |
| [tests/commands/test_status.py:2232](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2232) | TestLifecycleStatusSemantics.test_adr_report_accepts_semver_prefix | output |
| [tests/commands/test_status.py:2243](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2243) | TestLifecycleStatusSemantics.test_adr_report_no_arg_renders_summary_table | output |
| [tests/commands/test_status.py:2256](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2256) | TestLifecycleStatusSemantics.test_state_ready_json_only_includes_gate_ready_unattested_adrs | output |
| [tests/commands/test_status.py:2285](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2285) | TestStatusEpicFilter.test_status_epic_flag_documented_in_help | output |
| [tests/commands/test_status.py:2298](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2298) | TestStatusEpicFilter.test_status_epic_filter_matches_filename_prefix | output |
| [tests/commands/test_status.py:2322](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2322) | TestStatusEpicFilter.test_status_epic_filter_matches_frontmatter_field | output |
| [tests/commands/test_status.py:2340](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2340) | TestStatusEpicFilter.test_status_epic_filter_warns_on_mismatch | output |
| [tests/commands/test_status.py:2360](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2360) | TestStatusEpicFilter.test_status_epic_filter_empty_result_exits_zero | output |
| [tests/commands/test_status.py:2370](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2370) | TestStatusEpicFilter.test_status_default_behavior_unchanged_without_epic_flag | output |
| [tests/commands/test_status.py:2416](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2416) | TestStatusFullFlag.test_status_table_full_renders_long_adr_id_without_truncation | output |
| [tests/commands/test_status.py:2440](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2440) | TestStatusFullFlag.test_status_show_gates_full_renders_all_open_obpis | output |
| [tests/commands/test_status.py:2458](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2458) | TestStatusFullFlag.test_status_show_gates_default_truncates_to_three | output |
| [tests/commands/test_status.py:2513](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2513) | TestPostValidationObservedGateFail.test_adr_status_json_includes_observed_post_validation_failures | output |
| [tests/commands/test_status.py:2534](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2534) | TestPostValidationObservedGateFail.test_status_json_payload_field_is_jsonable | output |
| [tests/commands/test_status.py:2548](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2548) | TestPostValidationObservedGateFail.test_status_json_empty_when_no_laundering | output |
| [tests/commands/test_status.py:2564](/Users/jeff/Documents/Code/gzkit/tests/commands/test_status.py:2564) | TestPostValidationObservedGateFail.test_qc_readiness_blocked_by_observed_post_validation_failure | output |
| [tests/commands/test_sync_cmds.py:67](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:67) | TestGitSyncCommand.test_git_sync_skill_flag_prints_skill_path | output |
| [tests/commands/test_sync_cmds.py:75](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:75) | TestGitSyncCommand.test_sync_repo_alias_is_removed | output |
| [tests/commands/test_sync_cmds.py:83](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:83) | TestGitSyncCommand.test_git_sync_fails_outside_git_repo | output |
| [tests/commands/test_sync_cmds.py:91](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:91) | TestGitSyncCommand.test_git_sync_dry_run_in_git_repo | output |
| [tests/commands/test_sync_cmds.py:104](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:104) | TestGitSyncCommand.test_git_sync_dry_run_fetches_before_reading_divergence | output |
| [tests/commands/test_sync_cmds.py:163](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:163) | TestGitSyncCommand.test_git_sync_rejects_skip_that_disables_xenon | output |
| [tests/commands/test_sync_cmds.py:184](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:184) | TestSyncCommand.test_agent_sync_control_surfaces_updates_surfaces | output |
| [tests/commands/test_sync_cmds.py:192](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:192) | TestSyncCommand.test_agent_sync_agents_md_matches_governance_render | output |
| [tests/commands/test_sync_cmds.py:366](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:366) | TestSyncCommand.test_invariant_coherence_catches_hand_edit_to_agents_md | output |
| [tests/commands/test_sync_cmds.py:460](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:460) | TestSyncCommand.test_model_render_semantically_equivalent_to_pre_migration | output |
| [tests/commands/test_sync_cmds.py:506](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:506) | TestSyncCommand.test_agent_sync_dry_run_reports_complete_write_set | output |
| [tests/commands/test_sync_cmds.py:655](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:655) | TestSyncCommand.test_sync_alias_is_removed | output |
| [tests/commands/test_sync_cmds.py:663](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:663) | TestSyncCommand.test_agent_control_sync_alias_is_removed | output |
| [tests/commands/test_sync_cmds.py:671](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:671) | TestSyncCommand.test_agent_sync_fails_closed_on_canonical_skill_corruption | output |
| [tests/commands/test_sync_cmds.py:690](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:690) | TestSyncCommand.test_agent_sync_reports_stale_mirror_recovery_non_destructively | output |
| [tests/commands/test_sync_cmds.py:715](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:715) | TestSyncCommand.test_agent_sync_output_is_deterministic_across_repeated_runs | output |
| [tests/commands/test_sync_cmds.py:755](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:755) | TestSyncCommand.test_agent_sync_emits_ledger_event_on_apply | output |
| [tests/commands/test_sync_cmds.py:769](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:769) | TestSyncCommand.test_agent_sync_dry_run_does_not_emit_ledger_event | output |
| [tests/commands/test_sync_cmds.py:783](/Users/jeff/Documents/Code/gzkit/tests/commands/test_sync_cmds.py:783) | TestSyncCommand.test_agent_sync_event_payload_records_paths_and_rule_count | output |
| [tests/commands/test_upgrade.py:35](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:35) | TestUpgradeRegistration.test_upgrade_help_exits_0 | output |
| [tests/commands/test_upgrade.py:74](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:74) | TestUpgradeSurfaceFilter.test_unknown_surface_exits_1 | output |
| [tests/commands/test_upgrade.py:93](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:93) | TestUpgradeSurfaceFilter.test_unknown_surface_in_comma_list_exits_1 | output |
| [tests/commands/test_upgrade.py:103](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:103) | TestUpgradeSurfaceFilter.test_valid_surface_subset_accepted | output |
| [tests/commands/test_upgrade.py:149](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:149) | TestUpgradeEditedConflicts.test_edited_artifact_reported_and_not_overwritten | output |
| [tests/commands/test_upgrade.py:220](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:220) | TestUpgradeEditedConflicts.test_exit_0_when_no_conflicts | output |
| [tests/commands/test_upgrade.py:256](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:256) | TestUpgradeForce.test_force_overwrites_edited_artifact | output |
| [tests/commands/test_upgrade.py:292](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:292) | TestUpgradeForce.test_force_prints_overwrite_line_per_file | output |
| [tests/commands/test_upgrade.py:355](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:355) | TestUpgradeDryRun.test_dry_run_reports_classification | output |
| [tests/commands/test_upgrade.py:420](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:420) | TestUpgradeBootstrapRetrofit.test_works_without_gzkit_skills_dir | output |
| [tests/commands/test_upgrade.py:481](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:481) | TestUpgradeIdempotent.test_second_run_exits_0 | output |
| [tests/commands/test_upgrade.py:525](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:525) | TestUpgradeIdempotent.test_second_run_reports_zero_stale_or_edited | output |
| [tests/commands/test_upgrade.py:598](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:598) | TestUpgradeNoSideEffects.test_no_scaffold_hooks_invoked | output |
| [tests/commands/test_upgrade.py:674](/Users/jeff/Documents/Code/gzkit/tests/commands/test_upgrade.py:674) | TestUpgradeHonorsNamedExceptions.test_hooks_surface_rejected_as_unknown | output |
| [tests/commands/test_validate_cmds.py:17](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:17) | TestValidateCommand.test_validate_after_init | output |
| [tests/commands/test_validate_cmds.py:52](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:52) | TestValidateCommand.test_validate_ledger_flag_fails_on_invalid_ledger | output |
| [tests/commands/test_validate_cmds.py:64](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:64) | TestValidateCommand.test_validate_all_includes_ledger_checks | output |
| [tests/commands/test_validate_cmds.py:76](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:76) | TestValidateCommand.test_validate_decomposition_flag_accepted | output |
| [tests/commands/test_validate_cmds.py:85](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:85) | TestValidateCommand.test_validate_decomposition_detects_count_mismatch | output |
| [tests/commands/test_validate_cmds.py:121](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:121) | TestValidateCommand.test_validate_decomposition_skips_validated_legacy_adr_shape | output |
| [tests/commands/test_validate_cmds.py:150](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:150) | TestValidateCommand.test_validate_decomposition_draft_adr_still_requires_scorecard | output |
| [tests/commands/test_validate_cmds.py:180](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:180) | TestValidateCommand.test_validate_interviews_flag_accepted | output |
| [tests/commands/test_validate_cmds.py:189](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:189) | TestValidateCommand.test_validate_interviews_detects_missing_qa_transcript | output |
| [tests/commands/test_validate_cmds.py:262](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:262) | TestValidateCommand.test_validate_requirements_flag_accepted | output |
| [tests/commands/test_validate_cmds.py:271](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:271) | TestValidateCommand.test_validate_requirements_detects_bare_requirements_section | output |
| [tests/commands/test_validate_cmds.py:340](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:340) | TestValidateCommand.test_validate_commit_trailers_flag_accepted | output |
| [tests/commands/test_validate_cmds.py:350](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:350) | TestValidateCommand.test_validate_commit_trailers_flags_src_change_without_task_trailer | output |
| [tests/commands/test_validate_cmds.py:405](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:405) | TestValidateCommand.test_validate_commit_trailers_rejects_ceremony_alone_for_src | output |
| [tests/commands/test_validate_cmds.py:539](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:539) | TestValidateCommand.test_validate_briefs_tolerates_legacy_noncompleted_brief_shape | output |
| [tests/commands/test_validate_cmds.py:566](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:566) | TestValidateCommand.test_validate_briefs_does_not_require_live_scope_for_completed_history | output |
| [tests/commands/test_validate_cmds.py:688](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:688) | TestFrontmatterCoherence.test_lane_drift_detected | output |
| [tests/commands/test_validate_cmds.py:707](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:707) | TestFrontmatterCoherence.test_parent_drift_detected | output |
| [tests/commands/test_validate_cmds.py:724](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:724) | TestFrontmatterCoherence.test_id_drift_detected_for_obpi | output |
| [tests/commands/test_validate_cmds.py:743](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:743) | TestFrontmatterCoherence.test_json_output_includes_frontmatter_errors | output |
| [tests/commands/test_validate_cmds.py:783](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:783) | TestValidateTaxonomyFlag.test_validate_taxonomy_flag_clean_on_empty_tree | output |
| [tests/commands/test_validate_cmds.py:797](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:797) | TestValidateTaxonomyFlag.test_validate_taxonomy_detects_missing_kind | output |
| [tests/commands/test_validate_cmds.py:812](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_cmds.py:812) | TestValidateTaxonomyFlag.test_validate_taxonomy_detects_pool_kind_frontmatter | output |
| [tests/commands/test_validate_frontmatter.py:59](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:59) | TestFrontmatterGuard.test_coherent_repo_exits_0_and_empty_body | output |
| [tests/commands/test_validate_frontmatter.py:78](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:78) | TestFrontmatterGuard.test_status_drift_exits_3_reports_drift_line | output |
| [tests/commands/test_validate_frontmatter.py:100](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:100) | TestFrontmatterGuard.test_lane_drift_exits_3 | output |
| [tests/commands/test_validate_frontmatter.py:118](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:118) | TestFrontmatterGuard.test_parent_drift_exits_3 | output |
| [tests/commands/test_validate_frontmatter.py:136](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:136) | TestFrontmatterGuard.test_id_drift_resolves_via_path_not_fm_id | output |
| [tests/commands/test_validate_frontmatter.py:183](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:183) | TestFrontmatterGuard.test_json_output_emits_drift_array | output |
| [tests/commands/test_validate_frontmatter.py:206](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:206) | TestFrontmatterGuard.test_explain_emits_recovery_command_per_field | output |
| [tests/commands/test_validate_frontmatter.py:229](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:229) | TestFrontmatterGuard.test_adr_scope_restricts_output_to_one_artifact | output |
| [tests/commands/test_validate_frontmatter.py:280](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:280) | TestFrontmatterGuard.test_withdrawn_obpi_accepts_abandoned_frontmatter_status | output |
| [tests/commands/test_validate_frontmatter.py:313](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:313) | TestPoolAdrSkipParity.test_pool_adr_with_drift_is_skipped_silently | output |
| [tests/commands/test_validate_frontmatter.py:340](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:340) | TestPoolAdrSkipParity.test_active_adr_drift_still_reported_when_pool_present | output |
| [tests/commands/test_validate_frontmatter.py:374](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:374) | TestPoolAdrSkipParity.test_explain_on_pool_adr_emits_pool_aware_message | output |
| [tests/commands/test_validate_frontmatter.py:424](/Users/jeff/Documents/Code/gzkit/tests/commands/test_validate_frontmatter.py:424) | TestRecoveryCommandsResolveToCli.test_every_recovery_hint_resolves_to_a_registered_cli_verb | output |
| [tests/complexity/advisor/test_intrinsic.py:26](/Users/jeff/Documents/Code/gzkit/tests/complexity/advisor/test_intrinsic.py:26) | TestIntrinsicComplexityDecorator.test_registry_lookup_after_decoration | assertRegex |
| [tests/complexity/test_citation.py:93](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:93) | TestRuleCitationContractSection.test_canonical_tuple_named | assertRegex |
| [tests/complexity/test_citation.py:105](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:105) | TestRuleCitationContractSection.test_percentile_absolute_pairing_required | assertRegex |
| [tests/complexity/test_citation.py:112](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_citation.py:112) | TestRuleCitationContractSection.test_refresh_portability_rule_codified | assertRegex |
| [tests/complexity/test_distillation.py:133](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_distillation.py:133) | PerMetricTripleTests.test_each_canonical_metric_has_a_triple | assertRegex |
| [tests/complexity/test_distillation.py:206](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_distillation.py:206) | SubsequentRunDiffTests.test_shifted_baseline_lists_movements_with_operator_placeholders | assertRegex |
| [tests/complexity/test_distillation.py:296](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_distillation.py:296) | PractitionerEyeBlockTests.test_every_metric_has_operator_placeholder | assertRegex |
| [tests/complexity/test_measurement.py:245](/Users/jeff/Documents/Code/gzkit/tests/complexity/test_measurement.py:245) | TestPyprojectDeclaresDeps.test_pyproject_declares_three_deps_with_pins | assertRegex |
| [tests/content/test_advisor_qc.py:54](/Users/jeff/Documents/Code/gzkit/tests/content/test_advisor_qc.py:54) | TestRecordVerdictAdvisory.test_receipt_run_id_matches_attestation_regex | assertRegex |
| [tests/content/test_tui_affordances.py:26](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:26) | TestStatusLineTUI.test_render_tty_emits_status_to_stderr | getvalue |
| [tests/content/test_tui_affordances.py:51](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:51) | TestStatusLineTUI.test_render_status_line_formats_byte_count | assertRegex,getvalue |
| [tests/content/test_tui_affordances.py:76](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:76) | TestTableRendererTUI.test_list_tty_uses_rich_table | getvalue |
| [tests/content/test_tui_affordances.py:102](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:102) | TestTableRendererTUI.test_list_non_tty_produces_no_ansi | getvalue |
| [tests/content/test_tui_affordances.py:126](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:126) | TestPanelRendererTUI.test_show_tty_uses_rich_panel | getvalue |
| [tests/content/test_tui_affordances.py:144](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:144) | TestPanelRendererTUI.test_plain_flag_suppresses_rich_on_tty | getvalue |
| [tests/content/test_tui_affordances.py:255](/Users/jeff/Documents/Code/gzkit/tests/content/test_tui_affordances.py:255) | TestCommandSurfaceUnchanged.test_no_new_subcommands_added | stderr,stdout |
| [tests/content/test_validation_hooks.py:137](/Users/jeff/Documents/Code/gzkit/tests/content/test_validation_hooks.py:137) | TestValidateRender.test_no_warning_on_failure | output |
| [tests/content/test_validation_hooks.py:227](/Users/jeff/Documents/Code/gzkit/tests/content/test_validation_hooks.py:227) | TestValidateSave.test_no_warning_on_failure | output |
| [tests/eval/test_harness.py:139](/Users/jeff/Documents/Code/gzkit/tests/eval/test_harness.py:139) | TestQualityIntegration.test_run_eval_returns_quality_result | stdout |
| [tests/eval/test_harness.py:145](/Users/jeff/Documents/Code/gzkit/tests/eval/test_harness.py:145) | TestQualityIntegration.test_run_eval_has_surface_details | stdout |
| [tests/governance/test_advisor_proof_binding_validator.py:110](/Users/jeff/Documents/Code/gzkit/tests/governance/test_advisor_proof_binding_validator.py:110) | TestFixtureScope.test_empty_proof_fixture_fails_with_path_and_line | assertRegex |
| [tests/governance/test_advisor_proof_binding_validator.py:228](/Users/jeff/Documents/Code/gzkit/tests/governance/test_advisor_proof_binding_validator.py:228) | TestErrorMessageQuality.test_fixture_error_cites_path_and_line | assertRegex |
| [tests/governance/test_agents_md_map_conformance.py:338](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_conformance.py:338) | AgentsMdMapConformanceAuditTests.test_file_size_over_budget_is_reported_but_not_rejected | getvalue |
| [tests/governance/test_agents_md_map_doctrine.py:101](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine.py:101) | MapDoctrineRuleAuthorship.test_rule_file_exists_with_v010_and_required_shape | assertRegex |
| [tests/governance/test_agents_md_map_doctrine.py:181](/Users/jeff/Documents/Code/gzkit/tests/governance/test_agents_md_map_doctrine.py:181) | BudgetTightening.test_budget_enforces_codex_cap_and_files_fit | getvalue |
| [tests/governance/test_attestation_receipt_validator.py:200](/Users/jeff/Documents/Code/gzkit/tests/governance/test_attestation_receipt_validator.py:200) | AttestationReceiptCliSmokeTest.test_cli_reports_resolved_receipt | stderr,stdout |
| [tests/governance/test_audit_check_covers_backfill.py:1921](/Users/jeff/Documents/Code/gzkit/tests/governance/test_audit_check_covers_backfill.py:1921) | TestAdrAuditCheckIntegration.test_audit_check_json_output_includes_backfill_keys | getvalue |
| [tests/governance/test_audit_chores_layout.py:199](/Users/jeff/Documents/Code/gzkit/tests/governance/test_audit_chores_layout.py:199) | CliExitCodeTests.test_cli_exits_3_on_stray_chore_md | stderr,stdout |
| [tests/governance/test_audit_chores_layout.py:223](/Users/jeff/Documents/Code/gzkit/tests/governance/test_audit_chores_layout.py:223) | CliExitCodeTests.test_cli_exits_0_on_clean_tree | stderr,stdout |
| [tests/governance/test_behave_scenario_isolation.py:119](/Users/jeff/Documents/Code/gzkit/tests/governance/test_behave_scenario_isolation.py:119) | TestPatchReleaseStandsAlone.test_the_feature_passes_alone_with_gh_unauthenticated | stderr,stdout |
| [tests/governance/test_behave_sharding.py:205](/Users/jeff/Documents/Code/gzkit/tests/governance/test_behave_sharding.py:205) | TestShardFailureReporting.test_the_failing_shard_is_reported_first_and_named | stdout |
| [tests/governance/test_bullet_retention.py:346](/Users/jeff/Documents/Code/gzkit/tests/governance/test_bullet_retention.py:346) | TestCLIFlagRegistered.test_bullet_retention_flag_in_help | getvalue |
| [tests/governance/test_chore_control_surface_rule_conflicts_evidence.py:210](/Users/jeff/Documents/Code/gzkit/tests/governance/test_chore_control_surface_rule_conflicts_evidence.py:210) | SelfTestEntrypointTests.test_self_test_exits_zero | getvalue |
| [tests/governance/test_codex_delivery_witness.py:230](/Users/jeff/Documents/Code/gzkit/tests/governance/test_codex_delivery_witness.py:230) | AuditCodexDeliveryWitnessTest.test_truncated_delivery_is_advisory_never_fail_closed | getvalue |
| [tests/governance/test_complexity_doctrine_rule.py:63](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:63) | ComplexityDoctrineRuleAuthorship.test_rule_body_carries_version_marker_and_block_quote | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:77](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:77) | ComplexityDoctrineRuleAuthorship.test_seven_selection_criteria_present | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:97](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:97) | ComplexityDoctrineRuleAuthorship.test_seven_corpus_anti_patterns_present | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:117](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:117) | ComplexityDoctrineRuleAuthorship.test_three_cadence_triggers_and_six_month_minimum_present | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:134](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:134) | ComplexityDoctrineRuleAuthorship.test_citation_contract_names_distilled_characteristics_and_excludes_raw | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:148](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:148) | ComplexityDoctrineRuleAuthorship.test_project_doctrine_fitness_and_pytest_demerit_lesson | assertRegex |
| [tests/governance/test_complexity_doctrine_rule.py:166](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_doctrine_rule.py:166) | ComplexityDoctrineCrossSurfaceBindings.test_advisory_scorecard_classifies_rule_mechanical | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:94](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:94) | ComplexityThresholdsRuleAuthorship.test_rule_body_carries_version_marker_and_block_quote | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:122](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:122) | ComplexityThresholdsRuleAuthorship.test_trigger_semantic_vocabulary_declares_exactly_three_values | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:209](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:209) | ComplexityThresholdsRuleAuthorship.test_citation_section_names_canonical_tuple_and_resolves | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:257](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:257) | ComplexityThresholdsRuleAuthorship.test_operator_amendable_mapping_protocol_section_present | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:279](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:279) | ComplexityThresholdsRuleAuthorship.test_bootstrap_carve_out_names_exactly_three_metrics | assertRegex |
| [tests/governance/test_complexity_thresholds_rule.py:310](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_rule.py:310) | ComplexityThresholdsCrossSurfaceBindings.test_advisory_scorecard_classifies_rule_mechanical | assertRegex |
| [tests/governance/test_complexity_thresholds_validator.py:186](/Users/jeff/Documents/Code/gzkit/tests/governance/test_complexity_thresholds_validator.py:186) | BootstrapMode.test_bootstrap_section_emits_notice_to_stdout | getvalue |
| [tests/governance/test_dispatch_attestation_absorption.py:63](/Users/jeff/Documents/Code/gzkit/tests/governance/test_dispatch_attestation_absorption.py:63) | TestPoolAdrAnnotation.test_dispatch_attestation_audit_passes_on_project | stderr |
| [tests/governance/test_dispatch_attestation_absorption.py:85](/Users/jeff/Documents/Code/gzkit/tests/governance/test_dispatch_attestation_absorption.py:85) | TestDispatchAttestationAuditNegativeControl.test_audit_fails_when_marker_missing | stderr |
| [tests/governance/test_distribution_audit.py:370](/Users/jeff/Documents/Code/gzkit/tests/governance/test_distribution_audit.py:370) | TestDocumentationAndScorecard.test_distribution_flag_registered_in_cli | getvalue |
| [tests/governance/test_eval_feedback_trailer.py:32](/Users/jeff/Documents/Code/gzkit/tests/governance/test_eval_feedback_trailer.py:32) | TestEvalFeedbackTrailerValidation.test_eval_feedback_source_alone_rejected_for_src_commit | output |
| [tests/governance/test_eval_feedback_trailer.py:73](/Users/jeff/Documents/Code/gzkit/tests/governance/test_eval_feedback_trailer.py:73) | TestEvalFeedbackTrailerValidation.test_fails_rule_edit_closing_eval_feedback_ghi_without_trailer | output |
| [tests/governance/test_exemplar_corpus.py:90](/Users/jeff/Documents/Code/gzkit/tests/governance/test_exemplar_corpus.py:90) | TestCorpusShaPinning.test_every_commit_sha_is_pinned_40_char_hex | assertRegex |
| [tests/governance/test_handoff_archive.py:149](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_archive.py:149) | HandoffArchiveBehaviorTests.test_dry_run_reports_would_move_and_mutates_nothing | getvalue |
| [tests/governance/test_handoff_archive.py:345](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_archive.py:345) | HandoffArchiveBehaviorTests.test_dry_run_reports_preexisting_conflict | getvalue |
| [tests/governance/test_handoff_validation.py:758](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:758) | TestHandoffAbsorptionBrief.test_decision_recorded_as_absorb | assertRegex |
| [tests/governance/test_handoff_validation.py:768](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:768) | TestHandoffAbsorptionBrief.test_rationale_cites_concrete_differences | assertRegex |
| [tests/governance/test_handoff_validation.py:797](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:797) | TestHandoffAbsorptionBrief.test_req04_not_applicable_outcome_is_absorb | assertRegex |
| [tests/governance/test_handoff_validation.py:813](/Users/jeff/Documents/Code/gzkit/tests/governance/test_handoff_validation.py:813) | TestHandoffAbsorptionBrief.test_gate4_na_recorded_with_rationale | assertRegex |
| [tests/governance/test_historical_waiver_integration.py:106](/Users/jeff/Documents/Code/gzkit/tests/governance/test_historical_waiver_integration.py:106) | TestHistoricalWaiverIntegration.test_unwaivered_pre_cutoff_emits_no_error | output |
| [tests/governance/test_historical_waiver_integration.py:180](/Users/jeff/Documents/Code/gzkit/tests/governance/test_historical_waiver_integration.py:180) | TestHistoricalWaiverIntegration.test_bad_added_under_waiver_rejected | output |
| [tests/governance/test_obpi_complete_lock_release.py:99](/Users/jeff/Documents/Code/gzkit/tests/governance/test_obpi_complete_lock_release.py:99) | TestWriteCompletionHandoff.test_adr_id_normalized_to_bare_form | assertRegex |
| [tests/governance/test_qc_binding_scope.py:174](/Users/jeff/Documents/Code/gzkit/tests/governance/test_qc_binding_scope.py:174) | TestExitCodeBehavior.test_exit_0_when_all_bound_steps_have_negative_controls | stderr,stdout |
| [tests/governance/test_qc_binding_scope.py:270](/Users/jeff/Documents/Code/gzkit/tests/governance/test_qc_binding_scope.py:270) | TestCliAlignment.test_cli_alignment_exit_0 | stderr |
| [tests/governance/test_qc_binding_self_check.py:46](/Users/jeff/Documents/Code/gzkit/tests/governance/test_qc_binding_self_check.py:46) | TestQCBindingSelfCheck.test_fidelity_gate_passes_now_recovery_is_complete | stderr,stdout |
| [tests/governance/test_registration_membrane.py:202](/Users/jeff/Documents/Code/gzkit/tests/governance/test_registration_membrane.py:202) | TestBomPrefixedFoundationRefused.test_undecodable_package_is_refused_in_a_controlled_way | output |
| [tests/governance/test_rendition_lineage.py:325](/Users/jeff/Documents/Code/gzkit/tests/governance/test_rendition_lineage.py:325) | CoverageIsComputedAtRunTimeTest.test_scope_surfaces_the_computed_figure_on_the_clean_path | getvalue |
| [tests/governance/test_rendition_lineage.py:494](/Users/jeff/Documents/Code/gzkit/tests/governance/test_rendition_lineage.py:494) | MissingCommittedLineageIsDisclosedTest.test_declared_ownership_without_a_lineage_is_ungraded_not_failed | getvalue |
| [tests/governance/test_rendition_lineage.py:582](/Users/jeff/Documents/Code/gzkit/tests/governance/test_rendition_lineage.py:582) | RecoveryProseReachesStderrTest.test_fail_closed_path_writes_the_three_parts_to_stderr | getvalue |
| [tests/governance/test_req_coverage.py:97](/Users/jeff/Documents/Code/gzkit/tests/governance/test_req_coverage.py:97) | TestParseBriefReqs.test_skips_malformed_req_lines | output |
| [tests/governance/test_req_coverage.py:232](/Users/jeff/Documents/Code/gzkit/tests/governance/test_req_coverage.py:232) | TestDiscoverCoversAstSafety.test_skips_unparseable_file_keeps_valid_match | output |
| [tests/governance/test_retire_ln_surface.py:59](/Users/jeff/Documents/Code/gzkit/tests/governance/test_retire_ln_surface.py:59) | TestRetireLnSurface.test_closeout_proof_binding_flag_unknown | stderr |
| [tests/governance/test_security_sensitivity_rule.py:98](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_sensitivity_rule.py:98) | SecuritySensitivityRuleAuthorship.test_rule_body_documents_required_sections | assertRegex |
| [tests/governance/test_security_sensitivity_rule.py:162](/Users/jeff/Documents/Code/gzkit/tests/governance/test_security_sensitivity_rule.py:162) | SecuritySensitivityCrossSurfaceBindings.test_advisory_scorecard_classifies_rule_mechanical | assertRegex |
| [tests/governance/test_session_exit.py:360](/Users/jeff/Documents/Code/gzkit/tests/governance/test_session_exit.py:360) | TestExitBeatIsIntentionalAboutBookmarks.test_a_written_bookmark_is_staged | stdout |
| [tests/governance/test_session_exit.py:379](/Users/jeff/Documents/Code/gzkit/tests/governance/test_session_exit.py:379) | TestExitBeatIsIntentionalAboutBookmarks.test_a_staged_bookmark_rides_the_next_commit | stdout |
| [tests/governance/test_stage4_packet.py:524](/Users/jeff/Documents/Code/gzkit/tests/governance/test_stage4_packet.py:524) | TestReplayShellCanRunWhatTheGateSanctions.test_the_chosen_shell_executes_both_sanctioned_escapes | stdout |
| [tests/governance/test_task_envelope_coherence.py:1398](/Users/jeff/Documents/Code/gzkit/tests/governance/test_task_envelope_coherence.py:1398) | TestDiagnoseCmd.test_diagnose_renders_all_four_channels | getvalue |
| [tests/governance/test_task_envelope_coherence.py:1528](/Users/jeff/Documents/Code/gzkit/tests/governance/test_task_envelope_coherence.py:1528) | TestFrontmatterChannelFullSlugResolution.test_diagnose_renders_ch2_for_a_full_slug_brief | getvalue |
| [tests/governance/test_token_block_discipline.py:209](/Users/jeff/Documents/Code/gzkit/tests/governance/test_token_block_discipline.py:209) | TestFailClosedOnNoHandoff.test_release_fail_closed_without_handoff_or_abandon | getvalue |
| [tests/governance/test_validate_receipt_shape.py:313](/Users/jeff/Documents/Code/gzkit/tests/governance/test_validate_receipt_shape.py:313) | TestPreCutoffWaiverBehavior.test_pre_cutoff_without_waiver_file_is_warn_only | output |
| [tests/hooks/test_complexity_advisor_auto_chain.py:89](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:89) | TestRunAutoChain.test_block_band_exits_1 | getvalue |
| [tests/hooks/test_complexity_advisor_auto_chain.py:99](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:99) | TestRunAutoChain.test_warn_band_exits_0_with_stderr | getvalue |
| [tests/hooks/test_complexity_advisor_auto_chain.py:122](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:122) | TestRunAutoChain.test_timeout_exits_0_fail_open | getvalue |
| [tests/hooks/test_complexity_advisor_auto_chain.py:134](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:134) | TestRunAutoChain.test_xenon_fail_triggers_advisor | getvalue |
| [tests/hooks/test_complexity_advisor_auto_chain.py:298](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_complexity_advisor_auto_chain.py:298) | TestShellHookContract.test_hook_is_executable | stdout |
| [tests/hooks/test_formatter_failure_visibility.py:81](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_formatter_failure_visibility.py:81) | TestFormatterFailureIsObservable.test_the_failure_reaches_stderr | getvalue |
| [tests/hooks/test_formatter_failure_visibility.py:97](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_formatter_failure_visibility.py:97) | TestFormatterFailureIsObservable.test_the_diagnostic_is_not_reduced_to_a_line | getvalue |
| [tests/hooks/test_formatter_failure_visibility.py:116](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_formatter_failure_visibility.py:116) | TestFormatterFailureIsObservable.test_a_working_formatter_stays_silent_and_reports_success | getvalue |
| [tests/hooks/test_formatter_failure_visibility.py:136](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_formatter_failure_visibility.py:136) | TestFormatterFailureIsObservable.test_an_absent_directory_is_not_a_failure | getvalue |
| [tests/hooks/test_mx_awareness.py:84](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_mx_awareness.py:84) | TestHookAdapterBannerInjection.test_banner_injected_to_stdout_when_marker_present | getvalue |
| [tests/hooks/test_mx_awareness.py:104](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_mx_awareness.py:104) | TestHookAdapterBannerInjection.test_no_stdout_when_marker_absent | getvalue |
| [tests/hooks/test_stop_turn_feedback.py:74](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:74) | TestBlockOnFindings.test_dirty_files_with_findings_block_with_three_part_prose | getvalue |
| [tests/hooks/test_stop_turn_feedback.py:101](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:101) | TestSingleBlockPerTurn.test_stop_hook_active_true_exits_zero_even_with_findings | getvalue |
| [tests/hooks/test_stop_turn_feedback.py:211](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:211) | TestClaimGrounding.test_unbacked_claim_blocks_with_three_part_prose | getvalue |
| [tests/hooks/test_stop_turn_feedback.py:287](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:287) | TestClaimGrounding.test_ruff_findings_block_before_claim_check_runs | getvalue |
| [tests/hooks/test_stop_turn_feedback.py:349](/Users/jeff/Documents/Code/gzkit/tests/hooks/test_stop_turn_feedback.py:349) | TestDemoMode.test_demo_prints_prose_without_stdin_or_telemetry | getvalue |
| [tests/justify/test_evidence.py:240](/Users/jeff/Documents/Code/gzkit/tests/justify/test_evidence.py:240) | TestGatherEvidenceLibraryPurity.test_gather_evidence_never_emits_stdout_stderr | getvalue |
| [tests/knowledge/test_progressive_disclosure_path.py:91](/Users/jeff/Documents/Code/gzkit/tests/knowledge/test_progressive_disclosure_path.py:91) | TestCLIAlignmentAfterDocUpdates.test_cli_alignment_passes | stderr,stdout |
| [tests/policy/test_cli_consistency.py:246](/Users/jeff/Documents/Code/gzkit/tests/policy/test_cli_consistency.py:246) | TestCLIConsistency.test_help_renders | stderr,stdout |
| [tests/skills/test_complexity_advisor.py:66](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:66) | TestSkillFrontmatter.test_frontmatter_lifecycle_fields_present | assertRegex |
| [tests/skills/test_complexity_advisor.py:104](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:104) | TestThreeOperatorMoments.test_ad_hoc_preview_before_fail_documented | assertRegex |
| [tests/skills/test_complexity_advisor.py:118](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:118) | TestThreeOperatorMoments.test_auto_chain_context_documented | assertRegex |
| [tests/skills/test_complexity_advisor.py:132](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_advisor.py:132) | TestThreeOperatorMoments.test_intrinsic_attestation_guidance_documented | assertRegex |
| [tests/skills/test_complexity_guide.py:65](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:65) | TestSkillFrontmatter.test_frontmatter_lifecycle_fields_present | assertRegex |
| [tests/skills/test_complexity_guide.py:111](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:111) | TestOperatorMoment.test_ad_hoc_authoring_time_review_named_as_primary_surface | assertRegex |
| [tests/skills/test_complexity_guide.py:125](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:125) | TestOperatorMoment.test_first_stop_authoring_surface_named | assertRegex |
| [tests/skills/test_complexity_guide.py:210](/Users/jeff/Documents/Code/gzkit/tests/skills/test_complexity_guide.py:210) | TestCrossReference.test_trigger_time_vs_authoring_time_distinction_present | assertRegex |
| [tests/skills/test_ghi_author_brief_ownership.py:64](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_author_brief_ownership.py:64) | TestStepZeroSeesWorkOwningBriefs.test_a_brief_hit_is_an_operator_decision_not_an_agent_one | assertRegex |
| [tests/skills/test_ghi_author_brief_ownership.py:69](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_author_brief_ownership.py:69) | TestStepZeroSeesWorkOwningBriefs.test_the_residual_disclosure_names_the_categorical_gap | assertRegex |
| [tests/skills/test_ghi_author_brief_ownership.py:97](/Users/jeff/Documents/Code/gzkit/tests/skills/test_ghi_author_brief_ownership.py:97) | TestRoutingCriteriaAskWhoOwnsTheWork.test_routing_doc_makes_brief_ownership_a_precondition | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:70](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:70) | TestSkillFrontmatter.test_frontmatter_lifecycle_fields_present | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:109](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:109) | TestCadenceTriggers.test_annual_calendar_trigger_present | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:118](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:118) | TestCadenceTriggers.test_drift_signal_trigger_with_baseline_named | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:132](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:132) | TestCadenceTriggers.test_six_month_minimum_re_distillation_guard | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:141](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:141) | TestCadenceTriggers.test_judgment_trigger_for_groundbreaking_project | assertRegex |
| [tests/skills/test_gz_complexity_distill.py:183](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_complexity_distill.py:183) | TestCorpusReference.test_path_filters_referenced_not_duplicated | assertRegex |
| [tests/skills/test_gz_justify_skill.py:58](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_justify_skill.py:58) | TestGzJustifyFrontmatter.test_frontmatter_required_keys_present | assertRegex |
| [tests/skills/test_gz_justify_skill.py:108](/Users/jeff/Documents/Code/gzkit/tests/skills/test_gz_justify_skill.py:108) | TestGzJustifyBodyShape.test_red_flags_section_names_fabrication | assertRegex |
| [tests/skills/test_namespace_routers.py:84](/Users/jeff/Documents/Code/gzkit/tests/skills/test_namespace_routers.py:84) | TestRouterIntentTableSkillsResolve.test_intent_table_present_and_every_routed_skill_is_a_canonical_slug | assertRegex |
| [tests/skills/test_router_coverage_completion.py:100](/Users/jeff/Documents/Code/gzkit/tests/skills/test_router_coverage_completion.py:100) | TestChoresRouterSkillFile.test_gz_chores_intent_table_routes_all_seven_chore_skills | assertRegex |
| [tests/skills/test_router_coverage_completion.py:168](/Users/jeff/Documents/Code/gzkit/tests/skills/test_router_coverage_completion.py:168) | TestRouterMetadataPresence.test_every_router_carries_skill_version_and_last_reviewed | assertRegex |
| [tests/skills/test_skill_surface_sync_justify.py:70](/Users/jeff/Documents/Code/gzkit/tests/skills/test_skill_surface_sync_justify.py:70) | TestGzAdrEvaluateLowScoreFooter.test_adr_evaluate_has_low_score_footer_block | assertRegex |
| [tests/skills/test_skill_surface_sync_justify.py:124](/Users/jeff/Documents/Code/gzkit/tests/skills/test_skill_surface_sync_justify.py:124) | TestGzObpiPipelineConfidenceBlock.test_obpi_pipeline_has_low_confidence_block | assertRegex |
| [tests/test_acceptance_integration.py:51](/Users/jeff/Documents/Code/gzkit/tests/test_acceptance_integration.py:51) | TestAcceptanceAdvancement.test_green_commands_cannot_advance_a_real_brief_without_required_proof | getvalue,output |
| [tests/test_acceptance_integration.py:68](/Users/jeff/Documents/Code/gzkit/tests/test_acceptance_integration.py:68) | TestAcceptanceAdvancement.test_real_proof_and_reviews_drive_ceremony_without_history_reopening_acceptance | getvalue,output |
| [tests/test_acceptance_integration.py:121](/Users/jeff/Documents/Code/gzkit/tests/test_acceptance_integration.py:121) | TestAcceptanceAdvancement.test_direct_ceremony_entry_cannot_bypass_missing_proof | getvalue,output |
| [tests/test_adversarial_validation_gate.py:132](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:132) | TestAdversarialValidationGate.test_refutation_block_says_it_loops_rather_than_that_the_verdict_is_invalid | getvalue |
| [tests/test_adversarial_validation_gate.py:161](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:161) | TestAdversarialValidationGate.test_block_message_names_cause_and_runnable_next_step | getvalue |
| [tests/test_adversarial_validation_gate.py:173](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:173) | TestAdversarialValidationGate.test_refuted_block_message_demands_resolution | getvalue |
| [tests/test_adversarial_validation_gate.py:222](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:222) | TestStep4bTierBindingGate.test_claude_block_message_names_codex_and_next_step | getvalue |
| [tests/test_adversarial_validation_gate.py:292](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:292) | TestDeclaredTierGovernsOverNameInference.test_contradiction_block_message_names_both_halves_and_next_step | getvalue |
| [tests/test_adversarial_validation_gate.py:663](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:663) | TestReceiptGovernsTheDeclaredTier.test_block_message_names_the_receipt_and_a_runnable_next_step | getvalue |
| [tests/test_adversarial_validation_gate.py:747](/Users/jeff/Documents/Code/gzkit/tests/test_adversarial_validation_gate.py:747) | TestCrossVendorClaimRequiresReceipt.test_block_message_names_the_receipt_flag_and_the_tier_2_escape | getvalue |
| [tests/test_attest_deprecation.py:37](/Users/jeff/Documents/Code/gzkit/tests/test_attest_deprecation.py:37) | TestAttestDeprecationWarning.test_warning_shown_when_closeout_active | output |
| [tests/test_attest_deprecation.py:62](/Users/jeff/Documents/Code/gzkit/tests/test_attest_deprecation.py:62) | TestAttestDeprecationWarning.test_no_warning_without_closeout | output |
| [tests/test_attest_deprecation.py:89](/Users/jeff/Documents/Code/gzkit/tests/test_attest_deprecation.py:89) | TestAttestDeprecationContinuesNormally.test_attestation_recorded_after_warning | output |
| [tests/test_attest_deprecation.py:125](/Users/jeff/Documents/Code/gzkit/tests/test_attest_deprecation.py:125) | TestAttestDeprecationDryRun.test_dry_run_shows_warning_no_ledger_write | output |
| [tests/test_audit_pipeline.py:153](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:153) | TestAuditAttestationGuard.test_audit_blocks_without_attestation | output |
| [tests/test_audit_pipeline.py:167](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:167) | TestAuditArtifacts.test_audit_creates_artifacts | output |
| [tests/test_audit_pipeline.py:186](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:186) | TestAuditReceiptEmission.test_validation_receipt_in_ledger | output |
| [tests/test_audit_pipeline.py:203](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:203) | TestAuditStatusTransition.test_adr_transitions_to_validated | output |
| [tests/test_audit_pipeline.py:247](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:247) | TestAuditDryRun.test_dry_run_shows_receipt_and_transition_plan | output |
| [tests/test_audit_pipeline.py:259](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:259) | TestAuditDryRun.test_dry_run_json_includes_receipt_and_transition | output |
| [tests/test_audit_pipeline.py:274](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:274) | TestAuditJsonOutput.test_json_contains_all_fields | output |
| [tests/test_audit_pipeline.py:473](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:473) | TestAuditEnrichmentJsonKeys.test_json_output_contains_enrichment_keys | output |
| [tests/test_audit_pipeline.py:486](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:486) | TestAuditEnrichmentJsonKeys.test_json_output_preserves_existing_keys | output |
| [tests/test_audit_pipeline.py:501](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:501) | TestAuditEnrichmentJsonKeys.test_attestation_record_has_correct_fields | output |
| [tests/test_audit_pipeline.py:516](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:516) | TestAuditEnrichmentJsonKeys.test_gate_results_list_has_correct_structure | output |
| [tests/test_audit_pipeline.py:539](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:539) | TestAuditGeneratedLedgerEvent.test_audit_generated_event_in_ledger | output |
| [tests/test_audit_pipeline.py:573](/Users/jeff/Documents/Code/gzkit/tests/test_audit_pipeline.py:573) | TestAuditGeneratedLedgerEvent.test_dry_run_no_audit_generated_event | output |
| [tests/test_ceremony_data_summary_table.py:83](/Users/jeff/Documents/Code/gzkit/tests/test_ceremony_data_summary_table.py:83) | TestSummaryTableColumnAllocation.test_obpi_column_wraps_under_squeeze_so_objective_gets_room | getvalue |
| [tests/test_check_fingerprint.py:92](/Users/jeff/Documents/Code/gzkit/tests/test_check_fingerprint.py:92) | TestFingerprintNamesTheCommittableTree.test_the_real_index_is_left_alone | stdout |
| [tests/test_cli_parser.py:71](/Users/jeff/Documents/Code/gzkit/tests/test_cli_parser.py:71) | TestStableArgumentParserError.test_error_writes_blockers_prefix_to_stderr | getvalue,stderr |
| [tests/test_cli_parser.py:88](/Users/jeff/Documents/Code/gzkit/tests/test_cli_parser.py:88) | TestStableArgumentParserError.test_parse_error_exits_with_code_2 | stderr |
| [tests/test_cli_parser.py:156](/Users/jeff/Documents/Code/gzkit/tests/test_cli_parser.py:156) | TestStableArgumentParserIntegration.test_help_output_preserves_hyphens | getvalue |
| [tests/test_closeout_ceremony_cmd.py:216](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:216) | TestCeremonyInit.test_ceremony_init_creates_state | output |
| [tests/test_closeout_ceremony_cmd.py:233](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:233) | TestCeremonyInit.test_ceremony_init_json | output |
| [tests/test_closeout_ceremony_cmd.py:249](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:249) | TestCeremonyInit.test_ceremony_blocked_by_incomplete_obpis | output |
| [tests/test_closeout_ceremony_cmd.py:266](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:266) | TestCeremonyAdvance.test_advance_step_1_to_2 | output |
| [tests/test_closeout_ceremony_cmd.py:316](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:316) | TestCeremonyAdvance.test_next_without_init_fails | output |
| [tests/test_closeout_ceremony_cmd.py:332](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:332) | TestCeremonyAttestation.test_attest_at_wrong_step_exits_3 | output |
| [tests/test_closeout_ceremony_cmd.py:371](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:371) | TestCeremonyGate5Enforcement.test_next_at_step6_without_receipt_fail_closes | output |
| [tests/test_closeout_ceremony_cmd.py:396](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:396) | TestCeremonyGate5Enforcement.test_attest_emits_ledger_receipt_and_crosses | output |
| [tests/test_closeout_ceremony_cmd.py:425](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:425) | TestCeremonyGate5Enforcement.test_stale_receipt_does_not_satisfy_gate | output |
| [tests/test_closeout_ceremony_cmd.py:458](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:458) | TestCeremonyStatus.test_status_shows_step | output |
| [tests/test_closeout_ceremony_cmd.py:474](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:474) | TestCeremonyStatus.test_status_no_ceremony | output |
| [tests/test_closeout_ceremony_cmd.py:492](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:492) | TestCeremonyResume.test_resume_from_step_2 | output |
| [tests/test_closeout_ceremony_cmd.py:515](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:515) | TestCeremonyCompleted.test_completed_ceremony_offers_restart | output |
| [tests/test_closeout_ceremony_cmd.py:537](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:537) | TestCeremonyCompleted.test_restart_increments_attempt | output |
| [tests/test_closeout_ceremony_cmd.py:566](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:566) | TestCeremonyPause.test_pause_saves_state | output |
| [tests/test_closeout_ceremony_cmd.py:587](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:587) | TestNonCeremonyUnchanged.test_non_ceremony_closeout | output |
| [tests/test_closeout_ceremony_cmd.py:652](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:652) | TestStep5PerDemoCadence.test_step_5_renders_one_demo_at_a_time | output |
| [tests/test_closeout_ceremony_cmd.py:670](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:670) | TestStep5PerDemoCadence.test_next_advances_walkthrough_index_within_step_5 | output |
| [tests/test_closeout_ceremony_cmd.py:691](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:691) | TestStep5PerDemoCadence.test_next_on_last_demo_advances_to_attestation | output |
| [tests/test_closeout_ceremony_cmd.py:709](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:709) | TestStep5PerDemoCadence.test_next_with_single_demo_advances_to_attestation | output |
| [tests/test_closeout_ceremony_cmd.py:725](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:725) | TestStep5PerDemoCadence.test_next_with_zero_demos_advances_to_attestation | output |
| [tests/test_closeout_ceremony_cmd.py:740](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_cmd.py:740) | TestStep5PerDemoCadence.test_step_5_shows_progress_indicator | output |
| [tests/test_closeout_ceremony_consumption.py:66](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:66) | TestCloseoutConsumesCeremonyAttestation.test_ceremony_attestation_skips_prompt | output |
| [tests/test_closeout_ceremony_consumption.py:85](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:85) | TestCloseoutConsumesCeremonyAttestation.test_ceremony_attestation_recorded_in_ledger | output |
| [tests/test_closeout_ceremony_consumption.py:114](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:114) | TestCloseoutConsumesCeremonyAttestation.test_ceremony_dropped_attestation_yields_dropped_status | output |
| [tests/test_closeout_ceremony_consumption.py:139](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:139) | TestCloseoutConsumesCeremonyAttestation.test_ceremony_partial_attestation_yields_partial_status | output |
| [tests/test_closeout_ceremony_consumption.py:165](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:165) | TestCloseoutLegacyPromptPreserved.test_no_ceremony_state_uses_prompt | output |
| [tests/test_closeout_ceremony_consumption.py:178](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_ceremony_consumption.py:178) | TestCloseoutLegacyPromptPreserved.test_ceremony_state_before_attestation_uses_prompt | output |
| [tests/test_closeout_migration.py:65](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_migration.py:65) | TestCloseoutMigrationEnforce.test_blocks_when_enforced_and_missing | output |
| [tests/test_closeout_migration.py:92](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_migration.py:92) | TestCloseoutMigrationAdvisory.test_warns_when_not_enforced_and_missing | output |
| [tests/test_closeout_migration.py:120](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_migration.py:120) | TestCloseoutMigrationProofPresent.test_succeeds_with_proof_flag_true | output |
| [tests/test_closeout_migration.py:139](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_migration.py:139) | TestCloseoutMigrationProofPresent.test_succeeds_with_proof_flag_false | output |
| [tests/test_closeout_pipeline.py:78](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:78) | TestCloseoutPipelineGates.test_gates_run_inline_and_pass | output |
| [tests/test_closeout_pipeline.py:139](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:139) | TestCloseoutPipelineAttestation.test_attestation_recorded_in_ledger | output |
| [tests/test_closeout_pipeline.py:172](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:172) | TestCloseoutPipelineVersionBump.test_version_bump_when_needed | output |
| [tests/test_closeout_pipeline.py:195](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:195) | TestCloseoutPipelineCompletion.test_adr_marked_completed | output |
| [tests/test_closeout_pipeline.py:210](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:210) | TestCloseoutPipelineCompletion.test_adr_frontmatter_status_reconciled_to_ledger | output |
| [tests/test_closeout_pipeline.py:249](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:249) | TestCloseoutDryRun.test_dry_run_shows_plan_no_execution | output |
| [tests/test_closeout_pipeline.py:262](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:262) | TestCloseoutDryRun.test_dry_run_json_includes_version_sync | output |
| [tests/test_closeout_pipeline.py:284](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:284) | TestCloseoutJsonOutput.test_json_output_contains_all_stages | output |
| [tests/test_closeout_pipeline.py:300](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:300) | TestCloseoutJsonOutput.test_json_output_on_gate_failure | output |
| [tests/test_closeout_pipeline.py:319](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:319) | TestCloseoutAdrStatusRegen.test_adr_status_index_regenerated_on_closeout | output |
| [tests/test_closeout_pipeline.py:337](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:337) | TestCloseoutAdrStatusRegen.test_json_output_includes_adr_status_regen | output |
| [tests/test_closeout_pipeline.py:389](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:389) | TestDualRuntimeCollapseBI2.test_ceremony_driven_closeout_emits_single_attested | output |
| [tests/test_closeout_pipeline.py:442](/Users/jeff/Documents/Code/gzkit/tests/test_closeout_pipeline.py:442) | TestDualRuntimeCollapseBI2.test_direct_closeout_remains_sole_emitter | output |
| [tests/test_config_paths.py:196](/Users/jeff/Documents/Code/gzkit/tests/test_config_paths.py:196) | TestConfiguredSourceRoot.test_command_rejects_unmapped_literal_in_configured_source | getvalue |
| [tests/test_configured_path_consumers.py:179](/Users/jeff/Documents/Code/gzkit/tests/test_configured_path_consumers.py:179) | TestSourceScanFailures.test_cli_marks_unparseable_source_invalid_and_exits_nonzero | getvalue |
| [tests/test_formatters.py:50](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:50) | TestHumanMode.test_print_outputs_to_console | getvalue |
| [tests/test_formatters.py:62](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:62) | TestHumanMode.test_table_renders | getvalue |
| [tests/test_formatters.py:78](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:78) | TestHumanMode.test_data_renders_dict | getvalue |
| [tests/test_formatters.py:90](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:90) | TestHumanMode.test_err_goes_to_stderr | getvalue |
| [tests/test_formatters.py:102](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:102) | TestJsonMode.test_data_outputs_valid_json_to_stdout | getvalue |
| [tests/test_formatters.py:111](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:111) | TestJsonMode.test_print_goes_to_stderr_in_json_mode | getvalue |
| [tests/test_formatters.py:118](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:118) | TestJsonMode.test_data_and_logs_never_mix_on_stdout | getvalue |
| [tests/test_formatters.py:140](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:140) | TestJsonMode.test_table_suppressed_in_json_mode | getvalue |
| [tests/test_formatters.py:155](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:155) | TestJsonMode.test_err_goes_to_stderr_in_json_mode | getvalue |
| [tests/test_formatters.py:167](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:167) | TestQuietMode.test_print_suppressed | getvalue |
| [tests/test_formatters.py:179](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:179) | TestQuietMode.test_data_suppressed | getvalue |
| [tests/test_formatters.py:185](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:185) | TestQuietMode.test_table_suppressed | getvalue |
| [tests/test_formatters.py:199](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:199) | TestQuietMode.test_err_still_outputs | getvalue |
| [tests/test_formatters.py:205](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:205) | TestQuietMode.test_print_with_err_flag_outputs | getvalue |
| [tests/test_formatters.py:211](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:211) | TestQuietMode.test_log_suppressed | getvalue |
| [tests/test_formatters.py:222](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:222) | TestQuietMode.test_verbose_suppressed | getvalue |
| [tests/test_formatters.py:238](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:238) | TestVerboseMode.test_verbose_message_shown | getvalue |
| [tests/test_formatters.py:249](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:249) | TestVerboseMode.test_print_still_works | getvalue |
| [tests/test_formatters.py:260](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:260) | TestVerboseMode.test_debug_message_suppressed_in_verbose | getvalue |
| [tests/test_formatters.py:276](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:276) | TestDebugMode.test_debug_message_shown | getvalue |
| [tests/test_formatters.py:287](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:287) | TestDebugMode.test_verbose_message_also_shown | getvalue |
| [tests/test_formatters.py:298](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:298) | TestDebugMode.test_print_still_works | getvalue |
| [tests/test_formatters.py:496](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:496) | TestEmitMethod.test_string_human_mode_outputs_to_console | getvalue |
| [tests/test_formatters.py:505](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:505) | TestEmitMethod.test_string_json_mode_outputs_to_stdout | getvalue |
| [tests/test_formatters.py:515](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:515) | TestEmitMethod.test_dict_human_mode_outputs_to_console | getvalue |
| [tests/test_formatters.py:525](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:525) | TestEmitMethod.test_dict_json_mode_outputs_valid_json_sorted | getvalue |
| [tests/test_formatters.py:540](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:540) | TestEmitMethod.test_list_json_mode_outputs_valid_json | getvalue |
| [tests/test_formatters.py:553](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:553) | TestEmitMethod.test_pydantic_json_mode_outputs_model_dump_json | getvalue |
| [tests/test_formatters.py:563](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:563) | TestEmitMethod.test_pydantic_human_mode_outputs_formatted_dict | getvalue |
| [tests/test_formatters.py:580](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:580) | TestEmitMethod.test_quiet_mode_suppresses_string | getvalue |
| [tests/test_formatters.py:587](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:587) | TestEmitMethod.test_quiet_mode_suppresses_dict | getvalue |
| [tests/test_formatters.py:594](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:594) | TestEmitMethod.test_quiet_mode_suppresses_pydantic_model | getvalue |
| [tests/test_formatters.py:609](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:609) | TestEmitError.test_human_mode_writes_to_stderr | getvalue |
| [tests/test_formatters.py:616](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:616) | TestEmitError.test_json_mode_writes_to_stderr | getvalue |
| [tests/test_formatters.py:623](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:623) | TestEmitError.test_quiet_mode_writes_to_stderr_never_suppressed | getvalue |
| [tests/test_formatters.py:630](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:630) | TestEmitError.test_verbose_mode_writes_to_stderr | getvalue |
| [tests/test_formatters.py:637](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:637) | TestEmitError.test_debug_mode_writes_to_stderr | getvalue |
| [tests/test_formatters.py:659](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:659) | TestEmitTable.test_human_mode_renders_table | getvalue |
| [tests/test_formatters.py:671](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:671) | TestEmitTable.test_json_mode_outputs_valid_json_array | getvalue |
| [tests/test_formatters.py:681](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:681) | TestEmitTable.test_json_mode_rows_have_column_keys | getvalue |
| [tests/test_formatters.py:692](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:692) | TestEmitTable.test_quiet_mode_suppresses_table | getvalue |
| [tests/test_formatters.py:711](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:711) | TestEmitStatus.test_human_mode_success_shows_checkmark | getvalue |
| [tests/test_formatters.py:721](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:721) | TestEmitStatus.test_human_mode_failure_shows_cross | getvalue |
| [tests/test_formatters.py:730](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:730) | TestEmitStatus.test_human_mode_label_included | getvalue |
| [tests/test_formatters.py:740](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:740) | TestEmitStatus.test_json_mode_success_outputs_json | getvalue |
| [tests/test_formatters.py:750](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:750) | TestEmitStatus.test_json_mode_failure_outputs_json | getvalue |
| [tests/test_formatters.py:759](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:759) | TestEmitStatus.test_quiet_mode_suppresses_status | getvalue |
| [tests/test_formatters.py:778](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:778) | TestEmitBlocker.test_human_mode_writes_blockers_to_stderr | getvalue |
| [tests/test_formatters.py:785](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:785) | TestEmitBlocker.test_json_mode_writes_blockers_to_stderr | getvalue |
| [tests/test_formatters.py:792](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:792) | TestEmitBlocker.test_quiet_mode_writes_blockers_to_stderr_never_suppressed | getvalue |
| [tests/test_formatters.py:799](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:799) | TestEmitBlocker.test_verbose_mode_writes_blockers_to_stderr | getvalue |
| [tests/test_formatters.py:806](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:806) | TestEmitBlocker.test_debug_mode_writes_blockers_to_stderr | getvalue |
| [tests/test_formatters.py:813](/Users/jeff/Documents/Code/gzkit/tests/test_formatters.py:813) | TestEmitBlocker.test_blockers_prefix_always_present | getvalue |
| [tests/test_foundation_triage_e2e.py:131](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_e2e.py:131) | TestDocsFixturesCoverageE2E.test_plan_create_manpage_exists_and_covers_cli_audit | getvalue |
| [tests/test_foundation_triage_skill.py:92](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:92) | TestREQ04_EphemeralDiagnosisOnly.test_triage_run_leaves_governance_surfaces_untouched | stderr,stdout |
| [tests/test_foundation_triage_skill.py:146](/Users/jeff/Documents/Code/gzkit/tests/test_foundation_triage_skill.py:146) | TestREQ05_PortAdapterReclassification.test_cognitive_pass_section_names_port_adapter_reclassification | assertRegex |
| [tests/test_gates_deprecation.py:69](/Users/jeff/Documents/Code/gzkit/tests/test_gates_deprecation.py:69) | TestGatesDeprecationWarning.test_deprecation_warning_emitted | getvalue |
| [tests/test_hooks.py:1019](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1019) | TestPlanAuditGateHook.test_allows_when_plans_dir_is_missing | stderr |
| [tests/test_hooks.py:1043](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1043) | TestPlanAuditGateHook.test_blocks_when_obpi_plan_has_no_receipt | stderr |
| [tests/test_hooks.py:1086](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1086) | TestPlanAuditGateHook.test_blocks_when_receipt_is_older_than_plan | stderr |
| [tests/test_hooks.py:1101](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1101) | TestPlanAuditGateHook.test_blocks_when_receipt_obpi_does_not_match | stderr |
| [tests/test_hooks.py:1116](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1116) | TestPlanAuditGateHook.test_blocks_when_receipt_verdict_is_invalid | stderr |
| [tests/test_hooks.py:1132](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1132) | TestPlanAuditGateHook.test_allows_when_per_obpi_receipt_is_newer_than_plan | stderr |
| [tests/test_hooks.py:1150](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1150) | TestPlanAuditGateHook.test_allows_when_canonical_slug_per_obpi_receipt_matches_short_form_plan | stderr |
| [tests/test_hooks.py:1196](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1196) | TestPlanAuditGateHook.test_prefers_fresh_per_obpi_over_stale_legacy_receipt | stderr |
| [tests/test_hooks.py:1215](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1215) | TestPlanAuditGateHook.test_emits_prior_art_warning_without_blocking_valid_receipt | stderr |
| [tests/test_hooks.py:1301](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1301) | TestPlanAuditGateHook.test_self_audits_when_receipt_missing_and_allows_on_pass | stderr |
| [tests/test_hooks.py:1318](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1318) | TestPlanAuditGateHook.test_self_audits_when_receipt_obpi_mismatches_and_allows_on_pass | stderr |
| [tests/test_hooks.py:1337](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1337) | TestPlanAuditGateHook.test_blocks_when_self_audit_subprocess_fails | stderr |
| [tests/test_hooks.py:1353](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1353) | TestPlanAuditGateHook.test_blocks_when_self_audit_writes_fail_receipt | stderr |
| [tests/test_hooks.py:1370](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1370) | TestPlanAuditGateHook.test_allows_when_self_audit_writes_fail_receipt_with_nonzero_exit | stderr |
| [tests/test_hooks.py:1420](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1420) | TestPipelineRouterHook.test_allows_silently_when_receipt_is_missing | stderr,stdout |
| [tests/test_hooks.py:1431](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1431) | TestPipelineRouterHook.test_allows_silently_when_receipt_is_corrupt | stderr,stdout |
| [tests/test_hooks.py:1445](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1445) | TestPipelineRouterHook.test_allows_silently_when_receipt_has_no_obpi | stderr,stdout |
| [tests/test_hooks.py:1457](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1457) | TestPipelineRouterHook.test_allows_silently_when_receipt_verdict_is_fail | stderr,stdout |
| [tests/test_hooks.py:1474](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1474) | TestPipelineRouterHook.test_routes_when_receipt_verdict_is_pass | stderr,stdout |
| [tests/test_hooks.py:1531](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1531) | TestPipelineGateHook.test_allows_non_implementation_paths | stderr,stdout |
| [tests/test_hooks.py:1542](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1542) | TestPipelineGateHook.test_allows_when_receipt_is_missing | stderr,stdout |
| [tests/test_hooks.py:1553](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1553) | TestPipelineGateHook.test_allows_when_receipt_is_not_pass | stderr,stdout |
| [tests/test_hooks.py:1570](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1570) | TestPipelineGateHook.test_blocks_when_pass_receipt_exists_without_marker | stderr |
| [tests/test_hooks.py:1588](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1588) | TestPipelineGateHook.test_allows_when_per_obpi_marker_matches | stderr |
| [tests/test_hooks.py:1605](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1605) | TestPipelineGateHook.test_allows_when_richer_per_obpi_marker_matches | stderr |
| [tests/test_hooks.py:1649](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1649) | TestPipelineGateHook.test_blocks_src_write_when_marker_is_past_authoring_stage | stderr |
| [tests/test_hooks.py:1688](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1688) | TestPipelineGateHook.test_allows_tests_write_when_marker_is_past_authoring_stage | stderr |
| [tests/test_hooks.py:1720](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1720) | TestPipelineGateHook.test_allows_when_legacy_marker_matches | stderr |
| [tests/test_hooks.py:1733](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1733) | TestPipelineGateHook.test_blocks_when_marker_is_corrupt | stderr |
| [tests/test_hooks.py:1747](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1747) | TestPipelineGateHook.test_blocks_when_marker_obpi_does_not_match | stderr |
| [tests/test_hooks.py:1816](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1816) | TestPipelineGateHookLockArm.test_blocks_lock_held_no_marker_in_scope_without_receipt | stderr |
| [tests/test_hooks.py:1830](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1830) | TestPipelineGateHookLockArm.test_allows_lock_write_out_of_scope | stderr |
| [tests/test_hooks.py:1845](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1845) | TestPipelineGateHookLockArm.test_allows_when_lock_held_by_other_agent | stderr |
| [tests/test_hooks.py:1858](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1858) | TestPipelineGateHookLockArm.test_allows_when_lock_has_active_marker | stderr |
| [tests/test_hooks.py:1927](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1927) | TestPipelineCompletionReminderHook.test_allows_silently_when_command_is_not_commit_or_push | stderr,stdout |
| [tests/test_hooks.py:1938](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1938) | TestPipelineCompletionReminderHook.test_allows_silently_when_marker_is_missing | stderr,stdout |
| [tests/test_hooks.py:1949](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1949) | TestPipelineCompletionReminderHook.test_allows_silently_when_marker_is_corrupt | stderr,stdout |
| [tests/test_hooks.py:1963](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1963) | TestPipelineCompletionReminderHook.test_allows_silently_when_marker_has_no_obpi | stderr,stdout |
| [tests/test_hooks.py:1980](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1980) | TestPipelineCompletionReminderHook.test_allows_silently_when_brief_is_missing | stderr,stdout |
| [tests/test_hooks.py:1997](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:1997) | TestPipelineCompletionReminderHook.test_emits_stale_marker_note_when_brief_is_completed | stderr,stdout |
| [tests/test_hooks.py:2018](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2018) | TestPipelineCompletionReminderHook.test_emits_reminder_when_brief_is_incomplete | stderr,stdout |
| [tests/test_hooks.py:2039](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2039) | TestPipelineCompletionReminderHook.test_emits_reminder_with_richer_marker_payload | stderr,stdout |
| [tests/test_hooks.py:2141](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2141) | TestObpiCompletionValidatorHook.test_blocks_completion_without_implementation_summary | stderr |
| [tests/test_hooks.py:2163](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2163) | TestObpiCompletionValidatorHook.test_blocks_completion_without_key_proof | stderr |
| [tests/test_hooks.py:2185](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2185) | TestObpiCompletionValidatorHook.test_blocks_completion_with_both_missing | stderr |
| [tests/test_hooks.py:2265](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2265) | TestObpiCompletionValidatorHook.test_allows_completion_with_substantive_content | stderr |
| [tests/test_hooks.py:2336](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2336) | TestObpiCompletionValidatorHook.test_allows_completion_when_audit_evidence_keyed_by_full_slug | stderr |
| [tests/test_hooks.py:2394](/Users/jeff/Documents/Code/gzkit/tests/test_hooks.py:2394) | TestObpiCompletionValidatorHook.test_write_tool_checks_content_directly | stderr |
| [tests/test_hooks_guards.py:211](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:211) | TestForbidPytest.test_clean_root_returns_zero | getvalue |
| [tests/test_hooks_guards.py:223](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:223) | TestForbidPytest.test_bad_py_file_returns_one_and_prints_findings | getvalue |
| [tests/test_hooks_guards.py:238](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:238) | TestForbidPytest.test_conftest_under_root_flagged | getvalue |
| [tests/test_hooks_guards.py:249](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:249) | TestForbidPytest.test_pyproject_dependency_flagged | getvalue |
| [tests/test_hooks_guards.py:264](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:264) | TestSafePrint.test_ascii_passes_through | getvalue |
| [tests/test_hooks_guards.py:288](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards.py:288) | TestSafePrint.test_encodable_unicode_prints_directly | getvalue |
| [tests/test_hooks_guards_ledger_sync.py:164](/Users/jeff/Documents/Code/gzkit/tests/test_hooks_guards_ledger_sync.py:164) | TestForbidSkillSyncDrift.test_guard_names_no_retired_vendor_tree | getvalue |
| [tests/test_ledger_merge_driver.py:91](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_merge_driver.py:91) | TestEnsureMergeDriverRegistration.test_registers_driver_then_is_idempotent | stdout |
| [tests/test_ledger_transaction_boundary.py:256](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_transaction_boundary.py:256) | TestTrailingFragmentRecovery.test_recovery_is_reported_rather_than_silent | stderr |
| [tests/test_ledger_transaction_boundary.py:284](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_transaction_boundary.py:284) | TestTrailingFragmentRecovery.test_a_killed_writer_leaves_a_store_the_next_writer_can_use | stderr |
| [tests/test_ledger_transaction_boundary.py:508](/Users/jeff/Documents/Code/gzkit/tests/test_ledger_transaction_boundary.py:508) | TestACompleteRecordMissingItsSeparatorIsNotResidue.test_termination_is_reported_rather_than_silent | stderr |
| [tests/test_lint_parents.py:41](/Users/jeff/Documents/Code/gzkit/tests/test_lint_parents.py:41) | TestParentsPatternLint.test_violation_detected | stdout |
| [tests/test_lint_parents.py:57](/Users/jeff/Documents/Code/gzkit/tests/test_lint_parents.py:57) | TestParentsPatternLint.test_non_subscript_parents_access_detected | stdout |
| [tests/test_lock_manager.py:216](/Users/jeff/Documents/Code/gzkit/tests/test_lock_manager.py:216) | TestCurrentBranch.test_returns_unknown_on_nonzero_exit | stdout |
| [tests/test_lock_manager.py:223](/Users/jeff/Documents/Code/gzkit/tests/test_lock_manager.py:223) | TestCurrentBranch.test_subprocess_run_uses_errors_replace | stdout |
| [tests/test_logging.py:85](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:85) | TestVerbosityLevels.test_quiet_suppresses_info | getvalue |
| [tests/test_logging.py:92](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:92) | TestVerbosityLevels.test_quiet_shows_errors | getvalue |
| [tests/test_logging.py:99](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:99) | TestVerbosityLevels.test_normal_shows_warnings | getvalue |
| [tests/test_logging.py:106](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:106) | TestVerbosityLevels.test_normal_suppresses_info | getvalue |
| [tests/test_logging.py:113](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:113) | TestVerbosityLevels.test_verbose_shows_info | getvalue |
| [tests/test_logging.py:120](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:120) | TestVerbosityLevels.test_verbose_suppresses_debug | getvalue |
| [tests/test_logging.py:127](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:127) | TestVerbosityLevels.test_debug_shows_debug | getvalue |
| [tests/test_logging.py:227](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:227) | TestConsoleOutput.test_console_output_is_human_readable | getvalue |
| [tests/test_logging.py:238](/Users/jeff/Documents/Code/gzkit/tests/test_logging.py:238) | TestConsoleOutput.test_console_goes_to_stderr_by_default | getvalue |
| [tests/test_obpi_complete_cmd.py:651](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_complete_cmd.py:651) | TestObpiCompleteCmdJsonOutput.test_json_dry_run_output | getvalue,stdout |
| [tests/test_obpi_lock_cmd.py:964](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_lock_cmd.py:964) | TestClaimReleaseSafetyPrimitives.test_release_fail_closed_without_handoff_or_abandon | getvalue |
| [tests/test_obpi_repudiate_cli.py:186](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_repudiate_cli.py:186) | TestObpiRepudiateCmdDryRun.test_dry_run_no_ledger_write | getvalue |
| [tests/test_obpi_repudiate_cli.py:266](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_repudiate_cli.py:266) | TestObpiRepudiateCmdParserRejectsInvalidCause.test_invalid_cause_rejected_by_parser | stderr |
| [tests/test_obpi_validator.py:399](/Users/jeff/Documents/Code/gzkit/tests/test_obpi_validator.py:399) | TestObpiValidator.test_recorder_append_failure_is_warning_only | getvalue |
| [tests/test_ontology_source_roots.py:42](/Users/jeff/Documents/Code/gzkit/tests/test_ontology_source_roots.py:42) | TestOntologySourceRoots.test_configured_population_from_root_and_nested_directory | getvalue |
| [tests/test_packaging.py:225](/Users/jeff/Documents/Code/gzkit/tests/test_packaging.py:225) | TestPyInstallerBinaryDataBundling.test_gz_spec_extends_datas_with_chores | assertRegex |
| [tests/test_permitted_entry.py:197](/Users/jeff/Documents/Code/gzkit/tests/test_permitted_entry.py:197) | TestLightRepairCeiling.test_operator_repair_text_cannot_inject_or_crash_rich_markup | getvalue |
| [tests/test_plan_audit_cmd.py:589](/Users/jeff/Documents/Code/gzkit/tests/test_plan_audit_cmd.py:589) | TestPlanAuditCmdJson.test_json_output_is_valid | getvalue |
| [tests/test_plan_audit_scope.py:63](/Users/jeff/Documents/Code/gzkit/tests/test_plan_audit_scope.py:63) | TestPlanScope.test_outside_create_fails_receipt_while_allowed_create_passes | getvalue |
| [tests/test_progress.py:27](/Users/jeff/Documents/Code/gzkit/tests/test_progress.py:27) | TestProgressSpinner.test_spinner_suppressed_in_quiet_mode | getvalue |
| [tests/test_progress.py:38](/Users/jeff/Documents/Code/gzkit/tests/test_progress.py:38) | TestProgressSpinner.test_spinner_suppressed_in_json_mode | getvalue |
| [tests/test_progress.py:78](/Users/jeff/Documents/Code/gzkit/tests/test_progress.py:78) | TestProgressPhase.test_phase_suppressed_in_quiet_mode | getvalue |
| [tests/test_progress.py:89](/Users/jeff/Documents/Code/gzkit/tests/test_progress.py:89) | TestProgressPhase.test_phase_suppressed_in_json_mode | getvalue |
| [tests/test_progress.py:167](/Users/jeff/Documents/Code/gzkit/tests/test_progress.py:167) | TestProgressBar.test_bar_suppressed_in_json_mode | getvalue |
| [tests/test_quality.py:107](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:107) | TestRunCommand.test_successful_command | stdout |
| [tests/test_quality.py:120](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:120) | TestRunCommand.test_command_with_cwd | stdout |
| [tests/test_quality.py:130](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:130) | TestRunCommand.test_string_command_is_shlex_split | stderr,stdout |
| [tests/test_quality.py:140](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:140) | TestRunCommand.test_no_shell_metacharacter_interpretation | stdout |
| [tests/test_quality.py:161](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:161) | TestRunCommand.test_child_environment_forces_utf8_io | stdout |
| [tests/test_quality.py:178](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:178) | TestRunCommand.test_child_can_emit_non_ascii_glyph | stdout |
| [tests/test_quality.py:434](/Users/jeff/Documents/Code/gzkit/tests/test_quality.py:434) | TestAdrPathContractLint.test_fails_for_legacy_series_folder_paths | stdout |
| [tests/test_red_witness.py:241](/Users/jeff/Documents/Code/gzkit/tests/test_red_witness.py:241) | TestRunRedWitness.test_worktree_is_removed_after_the_run | stdout |
| [tests/test_red_witness.py:298](/Users/jeff/Documents/Code/gzkit/tests/test_red_witness.py:298) | TestResolveIntroducingBase.test_it_resolves_the_parent_of_the_introducing_commit | stdout |
| [tests/test_roles_cli.py:27](/Users/jeff/Documents/Code/gzkit/tests/test_roles_cli.py:27) | TestRolesDefaultOutput.test_output_contains_all_four_roles | getvalue |
| [tests/test_roles_cli.py:49](/Users/jeff/Documents/Code/gzkit/tests/test_roles_cli.py:49) | TestRolesJsonOutput.test_json_is_valid | getvalue |
| [tests/test_roles_cli.py:72](/Users/jeff/Documents/Code/gzkit/tests/test_roles_cli.py:72) | TestRolesPipelineOutput.test_pipeline_with_summary | getvalue |
| [tests/test_skill_body_audit.py:133](/Users/jeff/Documents/Code/gzkit/tests/test_skill_body_audit.py:133) | TestSkillBodyBaseline.test_packaged_ceilings_only_shrink_against_committed_baseline | stdout |
| [tests/test_skill_naming.py:36](/Users/jeff/Documents/Code/gzkit/tests/test_skill_naming.py:36) | TestSkillNaming.test_skill_dirs_and_frontmatter_names_are_kebab_case | assertRegex |
| [tests/test_traceability.py:471](/Users/jeff/Documents/Code/gzkit/tests/test_traceability.py:471) | TestScanTestTree.test_skips_malformed_req | output |
| [tests/test_traceability.py:876](/Users/jeff/Documents/Code/gzkit/tests/test_traceability.py:876) | TestCoversCLIHelp.test_help_exits_zero | getvalue |
| [tests/test_traceability.py:893](/Users/jeff/Documents/Code/gzkit/tests/test_traceability.py:893) | TestCoversCLIHelp.test_help_shows_description | getvalue |
| [tests/test_traceability.py:906](/Users/jeff/Documents/Code/gzkit/tests/test_traceability.py:906) | TestCoversCLIHelp.test_help_shows_examples | getvalue |
| [tests/test_triangle.py:461](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:461) | TestExtractMalformedLines.test_malformed_req_id_logged_and_skipped | output |
| [tests/test_triangle.py:1189](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:1189) | TestDriftHelpText.test_help_includes_description | stdout |
| [tests/test_triangle.py:1205](/Users/jeff/Documents/Code/gzkit/tests/test_triangle.py:1205) | TestDriftHelpText.test_help_lines_under_80_chars | stdout |
| [tests/test_uncovered_accept_kind_gate.py:60](/Users/jeff/Documents/Code/gzkit/tests/test_uncovered_accept_kind_gate.py:60) | TestBehaviorReqCannotBeWaived.test_refusal_names_the_req_the_kind_and_the_proof_channel | getvalue |
| [tests/unit/test_progress_indication.py:82](/Users/jeff/Documents/Code/gzkit/tests/unit/test_progress_indication.py:82) | TestProgressSuppression.test_quiet_mode_suppresses_progress | getvalue |
| [tests/unit/test_progress_indication.py:91](/Users/jeff/Documents/Code/gzkit/tests/unit/test_progress_indication.py:91) | TestProgressSuppression.test_json_mode_suppresses_progress | getvalue |
| [tests/unit/test_progress_indication.py:104](/Users/jeff/Documents/Code/gzkit/tests/unit/test_progress_indication.py:104) | TestProgressStdout.test_progress_never_writes_stdout | getvalue |
| [tests/unit/test_progress_indication.py:127](/Users/jeff/Documents/Code/gzkit/tests/unit/test_progress_indication.py:127) | TestProgressNonTTY.test_non_tty_prints_status_lines | getvalue |
| [tests/unit/test_runtime_presentation.py:272](/Users/jeff/Documents/Code/gzkit/tests/unit/test_runtime_presentation.py:272) | TestBlockersPrefix.test_parser_error_uses_blockers_prefix | getvalue,stderr |
| [tests/unit/test_runtime_presentation.py:405](/Users/jeff/Documents/Code/gzkit/tests/unit/test_runtime_presentation.py:405) | TestJsonModeClean.test_emit_status_json_no_symbols | getvalue |
