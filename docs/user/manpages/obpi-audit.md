# gz obpi audit

Gather evidence for OBPI brief and record in audit ledger.

## Usage

```
gz obpi audit OBPI-X.Y.Z-NN [--json]
gz obpi audit --adr ADR-X.Y.Z [--json]
```

## Description

Runs deterministic evidence checks:

- Test file discovery via @covers tags and OBPI references
- Test execution
- Coverage measurement (40% threshold)
- Appends structured entry to `{ADR-dir}/logs/obpi-audit.jsonl`

Does NOT modify brief files (evidence gathering only).

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier to audit |
| `--adr ADR-X.Y.Z` | Audit all OBPIs under this ADR |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All evidence criteria pass |
| 1 | Evidence gaps found |
| 2 | System error |

## Examples

```bash
gz obpi audit OBPI-0.1.0-01
gz obpi audit --adr ADR-0.1.0
gz obpi audit OBPI-0.1.0-01 --json
```
