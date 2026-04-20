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
## 2026-04-02T18:35:55-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (33.98s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (37.50s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.88s) -- exit 0 == 0

```text
[uv run -m unittest -q] stdout:
All frontmatter is aligned with ledger state. No changes.
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Completed  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Abandoned  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
{
  "passed": true,
  "commands_discovered": 68,
  "commands_checked": 68,
  "commands_with_gaps": 0,
  "gaps": [],
  "undeclared_commands": [],
  "orphaned_docs": []
}
Documentation Coverage Gap Report
========================================

PASSED: 68 commands discovered, 68 checked, all required surfaces present.
usage: gz flag [-h] [--quiet | --verbose] [--debug] {explain} ...

Single-flag inspection commands (explain).

positional arguments:
  {explain}
    explain      Show full metadata and resolved state for one flag

options:
  -h, --help     show this help message and exit
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flag explain ops.product_proof
    gz flag explain ops.product_proof --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz flags [-h] [--stale] [--json] [--quiet | --verbose] [--debug]

Display all registered feature flags with current values and sources.

options:
  -h, --help     show this help message and exit
  --stale        Show only stale flags (past review_by or remove_by dates)
  --json         Output as JSON
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flags
    gz flags --stale
    gz flags --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Unknown flag: 'bogus.key'

ops.product_proof
  Category:      ops
  Description:   Test flag.
  Owner:         test
  Default:       True
  Current value: True
  Source:        registry
  Review by:     2026-06-29 (88d)
  Linked ADR:    ADR-0.23.0
  Linked issue:  GHI-49

Unknown flag: 'nonexistent.key'
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
No stale flags.
                           Feature Flags (stale only)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key           ┃ Category ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ ops.stale_fl… │ ops      │ True    │ True  │ registry │ test  │ review:      │
│               │          │         │       │          │       │ -456d        │
└───────────────┴──────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Claimed: OBPI-0.1.0-01 (agent=unknown-64186, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-64186, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-64186, ttl=240m)
No lock found: OBPI-0.1.0-01
Released: OBPI-0.1.0-01
No active locks.
{
  "unlinked_specs": [],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 0,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 0
  },
  "scan_timestamp": "2026-04-02T23:35:16.292441+00:00"
}
{
  "unlinked_specs": [
    "REQ-0.1.0-01-01"
  ],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 1,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 1
  },
  "scan_timestamp": "2026-04-02T23:35:16.293146+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 33.737s

OK
[uv run coverage run -m unittest discover -s tests -t . -q] stdout:
All frontmatter is aligned with ledger state. No changes.
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Completed  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
                              State Repair Results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ OBPI          ┃ Old Status ┃ New Status ┃ File                               ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OBPI-0.1.0-01 │ Draft      │ Abandoned  │ docs/design/adr/ADR-0.1.0/obpis/O… │
└───────────────┴────────────┴────────────┴────────────────────────────────────┘

Repaired 1 frontmatter status field(s).
{
  "passed": true,
  "commands_discovered": 68,
  "commands_checked": 68,
  "commands_with_gaps": 0,
  "gaps": [],
  "undeclared_commands": [],
  "orphaned_docs": []
}
Documentation Coverage Gap Report
========================================

PASSED: 68 commands discovered, 68 checked, all required surfaces present.
usage: gz flag [-h] [--quiet | --verbose] [--debug] {explain} ...

Single-flag inspection commands (explain).

positional arguments:
  {explain}
    explain      Show full metadata and resolved state for one flag

options:
  -h, --help     show this help message and exit
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flag explain ops.product_proof
    gz flag explain ops.product_proof --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
usage: gz flags [-h] [--stale] [--json] [--quiet | --verbose] [--debug]

Display all registered feature flags with current values and sources.

options:
  -h, --help     show this help message and exit
  --stale        Show only stale flags (past review_by or remove_by dates)
  --json         Output as JSON
  --quiet, -q    Suppress non-error output
  --verbose, -v  Enable verbose output
  --debug        Enable debug mode with full tracebacks

Examples
    gz flags
    gz flags --stale
    gz flags --json

Exit codes
    0   Success
    1   User/config error
    2   System/IO error
    3   Policy breach
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Unknown flag: 'bogus.key'

ops.product_proof
  Category:      ops
  Description:   Test flag.
  Owner:         test
  Default:       True
  Current value: True
  Source:        registry
  Review by:     2026-06-29 (88d)
  Linked ADR:    ADR-0.23.0
  Linked issue:  GHI-49

Unknown flag: 'nonexistent.key'
                                 Feature Flags
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key          ┃ Category  ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ migration.c… │ migration │ False   │ False │ registry │ test  │ remove: 29d  │
│ ops.product… │ ops       │ True    │ True  │ registry │ test  │ review: 88d  │
│ release.dri… │ release   │ False   │ False │ registry │ test  │ remove: 28d  │
└──────────────┴───────────┴─────────┴───────┴──────────┴───────┴──────────────┘
No stale flags.
                           Feature Flags (stale only)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Key           ┃ Category ┃ Default ┃ Value ┃ Source   ┃ Owner ┃ Review/Remo… ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━┩
│ ops.stale_fl… │ ops      │ True    │ True  │ registry │ test  │ review:      │
│               │          │         │       │          │       │ -456d        │
└───────────────┴──────────┴─────────┴───────┴──────────┴───────┴──────────────┘
Claimed: OBPI-0.1.0-01 (agent=unknown-65446, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-65446, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-65446, ttl=240m)
No lock found: OBPI-0.1.0-01
Released: OBPI-0.1.0-01
No active locks.
{
  "unlinked_specs": [],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 0,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 0
  },
  "scan_timestamp": "2026-04-02T23:35:53.776788+00:00"
}
{
  "unlinked_specs": [
    "REQ-0.1.0-01-01"
  ],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 1,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 1
  },
  "scan_timestamp": "2026-04-02T23:35:53.777428+00:00"
}
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 37.124s

OK
[uv run coverage report --fail-under=40] stdout:
Name                                                    Stmts   Miss  Cover
---------------------------------------------------------------------------
src/gzkit/__init__.py                                       1      0   100%
src/gzkit/adapters/__init__.py                              0      0   100%
src/gzkit/adapters/config.py                               12      0   100%
src/gzkit/adr_eval.py                                     154     16    90%
src/gzkit/adr_eval_redteam.py                              43      4    91%
src/gzkit/adr_eval_scoring.py                             276     26    91%
src/gzkit/cli/__init__.py                                   7      0   100%
src/gzkit/cli/formatters.py                               173     14    92%
src/gzkit/cli/helpers/__init__.py                           4      0   100%
src/gzkit/cli/helpers/common_flags.py                      15      0   100%
src/gzkit/cli/helpers/epilog.py                            13      0   100%
src/gzkit/cli/helpers/exit_codes.py                        16      0   100%
src/gzkit/cli/helpers/standard_options.py                  23      0   100%
src/gzkit/cli/logging.py                                   45      1    98%
src/gzkit/cli/main.py                                      83      8    90%
src/gzkit/cli/parser.py                                    19      0   100%
src/gzkit/cli/parser_artifacts.py                         145      1    99%
src/gzkit/cli/parser_governance.py                        134      2    99%
src/gzkit/cli/parser_maintenance.py                       168      0   100%
src/gzkit/cli/progress.py                                  40      0   100%
src/gzkit/commands/__init__.py                              5      0   100%
src/gzkit/commands/adr_audit.py                           193     30    84%
src/gzkit/commands/adr_coverage.py                        186     42    77%
src/gzkit/commands/adr_promote.py                         165     43    74%
src/gzkit/commands/adr_promote_utils.py                   184     42    77%
src/gzkit/commands/attest.py                               90      2    98%
src/gzkit/commands/audit_cmd.py                           163      7    96%
src/gzkit/commands/ceremony_steps.py                       90     33    63%
src/gzkit/commands/chores.py                              191     61    68%
src/gzkit/commands/chores_exec.py                         181     57    69%
src/gzkit/commands/cli_audit.py                           128     32    75%
src/gzkit/commands/closeout.py                            262     31    88%
src/gzkit/commands/closeout_ceremony.py                   217     12    94%
src/gzkit/commands/closeout_form.py                       155     26    83%
src/gzkit/commands/common.py                              325     48    85%
src/gzkit/commands/config_paths.py                        148     16    89%
src/gzkit/commands/covers.py                               79      3    96%
src/gzkit/commands/drift.py                                83     10    88%
src/gzkit/commands/flags.py                                96      8    92%
src/gzkit/commands/gates.py                               140     73    48%
src/gzkit/commands/init_cmd.py                            144     42    71%
src/gzkit/commands/interview_cmd.py                        99     90     9%
src/gzkit/commands/obpi_audit_cmd.py                      177    154    13%
src/gzkit/commands/obpi_cmd.py                            215     53    75%
src/gzkit/commands/obpi_lock_cmd.py                        92     11    88%
src/gzkit/commands/obpi_stages.py                         128      9    93%
src/gzkit/commands/parity.py                               54     11    80%
src/gzkit/commands/personas.py                             38      1    97%
src/gzkit/commands/pipeline.py                             93      0   100%
src/gzkit/commands/plan.py                                 39     13    67%
src/gzkit/commands/plan_audit_cmd.py                      125      8    94%
src/gzkit/commands/preflight.py                            87     13    85%
src/gzkit/commands/quality.py                             127     71    44%
src/gzkit/commands/readiness.py                           139     34    76%
src/gzkit/commands/register.py                            173     16    91%
src/gzkit/commands/roles.py                                70     30    57%
src/gzkit/commands/skills_cmd.py                           74      4    95%
src/gzkit/commands/specify_cmd.py                         348     61    82%
src/gzkit/commands/state.py                               140      6    96%
src/gzkit/commands/status.py                              239     23    90%
src/gzkit/commands/status_obpi.py                         187     39    79%
src/gzkit/commands/status_obpi_inspect.py                 169     19    89%
src/gzkit/commands/status_render.py                       188     19    90%
src/gzkit/commands/sync.py                                202    116    43%
src/gzkit/commands/task.py                                132      7    95%
src/gzkit/commands/tidy.py                                 93     50    46%
src/gzkit/commands/validate_cmd.py                         88     13    85%
src/gzkit/commands/version_sync.py                         76      1    99%
src/gzkit/config.py                                        81      0   100%
src/gzkit/core/__init__.py                                  0      0   100%
src/gzkit/core/exceptions.py                               30      0   100%
src/gzkit/core/lifecycle.py                                36      0   100%
src/gzkit/core/models.py                                  123      3    98%
src/gzkit/core/scoring.py                                 195     29    85%
src/gzkit/core/validation_rules.py                         44      1    98%
src/gzkit/decomposition.py                                  2      0   100%
src/gzkit/doc_coverage/__init__.py                          5      0   100%
src/gzkit/doc_coverage/manifest.py                         33      1    97%
src/gzkit/doc_coverage/models.py                           43      0   100%
src/gzkit/doc_coverage/runner.py                           64     23    64%
src/gzkit/doc_coverage/scanner.py                         242     28    88%
src/gzkit/eval/__init__.py                                  0      0   100%
src/gzkit/eval/datasets.py                                 87     26    70%
src/gzkit/eval/delta.py                                    76      1    99%
src/gzkit/eval/regression.py                               97      3    97%
src/gzkit/eval/runner.py                                   47      0   100%
src/gzkit/eval/scorer.py                                  153      1    99%
src/gzkit/events.py                                       256     23    91%
src/gzkit/flags/__init__.py                                 6      0   100%
src/gzkit/flags/decisions.py                               17      0   100%
src/gzkit/flags/diagnostics.py                             75      1    99%
src/gzkit/flags/models.py                                  52      0   100%
src/gzkit/flags/registry.py                                47      2    96%
src/gzkit/flags/service.py                                 62      0   100%
src/gzkit/git_sync.py                                      93     19    80%
src/gzkit/hooks/__init__.py                                 3      0   100%
src/gzkit/hooks/claude.py                                  63      1    98%
src/gzkit/hooks/copilot.py                                 17      1    94%
src/gzkit/hooks/core.py                                   170     40    76%
src/gzkit/hooks/guards.py                                  60     47    22%
src/gzkit/hooks/obpi.py                                   310     38    88%
src/gzkit/hooks/scripts/__init__.py                         0      0   100%
src/gzkit/hooks/scripts/pipeline.py                         7      0   100%
src/gzkit/hooks/scripts/quality.py                          3      0   100%
src/gzkit/hooks/scripts/routing.py                          7      0   100%
src/gzkit/hooks/scripts/validation.py                       7      0   100%
src/gzkit/instruction_audit.py                            124     10    92%
src/gzkit/instruction_eval.py                             140     18    87%
src/gzkit/interview.py                                    119     29    76%
src/gzkit/ledger.py                                       289     14    95%
src/gzkit/ledger_events.py                                 61      1    98%
src/gzkit/ledger_proof.py                                  50      8    84%
src/gzkit/ledger_semantics.py                             208     19    91%
src/gzkit/lifecycle.py                                     21      0   100%
src/gzkit/models/__init__.py                                2      0   100%
src/gzkit/models/frontmatter.py                             2      0   100%
src/gzkit/models/persona.py                                55      2    96%
src/gzkit/personas.py                                      40      0   100%
src/gzkit/pipeline_dispatch.py                            222      2    99%
src/gzkit/pipeline_markers.py                             271     49    82%
src/gzkit/pipeline_runtime.py                             126      5    96%
src/gzkit/pipeline_verification.py                        145      1    99%
src/gzkit/ports/__init__.py                                 2      0   100%
src/gzkit/ports/interfaces.py                              15      0   100%
src/gzkit/quality.py                                      280     38    86%
src/gzkit/registry.py                                      57      0   100%
src/gzkit/reporter/__init__.py                              3      0   100%
src/gzkit/reporter/panels.py                               14      0   100%
src/gzkit/reporter/presets.py                              63      2    97%
src/gzkit/roles.py                                         79      1    99%
src/gzkit/rules.py                                        259     22    92%
src/gzkit/schemas/__init__.py                              12      0   100%
src/gzkit/skills.py                                       118     22    81%
src/gzkit/skills_audit.py                                 191     37    81%
src/gzkit/skills_mirror.py                                 51      1    98%
src/gzkit/sync.py                                         145      8    94%
src/gzkit/sync_skill_validation.py                        152     29    81%
src/gzkit/sync_skills.py                                  249     33    87%
src/gzkit/sync_surfaces.py                                160      9    94%
src/gzkit/tasks.py                                         66      0   100%
src/gzkit/templates/__init__.py                            28      2    93%
src/gzkit/traceability.py                                 184     18    90%
src/gzkit/triangle.py                                     164      5    97%
src/gzkit/utils.py                                         54      9    83%
src/gzkit/validate.py                                      40     22    45%
src/gzkit/validate_pkg/__init__.py                          0      0   100%
src/gzkit/validate_pkg/document.py                         70     25    64%
src/gzkit/validate_pkg/ledger_check.py                    132     30    77%
src/gzkit/validate_pkg/manifest.py                         36      8    78%
src/gzkit/validate_pkg/surface.py                          84     42    50%
tests/__init__.py                                           0      0   100%
tests/adr/__init__.py                                       0      0   100%
tests/adr/test_state_doctrine.py                          147      1    99%
tests/adr/test_storage_tiers.py                            45      2    96%
tests/commands/__init__.py                                  0      0   100%
tests/commands/common.py                                   69      4    94%
tests/commands/test_adr_promote.py                        100      0   100%
tests/commands/test_adr_resolution.py                      51      0   100%
tests/commands/test_attest.py                             134      0   100%
tests/commands/test_audit.py                              183      0   100%
tests/commands/test_chores.py                             138      0   100%
tests/commands/test_cli_audit.py                           55      0   100%
tests/commands/test_dry_run.py                             32      0   100%
tests/commands/test_gates.py                               14      0   100%
tests/commands/test_init.py                                44      0   100%
tests/commands/test_l3_gate_independence.py                83      0   100%
tests/commands/test_lint.py                                13      0   100%
tests/commands/test_migrate_semver.py                      45      0   100%
tests/commands/test_obpi_pipeline.py                      258      0   100%
tests/commands/test_obpi_validate_cmd.py                   88      0   100%
tests/commands/test_parsers.py                             10      0   100%
tests/commands/test_personas_cmd.py                        67      0   100%
tests/commands/test_pipeline_baseline_verification.py      29      0   100%
tests/commands/test_plan.py                                28      0   100%
tests/commands/test_prd.py                                 19      0   100%
tests/commands/test_preflight.py                           80      0   100%
tests/commands/test_register_adrs.py                      175      0   100%
tests/commands/test_runtime.py                            426      0   100%
tests/commands/test_skills.py                             130      0   100%
tests/commands/test_specify.py                             59      0   100%
tests/commands/test_status.py                             844      0   100%
tests/commands/test_sync_cmds.py                          106      1    99%
tests/commands/test_validate_cmds.py                       30      0   100%
tests/eval/__init__.py                                      0      0   100%
tests/eval/test_datasets.py                               106      1    99%
tests/eval/test_delta_gates.py                            186      1    99%
tests/eval/test_harness.py                                108      2    98%
tests/eval/test_regression.py                             208      1    99%
tests/fakes/__init__.py                                     5      0   100%
tests/fakes/config.py                                       7      0   100%
tests/fakes/filesystem.py                                  30      0   100%
tests/fakes/ledger.py                                       7      0   100%
tests/fakes/process.py                                     14      0   100%
tests/integration/__init__.py                               0      0   100%
tests/policy/__init__.py                                    0      0   100%
tests/policy/test_cli_consistency.py                      119     18    85%
tests/policy/test_env_usage.py                             97      4    96%
tests/policy/test_import_boundaries.py                    163     21    87%
tests/policy/test_naming_conventions.py                    61     10    84%
tests/test_adr_eval.py                                    149      1    99%
tests/test_adr_eval_redteam.py                             62      2    97%
tests/test_agent_sync.py                                  140      1    99%
tests/test_attest_deprecation.py                           66      1    98%
tests/test_audit_pipeline.py                              527      0   100%
tests/test_cli_parser.py                                  106      1    99%
tests/test_closeout_ceremony.py                           174      1    99%
tests/test_closeout_ceremony_cmd.py                       255      1    99%
tests/test_closeout_migration.py                          101      1    99%
tests/test_closeout_pipeline.py                           198      0   100%
tests/test_config.py                                      153      1    99%
tests/test_config_gates_removal.py                         56      2    96%
tests/test_config_paths.py                                 58      1    98%
tests/test_core_exceptions.py                              51      1    98%
tests/test_core_lifecycle.py                               56      1    98%
tests/test_core_models.py                                  35      1    97%
tests/test_core_scoring.py                                 43      1    98%
tests/test_core_validation.py                              40      1    98%
tests/test_decomposition.py                                36      1    97%
tests/test_doc_coverage.py                                454      3    99%
tests/test_epilog.py                                      111      8    93%
tests/test_fakes.py                                       311      1    99%
tests/test_feature_decisions.py                            65      1    98%
tests/test_flag_commands.py                                92      2    98%
tests/test_flag_diagnostics.py                            138      2    99%
tests/test_flag_models.py                                 114      1    99%
tests/test_flag_registry.py                               120      2    98%
tests/test_flag_service.py                                192      2    99%
tests/test_formatters.py                                  523      1    99%
tests/test_gates_deprecation.py                            59      1    98%
tests/test_help_text_completeness.py                       67     10    85%
tests/test_hooks.py                                       616      4    99%
tests/test_identity_surfaces.py                           153      1    99%
tests/test_instruction_audit.py                           250      0   100%
tests/test_instruction_eval.py                            127      1    99%
tests/test_interview.py                                    67      1    99%
tests/test_ledger.py                                      438      1    99%
tests/test_lifecycle.py                                   138      1    99%
tests/test_lifecycle_auto_fix.py                           65      1    98%
tests/test_lint_parents.py                                 50      1    98%
tests/test_load_config.py                                 101      1    99%
tests/test_logging.py                                     243      3    99%
tests/test_manifest_resolution.py                          43      1    98%
tests/test_manifest_v2.py                                  88      1    99%
tests/test_models.py                                      129      1    99%
tests/test_no_expired_flags.py                             19      4    79%
tests/test_obpi_lock_cmd.py                               203      1    99%
tests/test_obpi_template.py                                33      1    97%
tests/test_obpi_validator.py                              251      3    99%
tests/test_persona_composition.py                          78      2    97%
tests/test_persona_model.py                               107      1    99%
tests/test_persona_schema.py                              152      2    99%
tests/test_pipeline_dispatch.py                           511      1    99%
tests/test_pipeline_integration.py                        159      1    99%
tests/test_pipeline_runtime.py                            222      1    99%
tests/test_plan_audit_cmd.py                              176      1    99%
tests/test_ports.py                                       126      4    97%
tests/test_product_proof.py                               199      1    99%
tests/test_progress.py                                    131      1    99%
tests/test_pyinstaller_spec.py                             31      1    97%
tests/test_quality.py                                      65      1    98%
tests/test_registry.py                                    110      1    99%
tests/test_reporter.py                                    137      1    99%
tests/test_review_protocol.py                             333      1    99%
tests/test_reviewer_agent.py                              214      1    99%
tests/test_roles.py                                       146      1    99%
tests/test_roles_cli.py                                    81      1    99%
tests/test_rules.py                                       317      1    99%
tests/test_schemas.py                                     255     16    94%
tests/test_skill_naming.py                                 32      4    88%
tests/test_skills_audit.py                                293      1    99%
tests/test_sync.py                                        629      4    99%
tests/test_sync_surfaces.py                                36      1    97%
tests/test_tasks.py                                       512      4    99%
tests/test_templates.py                                   107      1    99%
tests/test_traceability.py                                548     27    95%
tests/test_triangle.py                                    576      1    99%
tests/test_validate.py                                    130      1    99%
tests/test_verification_dispatch.py                       341      1    99%
tests/test_version_sync.py                                 91      1    99%
tests/test_wbs_parser.py                                  110      1    99%
tests/unit/__init__.py                                      0      0   100%
tests/unit/test_common_flags.py                           132      1    99%
tests/unit/test_exception_hierarchy.py                     58      1    98%
tests/unit/test_exit_codes.py                              61      1    98%
tests/unit/test_progress_indication.py                     74      1    99%
tests/unit/test_runtime_presentation.py                   109      5    95%
tests/unit/test_standard_options.py                       137      1    99%
---------------------------------------------------------------------------
TOTAL                                                   35089   2614    93%
```
## 2026-04-19T19:50:02-05:00
- Status: FAIL
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (51.63s) -- exit 0 == 0
  - [FAIL] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=1 (62.10s) -- exit 1 != 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 50.795s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
