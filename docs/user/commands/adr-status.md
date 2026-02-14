# gz adr status

Show focused gate and lifecycle status for one ADR.

---

## Usage

```bash
gz adr status <ADR-ID> [--json]
```

---

## Runtime Behavior

`gz adr status` is ledger-first and additive.

It keeps existing compatibility fields and adds derived semantics:

- `lane`
- `lifecycle_status`
- `closeout_phase`
- `attestation_term`
- `closeout_initiated`
- `validated`
- `gate4_na_reason` (when applicable)

Lifecycle is derived from `attested`, `closeout_initiated`, and `audit_receipt_emitted` events.
OBPI-scoped receipts that carry `adr_completion: not_completed` remain accounting artifacts and do
not set ADR lifecycle to `Validated`.

---

## Example

```bash
uv run gz adr status ADR-0.3.0 --json
```
