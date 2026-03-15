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
For single-OBPI drilldown, use `gz obpi status` or `gz obpi reconcile`.

Per ADR it reports:

- OBPI summary (`total`, `completed`, `incomplete`, `unit_status`)
- OBPI rows (linked file presence, `runtime_state`, proof/attestation state, anchor state, and issues)
- Closeout readiness fields (`closeout_ready`, `closeout_blockers`)
- QC readiness summary (`READY` / `PENDING` with pending checkpoints)
- Canonical lifecycle (`Pending`, `Completed`, `Validated`, `Abandoned`)
- Canonical attestation term when attested
- Gate summaries (`1..5` where lane-applicable) only when `--show-gates` is supplied

`--table` renders a stable summary table with one row per ADR:
- ADR id
- lifecycle status
- lane
- OBPI completion ratio
- OBPI unit status
- QC readiness
- pending check categories (compact codes in `Checks`)

QC readiness is fail-closed for OBPI-first delivery:
- when linked OBPIs exist and OBPI unit is not `completed`, `QC` reports `PENDING`
- `Checks` includes `O` (`OBPI completion`) even if gate checks are otherwise passing

`Validated` applies to ADR-level validation receipts. OBPI-scoped receipts marked with
`adr_completion: not_completed` do not mark the parent ADR as validated.

When linked OBPIs exist and the OBPI unit is not `completed`, lifecycle is reported as `Pending`
even if ledger attestation/receipt events indicate `Completed` or `Validated`.
Anchor freshness stays fail-closed in `closeout_blockers`, but a completed OBPI
keeps its completed runtime state unless non-anchor proof/evidence drift is
present.

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
- `closeout_ready`
- `closeout_blockers`
- additive per-OBPI runtime fields such as `runtime_state`, `proof_state`,
  `attestation_requirement`, `attestation_state`, `req_proof_state`, `req_proof_inputs`,
  `anchor_state`, `anchor_commit`, `current_head`, `anchor_issues`,
  `anchor_drift_files`, `tracked_defects`, and `issue_details`
- related additive fields

If an OBPI brief records a `## Tracked Defects` section, the corresponding
closeout blockers carry those linked `GHI-*` refs so summary drilldowns keep
defect-level traceability without requiring live GitHub access.

---

## Example

```bash
uv run gz status
uv run gz status --table
uv run gz status --show-gates
uv run gz status --json
```

Table output excerpt (captured 2026-03-08):

```text
ADR Status
+------------------------------------------------------------------------------+
|ADR                         |Life     |Lane | OBPI|Unit     |QC     |Checks   |
|----------------------------+---------+-----+-----+---------+-------+---------|
|ADR-0.1.0                   |Pending  |LITE |  0/1|PENDING  |PENDING|O,T      |
|ADR-0.2.0                   |Completed|HEAVY|  3/3|COMPLETED|READY  |-        |
+------------------------------------------------------------------------------+
Checks legend: O=OBPI completion, T=TDD, D=Docs, B=BDD, H=Human attestation
```

The table uses compact cell padding so more ADR identifier text stays visible in the default terminal width. If an identifier still exceeds the available width, the `ADR` column folds it across lines instead of truncating it with an ellipsis.
