# gz obpi supersede

Supersede one OBPI by another.

## Usage

```bash
gz obpi supersede OBPI-<X.Y.Z-NN> --by OBPI-<X.Y.Z-MM> --rationale "..." --attestor "<human>"
gz obpi supersede OBPI-<X.Y.Z-NN> --by OBPI-<X.Y.Z-MM> --rationale "..." --attestor "<human>" --dry-run
```

## Description

Records an `obpi_superseded` event in the ledger. The superseded OBPI's
graph node is marked `superseded`; the OBPI remains in the ledger for
audit history but is replaced by the superseding OBPI named via `--by`.

Supersession is a **witnessed transition**: per the OBPI state machine
(OBPI-0.31.0-02 / OBPI-01), the `superseded` transition declares a
`human_attested` witness, so `--attestor` is required and must be
non-empty. Use `supersede` when an OBPI's intent is carried forward by a
different, replacing OBPI (e.g. a redesigned brief). Use `gz obpi
withdraw` instead when an OBPI is simply retired with no replacement.

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.21.0-01) |

## Flags

| Flag | Description |
|------|-------------|
| `--by` | Superseding OBPI identifier |
| `--rationale` | Why the OBPI is superseded (non-empty) |
| `--attestor` | Human attestor witnessing the supersession (non-empty) |
| `--dry-run` | Show planned actions without executing |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (invalid OBPI, missing rationale/attestor) |

## Examples

```bash
# Supersede an OBPI with the replacement that carries its intent forward
uv run gz obpi supersede OBPI-0.21.0-01 --by OBPI-0.21.0-04 \
  --rationale "Replaced by redesigned brief" --attestor "Jane Doe"

# Dry-run to see what would happen
uv run gz obpi supersede OBPI-0.21.0-01 --by OBPI-0.21.0-04 \
  --rationale "Replaced by redesigned brief" --attestor "Jane Doe" --dry-run
```

## Related

- `gz obpi withdraw` — permanently retire an OBPI with no replacement
- `gz obpi repudiate` — reverse a fraudulent or erroneous completion without retiring the OBPI
