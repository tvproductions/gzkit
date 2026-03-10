---
id: OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation: Anchor-aware OBPI drift and reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #4 -- "Deliver anchor-aware OBPI drift detection and reconciliation surfaces."

**Status:** Draft

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

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.29-obpi-completion-anchoring/ADR-0.0.29-obpi-completion-anchoring.md`
- [ ] `src/gzkit/commands/status.py`
- [ ] `src/gzkit/ledger.py`
- [ ] `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Anchor-bearing OBPI completion receipts exist or are stubbed deterministically
- [ ] `gz obpi reconcile` and `gz obpi status` surfaces are available

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.11.0-04-01: OBPI reconcile distinguishes ledger/file drift from anchor drift.
- [ ] REQ-0.11.0-04-02: Reconcile blocker output names missing or stale anchor evidence explicitly.
- [ ] REQ-0.11.0-04-03: Status surfaces preserve OBPI-granular drift reasons that map to remediation actions.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Code Quality:** Lint and type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
