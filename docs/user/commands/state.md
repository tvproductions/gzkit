# gz state

Query ledger artifact relationships and derived ADR semantics.

---

## Usage

```bash
gz state [--json] [--blocked] [--ready] [--repair]
```

---

## Filters

- `--blocked`: show unattested artifacts.
- `--ready`: show ADRs that are genuinely ready for attestation.

`--ready` means:

- ADR is unattested, and
- prerequisite gates required by lane are satisfied.

It is not just "pending attestation".

---

## Repair Mode

`--repair` force-reconciles all OBPI frontmatter status fields from
ledger-derived state. This is the operator recovery tool for restoring
consistency after drift between frontmatter (L3 cache) and the ledger
(L2 authority).

**Behavior:**

- Scans all OBPI brief files under the design root.
- Compares each brief's frontmatter `status` to ledger-derived state.
- Updates frontmatter where it disagrees with the ledger:
    - Ledger says completed -> frontmatter set to `Completed`.
    - Ledger says withdrawn -> frontmatter set to `Abandoned`.
    - No definitive ledger state -> frontmatter left unchanged.
- Reports what changed (human-readable table by default, JSON with `--json`).
- Idempotent: running twice produces no changes on the second run.
- Works after `git clone` with no dependency on L3 caches or markers.

**JSON output format:**

```json
{
  "changes": [
    {
      "obpi_id": "OBPI-0.1.0-01",
      "file": "docs/design/adr/ADR-0.1.0/obpis/OBPI-0.1.0-01-feature.md",
      "old_status": "Draft",
      "new_status": "Completed"
    }
  ],
  "total": 1
}
```

**Exit codes:**

- `0`: Success (repairs applied or already aligned).
- `1`: Configuration or initialization error.

---

## Derived ADR Fields

ADR entries include additive derived semantics (for example `lifecycle_status`, `closeout_phase`, `attestation_term`) based on ledger events.

---

## Task Data in JSON Output

When tasks exist for an OBPI, `--json` output includes a `task_summary` object
on that OBPI's entry with counts by status and the lane's tracing policy:

```json
{
  "OBPI-0.20.0-01": {
    "type": "obpi",
    "parent": "ADR-0.20.0",
    "task_summary": {
      "total": 3,
      "pending": 0,
      "in_progress": 1,
      "completed": 1,
      "blocked": 0,
      "escalated": 1,
      "tracing_policy": "required"
    }
  }
}
```

Task data does not appear when no tasks exist (backward compatible).

---

## Example

```bash
uv run gz state --ready
uv run gz state --ready --json
uv run gz state --repair
uv run gz state --repair --json
```
