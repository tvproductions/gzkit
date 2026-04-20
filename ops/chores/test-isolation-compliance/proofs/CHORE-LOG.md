# CHORE-LOG: test-isolation-compliance

## 2026-03-21T14:36:32-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation Compliance (Temp DB + Temp Dir)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (21.71s) — exit 0 == 0

```text
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.326s

OK
```
## 2026-04-02T19:53:31-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation Compliance (Temp DB + Temp Dir)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (37.57s) -- exit 0 == 0

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
Claimed: OBPI-0.1.0-01 (agent=unknown-21568, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-21568, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-21568, ttl=240m)
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
  "scan_timestamp": "2026-04-03T00:53:31.101930+00:00"
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
  "scan_timestamp": "2026-04-03T00:53:31.102534+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 37.320s

OK
```
## 2026-04-19T20:04:23-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (51.56s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (51.89s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 3243  Wall: 50.7s
Failures: 0  Errors: 0

Top 5 slowest tests:
   1.732s  test_check_surfaces_report_returns_valid_report (tests.test_doc_coverage.TestIntegration.test_check_surfaces_report_returns_valid_report)
   1.032s  test_chores_run_timeout_returns_nonzero (tests.commands.test_chores.TestChoresCommands.test_chores_run_timeout_returns_nonzero)
   0.619s  test_pydantic_models_rules_25_26 (tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits.test_pydantic_models_rules_25_26)
   0.532s  test_runtime_budget_under_one_second_on_real_repo (tests.commands.test_validate_frontmatter.TestFrontmatterGuard.test_runtime_budget_under_one_second_on_real_repo)
   0.477s  test_tier_b_rebuild_and_gz_state (tests.adr.test_storage_tiers.TestGitCloneRecovery.test_tier_b_rebuild_and_gz_state)

Top 5 modules by time:
    3.7s   25 tests  148.0ms/test  tests.test_obpi_validator.TestObpiValidator
    1.8s    2 tests  875.0ms/test  tests.test_doc_coverage.TestIntegration
    1.6s   33 tests   49.1ms/test  tests.commands.test_runtime.TestAdrRuntimeCommands
    1.5s   31 tests   47.7ms/test  tests.test_sync.TestSyncControlSurfaces
    1.5s   15 tests   97.3ms/test  tests.commands.test_skills.TestSkillCommands

PASSED: All thresholds met.
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 51.078s

OK (skipped=1)
```
## 2026-04-19T21:17:10-05:00
- Status: PASS
- Chore: test-isolation-compliance
- Title: Test Isolation & Health Compliance
- Lane: lite
- Version: 2.0.0
- Criteria Results:
  - [PASS] `uv run python tests/tools/test_health_profiler.py` => rc=0 (50.66s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (50.94s) -- exit 0 == 0

```text
[uv run python tests/tools/test_health_profiler.py] stdout:
Tests: 3243  Wall: 49.9s
Failures: 0  Errors: 0

Top 5 slowest tests:
   1.794s  test_check_surfaces_report_returns_valid_report (tests.test_doc_coverage.TestIntegration.test_check_surfaces_report_returns_valid_report)
   1.037s  test_chores_run_timeout_returns_nonzero (tests.commands.test_chores.TestChoresCommands.test_chores_run_timeout_returns_nonzero)
   0.580s  test_pydantic_models_rules_25_26 (tests.governance.test_promoted_advisory_audits.PromotedAdvisoryAudits.test_pydantic_models_rules_25_26)
   0.498s  test_runtime_budget_under_one_second_on_real_repo (tests.commands.test_validate_frontmatter.TestFrontmatterGuard.test_runtime_budget_under_one_second_on_real_repo)
   0.470s  test_tier_b_rebuild_and_gz_state (tests.adr.test_storage_tiers.TestGitCloneRecovery.test_tier_b_rebuild_and_gz_state)

Top 5 modules by time:
    3.6s   25 tests  143.2ms/test  tests.test_obpi_validator.TestObpiValidator
    1.8s    2 tests  910.0ms/test  tests.test_doc_coverage.TestIntegration
    1.6s   33 tests   47.0ms/test  tests.commands.test_runtime.TestAdrRuntimeCommands
    1.5s   14 tests  110.0ms/test  tests.commands.test_validate_cmds.TestValidateCommand
    1.5s   25 tests   60.4ms/test  tests.commands.test_status.TestStatusCommand

PASSED: All thresholds met.
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 50.152s

OK (skipped=1)
```
