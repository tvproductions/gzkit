---
id: OBPI-0.19.0-01-gz-closeout-adr-x-y-z-end-to-end-closeout-pipeline
parent: ADR-0.19.0-closeout-audit-processes
item: 1
lane: Lite
status: Completed
---

# OBPI-0.19.0-01: `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #1 - "OBPI-0.19.0-01: `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline"

**Status:** Completed

## Objective

Transform `closeout_cmd()` from a passive reporter that lists verification steps into an active orchestrator that runs quality gates inline, prompts for human attestation, records the attestation event in the ledger, bumps the project version to match the ADR semver, and marks the ADR as Completed — all within a single command invocation so operators cannot skip intermediate steps.

## Lane

**Lite** — Inherited from parent ADR lane (ledger `adr_created` event for ADR-0.19.0 records lane as `lite`).

> The parent ADR lane is Lite because this work orchestrates existing internal capabilities (gates, attest, version sync) into a pipeline. No new external CLI surface is created — `gz closeout` already exists. The change is behavioral: it runs steps inline instead of listing them.

## Allowed Paths

- `src/gzkit/cli.py` — Contains `closeout_cmd()` (line ~2494), `_closeout_verification_steps()`, `_render_closeout_output()`, `_closeout_result_payload()`, and `_write_adr_closeout_form()` which must be modified to run gates inline and orchestrate attestation
- `src/gzkit/commands/common.py` — Contains `run_command()` helper and `COMMAND_DOCS` registry; may need shared utilities for inline gate execution and attestation prompting
- `tests/test_closeout_pipeline.py` — New test module for end-to-end closeout pipeline coverage including gate execution, attestation recording, version bump, and ADR completion marking

## Denied Paths

- `src/gzkit/ledger.py` — Ledger event schema is reused, not changed (ADR non-goal)
- `.gzkit/ledger.jsonl` — Never edited manually
- `src/gzkit/commands/audit.py` — Audit pipeline is OBPI-02 scope
- `docs/user/commands/closeout.md` — Docs update is a separate concern unless output format changes
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `closeout_cmd()` MUST execute each verification step returned by `_closeout_verification_steps()` via `run_command()` inline, not merely list them in output. Each gate result (pass/fail, exit code, label) MUST be captured and included in the ledger event evidence.
2. REQUIREMENT: If any inline gate execution fails (non-zero exit code), `closeout_cmd()` MUST halt the pipeline, report which gate failed with its output, and exit with code 1. Partial gate results MUST still be recorded in the closeout event evidence.
3. REQUIREMENT: After all gates pass, `closeout_cmd()` MUST prompt for human attestation by presenting the attestation choices (`Completed`, `Completed - Partial: [reason]`, `Dropped - [reason]`) and recording the operator's selection as an `attestation` ledger event via the existing `attest` machinery.
4. REQUIREMENT: `closeout_cmd()` MUST call `check_version_sync()` and `sync_project_version()` to bump version files when the ADR semver exceeds the current project version, and record the version sync result in the ledger event evidence.
5. REQUIREMENT: After attestation and version bump succeed, `closeout_cmd()` MUST mark the ADR status as `Completed` in the ledger by appending the appropriate status-transition event.
6. REQUIREMENT: `--dry-run` MUST show the full pipeline plan (gates that would run, attestation that would be prompted, version that would be bumped) without executing any gate, writing any ledger event, or modifying any file.
7. REQUIREMENT: `--json` MUST emit a single JSON object to stdout containing all pipeline stage results (gate results array, attestation record, version sync record, ADR status transition) with logs to stderr.
8. NEVER: `closeout_cmd()` MUST NOT skip the attestation prompt — even for Lite lane ADRs, the operator must explicitly confirm completion.
9. NEVER: `closeout_cmd()` MUST NOT modify the ledger event schema. Existing event types (`closeout_initiated`, `attestation`, `gate_checked`) are reused.
10. ALWAYS: Exit code 0 means all gates passed, attestation recorded, version bumped, and ADR marked Completed. Exit code 1 means a blocker or gate failure halted the pipeline.

