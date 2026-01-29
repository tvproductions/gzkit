# gz implement

Run Gate 2 (TDD) and record results in the ledger.

---

## Usage

```bash
gz implement [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--adr` | string | ADR identifier to associate gate results with |

---

## What It Does

1. Resolves the target ADR (uses `--adr` or the single pending ADR)
2. Runs Gate 2 using the manifest test command
3. Appends a `gate_checked` event to the ledger
4. Exits non-zero if Gate 2 fails

---

## Example

```bash
# Run Gate 2 for the current ADR
gz implement

# Run Gate 2 for a specific ADR
gz implement --adr ADR-0.2.0
```