======================================================================
FAIL: test_runtime_budget_under_one_second_on_real_repo (tests.commands.test_validate_frontmatter.TestFrontmatterGuard.test_runtime_budget_under_one_second_on_real_repo)
Real repo runtime < 1.0s (~80 ADRs / ~200 OBPIs scale).
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\Jeff\source\repos\va\gzkit\tests\commands\test_validate_frontmatter.py", line 271, in test_runtime_budget_under_one_second_on_real_repo
    self.assertLess(
    ~~~~~~~~~~~~~~~^
        elapsed,
        ^^^^^^^^
        1.0,
        ^^^^
        f"Frontmatter guard exceeded 1.0s budget (took {elapsed:.2f}s)",
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
AssertionError: 1.2268592000000353 not less than 1.0 : Frontmatter guard exceeded 1.0s budget (took 1.23s)

----------------------------------------------------------------------
Ran 3243 tests in 60.662s

FAILED (failures=1, skipped=1)
```
## 2026-04-19T20:29:18-05:00
- Status: FAIL
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (50.77s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (60.00s) -- exit 0 == 0
  - [FAIL] `uv run coverage report --fail-under=40` => rc=1 (0.44s) -- exit 1 != 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 49.947s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 58.666s

OK (skipped=2)
[uv run coverage report --fail-under=40] stdout:
No source for code: 'C:\Users\Jeff\AppData\Local\Temp\tmp0u12we0n\.claude\hooks\pipeline-completion-reminder.py'; see https://coverage.readthedocs.io/en/7.13.4/messages.html#error-no-source
```
## 2026-04-19T20:34:16-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (52.06s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (61.27s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (1.00s) -- exit 0 == 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 51.249s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 59.919s

OK (skipped=2)
[uv run coverage report --fail-under=40] stdout:
Name                                            Stmts   Miss  Cover
-------------------------------------------------------------------
src\gzkit\__init__.py                               1      0   100%
src\gzkit\adapters\__init__.py                      0      0   100%
src\gzkit\adapters\config.py                       12      0   100%
src\gzkit\adr_eval.py                             154     16    90%
src\gzkit\adr_eval_redteam.py                      43      4    91%
src\gzkit\adr_eval_scoring.py                     276     26    91%
src\gzkit\arb\__init__.py                           7      0   100%
src\gzkit\arb\advisor.py                          118     26    78%
src\gzkit\arb\paths.py                             15      0   100%
src\gzkit\arb\patterns.py                         103     10    90%
src\gzkit\arb\ruff_reporter.py                    114     17    85%
src\gzkit\arb\step_reporter.py                     53      9    83%
src\gzkit\arb\validator.py                        115     16    86%
src\gzkit\cli\__init__.py                          15      1    93%
src\gzkit\cli\formatters.py                       173     14    92%
src\gzkit\cli\helpers\__init__.py                   4      0   100%
src\gzkit\cli\helpers\common_flags.py              15      0   100%
src\gzkit\cli\helpers\epilog.py                    13      0   100%
src\gzkit\cli\helpers\exit_codes.py                16      0   100%
src\gzkit\cli\helpers\standard_options.py          23      0   100%
src\gzkit\cli\logging.py                           45      1    98%
src\gzkit\cli\main.py                              92      8    91%
src\gzkit\cli\parser.py                            19      0   100%
src\gzkit\cli\parser_arb.py                        59      3    95%
src\gzkit\cli\parser_artifacts.py                 192      1    99%
src\gzkit\cli\parser_governance.py                153      2    99%
src\gzkit\cli\parser_maintenance.py               208      0   100%
src\gzkit\cli\progress.py                          43      2    95%
src\gzkit\commands\__init__.py                      0      0   100%
src\gzkit\commands\adr_audit.py                   200     27    86%
src\gzkit\commands\adr_coverage.py                221     44    80%
src\gzkit\commands\adr_promote.py                 189     43    77%
src\gzkit\commands\adr_promote_utils.py           184     46    75%
src\gzkit\commands\arb.py                          64     20    69%
src\gzkit\commands\attest.py                      104      8    92%
src\gzkit\commands\audit_cmd.py                   163      7    96%
src\gzkit\commands\ceremony_data.py               224     19    92%
src\gzkit\commands\ceremony_steps.py              102     26    75%
src\gzkit\commands\chores.py                      213     63    70%
src\gzkit\commands\chores_exec.py                 183     57    69%
src\gzkit\commands\cli_audit.py                   133     18    86%
src\gzkit\commands\closeout.py                    262     31    88%
src\gzkit\commands\closeout_ceremony.py           245     15    94%
src\gzkit\commands\closeout_form.py               155     26    83%
src\gzkit\commands\common.py                      339     47    86%
src\gzkit\commands\config_paths.py                148     16    89%
src\gzkit\commands\covers.py                       80      3    96%
src\gzkit\commands\drift.py                        80     10    88%
src\gzkit\commands\flags.py                        96      8    92%
src\gzkit\commands\frontmatter_reconcile.py        49     25    49%
src\gzkit\commands\gates.py                       199     96    52%
src\gzkit\commands\init_cmd.py                    294     65    78%
src\gzkit\commands\interview_cmd.py               132    121     8%
src\gzkit\commands\obpi_audit_cmd.py              240    197    18%
src\gzkit\commands\obpi_cmd.py                    216     53    75%
src\gzkit\commands\obpi_complete.py               225     19    92%
src\gzkit\commands\obpi_lock.py                    80     11    86%
src\gzkit\commands\obpi_lock_cmd.py                 2      2     0%
src\gzkit\commands\obpi_precomplete.py            116      7    94%
src\gzkit\commands\obpi_stages.py                 135      9    93%
src\gzkit\commands\parity.py                       54     11    80%
src\gzkit\commands\patch_release.py               341    133    61%
src\gzkit\commands\personas.py                     74      7    91%
src\gzkit\commands\pipeline.py                     93      0   100%
src\gzkit\commands\plan.py                         85     23    73%
src\gzkit\commands\plan_audit_cmd.py              215     15    93%
src\gzkit\commands\preflight.py                    87     11    87%
src\gzkit\commands\quality.py                     224    161    28%
src\gzkit\commands\readiness.py                   150     33    78%
src\gzkit\commands\register.py                    191     17    91%
src\gzkit\commands\roles.py                        70     30    57%
src\gzkit\commands\skills_cmd.py                   85      4    95%
src\gzkit\commands\specify_cmd.py                 360     66    82%
src\gzkit\commands\state.py                       152      6    96%
src\gzkit\commands\status.py                      221     19    91%
src\gzkit\commands\status_obpi.py                 192     39    80%
src\gzkit\commands\status_obpi_inspect.py         169     19    89%
src\gzkit\commands\status_render.py               196     19    90%
src\gzkit\commands\sync.py                        203     99    51%
src\gzkit\commands\task.py                        132      7    95%
src\gzkit\commands\tidy.py                         89     38    57%
src\gzkit\commands\validate_cmd.py                207     35    83%
src\gzkit\commands\validate_frontmatter.py        151     16    89%
src\gzkit\commands\version_sync.py                103      2    98%
src\gzkit\config.py                                88      0   100%
src\gzkit\core\__init__.py                          0      0   100%
src\gzkit\core\exceptions.py                       30      0   100%
src\gzkit\core\lifecycle.py                        36      0   100%
src\gzkit\core\models.py                          130      3    98%
src\gzkit\core\scoring.py                         195     25    87%
src\gzkit\core\validation_rules.py                 46      0   100%
src\gzkit\decomposition.py                          2      0   100%
src\gzkit\doc_coverage\__init__.py                  5      0   100%
src\gzkit\doc_coverage\manifest.py                 33      1    97%
src\gzkit\doc_coverage\models.py                   43      0   100%
src\gzkit\doc_coverage\runner.py                   61      7    89%
src\gzkit\doc_coverage\scanner.py                 273     28    90%
src\gzkit\eval\__init__.py                          0      0   100%
src\gzkit\eval\datasets.py                         87     26    70%
src\gzkit\eval\delta.py                            76      1    99%
src\gzkit\eval\regression.py                       97      3    97%
src\gzkit\eval\runner.py                           47      0   100%
src\gzkit\eval\scorer.py                          153      1    99%
src\gzkit\events.py                               261     23    91%
src\gzkit\flags\__init__.py                         6      0   100%
src\gzkit\flags\decisions.py                       17      0   100%
src\gzkit\flags\diagnostics.py                     75      1    99%
src\gzkit\flags\models.py                          52      0   100%
src\gzkit\flags\registry.py                        47      2    96%
src\gzkit\flags\service.py                         62      0   100%
src\gzkit\git_sync.py                              93     11    88%
src\gzkit\governance\__init__.py                    0      0   100%
src\gzkit\governance\frontmatter_coherence.py     218     36    83%
src\gzkit\governance\status_vocab.py               14      0   100%
src\gzkit\governance\trust_audits.py              516     98    81%
src\gzkit\handoff_validation.py                   135      2    99%
src\gzkit\hooks\__init__.py                         3      0   100%
src\gzkit\hooks\claude.py                         119      6    95%
src\gzkit\hooks\copilot.py                         19      1    95%
src\gzkit\hooks\core.py                           173     42    76%
src\gzkit\hooks\guards.py                         117      5    96%
src\gzkit\hooks\obpi.py                           367     26    93%
src\gzkit\hooks\scripts\__init__.py                 0      0   100%
src\gzkit\hooks\scripts\pipeline.py                 4      0   100%
src\gzkit\hooks\scripts\quality.py                  2      0   100%
src\gzkit\hooks\scripts\routing.py                  4      0   100%
src\gzkit\hooks\scripts\validation.py               4      0   100%
src\gzkit\instruction_audit.py                    124      7    94%
src\gzkit\instruction_eval.py                     140     17    88%
src\gzkit\interview.py                            119     29    76%
src\gzkit\ledger.py                               338     15    96%
src\gzkit\ledger_events.py                         69      2    97%
src\gzkit\ledger_proof.py                          50      8    84%
src\gzkit\ledger_semantics.py                     208     19    91%
src\gzkit\lifecycle.py                             21      0   100%
src\gzkit\lock_manager.py                          97      2    98%
src\gzkit\models\__init__.py                        2      0   100%
src\gzkit\models\frontmatter.py                     2      0   100%
src\gzkit\models\persona.py                        76      2    97%
src\gzkit\personas.py                             233     26    89%
src\gzkit\pipeline_dispatch.py                    222      2    99%
src\gzkit\pipeline_markers.py                     335     45    87%
src\gzkit\pipeline_runtime.py                     138      5    96%
src\gzkit\pipeline_verification.py                145      1    99%
src\gzkit\ports\__init__.py                         2      0   100%
src\gzkit\ports\interfaces.py                      24      9    62%
src\gzkit\quality.py                              362     46    87%
src\gzkit\registry.py                              57      0   100%
src\gzkit\reporter\__init__.py                      3      0   100%
src\gzkit\reporter\panels.py                       14      0   100%
src\gzkit\reporter\presets.py                      63      1    98%
src\gzkit\roles.py                                 79      1    99%
src\gzkit\rules.py                                265     19    93%
src\gzkit\schemas\__init__.py                      12      0   100%
src\gzkit\skills.py                               132     23    83%
src\gzkit\skills_audit.py                         217     46    79%
src\gzkit\skills_mirror.py                         93      6    94%
src\gzkit\sync.py                                 145      7    95%
src\gzkit\sync_skill_validation.py                152     29    81%
src\gzkit\sync_skills.py                          272     36    87%
src\gzkit\sync_skills_validation.py               123    123     0%
src\gzkit\sync_surfaces.py                        190     12    94%
src\gzkit\tasks.py                                 79      2    97%
src\gzkit\templates\__init__.py                    28      2    93%
src\gzkit\temporal_drift.py                       132      9    93%
src\gzkit\traceability.py                         269     29    89%
src\gzkit\triangle.py                             164      5    97%
src\gzkit\utils.py                                 59     10    83%
src\gzkit\validate.py                              40     22    45%
src\gzkit\validate_pkg\__init__.py                  0      0   100%
src\gzkit\validate_pkg\document.py                 78     25    68%
src\gzkit\validate_pkg\ledger_check.py            132     30    77%
src\gzkit\validate_pkg\manifest.py                 36      8    78%
src\gzkit\validate_pkg\surface.py                  87     42    52%
src\gzkit\validate_pkg\sync_parity.py             128     32    75%
-------------------------------------------------------------------
TOTAL                                           20464   3207    84%
```
## 2026-04-19T21:02:06-05:00
- Status: PASS
- Chore: coverage-40pct
- Title: Coverage >=40% Baseline
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (53.69s) -- exit 0 == 0
  - [PASS] `uv run coverage run -m unittest discover -s tests -t . -q` => rc=0 (60.12s) -- exit 0 == 0
  - [PASS] `uv run coverage report --fail-under=40` => rc=0 (0.98s) -- exit 0 == 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 52.877s

OK (skipped=1)
[uv run coverage run -m unittest discover -s tests -t . -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 58.800s

OK (skipped=2)
[uv run coverage report --fail-under=40] stdout:
Name                                            Stmts   Miss  Cover
-------------------------------------------------------------------
src\gzkit\__init__.py                               1      0   100%
src\gzkit\adapters\__init__.py                      0      0   100%
src\gzkit\adapters\config.py                       12      0   100%
src\gzkit\adr_eval.py                             154     16    90%
src\gzkit\adr_eval_redteam.py                      43      4    91%
src\gzkit\adr_eval_scoring.py                     276     26    91%
src\gzkit\arb\__init__.py                           7      0   100%
src\gzkit\arb\advisor.py                          118     26    78%
src\gzkit\arb\paths.py                             15      0   100%
src\gzkit\arb\patterns.py                         103     10    90%
src\gzkit\arb\ruff_reporter.py                    114     17    85%
src\gzkit\arb\step_reporter.py                     53      9    83%
src\gzkit\arb\validator.py                        115     16    86%
src\gzkit\cli\__init__.py                          15      1    93%
src\gzkit\cli\formatters.py                       173     14    92%
src\gzkit\cli\helpers\__init__.py                   4      0   100%
src\gzkit\cli\helpers\common_flags.py              15      0   100%
src\gzkit\cli\helpers\epilog.py                    13      0   100%
src\gzkit\cli\helpers\exit_codes.py                16      0   100%
src\gzkit\cli\helpers\standard_options.py          23      0   100%
src\gzkit\cli\logging.py                           45      1    98%
src\gzkit\cli\main.py                              92      8    91%
src\gzkit\cli\parser.py                            19      0   100%
src\gzkit\cli\parser_arb.py                        60      3    95%
src\gzkit\cli\parser_artifacts.py                 192      1    99%
src\gzkit\cli\parser_governance.py                153      2    99%
src\gzkit\cli\parser_maintenance.py               208      0   100%
src\gzkit\cli\progress.py                          43      2    95%
src\gzkit\commands\__init__.py                      0      0   100%
src\gzkit\commands\adr_audit.py                   200     27    86%
src\gzkit\commands\adr_coverage.py                221     44    80%
src\gzkit\commands\adr_promote.py                 189     43    77%
src\gzkit\commands\adr_promote_utils.py           184     46    75%
src\gzkit\commands\arb.py                          64     20    69%
src\gzkit\commands\attest.py                      104      8    92%
src\gzkit\commands\audit_cmd.py                   163      7    96%
src\gzkit\commands\ceremony_data.py               224     19    92%
src\gzkit\commands\ceremony_steps.py              102     26    75%
src\gzkit\commands\chores.py                      213     63    70%
src\gzkit\commands\chores_exec.py                 183     57    69%
src\gzkit\commands\cli_audit.py                   133     33    75%
src\gzkit\commands\closeout.py                    262     31    88%
src\gzkit\commands\closeout_ceremony.py           245     15    94%
src\gzkit\commands\closeout_form.py               155     26    83%
src\gzkit\commands\common.py                      339     47    86%
src\gzkit\commands\config_paths.py                148     16    89%
src\gzkit\commands\covers.py                       80      3    96%
src\gzkit\commands\drift.py                        80     10    88%
src\gzkit\commands\flags.py                        96      8    92%
src\gzkit\commands\frontmatter_reconcile.py        49     25    49%
src\gzkit\commands\gates.py                       199     96    52%
src\gzkit\commands\init_cmd.py                    294     65    78%
src\gzkit\commands\interview_cmd.py               132    121     8%
src\gzkit\commands\obpi_audit_cmd.py              240    197    18%
src\gzkit\commands\obpi_cmd.py                    216     53    75%
src\gzkit\commands\obpi_complete.py               225     19    92%
src\gzkit\commands\obpi_lock.py                    80     11    86%
src\gzkit\commands\obpi_lock_cmd.py                 2      2     0%
src\gzkit\commands\obpi_precomplete.py            116      7    94%
src\gzkit\commands\obpi_stages.py                 135      9    93%
src\gzkit\commands\parity.py                       54     11    80%
src\gzkit\commands\patch_release.py               341    133    61%
src\gzkit\commands\personas.py                     74      7    91%
src\gzkit\commands\pipeline.py                     93      0   100%
src\gzkit\commands\plan.py                        103     30    71%
src\gzkit\commands\plan_audit_cmd.py              215     15    93%
src\gzkit\commands\preflight.py                    87     11    87%
src\gzkit\commands\quality.py                     224    161    28%
src\gzkit\commands\readiness.py                   150     33    78%
src\gzkit\commands\register.py                    191     17    91%
src\gzkit\commands\roles.py                        70     30    57%
src\gzkit\commands\skills_cmd.py                   85      4    95%
src\gzkit\commands\specify_cmd.py                 360     66    82%
src\gzkit\commands\state.py                       152      6    96%
src\gzkit\commands\status.py                      221     19    91%
src\gzkit\commands\status_obpi.py                 192     39    80%
src\gzkit\commands\status_obpi_inspect.py         169     19    89%
src\gzkit\commands\status_render.py               196     19    90%
src\gzkit\commands\sync.py                        203     99    51%
src\gzkit\commands\task.py                        132      7    95%
src\gzkit\commands\tidy.py                         89     38    57%
src\gzkit\commands\validate_cmd.py                207     35    83%
src\gzkit\commands\validate_frontmatter.py        151     16    89%
src\gzkit\commands\version_sync.py                103      2    98%
src\gzkit\config.py                                88      0   100%
src\gzkit\core\__init__.py                          0      0   100%
src\gzkit\core\exceptions.py                       30      0   100%
src\gzkit\core\lifecycle.py                        36      0   100%
src\gzkit\core\models.py                          130      3    98%
src\gzkit\core\scoring.py                         195     25    87%
src\gzkit\core\validation_rules.py                 46      0   100%
src\gzkit\decomposition.py                          2      0   100%
src\gzkit\doc_coverage\__init__.py                  5      0   100%
src\gzkit\doc_coverage\manifest.py                 33      1    97%
src\gzkit\doc_coverage\models.py                   43      0   100%
src\gzkit\doc_coverage\runner.py                   61     21    66%
src\gzkit\doc_coverage\scanner.py                 275     30    89%
src\gzkit\eval\__init__.py                          0      0   100%
src\gzkit\eval\datasets.py                         87     26    70%
src\gzkit\eval\delta.py                            76      1    99%
src\gzkit\eval\regression.py                       97      3    97%
src\gzkit\eval\runner.py                           47      0   100%
src\gzkit\eval\scorer.py                          153      1    99%
src\gzkit\events.py                               261     23    91%
src\gzkit\flags\__init__.py                         6      0   100%
src\gzkit\flags\decisions.py                       17      0   100%
src\gzkit\flags\diagnostics.py                     75      1    99%
src\gzkit\flags\models.py                          52      0   100%
src\gzkit\flags\registry.py                        47      2    96%
src\gzkit\flags\service.py                         62      0   100%
src\gzkit\git_sync.py                              93     11    88%
src\gzkit\governance\__init__.py                    0      0   100%
src\gzkit\governance\frontmatter_coherence.py     218     36    83%
src\gzkit\governance\status_vocab.py               14      0   100%
src\gzkit\governance\trust_audits.py              516     98    81%
src\gzkit\handoff_validation.py                   135      2    99%
src\gzkit\hooks\__init__.py                         3      0   100%
src\gzkit\hooks\claude.py                         119      6    95%
src\gzkit\hooks\copilot.py                         19      1    95%
src\gzkit\hooks\core.py                           173     42    76%
src\gzkit\hooks\guards.py                         117      5    96%
src\gzkit\hooks\obpi.py                           367     26    93%
src\gzkit\hooks\scripts\__init__.py                 0      0   100%
src\gzkit\hooks\scripts\pipeline.py                 4      0   100%
src\gzkit\hooks\scripts\quality.py                  2      0   100%
src\gzkit\hooks\scripts\routing.py                  4      0   100%
src\gzkit\hooks\scripts\validation.py               4      0   100%
src\gzkit\instruction_audit.py                    124      7    94%
src\gzkit\instruction_eval.py                     140     17    88%
src\gzkit\interview.py                            119     29    76%
src\gzkit\ledger.py                               338     15    96%
src\gzkit\ledger_events.py                         69      2    97%
src\gzkit\ledger_proof.py                          50      8    84%
src\gzkit\ledger_semantics.py                     208     19    91%
src\gzkit\lifecycle.py                             21      0   100%
src\gzkit\lock_manager.py                          97      2    98%
src\gzkit\models\__init__.py                        2      0   100%
src\gzkit\models\frontmatter.py                     2      0   100%
src\gzkit\models\persona.py                        76      2    97%
src\gzkit\personas.py                             233     26    89%
src\gzkit\pipeline_dispatch.py                    222      2    99%
src\gzkit\pipeline_markers.py                     335     45    87%
src\gzkit\pipeline_runtime.py                     138      5    96%
src\gzkit\pipeline_verification.py                145      1    99%
src\gzkit\ports\__init__.py                         2      0   100%
src\gzkit\ports\interfaces.py                      24      9    62%
src\gzkit\quality.py                              362     46    87%
src\gzkit\registry.py                              57      0   100%
src\gzkit\reporter\__init__.py                      3      0   100%
src\gzkit\reporter\panels.py                       14      0   100%
src\gzkit\reporter\presets.py                      63      1    98%
src\gzkit\roles.py                                 79      1    99%
src\gzkit\rules.py                                265     19    93%
src\gzkit\schemas\__init__.py                      12      0   100%
src\gzkit\skills.py                               132     23    83%
src\gzkit\skills_audit.py                         217     46    79%
src\gzkit\skills_mirror.py                         93      6    94%
src\gzkit\sync.py                                 145      7    95%
src\gzkit\sync_skill_validation.py                152     29    81%
src\gzkit\sync_skills.py                          272     36    87%
src\gzkit\sync_skills_validation.py               123    123     0%
src\gzkit\sync_surfaces.py                        190     12    94%
src\gzkit\tasks.py                                 79      2    97%
src\gzkit\templates\__init__.py                    28      2    93%
src\gzkit\temporal_drift.py                       132      9    93%
src\gzkit\traceability.py                         269     29    89%
src\gzkit\triangle.py                             164      5    97%
src\gzkit\utils.py                                 59     10    83%
src\gzkit\validate.py                              40     22    45%
src\gzkit\validate_pkg\__init__.py                  0      0   100%
src\gzkit\validate_pkg\document.py                 78     25    68%
src\gzkit\validate_pkg\ledger_check.py            132     30    77%
src\gzkit\validate_pkg\manifest.py                 36      8    78%
src\gzkit\validate_pkg\surface.py                  87     42    52%
src\gzkit\validate_pkg\sync_parity.py             128     32    75%
-------------------------------------------------------------------
TOTAL                                           20485   3245    84%
```
