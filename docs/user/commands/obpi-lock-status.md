# gz obpi lock-status

List active OBPI work locks.

## Usage

```
gz obpi lock-status [--adr ADR-X.Y.Z] [--json]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `--adr ADR-X.Y.Z` | Filter locks by parent ADR |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 2 | System error |

## Examples

```bash
gz obpi lock-status
gz obpi lock-status --adr ADR-0.1.0
gz obpi lock-status --json
```
