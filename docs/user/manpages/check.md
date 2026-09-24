# gz check

Run the per-change quality gate (lint, typecheck, unit tests, validators) and advisory drift detection in a single pass. `--full` adds Behave and preflight, the heavy-lane and CI sweep.

## Usage

```bash
gz check [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output results as JSON to stdout |
| `--full` | Full sweep: the default steps plus `Behave` and `Preflight`. Heavy-lane and CI scope; CI runs it on every commit |
| `--fast` | Inner-loop scope: run every lint/type/governance step, plus only the tests the working tree touches. Skips `Test`, `Behave`, and `Docs build`. Never satisfies the pre-push gate |
| `--reuse-verified` | Skip the run when this exact staged tree already passed a check covering the requested scope. Used by the pre-push gate |

`--full` and `--fast` are mutually exclusive.

### Default scope: the per-change gate

Plain `gz check` runs the `change` scope declared in `data/check_step_scopes.json`:
every step except `Behave` and `Preflight`. `AGENTS.md` § Gate Covenant binds the
unit tier to every change and `behave` to heavy-lane OBPI work and CI, never to a
per-change gate (GHI #1088). `Preflight` is a janitorial scan whose verdict tracks
wall-clock age rather than the content being pushed. Both still run under
`--full`, and CI runs `--full` on every commit.

### `--full`

Runs every registered step. Use it for heavy-lane closeout and whenever CI's
verdict is wanted locally. Heavy-lane Gate 4 evidence comes from its own
canonical behave invocation, not from this sweep.

### `--fast`

Runs the full step list minus the three expensive steps, and substitutes a
`Test (changed)` step that runs only the test modules the working tree touches.

Measured 2026-08-22 on a 10-core host, against a 148 s full run: `Test` 44 s,
`Behave` 33 s, `Docs build` 4 s. Every other step stays, because the whole
remainder is cheaper than any one of the three and it is where the governance
value lives.

**A `--fast` pass never records a verified fingerprint**, so `--reuse-verified`
cannot be satisfied by one and the pre-push gate still runs its own scope. The test
selection is a name-match heuristic, not a dependency graph — it will miss a test
that exercises a module it is not named after. That is a convenience for the
inner loop, never a claim of coverage, and the output says so.

### `--reuse-verified`

Skips the run when this exact **staged tree** already passed a check covering the
requested scope (GHI #835). A default-scope or `--full` pass satisfies the default
scope; only a `--full` pass satisfies `--full --reuse-verified`, because a
default-scope pass never ran `Behave`. Without it a fix pays the gate twice: once when it is verified,
then again when `git push` fires the pre-push gate over a tree that has not
changed. The second run cannot reach a different verdict.

**Use it as: `git add -A && uv run gz check && git commit && git push`.** The
staging step is not incidental — it is what makes the skip possible.

The fingerprint is the **index** tree, and both alternatives were tried and
rejected against real measurement:

- `HEAD` fails because a commit is created between verify and push, so it always
  differs while the files do not.
- The **working tree** fails for the mirror reason: `pre-commit` stashes unstaged
  changes while hooks run, so a pre-push hook observes HEAD-plus-staged and never
  the working tree. Measured 2026-08-22 against this repository, where
  `.gzkit/ledger.jsonl` is dirty on essentially every run because governance
  commands append to it — the first implementation fingerprinted the working
  tree, passed all its own tests on clean fixtures, and skipped exactly zero real
  pushes.

A pass is recorded **only when nothing is unstaged or untracked**. The gate runs
against the working tree while the fingerprint names the index tree, and those
are the same object only when the tree is fully staged; recording otherwise would
attest a tree that was never the one tested. When it declines to record, it says
so on stdout.

Fail-open by construction: any git failure yields no fingerprint, no fingerprint
ever matches, and the gate runs. A fingerprint mechanism that failed closed would
refuse pushes on a repository it merely could not read.

## Description

Runs the quality assurance suite: linting with Ruff, format check, static type checking with ty, unit tests with unittest, a strict `mkdocs build --strict` docs build (skipped when the project ships no `mkdocs.yml`), skill audit, parity check, readiness audit, CLI documentation audit and surface-fidelity validation. `--full` adds Behave scenarios and the preflight scan for stale pipeline markers and orphan plan-audit receipts. After all blocking checks complete, runs advisory drift detection using the same engine as `gz drift`.

The `Surface fidelity` step runs `gz validate --surface-fidelity` to verify all four surface-fidelity invariants (ADR-0.0.33-05).

The `Lock-exchange coupling` step runs `gz validate --lock-exchange-coupling` to
enforce the token-block discipline: every `obpi_lock_released` event in the
ledger (post-OBPI-02 cutover) must carry a valid `handoff_path` and satisfy
Sub-Invariant 2's minimum-information rule (ADR-0.0.41 / OBPI-0.0.41-04).

The `CLI audit` and `Preflight` steps catch workflow-integrity drift that would otherwise go undetected — a new subcommand missing from the operator runbook, or stale artifacts left behind from a previous pipeline session — and apply self-healing pressure on every canonical quality run (`Preflight` under `--full`).

Drift findings are advisory — they appear as warnings but do not affect the exit code. This surfaces spec-test-code drift early without blocking the development workflow.

## Advisory Drift Output

When drift exists, `gz check` appends an advisory section after the blocking check results:

```text
  ✓ Lint
  ✓ Format
  ✓ Typecheck
  ✓ Test

✓ All per-change checks passed. (Behave, Preflight are heavy-lane / CI scope: `gz check --full` runs them, and CI runs the full sweep)

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
  "scope": "change",
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
