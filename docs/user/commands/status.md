# gz status

Display gate and lifecycle status across ADRs.

---

## Usage

```bash
gz status [--json]
```

---

## Runtime Behavior

`gz status` derives ADR lifecycle from ledger events and keeps gate output additive/backward-compatible.

Per ADR it reports:

- Gate summaries (`1..5` where lane-applicable)
- Canonical lifecycle (`Pending`, `Completed`, `Validated`, `Abandoned`)
- Canonical attestation term when attested
- Heavy-lane Gate 4 N/A rationale when `features/` is absent

`Validated` applies to ADR-level validation receipts. OBPI-scoped receipts marked with
`adr_completion: not_completed` do not mark the parent ADR as validated.

---

## JSON Output

`--json` includes the existing top-level shape plus enriched per-ADR data (`gates`, `lane`, `lifecycle_status`, `attestation_term`, `closeout_phase`, and related additive fields).

---

## Example

```bash
uv run gz status
uv run gz status --json
```
