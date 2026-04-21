# gz arb patterns

Extract recurring anti-patterns from ARB receipts.

---

## Usage

```bash
gz arb patterns [--limit N] [--compact] [--json]
```

Aggregates recurring lint rules across recent receipts and emits pattern
candidates with guidance text suitable for agent instructions (additions to
`.gzkit/rules/` or skill bodies).

---

## Options

| Option | Description |
|--------|-------------|
| `--limit N` | Maximum number of most-recent receipts to scan (default: 500) |
| `--compact` | Emit a single-line summary instead of the full Markdown report |
| `--json` | Emit machine-readable JSON instead of the Markdown report |

---

## Examples

```bash
gz arb patterns
gz arb patterns --compact
gz arb patterns --json
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Pattern report generated |
| 1 | No receipts available to scan |
| 2 | ARB internal error |

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz arb advise`](arb-advise.md) — per-rule recommendations
- Rule: `.gzkit/rules/attestation-enrichment.md`
