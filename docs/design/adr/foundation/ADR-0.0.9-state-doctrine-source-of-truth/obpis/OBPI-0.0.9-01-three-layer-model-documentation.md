---
id: OBPI-0.0.9-01-three-layer-model-documentation
parent: ADR-0.0.9
item: 1
lane: lite
status: Draft
---

# OBPI-0.0.9-01: Three-Layer Model and Authority Rules Documentation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #1 - "Document three-layer model and five authority rules"

**Status:** Draft

## Objective

A reference document exists in `docs/governance/` that defines the three storage
layers (L1: governance canon, L2: event log, L3: derived state) and the five
authority rules. All `gz` commands can reference this as the canonical state doctrine.

## Lane

**Lite** - Documentation and governance reference only. No CLI or external contract changes.

## Allowed Paths

- `docs/governance/state-doctrine.md`
- `docs/governance/governance_runbook.md`

## Denied Paths

- `src/gzkit/` — no code changes in this OBPI
- `tests/` — no test changes in this OBPI

## Requirements (FAIL-CLOSED)

1. Document MUST define all three layers with examples from the gzkit repo
2. Document MUST state the five authority rules verbatim from ADR-0.0.9 Decision section
3. Document MUST include a decision table: "when layers disagree, which wins?"
4. Document MUST be linked from `docs/governance/governance_runbook.md`

> STOP-on-BLOCKERS: if ADR-0.0.9 Decision section is incomplete, halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] Architecture Planning Memo Section 2

**Existing Code (understand current state):**

- [ ] `src/gzkit/ledger_semantics.py` — current ledger-first patterns
- [ ] `src/gzkit/sync.py` — current frontmatter sync patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] N/A — documentation-only OBPI
- [ ] Validation: `uv run mkdocs build --strict`

### Code Quality

- [ ] N/A — no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify state-doctrine.md renders correctly
```

## Acceptance Criteria

- [ ] REQ-0.0.9-01-01: `docs/governance/state-doctrine.md` exists with three-layer definitions
- [ ] REQ-0.0.9-01-02: Five authority rules are stated with rationale
- [ ] REQ-0.0.9-01-03: Governance runbook links to state doctrine reference

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** mkdocs build passes
- [ ] **Code Quality:** N/A
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste mkdocs build output here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