> STOP-on-BLOCKERS: if prerequisites are missing (incomplete OBPIs, missing ADR file, ADR not in ledger), print a BLOCKERS list and halt with exit code 1.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- [ ] Related OBPIs: OBPI-0.19.0-08 (deprecate `gz gates`), OBPI-0.19.0-09 (deprecate manual `gz attest` during closeout)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/cli.py` — `closeout_cmd()` exists at line ~2494
- [ ] `src/gzkit/cli.py` — `_closeout_verification_steps()` exists at line ~2378
- [ ] `src/gzkit/cli.py` — `run_command()` import exists for subprocess execution
- [ ] `src/gzkit/cli.py` — `check_version_sync()` and `sync_project_version()` imports exist

**Existing Code (understand current state):**

- [ ] Pattern to follow: `audit_cmd()` at line ~2634 already runs `run_command()` in a loop and captures results — same pattern needed for closeout gates
- [ ] Pattern to follow: `tests/commands/test_gates.py` — test harness for gate commands
- [ ] Pattern to follow: `tests/commands/test_attest.py` — test harness for attestation
- [ ] Test infrastructure: `tests/commands/common.py` — `CliRunner` and `_quick_init()` helpers

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
# Unit tests for closeout pipeline
uv run python -m unittest tests.test_closeout_pipeline -v

# Full test suite
uv run gz test

# Quality gates
uv run gz lint
uv run gz typecheck

# Specific verification: closeout dry-run shows inline gate plan
uv run gz closeout ADR-0.19.0 --dry-run

# Specific verification: closeout JSON output includes gate results
uv run gz closeout ADR-0.19.0 --dry-run --json
```

## Acceptance Criteria

- [ ] REQ-0.19.0-01-01: Given an ADR with all OBPIs completed, when `gz closeout ADR-X.Y.Z` is run, then each quality gate (lint, typecheck, test, and docs/BDD for heavy lane) is executed inline via `run_command()` and the gate pass/fail results are captured in the ledger event evidence.
- [ ] REQ-0.19.0-01-02: Given a closeout where one quality gate fails (non-zero exit code), when `gz closeout ADR-X.Y.Z` is run, then the pipeline halts at the failing gate, reports which gate failed and its output, records partial results in evidence, and exits with code 1.
- [ ] REQ-0.19.0-01-03: Given all quality gates pass, when `gz closeout ADR-X.Y.Z` is run, then the command prompts for human attestation with the standard choices and records the attestation event in the ledger.
- [ ] REQ-0.19.0-01-04: Given attestation is recorded and the ADR semver exceeds the current project version, when `gz closeout ADR-X.Y.Z` is run, then `sync_project_version()` bumps pyproject.toml, `__init__.py`, and README.md, and the version sync result is recorded in the ledger event evidence.
- [ ] REQ-0.19.0-01-05: Given attestation and version bump succeed, when `gz closeout ADR-X.Y.Z` is run, then the ADR status transitions to Completed via a ledger status-transition event and the command exits with code 0.
- [ ] REQ-0.19.0-01-06: Given any ADR, when `gz closeout ADR-X.Y.Z --dry-run` is run, then the full pipeline plan is displayed (gates to run, attestation to prompt, version to bump) without executing any gate, writing any ledger event, or modifying any file.
- [ ] REQ-0.19.0-01-07: Given any ADR, when `gz closeout ADR-X.Y.Z --json` is run, then the output is a single valid JSON object containing gate results, attestation record, version sync, and ADR status transition, with all non-JSON output directed to stderr.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run python -m unittest tests.test_closeout_pipeline -v
Ran 13 tests in 1.208s — OK
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
$ uv run gz test — 1031 tests OK
```

### Value Narrative

Before this OBPI, `gz closeout` was a passive reporter: it checked OBPI completion, listed verification commands the operator should run manually, printed attestation instructions, and recorded a `closeout_initiated` event. The operator then had to manually run `gz lint`, `gz test`, `gz typecheck`, `gz attest`, and hope they did not skip any step. In practice, ADRs routinely ended up partially closed out — attestation missing, version never bumped, gates never actually executed.

After this OBPI, `gz closeout ADR-X.Y.Z` is a single orchestrated pipeline that runs gates inline, halts on failure, prompts for attestation, bumps version, and marks the ADR Completed. The operator runs one command; the pipeline enforces the full sequence.

### Key Proof

```text
$ uv run python -m unittest tests.test_closeout_pipeline -v
test_dry_run_json_includes_version_sync ... ok
test_dry_run_shows_plan_no_execution ... ok
test_exit_0_on_success ... ok
test_exit_1_on_gate_failure ... ok
test_json_output_contains_all_stages ... ok
test_json_output_on_gate_failure ... ok
test_attestation_never_skipped ... ok
test_attestation_recorded_in_ledger ... ok
test_adr_marked_completed ... ok
test_gate_failure_halts_pipeline ... ok
test_gates_run_inline_and_pass ... ok
test_partial_gate_results_recorded_on_failure ... ok
test_version_bump_when_needed ... ok
----------------------------------------------------------------------
Ran 13 tests in 1.208s
OK
```

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `tests/test_closeout_pipeline.py`
- Tests added: 13 tests covering all 10 requirements
- Date completed: 2026-03-22
- Attestation status: Completed (human attested)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: Completed
- Date: 2026-03-22

---

**Brief Status:** Completed

**Date Completed:** 2026-03-22

**Evidence Hash:** -
