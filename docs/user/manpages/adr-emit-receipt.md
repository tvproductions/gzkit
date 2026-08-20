# gz adr emit-receipt

Emit a receipt event (`completed`, `validated`, or `closed`) for an ADR.

---

## Usage

```bash
gz adr emit-receipt <ADR-ID> --event {completed,validated,closed} --attestor <text> [--evidence-json <json>] [--attestor-present] [--dry-run]
```

---

## Options

| Option | Description |
|--------|-------------|
| `--event` | Receipt event type (`completed`, `validated`, or `closed`) |
| `--attestor` | Identity of the attestor |
| `--evidence-json` | JSON payload with `value_narrative`, `key_proof`; Heavy/Foundation adds attestation fields |
| `--attestor-present` | Retained for compatibility; no longer load-bearing. Human-attestation receipt events record the operator's verbatim attestation from the `--evidence-json` `attestation_text` (or `scope`) field as `attestation_type: operator-verbatim-conversational`. The prior TTY `ATTEST` authenticity gate has been removed. |
| `--dry-run` | Show planned actions without executing |

---

## Runtime Behavior

- Validates receipt event choice.
- Validates `--evidence-json` as a JSON object (when provided).
- Blocks pool ADRs (`ADR-pool.*`) until promoted out of pool.
- Appends `audit_receipt_emitted` to the ledger (unless `--dry-run`).
- **REQ-coverage gate (`--event closed`, ADR-0.0.25):** Refuses to close the ADR while any of its OBPIs has an unwaived REQ gap. Each REQ in a brief's `## Acceptance Criteria` section must have at least one passing `@covers`-decorated test. Exits 3 when the gate fires. Use `--accept-uncovered REQ-ID --accept-uncovered-reason REASON` on `gz obpi complete` to waive individual REQs before closing the ADR.

For OBPI-level receipt events, prefer `gz obpi emit-receipt`.
ADR-scoped evidence payloads remain supported for compatibility. If you use ADR receipts
for OBPI context, include explicit scope fields:

- `scope: "OBPI-..."`
- `adr_completion: "not_completed"`
- `obpi_completion: "attested_completed"`

---

## Example

```bash
uv run gz adr emit-receipt ADR-0.3.0 --event validated --attestor "g0" --evidence-json '{"scope":"OBPI-0.3.0-04","adr_completion":"not_completed","obpi_completion":"attested_completed"}'
```
