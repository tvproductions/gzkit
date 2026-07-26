# gz obpi repudiate

Repudiate a fraudulent or erroneous OBPI completion without retiring the OBPI.

## Usage

```bash
gz obpi repudiate OBPI-<X.Y.Z-NN> --cause <enum> --reason "<text>" --attestor "<human>"
gz obpi repudiate OBPI-<X.Y.Z-NN> --cause <enum> --reason "<text>" --attestor "<human>" --dry-run
```

## Description

Records an `obpi_completion_repudiated` event in the ledger. Reverses an
erroneous or fraudulent completion **without** the permanent retirement
semantics of `gz obpi withdraw` — the OBPI stays live in `gz state` and
is re-completable after a genuine re-attestation.

**Operator-gated.** Only a human may repudiate a Gate-5 attestation.
`--attestor` and `--reason` are required and must be non-empty; empty values
exit 1 with no ledger write.

**Withdraw vs Repudiate:**

| Verb | What it does | OBPI state after |
|------|-------------|-----------------|
| `gz obpi withdraw` | Permanent one-way retirement | `withdrawn=True`; hidden from `gz state`; no re-completion path |
| `gz obpi repudiate` | Reverse-and-keep | `repudiated=True`; visible in `gz state`; re-completable via genuine attestation |

Use `repudiate` when an existing completion was fraudulent or invalid and
the OBPI should be re-completed honestly. Use `withdraw` when the OBPI is
being permanently retired (superseded, phantom entry, etc.).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `obpi` | Yes | OBPI identifier (e.g. OBPI-0.0.70-02) |

## Flags

| Flag | Description |
|------|-------------|
| `--cause` | Required cause enum: `model-induced-fabrication`, `operator-error`, or `verification-invalid` |
| `--reason` | Required repudiation reason text (non-empty) |
| `--attestor` | Human attestor name (non-empty; only humans may repudiate a Gate-5) |
| `--dry-run` | Show planned event without writing to ledger |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (OBPI not found, not completed, empty attestor/reason) |
| 2 | Parser error (invalid `--cause` value) |

## Examples

```bash
# Repudiate a fabricated Gate-5 attestation
gz obpi repudiate OBPI-0.0.70-02 \
  --cause model-induced-fabrication \
  --reason "Agent fabricated attestation — operator only said 'attest completed' for -01" \
  --attestor "g0"

# Dry-run to preview the event without writing
gz obpi repudiate OBPI-0.0.70-02 \
  --cause operator-error \
  --reason "Completed with wrong evidence" \
  --attestor "g0" \
  --dry-run
```

## Related

- `gz obpi withdraw` — permanently retire an OBPI (one-way, no re-completion)
- `gz obpi complete` — record a genuine completion attestation
- `gz obpi sync` — verify brief and ledger state agree after repudiation
