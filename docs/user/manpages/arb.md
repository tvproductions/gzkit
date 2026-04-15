# gz-arb(1) — ARB self-reporting middleware

## NAME

**gz arb** — wrap QA commands and emit schema-validated receipts

## SYNOPSIS

```text
gz arb ruff [--fix] [--soft-fail] [PATHS...]
gz arb step --name NAME [--soft-fail] -- COMMAND [ARGS...]
gz arb ty COMMAND [ARGS...]
gz arb coverage COMMAND [ARGS...]
gz arb validate [--limit N] [--json]
gz arb advise [--limit N] [--json]
gz arb patterns [--limit N] [--compact] [--json]
```

## DESCRIPTION

The **arb** command group wraps QA commands (ruff, ty, unittest, coverage) and emits schema-validated JSON receipts to `artifacts/receipts/`. These receipts are the canonical attestation evidence cited in Heavy-lane OBPI closeout claims.

ARB's purpose is to reduce the rate of agent-authored defects (first-pass failures) by aggregating recurring lint patterns into actionable guardrail recommendations — not to generate workflow noise.

## VERBS

### ruff

Run `ruff check` via ARB and emit a lint receipt.

```text
gz arb ruff [--fix] [--soft-fail] [PATHS...]
```

**Options:**

- `--fix` — Apply ruff auto-fixes
- `--soft-fail` — Emit receipt but always return exit 0 (measurement-only mode)

**Example:**

```bash
gz arb ruff src/gzkit
```

### step

Wrap an arbitrary command and emit a step receipt.

```text
gz arb step --name NAME [--soft-fail] -- COMMAND [ARGS...]
```

**Example:**

```bash
gz arb step --name unittest -- uv run -m unittest
```

### ty, coverage

Dedicated wrappers for common step invocations.

```bash
gz arb ty check .
gz arb coverage run -m unittest discover
```

### validate

Validate recent receipts against `gzkit.arb.lint_receipt.v1` / `gzkit.arb.step_receipt.v1`.

```text
gz arb validate [--limit N] [--json]
```

### advise

Summarize recent lint receipts into guardrail tuning recommendations.

```text
gz arb advise [--limit N] [--json]
```

### patterns

Extract recurring anti-patterns from receipts as Markdown, compact summary, or JSON.

```text
gz arb patterns [--limit N] [--compact] [--json]
```

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Command succeeded; receipt created |
| 1 | Command failed; receipt created with findings |
| 2 | ARB internal error (receipt directory, config, invalid step) |

## RECEIPTS

Receipts are written to the directory resolved by:

1. `GZKIT_ARB_RECEIPTS_ROOT` environment variable (absolute path, used by tests)
2. `arb.receipts_root` from `.gzkit.json` (default: `artifacts/receipts`)

Each receipt is a JSON file named by `run_id`. Schemas live under `data/schemas/`:

- `arb_lint_receipt.schema.json` (`$id: gzkit.arb.lint_receipt.schema.json`)
- `arb_step_receipt.schema.json` (`$id: gzkit.arb.step_receipt.schema.json`)

## SEE ALSO

- `gz check` — full quality pass (lint, typecheck, test, drift)
- `gz drift` — spec-test-code drift scanner
- `.gzkit/rules/arb.md` — ARB rule and concept reference
- `.gzkit/rules/attestation-enrichment.md` — attestation receipt contract

## HISTORY

Absorbed from `airlineops/src/opsdev/arb/` under OBPI-0.25.0-33 (2026-04-14), which closed a governance vacuum where `.gzkit/rules/arb.md` documented a fully-working `gz arb` surface that did not exist in gzkit. See the ADR-0.25.0 closeout record for the forensic trace.
