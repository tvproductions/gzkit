# gz obpi withdraw

Record an OBPI withdrawal event.

## Usage

```bash
gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..." --attestor "<human>"
gz obpi withdraw OBPI-<X.Y.Z-NN> --reason "..." --attestor "<human>" --dry-run
```

## Description

Records an `obpi_withdrawn` event in the ledger. The OBPI remains in the
ledger for audit history but is excluded from completion counts and
roll-up calculations. Use when an OBPI is no longer needed or has been
superseded.

Withdrawal is a **witnessed transition**: per the OBPI state machine
(OBPI-0.31.0-02 / OBPI-01), the `withdrawn` transition declares a
`human_attested` witness, so `--attestor` is required and must be
non-empty. Withdrawal is permanent and one-way — there is no
re-completion path once withdrawn. Use `gz obpi repudiate` instead when
the intent is to reverse a completion while keeping the OBPI re-completable.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.21.0-01) |

## Flags

| Flag | Description |
|------|-------------|
| `--reason` | Required reason string for withdrawal |
| `--attestor` | Human attestor witnessing the withdrawal (non-empty; only humans witness) |
| `--dry-run` | Show planned actions without executing |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (invalid OBPI, missing reason, missing attestor) |

## Examples

```bash
# Withdraw an OBPI with reason
uv run gz obpi withdraw OBPI-0.21.0-03 --reason "Superseded by OBPI-0.21.0-04" --attestor "Jane Doe"

# Dry-run to see what would happen
uv run gz obpi withdraw OBPI-0.21.0-03 --reason "No longer needed" --attestor "Jane Doe" --dry-run
```
