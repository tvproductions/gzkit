# gz register-adrs

Register ADR files that exist in canon but are missing from ledger state.

---

## Usage

```bash
gz register-adrs [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--lane` | `lite` or `heavy` | Default lane when ADR metadata does not declare one |
| `--pool-only/--all` | flag | Register pool ADRs only (default) or all ADRs |
| `--dry-run` | flag | Show registration actions without writing ledger events |

---

## What It Does

1. Scans existing ADR files under the configured design root.
2. Parses ADR IDs from frontmatter (`id:`) or header fallback.
3. Filters to pool ADRs by default (`--all` includes non-pool ADRs too).
4. Checks which ADRs are already represented in ledger state.
5. Appends `adr_created` events for missing ADRs only.

---

## Examples

```bash
# Preview missing ADR registrations
gz register-adrs --dry-run

# Record missing ADRs in ledger
gz register-adrs

# Include non-pool ADRs too
gz register-adrs --all
```
