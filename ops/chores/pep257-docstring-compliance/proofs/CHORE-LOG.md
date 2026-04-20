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
## 2026-04-19T19:55:12-05:00
- Status: FAIL
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (1.37s) -- exit 0 == 0
  - [FAIL] `uvx ruff check src/gzkit --select D` => rc=1 (0.08s) -- exit 1 != 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                                    |  Total |  Miss |  Cover |  Cover% |
|-----------------------------------------|--------|-------|--------|---------|
| __init__.py                             |      1 |     0 |      1 |    100% |
| adr_eval.py                             |     13 |     2 |     11 |     85% |
| adr_eval_redteam.py                     |      4 |     0 |      4 |    100% |
| adr_eval_scoring.py                     |     17 |    14 |      3 |     18% |
| config.py                               |     10 |     0 |     10 |    100% |
| decomposition.py                        |      1 |     0 |      1 |    100% |
| events.py                               |     43 |    11 |     32 |     74% |
| git_sync.py                             |      8 |     0 |      8 |    100% |
| handoff_validation.py                   |     13 |     3 |     10 |     77% |
| instruction_audit.py                    |      6 |     0 |      6 |    100% |
| instruction_eval.py                     |     17 |    10 |      7 |     41% |
| interview.py                            |     11 |     0 |     11 |    100% |
| ledger.py                               |     35 |     6 |     29 |     83% |
| ledger_events.py                        |     20 |     0 |     20 |    100% |
| ledger_proof.py                         |      5 |     0 |      5 |    100% |
| ledger_semantics.py                     |     22 |     0 |     22 |    100% |
| lifecycle.py                            |      5 |     0 |      5 |    100% |
| lock_manager.py                         |     14 |     0 |     14 |    100% |
| personas.py                             |     18 |     0 |     18 |    100% |
| pipeline_dispatch.py                    |     26 |     0 |     26 |    100% |
| pipeline_markers.py                     |     35 |     0 |     35 |    100% |
| pipeline_runtime.py                     |     16 |     0 |     16 |    100% |
| pipeline_verification.py                |     19 |     2 |     17 |     89% |
| quality.py                              |     41 |     0 |     41 |    100% |
| registry.py                             |     10 |     0 |     10 |    100% |
| roles.py                                |     14 |     0 |     14 |    100% |
| rules.py                                |     21 |     0 |     21 |    100% |
| skills.py                               |     15 |     0 |     15 |    100% |
| skills_audit.py                         |     20 |     0 |     20 |    100% |
| skills_mirror.py                        |      7 |     0 |      7 |    100% |
| sync.py                                 |      7 |     0 |      7 |    100% |
| sync_skill_validation.py                |     16 |     0 |     16 |    100% |
| sync_skills.py                          |     17 |     0 |     17 |    100% |
| sync_skills_validation.py               |     14 |     0 |     14 |    100% |
| sync_surfaces.py                        |     17 |     0 |     17 |    100% |
| tasks.py                                |     12 |     0 |     12 |    100% |
| temporal_drift.py                       |     14 |     0 |     14 |    100% |
| traceability.py                         |     28 |     4 |     24 |     86% |
| triangle.py                             |     22 |     1 |     21 |     95% |
| utils.py                                |      7 |     0 |      7 |    100% |
| validate.py                             |      3 |     0 |      3 |    100% |
| adapters\__init__.py                    |      1 |     0 |      1 |    100% |
| adapters\config.py                      |      5 |     0 |      5 |    100% |
| arb\__init__.py                         |      1 |     0 |      1 |    100% |
| arb\advisor.py                          |      7 |     3 |      4 |     57% |
| arb\paths.py                            |      2 |     0 |      2 |    100% |
| arb\patterns.py                         |      8 |     1 |      7 |     88% |
| arb\ruff_reporter.py                    |     12 |    10 |      2 |     17% |
| arb\step_reporter.py                    |      5 |     3 |      2 |     40% |
| arb\validator.py                        |      8 |     3 |      5 |     62% |
| cli\__init__.py                         |      2 |     1 |      1 |     50% |
| cli\formatters.py                       |     25 |     0 |     25 |    100% |
| cli\logging.py                          |      5 |     0 |      5 |    100% |
| cli\main.py                             |      8 |     1 |      7 |     88% |
| cli\parser.py                           |      7 |     2 |      5 |     71% |
| cli\parser_arb.py                       |     11 |     8 |      3 |     27% |
| cli\parser_artifacts.py                 |      7 |     1 |      6 |     86% |
| cli\parser_governance.py                |      5 |     1 |      4 |     80% |
| cli\parser_maintenance.py               |     11 |     1 |     10 |     91% |
| cli\progress.py                         |      6 |     0 |      6 |    100% |
| cli\helpers\__init__.py                 |      1 |     0 |      1 |    100% |
| cli\helpers\common_flags.py             |      2 |     0 |      2 |    100% |
| cli\helpers\epilog.py                   |      2 |     0 |      2 |    100% |
| cli\helpers\exit_codes.py               |      2 |     0 |      2 |    100% |
| cli\helpers\standard_options.py         |      7 |     0 |      7 |    100% |
| commands\__init__.py                    |      1 |     0 |      1 |    100% |
| commands\adr_audit.py                   |     10 |     0 |     10 |    100% |
| commands\adr_coverage.py                |     12 |     0 |     12 |    100% |
| commands\adr_promote.py                 |     11 |     0 |     11 |    100% |
| commands\adr_promote_utils.py           |     18 |     0 |     18 |    100% |
| commands\arb.py                         |      9 |     0 |      9 |    100% |
| commands\attest.py                      |      6 |     0 |      6 |    100% |
| commands\audit_cmd.py                   |      9 |     0 |      9 |    100% |
| commands\ceremony_data.py               |     18 |     2 |     16 |     89% |
| commands\ceremony_steps.py              |     12 |     0 |     12 |    100% |
| commands\chores.py                      |     16 |     0 |     16 |    100% |
| commands\chores_exec.py                 |      8 |     0 |      8 |    100% |
| commands\cli_audit.py                   |      7 |     0 |      7 |    100% |
| commands\closeout.py                    |     16 |     9 |      7 |     44% |
| commands\closeout_ceremony.py           |     25 |     6 |     19 |     76% |
| commands\closeout_form.py               |     14 |     1 |     13 |     93% |
| commands\common.py                      |     29 |     1 |     28 |     97% |
| commands\config_paths.py                |     10 |     0 |     10 |    100% |
| commands\covers.py                      |      6 |     0 |      6 |    100% |
| commands\drift.py                       |      6 |     0 |      6 |    100% |
| commands\flags.py                       |      5 |     0 |      5 |    100% |
| commands\frontmatter_reconcile.py       |      4 |     0 |      4 |    100% |
| commands\gates.py                       |     14 |     6 |      8 |     57% |
| commands\init_cmd.py                    |     13 |     0 |     13 |    100% |
| commands\interview_cmd.py               |      5 |     0 |      5 |    100% |
| commands\obpi_audit_cmd.py              |     20 |     0 |     20 |    100% |
| commands\obpi_cmd.py                    |      7 |     0 |      7 |    100% |
| commands\obpi_complete.py               |     22 |     0 |     22 |    100% |
| commands\obpi_lock.py                   |      6 |     0 |      6 |    100% |
| commands\obpi_lock_cmd.py               |      1 |     0 |      1 |    100% |
| commands\obpi_precomplete.py            |     11 |     0 |     11 |    100% |
| commands\obpi_stages.py                 |      8 |     0 |      8 |    100% |
| commands\parity.py                      |      3 |     0 |      3 |    100% |
| commands\patch_release.py               |     23 |     0 |     23 |    100% |
| commands\personas.py                    |      5 |     0 |      5 |    100% |
| commands\pipeline.py                    |      9 |     0 |      9 |    100% |
| commands\plan.py                        |      4 |     0 |      4 |    100% |
| commands\plan_audit_cmd.py              |     18 |     0 |     18 |    100% |
| commands\preflight.py                   |      5 |     0 |      5 |    100% |
| commands\quality.py                     |     14 |     1 |     13 |     93% |
| commands\readiness.py                   |     12 |     0 |     12 |    100% |
| commands\register.py                    |      9 |     0 |      9 |    100% |
| commands\roles.py                       |      4 |     0 |      4 |    100% |
| commands\skills_cmd.py                  |      9 |     0 |      9 |    100% |
| commands\specify_cmd.py                 |     37 |     0 |     37 |    100% |
| commands\state.py                       |      8 |     0 |      8 |    100% |
| commands\status.py                      |     12 |     0 |     12 |    100% |
| commands\status_obpi.py                 |     15 |     4 |     11 |     73% |
| commands\status_obpi_inspect.py         |     14 |    10 |      4 |     29% |
| commands\status_render.py               |     12 |     2 |     10 |     83% |
| commands\sync.py                        |     11 |     0 |     11 |    100% |
| commands\task.py                        |     10 |     0 |     10 |    100% |
| commands\tidy.py                        |      6 |     0 |      6 |    100% |
| commands\validate_cmd.py                |     17 |     0 |     17 |    100% |
| commands\validate_frontmatter.py        |     10 |     1 |      9 |     90% |
| commands\version_sync.py                |      9 |     0 |      9 |    100% |
| core\__init__.py                        |      1 |     0 |      1 |    100% |
| core\exceptions.py                      |     15 |     0 |     15 |    100% |
| core\lifecycle.py                       |      7 |     0 |      7 |    100% |
| core\models.py                          |     25 |     0 |     25 |    100% |
| core\scoring.py                         |     15 |     2 |     13 |     87% |
| core\validation_rules.py                |      5 |     0 |      5 |    100% |
| doc_coverage\__init__.py                |      1 |     0 |      1 |    100% |
| doc_coverage\manifest.py                |      7 |     0 |      7 |    100% |
| doc_coverage\models.py                  |      8 |     0 |      8 |    100% |
| doc_coverage\runner.py                  |      4 |     0 |      4 |    100% |
| doc_coverage\scanner.py                 |     23 |     1 |     22 |     96% |
| eval\__init__.py                        |      1 |     0 |      1 |    100% |
| eval\datasets.py                        |      9 |     0 |      9 |    100% |
| eval\delta.py                           |     11 |     0 |     11 |    100% |
| eval\regression.py                      |     12 |     0 |     12 |    100% |
| eval\runner.py                          |      6 |     0 |      6 |    100% |
| eval\scorer.py                          |     13 |     1 |     12 |     92% |
| flags\__init__.py                       |      1 |     0 |      1 |    100% |
| flags\decisions.py                      |      6 |     0 |      6 |    100% |
| flags\diagnostics.py                    |      6 |     0 |      6 |    100% |
| flags\models.py                         |      9 |     0 |      9 |    100% |
| flags\registry.py                       |      3 |     0 |      3 |    100% |
| flags\service.py                        |     13 |     0 |     13 |    100% |
| governance\__init__.py                  |      1 |     0 |      1 |    100% |
| governance\frontmatter_coherence.py     |     23 |     1 |     22 |     96% |
| governance\status_vocab.py              |      2 |     0 |      2 |    100% |
| governance\trust_audits.py              |     27 |     9 |     18 |     67% |
| hooks\__init__.py                       |      1 |     0 |      1 |    100% |
| hooks\claude.py                         |     10 |     0 |     10 |    100% |
| hooks\copilot.py                        |      4 |     0 |      4 |    100% |
| hooks\core.py                           |     13 |     4 |      9 |     69% |
| hooks\guards.py                         |      9 |     0 |      9 |    100% |
| hooks\obpi.py                           |     30 |     0 |     30 |    100% |
| hooks\scripts\__init__.py               |      1 |     0 |      1 |    100% |
| hooks\scripts\pipeline.py               |      4 |     0 |      4 |    100% |
| hooks\scripts\quality.py                |      2 |     0 |      2 |    100% |
| hooks\scripts\routing.py                |      4 |     0 |      4 |    100% |
| hooks\scripts\validation.py             |      4 |     0 |      4 |    100% |
| models\__init__.py                      |      1 |     0 |      1 |    100% |
| models\frontmatter.py                   |      1 |     0 |      1 |    100% |
| models\persona.py                       |      9 |     0 |      9 |    100% |
| ports\__init__.py                       |      1 |     0 |      1 |    100% |
| ports\interfaces.py                     |     14 |     0 |     14 |    100% |
| reporter\__init__.py                    |      1 |     0 |      1 |    100% |
| reporter\panels.py                      |      2 |     0 |      2 |    100% |
| reporter\presets.py                     |      7 |     0 |      7 |    100% |
| schemas\__init__.py                     |      3 |     0 |      3 |    100% |
| templates\__init__.py                   |      7 |     1 |      6 |     86% |
| validate_pkg\__init__.py                |      1 |     0 |      1 |    100% |
| validate_pkg\document.py                |      6 |     0 |      6 |    100% |
| validate_pkg\ledger_check.py            |     10 |     7 |      3 |     30% |
| validate_pkg\manifest.py                |      2 |     0 |      2 |    100% |
| validate_pkg\surface.py                 |      4 |     0 |      4 |    100% |
| validate_pkg\sync_parity.py             |     10 |     0 |     10 |    100% |
|-----------------------------------------|--------|-------|--------|---------|
| TOTAL                                   |   1844 |   157 |   1687 |   91.5% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 91.5%) ----------------
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stderr:
Installed 6 packages in 44ms
[uvx ruff check src/gzkit --select D] stdout:
D413 [*] Missing blank line after last section ("Raises")
  --> src\gzkit\arb\paths.py:35:5
   |
