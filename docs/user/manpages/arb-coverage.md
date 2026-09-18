# gz arb coverage

Run `coverage` via ARB and emit a step receipt.

---

## Usage

```bash
gz arb coverage [ARGS...]
```

With no arguments, runs the canonical full-suite coverage measurement — the
parallel runner with coverage tracing, read from `CANONICAL_STEP_COMMANDS["coverage"]`
— and emits the `coverage` receipt `gz arb validate` accepts. With arguments, forwards
them to coverage.py under the ARB step wrapper (for example `report --fail-under=40`
against the data file the canonical run wrote).

---

## Options

| Option | Description |
|--------|-------------|
| `argv` | Arguments to forward to coverage; omit for the canonical run |

---

## Examples

```bash
gz arb coverage
gz arb coverage report --fail-under=40
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | coverage run succeeded; receipt created |
| 1 | coverage reported a failure (e.g. fail-under breached); receipt created |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.step_receipt.v1`
- Prefix: `arb-step-coverage-<timestamp>`
- Canonical for attestation claim "Coverage floor" per
  `AGENTS.md` § Attestation.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz test`](test.md) — unwrapped test runner
- Rule: `AGENTS.md` § Attestation (binding) / `docs/governance/arb-middleware.md` (deep-dive)
