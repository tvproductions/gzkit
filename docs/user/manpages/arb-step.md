# gz arb step

Wrap an arbitrary command and emit a schema-validated step receipt.

---

## Usage

```bash
gz arb step --name <label> [--soft-fail] [--max-output-chars N] -- <command> [ARGS...]
```

Runs the given command, captures stdout/stderr tail, duration, and exit code,
then writes a step receipt to `artifacts/receipts/`. Use this when no
dedicated wrapper (ruff / ty / typecheck / coverage) exists for your QA step.

---

## Options

| Option | Description |
|--------|-------------|
| `--name` | Logical step name for the receipt (required) |
| `--soft-fail` | Emit the receipt but return exit 0 even on failure |
| `--max-output-chars N` | Characters retained per stdout/stderr stream (default: 8000); negative values retain all output, zero retains none |
| `argv` | Command and arguments after `--` |

---

## Examples

```bash
gz arb step --name unittest -- uv run -m unittest -q
gz arb step --name mkdocs -- uv run mkdocs build --strict
gz arb step --name review --max-output-chars -1 -- claude --print "Review the supplied acceptance evidence."
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Wrapped command succeeded; receipt created |
| Other command status | Wrapped command exit status is propagated; receipt created |
| 2 | ARB internal error |

---

## Receipt

- Schema: `gzkit.arb.step_receipt.v1` (`data/schemas/arb_step_receipt.schema.json`)
- Prefix: `arb-step-<name>-<timestamp>`
- Canonical for attestation claim "Tests pass" / "Docs build clean" via
  `arb-step-unittest-*` and `arb-step-mkdocs-*` per
  `AGENTS.md` § Attestation.

---

## See Also

- [`gz arb`](arb.md) — ARB parent reference
- [`gz arb typecheck`](arb-typecheck.md) — canonical typecheck wrapper
- Rule: `AGENTS.md` § Attestation (binding) / `docs/governance/arb-middleware.md` (deep-dive)
