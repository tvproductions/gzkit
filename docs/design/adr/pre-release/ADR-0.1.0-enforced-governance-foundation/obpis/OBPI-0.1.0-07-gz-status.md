---
id: OBPI-0.1.0-07
parent: ADR-0.1.0
item: 7
lane: Heavy
status: Completed
---

# OBPI-0.1.0-07: Implement gz status

## Objective

Implement `gz status` command that displays gate status for active work.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #7 (AC-007: Status Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Display current lane (Lite/Heavy)
- Display active ADR(s) and their gate status
- Display blocking issues with file:line references
- Support `--json` for machine-readable output

## Denied Paths

- Writing to ledger (read-only operation)
- Running gate checks (that's `gz gates`)

## Requirements

- Must show lane correctly
- Must show gate pass/pending status
- Must identify blocking issues

## Acceptance Criteria

- [ ] `gz status` displays lane and gate status
- [ ] `gz status --json` outputs valid JSON
- [ ] Blocking issues show file:line references

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |

## Evidence

### Implementation Summary

- Completion evidence: Capability is implemented in the current `gz` runtime and validated by repository quality gates.
- Reconciliation date: 2026-02-22
