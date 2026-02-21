# gz adr status

Show focused OBPI progress, lifecycle status, and gate readiness for one ADR.

---

## Usage

```bash
gz adr status <ADR-ID> [--json] [--show-gates]
```

---

## Runtime Behavior

`gz adr status` is ledger-first and additive, with OBPI completion as the primary progress unit.

It keeps existing compatibility fields and adds derived semantics:

- `obpis` (linked OBPI status rows: file presence, completion, evidence, and issues)
- `obpi_summary` (`total`, `completed`, `incomplete`, `unit_status`, `outstanding_ids`)
- `lane`
- `lifecycle_status`
- `closeout_phase`
- `attestation_term`
- `closeout_initiated`
- `validated`
- `gate4_na_reason` (when applicable)

Default text output is OBPI-first and shows a summarized QC readiness line.
Use `--show-gates` for full gate-by-gate diagnostics.

Lifecycle is derived from `attested`, `closeout_initiated`, and `audit_receipt_emitted` events.
OBPI-scoped receipts that carry `adr_completion: not_completed` remain accounting artifacts and do
not set ADR lifecycle to `Validated`.
If linked OBPIs exist but OBPI unit status is not `completed`, lifecycle is reported as `Pending`
even when ledger attestation/receipt events exist.

OBPI rows are resolved from linked ledger children plus on-disk briefs. Missing linked files are
reported explicitly so gaps are visible in a single ADR view.

---

## Example

```bash
uv run gz adr status ADR-0.3.0
uv run gz adr status ADR-0.3.0 --show-gates
uv run gz adr status ADR-0.3.0 --json
```