33 |         The resolved receipts directory (created if missing).
34 |
35 |     Raises:
   |     ^^^^^^
36 |         OSError: If the directory cannot be created.
37 |     """
   |
help: Add blank line after "Raises"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\arb\ruff_reporter.py:163:5
    |
161 |             blocking caller workflows (measurement-only mode).
162 |
163 |     Returns:
    |     ^^^^^^^
164 |         Tuple of (exit_status, receipt_path).
165 |     """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Raises")
  --> src\gzkit\arb\step_reporter.py:61:5
   |
59 |         Tuple of (exit_status, receipt_path).
60 |
61 |     Raises:
   |     ^^^^^^
62 |         ValueError: If name is empty or cmd is empty.
63 |     """
   |
help: Add blank line after "Raises"

D413 [*] Missing blank line after last section ("Returns")
  --> src\gzkit\arb\validator.py:91:5
   |
89 |         root: Override receipts directory (primarily for tests).
90 |
91 |     Returns:
   |     ^^^^^^^
92 |         Validation summary.
93 |     """
   |
help: Add blank line after "Returns"

D401 First line of docstring should be in imperative mood: "Handler for ``gz frontmatter reconcile``."
  --> src\gzkit\commands\frontmatter_reconcile.py:27:5
   |
26 |   def frontmatter_reconcile_cmd(*, dry_run: bool = False, as_json: bool = False) -> int:
27 | /     """Handler for ``gz frontmatter reconcile``.
28 | |
29 | |     Exit codes (per .claude/rules/cli.md):
30 | |       0 = success
31 | |       1 = user/config error (not a gzkit project)
32 | |       2 = system/IO error (ledger unreadable, write failure)
33 | |       3 = policy breach (UnmappedStatusBlocker)
34 | |
35 | |     Non-zero exit codes are propagated via ``SystemExit`` so ``gzkit.cli.main``
36 | |     terminates the process with the correct code — its else-branch swallows
37 | |     handler return values otherwise.
38 | |     """
   | |_______^
