---
id: OBPI-0.11.0-06-template-closeout-and-migration-alignment
parent: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.11.0-06-template-closeout-and-migration-alignment: Template, closeout, and migration alignment

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- **Checklist Item:** #6 -- "Align templates, closeout guidance, and operator docs to the faithful AirlineOps completion pipeline."

**Status:** Draft

## Objective

Align gzkit templates, operator docs, and closeout surfaces so the faithful
OBPI completion pipeline is visible and executable across drafting,
implementation, attestation, and audit without drifting between runtime logic
and written guidance.

## Lane

**Heavy** -- This unit changes operator-visible guidance and template contracts
used by multiple control surfaces.

## Allowed Paths

- `.gzkit/skills/**`, `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` -- template and mirrored skill surfaces
- `docs/governance/GovZero/**` -- canonical ceremony and transaction docs
- `docs/user/commands/**`, `docs/user/concepts/**`, `docs/user/runbook.md` -- operator-facing guidance
- `src/gzkit/commands/**` -- closeout/help text alignment if required
- `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/**` and `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- migration notes or cross-links if required
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/**` -- ADR/OBPI evidence and linkage

## Denied Paths

- `../airlineops/**`
- Any template change that weakens fail-closed scope or evidence rules
- Any closeout guidance that implies Gate 5 can be automated
- New dependencies or unrelated runtime feature work

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Templates MUST reflect the same transaction and evidence rules enforced by runtime surfaces.
1. REQUIREMENT: Operator docs MUST describe the faithful OBPI completion flow from draft through attestation and reconciliation.
1. REQUIREMENT: If mirrored skill/control surfaces change, `gz agent sync control-surfaces` MUST be run and captured in evidence.
1. NEVER: Leave 0.7.0 / 0.10.0 and 0.11.0 guidance in contradictory states.
1. ALWAYS: Preserve human closeout authority explicitly in docs and examples.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`

**Context:**

- [ ] `../airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.32-govzero-obpi-transaction-protocol/ADR-0.0.32-govzero-obpi-transaction-protocol.md`
- [ ] `docs/governance/GovZero/validation-receipts.md`
- [ ] `docs/user/commands/obpi-status.md`
- [ ] `docs/user/commands/obpi-reconcile.md`
- [ ] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/`
- [ ] `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/`

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical skill/template directories exist
- [ ] Closeout and attestation command docs exist

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
- [ ] Relevant docs and templates updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/
```

## Acceptance Criteria

- [ ] REQ-0.11.0-06-01: Templates express the faithful transaction and evidence rules consistently with runtime surfaces.
- [ ] REQ-0.11.0-06-02: Operator docs describe one coherent OBPI completion and closeout flow.
- [ ] REQ-0.11.0-06-03: Migration notes eliminate contradictory guidance across 0.7.0, 0.10.0, and 0.11.0 surfaces.

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
