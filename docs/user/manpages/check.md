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
| `--fast` | Inner-loop scope: run every lint/type/governance step, plus only the tests the working tree touches. Skips `Test`, `Behave`, and `Docs build`. Never satisfies the pre-push gate |
| `--reuse-verified` | Skip the run when this exact working-tree content already passed a full check. Used by the pre-push gate |

### `--fast`

Runs the full step list minus the three expensive steps, and substitutes a
`Test (changed)` step that runs only the test modules the working tree touches.

Measured 2026-08-22 on a 10-core host, against a 148 s full run: `Test` 44 s,
`Behave` 33 s, `Docs build` 4 s. Every other step stays, because the whole
remainder is cheaper than any one of the three and it is where the governance
value lives.

**A `--fast` pass never records a verified fingerprint**, so `--reuse-verified`
cannot be satisfied by one and the pre-push gate still runs in full. The test
selection is a name-match heuristic, not a dependency graph — it will miss a test
that exercises a module it is not named after. That is a convenience for the
inner loop, never a claim of coverage, and the output says so.

### `--reuse-verified`

Skips the run when this exact working-tree **content** already passed a full
check (GHI #835). Without it a fix pays the full run twice: once when it is
verified, then again when `git push` fires the pre-push gate over a tree that has
not changed. The second run cannot reach a different verdict.

The fingerprint is content-addressed, deliberately not `HEAD`: a commit is
created between the two runs, so keying on the commit would mean the skip never
fires. It is taken by staging the worktree into a throwaway index and reading
that index's tree hash, so `.gitignore` is honoured, staged/unstaged/untracked
content all count, and the real index is never touched.

Fail-open by construction: any git failure yields no fingerprint, no fingerprint
ever matches, and the gate runs. A fingerprint mechanism that failed closed would
refuse pushes on a repository it merely could not read.

## Description

Runs the complete quality assurance suite: linting with Ruff, format check, static type checking with ty, unit tests with unittest, Behave scenarios, a strict `mkdocs build --strict` docs build (skipped when the project ships no `mkdocs.yml`), skill audit, parity check, readiness audit, CLI documentation audit, surface-fidelity validation, and preflight scan for stale pipeline markers and orphan plan-audit receipts. After all blocking checks complete, runs advisory drift detection using the same engine as `gz drift`.

The `Surface fidelity` step runs `gz validate --surface-fidelity` to verify all four surface-fidelity invariants (ADR-0.0.33-05).

The `Lock-exchange coupling` step runs `gz validate --lock-exchange-coupling` to
enforce the token-block discipline: every `obpi_lock_released` event in the
ledger (post-OBPI-02 cutover) must carry a valid `handoff_path` and satisfy
Sub-Invariant 2's minimum-information rule (ADR-0.0.41 / OBPI-0.0.41-04).

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
