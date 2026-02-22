# gz status

Display OBPI progress, lifecycle status, and gate readiness across ADRs.

---

## Usage

```bash
gz status [--json] [--table] [--show-gates]
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

`--table` renders a stable summary table with one row per ADR:
- ADR id
- lifecycle status
- lane
- OBPI completion ratio
- OBPI unit status
- QC readiness
- pending check categories

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
uv run gz status --table
uv run gz status --show-gates
uv run gz status --json
```

Table output excerpt (captured 2026-02-22):

```text
ADR Status
| ADR                                  | Lifecycle | Lane  | OBPI | OBPI Unit | QC      | Pending Checks               |
| ------------------------------------ | --------- | ----- | ---- | --------- | ------- | ---------------------------- |
| ADR-0.6.0-pool-promotion-protocol    | Pending   | HEAVY | 3/3  | COMPLETED | PENDING | Human attestation            |
| ADR-0.4.0-skill-capability-mirroring | Validated | HEAVY | 4/4  | COMPLETED | READY   | -                            |
```
