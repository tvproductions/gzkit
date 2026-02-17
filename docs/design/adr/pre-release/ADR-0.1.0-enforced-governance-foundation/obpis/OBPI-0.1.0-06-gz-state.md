---
id: OBPI-0.1.0-06
parent: ADR-0.1.0
item: 6
lane: Heavy
status: Pending
---

# OBPI-0.1.0-06: Implement gz state

## Objective

Implement `gz state` command that queries ledger and displays current artifact state.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #6 (AC-006: State Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Parse `.gzkit/ledger.jsonl` and compute current state
- Display dependency graph of artifacts (PRD → Brief → ADR)
- Support `--json` for machine-readable output
- Support `--blocked` to show items with unresolved dependencies
- Support `--ready` to show items ready for work

## Denied Paths

- Writing to ledger (read-only operation)
- Modifying any files

## Requirements

- Must parse ledger correctly
- Must compute state from event sequence
- Must display parent/child relationships

## Acceptance Criteria

- [ ] `gz state` parses ledger and displays state
- [ ] `gz state --json` outputs valid JSON
- [ ] `gz state --blocked` shows blocked items
- [ ] `gz state --ready` shows ready items
- [ ] State display shows dependency graph

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |
