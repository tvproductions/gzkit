---
id: OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation: Anchor-aware OBPI drift and reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #4 -- "Deliver anchor-aware OBPI drift detection and reconciliation surfaces."

**Status:** Completed

## Objective

Extend gzkit reconciliation from simple ledger/file mismatch detection to
faithful AirlineOps-style drift analysis by comparing recorded completion
anchors and transaction evidence against current repository state and rendering
specific blocker reasons at OBPI granularity.

## Lane

**Heavy** -- This unit changes operator-visible reconciliation semantics and
closeout diagnostics.

## Allowed Paths

- `src/gzkit/ledger.py` -- anchor-aware drift semantics
- `src/gzkit/commands/status.py` and `src/gzkit/commands/common.py` -- status and reconcile surfaces
- `src/gzkit/utils.py` -- git comparison helpers if required
- `tests/**` and `features/**` -- reconciliation coverage
- `docs/user/commands/**` and `docs/governance/GovZero/**` -- operator and governance docs
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any implementation that reports anchor drift as a generic pending state
- Any implementation that hides the specific blocker list from reconcile output
- New external services or databases

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Reconciliation MUST distinguish ledger/file drift from git-anchor drift.
1. REQUIREMENT: Reconciliation MUST report missing, mismatched, and stale anchor evidence as explicit blockers.
1. REQUIREMENT: Status surfaces MUST preserve OBPI identifiers and drift reasons suitable for remediation.
1. NEVER: Collapse anchor-aware drift back into opaque ADR-only summaries.
1. ALWAYS: Reuse the canonical ledger-first OBPI runtime contract where possible.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md`
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [x] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.29-obpi-completion-anchoring/ADR-0.0.29-obpi-completion-anchoring.md`
- [x] `src/gzkit/commands/status.py`
- [x] `src/gzkit/ledger.py`
- [x] `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Anchor-bearing OBPI completion receipts exist or are stubbed deterministically
- [x] `gz obpi reconcile` and `gz obpi status` surfaces are available

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz obpi status <obpi-id>
uv run gz obpi reconcile <obpi-id>
uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.11.0-04-01: OBPI reconcile distinguishes ledger/file drift from anchor drift.
- [x] REQ-0.11.0-04-02: Reconcile blocker output names missing or stale anchor evidence explicitly.
- [x] REQ-0.11.0-04-03: Status surfaces preserve OBPI-granular drift reasons that map to remediation actions.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass
- [x] **Code Quality:** Lint and type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 348 tests in 8.080s
OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed!

$ uv run gz typecheck
All checks passed!

$ uv run gz validate --documents
All validations passed.

$ uv run mkdocs build --strict
Documentation built successfully.

$ uv run -m behave features/
2 features passed, 4 scenarios passed
```

### Value Narrative

Before this tranche, `gz obpi reconcile` could only fail on missing proof or
ledger/brief disagreement, so completed OBPIs had no repository-state-aware way
to explain whether later changes actually touched the recorded completion scope.
Now the runtime contract consumes completion anchors, scope audits, and
git-sync evidence directly from ledger receipts so operator surfaces can
distinguish generic proof drift from anchor drift with remediation-ready OBPI
reasons.

### Key Proof

```text
Focused proof surface:

$ uv run gz obpi reconcile OBPI-0.11.0-03-obpi-completion-recorder-and-anchor-receipts --json
{
  "passed": false,
  "runtime_state": "drift",
  "anchor_state": "stale",
  "blockers": [
    "completion anchor drifted in recorded OBPI scope",
    "completion receipt was captured from a dirty worktree"
  ]
}

That drill-down demonstrates the exact behavior landed here:

- completion-accounting data remains intact (`completed: true`) while
  reconciliation fails closed on anchor-specific blockers
- `anchor_state`, `anchor_commit`, `current_head`, and
  `anchor_drift_files` now explain why a completed OBPI is drifted
- ADR closeout blockers preserve the OBPI identifier and the same specific
  drift reasons without collapsing back to a generic ADR summary
```

### Implementation Summary

- Files created/modified:
  - `src/gzkit/ledger.py`
  - `src/gzkit/commands/status.py`
  - `src/gzkit/utils.py`
  - `src/gzkit/cli.py`
  - `tests/test_ledger.py`
  - `tests/commands/test_status.py`
  - `tests/commands/common.py`
  - `features/steps/gz_steps.py`
  - `features/obpi_anchor_drift.feature`
  - `docs/user/commands/obpi-status.md`
  - `docs/user/commands/obpi-reconcile.md`
  - `docs/user/commands/adr-status.md`
  - `docs/user/commands/status.md`
  - `docs/governance/GovZero/obpi-runtime-contract.md`
- Tests added/updated:
  - `tests/test_ledger.py`
  - `tests/commands/test_status.py`
  - `features/obpi_anchor_drift.feature`
- Date completed: 2026-03-12
- Follow-on defect tracked:
  - completion receipts emitted from a dirty worktree now reconcile as drift
    immediately; this should be aligned with the staged pipeline ceremony in
    OBPI-0.11.0-05/06 rather than left as operator guesswork

## Human Attestation

- Attestor: human:jeff
- Attestation: getting closer to the way i expect to use the pipeline - good! attest completed
- Date: 2026-03-12

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** e45c26c
