# gz obpi withdraw

Record an OBPI withdrawal event.

## Usage

```bash
gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..."
gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..." --dry-run
```

## Description

Records an `obpi_withdrawn` event in the ledger. The OBPI remains in the
ledger for audit history but is excluded from completion counts and
roll-up calculations. Use when an OBPI is no longer needed or has been
superseded.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.21.0-01) |

## Flags

| Flag | Description |
|------|-------------|
| `--reason` | Required reason string for withdrawal |
| `--dry-run` | Show planned actions without executing |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (invalid OBPI, missing reason) |

## Examples

```bash
# Withdraw an OBPI with reason
uv run gz obpi withdraw OBPI-0.21.0-03 --reason "Superseded by OBPI-0.21.0-04"

# Dry-run to see what would happen
uv run gz obpi withdraw OBPI-0.21.0-03 --reason "No longer needed" --dry-run
```
