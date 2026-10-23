# gz arb ruff

Run ruff check via ARB and emit a schema-validated lint receipt.

---

## Usage

```bash
gz arb ruff [PATHS...] [--fix] [--soft-fail]
```

Runs the locked Ruff (`uv run ruff check`) against the given paths (defaults to `.`), judges the
findings against `data/ruff_baseline.json` as `gz lint` does, and writes a lint receipt to
`artifacts/receipts/`. Ruff selects every rule (RO-9 tranche 4), so the receipt records only the
findings the baseline does not hold, and each row their findings no longer fill; a tree with no
baseline records every finding. The receipt is
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
| 0 | No finding outside the baseline; receipt created |
| 1 | A finding the baseline does not hold, or a row to lower; receipt created with them |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.lint_receipt.v1` (`data/schemas/arb_lint_receipt.schema.json`)
- Prefix: `arb-ruff-<timestamp>`
- Canonical for attestation claim "Lint clean" per `AGENTS.md` § Attestation.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz lint`](lint.md) — unwrapped lint runner
- Rule: `AGENTS.md` § Attestation (binding) / `docs/governance/arb-middleware.md` (deep-dive)
