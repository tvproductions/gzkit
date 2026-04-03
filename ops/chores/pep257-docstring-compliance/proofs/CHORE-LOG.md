# CHORE-LOG: pep257-docstring-compliance

## 2026-03-21T14:33:19-05:00
- Status: FAIL
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.68s) — exit 0 == 0
  - [FAIL] `uvx ruff check src/gzkit --select D` => rc=1 (0.07s) — exit 1 != 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                        |     Total |     Miss |     Cover |     Cover% |
|-----------------------------|-----------|----------|-----------|------------|
| __init__.py                 |         1 |        0 |         1 |       100% |
| cli.py                      |       139 |       11 |       128 |        92% |
| config.py                   |         8 |        0 |         8 |       100% |
| decomposition.py            |        13 |        2 |        11 |        85% |
| events.py                   |        37 |       11 |        26 |        70% |
| git_sync.py                 |         8 |        0 |         8 |       100% |
| instruction_audit.py        |         6 |        0 |         6 |       100% |
| instruction_eval.py         |        17 |       10 |         7 |        41% |
| interview.py                |        11 |        0 |        11 |       100% |
| ledger.py                   |        68 |        5 |        63 |        93% |
| lifecycle.py                |        11 |        0 |        11 |       100% |
| pipeline_runtime.py         |        85 |        5 |        80 |        94% |
| quality.py                  |        17 |        0 |        17 |       100% |
| registry.py                 |        10 |        0 |        10 |       100% |
| roles.py                    |        14 |        0 |        14 |       100% |
| rules.py                    |        21 |        0 |        21 |       100% |
| skills.py                   |        33 |        0 |        33 |       100% |
| superbook.py                |        15 |        1 |        14 |        93% |
| superbook_models.py         |        10 |        0 |        10 |       100% |
| superbook_parser.py         |         8 |        0 |         8 |       100% |
| sync.py                     |        52 |        0 |        52 |       100% |
| utils.py                    |         7 |        0 |         7 |       100% |
| validate.py                 |        23 |        7 |        16 |        70% |
| commands\__init__.py        |         1 |        0 |         1 |       100% |
| commands\attest.py          |         4 |        0 |         4 |       100% |
| commands\chores.py          |        20 |        0 |        20 |       100% |
| commands\common.py          |        31 |        2 |        29 |        94% |
| commands\plan.py            |         2 |        0 |         2 |       100% |
| commands\roles.py           |         4 |        0 |         4 |       100% |
| commands\state.py           |         2 |        0 |         2 |       100% |
| commands\status.py          |        45 |       16 |        29 |        64% |
| commands\superbook.py       |         2 |        0 |         2 |       100% |
| hooks\__init__.py           |         1 |        0 |         1 |       100% |
| hooks\claude.py             |        15 |        0 |        15 |       100% |
| hooks\copilot.py            |         4 |        0 |         4 |       100% |
| hooks\core.py               |        13 |        4 |         9 |        69% |
| hooks\guards.py             |         5 |        0 |         5 |       100% |
| hooks\obpi.py               |        18 |        0 |        18 |       100% |
| models\__init__.py          |         1 |        0 |         1 |       100% |
| models\frontmatter.py       |         9 |        0 |         9 |       100% |
| schemas\__init__.py         |         3 |        0 |         3 |       100% |
| templates\__init__.py       |         7 |        1 |         6 |        86% |
|-----------------------------|-----------|----------|-----------|------------|
| TOTAL                       |       801 |       75 |       726 |      90.6% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 90.6%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
D102 Missing docstring in public method
   --> src\gzkit\pipeline_runtime.py:593:9
    |
592 |     @property
593 |     def completed_count(self) -> int:
    |         ^^^^^^^^^^^^^^^
594 |         done = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS}
595 |         return sum(1 for r in self.records if r.status in done)
    |

D102 Missing docstring in public method
   --> src\gzkit\pipeline_runtime.py:598:9
    |
