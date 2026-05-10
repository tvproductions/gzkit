# CHORE-LOG: pep257-docstring-compliance

## 2026-05-10T13:53:06-05:00
- Status: FAIL
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.60s) -- exit 0 == 0
  - [FAIL] `uvx ruff check src/gzkit --select D` => rc=1 (0.07s) -- exit 1 != 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                                                  | Total | Miss | Cover | Cover% |
|-------------------------------------------------------|-------|------|-------|--------|
| __init__.py                                           |     1 |    0 |     1 |   100% |
| __main__.py                                           |     1 |    0 |     1 |   100% |
| adr_eval.py                                           |    13 |    2 |    11 |    85% |
| adr_eval_redteam.py                                   |     4 |    0 |     4 |   100% |
| adr_eval_scoring.py                                   |    17 |   14 |     3 |    18% |
| config.py                                             |    10 |    0 |    10 |   100% |
| decomposition.py                                      |     1 |    0 |     1 |   100% |
| events.py                                             |    55 |   11 |    44 |    80% |
| git_sync.py                                           |     8 |    0 |     8 |   100% |
| handoff_validation.py                                 |    13 |    3 |    10 |    77% |
| instruction_audit.py                                  |     6 |    0 |     6 |   100% |
| instruction_eval.py                                   |    17 |   10 |     7 |    41% |
| interview.py                                          |    11 |    0 |    11 |   100% |
| ledger.py                                             |    40 |    6 |    34 |    85% |
| ledger_events.py                                      |    26 |    0 |    26 |   100% |
| ledger_proof.py                                       |     5 |    0 |     5 |   100% |
| ledger_semantics.py                                   |    22 |    0 |    22 |   100% |
| lifecycle.py                                          |     5 |    0 |     5 |   100% |
| lock_manager.py                                       |    14 |    0 |    14 |   100% |
| personas.py                                           |    18 |    0 |    18 |   100% |
| pipeline_dispatch.py                                  |    26 |    0 |    26 |   100% |
| pipeline_markers.py                                   |    38 |    0 |    38 |   100% |
| pipeline_runtime.py                                   |    16 |    0 |    16 |   100% |
| pipeline_verification.py                              |    19 |    2 |    17 |    89% |
| quality.py                                            |    52 |    0 |    52 |   100% |
| registry.py                                           |    10 |    0 |    10 |   100% |
| roles.py                                              |    14 |    0 |    14 |   100% |
| rules.py                                              |    22 |    0 |    22 |   100% |
| skill_contract.py                                     |     1 |    0 |     1 |   100% |
| skills.py                                             |    17 |    0 |    17 |   100% |
| skills_audit.py                                       |    21 |    0 |    21 |   100% |
| skills_mirror.py                                      |     7 |    0 |     7 |   100% |
| sync.py                                               |     7 |    0 |     7 |   100% |
| sync_skill_validation.py                              |    17 |    0 |    17 |   100% |
| sync_skills.py                                        |    17 |    0 |    17 |   100% |
| sync_skills_validation.py                             |    15 |    0 |    15 |   100% |
| sync_surfaces.py                                      |    18 |    0 |    18 |   100% |
| tasks.py                                              |    13 |    0 |    13 |   100% |
| temporal_drift.py                                     |    14 |    0 |    14 |   100% |
| traceability.py                                       |    31 |    4 |    27 |    87% |
| triangle.py                                           |    22 |    1 |    21 |    95% |
| utils.py                                              |     7 |    0 |     7 |   100% |
| validate.py                                           |     3 |    0 |     3 |   100% |
| adapters\__init__.py                                  |     1 |    0 |     1 |   100% |
| adapters\config.py                                    |     5 |    0 |     5 |   100% |
| arb\__init__.py                                       |     1 |    0 |     1 |   100% |
| arb\advisor.py                                        |     7 |    3 |     4 |    57% |
| arb\paths.py                                          |     2 |    0 |     2 |   100% |
| arb\patterns.py                                       |     8 |    1 |     7 |    88% |
| arb\ruff_reporter.py                                  |    12 |   10 |     2 |    17% |
| arb\step_reporter.py                                  |     5 |    3 |     2 |    40% |
| arb\validator.py                                      |     8 |    3 |     5 |    62% |
| chores\__init__.py                                    |     7 |    2 |     5 |    71% |
| chores\eval_feedback_cluster_lib.py                   |    13 |    0 |    13 |   100% |
| chores\pythonic-design-pattern-detection\scan.py      |    34 |   33 |     1 |     3% |
| cli\__init__.py                                       |     2 |    1 |     1 |    50% |
| cli\formatters.py                                     |    25 |    0 |    25 |   100% |
| cli\logging.py                                        |     5 |    0 |     5 |   100% |
| cli\main.py                                           |     8 |    1 |     7 |    88% |
| cli\parser.py                                         |     7 |    2 |     5 |    71% |
| cli\parser_arb.py                                     |    11 |    8 |     3 |    27% |
| cli\parser_artifacts.py                               |    10 |    1 |     9 |    90% |
| cli\parser_governance.py                              |     5 |    1 |     4 |    80% |
| cli\parser_maintenance.py                             |    11 |    1 |    10 |    91% |
| cli\progress.py                                       |     6 |    0 |     6 |   100% |
| cli\helpers\__init__.py                               |     1 |    0 |     1 |   100% |
| cli\helpers\common_flags.py                           |     2 |    0 |     2 |   100% |
| cli\helpers\epilog.py                                 |     2 |    0 |     2 |   100% |
| cli\helpers\exit_codes.py                             |     2 |    0 |     2 |   100% |
| cli\helpers\standard_options.py                       |     7 |    0 |     7 |   100% |
| commands\__init__.py                                  |     1 |    0 |     1 |   100% |
| commands\adr_audit.py                                 |    33 |    0 |    33 |   100% |
| commands\adr_audit_covers_backfill.py                 |    27 |    3 |    24 |    89% |
| commands\adr_coverage.py                              |    12 |    0 |    12 |   100% |
| commands\adr_promote.py                               |    11 |    0 |    11 |   100% |
| commands\adr_promote_utils.py                         |    20 |    0 |    20 |   100% |
| commands\arb.py                                       |     9 |    0 |     9 |   100% |
| commands\attest.py                                    |     6 |    0 |     6 |   100% |
| commands\audit_cmd.py                                 |     9 |    0 |     9 |   100% |
| commands\ceremony_data.py                             |    18 |    2 |    16 |    89% |
| commands\ceremony_intent.py                           |     6 |    1 |     5 |    83% |
| commands\ceremony_steps.py                            |    12 |    0 |    12 |   100% |
| commands\chores.py                                    |    28 |    0 |    28 |   100% |
| commands\chores_exec.py                               |     8 |    0 |     8 |   100% |
| commands\chores_propose_ghi_cmd.py                    |     6 |    0 |     6 |   100% |
| commands\cli_audit.py                                 |     7 |    0 |     7 |   100% |
| commands\closeout.py                                  |    18 |    9 |     9 |    50% |
| commands\closeout_ceremony.py                         |    27 |    6 |    21 |    78% |
| commands\closeout_form.py                             |    14 |    1 |    13 |    93% |
| commands\common.py                                    |    29 |    1 |    28 |    97% |
| commands\complexity_advise.py                         |    13 |    2 |    11 |    85% |
| commands\complexity_distill_cmd.py                    |     7 |    0 |     7 |   100% |
| commands\complexity_guide.py                          |     4 |    0 |     4 |   100% |
| commands\config_paths.py                              |    10 |    0 |    10 |   100% |
| commands\covers.py                                    |     6 |    0 |     6 |   100% |
| commands\drift.py                                     |     6 |    0 |     6 |   100% |
| commands\flags.py                                     |     5 |    0 |     5 |   100% |
| commands\frontmatter_reconcile.py                     |     4 |    0 |     4 |   100% |
| commands\gates.py                                     |    14 |    6 |     8 |    57% |
| commands\init_cmd.py                                  |    15 |    0 |    15 |   100% |
| commands\interview_cmd.py                             |     5 |    0 |     5 |   100% |
| commands\issue_cmd.py                                 |     8 |    0 |     8 |   100% |
| commands\justify_cmd.py                               |     2 |    0 |     2 |   100% |
| commands\obpi_audit_cmd.py                            |    20 |    0 |    20 |   100% |
| commands\obpi_cmd.py                                  |    11 |    0 |    11 |   100% |
| commands\obpi_complete.py                             |    35 |    0 |    35 |   100% |
| commands\obpi_lock.py                                 |     6 |    0 |     6 |   100% |
| commands\obpi_lock_cmd.py                             |     1 |    0 |     1 |   100% |
| commands\obpi_precomplete.py                          |    13 |    0 |    13 |   100% |
| commands\obpi_stages.py                               |    14 |    1 |    13 |    93% |
| commands\parity.py                                    |     3 |    0 |     3 |   100% |
| commands\patch_release.py                             |    23 |    0 |    23 |   100% |
| commands\personas.py                                  |     5 |    0 |     5 |   100% |
| commands\pipeline.py                                  |     9 |    0 |     9 |   100% |
| commands\plan.py                                      |    10 |    0 |    10 |   100% |
| commands\plan_audit_cmd.py                            |    18 |    0 |    18 |   100% |
| commands\preflight.py                                 |     5 |    0 |     5 |   100% |
| commands\quality.py                                   |    17 |    2 |    15 |    88% |
| commands\readiness.py                                 |    12 |    0 |    12 |   100% |
| commands\register.py                                  |    14 |    1 |    13 |    93% |
| commands\roles.py                                     |     4 |    0 |     4 |   100% |
| commands\skills_cmd.py                                |     9 |    0 |     9 |   100% |
| commands\specify_cmd.py                               |    37 |    0 |    37 |   100% |
| commands\state.py                                     |     9 |    0 |     9 |   100% |
| commands\status.py                                    |    15 |    1 |    14 |    93% |
| commands\status_obpi.py                               |    16 |    4 |    12 |    75% |
| commands\status_obpi_inspect.py                       |    14 |   10 |     4 |    29% |
| commands\status_render.py                             |    13 |    3 |    10 |    77% |
| commands\sync.py                                      |    11 |    0 |    11 |   100% |
| commands\task.py                                      |    10 |    0 |    10 |   100% |
| commands\tidy.py                                      |     6 |    0 |     6 |   100% |
| commands\validate_cmd.py                              |    31 |    2 |    29 |    94% |
| commands\validate_frontmatter.py                      |    10 |    1 |     9 |    90% |
| commands\version_sync.py                              |     9 |    0 |     9 |   100% |
| complexity\__init__.py                                |     1 |    0 |     1 |   100% |
| complexity\aggregator.py                              |     6 |    0 |     6 |   100% |
| complexity\baseline.py                                |    11 |    0 |    11 |   100% |
| complexity\citation.py                                |     4 |    0 |     4 |   100% |
| complexity\distillation.py                            |    18 |    0 |    18 |   100% |
| complexity\measurement.py                             |    24 |    1 |    23 |    96% |
| complexity\thresholds.py                              |    10 |    2 |     8 |    80% |
| complexity\advisor\__init__.py                        |     1 |    0 |     1 |   100% |
| complexity\advisor\archetype_rules.py                 |    18 |    9 |     9 |    50% |
| complexity\advisor\config.py                          |     2 |    0 |     2 |   100% |
| complexity\advisor\diagnosis.py                       |     8 |    2 |     6 |    75% |
| complexity\advisor\engine.py                          |    14 |    9 |     5 |    36% |
| complexity\advisor\intrinsic.py                       |     5 |    1 |     4 |    80% |
| complexity\advisor\presentation.py                    |    10 |    0 |    10 |   100% |
| complexity\advisor\timeout.py                         |    10 |    3 |     7 |    70% |
| complexity\authoring\__init__.py                      |     1 |    0 |     1 |   100% |
| complexity\authoring\engine.py                        |     8 |    0 |     8 |   100% |
| complexity\authoring\hint.py                          |     4 |    1 |     3 |    75% |
| complexity\authoring\protocol.py                      |    13 |    1 |    12 |    92% |
| core\__init__.py                                      |     1 |    0 |     1 |   100% |
| core\exceptions.py                                    |    15 |    0 |    15 |   100% |
| core\lifecycle.py                                     |     7 |    0 |     7 |   100% |
| core\models.py                                        |    25 |    0 |    25 |   100% |
| core\scoring.py                                       |    15 |    2 |    13 |    87% |
| core\validation_rules.py                              |     5 |    0 |     5 |   100% |
| doc_coverage\__init__.py                              |     1 |    0 |     1 |   100% |
| doc_coverage\flag_scanner.py                          |     6 |    0 |     6 |   100% |
| doc_coverage\manifest.py                              |     7 |    0 |     7 |   100% |
| doc_coverage\models.py                                |     8 |    0 |     8 |   100% |
| doc_coverage\runner.py                                |     4 |    0 |     4 |   100% |
| doc_coverage\scanner.py                               |    23 |    1 |    22 |    96% |
| eval\__init__.py                                      |     1 |    0 |     1 |   100% |
| eval\datasets.py                                      |     9 |    0 |     9 |   100% |
| eval\delta.py                                         |    11 |    0 |    11 |   100% |
| eval\regression.py                                    |    12 |    0 |    12 |   100% |
| eval\runner.py                                        |     6 |    0 |     6 |   100% |
| eval\scorer.py                                        |    13 |    1 |    12 |    92% |
| flags\__init__.py                                     |     1 |    0 |     1 |   100% |
| flags\decisions.py                                    |     6 |    0 |     6 |   100% |
| flags\diagnostics.py                                  |     6 |    0 |     6 |   100% |
| flags\models.py                                       |     9 |    0 |     9 |   100% |
| flags\registry.py                                     |     3 |    0 |     3 |   100% |
| flags\service.py                                      |    13 |    0 |    13 |   100% |
| governance\__init__.py                                |     1 |    0 |     1 |   100% |
| governance\adr_status_index.py                        |    12 |    1 |    11 |    92% |
| governance\brief_path_validity.py                     |    12 |    0 |    12 |   100% |
| governance\frontmatter_coherence.py                   |    23 |    0 |    23 |   100% |
| governance\req_coverage.py                            |     5 |    0 |     5 |   100% |
| governance\status_vocab.py                            |     2 |    0 |     2 |   100% |
| governance\trust_audits\__init__.py                   |     1 |    0 |     1 |   100% |
| governance\trust_audits\absorption_duplicates.py      |     5 |    2 |     3 |    60% |
| governance\trust_audits\advisor_proof_binding.py      |    12 |    6 |     6 |    50% |
| governance\trust_audits\attestation_receipts.py       |    12 |    3 |     9 |    75% |
| governance\trust_audits\briefs.py                     |    10 |    2 |     8 |    80% |
| governance\trust_audits\chores.py                     |     5 |    1 |     4 |    80% |
| governance\trust_audits\cli.py                        |     8 |    0 |     8 |   100% |
| governance\trust_audits\code_quality.py               |     4 |    0 |     4 |   100% |
| governance\trust_audits\complexity_doctrine_links.py  |    10 |    0 |    10 |   100% |
| governance\trust_audits\complexity_thresholds.py      |     7 |    4 |     3 |    43% |
| governance\trust_audits\cross_platform.py             |    10 |    2 |     8 |    80% |
| governance\trust_audits\doc_surface_parity.py         |     2 |    1 |     1 |    50% |
| governance\trust_audits\evaluation_justify_binding.py |     5 |    0 |     5 |   100% |
| governance\trust_audits\events.py                     |    13 |    6 |     7 |    54% |
| governance\trust_audits\insights.py                   |     3 |    0 |     3 |   100% |
| governance\trust_audits\instructions_files_budget.py  |     4 |    1 |     3 |    75% |
| governance\trust_audits\intrinsic_attestation.py      |     2 |    0 |     2 |   100% |
| governance\trust_audits\models.py                     |     8 |    5 |     3 |    38% |
| governance\trust_audits\orientation.py                |    16 |    6 |    10 |    62% |
| governance\trust_audits\reconcile.py                  |     5 |    1 |     4 |    80% |
| governance\trust_audits\release.py                    |     4 |    1 |     3 |    75% |
| governance\trust_audits\sensitivity.py                |     9 |    1 |     8 |    89% |
| governance\trust_audits\taxonomy.py                   |    15 |    6 |     9 |    60% |
| hooks\__init__.py                                     |     1 |    0 |     1 |   100% |
| hooks\claude.py                                       |    10 |    0 |    10 |   100% |
| hooks\copilot.py                                      |     4 |    0 |     4 |   100% |
| hooks\core.py                                         |    13 |    4 |     9 |    69% |
| hooks\guards.py                                       |     9 |    0 |     9 |   100% |
| hooks\install_complexity_advisor.py                   |    10 |    1 |     9 |    90% |
| hooks\obpi.py                                         |    30 |    0 |    30 |   100% |
| hooks\scripts\__init__.py                             |     1 |    0 |     1 |   100% |
| hooks\scripts\ghi.py                                  |     2 |    0 |     2 |   100% |
| hooks\scripts\pipeline.py                             |     4 |    0 |     4 |   100% |
| hooks\scripts\quality.py                              |     2 |    0 |     2 |   100% |
| hooks\scripts\routing.py                              |     4 |    0 |     4 |   100% |
| hooks\scripts\validation.py                           |     4 |    0 |     4 |   100% |
| insights\__init__.py                                  |     1 |    0 |     1 |   100% |
| insights\model.py                                     |     2 |    0 |     2 |   100% |
| justify\__init__.py                                   |     1 |    0 |     1 |   100% |
| justify\anchors.py                                    |     5 |    3 |     2 |    40% |
| justify\cli.py                                        |     6 |    3 |     3 |    50% |
| justify\complexity_hints.py                           |     5 |    0 |     5 |   100% |
| justify\evidence.py                                   |    14 |   12 |     2 |    14% |
| justify\models.py                                     |     8 |    1 |     7 |    88% |
| justify\parser.py                                     |    12 |    3 |     9 |    75% |
| justify\walkthrough.py                                |    14 |    7 |     7 |    50% |
| justify\templates\__init__.py                         |     1 |    0 |     1 |   100% |
| models\__init__.py                                    |     1 |    0 |     1 |   100% |
| models\exemplar.py                                    |     6 |    0 |     6 |   100% |
| models\frontmatter.py                                 |     1 |    0 |     1 |   100% |
| models\persona.py                                     |     9 |    0 |     9 |   100% |
| models\security_surfaces.py                           |     7 |    3 |     4 |    57% |
| ports\__init__.py                                     |     1 |    0 |     1 |   100% |
| ports\interfaces.py                                   |    14 |    0 |    14 |   100% |
| reporter\__init__.py                                  |     1 |    0 |     1 |   100% |
| reporter\panels.py                                    |     2 |    0 |     2 |   100% |
| reporter\presets.py                                   |     7 |    0 |     7 |   100% |
| scan\__init__.py                                      |     1 |    0 |     1 |   100% |
| scan\mapping.py                                       |     2 |    0 |     2 |   100% |
| scan\models.py                                        |     9 |    6 |     3 |    33% |
| schemas\__init__.py                                   |     3 |    0 |     3 |   100% |
| templates\__init__.py                                 |     7 |    1 |     6 |    86% |
| validate_pkg\__init__.py                              |     1 |    0 |     1 |   100% |
| validate_pkg\document.py                              |     6 |    0 |     6 |   100% |
| validate_pkg\ledger_check.py                          |    10 |    7 |     3 |    30% |
| validate_pkg\manifest.py                              |     2 |    0 |     2 |   100% |
| validate_pkg\surface.py                               |     4 |    0 |     4 |   100% |
| validate_pkg\sync_parity.py                           |    10 |    0 |    10 |   100% |
| validators\__init__.py                                |     1 |    0 |     1 |   100% |
| validators\unscoped_rules.py                          |    11 |    0 |    11 |   100% |
|-------------------------------------------------------|-------|------|-------|--------|
| TOTAL                                                 |  2590 |  312 |  2278 |  88.0% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 88.0%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\chores\eval_feedback_cluster_lib.py:347:5
    |
