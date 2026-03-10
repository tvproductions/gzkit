---
id: OBPI-0.11.0-03-obpi-completion-recorder-and-anchor-receipts
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.11.0-03-obpi-completion-recorder-and-anchor-receipts: OBPI completion recorder and anchor receipts

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #3 -- "Deliver recorder and receipt semantics for git-anchored OBPI completion evidence."

**Status:** Draft

## Objective

Record OBPI completion transitions as structured, git-anchored receipt events
that carry the evidence needed for later drift detection while preserving the
AirlineOps rule that post-completion recorder failures warn loudly but do not
block the edit path.

## Lane

**Heavy** -- This unit changes ledger evidence semantics and the runtime
recorder behavior consumed by operator reconciliation.

## Allowed Paths

- `src/gzkit/ledger.py` and `src/gzkit/schemas/ledger.json` -- receipt schema and anchor fields
- `src/gzkit/hooks/**` -- post-completion recorder integration
- `src/gzkit/utils.py` -- git anchor helpers if required
- `tests/**` and `features/**` -- receipt and recorder coverage
- `docs/governance/GovZero/**` and `docs/user/commands/**` -- receipt and anchoring docs
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any implementation that drops anchor capture to free-form text only
- Any implementation that makes post-completion recorder warnings indistinguishable from success
- New dependencies or external storage systems

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Completion receipts MUST carry a structured git anchor suitable for later drift comparison.
1. REQUIREMENT: Receipt evidence MUST preserve the transaction fields required for changed-files and scope reconciliation.
1. REQUIREMENT: Recorder failures after completion MUST surface as explicit warnings without rewriting the completion decision retroactively.
1. NEVER: Record an unstructured anchor blob that later consumers cannot parse deterministically.
1. ALWAYS: Keep receipt semantics ledger-first and repository-local.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.29-obpi-completion-anchoring/ADR-0.0.29-obpi-completion-anchoring.md`
- [ ] `src/gzkit/ledger.py`
- [ ] `src/gzkit/schemas/ledger.json`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/obpis/OBPI-0.7.0-02-obpi-completion-recorder-and-anchor.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/ledger.jsonl`
- [ ] Current receipt event family resolves through existing ledger consumers

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
uv run gz obpi status <obpi-id> --json
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [ ] REQ-0.11.0-03-01: OBPI completion receipts include structured git anchor data.
- [ ] REQ-0.11.0-03-02: Receipt evidence preserves transaction-scope fields needed for later reconciliation.
- [ ] REQ-0.11.0-03-03: Recorder failure semantics are explicit, warning-only, and tested.

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
