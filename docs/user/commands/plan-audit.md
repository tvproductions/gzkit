# gz plan audit

Structural prerequisite check for plan-OBPI alignment.

## Usage

```
gz plan-audit OBPI-X.Y.Z-NN [--json]
```

## Description

Runs deterministic structural checks:
- ADR package directory exists
- OBPI brief file exists
- Plan file exists in `.claude/plans/`
- Plan file paths stay within brief allowed paths

Writes a receipt to `.claude/plans/.plan-audit-receipt-{OBPI-ID}.json`.

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS -- all prerequisites met |
| 1 | FAIL -- structural gaps found |
| 2 | System error |

## Examples

```bash
gz plan-audit OBPI-0.1.0-01
gz plan-audit OBPI-0.1.0-01 --json
```
