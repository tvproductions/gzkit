# CHORE-LOG: skill-command-doc-parity

## 2026-03-21T13:28:32-05:00
- Status: PASS
- Chore: skill-command-doc-parity
- Title: Skill & Command Documentation Parity
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.32s) — exit 0 == 0
  - [PASS] `uv run gz validate --documents --surfaces` => rc=0 (0.34s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (22.76s) — exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
[uv run gz validate --documents --surfaces] stdout:
All validations passed.
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 22.341s

OK
```
## 2026-03-21T14:38:46-05:00
- Status: PASS
- Chore: skill-command-doc-parity
- Title: Skill & Command Documentation Parity
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.29s) — exit 0 == 0
  - [PASS] `uv run gz validate --documents --surfaces` => rc=0 (0.30s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (22.04s) — exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
[uv run gz validate --documents --surfaces] stdout:
All validations passed.
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.646s

OK
```
## 2026-04-02T19:51:43-05:00
- Status: PASS
- Chore: skill-command-doc-parity
- Title: Skill & Command Documentation Parity
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.71s) -- exit 0 == 0
  - [PASS] `uv run gz validate --documents --surfaces` => rc=0 (0.16s) -- exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (33.80s) -- exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
Cross-coverage: 68/68 commands fully covered.
[uv run gz validate --documents --surfaces] stdout:
Validated: surfaces, documents

✓ All validations passed (2 scopes).
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
Claimed: OBPI-0.1.0-01 (agent=unknown-17786, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-17786, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-17786, ttl=240m)
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
  "scan_timestamp": "2026-04-03T00:51:43.126303+00:00"
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
  "scan_timestamp": "2026-04-03T00:51:43.126846+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 33.560s

OK
```
