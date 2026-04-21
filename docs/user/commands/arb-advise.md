# gz arb advise

Summarize recent ARB receipts into actionable recommendations.

---

## Usage

```bash
gz arb advise [--limit N] [--json]
```

Aggregates recent lint receipts, counts rule frequencies, and emits
guardrail-tuning recommendations (which ruff rules are firing often enough
to consider promoting to mechanical enforcement, which are likely noise).

---

## Options

| Option | Description |
|--------|-------------|
| `--limit N` | Maximum number of most-recent receipts to summarize (default: 50) |
| `--json` | Emit machine-readable JSON instead of the Rich report |

---

## Examples

```bash
gz arb advise
gz arb advise --limit 10
gz arb advise --json
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Advice report generated |
| 1 | No receipts available to advise over |
| 2 | ARB internal error |

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz arb patterns`](arb-patterns.md) — extract anti-pattern catalog from receipts
- [`gz arb validate`](arb-validate.md) — schema-validate receipts
- Rule: `.gzkit/rules/attestation-enrichment.md`