597 |     @property
598 |     def blocked_count(self) -> int:
    |         ^^^^^^^^^^^^^
599 |         return sum(1 for r in self.records if r.status == TaskStatus.BLOCKED)
    |

D102 Missing docstring in public method
   --> src\gzkit\pipeline_runtime.py:602:9
    |
601 |     @property
602 |     def is_finished(self) -> bool:
    |         ^^^^^^^^^^^
603 |         terminal = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS, TaskStatus.BLOCKED}
604 |         return all(r.status in terminal for r in self.records)
    |

Found 3 errors.
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
## 2026-03-21T14:33:53-05:00
- Status: PASS
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.38s) — exit 0 == 0
  - [PASS] `uvx ruff check src/gzkit --select D` => rc=0 (0.06s) — exit 0 == 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                        |     Total |     Miss |     Cover |     Cover% |
|-----------------------------|-----------|----------|-----------|------------|
| __init__.py                 |         1 |        0 |         1 |       100% |
| cli.py                      |       139 |       11 |       128 |        92% |
| config.py                   |         8 |        0 |         8 |       100% |
| decomposition.py            |        13 |        2 |        11 |        85% |
| events.py                   |        37 |       11 |        26 |        70% |
| git_sync.py                 |         8 |        0 |         8 |       100% |
| instruction_audit.py        |         6 |        0 |         6 |       100% |
| instruction_eval.py         |        17 |       10 |         7 |        41% |
| interview.py                |        11 |        0 |        11 |       100% |
| ledger.py                   |        68 |        5 |        63 |        93% |
| lifecycle.py                |        11 |        0 |        11 |       100% |
| pipeline_runtime.py         |        85 |        2 |        83 |        98% |
| quality.py                  |        17 |        0 |        17 |       100% |
| registry.py                 |        10 |        0 |        10 |       100% |
| roles.py                    |        14 |        0 |        14 |       100% |
| rules.py                    |        21 |        0 |        21 |       100% |
| skills.py                   |        33 |        0 |        33 |       100% |
| superbook.py                |        15 |        1 |        14 |        93% |
| superbook_models.py         |        10 |        0 |        10 |       100% |
| superbook_parser.py         |         8 |        0 |         8 |       100% |
| sync.py                     |        52 |        0 |        52 |       100% |
| utils.py                    |         7 |        0 |         7 |       100% |
| validate.py                 |        23 |        7 |        16 |        70% |
| commands\__init__.py        |         1 |        0 |         1 |       100% |
| commands\attest.py          |         4 |        0 |         4 |       100% |
| commands\chores.py          |        20 |        0 |        20 |       100% |
| commands\common.py          |        31 |        2 |        29 |        94% |
| commands\plan.py            |         2 |        0 |         2 |       100% |
| commands\roles.py           |         4 |        0 |         4 |       100% |
| commands\state.py           |         2 |        0 |         2 |       100% |
| commands\status.py          |        45 |       16 |        29 |        64% |
| commands\superbook.py       |         2 |        0 |         2 |       100% |
| hooks\__init__.py           |         1 |        0 |         1 |       100% |
| hooks\claude.py             |        15 |        0 |        15 |       100% |
| hooks\copilot.py            |         4 |        0 |         4 |       100% |
| hooks\core.py               |        13 |        4 |         9 |        69% |
| hooks\guards.py             |         5 |        0 |         5 |       100% |
| hooks\obpi.py               |        18 |        0 |        18 |       100% |
| models\__init__.py          |         1 |        0 |         1 |       100% |
| models\frontmatter.py       |         9 |        0 |         9 |       100% |
| schemas\__init__.py         |         3 |        0 |         3 |       100% |
| templates\__init__.py       |         7 |        1 |         6 |        86% |
|-----------------------------|-----------|----------|-----------|------------|
| TOTAL                       |       801 |       72 |       729 |      91.0% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 91.0%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
All checks passed!
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
## 2026-04-02T19:18:07-05:00
- Status: PASS
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.21s) -- exit 0 == 0
  - [PASS] `uvx ruff check src/gzkit --select D` => rc=0 (0.03s) -- exit 0 == 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
