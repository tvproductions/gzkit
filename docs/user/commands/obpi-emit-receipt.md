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
- Completed receipts normalize machine-readable `req_proof_inputs`.
  - If `evidence.req_proof_inputs` is supplied, each item must include
    `name`, `kind`, `source`, and `status`.
  - Each item may also include optional `scope` and `gap_reason`.
  - If it is omitted, gzkit derives a minimal proof-input list from `key_proof`
    and any completed human-attestation evidence.
- For `--event completed` under Heavy or Foundation (`ADR-0.0.x`) parent ADRs,
  fails closed unless evidence also includes:
  - `human_attestation: true`
  - `attestation_text` (string)
  - `attestation_date` (`YYYY-MM-DD`)
  and `--attestor` uses `human:<name>` format.
- Appends `obpi_receipt_emitted` to the ledger (unless `--dry-run`).
  Completed receipts write machine-readable completion semantics
  (`obpi_completion`) plus proof metadata for lifecycle reconciliation.
- Completed receipts also carry structured recorder context:
  - `scope_audit` (`allowlist`, `changed_files`, `out_of_scope_files`)
  - `git_sync_state` (branch/remote/dirty/ahead/behind/diverged/actions/warnings/blockers)
  - `recorder_source`
  - `recorder_warnings`
- If `scope_audit` or `git_sync_state` is omitted for a completed receipt,
  gzkit derives it from the current OBPI brief and repository state. If either
  field is supplied explicitly, gzkit validates the structure before writing the
  receipt.
- The resulting runtime evidence is consumed by `gz obpi status`,
  `gz obpi reconcile`, and ADR status/lifecycle surfaces.

---

## Example

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-02-promotion-command-lineage --event validated --attestor "human:Jeff" --evidence-json '{"acceptance":"operator observed deterministic pool promotion behavior","date":"2026-02-21"}'

uv run gz obpi emit-receipt OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --event completed --attestor "human:jeff" --evidence-json '{"value_narrative":"OBPI completion receipts now preserve structured scope and git-sync evidence for later drift checks.","key_proof":"uv run gz obpi status OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --json","human_attestation":true,"attestation_text":"attest completed","attestation_date":"2026-03-01","req_proof_inputs":[{"name":"key_proof","kind":"command","source":"uv run gz obpi status OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --json","status":"present"},{"name":"human_attestation","kind":"attestation","source":"human:jeff @ 2026-03-01","status":"present"}]}'
```
