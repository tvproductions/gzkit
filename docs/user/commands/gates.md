# gz gates

Run applicable gates for the current lane and record results in the ledger.

---

## Usage

```bash
gz gates [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--gate` | integer | Run a specific gate (1-5) |
| `--adr` | string | ADR identifier to associate gate results with |

---

## What It Does

1. Resolves the target ADR (uses `--adr` or the single pending ADR)
2. Runs the gates required for the current lane
3. Appends a `gate_checked` event for each gate that runs
4. Exits non-zero if any required gate fails

Gate commands use `.gzkit/manifest.json` when available:

- Gate 2 (TDD): `verification.test`
- Gate 3 (Docs): `verification.docs` or `uv run mkdocs build --strict`
- Gate 4 (BDD): `verification.bdd` or `uv run -m behave features/`

---

## Example

```bash
# Run all required gates for the current lane
gz gates

# Run a specific gate
gz gates --gate 2

# Run gates for a specific ADR
gz gates --adr ADR-0.2.0
```
