# gz arb coverage

Run `coverage` via ARB and emit a step receipt.

---

## Usage

```bash
gz arb coverage [ARGS...]
```

Runs coverage.py under the ARB step wrapper. Forwards every argument directly
to coverage.

---

## Options

| Option | Description |
|--------|-------------|
| `argv` | Arguments to forward to coverage |

---

## Examples

```bash
gz arb coverage run -m unittest discover -s tests -t .
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
  `.gzkit/rules/attestation-enrichment.md`.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz test`](test.md) — unwrapped test runner
- Rule: `.gzkit/rules/arb.md`
