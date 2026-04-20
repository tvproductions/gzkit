# gz arb ruff

Run ruff check via ARB and emit a schema-validated lint receipt.

---

## Usage

```bash
gz arb ruff [PATHS...] [--fix] [--soft-fail]
```

Runs `uvx ruff check` against the given paths (defaults to `.`), captures the
findings, and writes a lint receipt to `artifacts/receipts/`. The receipt is
the canonical attestation evidence for any Heavy-lane claim of lint cleanliness.

---

## Options

| Option | Description |
|--------|-------------|
| `paths` | Paths to check (default: `.`) |
| `--fix` | Apply ruff auto-fixes before capturing the receipt |
| `--soft-fail` | Emit the receipt but return exit 0 even on findings (measurement mode) |

---

## Examples

```bash
gz arb ruff src/gzkit
gz arb ruff --fix src tests
gz arb ruff --soft-fail src
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Ruff clean; receipt created |
| 1 | Ruff reported findings; receipt created with findings |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.lint_receipt.v1` (`data/schemas/arb_lint_receipt.schema.json`)
- Prefix: `arb-ruff-<timestamp>`
- Canonical for attestation claim "Lint clean" per `.gzkit/rules/attestation-enrichment.md`.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz lint`](lint.md) — unwrapped lint runner
- Rule: `.gzkit/rules/arb.md`
