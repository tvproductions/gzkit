# gz adr audit-check

Verify linked OBPIs for one ADR are completed and include implementation evidence.

---

## Usage

```bash
gz adr audit-check <ADR-ID> [--json]
```

---

## What It Checks

- ADR-to-OBPI linkage from ledger and artifact metadata
- OBPI completion markers (`status: Completed` and/or `**Brief Status:** Completed`)
- Presence of non-placeholder implementation summary evidence

Returns explicit missing-proof findings and exits non-zero on failure.

---

## Example

```bash
uv run gz adr audit-check ADR-0.3.0
```
