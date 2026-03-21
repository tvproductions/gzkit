# CHORE-LOG: coverage-40pct

## 2026-03-21T14:31:47-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (21.63s) — exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (23.34s) — exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.95s) — exit 0 == 0

```text
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.253s

OK
[uv run coverage run -m unittest discover -s tests -t . -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 22.548s

OK
[uv run coverage report --fail-under=40] stdout:
Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
src\gzkit\__init__.py                          1      0   100%
src\gzkit\cli.py                            2579    612    76%
src\gzkit\commands\__init__.py                 5      0   100%
src\gzkit\commands\attest.py                  77      2    97%
src\gzkit\commands\chores.py                 361    114    68%
src\gzkit\commands\common.py                 318     59    81%
src\gzkit\commands\plan.py                    26      4    85%
src\gzkit\commands\roles.py                   70     30    57%
src\gzkit\commands\state.py                   39      4    90%
src\gzkit\commands\status.py                 655     89    86%
src\gzkit\config.py                           70      0   100%
src\gzkit\decomposition.py                   170     25    85%
src\gzkit\events.py                          225     13    94%
src\gzkit\git_sync.py                         93     19    80%
src\gzkit\hooks\__init__.py                    3      0   100%
src\gzkit\hooks\claude.py                     80      1    99%
src\gzkit\hooks\copilot.py                    17      1    94%
src\gzkit\hooks\core.py                      169     39    77%
src\gzkit\hooks\guards.py                     61     48    21%
src\gzkit\hooks\obpi.py                      211     34    84%
src\gzkit\instruction_audit.py               124     10    92%
src\gzkit\instruction_eval.py                140     18    87%
src\gzkit\interview.py                       118     29    75%
src\gzkit\ledger.py                          575     41    93%
src\gzkit\lifecycle.py                        53      0   100%
src\gzkit\models\__init__.py                   2      0   100%
src\gzkit\models\frontmatter.py               82      3    96%
src\gzkit\pipeline_runtime.py                725     54    93%
src\gzkit\quality.py                         100     27    73%
src\gzkit\registry.py                         54      0   100%
src\gzkit\roles.py                            79      1    99%
src\gzkit\rules.py                           256     22    91%
src\gzkit\schemas\__init__.py                 12      0   100%
src\gzkit\skills.py                          347     59    83%
src\gzkit\superbook.py                       169     58    66%
src\gzkit\superbook_models.py                 63      0   100%
src\gzkit\superbook_parser.py                 90      3    97%
src\gzkit\sync.py                            656     79    88%
src\gzkit\templates\__init__.py               28      2    93%
src\gzkit\utils.py                            54      9    83%
src\gzkit\validate.py                        373    128    66%
tests\__init__.py                              0      0   100%
tests\commands\__init__.py                     0      0   100%
tests\commands\common.py                      69      6    91%
tests\commands\test_adr_promote.py            88      0   100%
tests\commands\test_adr_resolution.py         51      0   100%
tests\commands\test_attest.py                136      0   100%
tests\commands\test_audit.py                 173      0   100%
tests\commands\test_chores.py                138      0   100%
tests\commands\test_dry_run.py                32      0   100%
tests\commands\test_gates.py                  14      0   100%
tests\commands\test_init.py                   44      0   100%
tests\commands\test_lint.py                   13      0   100%
tests\commands\test_migrate_semver.py         45      0   100%
tests\commands\test_obpi_pipeline.py         248      0   100%
tests\commands\test_obpi_validate_cmd.py      48      0   100%
tests\commands\test_parsers.py                10      0   100%
tests\commands\test_plan.py                   17      0   100%
tests\commands\test_prd.py                    19      0   100%
tests\commands\test_register_adrs.py          82      0   100%
tests\commands\test_runtime.py               421      0   100%
tests\commands\test_skills.py                131      0   100%
tests\commands\test_specify.py                32      0   100%
tests\commands\test_status.py                840      0   100%
tests\commands\test_sync_cmds.py             106      1    99%
tests\commands\test_validate_cmds.py          30      0   100%
tests\test_agent_sync.py                     125      1    99%
tests\test_config.py                         120      1    99%
tests\test_decomposition.py                   36      1    97%
tests\test_hooks.py                          589      4    99%
tests\test_instruction_audit.py              240      0   100%
tests\test_instruction_eval.py               127      1    99%
tests\test_interview.py                       67      1    99%
tests\test_ledger.py                         363      1    99%
tests\test_lifecycle.py                      100      1    99%
tests\test_models.py                         129      1    99%
tests\test_obpi_validator.py                 181      1    99%
tests\test_pipeline_dispatch.py              506      1    99%
tests\test_pipeline_integration.py           159      1    99%
tests\test_pipeline_runtime.py               127      1    99%
tests\test_pyinstaller_spec.py                31      1    97%
tests\test_quality.py                         65      1    98%
tests\test_registry.py                       110      1    99%
tests\test_review_protocol.py                331      1    99%
tests\test_roles.py                          146      1    99%
tests\test_roles_cli.py                       79      1    99%
tests\test_rules.py                          306      1    99%
tests\test_schemas.py                        241     16    93%
tests\test_skill_naming.py                    32      4    88%
tests\test_skills_audit.py                   293      1    99%
tests\test_superbook.py                      101      1    99%
tests\test_superbook_models.py                35      1    97%
tests\test_superbook_parser.py                79      1    99%
tests\test_sync.py                           629      4    99%
tests\test_templates.py                       97      1    99%
tests\test_validate.py                       130      1    99%
tests\test_verification_dispatch.py          337      1    99%
--------------------------------------------------------------
TOTAL                                      18028   1698    91%
```
