# gz covers

Report requirement coverage from `@covers` annotations.

## Usage

```bash
gz covers [TARGET] [OPTIONS]
```

## Description

Scans test files for `@covers` decorators and cross-references
against known REQs extracted from OBPI briefs. Reports coverage
at three granularity levels:

- **All** --- `gz covers` (no arguments)
- **By ADR** --- `gz covers ADR-0.20.0`
- **By OBPI** --- `gz covers OBPI-0.20.0-01`

Coverage reporting is informational and always exits with code 0.

## Arguments

| Argument | Description |
|----------|-------------|
| `TARGET` | Optional. `ADR-X.Y.Z` or `OBPI-X.Y.Z-NN` to filter scope |

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output valid JSON CoverageReport to stdout |
| `--plain` | One record per line (grep-friendly) |
| `--adr-dir DIR` | Override ADR directory (default: `docs/design/adr`) |
| `--test-dir DIR` | Override test directory (default: `tests`) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Always (coverage reporting is informational) |

## Examples

```bash
# Show all-REQ coverage summary
gz covers

# Coverage for a single ADR
gz covers ADR-0.20.0

# Coverage for a single OBPI
gz covers OBPI-0.20.0-01

# Machine-readable JSON output
gz covers --json

# Grep-friendly plain output for one ADR
gz covers ADR-0.20.0 --plain
```

## Output Modes

### Human (default)

```text
Coverage by ADR
ADR                   Covered    Total        %
------------------------------------------------
ADR-0.15.0                  3        5    60.0%
ADR-0.20.0                  2        3    66.7%

Coverage by OBPI
OBPI                  Covered    Total        %
------------------------------------------------
OBPI-0.15.0-03              2        3    66.7%
OBPI-0.15.0-04              1        2    50.0%
OBPI-0.20.0-01              2        3    66.7%

Summary: 5/8 REQs covered (62.5%)
```

### JSON (`--json`)

```json
{
  "by_adr": [
    {
      "identifier": "ADR-0.15.0",
      "total_reqs": 5,
      "covered_reqs": 3,
      "uncovered_reqs": 2,
      "coverage_percent": 60.0
    }
  ],
  "by_obpi": [...],
  "entries": [
    {
      "req_id": "REQ-0.15.0-03-01",
      "covered": true,
      "covering_tests": ["TestFoo.test_bar"]
    }
  ],
  "summary": {
    "identifier": "all",
    "total_reqs": 8,
    "covered_reqs": 5,
    "uncovered_reqs": 3,
    "coverage_percent": 62.5
  }
}
```

### Plain (`--plain`)

```text
REQ-0.15.0-03-01	covered	TestFoo.test_bar
REQ-0.15.0-03-02	uncovered	-
REQ-0.15.0-03-03	uncovered	-
```