39 |       project_root = _resolve_project_root()
40 |       if project_root is None:
   |

D301 Use `r"""` if any backslashes in a docstring
   --> src\gzkit\commands\init_cmd.py:509:5
    |
508 |   def _canonicalize_prd_id(name: str) -> tuple[str, str]:
509 | /     """Normalize a user-supplied PRD name to the canonical ``PRD-<UPPER>-<semver>`` form.
510 | |
511 | |     The validator schema at ``src/gzkit/schemas/prd.json`` requires
512 | |     ``^PRD-[A-Z0-9]+-[0-9]+\\.[0-9]+\\.[0-9]+$``. This function guarantees the
513 | |     scaffolder and validator agree on the id format (GHI #186).
514 | |
515 | |     Returns ``(prd_id, semver)``.
516 | |     """
    | |_______^
517 |       stem = name[4:] if name.startswith("PRD-") else name
518 |       semver = "1.0.0"
    |
help: Add `r` prefix

D301 Use `r"""` if any backslashes in a docstring
   --> src\gzkit\commands\init_cmd.py:567:5
    |
566 |   def _canonicalize_constitution_id(name: str) -> tuple[str, str]:
567 | /     """Normalize a user-supplied constitution name to ``CONSTITUTION-<UPPER>-<semver>``.
568 | |
569 | |     The validator schema at ``src/gzkit/schemas/constitution.json`` requires
570 | |     ``^CONSTITUTION-[A-Z0-9]+-[0-9]+\\.[0-9]+\\.[0-9]+$``. This function guarantees
571 | |     the scaffolder and validator agree on id format (GHI #216 / GZKIT-BOOTSTRAP-008).
572 | |
573 | |     Returns ``(constitution_id, semver)``.
574 | |     """
    | |_______^
575 |       stem = name[len("CONSTITUTION-") :] if name.startswith("CONSTITUTION-") else name
576 |       semver = "1.0.0"
    |
help: Add `r` prefix

D401 First line of docstring should be in imperative mood: "Handler for ``gz obpi precomplete``."
  --> src\gzkit\commands\obpi_precomplete.py:51:5
   |
50 |   def obpi_precomplete_cmd(*, obpi_id: str, as_json: bool = False) -> int:
51 | /     """Handler for ``gz obpi precomplete``.
52 | |
53 | |     Exit codes (per .claude/rules/cli.md):
54 | |       0 = all preconditions met (safe to invoke gz obpi complete)
55 | |       1 = user/config error (brief not found, OBPI id invalid, etc.)
56 | |       3 = policy breach (one or more preconditions failed)
57 | |
58 | |     Non-zero exit codes are propagated via ``SystemExit`` so
59 | |     ``gzkit.cli.main`` terminates the process with the correct code — its
60 | |     else-branch swallows handler return values otherwise.
61 | |     """
   | |_______^
62 |       project_root = get_project_root()
   |

D401 First line of docstring should be in imperative mood: "A path is specific enough to yield useful collision signal."
   --> src\gzkit\commands\plan_audit_cmd.py:269:5
    |
268 |   def _is_specific_path(path: str) -> bool:
269 | /     """A path is specific enough to yield useful collision signal.
270 | |
271 | |     Root-level globs like ``src/``, ``tests/``, ``docs/``, or two-component
272 | |     paths like ``src/gzkit/`` are too broad -- every brief targets one of
273 | |     them. We only flag overlaps whose contested path descends at least three
274 | |     components deep.
275 | |     """
    | |_______^
276 |       parts = [p for p in path.rstrip("/").split("/") if p]
277 |       return len(parts) >= 3
    |

D202 [*] No blank lines allowed after function docstring (found 1)
  --> src\gzkit\commands\validate_cmd.py:36:5
   |
