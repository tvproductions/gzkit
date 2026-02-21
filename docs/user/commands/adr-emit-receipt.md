# gz adr emit-receipt

Emit a receipt event (`completed` or `validated`) for an ADR.

---

## Usage

```bash
gz adr emit-receipt <ADR-ID> --event {completed,validated} --attestor <text> [--evidence-json <json>] [--dry-run]
```

---

## Runtime Behavior

- Validates receipt event choice.
- Validates `--evidence-json` as a JSON object (when provided).
- Blocks pool ADRs (`ADR-pool.*`) until promoted out of pool.
- Appends `audit_receipt_emitted` to the ledger (unless `--dry-run`).

For OBPI-level receipt events, prefer `gz obpi emit-receipt`.
ADR-scoped evidence payloads remain supported for compatibility. If you use ADR receipts
for OBPI context, include explicit scope fields:

- `scope: "OBPI-..."`
- `adr_completion: "not_completed"`
- `obpi_completion: "attested_completed"`

---

## Example

```bash
uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"OBPI-0.3.0-04","adr_completion":"not_completed","obpi_completion":"attested_completed"}'
```
