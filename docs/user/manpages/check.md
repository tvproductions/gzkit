# gz check

Run the per-change quality gate (lint, typecheck, validators, the tests the change touches) and advisory drift detection in a single pass. `--full` adds the whole unit tier, Behave, the docs build, preflight and the guard-canary sweep: the CI, release and chore sweep.

## Usage

```bash
gz check [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output results as JSON to stdout |
| `--full` | Full sweep: the default steps plus `Test`, `Behave`, `Docs build`, `Preflight` and `Guard canary sweep`. CI runs it on every code push |
| `--reuse-verified` | Skip the run when this exact staged tree already passed a check covering the requested scope. Used by the pre-push gate |

### Default scope: the per-change gate

Plain `gz check` runs the `change` scope declared in `src/gzkit/check_step_scopes.json`, which ships
inside the gzkit package, so every project that installs gzkit runs this gate:
lint, format, typecheck, every validator, the smoke tier, and `Test (changed)`,
the tests the change touches. It drops `Test` (the whole unit tier), `Behave`,
`Docs build`, `Preflight` and `Guard canary sweep` (GHI #1088, #1191). The
pre-push hook runs this scope.

`Test (changed)` selects test modules two ways: a changed test module exactly,
and, for a changed production module, every test module whose filename contains
its stem. The change is the working tree against `HEAD`, untracked files, and
the working tree against the upstream branch, so the selection holds at push
time when the change is already committed. The name match is a heuristic, not a
dependency graph: it misses a test that exercises a module it is not named
after. The whole unit tier is what proves the tree, and it runs under `--full`.

Measured 2026-10-11 on a 10-core host (a dated record): the whole unit tier took
117 s inside the gate, and every other default step together took 16 s.

### `--full`

Runs every registered step. CI runs it on every code push, `gz chores run
quality-check` runs it as a chore, and it is the sweep to run before a release.
Heavy-lane Gate 4 evidence comes from its own canonical behave invocation, not
from this sweep, and Gate 2 at OBPI completion is `gz test`.

`Guard canary sweep` applies every reviewed mutant in `data/guard_canaries.json`
to an isolated copy of the tree and requires its designated test to fail. It
exits 3 when a mutant is not killed. A project with no canary registry has
nothing to sweep.

The `--fast` flag was retired on 2026-10-11 (GHI #1191): the default scope took
its shape, so it named nothing the default did not.

### `--reuse-verified`

Skips the run when this exact **staged tree** already passed a check covering the
requested scope (GHI #835). A default-scope or `--full` pass satisfies the default
scope; only a `--full` pass satisfies `--full --reuse-verified`, because a
default-scope pass never ran the full tier. Without it a fix pays the gate twice: once when it is verified,
then again when `git push` fires the pre-push gate over a tree that has not
changed. For every step that reads only the tree, the second run cannot reach a
different verdict. The commit-trailer checks read the commits being pushed, which
the fingerprint does not hash, so a matching tree whose pushed commits lack a
required trailer is not skipped: the gate runs and reports them (GHI #1017).

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

Runs the per-change quality checks: linting with Ruff, format check, static type checking with ty, the unit tests the change touches, the smoke tier, skill audit, parity check, readiness audit, CLI documentation audit and surface-fidelity validation. `--full` adds the whole unit tier, a strict `mkdocs build --strict` docs build (skipped when the project ships no `mkdocs.yml`), Behave scenarios, the guard-canary sweep and the preflight scan for stale pipeline markers and orphan plan-audit receipts. After all blocking checks complete, runs advisory drift detection using the same engine as `gz drift`.

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
  ✓ Test (changed)

✓ All per-change checks passed. (Behave, Docs build, Guard canary sweep, Preflight, Test are full-tier scope: run `gz check --full` in CI and before a release)

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
    "Test (changed)": true
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
