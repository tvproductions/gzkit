---
id: OBPI-0.0.9-02-ledger-first-status-reads
parent: ADR-0.0.9-state-doctrine-source-of-truth
item: 2
lane: lite
status: attested_completed
---

# OBPI-0.0.9-02: Ledger-First Status Reads

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md`
- **Checklist Item:** #2 - "All gz commands that read entity status use ledger-derived state"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `ADR-0.0.9-state-doctrine-source-of-truth.md`
- [x] OBPI-0.0.9-01 (three-layer model) for layer definitions

**Existing Code (understand current state):**

- [x] `src/gzkit/ledger_semantics.py` -- current ledger-first patterns
- [x] `src/gzkit/commands/` -- all status-reading commands
- [x] `src/gzkit/sync.py` -- current frontmatter sync patterns

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Test exists proving ledger wins over frontmatter
- [x] `uv run -m unittest -q` passes

### Code Quality

- [x] `uv run ruff check . --fix && uv run ruff format .`
- [x] `uvx ty check . --exclude 'features/**'`

## Verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
# Verify no command reads frontmatter status: as authoritative
```

## Acceptance Criteria

- [x] REQ-0.0.9-02-01: All status-reading commands derive state from ledger events
- [x] REQ-0.0.9-02-02: Test exists proving ledger wins when frontmatter disagrees
- [x] REQ-0.0.9-02-03: No command reads frontmatter `status:` field as authoritative

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, ledger-wins test exists
- [x] **Code Quality:** Ruff and ty pass
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
test_derive_obpi_semantics_ledger_wins_when_frontmatter_says_completed ... ok
test_derive_obpi_semantics_ledger_wins_when_frontmatter_says_draft ... ok
test_blocks_when_obpi_is_ledger_completed ... ok
Ran 3 tests in 0.020s — OK
```

### Value Narrative

Before this OBPI, the pipeline launch command checked frontmatter `status: Completed` to decide whether an OBPI was already done. A Layer 3 convenience cache was acting as authoritative source-of-truth, allowing manual frontmatter edits to bypass or block governance. Now the pipeline gates on `ledger_completed` — the ledger event log is the sole authority for completion status in all commands.

### Key Proof

```bash
uv run -m unittest tests.test_ledger.TestLedger.test_derive_obpi_semantics_ledger_wins_when_frontmatter_says_completed tests.test_ledger.TestLedger.test_derive_obpi_semantics_ledger_wins_when_frontmatter_says_draft tests.commands.test_obpi_pipeline.TestObpiPipelineCommand.test_blocks_when_obpi_is_ledger_completed -v
```

### Implementation Summary

- Files modified: src/gzkit/commands/obpi_cmd.py (changed file_completed gate to ledger_completed)
- Tests added: 2 ledger-wins tests in tests/test_ledger.py, 1 updated pipeline test in tests/commands/test_obpi_pipeline.py
- Date completed: 2026-03-31
- Attestation status: Human attested
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
