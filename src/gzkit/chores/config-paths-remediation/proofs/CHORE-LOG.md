# CHORE-LOG: config-paths-remediation

## 2026-03-21T14:30:55-05:00
- Status: PASS
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (22.22s) — exit 0 == 0
  - [PASS] `uv run gz check-config-paths` => rc=0 (0.31s) — exit 0 == 0

```text
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.831s

OK
[uv run gz check-config-paths] stdout:
Config-path audit passed.
```
## 2026-04-02T18:33:22-05:00
- Status: PASS
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (33.78s) -- exit 0 == 0
  - [PASS] `uv run gz check-config-paths` => rc=0 (0.29s) -- exit 0 == 0

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
Claimed: OBPI-0.1.0-01 (agent=unknown-60411, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-60411, ttl=120m)
Claimed: OBPI-0.1.0-01 (agent=unknown-60411, ttl=240m)
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
  "scan_timestamp": "2026-04-02T23:33:21.514641+00:00"
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
  "scan_timestamp": "2026-04-02T23:33:21.515247+00:00"
}
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 2359 tests in 33.538s

OK
[uv run gz check-config-paths] stdout:
Config-path audit passed.
```
## 2026-04-19T19:48:01-05:00
- Status: FAIL
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (51.34s) -- exit 0 == 0
  - [FAIL] `uv run gz check-config-paths` => rc=1 (0.54s) -- exit 1 != 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 50.521s

OK (skipped=1)
[uv run gz check-config-paths] stdout:
Config-path audit failed.
[uv run gz check-config-paths] stderr:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\Jeff\source\repos\va\gzkit\.venv\Scripts\gz.exe\__main__.py", line 10, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Users\Jeff\source\repos\va\gzkit\src\gzkit\cli\main.py", line 166, in main
    console.print(f"[red]Unexpected error: {exc}[/red]")
    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Jeff\source\repos\va\gzkit\.venv\Lib\site-packages\rich\console.py", line 1698, in print
    renderables = self._collect_renderables(
        objects,
    ...<5 lines>...
        highlight=highlight,
    )
  File "C:\Users\Jeff\source\repos\va\gzkit\.venv\Lib\site-packages\rich\console.py", line 1558, in _collect_renderables
    self.render_str(
    ~~~~~~~~~~~~~~~^
        renderable,
        ^^^^^^^^^^^
    ...<3 lines>...
        highlighter=_highlighter,
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\Jeff\source\repos\va\gzkit\.venv\Lib\site-packages\rich\console.py", line 1448, in render_str
    rich_text = render_markup(
        text,
    ...<2 lines>...
        emoji_variant=self._emoji_variant,
    )
  File "C:\Users\Jeff\source\repos\va\gzkit\.venv\Lib\site-packages\rich\markup.py", line 167, in render
    raise MarkupError(
        f"closing tag '{tag.markup}' at position {position} doesn't match any open tag"
    ) from None
rich.errors.MarkupError: closing tag '[/green]' at position 36 doesn't match any open tag
```
## 2026-04-19T20:14:28-05:00
- Status: PASS
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (51.62s) -- exit 0 == 0
  - [PASS] `uv run gz check-config-paths` => rc=0 (0.52s) -- exit 0 == 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 50.822s

OK (skipped=1)
[uv run gz check-config-paths] stdout:
Config-path audit passed.
```
## 2026-04-19T21:00:11-05:00
- Status: PASS
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (53.16s) -- exit 0 == 0
  - [PASS] `uv run gz check-config-paths` => rc=0 (0.55s) -- exit 0 == 0

```text
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 3243 tests in 52.339s

OK (skipped=1)
[uv run gz check-config-paths] stdout:
Config-path audit passed.
```
## 2026-04-24T02:01:25-05:00
- Status: PASS
- Chore: config-paths-remediation
- Title: Config Paths Remediation
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest -q` => rc=0 (25.65s) -- exit 0 == 0
  - [PASS] `uv run gz check-config-paths` => rc=0 (0.29s) -- exit 0 == 0

```text
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
Ran 3547 tests in 25.278s

OK (skipped=1)
[uv run gz check-config-paths] stdout:
Config-path audit passed.
```
