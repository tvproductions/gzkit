---
id: OBPI-0.1.0-01
parent: ADR-0.1.0
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.1.0-01: Implement gz init

## Objective

Implement `gz init` command that scaffolds project structure, ledger, and Claude hooks.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #1 (AC-001: Project Initialization)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Create `.gzkit/` directory with `ledger.jsonl` and `config.json`
- Create `.claude/` directory with `settings.json` and `hooks/ledger-writer.py`
- Create `docs/` subdirectories (prd, constitutions, briefs, adr)
- Append `project_init` event to ledger

## Denied Paths

- Overwriting existing gzkit structure (must fail with error)
- Creating files outside project root
- Network calls

## Requirements

- Command must be idempotent-safe (fail if already initialized)
- All created files must be valid (parseable JSON, executable Python)
- Ledger must be created before any events are written

## Acceptance Criteria

- [ ] `gz init test-project` creates all directories
- [ ] `.gzkit/ledger.jsonl` created (empty or with init event)
- [ ] `.gzkit/config.json` created with defaults
- [ ] `.claude/settings.json` created with hook config
- [ ] `.claude/hooks/ledger-writer.py` created and executable
- [ ] `project_init` event appended to ledger
- [ ] Command fails with clear error if structure already exists

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |

## Evidence

### Implementation Summary

- Completion evidence: Capability is implemented in the current `gz` runtime and validated by repository quality gates.
- Reconciliation date: 2026-02-22
