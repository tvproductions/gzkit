# gz arb validate

Validate recent ARB receipts against their JSON schemas.

---

## Usage

```bash
gz arb validate [--limit N] [--json]
```

Loads the most recent N receipts from `artifacts/receipts/` and validates
each against its declared schema. Reports valid/invalid/unknown counts.

---

## Options

| Option | Description |
|--------|-------------|
| `--limit N` | Maximum number of most-recent receipts to validate (default: 50) |
| `--json` | Emit machine-readable JSON summary instead of the Rich report |

---

## Examples

```bash
gz arb validate
gz arb validate --limit 100
gz arb validate --json
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All inspected receipts valid against their schemas |
| 1 | One or more receipts failed validation; details in report |
| 2 | ARB internal error |

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz arb advise`](arb-advise.md) — summarize lint patterns across receipts
- Rule: `AGENTS.md` § Attestation (binding) / `docs/governance/arb-middleware.md` (deep-dive)
