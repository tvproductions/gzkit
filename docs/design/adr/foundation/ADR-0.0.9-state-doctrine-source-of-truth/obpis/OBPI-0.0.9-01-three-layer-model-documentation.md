---
id: OBPI-0.0.9-01-three-layer-model-documentation
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 1
lane: lite
status: Completed
---

# OBPI-0.0.9-01: Three-Layer Model and Authority Rules Documentation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #1 - "Document three-layer model and five authority rules"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [x] Architecture Planning Memo Section 2

**Existing Code (understand current state):**

- [x] `src/gzkit/ledger_semantics.py` — current ledger-first patterns
- [x] `src/gzkit/sync.py` — current frontmatter sync patterns

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] N/A — documentation-only OBPI
- [x] Validation: `uv run mkdocs build --strict`

### Code Quality

- [x] N/A — no code changes

## Verification

```bash
uv run mkdocs build --strict
# Verify state-doctrine.md renders correctly
```

## Acceptance Criteria

- [x] REQ-0.0.9-01-01: `docs/governance/state-doctrine.md` exists with three-layer definitions
- [x] REQ-0.0.9-01-02: Five authority rules are stated with rationale
- [x] REQ-0.0.9-01-03: Governance runbook links to state doctrine reference

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** mkdocs build passes
- [x] **Code Quality:** N/A
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
INFO - Documentation built in 1.03 seconds (mkdocs build --strict, zero warnings)
```

### Value Narrative

Before this OBPI, the three-layer model and authority rules existed only in the ADR-0.0.9 Decision section. Operators and agents had no single canonical reference document to consult when diagnosing state conflicts. Now `docs/governance/state-doctrine.md` provides the definitive reference with gzkit-specific examples, verbatim rules, and a conflict decision table.

### Key Proof

```bash
uv run mkdocs build --strict
# INFO - Documentation built in 1.03 seconds
# state-doctrine.md renders at governance/state-doctrine/
# governance_runbook.md cross-links at lines 91 and 544
```

### Implementation Summary

- Files created: `docs/governance/state-doctrine.md`
- Files modified: `docs/governance/governance_runbook.md`, `mkdocs.yml`
- Tests added: N/A (documentation-only)
- Date completed: 2026-03-31
- Attestation status: Human-attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attset completed`
- Date: `2026-03-31`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-31

**Evidence Hash:** -
