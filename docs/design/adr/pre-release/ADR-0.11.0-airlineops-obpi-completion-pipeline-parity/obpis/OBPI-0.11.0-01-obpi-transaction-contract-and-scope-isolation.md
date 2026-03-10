---
id: OBPI-0.11.0-01-obpi-transaction-contract-and-scope-isolation
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.11.0-01-obpi-transaction-contract-and-scope-isolation: OBPI transaction contract and scope isolation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #1 -- "Define the OBPI transaction contract, scope isolation rules, and parallel-safe execution doctrine."

**Status:** Draft

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

- [ ] Intent and scope recorded in this brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Validation commands pass for updated docs/surfaces
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant doctrine and concept docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.11.0-01-01: OBPI transaction scope is defined as an explicit allowlist contract.
- [ ] REQ-0.11.0-01-02: Changed-files audit and spine-touch serialization rules are documented as fail-closed requirements.
- [ ] REQ-0.11.0-01-03: Parallel OBPI execution doctrine is explicit about disjoint allowlists and blocker conditions.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests and validation commands pass
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
