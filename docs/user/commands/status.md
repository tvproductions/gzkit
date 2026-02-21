# gz status

Display OBPI progress, lifecycle status, and gate readiness across ADRs.

---

## Usage

```bash
gz status [--json] [--show-gates]
```

---

## Runtime Behavior

`gz status` derives ADR lifecycle from ledger events and treats OBPI completion as the primary progress unit.

Per ADR it reports:

- OBPI summary (`total`, `completed`, `incomplete`, `unit_status`)
- OBPI rows (linked file presence, completion, evidence, issues)
- QC readiness summary (`READY` / `PENDING` with pending checkpoints)
- Canonical lifecycle (`Pending`, `Completed`, `Validated`, `Abandoned`)
- Canonical attestation term when attested
- Gate summaries (`1..5` where lane-applicable) only when `--show-gates` is supplied
- Heavy-lane Gate 4 N/A rationale when `features/` is absent

`Validated` applies to ADR-level validation receipts. OBPI-scoped receipts marked with
`adr_completion: not_completed` do not mark the parent ADR as validated.

When linked OBPIs exist and the OBPI unit is not `completed`, lifecycle is reported as `Pending`
even if ledger attestation/receipt events indicate `Completed` or `Validated`.

---

## JSON Output

`--json` includes the existing top-level shape plus enriched per-ADR data:
- `obpis`
- `obpi_summary`
- `gates`
- `lane`
- `lifecycle_status`
- `attestation_term`
- `closeout_phase`
- related additive fields

---

## Example

```bash
uv run gz status
uv run gz status --show-gates
uv run gz status --json
```
