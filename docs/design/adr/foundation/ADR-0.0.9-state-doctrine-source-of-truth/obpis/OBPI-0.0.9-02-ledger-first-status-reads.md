---
id: OBPI-0.0.9-02-ledger-first-status-reads
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 2
lane: lite
status: Draft
---

# OBPI-0.0.9-02: Ledger-First Status Reads

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #2 - "All gz commands that read entity status use ledger-derived state"

**Status:** Draft

## Objective

All `gz` commands that read entity status use ledger-derived state, never
frontmatter as source-of-truth. Frontmatter is a convenience cache (L3);
the ledger event log (L2) is authoritative for all status reads.

## Lane

**Lite** - Audit and refactor existing status-reading commands. No new subcommands or external contract changes.

## Allowed Paths

- `src/gzkit/commands/`
- `src/gzkit/ledger_semantics.py`

## Denied Paths

- `docs/` -- no documentation changes in this OBPI
- `features/` -- no BDD features in this OBPI

## Requirements (FAIL-CLOSED)

1. Audit all status-reading commands; identify any that read frontmatter `status:` as authoritative
2. Refactor each to derive status from ledger events via `ledger_semantics.py`
3. Add test asserting that when frontmatter disagrees with ledger, ledger wins
4. No command may read frontmatter `status:` field as authoritative source-of-truth

> STOP-on-BLOCKERS: if `ledger_semantics.py` lacks a status-derivation function, halt and file defect.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [ ] OBPI-0.0.9-01 (three-layer model) for layer definitions

**Existing Code (understand current state):**

- [ ] `src/gzkit/ledger_semantics.py` -- current ledger-first patterns
- [ ] `src/gzkit/commands/` -- all status-reading commands
- [ ] `src/gzkit/sync.py` -- current frontmatter sync patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Test exists proving ledger wins over frontmatter
- [ ] `uv run -m unittest -q` passes

### Code Quality

- [ ] `uv run ruff check . --fix && uv run ruff format .`
- [ ] `uvx ty check . --exclude 'features/**'`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
# Verify no command reads frontmatter status: as authoritative
```

## Acceptance Criteria

- [ ] REQ-0.0.9-02-01: All status-reading commands derive state from ledger events
- [ ] REQ-0.0.9-02-02: Test exists proving ledger wins when frontmatter disagrees
- [ ] REQ-0.0.9-02-03: No command reads frontmatter `status:` field as authoritative

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, ledger-wins test exists
- [ ] **Code Quality:** Ruff and ty pass
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
