---
id: OBPI-0.19.0-02-gz-audit-adr-x-y-z-end-to-end-audit-pipeline
parent: ADR-0.19.0-closeout-audit-processes
item: 2
lane: Lite
status: Draft
---

# OBPI-0.19.0-02: `gz audit ADR-X.Y.Z` — end-to-end audit pipeline

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #2 - "OBPI-0.19.0-02: `gz audit ADR-X.Y.Z` — end-to-end audit pipeline"

**Status:** Draft

## Objective

Extend `audit_cmd()` so that after creating audit artifacts (AUDIT_PLAN.md, AUDIT.md, proof files), it also emits a validation receipt via the existing `gz adr emit-receipt` machinery and transitions the ADR status from Completed to Validated in the ledger — completing the post-attestation reconciliation lifecycle in a single command invocation instead of requiring separate manual `emit-receipt` and status-transition steps.

## Lane

**Lite** — Inherited from parent ADR lane (ledger `adr_created` event for ADR-0.19.0 records lane as `lite`).

> The parent ADR lane is Lite because `gz audit` already exists as a command surface. This OBPI adds two internal pipeline stages (receipt emission and status transition) to an existing command. No new CLI surface, flag, or schema is introduced.

## Allowed Paths

- `src/gzkit/cli.py` — Contains `audit_cmd()` (line ~2634) which must be extended to emit the validation receipt and append an ADR status-transition event after proof collection succeeds
- `tests/test_audit_pipeline.py` — New test module for end-to-end audit pipeline coverage including attestation gate, artifact creation, receipt emission, and status transition

## Denied Paths

- `src/gzkit/ledger.py` — Ledger event schema is reused, not changed (ADR non-goal)
- `.gzkit/ledger.jsonl` — Never edited manually
- `src/gzkit/cli.py` `closeout_cmd()` — Closeout pipeline is OBPI-01 scope
- `docs/user/commands/audit.md` — Docs update only if output format materially changes
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `audit_cmd()` MUST block execution and exit with code 1 if the ADR has not been attested. The existing attestation check (`adr_info.get("attested")`) MUST remain the first guard after ADR resolution.
2. REQUIREMENT: `audit_cmd()` MUST create the audit directory tree (`audit/`, `audit/proofs/`), run all verification commands via `run_command()`, and write `AUDIT_PLAN.md` and `AUDIT.md` with pass/fail results for each command — preserving all existing artifact-creation behavior.
3. REQUIREMENT: After all verification commands complete and audit artifacts are written, `audit_cmd()` MUST emit a validation receipt by appending an `audit_validated` (or equivalent existing event type) ledger event containing: ADR ID, audit date, verification results summary (pass count, fail count), audit artifact paths, and the auditor identity from `get_git_user()`.
4. REQUIREMENT: After the validation receipt is emitted, `audit_cmd()` MUST transition the ADR status to `Validated` by appending the appropriate status-transition ledger event, but ONLY if all verification commands passed (zero failures).
5. REQUIREMENT: If any verification command fails, `audit_cmd()` MUST still write audit artifacts and the validation receipt (recording the failures), but MUST NOT transition the ADR to Validated. Exit code MUST be 1.
6. REQUIREMENT: `--dry-run` MUST show the audit plan including which commands would run, which artifacts would be created, that a validation receipt would be emitted, and that the ADR would transition to Validated — without executing any command, writing any file, or appending any ledger event.
7. REQUIREMENT: `--json` MUST emit a single JSON object to stdout containing: ADR ID, audit artifact paths, verification results array, validation receipt record, and ADR status transition record. All non-JSON output MUST go to stderr.
8. NEVER: `audit_cmd()` MUST NOT transition the ADR to Validated if any verification command failed. The Validated status is reserved for fully-passing audits.
9. NEVER: `audit_cmd()` MUST NOT change the existing attestation guard behavior — `gz audit` without prior attestation MUST still fail with the current error message and next-steps guidance.
10. ALWAYS: The validation receipt MUST be a ledger event (not a standalone file) so it is subject to the same trust guarantees as all other ledger events.

