# Operator Runbook

This runbook is a proof surface and must match executable runtime behavior.

---

## Operating Model (OBPI-First)

- The atomic unit of delivery is the OBPI (One Brief Per Item).
- ADRs are planning and attestation containers that roll up many OBPIs.
- Daily execution should iterate OBPI-by-OBPI, not wait for end-of-ADR batching.

---

## Loop A: OBPI Increment (Primary Daily Loop)

```bash
# 1) Orientation + parent ADR context
uv run gz status
uv run gz adr status ADR-<X.Y.Z> --json

# 2) Implement one OBPI increment (code + docs as needed)
# 3) Verify this increment
uv run gz implement --adr ADR-<X.Y.Z>
uv run gz gates --gate 3 --adr ADR-<X.Y.Z>   # when docs changed
uv run gz lint

# 4) Update the OBPI brief with substantive implementation evidence
#    (status Completed + concrete summary, not placeholders)

# 5) Record OBPI-scoped receipt evidence on the OBPI itself
uv run gz obpi emit-receipt OBPI-<X.Y.Z-NN>-<slug> --event completed --attestor "<Human Name>" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-<X.Y.Z-NN>.","date":"YYYY-MM-DD"}'
```

---

## Loop B: ADR Closeout (After OBPI Batch Completion)

Run this only when linked OBPIs are complete and evidenced.

```bash
# 1) Reconcile ADR <-> OBPI completeness
uv run gz adr audit-check ADR-<X.Y.Z>

# 2) Closeout presentation (paths/commands only)
uv run gz closeout ADR-<X.Y.Z>

# 3) Human attestation (prerequisites enforced by default)
uv run gz attest ADR-<X.Y.Z> --status completed

# 4) Post-attestation audit (strict)
uv run gz audit ADR-<X.Y.Z>

# 5) Receipt/accounting at ADR scope
uv run gz adr emit-receipt ADR-<X.Y.Z> --event validated --attestor "<Human Name>" --evidence-json '{"scope":"ADR-<X.Y.Z>","date":"YYYY-MM-DD"}'
```

---

## Normal Use Flows (Concrete Example, Captured 2026-02-22)

These are copy/paste examples from this repository using real IDs and current CLI output.

### Flow 1: Daily OBPI Work (In-Progress ADR)

Use an active ADR with incomplete OBPIs:

```bash
uv run gz adr status ADR-0.5.0-skill-lifecycle-governance --json
```

Output excerpt:

```json
{
  "adr": "ADR-0.5.0-skill-lifecycle-governance",
  "lifecycle_status": "Pending",
  "gates": {
    "1": "pass",
    "2": "pending",
    "3": "pending",
    "4": "n/a",
    "5": "pending"
  },
  "obpi_summary": {
    "total": 5,
    "completed": 0,
    "incomplete": 5,
    "unit_status": "pending"
  }
}
```

Run implementation and verification for one increment:

```bash
uv run gz implement --adr ADR-0.5.0-skill-lifecycle-governance
uv run gz gates --gate 3 --adr ADR-0.5.0-skill-lifecycle-governance
uv run gz lint
```

After brief evidence is updated, emit OBPI receipt:

```bash
uv run gz obpi emit-receipt OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity --event completed --attestor "Jeffry Babb" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-0.5.0-05.","date":"2026-02-22"}'
```

### Flow 2: ADR Closeout (OBPIs Completed)

Use an ADR whose OBPIs are completed:

```bash
uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol
```

Output:

```text
ADR audit-check: ADR-0.6.0-pool-promotion-protocol
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.6.0-01-pool-source-contract
  - OBPI-0.6.0-02-promotion-command-lineage
  - OBPI-0.6.0-03-operator-narratives-and-auditability
```

Dry-run closeout and attestation first:

```bash
uv run gz closeout ADR-0.6.0-pool-promotion-protocol --dry-run
uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed --dry-run
```

Closeout dry-run excerpt:

```text
Dry run: no ledger event will be written.
  Would initiate closeout for: ADR-0.6.0-pool-promotion-protocol
  Gate 2 (TDD): uv run -m unittest discover tests
  Gate 3 (Docs): uv run mkdocs build --strict
  Gate 4 (BDD): N/A (features/ not found; Gate 4 is N/A for this repository.)
  Gate 5 (Human): Awaiting explicit attestation
```

Then run non-dry commands and record receipts:

```bash
uv run gz closeout ADR-0.6.0-pool-promotion-protocol
uv run gz attest ADR-0.6.0-pool-promotion-protocol --status completed
uv run gz audit ADR-0.6.0-pool-promotion-protocol
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}'
```

If you want to inspect receipt payloads before writing events:

```bash
uv run gz obpi emit-receipt OBPI-0.6.0-03-operator-narratives-and-auditability --event completed --attestor "Jeffry Babb" --evidence-json '{"attestation":"I attest I understand the completion of OBPI-0.6.0-03.","date":"2026-02-22"}' --dry-run
uv run gz adr emit-receipt ADR-0.6.0-pool-promotion-protocol --event validated --attestor "Jeffry Babb" --evidence-json '{"scope":"ADR-0.6.0-pool-promotion-protocol","date":"2026-02-22"}' --dry-run
```

---

## Verification Checklist (OBPI + ADR)

- `uv run -m unittest discover tests`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run mkdocs build --strict`
- `uv run gz validate --documents`
- `uv run gz cli audit`
- `uv run gz check-config-paths`
- `uv run gz adr audit-check ADR-<X.Y.Z>`
- `uv run gz adr status ADR-<X.Y.Z> --json`
- `uv run gz status --json`

---

## AirlineOps Parity Scan Canonical-Root Rules

When running parity scans, canonical root resolution is deterministic and fail-closed:

1. explicit override (if provided)
2. sibling path `../airlineops`
3. absolute fallback `/Users/jeff/Documents/Code/airlineops`

If none resolve, stop and report blockers. Do not claim parity completion without canonical-root evidence.

---

## Notes

- Do not run `gz audit` pre-attestation.
- Do not use OBPI-scoped receipt emission as a substitute for ADR completion attestation.
- `gz adr emit-receipt` remains available for ADR-level accounting and legacy scoped payload flows.
- For heavy lane without `features/`, Gate 4 is reported N/A with explicit rationale.
- Historical files under `docs/user/reference/**` are archival and may contain legacy command examples; active operator command contracts are in `docs/user/commands/**` and CLI help output.