=========== Coverage for /Users/jeff/Documents/Code/gzkit/src/gzkit/ ===========
----------------------------------- Summary ------------------------------------
| Name                                 |   Total |   Miss |   Cover |   Cover% |
|--------------------------------------|---------|--------|---------|----------|
| __init__.py                          |       1 |      0 |       1 |     100% |
| adr_eval.py                          |      13 |      2 |      11 |      85% |
| adr_eval_redteam.py                  |       4 |      0 |       4 |     100% |
| adr_eval_scoring.py                  |      17 |     14 |       3 |      18% |
| config.py                            |       9 |      0 |       9 |     100% |
| decomposition.py                     |       1 |      0 |       1 |     100% |
| events.py                            |      42 |     11 |      31 |      74% |
| git_sync.py                          |       8 |      0 |       8 |     100% |
| instruction_audit.py                 |       6 |      0 |       6 |     100% |
| instruction_eval.py                  |      17 |     10 |       7 |      41% |
| interview.py                         |      11 |      0 |      11 |     100% |
| ledger.py                            |      32 |      6 |      26 |      81% |
| ledger_events.py                     |      17 |      0 |      17 |     100% |
| ledger_proof.py                      |       5 |      0 |       5 |     100% |
| ledger_semantics.py                  |      22 |      0 |      22 |     100% |
| lifecycle.py                         |       5 |      0 |       5 |     100% |
| personas.py                          |       3 |      0 |       3 |     100% |
| pipeline_dispatch.py                 |      26 |      0 |      26 |     100% |
| pipeline_markers.py                  |      31 |      0 |      31 |     100% |
| pipeline_runtime.py                  |      14 |      0 |      14 |     100% |
| pipeline_verification.py             |      19 |      2 |      17 |      89% |
| quality.py                           |      33 |      0 |      33 |     100% |
| registry.py                          |      10 |      0 |      10 |     100% |
| roles.py                             |      14 |      0 |      14 |     100% |
| rules.py                             |      21 |      0 |      21 |     100% |
| skills.py                            |      14 |      0 |      14 |     100% |
| skills_audit.py                      |      19 |      0 |      19 |     100% |
| skills_mirror.py                     |       3 |      0 |       3 |     100% |
| sync.py                              |       7 |      0 |       7 |     100% |
| sync_skill_validation.py             |      16 |      0 |      16 |     100% |
| sync_skills.py                       |      16 |      0 |      16 |     100% |
| sync_skills_validation.py            |      14 |      0 |      14 |     100% |
| sync_surfaces.py                     |      16 |      0 |      16 |     100% |
| tasks.py                             |      11 |      0 |      11 |     100% |
| traceability.py                      |      21 |      1 |      20 |      95% |
| triangle.py                          |      22 |      1 |      21 |      95% |
| utils.py                             |       7 |      0 |       7 |     100% |
| validate.py                          |       3 |      0 |       3 |     100% |
| adapters/__init__.py                 |       1 |      0 |       1 |     100% |
| adapters/config.py                   |       5 |      0 |       5 |     100% |
| cli/__init__.py                      |       1 |      0 |       1 |     100% |
| cli/formatters.py                    |      25 |      0 |      25 |     100% |
| cli/logging.py                       |       5 |      0 |       5 |     100% |
| cli/main.py                          |       7 |      0 |       7 |     100% |
| cli/parser.py                        |       7 |      2 |       5 |      71% |
| cli/parser_artifacts.py              |       6 |      0 |       6 |     100% |
| cli/parser_governance.py             |       4 |      0 |       4 |     100% |
| cli/parser_maintenance.py            |       9 |      0 |       9 |     100% |
| cli/progress.py                      |       6 |      0 |       6 |     100% |
| cli/helpers/__init__.py              |       1 |      0 |       1 |     100% |
| cli/helpers/common_flags.py          |       2 |      0 |       2 |     100% |
| cli/helpers/epilog.py                |       2 |      0 |       2 |     100% |
| cli/helpers/exit_codes.py            |       2 |      0 |       2 |     100% |
| cli/helpers/standard_options.py      |       7 |      0 |       7 |     100% |
| commands/__init__.py                 |       1 |      0 |       1 |     100% |
| commands/adr_audit.py                |      10 |      0 |      10 |     100% |
| commands/adr_coverage.py             |      11 |      0 |      11 |     100% |
| commands/adr_promote.py              |       9 |      0 |       9 |     100% |
| commands/adr_promote_utils.py        |      18 |      0 |      18 |     100% |
| commands/attest.py                   |       5 |      0 |       5 |     100% |
| commands/audit_cmd.py                |       9 |      0 |       9 |     100% |
| commands/ceremony_steps.py           |      14 |      0 |      14 |     100% |
| commands/chores.py                   |      13 |      0 |      13 |     100% |
| commands/chores_exec.py              |       8 |      0 |       8 |     100% |
| commands/cli_audit.py                |       7 |      0 |       7 |     100% |
| commands/closeout.py                 |      16 |      9 |       7 |      44% |
| commands/closeout_ceremony.py        |      23 |      6 |      17 |      74% |
| commands/closeout_form.py            |      14 |      1 |      13 |      93% |
| commands/common.py                   |      28 |      1 |      27 |      96% |
| commands/config_paths.py             |      10 |      0 |      10 |     100% |
| commands/covers.py                   |       6 |      0 |       6 |     100% |
| commands/drift.py                    |       6 |      0 |       6 |     100% |
| commands/flags.py                    |       5 |      0 |       5 |     100% |
| commands/gates.py                    |      11 |      7 |       4 |      36% |
| commands/init_cmd.py                 |       6 |      0 |       6 |     100% |
| commands/interview_cmd.py            |       4 |      0 |       4 |     100% |
| commands/obpi_audit_cmd.py           |      17 |      0 |      17 |     100% |
| commands/obpi_cmd.py                 |       7 |      0 |       7 |     100% |
| commands/obpi_lock_cmd.py            |       8 |      0 |       8 |     100% |
| commands/obpi_stages.py              |       8 |      0 |       8 |     100% |
| commands/parity.py                   |       3 |      0 |       3 |     100% |
| commands/personas.py                 |       2 |      0 |       2 |     100% |
| commands/pipeline.py                 |       9 |      0 |       9 |     100% |
| commands/plan.py                     |       2 |      0 |       2 |     100% |
| commands/plan_audit_cmd.py           |      10 |      0 |      10 |     100% |
| commands/preflight.py                |       5 |      0 |       5 |     100% |
| commands/quality.py                  |       9 |      1 |       8 |      89% |
| commands/readiness.py                |      11 |      0 |      11 |     100% |
| commands/register.py                 |       9 |      0 |       9 |     100% |
| commands/roles.py                    |       4 |      0 |       4 |     100% |
| commands/skills_cmd.py               |       9 |      0 |       9 |     100% |
| commands/specify_cmd.py              |      36 |      0 |      36 |     100% |
| commands/state.py                    |       7 |      0 |       7 |     100% |
| commands/status.py                   |      12 |      0 |      12 |     100% |
| commands/status_obpi.py              |      15 |      4 |      11 |      73% |
| commands/status_obpi_inspect.py      |      14 |     10 |       4 |      29% |
| commands/status_render.py            |      12 |      2 |      10 |      83% |
| commands/sync.py                     |      11 |      0 |      11 |     100% |
| commands/task.py                     |      10 |      0 |      10 |     100% |
| commands/tidy.py                     |       6 |      0 |       6 |     100% |
| commands/validate_cmd.py             |       6 |      0 |       6 |     100% |
| commands/version_sync.py             |       7 |      0 |       7 |     100% |
| core/__init__.py                     |       1 |      0 |       1 |     100% |
| core/exceptions.py                   |      15 |      0 |      15 |     100% |
| core/lifecycle.py                    |       7 |      0 |       7 |     100% |
| core/models.py                       |      24 |      0 |      24 |     100% |
| core/scoring.py                      |      15 |      2 |      13 |      87% |
| core/validation_rules.py             |       5 |      0 |       5 |     100% |
| doc_coverage/__init__.py             |       1 |      0 |       1 |     100% |
| doc_coverage/manifest.py             |       7 |      0 |       7 |     100% |
| doc_coverage/models.py               |       8 |      0 |       8 |     100% |
| doc_coverage/runner.py               |       4 |      0 |       4 |     100% |
| doc_coverage/scanner.py              |      22 |      1 |      21 |      95% |
| eval/__init__.py                     |       1 |      0 |       1 |     100% |
| eval/datasets.py                     |       9 |      0 |       9 |     100% |
| eval/delta.py                        |      11 |      0 |      11 |     100% |
| eval/regression.py                   |      12 |      0 |      12 |     100% |
| eval/runner.py                       |       6 |      0 |       6 |     100% |
| eval/scorer.py                       |      13 |      1 |      12 |      92% |
| flags/__init__.py                    |       1 |      0 |       1 |     100% |
| flags/decisions.py                   |       6 |      0 |       6 |     100% |
| flags/diagnostics.py                 |       6 |      0 |       6 |     100% |
| flags/models.py                      |       9 |      0 |       9 |     100% |
| flags/registry.py                    |       3 |      0 |       3 |     100% |
| flags/service.py                     |      13 |      0 |      13 |     100% |
| hooks/__init__.py                    |       1 |      0 |       1 |     100% |
| hooks/claude.py                      |       5 |      0 |       5 |     100% |
| hooks/copilot.py                     |       4 |      0 |       4 |     100% |
| hooks/core.py                        |      13 |      4 |       9 |      69% |
| hooks/guards.py                      |       5 |      0 |       5 |     100% |
| hooks/obpi.py                        |      27 |      0 |      27 |     100% |
| hooks/scripts/__init__.py            |       1 |      0 |       1 |     100% |
| hooks/scripts/pipeline.py            |       4 |      0 |       4 |     100% |
| hooks/scripts/quality.py             |       2 |      0 |       2 |     100% |
| hooks/scripts/routing.py             |       4 |      0 |       4 |     100% |
| hooks/scripts/validation.py          |       4 |      0 |       4 |     100% |
| models/__init__.py                   |       1 |      0 |       1 |     100% |
| models/frontmatter.py                |       1 |      0 |       1 |     100% |
| models/persona.py                    |       6 |      0 |       6 |     100% |
| ports/__init__.py                    |       1 |      0 |       1 |     100% |
| ports/interfaces.py                  |      14 |      0 |      14 |     100% |
| reporter/__init__.py                 |       1 |      0 |       1 |     100% |
| reporter/panels.py                   |       2 |      0 |       2 |     100% |
| reporter/presets.py                  |       7 |      0 |       7 |     100% |
| schemas/__init__.py                  |       3 |      0 |       3 |     100% |
| templates/__init__.py                |       7 |      1 |       6 |      86% |
| validate_pkg/__init__.py             |       1 |      0 |       1 |     100% |
| validate_pkg/document.py             |       5 |      0 |       5 |     100% |
| validate_pkg/ledger_check.py         |      10 |      7 |       3 |      30% |
| validate_pkg/manifest.py             |       2 |      0 |       2 |     100% |
| validate_pkg/surface.py              |       4 |      0 |       4 |     100% |
|--------------------------------------|---------|--------|---------|----------|
| TOTAL                                |    1457 |    106 |    1351 |    92.7% |
---------------- RESULT: PASSED (minimum: 85.0%, actual: 92.7%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
All checks passed!
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
