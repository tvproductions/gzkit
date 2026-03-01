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
- For `--event completed`, fails closed unless evidence includes:
  - `value_narrative` (string)
  - `key_proof` (string)
- For `--event completed` under Heavy or Foundation (`ADR-0.0.x`) parent ADRs,
  fails closed unless evidence also includes:
  - `human_attestation: true`
  - `attestation_text` (string)
  - `attestation_date` (`YYYY-MM-DD`)
  and `--attestor` uses `human:<name>` format.
- Appends `obpi_receipt_emitted` to the ledger (unless `--dry-run`).
  Completed receipts write machine-readable completion semantics
  (`obpi_completion`) for lifecycle reconciliation.

---

## Example

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-02-promotion-command-lineage --event validated --attestor "human:Jeff" --evidence-json '{"acceptance":"operator observed deterministic pool promotion behavior","date":"2026-02-21"}'

uv run gz obpi emit-receipt OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --event completed --attestor "human:jeff" --evidence-json '{"value_narrative":"OBPI completion now fail-closes when attestation evidence is missing for Heavy/Foundation parents.","key_proof":"uv run gz obpi emit-receipt ... --event completed --evidence-json <payload>","human_attestation":true,"attestation_text":"attest completed","attestation_date":"2026-03-01"}'
```
