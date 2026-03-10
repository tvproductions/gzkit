# gz register-adrs

Register ADR packages that exist in canon but are missing from ledger state.

---

## Usage

```bash
gz register-adrs [ADR-ID ...] [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `ADR-ID ...` | positional | Optional ADR ids to reconcile; when omitted, scans all eligible ADR packages |
| `--lane` | `lite` or `heavy` | Default lane when ADR metadata does not declare one |
| `--pool-only/--all` | flag | Register pool ADRs only (default) or all ADRs |
| `--dry-run` | flag | Show registration actions without writing ledger events |

---

## What It Does

1. Scans existing ADR files under the configured design root.
2. Parses ADR IDs from frontmatter (`id:`) or header fallback.
3. Filters to named ADR packages when `ADR-ID` arguments are supplied.
4. Filters to pool ADRs by default (`--all` includes non-pool ADRs too).
5. Checks which ADRs are already represented in ledger state.
6. Appends `adr_created` events for missing ADRs only.
7. Scans linked `obpis/` files beneath the selected ADR packages and appends
   `obpi_created` events for missing OBPIs only.

---

## Examples

```bash
# Preview missing ADR registrations
gz register-adrs --dry-run

# Record missing ADRs and linked OBPIs in ledger
gz register-adrs

# Include non-pool ADRs too
gz register-adrs --all

# Repair one promoted ADR package without touching unrelated work
gz register-adrs ADR-0.10.0-obpi-runtime-surface --all
```
