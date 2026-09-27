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
2. Runs Gate 2 using the manifest `verification.test` command (default `uv run gz test`)
3. Appends a Gate 2 `gate_checked` event to the ledger
4. When the tests pass, runs the eval delta against `data/eval/` baselines and appends a second Gate 2 event (`eval-delta`); with no datasets or no baselines it records a skip
5. Exits non-zero if the tests fail or the eval delta finds a regression

---

## Example

```bash
# Run Gate 2 for the current ADR
gz implement

# Run Gate 2 for a specific ADR
gz implement --adr ADR-0.2.0
```