> STOP-on-BLOCKERS: if the ADR is not attested, not in the ledger, or is a pool ADR, print the blocker and halt with exit code 1.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- [ ] Related OBPIs: OBPI-0.19.0-05 (`audit_generated` event), OBPI-0.19.0-07 (Completed -> Validated transition)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/cli.py` — `audit_cmd()` exists at line ~2634
- [ ] `src/gzkit/cli.py` — `run_command()` import exists for subprocess execution
- [ ] `src/gzkit/cli.py` — `get_git_user()` exists for auditor identity
- [ ] `src/gzkit/cli.py` — Attestation guard logic exists at lines ~2650-2667

**Existing Code (understand current state):**

- [ ] `audit_cmd()` at line ~2634 — already runs `run_command()` in a loop, captures results, writes `AUDIT_PLAN.md` and `AUDIT.md`, and gates on attestation
- [ ] `tests/commands/test_audit.py` — existing audit test patterns (currently tests `cli audit` and `check-config-paths`, not `gz audit ADR-X.Y.Z`)
- [ ] Test infrastructure: `tests/commands/common.py` — `CliRunner` and `_quick_init()` helpers
- [ ] `closeout_cmd()` at line ~2494 — pattern for ledger event creation and version sync

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
# Unit tests for audit pipeline
uv run python -m unittest tests.test_audit_pipeline -v

# Full test suite
uv run gz test

# Quality gates
uv run gz lint
uv run gz typecheck

# Specific verification: audit dry-run shows receipt emission plan
uv run gz audit ADR-0.19.0 --dry-run

# Specific verification: audit JSON output includes receipt and transition
uv run gz audit ADR-0.19.0 --dry-run --json
```

## Acceptance Criteria

- [ ] REQ-0.19.0-02-01: Given an ADR that has NOT been attested, when `gz audit ADR-X.Y.Z` is run, then the command prints "gz audit requires human attestation first (Gate 5)" with next-step guidance and exits with code 1 without creating any artifacts.
- [ ] REQ-0.19.0-02-02: Given an attested ADR, when `gz audit ADR-X.Y.Z` is run, then the command creates the `audit/` directory, runs each verification command via `run_command()`, writes proof files to `audit/proofs/`, and generates `AUDIT_PLAN.md` and `AUDIT.md` with pass/fail status for each command.
- [ ] REQ-0.19.0-02-03: Given all verification commands pass, when `gz audit ADR-X.Y.Z` completes artifact creation, then a validation receipt ledger event is appended containing the ADR ID, audit date, pass/fail summary, audit artifact paths, and auditor identity.
- [ ] REQ-0.19.0-02-04: Given all verification commands pass and the validation receipt is emitted, when `gz audit ADR-X.Y.Z` completes, then the ADR status transitions to Validated via a ledger status-transition event and the command exits with code 0.
- [ ] REQ-0.19.0-02-05: Given one or more verification commands fail, when `gz audit ADR-X.Y.Z` completes, then audit artifacts and the validation receipt are still written (recording failures), but the ADR status does NOT transition to Validated and the command exits with code 1.
- [ ] REQ-0.19.0-02-06: Given any attested ADR, when `gz audit ADR-X.Y.Z --dry-run` is run, then the command displays the full audit plan (commands to run, artifacts to create, receipt to emit, status transition to perform) without executing anything or writing any file.
- [ ] REQ-0.19.0-02-07: Given any attested ADR, when `gz audit ADR-X.Y.Z --json` is run, then the output is a single valid JSON object containing audit results, receipt record, and status transition, with non-JSON output to stderr.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Value Narrative

Before this OBPI, `gz audit` created proof artifacts (AUDIT_PLAN.md, AUDIT.md, proof text files) but stopped there. The operator then had to manually run `gz adr emit-receipt ADR-X.Y.Z --event validated` and somehow ensure the ADR status transitioned to Validated. In practice, operators ran the audit, saw the pass/fail table, and moved on — leaving the ADR in Completed status with no validation receipt in the ledger. The audit existed as files on disk but was invisible to ledger-based governance queries.

After this OBPI, `gz audit ADR-X.Y.Z` runs the full post-attestation reconciliation pipeline: verification, artifact creation, receipt emission, and status transition. The validation receipt lives in the ledger alongside all other governance events, and the ADR status reflects the actual audit outcome.

## Key Proof

```text
$ uv run gz audit ADR-0.19.0 --dry-run
Dry run: no files will be written.
  Would create: docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit
  Would create: docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/audit/proofs
  Would run: uv run gz test
  Would run: uv run gz lint
  Would run: uv run gz typecheck
  Would run: uv run mkdocs build --strict
  Would emit validation receipt to ledger
  Would transition ADR status: Completed -> Validated
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane — self-closeable after evidence)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
