# gz arb typecheck

Canonical Heavy-lane type-check receipt — wraps the exact command `gz typecheck` invokes.

---

## Usage

```bash
gz arb typecheck
```

Wraps the same ty invocation `gz typecheck` and `gz closeout` use. This locks
the ARB receipt scope to the governance gate's scope so attestation evidence
cannot diverge from the canonical gate output. Prefer this over
`gz arb ty check <custom-scope>` for Heavy-lane attestation evidence.

---

## Examples

```bash
gz arb typecheck
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | ty clean against canonical scope; receipt created |
| 1 | ty reported diagnostics; receipt created |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.step_receipt.v1`
- Prefix: `arb-step-typecheck-<timestamp>`
- Canonical for attestation claim "Type check clean" per
  `AGENTS.md` § Attestation.

---

## See Also

- [`gz typecheck`](typecheck.md) — unwrapped gate runner
- [`gz arb ty`](arb-ty.md) — raw ty wrapper for non-canonical scopes
- GHI #199 — why canonical matters for receipts
