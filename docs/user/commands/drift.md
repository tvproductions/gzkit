# gz drift

Detect spec-test-code governance drift.

## Usage

```bash
gz drift [OPTIONS]
```

## Description

Scans OBPI briefs for REQ entities, test files for `@covers`
references, and the active repository change set to detect
governance drift. Reports three drift categories:

- **Unlinked specs** — REQs with no test coverage
- **Orphan tests** — tests covering absent REQs
- **Unjustified code changes** — source changes without
  governance justification

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output valid JSON DriftReport to stdout |
| `--plain` | One record per line (grep-friendly) |
| `--adr-dir DIR` | Override ADR directory (default: `docs/design/adr`) |
| `--test-dir DIR` | Override test directory (default: `tests`) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No drift detected |
| 1 | Drift detected in one or more categories |

## Examples

```bash
# Human-readable drift report
gz drift

# Machine-readable JSON output
gz drift --json

# Grep-friendly plain output
gz drift --plain

# Scan a specific ADR directory
gz drift --adr-dir docs/design/adr/pre-release/ADR-0.20.0
```

## Output Modes

### Human (default)

```text
Unlinked Specs (REQs with no test)
----------------------------------------
  REQ-0.15.0-03-01
  REQ-0.15.0-03-02

Summary: 2 unlinked, 0 orphan, 0 unjustified (2 total)
```

### JSON (`--json`)

```json
{
  "unlinked_specs": ["REQ-0.15.0-03-01"],
  "orphan_tests": [],
  "unjustified_code_changes": [],
  "summary": {
    "unlinked_spec_count": 1,
    "orphan_test_count": 0,
    "unjustified_code_change_count": 0,
    "total_drift_count": 1
  },
  "scan_timestamp": "2026-03-27T00:00:00Z"
}
```

### Plain (`--plain`)

```text
unlinked	REQ-0.15.0-03-01
orphan	REQ-0.15.0-99-01
unjustified	src/gzkit/module.py
```
