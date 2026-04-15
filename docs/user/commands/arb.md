# gz arb

ARB (Agent Self-Reporting) middleware. Wraps QA commands (ruff, ty, unittest, coverage) and emits schema-validated JSON receipts for attestation evidence.

## Usage

```bash
gz arb <verb> [OPTIONS]
```

## Verbs

| Verb | Description |
|------|-------------|
| `ruff` | Run ruff via ARB and emit a lint receipt |
| `step` | Wrap an arbitrary command and emit a step receipt |
| `ty` | Run `uvx ty` via ARB step wrapper |
| `coverage` | Run `coverage` via ARB step wrapper |
| `validate` | Validate recent receipts against their JSON schemas |
| `advise` | Summarize recent receipts into actionable recommendations |
| `patterns` | Extract recurring anti-patterns from receipts |

## Exit Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| **0** | Command succeeded; receipt created | — |
| **1** | Command failed; receipt created with findings | Fix the underlying failure |
| **2** | ARB internal error | Check receipt directory and configuration |

## Description

ARB intercepts QA command execution and records:

- Execution metadata (timestamp, duration, environment)
- Input/output (command, arguments, exit code, stderr/stdout)
- Structured findings (linting violations, type errors, test failures)
- Receipt artifacts (JSON schema-validated, persistent)

Receipts are written to `artifacts/receipts/` (configurable via `arb.receipts_root` in `.gzkit.json`) and are the canonical attestation evidence cited in Heavy-lane OBPI closeout claims. See `.gzkit/rules/arb.md` for the rule contract and `.gzkit/rules/attestation-enrichment.md` for the receipt-ID requirement.

## Examples

### Wrap a Ruff Run

```bash
gz arb ruff src/gzkit
gz arb ruff --fix src tests
gz arb ruff --soft-fail src
```

### Wrap an Arbitrary Step

```bash
gz arb step --name unittest -- uv run -m unittest
gz arb step --name mkdocs -- uv run mkdocs build --strict
```

### Dedicated Wrappers

```bash
gz arb ty check .
gz arb coverage run -m unittest discover -s tests -t .
```

### Validate Analyze Receipts

```bash
gz arb validate                # Default: scan last 50 receipts
gz arb validate --limit 100    # Scan last 100 receipts
gz arb validate --json         # Machine-readable output
```

### Recommendations from Recent Receipts

```bash
gz arb advise                  # Default: last 50 receipts
gz arb advise --limit 10       # Scan only the last 10
gz arb advise --json           # JSON output
```

### Pattern Extraction

```bash
gz arb patterns                # Full Markdown report
gz arb patterns --compact      # Single-line summary
gz arb patterns --json         # Machine-readable
```

## Receipt Schemas

ARB emits two schema variants, both stored under `data/schemas/`:

| Schema | ID | Emitted by |
|--------|----|-----------|
| `arb_lint_receipt.schema.json` | `gzkit.arb.lint_receipt.v1` | `gz arb ruff` |
| `arb_step_receipt.schema.json` | `gzkit.arb.step_receipt.v1` | `gz arb step`, `gz arb ty`, `gz arb coverage` |

All receipts include: `schema`, `run_id`, `timestamp_utc`, `git` (commit/branch/dirty), `exit_status`. Lint receipts additionally carry `tool`, `findings`, and `findings_total`. Step receipts additionally carry `step.name`, `step.command`, `duration_ms`, `stdout_tail`, and `stderr_tail`.

## Related

- Rule: `.gzkit/rules/arb.md`
- Attestation contract: `.gzkit/rules/attestation-enrichment.md`
- Manpage: `docs/user/manpages/arb.md`
- Commands index: `docs/user/commands/index.md`
