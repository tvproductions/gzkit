# gz arb ty

Run `uvx ty` via ARB and emit a step receipt.

---

## Usage

```bash
gz arb ty [ARGS...]
```

Runs the ty type checker under the ARB step wrapper. Forwards every argument
after `ty` directly to the checker. Prefer [`gz arb typecheck`](arb-typecheck.md)
for Heavy-lane attestation so the receipt scope cannot drift from the
governance gate.

---

## Options

| Option | Description |
|--------|-------------|
| `argv` | Arguments to forward to ty |

---

## Examples

```bash
gz arb ty check .
gz arb ty check src
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | ty clean; receipt created |
| 1 | ty reported diagnostics; receipt created |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.step_receipt.v1`
- Prefix: `arb-step-ty-<timestamp>`

---

## See Also

- [`gz arb typecheck`](arb-typecheck.md) — canonical wrapper locked to `gz typecheck` scope
- [`gz typecheck`](typecheck.md) — unwrapped type checker
- GHI #199 — scope-divergence rationale for preferring `arb typecheck`