35 | def _validate_interviews(project_root: Path) -> list[ValidationError]:
36 |     """Check that ADRs with OBPIs have an interview transcript artifact."""
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
37 |
38 |     adr_root = project_root / "docs" / "design" / "adr"
   |
help: Remove blank line(s) after function docstring

D107 Missing docstring in `__init__`
  --> src\gzkit\governance\frontmatter_coherence.py:94:9
   |
92 |     """
93 |
94 |     def __init__(self, artifact: str, term: str) -> None:
   |         ^^^^^^^^
95 |         self.artifact = artifact
96 |         self.term = term
   |

D401 First line of docstring should be in imperative mood: "Main entry point: detect drift via the validator, rewrite to ledger-wins."
   --> src\gzkit\governance\frontmatter_coherence.py:248:5
    |
247 |   def reconcile_frontmatter(project_root: Path, *, dry_run: bool) -> ReconciliationReceipt:
248 | /     """Main entry point: detect drift via the validator, rewrite to ledger-wins.
249 | |
250 | |     Pre-flight: every file with drifted ``status:`` must have its current
251 | |     frontmatter term in STATUS_VOCAB_MAPPING. Unmapped → UnmappedStatusBlocker
252 | |     raised before any mutation.
253 | |
254 | |     Pool ADRs: skipped and noted in the receipt.
255 | |
256 | |     Ledger cursor: sampled once at entry (sha256 of ledger file bytes); never
257 | |     re-read mid-run. Mid-run ledger mutations do not leak into this receipt.
258 | |     """
    | |_______^
259 |       from gzkit.ledger import Ledger  # noqa: PLC0415
    |

D401 First line of docstring should be in imperative mood: "True when ``term`` is case-insensitively present as a key in STATUS_VOCAB_MAPPING."
   --> src\gzkit\governance\frontmatter_coherence.py:364:5
    |
363 | def _status_is_known(term: str) -> bool:
364 |     """True when ``term`` is case-insensitively present as a key in STATUS_VOCAB_MAPPING."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
365 |     if not term:
366 |         return False
    |

D413 [*] Missing blank line after last section ("Raises")
   --> src\gzkit\handoff_validation.py:140:5
    |
138 |         Parsed YAML as a dict.
139 |
140 |     Raises:
    |     ^^^^^^
141 |         HandoffValidationError: If frontmatter delimiters are missing or YAML is invalid.
142 |     """
    |
help: Add blank line after "Raises"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\handoff_validation.py:175:5
    |
173 |         content: Full Markdown document text.
174 |
175 |     Returns:
    |     ^^^^^^^
176 |         List of violation descriptions (empty = clean).
177 |     """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\handoff_validation.py:195:5
    |
193 |         content: Full Markdown document text.
194 |
195 |     Returns:
    |     ^^^^^^^
196 |         List of violation descriptions (empty = clean).
197 |     """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\handoff_validation.py:211:5
    |
209 |         content: Full Markdown document text.
210 |
211 |     Returns:
    |     ^^^^^^^
212 |         List of missing section names (empty = all present).
213 |     """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\handoff_validation.py:230:5
    |
228 |         base_path: Repository root to resolve relative paths against.
229 |
230 |     Returns:
    |     ^^^^^^^
231 |         List of nonexistent file paths (empty = all exist).
232 |     """
    |
help: Add blank line after "Returns"

D413 [*] Missing blank line after last section ("Returns")
   --> src\gzkit\handoff_validation.py:276:5
    |
274 |         base_path: Repository root for file reference checks.
275 |
276 |     Returns:
    |     ^^^^^^^
277 |         List of all violation messages (empty = valid).
278 |     """
    |
help: Add blank line after "Returns"

D301 Use `r"""` if any backslashes in a docstring
  --> src\gzkit\hooks\obpi.py:61:5
   |
60 |   def extract_gz_command_chains(content: str) -> list[list[str]]:
61 | /     """Extract every `gz <verb> [<verb>...]` chain from brief code segments.
62 | |
63 | |     Scans inline code (\\`...\\`) and fenced code blocks (\\`\\`\\`...\\`\\`\\`)
64 | |     only — prose mentions are ignored by design (brief authors quote
65 | |     prescriptive commands; prose references are descriptive). Used by
66 | |     ObpiValidator._validate_command_shapes to verify each chain resolves
67 | |     against the registered CLI parser tree (GHI #194).
68 | |     """
   | |_______^
69 |       chains: list[list[str]] = []
70 |       code_segments = _INLINE_CODE_PATTERN.findall(content) + _FENCED_BLOCK_PATTERN.findall(content)
   |
help: Add `r` prefix

D401 First line of docstring should be in imperative mood: "True if the line contains only ``@...`` tokens (whitespace-separated)."
   --> src\gzkit\traceability.py:380:5
    |
379 | def _is_tag_only_line(stripped: str) -> bool:
380 |     """True if the line contains only ``@...`` tokens (whitespace-separated)."""
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
381 |     tokens = stripped.split()
382 |     return all(token.startswith("@") for token in tokens)
    |

Found 21 errors.
[*] 11 fixable with the `--fix` option (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
## 2026-04-19T20:20:41-05:00
- Status: PASS
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.69s) -- exit 0 == 0
  - [PASS] `uvx ruff check src/gzkit --select D` => rc=0 (0.06s) -- exit 0 == 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                                    |  Total |  Miss |  Cover |  Cover% |
