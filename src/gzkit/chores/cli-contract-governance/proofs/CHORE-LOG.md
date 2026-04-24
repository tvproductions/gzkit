# CHORE-LOG: cli-contract-governance

## 2026-03-21T14:38:17-05:00
- Status: PASS
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.29s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (21.75s) — exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.356s

OK
```
## 2026-04-02T18:30:45-05:00
- Status: PASS
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.71s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (33.55s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 68/68 commands fully covered.
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
Claimed: OBPI-0.1.0-01 (agent=unknown-55353, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-55353, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-55353, ttl=240m)
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
  "scan_timestamp": "2026-04-02T23:30:45.193782+00:00"
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
  "scan_timestamp": "2026-04-02T23:30:45.194395+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 33.304s

OK
```
## 2026-04-19T19:46:05-05:00
- Status: FAIL
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run gz cli audit` => rc=1 (1.87s) -- exit 1 != 0

```text
[uv run gz cli audit] stdout:
CLI audit failed.
  - docs\user\commands\arb-ruff.md: missing doc for `arb ruff`
  - docs\user\commands\arb-step.md: missing doc for `arb step`
  - docs\user\commands\arb-ty.md: missing doc for `arb ty`
  - docs\user\commands\arb-typecheck.md: missing doc for `arb typecheck`
  - docs\user\commands\arb-coverage.md: missing doc for `arb coverage`
  - docs\user\commands\arb-validate.md: missing doc for `arb validate`
  - docs\user\commands\arb-advise.md: missing doc for `arb advise`
  - docs\user\commands\arb-patterns.md: missing doc for `arb patterns`
  - cross-coverage:arb ruff: missing manpage: Missing arb-ruff.md
  - cross-coverage:arb ruff: missing index_entry: 'arb-ruff.md' not in index
  - cross-coverage:arb ruff: missing docstring: No handler name resolved
  - cross-coverage:arb step: missing manpage: Missing arb-step.md
  - cross-coverage:arb step: missing index_entry: 'arb-step.md' not in index
  - cross-coverage:arb step: missing docstring: No handler name resolved
  - cross-coverage:arb ty: missing manpage: Missing arb-ty.md
  - cross-coverage:arb ty: missing index_entry: 'arb-ty.md' not in index
  - cross-coverage:arb ty: missing docstring: No handler name resolved
  - cross-coverage:arb typecheck: missing manpage: Missing arb-typecheck.md
  - cross-coverage:arb typecheck: missing index_entry: 'arb-typecheck.md' not
in index
  - cross-coverage:arb typecheck: missing docstring: No handler name resolved
  - cross-coverage:arb coverage: missing manpage: Missing arb-coverage.md
  - cross-coverage:arb coverage: missing index_entry: 'arb-coverage.md' not in
index
  - cross-coverage:arb coverage: missing operator_runbook: 'gz arb coverage'
not found in runbook.md
  - cross-coverage:arb coverage: missing docstring: No handler name resolved
  - cross-coverage:arb validate: missing manpage: Missing arb-validate.md
  - cross-coverage:arb validate: missing index_entry: 'arb-validate.md' not in
index
  - cross-coverage:arb validate: missing docstring: No handler name resolved
  - cross-coverage:arb advise: missing manpage: Missing arb-advise.md
  - cross-coverage:arb advise: missing index_entry: 'arb-advise.md' not in
index
  - cross-coverage:arb advise: missing operator_runbook: 'gz arb advise' not
found in runbook.md
  - cross-coverage:arb advise: missing docstring: No handler name resolved
  - cross-coverage:arb patterns: missing manpage: Missing arb-patterns.md
  - cross-coverage:arb patterns: missing index_entry: 'arb-patterns.md' not in
index
  - cross-coverage:arb patterns: missing operator_runbook: 'gz arb patterns'
not found in runbook.md
  - cross-coverage:arb patterns: missing docstring: No handler name resolved
  - cross-coverage:orphan: orphaned manpage: docs\user\commands\arb.md (Manpage
'arb.md' has no matching discovered command)
  - cross-coverage:orphan: orphaned manpage: docs\user\commands\plan.md
(Manpage 'plan.md' has no matching discovered command)

Cross-coverage: 8/85 commands have gaps.
  - arb ruff: missing manpage, index_entry, docstring
  - arb step: missing manpage, index_entry, docstring
  - arb ty: missing manpage, index_entry, docstring
  - arb typecheck: missing manpage, index_entry, docstring
  - arb coverage: missing manpage, index_entry, operator_runbook, docstring
  - arb validate: missing manpage, index_entry, docstring
  - arb advise: missing manpage, index_entry, operator_runbook, docstring
  - arb patterns: missing manpage, index_entry, operator_runbook, docstring

Orphaned documentation:
  - docs\user\commands\arb.md: Manpage 'arb.md' has no matching discovered
command
  - docs\user\commands\plan.md: Manpage 'plan.md' has no matching discovered
command
```
## 2026-04-19T20:47:34-05:00
- Status: PASS
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (2.01s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (53.41s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 85/85 commands fully covered.
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 52.581s

OK (skipped=1)
```
## 2026-04-19T20:58:23-05:00
- Status: PASS
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (2.02s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (52.90s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 85/85 commands fully covered.
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 52.062s

OK (skipped=1)
```
## 2026-04-24T01:59:29-05:00
- Status: PASS
- Chore: cli-contract-governance
- Title: CLI Contract Governance (Drift & Evolution)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (1.45s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (25.12s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 86/86 commands fully covered.
[uv run -m unittest -q] stdout:
=== Human Attestation Required (GHI #290) ===
  OBPI:        OBPI-0.0.14-02
  Parent ADR:  ADR-0.0.14
  Attestor:    g0
  Attestation: real human attestation

Type the word ATTEST (uppercase, no quotes) to confirm you personally attest, or
anything else to abort:

=== Human Attestation Required (GHI #290) ===
  OBPI:        OBPI-0.0.14-02
  Parent ADR:  ADR-0.0.14
  Attestor:    g0
  Attestation: real attestation

Type the word ATTEST (uppercase, no quotes) to confirm you personally attest, or
anything else to abort:
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3547 tests in 24.742s

OK (skipped=1)
```
