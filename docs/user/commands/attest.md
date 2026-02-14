# gz attest

Record human attestation for an ADR.

---

## Usage

```bash
gz attest <ADR> --status {completed,partial,dropped} [--reason <text>] [--force] [--dry-run]
```

---

## Runtime Behavior

`gz attest` enforces prerequisite gates before writing an attestation event.

- Lite lane: Gate 2 must be `pass`.
- Heavy lane: Gate 2 and Gate 3 must be `pass`.
- Heavy lane Gate 4: must be `pass` when `features/` exists; otherwise Gate 4 is treated as N/A with explicit rationale.

If prerequisites fail, the command exits non-zero.

`--force` bypasses failed prerequisites, but `--reason` is mandatory when bypassing.

---

## Canonical Term Mapping

Input status tokens stay stable for CLI compatibility, but outputs map to canonical terms:

| Input token | Canonical term |
|-------------|----------------|
| `completed` | `Completed` |
| `partial` | `Completed — Partial` |
| `dropped` | `Dropped` |

`partial` and `dropped` always require `--reason`.

---

## Examples

```bash
# Standard completion
gz attest ADR-0.3.0 --status completed

# Partial completion with rationale
gz attest ADR-0.3.0 --status partial --reason "Scope reduced to runtime parity"

# Dropped with rationale
gz attest ADR-0.3.0 --status dropped --reason "Superseded by newer ADR"

# Force bypass with explicit accountability rationale
gz attest ADR-0.3.0 --status completed --force --reason "Emergency override after manual verification"

# Preview only
gz attest ADR-0.3.0 --status completed --dry-run
```

---

## Notes

- Attestation writes an `attested` ledger event.
- `gz status` and `gz adr status` display canonical lifecycle/term overlays derived from ledger events.
- Human attestation remains explicit and manual.
