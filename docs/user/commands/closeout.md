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
- Product proof status table (per-OBPI documentation proof)
- Closeout blockers when any linked OBPI is not closeout-ready
- Generated `ADR-CLOSEOUT-FORM.md` path inside the ADR package
- Linked OBPI evidence paths
- Verification command set for the ADR lane
- Canonical attestation choices
- Heavy-lane Gate 4 command (always required for heavy lane)

If any linked OBPI still has missing proof, canonical drift, or missing
required human-attestation evidence, `gz closeout` prints `BLOCKERS:` and exits
`1` without writing `closeout_initiated`.

### Product Proof Gate

After OBPI completion checks pass, `gz closeout` validates that each OBPI has
at least one form of operator-facing documentation proof:

| Proof Type | Detection Method |
|------------|-----------------|
| `runbook` | OBPI ID or slug keywords found in `docs/user/runbook.md` |
| `command_doc` | Command doc file from OBPI allowed paths exists with >100 chars |
| `docstring` | Public function/class in source files from allowed paths has docstring |

At least one proof type must exist per OBPI. If any OBPI has `MISSING` proof,
closeout exits `1` with a table showing which OBPIs lack proof.

### Defense Brief

After product proof passes, `gz closeout` computes a **Defense Brief** section
that is included in both the `--dry-run` preview and the final
`ADR-CLOSEOUT-FORM.md`. The Defense Brief contains:

| Section | Content |
|---------|---------|
| Closing Arguments | Per-OBPI closing argument text extracted from each brief |
| Product Proof | Per-OBPI proof type and status table |
| Reviewer Assessment | Per-OBPI reviewer verdict from `REVIEW-*.md` artifacts |

The Defense Brief transforms the closeout form from a checklist into a defense
presentation where the completing agent's evidence is laid out for human
judgment.

When closeout succeeds without `--dry-run`, `gz closeout` creates or refreshes
`ADR-CLOSEOUT-FORM.md` beside the ADR file with the current evidence inventory,
Defense Brief, and Gate 5 attestation command.

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
