---
id: OBPI-0.11.0-03-obpi-completion-recorder-and-anchor-receipts
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.11.0-03-obpi-completion-recorder-and-anchor-receipts: OBPI completion recorder and anchor receipts

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #3 -- "Deliver recorder and receipt semantics for git-anchored OBPI completion evidence."

**Status:** Completed

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
- `src/gzkit/cli.py` -- manual receipt emission must match the same structured completion evidence contract
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
uv run gz validate --documents
uv run gz obpi status <obpi-id> --json
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.11.0-03-01: OBPI completion receipts include structured git anchor data.
- [x] REQ-0.11.0-03-02: Receipt evidence preserves transaction-scope fields needed for later reconciliation.
- [x] REQ-0.11.0-03-03: Recorder failure semantics are explicit, warning-only, and tested.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass
- [x] **Code Quality:** Lint and type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

### Value Narrative

Before this tranche, gzkit could emit OBPI completion receipts, but the
receipts were too coarse for later drift analysis. Hook-driven completion writes
captured anchor data only as a best-effort blob, manual `gz obpi emit-receipt`
did not normalize the same structured context, and the recorder could pollute
its own scope evidence by including `.gzkit/ledger.jsonl` in the changed-files
snapshot.

After this tranche, completed receipts preserve one deterministic evidence
envelope across hook-driven and manual completion paths. `scope_audit` now
captures the OBPI allowlist plus the pre-recorder changed-files snapshot,
`git_sync_state` preserves the repository sync posture that later reconciliation
needs, and `recorder_source` plus `recorder_warnings` make degraded anchoring
or post-completion recorder failures explicit without retroactively undoing the
completion decision.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

```text
$ uv run gz validate --documents
All validations passed.
```

### Gate 2 (TDD)

```text
$ uv run gz test
Ran 342 tests in 7.322s
OK
```

### Code Quality

```text
$ uv run gz lint
Running linters...
All checks passed!
ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!
Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Documentation built in 0.71 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Key Proof

```text
Focused proof surface:

$ uv run -m unittest tests.test_obpi_validator tests.commands.test_runtime tests.test_validate
Ran 65 tests in 3.458s
OK

That proof tranche exercises the exact contract landed here:

- hook-driven completion receipts now include `scope_audit`, `git_sync_state`,
  `recorder_source`, and `recorder_warnings`
- recorder scope snapshots are captured before the ledger write so
  `.gzkit/ledger.jsonl` does not contaminate OBPI transaction evidence
- degraded anchor capture and receipt-append failures warn explicitly without
  rewriting the completion decision
- manual `gz obpi emit-receipt --event completed` enriches the same structured
  receipt context as the hook path
```

### Implementation Summary

- Files created/modified:
  - `src/gzkit/hooks/core.py`
  - `src/gzkit/hooks/obpi.py`
  - `src/gzkit/cli.py`
  - `src/gzkit/utils.py`
  - `src/gzkit/schemas/ledger.json`
  - `src/gzkit/validate.py`
  - `docs/user/commands/obpi-emit-receipt.md`
  - `docs/governance/GovZero/validation-receipts.md`
  - `docs/governance/GovZero/obpi-runtime-contract.md`
  - `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
  - this OBPI brief
- Tests added/updated:
  - `tests/test_obpi_validator.py`
  - `tests/commands/test_runtime.py`
  - `tests/test_validate.py`
- Date completed: 2026-03-12
- Completion receipt surface:
  - hook recorder and manual `gz obpi emit-receipt` now normalize the same structured completion evidence contract

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-12

---

**Brief Status:** Completed

**Date Completed:** 2026-03-12

**Evidence Hash:** a809a9d
