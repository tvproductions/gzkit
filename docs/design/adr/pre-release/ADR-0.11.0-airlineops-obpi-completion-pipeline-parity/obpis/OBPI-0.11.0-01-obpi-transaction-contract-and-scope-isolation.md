---
id: OBPI-0.11.0-01-obpi-transaction-contract-and-scope-isolation
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.11.0-01-obpi-transaction-contract-and-scope-isolation: OBPI transaction contract and scope isolation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #1 -- "Define the OBPI transaction contract, scope isolation rules, and parallel-safe execution doctrine."

**Status:** Completed

## Objective

Codify OBPI work in gzkit as a bounded transaction with explicit allowlisted
scope, changed-files audit requirements, spine-touch serialization, and
parallel-safe execution rules so completion is mechanically constrained instead
of informally described.

## Lane

**Heavy** -- This unit defines operator-facing governance law and the execution
contract that later runtime surfaces must enforce.

## Allowed Paths

- `docs/governance/GovZero/**` -- canonical transaction and scope-isolation doctrine
- `docs/user/concepts/**` -- user-facing lifecycle and OBPI concept alignment
- `.gzkit/skills/**`, `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- skill text if the contract must be mirrored
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**` -- canonical source remains read-only
- `src/**` runtime implementation work
- New dependencies, lockfiles, or CI changes
- Any change that weakens Gate 5 human authority

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The contract MUST define ALLOWED PATHS as law, not advisory guidance.
1. REQUIREMENT: The contract MUST require a changed-files audit against the allowlist before completion can succeed.
1. REQUIREMENT: The contract MUST define spine surfaces and require serialized execution for spine-touch OBPIs.
1. REQUIREMENT: The contract MUST define when parallel OBPI execution is allowed and when it must stop with BLOCKERS.
1. NEVER: Recast scope isolation as a best-effort suggestion.
1. ALWAYS: Preserve explicit human attestation as the completion authority boundary for heavy and foundation work.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- [ ] `docs/governance/GovZero/obpi-decomposition-matrix.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.32-govzero-obpi-transaction-protocol/ADR-0.0.32-govzero-obpi-transaction-protocol.md`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- [ ] `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/GovZero/`
- [ ] `docs/user/concepts/`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Validation commands pass for updated docs/surfaces
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant doctrine and concept docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [x] REQ-0.11.0-01-01: OBPI transaction scope is defined as an explicit allowlist contract.
- [x] REQ-0.11.0-01-02: [doc] Changed-files audit and spine-touch serialization rules are documented as fail-closed requirements.
- [x] REQ-0.11.0-01-03: [doc] Parallel OBPI execution doctrine is explicit about disjoint allowlists and blocker conditions.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests and validation commands pass
- [x] **Code Quality:** Lint and type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

### Value Narrative

Before this tranche, gzkit had a transaction-contract page, but it still left
real execution compatibility rules implicit even after the AirlineOps pipeline
import. Operators could read the doctrine without seeing how missing plan-audit
receipts or missing lock parity should constrain real OBPI execution.

After this tranche, the canonical contract now states those constraints
explicitly: plan receipts are consumed when present, missing receipt-generation
parity is treated as a governance gap, and shared or spine-touch work remains
single-OBPI until a native lock surface exists.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run gz validate --documents
All validations passed.

$ uv run gz test
Ran 334 tests in 4.435s
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
INFO    -  Documentation built in 0.75 seconds
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
Canonical doctrine now distinguishes execution-boundary law from runtime-state law:

- docs/governance/GovZero/obpi-transaction-contract.md
- docs/governance/GovZero/obpi-runtime-contract.md

Operator-facing concept docs now point to the transaction contract for
allowlists, changed-files audit, spine-touch serialization, and parallel-safe
blockers.

Compatibility constraints are now explicit in doctrine as well:

- plan-audit receipts are consumed when present during context loading
- missing receipt-generation parity is treated as a governance gap
- shared or spine-touch work remains single-OBPI until lock parity exists

Supporting parity evidence:

- docs/proposals/REPORT-airlineops-parity-2026-03-11.md
- docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md

ADR package readiness still fails closed until later tranches finish:

- `uv run gz adr audit-check ADR-0.11.0-airlineops-obpi-completion-pipeline-parity`
  reports the expected incomplete-OBPI blocker set
```

### Implementation Summary

- Files created/modified:
  - `docs/governance/GovZero/obpi-transaction-contract.md`
  - `docs/governance/GovZero/obpi-runtime-contract.md`
  - `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
  - `docs/user/concepts/obpis.md`
  - `docs/user/concepts/lifecycle.md`
  - `docs/proposals/REPORT-airlineops-parity-2026-03-11.md`
  - `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-11.md`
  - `mkdocs.yml`
- Tests added: none
- Date completed: 2026-03-11
- Attestation status: human attestation recorded and completion receipt emitted
- Defects noted:
  - `gz-obpi-lock` parity is still missing; concurrent/shared-scope execution
    must fail closed until a native lock surface lands.
  - plan-audit hook and receipt-generation parity are still missing; receipt
    consumption is documented, but creation remains a follow-on import.

## Human Attestation

- Attestor: human:jeff
- Attestation: this opbi pipeline is nothing like airlineops. anyway... attest completed
- Date: 2026-03-11
- Scope: OBPI-0.11.0-01 transaction-contract doctrine, compatibility constraints, and supporting operator concept updates reviewed and accepted for completion.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-11

**Evidence Hash:** 086097b
