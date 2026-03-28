# gz state

Query ledger artifact relationships and derived ADR semantics.

---

## Usage

```bash
gz state [--json] [--blocked] [--ready]
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
```
