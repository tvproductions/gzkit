# gz obpi emit-receipt

Emit a receipt event (`completed` or `validated`) for a specific OBPI.

---

## Usage

```bash
gz obpi emit-receipt <OBPI-ID> --event {completed,validated} --attestor <text> [--evidence-json <json>] [--dry-run]
```

---

## Runtime Behavior

- Resolves OBPI IDs through ledger rename chains.
- Requires the OBPI to exist in ledger state and on-disk ADR-local `obpis/` paths.
- Blocks OBPIs whose parent ADR is still in pool state.
- Validates `--evidence-json` as a JSON object (when provided).
- Appends `obpi_receipt_emitted` to the ledger (unless `--dry-run`).

---

## Example

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-02-promotion-command-lineage --event validated --attestor "human:Jeff" --evidence-json '{"acceptance":"operator observed deterministic pool promotion behavior","date":"2026-02-21"}'
```