345 |             (default 3.0).
346 |
347 |     Returns:
    |     ^^^^^^^
348 |         List of newly-written ProposalRecord objects. Empty if no new clusters
349 |         exceed threshold or all matching clusters were already written.
    |
help: Add blank line after "Returns"

D101 Missing docstring in public class
  --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:33:7
   |
33 | class Candidate(NamedTuple):
   |       ^^^^^^^^^
34 |     file: Path
35 |     line: int
   |

D103 Missing docstring in public function
   --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:537:5
    |
537 | def scan_file(path: Path, source: str) -> Iterator[Candidate]:
    |     ^^^^^^^^^
538 |     try:
539 |         tree = ast.parse(source, filename=str(path))
    |

D103 Missing docstring in public function
   --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:574:5
    |
574 | def scan_root(root: Path, exclude: Iterable[str]) -> list[Candidate]:
    |     ^^^^^^^^^
575 |     excludes = tuple(exclude)
576 |     candidates: list[Candidate] = []
    |

D103 Missing docstring in public function
   --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:589:5
    |
589 | def render_report(candidates: list[Candidate], root: Path, scanned_count: int) -> str:
    |     ^^^^^^^^^^^^^
590 |     today = dt.date.today().isoformat()
591 |     lines: list[str] = [
    |

D103 Missing docstring in public function
   --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:889:5
    |
889 | def run_self_test() -> int:
    |     ^^^^^^^^^^^^^
890 |     errors: list[str] = []
891 |     for expected_pattern, source, expected_name in _SELF_TEST_FIXTURES:
    |

D103 Missing docstring in public function
   --> src\gzkit\chores\pythonic-design-pattern-detection\scan.py:920:5
    |
920 | def main(argv: list[str] | None = None) -> int:
    |     ^^^^
921 |     parser = argparse.ArgumentParser(description=__doc__)
922 |     parser.add_argument("--root", type=Path, default=Path("src"), help="Source tree to scan")
    |

D205 1 blank line required between summary line and description
   --> src\gzkit\commands\adr_audit_covers_backfill.py:483:5
    |
482 |   def _ceremony_subject_marker(sha: str, project_root: Path, git_runner: GitRunner) -> str | None:
483 | /     """Return the canonical ceremony name when ``sha``'s subject carries the historical
484 | |     parenthesized suffix (e.g. ``(gz git-sync)``) at end of line.
485 | |
486 | |     Pre-GHI #201 ceremony commits embedded the marker in the subject suffix
487 | |     rather than the ``Ceremony:`` trailer; ADR-0.0.16 and other foundation-kind
488 | |     ADRs closed under that window failed audit-check despite legitimate
489 | |     cross-OBPI coverage extension being bundled into a single ``gz git-sync``
490 | |     commit. Maps the historical suffix to the same canonical names that
491 | |     :data:`_EXEMPT_CEREMONIES` enumerates.
492 | |     """
    | |_______^
493 |       rc, stdout, _stderr = git_runner(["log", "-1", "--format=%s", sha], project_root)
494 |       if rc != 0:
    |
help: Insert single blank line

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\commands\complexity_advise.py:183:5
    |
181 |     pending operator authoring.
182 |
183 |     Returns:
    |     ^^^^^^^
184 |         (diagnoses, attested_infos, func_block_count)
185 |     """
    |
help: Add blank line after "Returns"

D205 1 blank line required between summary line and description
   --> src\gzkit\commands\quality.py:283:5
    |
282 |   def _build_check_steps() -> list[tuple[str, CheckStepRunner]]:
283 | /     """Build the canonical `gz check` steps list. Module-scope-importable so
284 | |     tests and external callers can introspect the aggregator without invoking
285 | |     the full check pipeline (REQ-0.0.27-07-06)."""
    | |__________________________________________________^
286 |       from gzkit.quality import (
287 |           run_adr_status_fresh_audit,
    |
help: Insert single blank line

D209 [*] Multi-line docstring closing quotes should be on a separate line
   --> src\gzkit\commands\quality.py:283:5
    |
282 |   def _build_check_steps() -> list[tuple[str, CheckStepRunner]]:
283 | /     """Build the canonical `gz check` steps list. Module-scope-importable so
284 | |     tests and external callers can introspect the aggregator without invoking
285 | |     the full check pipeline (REQ-0.0.27-07-06)."""
    | |__________________________________________________^
286 |       from gzkit.quality import (
287 |           run_adr_status_fresh_audit,
    |
help: Move closing quotes to new line

D102 Missing docstring in public method
  --> src\gzkit\complexity\advisor\archetype_rules.py:94:9
   |
92 |     bands: tuple[Literal["block", "warn", "advise"], ...] = Field(min_length=1)
93 |
94 |     def matches(self, metric: str, band: str) -> bool:
   |         ^^^^^^^
95 |         return metric in self.metrics and band in self.bands
   |

D102 Missing docstring in public method
   --> src\gzkit\complexity\advisor\archetype_rules.py:132:9
    |
130 |         return self
131 |
132 |     def matches(self, node: ast.AST) -> bool:
    |         ^^^^^^^
133 |         if self.node_kind is not None and type(node).__name__ != self.node_kind:
134 |             return False
    |

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\advisor\archetype_rules.py:163:5
    |
162 |   def load_archetype_rules(path: Path | None = None) -> tuple[ArchetypeRule, ...]:
163 | /     """Load and validate the rule table at ``path`` (default: canonical path).
164 | |
165 | |     Validates against the JSON Schema mirror first (collecting every error in
166 | |     one pass; no silent truncation), then constructs frozen Pydantic
167 | |     ``ArchetypeRule`` instances. Raises :class:`ValueError` on schema failure;
168 | |     raises :class:`pydantic.ValidationError` on Pydantic-level failure.
169 | |     """
    | |_______^
170 |
171 |       target = path if path is not None else CANONICAL_RULE_TABLE_PATH
    |
help: Remove blank line(s) after function docstring

D107 Missing docstring in `__init__`
   --> src\gzkit\complexity\advisor\engine.py:109:9
    |
107 |     """
108 |
109 |     def __init__(
    |         ^^^^^^^^
110 |         self,
111 |         rules: tuple[ArchetypeRule, ...] | None = None,
    |

D102 Missing docstring in public method
   --> src\gzkit\complexity\advisor\engine.py:121:9
    |
119 |         )
120 |
121 |     def diagnose(
    |         ^^^^^^^^
122 |         self,
123 |         ast_context: AstContext,
    |

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\advisor\engine.py:167:5
    |
165 |     rules: tuple[ArchetypeRule, ...] | None = None,
166 | ) -> AdvisorDiagnosis | None:
167 |     """Module-level convenience wrapper around :class:`DiagnosisEngine`."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
168 |
169 |     return DiagnosisEngine(rules=rules).diagnose(ast_context, metric, value, table)
    |
help: Remove blank line(s) after function docstring

D401 First line of docstring should be in imperative mood: "Decorator declaring a function as having irreducibly intrinsic complexity."
  --> src\gzkit\complexity\advisor\intrinsic.py:20:5
   |
19 |   def intrinsic_complexity(*, reason: str, attestor: str) -> Callable[[_F], _F]:
20 | /     """Decorator declaring a function as having irreducibly intrinsic complexity.
21 | |
22 | |     No-op at runtime: returns the decorated function unchanged.
23 | |     Registers (file_path, qualname) -> (reason, attestor, date) in the module registry.
24 | |     """
   | |_______^
25 |       decoration_date = date.today().isoformat()
   |

D413 [*] Missing blank line after last section ("Returns")
  --> src\gzkit\complexity\advisor\presentation.py:44:9
   |
42 |             functions_checked: Number of functions checked (for reporting).
43 |
44 |         Returns:
   |         ^^^^^^^
45 |             Formatted output string.
46 |         """
   |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
  --> src\gzkit\complexity\advisor\presentation.py:70:9
   |
68 |             functions_checked: Number of functions checked.
69 |
70 |         Returns:
   |         ^^^^^^^
71 |             Verbose formatted output; "no crossings" message if diagnoses empty.
72 |         """
   |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
  --> src\gzkit\complexity\advisor\presentation.py:92:9
   |
90 |             diagnosis: The diagnosis to format.
91 |
92 |         Returns:
   |         ^^^^^^^
93 |             Multi-line formatted string for this diagnosis.
94 |         """
   |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\complexity\advisor\presentation.py:138:9
    |
136 |             end_line: Last line to read (1-indexed inclusive).
137 |
138 |         Returns:
    |         ^^^^^^^
139 |             Formatted source code snippet or fallback message.
140 |         """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\complexity\advisor\presentation.py:183:9
    |
181 |             functions_checked: Number of functions checked (unused in auto-chain).
182 |
183 |         Returns:
    |         ^^^^^^^
184 |             Concise formatted output (empty string if no diagnoses).
185 |         """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\complexity\advisor\presentation.py:204:9
    |
202 |             diagnosis: The diagnosis to format.
203 |
204 |         Returns:
    |         ^^^^^^^
205 |             One-line summary (no doctrinal excerpt).
206 |         """
    |
help: Add blank line after "Returns"

D301 Use `r"""` if any backslashes in a docstring
  --> src\gzkit\complexity\authoring\protocol.py:1:1
   |
 1 | / """JSON-over-stdio protocol server for editor/IDE integration (OBPI-0.0.30-04).
 2 | |
 3 | | Implements a Content-Length-framed JSON-RPC-like protocol over binary stdio.
 4 | | Invoked by ``gz complexity-guide --server``. Three message types:
 5 | | ``initialize``, ``analyze``, ``shutdown``.
 6 | |
 7 | | Framing follows the Language Server Protocol envelope:
 8 | |     Content-Length: <N>\r\n\r\n<N bytes of UTF-8 JSON>
 9 | |
10 | | No third-party JSON-RPC library is used (stdlib-first doctrine).
11 | | """
   | |___^
12 |
13 |   from __future__ import annotations
   |
help: Add `r` prefix

D301 Use `r"""` if any backslashes in a docstring
   --> src\gzkit\complexity\authoring\protocol.py:146:5
    |
145 |   def _configure_binary_stdio() -> None:
146 | /     """Reconfigure sys.stdin/stdout to binary mode at server startup.
147 | |
148 | |     On Windows the CRT opens stdin/stdout in O_TEXT mode at the fd level,
149 | |     which allows \\n→\\r\\n translation and corrupts Content-Length framing.
150 | |     Calling msvcrt.setmode forces O_BINARY on the underlying fd.
151 | |     On POSIX this is a no-op.
152 | |     """
    | |_______^
153 |       if sys.platform == "win32":
154 |           import msvcrt
    |
help: Add `r` prefix

D202 [*] No blank lines allowed after function docstring (found 1)
  --> src\gzkit\complexity\citation.py:47:5
   |
46 |   def parse_citation(text: str) -> Citation:
47 | /     """Parse the canonical string form into a ``Citation`` instance.
48 | |
49 | |     Canonical form is::
50 | |
51 | |         docs/governance/complexity/distilled-characteristics-{date}.md
52 | |             § {anchor} (corpus revision {N})
53 | |
54 | |     Raises :class:`pydantic.ValidationError` when any of the three fields is
55 | |     missing or fails its constraint.
56 | |     """
   | |_______^
57 |
58 |       match = _CANONICAL_PATTERN.match(text.strip())
   |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
  --> src\gzkit\complexity\citation.py:77:5
   |
75 |       supported_window: int = DEFAULT_SUPPORTED_WINDOW,
76 |   ) -> bool:
77 | /     """Return ``True`` when ``citation`` is portable against ``current_revision``.
78 | |
79 | |     A citation written against revision ``N`` is portable when ``current_revision``
80 | |     is in ``[N, N + supported_window - 1]``.  At ``current_revision >= N + supported_window``
81 | |     the citation is out of date and the link-integrity validator (OBPI-07) flags
82 | |     it for amendment.
83 | |     """
   | |_______^
84 |
85 |       delta = current_revision - citation.corpus_revision
   |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:149:5
    |
148 | def _select_cross_metric(baseline: BaselineArtifact, metric_key: str) -> CrossMetricAggregate:
149 |     """Look up a cross-project aggregate by metric key, fail closed if absent."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
150 |
151 |     for aggregate in baseline.cross_project.metrics:
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:159:5
    |
158 | def render_metric_triple(metric_key: str, baseline: BaselineArtifact) -> PerMetricTriple:
159 |     """Build the per-metric triple from the cross-project p90 boundary."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
160 |
161 |     cross = _select_cross_metric(baseline, metric_key)
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:173:5
    |
172 | def _render_metric_aggregate_prose(metric_key: str, baseline: BaselineArtifact) -> str:
173 |     """Agent-drafted percentile prose per metric (REQ-03 prose surface)."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
174 |
175 |     cross = _select_cross_metric(baseline, metric_key)
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:188:5
    |
187 | def _variance_commentary(variance: float) -> str:
188 |     """One-line commentary on inter-project variance shape."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
189 |
190 |     if variance < 0.5:
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:198:5
    |
197 | def _render_practitioner_eye_block(metric_key: str) -> str:
198 |     """Operator-attested practitioner-eye placeholder (REQ-10 surface)."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
199 |
200 |     return (
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:209:5
    |
208 | def _render_metric_section(metric_key: str, baseline: BaselineArtifact) -> str:
209 |     """Render one full metric section: header + prose + triple + practitioner-eye."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
210 |
211 |     triple = render_metric_triple(metric_key, baseline)
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:227:5
    |
226 | def _render_cold_start_diff() -> str:
227 |     """REQ-03/04: first-run cold-start diff sentinel."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
228 |
229 |     return (
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:244:5
    |
243 | def _parse_prior_boundaries(prior_text: str) -> dict[str, _PriorMetricBoundary]:
244 |     """Extract per-metric boundaries from a prior distillation document."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
245 |
246 |     boundaries: dict[str, _PriorMetricBoundary] = {}
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:258:5
    |
257 | def _render_movement_line(metric_key: str, prior_absolute: float, current_absolute: float) -> str:
258 |     """Render one boundary-movement narration with operator placeholder."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
259 |
260 |     if prior_absolute == 0.0:
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:278:5
    |
276 |     current_baseline: BaselineArtifact,
277 | ) -> str:
278 |     """REQ-04: diff against prior distillation, or cold-start sentinel."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
279 |
280 |     if prior_distillation is None:
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:318:5
    |
316 |     today: date,
317 | ) -> str:
318 |     """Render the YAML frontmatter for the distilled document."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
319 |
320 |     prior_value = (
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:334:5
    |
333 | def _render_citation_form_section(baseline: BaselineArtifact) -> str:
334 |     """REQ-06: name the canonical citation tuple."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
335 |
336 |     return (
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:358:5
    |
357 | def _resolve_output_path(*, output_dir: Path, today: date, allow_dated_sibling: bool) -> Path:
358 |     """Pick the dated output path, fail or suffix on collision per REQ-05."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
359 |
360 |     output_dir.mkdir(parents=True, exist_ok=True)
    |
help: Remove blank line(s) after function docstring

D202 [*] No blank lines allowed after function docstring (found 1)
   --> src\gzkit\complexity\distillation.py:389:5
    |
387 |     allow_dated_sibling: bool = False,
388 | ) -> Path:
389 |     """Render the full distilled-characteristics document and return its path."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
390 |
391 |     output_path = _resolve_output_path(
    |
help: Remove blank line(s) after function docstring

D107 Missing docstring in `__init__`
  --> src\gzkit\complexity\measurement.py:75:9
   |
73 |     """
74 |
75 |     def __init__(self, tool: str) -> None:
   |         ^^^^^^^^
76 |         self.tool = tool
77 |         super().__init__(f"Missing measurement tool binary: {tool!r}")
   |

D401 First line of docstring should be in imperative mood: "Comparable tuple for drift detection (excludes regen date)."
  --> src\gzkit\governance\adr_status_index.py:58:9
   |
57 |     def signature(self) -> tuple[str, ...]:
58 |         """Comparable tuple for drift detection (excludes regen date)."""
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
59 |         return (
60 |             self.adr_id,
   |

D401 First line of docstring should be in imperative mood: "Convenience: extract allowed + brief-level creates and run validity check."
   --> src\gzkit\governance\brief_path_validity.py:209:5
    |
207 |       brief_path: Path,
208 |   ) -> list[str]:
209 | /     """Convenience: extract allowed + brief-level creates and run validity check.
210 | |
211 | |     Returns an empty list when the brief has no ``## Allowed Paths`` section
212 | |     (newly scaffolded briefs surface no signal until paths are authored).
213 | |     """
    | |_______^
214 |       allowed = extract_allowed_paths(brief_path)
215 |       if not allowed:
    |

D205 1 blank line required between summary line and description
  --> src\gzkit\governance\req_coverage.py:78:5
   |
76 |       features_root: Path | None = None,
77 |   ) -> list[TestRef]:
78 | /     """Return every covering reference for ``req_id`` under ``tests_root`` and
79 | |     optionally ``features_root``.
80 | |
81 | |     Unions ``scan_test_tree(tests_root)`` (``@covers``-decorated unit tests)
82 | |     with ``scan_feature_tree(features_root)`` (``@REQ-*`` BDD scenario tags)
83 | |     when ``features_root`` is supplied — matching the ``gz covers`` behaviour
84 | |     (covers.py:174). No test modules are imported during discovery —
85 | |     REQ-0.0.25-01-05.
86 | |
87 | |     File paths are rendered with ``Path.as_posix()`` so cross-platform
88 | |     consumers (ledger artifacts, JSON, downstream string comparisons) see
89 | |     forward-slash separators on every platform per
90 | |     ``.claude/rules/cross-platform.md``.
91 | |     """
   | |_______^
92 |       records = []
93 |       if tests_root.is_dir():
   |
help: Insert single blank line

D205 1 blank line required between summary line and description
  --> src\gzkit\governance\trust_audits\complexity_doctrine_links.py:53:5
   |
52 |   def _enumerate_in_scope_artifacts(project_root: Path) -> list[Path]:
53 | /     """Return cluster ADR bodies + OBPI briefs + complexity-doctrine.md
54 | |     + docs/governance/complexity/**/*.md (excluding distilled-characteristics-*).
55 | |     """
   | |_______^
56 |       artifacts: list[Path] = []
57 |       foundation_root = project_root / "docs" / "design" / "adr" / "foundation"
   |
help: Insert single blank line

D205 1 blank line required between summary line and description
  --> src\gzkit\governance\trust_audits\complexity_doctrine_links.py:78:5
   |
77 |   def _extract_citations(file: Path) -> list[tuple[int, str]]:
78 | /     """Return (lineno, citation_text) for every line referencing a complexity doc,
79 | |     EXCLUDING any line preceded by the speculative skip marker.
80 | |     """
   | |_______^
81 |       try:
82 |           lines = file.read_text(encoding="utf-8").splitlines()
   |
help: Insert single blank line

D205 1 blank line required between summary line and description
   --> src\gzkit\governance\trust_audits\complexity_doctrine_links.py:142:5
    |
141 |   def _read_current_corpus_revision(project_root: Path) -> int | None:
142 | /     """Parse corpus_revision from frontmatter of the most recent
143 | |     distilled-characteristics-*.md (sorted by filename desc).
144 | |     """
    | |_______^
145 |       complexity_docs = project_root / "docs" / "governance" / "complexity"
146 |       if not complexity_docs.is_dir():
    |
help: Insert single blank line

D205 1 blank line required between summary line and description
   --> src\gzkit\governance\trust_audits\complexity_doctrine_links.py:185:5
    |
184 |   def validate_complexity_doctrine_links(project_root: Path) -> list[ValidationError]:
185 | /     """Main entry point. Enumerates artifacts, walks each citation, applies
186 | |     the four checks, returns list of ValidationError on any miss.
187 | |     """
    | |_______^
188 |       errors: list[ValidationError] = []
189 |       current_revision = _read_current_corpus_revision(project_root)
    |
help: Insert single blank line

D401 First line of docstring should be in imperative mood: "Main entry point. Enumerates artifacts, walks each citation, applies"
   --> src\gzkit\governance\trust_audits\complexity_doctrine_links.py:185:5
    |
184 |   def validate_complexity_doctrine_links(project_root: Path) -> list[ValidationError]:
185 | /     """Main entry point. Enumerates artifacts, walks each citation, applies
186 | |     the four checks, returns list of ValidationError on any miss.
187 | |     """
    | |_______^
188 |       errors: list[ValidationError] = []
189 |       current_revision = _read_current_corpus_revision(project_root)
    |

D103 Missing docstring in public function
  --> src\gzkit\governance\trust_audits\doc_surface_parity.py:22:5
   |
22 | def audit_doc_surface_parity(project_root: Path) -> list[ValidationError]:
   |     ^^^^^^^^^^^^^^^^^^^^^^^^
23 |     target = project_root / _DECOMMISSIONED_DIR
24 |     if not target.is_dir():
   |

D413 [*] Missing blank line after last section ("Returns")
  --> src\gzkit\governance\trust_audits\evaluation_justify_binding.py:28:5
   |
26 |     """Return ValidationError if low evaluation scores have no gz-justify artifact.
27 |
28 |     Returns:
   |     ^^^^^^^
29 |         Empty list if gate passes (no trigger, or trigger + artifact present).
30 |         Non-empty list if gate fires (trigger + no artifact).
   |
help: Add blank line after "Returns"

D401 First line of docstring should be in imperative mood: "True for ``Name``/``Attribute`` nodes referring to ``_ORIENTATION_COLLECTOR``."
   --> src\gzkit\governance\trust_audits\orientation.py:114:5
    |
113 | def _node_references_collector(node: ast.AST) -> bool:
114 |     """True for ``Name``/``Attribute`` nodes referring to ``_ORIENTATION_COLLECTOR``."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
115 |     if isinstance(node, ast.Name) and node.id == _ORIENTATION_COLLECTOR:
116 |         return True
    |

D413 [*] Missing blank line after last section ("Raises")
   --> src\gzkit\models\exemplar.py:188:5
    |
186 |         A frozen ``ExemplarCorpus`` instance.
187 |
188 |     Raises:
    |     ^^^^^^
189 |         pydantic.ValidationError: If the JSON does not conform to the
190 |             ``ExemplarCorpus`` schema.
    |
help: Add blank line after "Raises"

D102 Missing docstring in public method
  --> src\gzkit\models\security_surfaces.py:63:9
   |
61 |     rationale: str = Field(..., min_length=1, description="Why this surface is security-sensitive.")
62 |
63 |     def model_post_init(self, _context: object) -> None:
   |         ^^^^^^^^^^^^^^^
64 |         for glob in self.globs:
65 |             if not glob:
   |

D202 [*] No blank lines allowed after function docstring (found 1)
  --> src\gzkit\scan\mapping.py:21:5
   |
20 |   def load_mapping(path: Path) -> dict[str, dict[str, Any]]:
21 | /     """Load and validate the OWASP 2025 analyzer mapping at ``path``.
22 | |
23 | |     Sibling file ``mapping.schema.json`` (next to ``path``) is loaded as the
24 | |     JSON Schema and used to validate the mapping payload. Validation
25 | |     collects every error in one pass (no silent truncation) and raises
26 | |     :class:`ValueError` on failure.
27 | |
28 | |     Returns the ``categories`` dict keyed by OWASP 2025 category code
29 | |     (``A01``..``A10``). The top-level ``owasp_year`` constant is dropped
30 | |     because every consumer already imports it via the
31 | |     ``OwaspScanReport.owasp_year`` Literal.
32 | |     """
   | |_______^
33 |
34 |       schema_path = path.parent / "mapping.schema.json"
   |
help: Remove blank line(s) after function docstring

D413 [*] Missing blank line after last section ("Args")
   --> src\gzkit\sync_surfaces.py:399:5
    |
397 |     """Generate .claude/settings.json for hooks.
398 |
399 |     Args:
    |     ^^^^
400 |         project_root: Project root directory.
401 |         config: Project configuration.
    |
help: Add blank line after "Args"

Found 58 errors.
[*] 31 fixable with the `--fix` option (2 hidden fixes can be enabled with the `--unsafe-fixes` option).
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
## 2026-05-10T13:58:06-05:00
- Status: PASS
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.76s) -- exit 0 == 0
  - [PASS] `uvx ruff check src/gzkit --select D` => rc=0 (0.07s) -- exit 0 == 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                                                  | Total | Miss | Cover | Cover% |
|-------------------------------------------------------|-------|------|-------|--------|
| __init__.py                                           |     1 |    0 |     1 |   100% |
| __main__.py                                           |     1 |    0 |     1 |   100% |
| adr_eval.py                                           |    13 |    2 |    11 |    85% |
| adr_eval_redteam.py                                   |     4 |    0 |     4 |   100% |
| adr_eval_scoring.py                                   |    17 |   14 |     3 |    18% |
| config.py                                             |    10 |    0 |    10 |   100% |
| decomposition.py                                      |     1 |    0 |     1 |   100% |
| events.py                                             |    55 |   11 |    44 |    80% |
| git_sync.py                                           |     8 |    0 |     8 |   100% |
| handoff_validation.py                                 |    13 |    3 |    10 |    77% |
| instruction_audit.py                                  |     6 |    0 |     6 |   100% |
| instruction_eval.py                                   |    17 |   10 |     7 |    41% |
| interview.py                                          |    11 |    0 |    11 |   100% |
| ledger.py                                             |    40 |    6 |    34 |    85% |
| ledger_events.py                                      |    26 |    0 |    26 |   100% |
| ledger_proof.py                                       |     5 |    0 |     5 |   100% |
| ledger_semantics.py                                   |    22 |    0 |    22 |   100% |
| lifecycle.py                                          |     5 |    0 |     5 |   100% |
| lock_manager.py                                       |    14 |    0 |    14 |   100% |
| personas.py                                           |    18 |    0 |    18 |   100% |
| pipeline_dispatch.py                                  |    26 |    0 |    26 |   100% |
| pipeline_markers.py                                   |    38 |    0 |    38 |   100% |
| pipeline_runtime.py                                   |    16 |    0 |    16 |   100% |
| pipeline_verification.py                              |    19 |    2 |    17 |    89% |
| quality.py                                            |    52 |    0 |    52 |   100% |
| registry.py                                           |    10 |    0 |    10 |   100% |
| roles.py                                              |    14 |    0 |    14 |   100% |
| rules.py                                              |    22 |    0 |    22 |   100% |
| skill_contract.py                                     |     1 |    0 |     1 |   100% |
| skills.py                                             |    17 |    0 |    17 |   100% |
| skills_audit.py                                       |    21 |    0 |    21 |   100% |
| skills_mirror.py                                      |     7 |    0 |     7 |   100% |
| sync.py                                               |     7 |    0 |     7 |   100% |
| sync_skill_validation.py                              |    17 |    0 |    17 |   100% |
| sync_skills.py                                        |    17 |    0 |    17 |   100% |
| sync_skills_validation.py                             |    15 |    0 |    15 |   100% |
| sync_surfaces.py                                      |    18 |    0 |    18 |   100% |
| tasks.py                                              |    13 |    0 |    13 |   100% |
| temporal_drift.py                                     |    14 |    0 |    14 |   100% |
| traceability.py                                       |    31 |    4 |    27 |    87% |
| triangle.py                                           |    22 |    1 |    21 |    95% |
| utils.py                                              |     7 |    0 |     7 |   100% |
| validate.py                                           |     3 |    0 |     3 |   100% |
| adapters\__init__.py                                  |     1 |    0 |     1 |   100% |
| adapters\config.py                                    |     5 |    0 |     5 |   100% |
| arb\__init__.py                                       |     1 |    0 |     1 |   100% |
| arb\advisor.py                                        |     7 |    3 |     4 |    57% |
| arb\paths.py                                          |     2 |    0 |     2 |   100% |
| arb\patterns.py                                       |     8 |    1 |     7 |    88% |
| arb\ruff_reporter.py                                  |    12 |   10 |     2 |    17% |
| arb\step_reporter.py                                  |     5 |    3 |     2 |    40% |
| arb\validator.py                                      |     8 |    3 |     5 |    62% |
| chores\__init__.py                                    |     7 |    2 |     5 |    71% |
| chores\eval_feedback_cluster_lib.py                   |    13 |    0 |    13 |   100% |
| chores\pythonic-design-pattern-detection\scan.py      |    34 |   27 |     7 |    21% |
| cli\__init__.py                                       |     2 |    1 |     1 |    50% |
| cli\formatters.py                                     |    25 |    0 |    25 |   100% |
| cli\logging.py                                        |     5 |    0 |     5 |   100% |
| cli\main.py                                           |     8 |    1 |     7 |    88% |
| cli\parser.py                                         |     7 |    2 |     5 |    71% |
| cli\parser_arb.py                                     |    11 |    8 |     3 |    27% |
| cli\parser_artifacts.py                               |    10 |    1 |     9 |    90% |
| cli\parser_governance.py                              |     5 |    1 |     4 |    80% |
| cli\parser_maintenance.py                             |    11 |    1 |    10 |    91% |
| cli\progress.py                                       |     6 |    0 |     6 |   100% |
| cli\helpers\__init__.py                               |     1 |    0 |     1 |   100% |
| cli\helpers\common_flags.py                           |     2 |    0 |     2 |   100% |
| cli\helpers\epilog.py                                 |     2 |    0 |     2 |   100% |
| cli\helpers\exit_codes.py                             |     2 |    0 |     2 |   100% |
| cli\helpers\standard_options.py                       |     7 |    0 |     7 |   100% |
| commands\__init__.py                                  |     1 |    0 |     1 |   100% |
| commands\adr_audit.py                                 |    33 |    0 |    33 |   100% |
| commands\adr_audit_covers_backfill.py                 |    27 |    3 |    24 |    89% |
| commands\adr_coverage.py                              |    12 |    0 |    12 |   100% |
| commands\adr_promote.py                               |    11 |    0 |    11 |   100% |
| commands\adr_promote_utils.py                         |    20 |    0 |    20 |   100% |
| commands\arb.py                                       |     9 |    0 |     9 |   100% |
| commands\attest.py                                    |     6 |    0 |     6 |   100% |
| commands\audit_cmd.py                                 |     9 |    0 |     9 |   100% |
| commands\ceremony_data.py                             |    18 |    2 |    16 |    89% |
| commands\ceremony_intent.py                           |     6 |    1 |     5 |    83% |
| commands\ceremony_steps.py                            |    12 |    0 |    12 |   100% |
| commands\chores.py                                    |    28 |    0 |    28 |   100% |
| commands\chores_exec.py                               |     8 |    0 |     8 |   100% |
| commands\chores_propose_ghi_cmd.py                    |     6 |    0 |     6 |   100% |
| commands\cli_audit.py                                 |     7 |    0 |     7 |   100% |
| commands\closeout.py                                  |    18 |    9 |     9 |    50% |
| commands\closeout_ceremony.py                         |    27 |    6 |    21 |    78% |
| commands\closeout_form.py                             |    14 |    1 |    13 |    93% |
| commands\common.py                                    |    29 |    1 |    28 |    97% |
| commands\complexity_advise.py                         |    13 |    2 |    11 |    85% |
| commands\complexity_distill_cmd.py                    |     7 |    0 |     7 |   100% |
| commands\complexity_guide.py                          |     4 |    0 |     4 |   100% |
| commands\config_paths.py                              |    10 |    0 |    10 |   100% |
| commands\covers.py                                    |     6 |    0 |     6 |   100% |
| commands\drift.py                                     |     6 |    0 |     6 |   100% |
| commands\flags.py                                     |     5 |    0 |     5 |   100% |
| commands\frontmatter_reconcile.py                     |     4 |    0 |     4 |   100% |
| commands\gates.py                                     |    14 |    6 |     8 |    57% |
| commands\init_cmd.py                                  |    15 |    0 |    15 |   100% |
| commands\interview_cmd.py                             |     5 |    0 |     5 |   100% |
| commands\issue_cmd.py                                 |     8 |    0 |     8 |   100% |
| commands\justify_cmd.py                               |     2 |    0 |     2 |   100% |
| commands\obpi_audit_cmd.py                            |    20 |    0 |    20 |   100% |
| commands\obpi_cmd.py                                  |    11 |    0 |    11 |   100% |
| commands\obpi_complete.py                             |    35 |    0 |    35 |   100% |
| commands\obpi_lock.py                                 |     6 |    0 |     6 |   100% |
| commands\obpi_lock_cmd.py                             |     1 |    0 |     1 |   100% |
| commands\obpi_precomplete.py                          |    13 |    0 |    13 |   100% |
| commands\obpi_stages.py                               |    14 |    1 |    13 |    93% |
| commands\parity.py                                    |     3 |    0 |     3 |   100% |
| commands\patch_release.py                             |    23 |    0 |    23 |   100% |
| commands\personas.py                                  |     5 |    0 |     5 |   100% |
| commands\pipeline.py                                  |     9 |    0 |     9 |   100% |
| commands\plan.py                                      |    10 |    0 |    10 |   100% |
| commands\plan_audit_cmd.py                            |    18 |    0 |    18 |   100% |
| commands\preflight.py                                 |     5 |    0 |     5 |   100% |
| commands\quality.py                                   |    17 |    2 |    15 |    88% |
| commands\readiness.py                                 |    12 |    0 |    12 |   100% |
| commands\register.py                                  |    14 |    1 |    13 |    93% |
| commands\roles.py                                     |     4 |    0 |     4 |   100% |
| commands\skills_cmd.py                                |     9 |    0 |     9 |   100% |
| commands\specify_cmd.py                               |    37 |    0 |    37 |   100% |
| commands\state.py                                     |     9 |    0 |     9 |   100% |
| commands\status.py                                    |    15 |    1 |    14 |    93% |
| commands\status_obpi.py                               |    16 |    4 |    12 |    75% |
| commands\status_obpi_inspect.py                       |    14 |   10 |     4 |    29% |
| commands\status_render.py                             |    13 |    3 |    10 |    77% |
| commands\sync.py                                      |    11 |    0 |    11 |   100% |
| commands\task.py                                      |    10 |    0 |    10 |   100% |
| commands\tidy.py                                      |     6 |    0 |     6 |   100% |
| commands\validate_cmd.py                              |    31 |    2 |    29 |    94% |
| commands\validate_frontmatter.py                      |    10 |    1 |     9 |    90% |
| commands\version_sync.py                              |     9 |    0 |     9 |   100% |
| complexity\__init__.py                                |     1 |    0 |     1 |   100% |
| complexity\aggregator.py                              |     6 |    0 |     6 |   100% |
| complexity\baseline.py                                |    11 |    0 |    11 |   100% |
| complexity\citation.py                                |     4 |    0 |     4 |   100% |
| complexity\distillation.py                            |    18 |    0 |    18 |   100% |
| complexity\measurement.py                             |    24 |    0 |    24 |   100% |
| complexity\thresholds.py                              |    10 |    2 |     8 |    80% |
| complexity\advisor\__init__.py                        |     1 |    0 |     1 |   100% |
| complexity\advisor\archetype_rules.py                 |    18 |    7 |    11 |    61% |
| complexity\advisor\config.py                          |     2 |    0 |     2 |   100% |
| complexity\advisor\diagnosis.py                       |     8 |    2 |     6 |    75% |
| complexity\advisor\engine.py                          |    14 |    7 |     7 |    50% |
| complexity\advisor\intrinsic.py                       |     5 |    1 |     4 |    80% |
| complexity\advisor\presentation.py                    |    10 |    0 |    10 |   100% |
| complexity\advisor\timeout.py                         |    10 |    3 |     7 |    70% |
| complexity\authoring\__init__.py                      |     1 |    0 |     1 |   100% |
| complexity\authoring\engine.py                        |     8 |    0 |     8 |   100% |
| complexity\authoring\hint.py                          |     4 |    1 |     3 |    75% |
| complexity\authoring\protocol.py                      |    13 |    1 |    12 |    92% |
| core\__init__.py                                      |     1 |    0 |     1 |   100% |
| core\exceptions.py                                    |    15 |    0 |    15 |   100% |
| core\lifecycle.py                                     |     7 |    0 |     7 |   100% |
| core\models.py                                        |    25 |    0 |    25 |   100% |
| core\scoring.py                                       |    15 |    2 |    13 |    87% |
| core\validation_rules.py                              |     5 |    0 |     5 |   100% |
| doc_coverage\__init__.py                              |     1 |    0 |     1 |   100% |
| doc_coverage\flag_scanner.py                          |     6 |    0 |     6 |   100% |
| doc_coverage\manifest.py                              |     7 |    0 |     7 |   100% |
| doc_coverage\models.py                                |     8 |    0 |     8 |   100% |
| doc_coverage\runner.py                                |     4 |    0 |     4 |   100% |
| doc_coverage\scanner.py                               |    23 |    1 |    22 |    96% |
| eval\__init__.py                                      |     1 |    0 |     1 |   100% |
| eval\datasets.py                                      |     9 |    0 |     9 |   100% |
| eval\delta.py                                         |    11 |    0 |    11 |   100% |
| eval\regression.py                                    |    12 |    0 |    12 |   100% |
| eval\runner.py                                        |     6 |    0 |     6 |   100% |
| eval\scorer.py                                        |    13 |    1 |    12 |    92% |
| flags\__init__.py                                     |     1 |    0 |     1 |   100% |
| flags\decisions.py                                    |     6 |    0 |     6 |   100% |
| flags\diagnostics.py                                  |     6 |    0 |     6 |   100% |
| flags\models.py                                       |     9 |    0 |     9 |   100% |
| flags\registry.py                                     |     3 |    0 |     3 |   100% |
| flags\service.py                                      |    13 |    0 |    13 |   100% |
| governance\__init__.py                                |     1 |    0 |     1 |   100% |
| governance\adr_status_index.py                        |    12 |    1 |    11 |    92% |
| governance\brief_path_validity.py                     |    12 |    0 |    12 |   100% |
| governance\frontmatter_coherence.py                   |    23 |    0 |    23 |   100% |
| governance\req_coverage.py                            |     5 |    0 |     5 |   100% |
| governance\status_vocab.py                            |     2 |    0 |     2 |   100% |
| governance\trust_audits\__init__.py                   |     1 |    0 |     1 |   100% |
| governance\trust_audits\absorption_duplicates.py      |     5 |    2 |     3 |    60% |
| governance\trust_audits\advisor_proof_binding.py      |    12 |    6 |     6 |    50% |
| governance\trust_audits\attestation_receipts.py       |    12 |    3 |     9 |    75% |
| governance\trust_audits\briefs.py                     |    10 |    2 |     8 |    80% |
| governance\trust_audits\chores.py                     |     5 |    1 |     4 |    80% |
| governance\trust_audits\cli.py                        |     8 |    0 |     8 |   100% |
| governance\trust_audits\code_quality.py               |     4 |    0 |     4 |   100% |
| governance\trust_audits\complexity_doctrine_links.py  |    10 |    0 |    10 |   100% |
| governance\trust_audits\complexity_thresholds.py      |     7 |    4 |     3 |    43% |
| governance\trust_audits\cross_platform.py             |    10 |    2 |     8 |    80% |
| governance\trust_audits\doc_surface_parity.py         |     2 |    0 |     2 |   100% |
| governance\trust_audits\evaluation_justify_binding.py |     5 |    0 |     5 |   100% |
| governance\trust_audits\events.py                     |    13 |    6 |     7 |    54% |
| governance\trust_audits\insights.py                   |     3 |    0 |     3 |   100% |
| governance\trust_audits\instructions_files_budget.py  |     4 |    1 |     3 |    75% |
| governance\trust_audits\intrinsic_attestation.py      |     2 |    0 |     2 |   100% |
| governance\trust_audits\models.py                     |     8 |    5 |     3 |    38% |
| governance\trust_audits\orientation.py                |    16 |    6 |    10 |    62% |
| governance\trust_audits\reconcile.py                  |     5 |    1 |     4 |    80% |
| governance\trust_audits\release.py                    |     4 |    1 |     3 |    75% |
| governance\trust_audits\sensitivity.py                |     9 |    1 |     8 |    89% |
| governance\trust_audits\taxonomy.py                   |    15 |    6 |     9 |    60% |
| hooks\__init__.py                                     |     1 |    0 |     1 |   100% |
| hooks\claude.py                                       |    10 |    0 |    10 |   100% |
| hooks\copilot.py                                      |     4 |    0 |     4 |   100% |
| hooks\core.py                                         |    13 |    4 |     9 |    69% |
| hooks\guards.py                                       |     9 |    0 |     9 |   100% |
| hooks\install_complexity_advisor.py                   |    10 |    1 |     9 |    90% |
| hooks\obpi.py                                         |    30 |    0 |    30 |   100% |
| hooks\scripts\__init__.py                             |     1 |    0 |     1 |   100% |
| hooks\scripts\ghi.py                                  |     2 |    0 |     2 |   100% |
| hooks\scripts\pipeline.py                             |     4 |    0 |     4 |   100% |
| hooks\scripts\quality.py                              |     2 |    0 |     2 |   100% |
| hooks\scripts\routing.py                              |     4 |    0 |     4 |   100% |
| hooks\scripts\validation.py                           |     4 |    0 |     4 |   100% |
| insights\__init__.py                                  |     1 |    0 |     1 |   100% |
| insights\model.py                                     |     2 |    0 |     2 |   100% |
| justify\__init__.py                                   |     1 |    0 |     1 |   100% |
| justify\anchors.py                                    |     5 |    3 |     2 |    40% |
| justify\cli.py                                        |     6 |    3 |     3 |    50% |
| justify\complexity_hints.py                           |     5 |    0 |     5 |   100% |
| justify\evidence.py                                   |    14 |   12 |     2 |    14% |
| justify\models.py                                     |     8 |    1 |     7 |    88% |
| justify\parser.py                                     |    12 |    3 |     9 |    75% |
| justify\walkthrough.py                                |    14 |    7 |     7 |    50% |
| justify\templates\__init__.py                         |     1 |    0 |     1 |   100% |
| models\__init__.py                                    |     1 |    0 |     1 |   100% |
| models\exemplar.py                                    |     6 |    0 |     6 |   100% |
| models\frontmatter.py                                 |     1 |    0 |     1 |   100% |
| models\persona.py                                     |     9 |    0 |     9 |   100% |
| models\security_surfaces.py                           |     7 |    2 |     5 |    71% |
| ports\__init__.py                                     |     1 |    0 |     1 |   100% |
| ports\interfaces.py                                   |    14 |    0 |    14 |   100% |
| reporter\__init__.py                                  |     1 |    0 |     1 |   100% |
| reporter\panels.py                                    |     2 |    0 |     2 |   100% |
| reporter\presets.py                                   |     7 |    0 |     7 |   100% |
| scan\__init__.py                                      |     1 |    0 |     1 |   100% |
| scan\mapping.py                                       |     2 |    0 |     2 |   100% |
| scan\models.py                                        |     9 |    6 |     3 |    33% |
| schemas\__init__.py                                   |     3 |    0 |     3 |   100% |
| templates\__init__.py                                 |     7 |    1 |     6 |    86% |
| validate_pkg\__init__.py                              |     1 |    0 |     1 |   100% |
| validate_pkg\document.py                              |     6 |    0 |     6 |   100% |
| validate_pkg\ledger_check.py                          |    10 |    7 |     3 |    30% |
| validate_pkg\manifest.py                              |     2 |    0 |     2 |   100% |
| validate_pkg\surface.py                               |     4 |    0 |     4 |   100% |
| validate_pkg\sync_parity.py                           |    10 |    0 |    10 |   100% |
| validators\__init__.py                                |     1 |    0 |     1 |   100% |
| validators\unscoped_rules.py                          |    11 |    0 |    11 |   100% |
|-------------------------------------------------------|-------|------|-------|--------|
| TOTAL                                                 |  2590 |  299 |  2291 |  88.5% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 88.5%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
All checks passed!
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
