# gz closeout

Initiate closeout mode for an ADR and record `closeout_initiated` in the ledger.

---

## Usage

```bash
gz closeout <ADR-ID> [--json] [--dry-run]
```

---

## Runtime Behavior

`gz closeout` is fail-closed on linked OBPI runtime proof.
Pool ADRs (`ADR-pool.*`) are blocked from closeout until promoted out of pool.

Output includes:

- Gate 1 ADR path
- OBPI completion summary
- Closeout blockers when any linked OBPI is not closeout-ready
- Generated `ADR-CLOSEOUT-FORM.md` path inside the ADR package
- Linked OBPI evidence paths
- Verification command set for the ADR lane
- Canonical attestation choices
- Heavy-lane Gate 4 command (always required for heavy lane)

If any linked OBPI still has missing proof, canonical drift, or missing
required human-attestation evidence, `gz closeout` prints `BLOCKERS:` and exits
`1` without writing `closeout_initiated`.

When closeout succeeds without `--dry-run`, `gz closeout` creates or refreshes
`ADR-CLOSEOUT-FORM.md` beside the ADR file with the current evidence inventory
and Gate 5 attestation command.

`--json` adds:

- `allowed`
- `blockers`
- `obpi_summary`
- `obpi_rows`
- `next_steps`

It still does not interpret the verification command outcomes themselves.

---

## Canonical Attestation Choices

- `Completed`
- `Completed — Partial: [reason]`
- `Dropped — [reason]`

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable closeout payload |
| `--dry-run` | Show payload without writing ledger event |

---

## Example

```bash
uv run gz closeout ADR-0.10.0 --dry-run
```

```text
Dry run blocked: ADR-0.10.0-obpi-runtime-surface
  Gate 1 (ADR): docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md
  OBPI Completion: 2/3 complete
BLOCKERS:
- OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration: ledger proof of completion is missing
Next steps:
  - uv run gz adr status ADR-0.10.0-obpi-runtime-surface
  - uv run gz adr audit-check ADR-0.10.0-obpi-runtime-surface
  - uv run gz obpi reconcile OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration
```
