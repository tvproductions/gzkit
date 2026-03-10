# gz adr status

Show focused OBPI progress, lifecycle status, and gate readiness for one ADR.

---

## Usage

```bash
gz adr status <ADR-ID> [--json] [--show-gates]
```

`<ADR-ID>` accepts full IDs (for example `ADR-0.5.0-skill-lifecycle-governance`) and
unique SemVer prefixes (for example `0.5.0` or `ADR-0.5.0`) when exactly one ADR ID
starts with that prefix.

---

## Runtime Behavior

`gz adr status` is ledger-first and additive, with OBPI completion as the primary progress unit.

It keeps existing compatibility fields and adds derived semantics:

- `obpis` (linked OBPI status rows including `runtime_state`, `proof_state`,
  `attestation_requirement`, `attestation_state`, `req_proof_state`,
  `req_proof_inputs`, and `issues`)
- `obpi_summary` (`total`, `completed`, `incomplete`, `unit_status`, `outstanding_ids`)
- `lane`
- `lifecycle_status`
- `closeout_phase`
- `attestation_term`
- `closeout_initiated`
- `validated`
- `closeout_ready`
- `closeout_blockers`
- `gate4_na_reason` (when applicable)

Default text output is OBPI-first and shows both closeout readiness and QC readiness.
QC readiness is fail-closed on OBPI completion: when linked OBPIs exist and unit status is not
`completed`, readiness is `PENDING` with `OBPI completion` in pending checkpoints.
Use `--show-gates` for full gate-by-gate diagnostics.

Lifecycle is derived from `attested`, `closeout_initiated`, and `audit_receipt_emitted` events.
OBPI-scoped receipts that carry `adr_completion: not_completed` remain accounting artifacts and do
not set ADR lifecycle to `Validated`.
If linked OBPIs exist but OBPI unit status is not `completed`, lifecycle is reported as `Pending`
even when ledger attestation/receipt events exist.

OBPI rows are resolved from linked ledger children plus on-disk briefs. Missing linked files are
reported explicitly so gaps are visible in a single ADR view.
Closeout readiness reuses the same OBPI runtime issues and reports `BLOCKED` until every linked
OBPI is closeout-ready.
The runtime model is additive and fail-closed:

- legacy receipts without explicit `req_proof_inputs` are backfilled from substantive brief `Key Proof`
- missing or placeholder proof/evidence keeps the OBPI in a non-complete runtime state
- heavy/foundation completion requires human-attestation proof before `attested_completed`

---

## Example

```bash
uv run gz adr status ADR-0.3.0
uv run gz adr status ADR-0.3.0 --show-gates
uv run gz adr status ADR-0.3.0 --json
uv run gz adr status 0.5.0
```
