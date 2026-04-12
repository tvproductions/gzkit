# gz check

Run full quality checks (lint, typecheck, test) and advisory drift detection in a single pass.

## Usage

```bash
gz check [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output results as JSON to stdout |

## Description

Runs the complete quality assurance suite: linting with Ruff, format check, static type checking with ty, unit tests with unittest, Behave scenarios, skill audit, parity check, readiness audit, CLI documentation audit, and preflight scan for stale pipeline markers and orphan plan-audit receipts. After all blocking checks complete, runs advisory drift detection using the same engine as `gz drift`.

The `CLI audit` and `Preflight` steps catch workflow-integrity drift that would otherwise go undetected — a new subcommand missing from the operator runbook, or stale artifacts left behind from a previous pipeline session — and apply self-healing pressure on every canonical quality run.

Drift findings are advisory — they appear as warnings but do not affect the exit code. This surfaces spec-test-code drift early without blocking the development workflow.

## Advisory Drift Output

When drift exists, `gz check` appends an advisory section after the blocking check results:

```text
  ✓ Lint
  ✓ Format
  ✓ Typecheck
  ✓ Test

✓ All checks passed.

⚠ Advisory: spec-test-code drift detected
  Unlinked specs (REQs with no test):
    advisory  REQ-0.1.0-01-01
  Total: 1 finding(s) (advisory — does not affect exit code)
```

## JSON Output

`gz check --json` includes a `drift` object with `advisory: true`:

```json
{
  "success": true,
  "checks": {
    "Lint": true,
    "Format": true,
    "Typecheck": true,
    "Test": true
  },
  "drift": {
    "advisory": true,
    "has_drift": true,
    "unlinked_specs": ["REQ-0.1.0-01-01"],
    "orphan_tests": [],
    "unjustified_code_changes": [],
    "total_drift_count": 1,
    "scan_timestamp": "2026-03-27T00:00:00+00:00"
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All blocking checks passed (drift is advisory, does not affect exit code) |
| 1 | One or more blocking checks failed |