|-----------------------------------------|--------|-------|--------|---------|
| __init__.py                             |      1 |     0 |      1 |    100% |
| adr_eval.py                             |     13 |     2 |     11 |     85% |
| adr_eval_redteam.py                     |      4 |     0 |      4 |    100% |
| adr_eval_scoring.py                     |     17 |    14 |      3 |     18% |
| config.py                               |     10 |     0 |     10 |    100% |
| decomposition.py                        |      1 |     0 |      1 |    100% |
| events.py                               |     43 |    11 |     32 |     74% |
| git_sync.py                             |      8 |     0 |      8 |    100% |
| handoff_validation.py                   |     13 |     3 |     10 |     77% |
| instruction_audit.py                    |      6 |     0 |      6 |    100% |
| instruction_eval.py                     |     17 |    10 |      7 |     41% |
| interview.py                            |     11 |     0 |     11 |    100% |
| ledger.py                               |     35 |     6 |     29 |     83% |
| ledger_events.py                        |     20 |     0 |     20 |    100% |
| ledger_proof.py                         |      5 |     0 |      5 |    100% |
| ledger_semantics.py                     |     22 |     0 |     22 |    100% |
| lifecycle.py                            |      5 |     0 |      5 |    100% |
| lock_manager.py                         |     14 |     0 |     14 |    100% |
| personas.py                             |     18 |     0 |     18 |    100% |
| pipeline_dispatch.py                    |     26 |     0 |     26 |    100% |
| pipeline_markers.py                     |     35 |     0 |     35 |    100% |
| pipeline_runtime.py                     |     16 |     0 |     16 |    100% |
| pipeline_verification.py                |     19 |     2 |     17 |     89% |
| quality.py                              |     41 |     0 |     41 |    100% |
| registry.py                             |     10 |     0 |     10 |    100% |
| roles.py                                |     14 |     0 |     14 |    100% |
| rules.py                                |     21 |     0 |     21 |    100% |
| skills.py                               |     15 |     0 |     15 |    100% |
| skills_audit.py                         |     20 |     0 |     20 |    100% |
| skills_mirror.py                        |      7 |     0 |      7 |    100% |
| sync.py                                 |      7 |     0 |      7 |    100% |
| sync_skill_validation.py                |     16 |     0 |     16 |    100% |
| sync_skills.py                          |     17 |     0 |     17 |    100% |
| sync_skills_validation.py               |     14 |     0 |     14 |    100% |
| sync_surfaces.py                        |     17 |     0 |     17 |    100% |
| tasks.py                                |     12 |     0 |     12 |    100% |
| temporal_drift.py                       |     14 |     0 |     14 |    100% |
| traceability.py                         |     28 |     4 |     24 |     86% |
| triangle.py                             |     22 |     1 |     21 |     95% |
| utils.py                                |      7 |     0 |      7 |    100% |
| validate.py                             |      3 |     0 |      3 |    100% |
| adapters\__init__.py                    |      1 |     0 |      1 |    100% |
| adapters\config.py                      |      5 |     0 |      5 |    100% |
| arb\__init__.py                         |      1 |     0 |      1 |    100% |
| arb\advisor.py                          |      7 |     3 |      4 |     57% |
| arb\paths.py                            |      2 |     0 |      2 |    100% |
| arb\patterns.py                         |      8 |     1 |      7 |     88% |
| arb\ruff_reporter.py                    |     12 |    10 |      2 |     17% |
| arb\step_reporter.py                    |      5 |     3 |      2 |     40% |
| arb\validator.py                        |      8 |     3 |      5 |     62% |
| cli\__init__.py                         |      2 |     1 |      1 |     50% |
| cli\formatters.py                       |     25 |     0 |     25 |    100% |
| cli\logging.py                          |      5 |     0 |      5 |    100% |
| cli\main.py                             |      8 |     1 |      7 |     88% |
| cli\parser.py                           |      7 |     2 |      5 |     71% |
| cli\parser_arb.py                       |     11 |     8 |      3 |     27% |
| cli\parser_artifacts.py                 |      7 |     1 |      6 |     86% |
| cli\parser_governance.py                |      5 |     1 |      4 |     80% |
| cli\parser_maintenance.py               |     11 |     1 |     10 |     91% |
| cli\progress.py                         |      6 |     0 |      6 |    100% |
| cli\helpers\__init__.py                 |      1 |     0 |      1 |    100% |
| cli\helpers\common_flags.py             |      2 |     0 |      2 |    100% |
| cli\helpers\epilog.py                   |      2 |     0 |      2 |    100% |
| cli\helpers\exit_codes.py               |      2 |     0 |      2 |    100% |
| cli\helpers\standard_options.py         |      7 |     0 |      7 |    100% |
| commands\__init__.py                    |      1 |     0 |      1 |    100% |
| commands\adr_audit.py                   |     10 |     0 |     10 |    100% |
| commands\adr_coverage.py                |     12 |     0 |     12 |    100% |
| commands\adr_promote.py                 |     11 |     0 |     11 |    100% |
| commands\adr_promote_utils.py           |     18 |     0 |     18 |    100% |
| commands\arb.py                         |      9 |     0 |      9 |    100% |
| commands\attest.py                      |      6 |     0 |      6 |    100% |
| commands\audit_cmd.py                   |      9 |     0 |      9 |    100% |
| commands\ceremony_data.py               |     18 |     2 |     16 |     89% |
| commands\ceremony_steps.py              |     12 |     0 |     12 |    100% |
| commands\chores.py                      |     16 |     0 |     16 |    100% |
| commands\chores_exec.py                 |      8 |     0 |      8 |    100% |
| commands\cli_audit.py                   |      7 |     0 |      7 |    100% |
| commands\closeout.py                    |     16 |     9 |      7 |     44% |
| commands\closeout_ceremony.py           |     25 |     6 |     19 |     76% |
| commands\closeout_form.py               |     14 |     1 |     13 |     93% |
| commands\common.py                      |     29 |     1 |     28 |     97% |
| commands\config_paths.py                |     10 |     0 |     10 |    100% |
| commands\covers.py                      |      6 |     0 |      6 |    100% |
| commands\drift.py                       |      6 |     0 |      6 |    100% |
| commands\flags.py                       |      5 |     0 |      5 |    100% |
| commands\frontmatter_reconcile.py       |      4 |     0 |      4 |    100% |
| commands\gates.py                       |     14 |     6 |      8 |     57% |
| commands\init_cmd.py                    |     13 |     0 |     13 |    100% |
| commands\interview_cmd.py               |      5 |     0 |      5 |    100% |
| commands\obpi_audit_cmd.py              |     20 |     0 |     20 |    100% |
| commands\obpi_cmd.py                    |      7 |     0 |      7 |    100% |
| commands\obpi_complete.py               |     22 |     0 |     22 |    100% |
| commands\obpi_lock.py                   |      6 |     0 |      6 |    100% |
| commands\obpi_lock_cmd.py               |      1 |     0 |      1 |    100% |
| commands\obpi_precomplete.py            |     11 |     0 |     11 |    100% |
| commands\obpi_stages.py                 |      8 |     0 |      8 |    100% |
| commands\parity.py                      |      3 |     0 |      3 |    100% |
| commands\patch_release.py               |     23 |     0 |     23 |    100% |
| commands\personas.py                    |      5 |     0 |      5 |    100% |
| commands\pipeline.py                    |      9 |     0 |      9 |    100% |
| commands\plan.py                        |      4 |     0 |      4 |    100% |
| commands\plan_audit_cmd.py              |     18 |     0 |     18 |    100% |
| commands\preflight.py                   |      5 |     0 |      5 |    100% |
| commands\quality.py                     |     14 |     1 |     13 |     93% |
| commands\readiness.py                   |     12 |     0 |     12 |    100% |
| commands\register.py                    |      9 |     0 |      9 |    100% |
| commands\roles.py                       |      4 |     0 |      4 |    100% |
| commands\skills_cmd.py                  |      9 |     0 |      9 |    100% |
| commands\specify_cmd.py                 |     37 |     0 |     37 |    100% |
| commands\state.py                       |      8 |     0 |      8 |    100% |
| commands\status.py                      |     12 |     0 |     12 |    100% |
| commands\status_obpi.py                 |     15 |     4 |     11 |     73% |
| commands\status_obpi_inspect.py         |     14 |    10 |      4 |     29% |
| commands\status_render.py               |     12 |     2 |     10 |     83% |
| commands\sync.py                        |     11 |     0 |     11 |    100% |
| commands\task.py                        |     10 |     0 |     10 |    100% |
| commands\tidy.py                        |      6 |     0 |      6 |    100% |
| commands\validate_cmd.py                |     17 |     0 |     17 |    100% |
| commands\validate_frontmatter.py        |     10 |     1 |      9 |     90% |
| commands\version_sync.py                |      9 |     0 |      9 |    100% |
| core\__init__.py                        |      1 |     0 |      1 |    100% |
| core\exceptions.py                      |     15 |     0 |     15 |    100% |
| core\lifecycle.py                       |      7 |     0 |      7 |    100% |
| core\models.py                          |     25 |     0 |     25 |    100% |
| core\scoring.py                         |     15 |     2 |     13 |     87% |
| core\validation_rules.py                |      5 |     0 |      5 |    100% |
| doc_coverage\__init__.py                |      1 |     0 |      1 |    100% |
| doc_coverage\manifest.py                |      7 |     0 |      7 |    100% |
| doc_coverage\models.py                  |      8 |     0 |      8 |    100% |
| doc_coverage\runner.py                  |      4 |     0 |      4 |    100% |
| doc_coverage\scanner.py                 |     23 |     1 |     22 |     96% |
| eval\__init__.py                        |      1 |     0 |      1 |    100% |
| eval\datasets.py                        |      9 |     0 |      9 |    100% |
| eval\delta.py                           |     11 |     0 |     11 |    100% |
| eval\regression.py                      |     12 |     0 |     12 |    100% |
| eval\runner.py                          |      6 |     0 |      6 |    100% |
| eval\scorer.py                          |     13 |     1 |     12 |     92% |
| flags\__init__.py                       |      1 |     0 |      1 |    100% |
| flags\decisions.py                      |      6 |     0 |      6 |    100% |
| flags\diagnostics.py                    |      6 |     0 |      6 |    100% |
| flags\models.py                         |      9 |     0 |      9 |    100% |
| flags\registry.py                       |      3 |     0 |      3 |    100% |
| flags\service.py                        |     13 |     0 |     13 |    100% |
| governance\__init__.py                  |      1 |     0 |      1 |    100% |
| governance\frontmatter_coherence.py     |     23 |     0 |     23 |    100% |
| governance\status_vocab.py              |      2 |     0 |      2 |    100% |
| governance\trust_audits.py              |     27 |     9 |     18 |     67% |
| hooks\__init__.py                       |      1 |     0 |      1 |    100% |
| hooks\claude.py                         |     10 |     0 |     10 |    100% |
| hooks\copilot.py                        |      4 |     0 |      4 |    100% |
| hooks\core.py                           |     13 |     4 |      9 |     69% |
| hooks\guards.py                         |      9 |     0 |      9 |    100% |
| hooks\obpi.py                           |     30 |     0 |     30 |    100% |
| hooks\scripts\__init__.py               |      1 |     0 |      1 |    100% |
| hooks\scripts\pipeline.py               |      4 |     0 |      4 |    100% |
| hooks\scripts\quality.py                |      2 |     0 |      2 |    100% |
| hooks\scripts\routing.py                |      4 |     0 |      4 |    100% |
| hooks\scripts\validation.py             |      4 |     0 |      4 |    100% |
| models\__init__.py                      |      1 |     0 |      1 |    100% |
| models\frontmatter.py                   |      1 |     0 |      1 |    100% |
| models\persona.py                       |      9 |     0 |      9 |    100% |
| ports\__init__.py                       |      1 |     0 |      1 |    100% |
| ports\interfaces.py                     |     14 |     0 |     14 |    100% |
| reporter\__init__.py                    |      1 |     0 |      1 |    100% |
| reporter\panels.py                      |      2 |     0 |      2 |    100% |
| reporter\presets.py                     |      7 |     0 |      7 |    100% |
| schemas\__init__.py                     |      3 |     0 |      3 |    100% |
| templates\__init__.py                   |      7 |     1 |      6 |     86% |
| validate_pkg\__init__.py                |      1 |     0 |      1 |    100% |
| validate_pkg\document.py                |      6 |     0 |      6 |    100% |
| validate_pkg\ledger_check.py            |     10 |     7 |      3 |     30% |
| validate_pkg\manifest.py                |      2 |     0 |      2 |    100% |
| validate_pkg\surface.py                 |      4 |     0 |      4 |    100% |
| validate_pkg\sync_parity.py             |     10 |     0 |     10 |    100% |
|-----------------------------------------|--------|-------|--------|---------|
| TOTAL                                   |   1844 |   156 |   1688 |   91.5% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 91.5%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
All checks passed!
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
## 2026-04-19T21:07:23-05:00
- Status: PASS
- Chore: pep257-docstring-compliance
- Title: PEP 257 Docstring Compliance (Style + Coverage)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uvx interrogate -v -f 85 -c pyproject.toml src/gzkit` => rc=0 (0.63s) -- exit 0 == 0
  - [PASS] `uvx ruff check src/gzkit --select D` => rc=0 (0.06s) -- exit 0 == 0

```text
[uvx interrogate -v -f 85 -c pyproject.toml src/gzkit] stdout:
========= Coverage for C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\ =========
----------------------------------- Summary -----------------------------------
| Name                                    |  Total |  Miss |  Cover |  Cover% |
|-----------------------------------------|--------|-------|--------|---------|
| __init__.py                             |      1 |     0 |      1 |    100% |
| adr_eval.py                             |     13 |     2 |     11 |     85% |
| adr_eval_redteam.py                     |      4 |     0 |      4 |    100% |
| adr_eval_scoring.py                     |     17 |    14 |      3 |     18% |
| config.py                               |     10 |     0 |     10 |    100% |
| decomposition.py                        |      1 |     0 |      1 |    100% |
| events.py                               |     43 |    11 |     32 |     74% |
| git_sync.py                             |      8 |     0 |      8 |    100% |
| handoff_validation.py                   |     13 |     3 |     10 |     77% |
| instruction_audit.py                    |      6 |     0 |      6 |    100% |
| instruction_eval.py                     |     17 |    10 |      7 |     41% |
| interview.py                            |     11 |     0 |     11 |    100% |
| ledger.py                               |     35 |     6 |     29 |     83% |
| ledger_events.py                        |     20 |     0 |     20 |    100% |
| ledger_proof.py                         |      5 |     0 |      5 |    100% |
| ledger_semantics.py                     |     22 |     0 |     22 |    100% |
| lifecycle.py                            |      5 |     0 |      5 |    100% |
| lock_manager.py                         |     14 |     0 |     14 |    100% |
| personas.py                             |     18 |     0 |     18 |    100% |
| pipeline_dispatch.py                    |     26 |     0 |     26 |    100% |
| pipeline_markers.py                     |     35 |     0 |     35 |    100% |
| pipeline_runtime.py                     |     16 |     0 |     16 |    100% |
| pipeline_verification.py                |     19 |     2 |     17 |     89% |
| quality.py                              |     41 |     0 |     41 |    100% |
| registry.py                             |     10 |     0 |     10 |    100% |
| roles.py                                |     14 |     0 |     14 |    100% |
| rules.py                                |     21 |     0 |     21 |    100% |
| skills.py                               |     15 |     0 |     15 |    100% |
| skills_audit.py                         |     20 |     0 |     20 |    100% |
| skills_mirror.py                        |      7 |     0 |      7 |    100% |
| sync.py                                 |      7 |     0 |      7 |    100% |
| sync_skill_validation.py                |     16 |     0 |     16 |    100% |
| sync_skills.py                          |     17 |     0 |     17 |    100% |
| sync_skills_validation.py               |     14 |     0 |     14 |    100% |
| sync_surfaces.py                        |     17 |     0 |     17 |    100% |
| tasks.py                                |     12 |     0 |     12 |    100% |
| temporal_drift.py                       |     14 |     0 |     14 |    100% |
| traceability.py                         |     28 |     4 |     24 |     86% |
| triangle.py                             |     22 |     1 |     21 |     95% |
| utils.py                                |      7 |     0 |      7 |    100% |
| validate.py                             |      3 |     0 |      3 |    100% |
| adapters\__init__.py                    |      1 |     0 |      1 |    100% |
| adapters\config.py                      |      5 |     0 |      5 |    100% |
| arb\__init__.py                         |      1 |     0 |      1 |    100% |
| arb\advisor.py                          |      7 |     3 |      4 |     57% |
| arb\paths.py                            |      2 |     0 |      2 |    100% |
| arb\patterns.py                         |      8 |     1 |      7 |     88% |
| arb\ruff_reporter.py                    |     12 |    10 |      2 |     17% |
| arb\step_reporter.py                    |      5 |     3 |      2 |     40% |
| arb\validator.py                        |      8 |     3 |      5 |     62% |
| cli\__init__.py                         |      2 |     1 |      1 |     50% |
| cli\formatters.py                       |     25 |     0 |     25 |    100% |
| cli\logging.py                          |      5 |     0 |      5 |    100% |
| cli\main.py                             |      8 |     1 |      7 |     88% |
| cli\parser.py                           |      7 |     2 |      5 |     71% |
| cli\parser_arb.py                       |     11 |     8 |      3 |     27% |
| cli\parser_artifacts.py                 |      7 |     1 |      6 |     86% |
| cli\parser_governance.py                |      5 |     1 |      4 |     80% |
| cli\parser_maintenance.py               |     11 |     1 |     10 |     91% |
| cli\progress.py                         |      6 |     0 |      6 |    100% |
| cli\helpers\__init__.py                 |      1 |     0 |      1 |    100% |
| cli\helpers\common_flags.py             |      2 |     0 |      2 |    100% |
| cli\helpers\epilog.py                   |      2 |     0 |      2 |    100% |
| cli\helpers\exit_codes.py               |      2 |     0 |      2 |    100% |
| cli\helpers\standard_options.py         |      7 |     0 |      7 |    100% |
| commands\__init__.py                    |      1 |     0 |      1 |    100% |
| commands\adr_audit.py                   |     10 |     0 |     10 |    100% |
| commands\adr_coverage.py                |     12 |     0 |     12 |    100% |
| commands\adr_promote.py                 |     11 |     0 |     11 |    100% |
| commands\adr_promote_utils.py           |     18 |     0 |     18 |    100% |
| commands\arb.py                         |      9 |     0 |      9 |    100% |
| commands\attest.py                      |      6 |     0 |      6 |    100% |
| commands\audit_cmd.py                   |      9 |     0 |      9 |    100% |
| commands\ceremony_data.py               |     18 |     2 |     16 |     89% |
| commands\ceremony_steps.py              |     12 |     0 |     12 |    100% |
| commands\chores.py                      |     16 |     0 |     16 |    100% |
| commands\chores_exec.py                 |      8 |     0 |      8 |    100% |
| commands\cli_audit.py                   |      7 |     0 |      7 |    100% |
| commands\closeout.py                    |     16 |     9 |      7 |     44% |
| commands\closeout_ceremony.py           |     25 |     6 |     19 |     76% |
| commands\closeout_form.py               |     14 |     1 |     13 |     93% |
| commands\common.py                      |     29 |     1 |     28 |     97% |
| commands\config_paths.py                |     10 |     0 |     10 |    100% |
| commands\covers.py                      |      6 |     0 |      6 |    100% |
| commands\drift.py                       |      6 |     0 |      6 |    100% |
| commands\flags.py                       |      5 |     0 |      5 |    100% |
| commands\frontmatter_reconcile.py       |      4 |     0 |      4 |    100% |
| commands\gates.py                       |     14 |     6 |      8 |     57% |
| commands\init_cmd.py                    |     13 |     0 |     13 |    100% |
| commands\interview_cmd.py               |      5 |     0 |      5 |    100% |
| commands\obpi_audit_cmd.py              |     20 |     0 |     20 |    100% |
| commands\obpi_cmd.py                    |      7 |     0 |      7 |    100% |
| commands\obpi_complete.py               |     22 |     0 |     22 |    100% |
| commands\obpi_lock.py                   |      6 |     0 |      6 |    100% |
| commands\obpi_lock_cmd.py               |      1 |     0 |      1 |    100% |
| commands\obpi_precomplete.py            |     11 |     0 |     11 |    100% |
| commands\obpi_stages.py                 |      8 |     0 |      8 |    100% |
| commands\parity.py                      |      3 |     0 |      3 |    100% |
| commands\patch_release.py               |     23 |     0 |     23 |    100% |
| commands\personas.py                    |      5 |     0 |      5 |    100% |
| commands\pipeline.py                    |      9 |     0 |      9 |    100% |
| commands\plan.py                        |      8 |     0 |      8 |    100% |
| commands\plan_audit_cmd.py              |     18 |     0 |     18 |    100% |
| commands\preflight.py                   |      5 |     0 |      5 |    100% |
| commands\quality.py                     |     14 |     1 |     13 |     93% |
| commands\readiness.py                   |     12 |     0 |     12 |    100% |
| commands\register.py                    |      9 |     0 |      9 |    100% |
| commands\roles.py                       |      4 |     0 |      4 |    100% |
| commands\skills_cmd.py                  |      9 |     0 |      9 |    100% |
| commands\specify_cmd.py                 |     37 |     0 |     37 |    100% |
| commands\state.py                       |      8 |     0 |      8 |    100% |
| commands\status.py                      |     12 |     0 |     12 |    100% |
| commands\status_obpi.py                 |     15 |     4 |     11 |     73% |
| commands\status_obpi_inspect.py         |     14 |    10 |      4 |     29% |
| commands\status_render.py               |     12 |     2 |     10 |     83% |
| commands\sync.py                        |     11 |     0 |     11 |    100% |
| commands\task.py                        |     10 |     0 |     10 |    100% |
| commands\tidy.py                        |      6 |     0 |      6 |    100% |
| commands\validate_cmd.py                |     17 |     0 |     17 |    100% |
| commands\validate_frontmatter.py        |     10 |     1 |      9 |     90% |
| commands\version_sync.py                |      9 |     0 |      9 |    100% |
| core\__init__.py                        |      1 |     0 |      1 |    100% |
| core\exceptions.py                      |     15 |     0 |     15 |    100% |
| core\lifecycle.py                       |      7 |     0 |      7 |    100% |
| core\models.py                          |     25 |     0 |     25 |    100% |
| core\scoring.py                         |     15 |     2 |     13 |     87% |
| core\validation_rules.py                |      5 |     0 |      5 |    100% |
| doc_coverage\__init__.py                |      1 |     0 |      1 |    100% |
| doc_coverage\manifest.py                |      7 |     0 |      7 |    100% |
| doc_coverage\models.py                  |      8 |     0 |      8 |    100% |
| doc_coverage\runner.py                  |      4 |     0 |      4 |    100% |
| doc_coverage\scanner.py                 |     23 |     1 |     22 |     96% |
| eval\__init__.py                        |      1 |     0 |      1 |    100% |
| eval\datasets.py                        |      9 |     0 |      9 |    100% |
| eval\delta.py                           |     11 |     0 |     11 |    100% |
| eval\regression.py                      |     12 |     0 |     12 |    100% |
| eval\runner.py                          |      6 |     0 |      6 |    100% |
| eval\scorer.py                          |     13 |     1 |     12 |     92% |
| flags\__init__.py                       |      1 |     0 |      1 |    100% |
| flags\decisions.py                      |      6 |     0 |      6 |    100% |
| flags\diagnostics.py                    |      6 |     0 |      6 |    100% |
| flags\models.py                         |      9 |     0 |      9 |    100% |
| flags\registry.py                       |      3 |     0 |      3 |    100% |
| flags\service.py                        |     13 |     0 |     13 |    100% |
| governance\__init__.py                  |      1 |     0 |      1 |    100% |
| governance\frontmatter_coherence.py     |     23 |     0 |     23 |    100% |
| governance\status_vocab.py              |      2 |     0 |      2 |    100% |
| governance\trust_audits.py              |     27 |     9 |     18 |     67% |
| hooks\__init__.py                       |      1 |     0 |      1 |    100% |
| hooks\claude.py                         |     10 |     0 |     10 |    100% |
| hooks\copilot.py                        |      4 |     0 |      4 |    100% |
| hooks\core.py                           |     13 |     4 |      9 |     69% |
| hooks\guards.py                         |      9 |     0 |      9 |    100% |
| hooks\obpi.py                           |     30 |     0 |     30 |    100% |
| hooks\scripts\__init__.py               |      1 |     0 |      1 |    100% |
| hooks\scripts\pipeline.py               |      4 |     0 |      4 |    100% |
| hooks\scripts\quality.py                |      2 |     0 |      2 |    100% |
| hooks\scripts\routing.py                |      4 |     0 |      4 |    100% |
| hooks\scripts\validation.py             |      4 |     0 |      4 |    100% |
| models\__init__.py                      |      1 |     0 |      1 |    100% |
| models\frontmatter.py                   |      1 |     0 |      1 |    100% |
| models\persona.py                       |      9 |     0 |      9 |    100% |
| ports\__init__.py                       |      1 |     0 |      1 |    100% |
| ports\interfaces.py                     |     14 |     0 |     14 |    100% |
| reporter\__init__.py                    |      1 |     0 |      1 |    100% |
| reporter\panels.py                      |      2 |     0 |      2 |    100% |
| reporter\presets.py                     |      7 |     0 |      7 |    100% |
| schemas\__init__.py                     |      3 |     0 |      3 |    100% |
| templates\__init__.py                   |      7 |     1 |      6 |     86% |
| validate_pkg\__init__.py                |      1 |     0 |      1 |    100% |
| validate_pkg\document.py                |      6 |     0 |      6 |    100% |
| validate_pkg\ledger_check.py            |     10 |     7 |      3 |     30% |
| validate_pkg\manifest.py                |      2 |     0 |      2 |    100% |
| validate_pkg\surface.py                 |      4 |     0 |      4 |    100% |
| validate_pkg\sync_parity.py             |     10 |     0 |     10 |    100% |
|-----------------------------------------|--------|-------|--------|---------|
| TOTAL                                   |   1848 |   156 |   1692 |   91.6% |
--------------- RESULT: PASSED (minimum: 85.0%, actual: 91.6%) ----------------
[uvx ruff check src/gzkit --select D] stdout:
All checks passed!
[uvx ruff check src/gzkit --select D] stderr:
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible. Ignoring `incorrect-blank-line-before-class`.
warning: `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible. Ignoring `multi-line-summary-second-line`.
```
