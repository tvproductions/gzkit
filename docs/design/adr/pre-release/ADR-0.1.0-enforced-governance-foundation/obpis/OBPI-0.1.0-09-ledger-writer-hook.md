---
id: OBPI-0.1.0-09
parent: ADR-0.1.0
item: 9
lane: Heavy
status: Completed
---

# OBPI-0.1.0-09: Implement ledger-writer hook

## Objective

Implement Claude hook script that appends `artifact_edited` events to ledger on governance artifact edits.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #9 (AC-009: Hooks)

## Lane

**Heavy** — External integration contract

## Allowed Paths

- Fire on PostToolUse for Edit/Write tools
- Match governance artifact patterns:
  - `docs/adr/**/*.md`
  - `docs/briefs/**/*.md`
  - `docs/prd/**/*.md`
  - `docs/constitutions/**/*.md`
  - `docs/audit/**/*.md`
- Append `artifact_edited` event to ledger
- Include session ID for traceability
- Exit 0 on success (non-blocking)

## Denied Paths

- Blocking on ledger write failure
- Modifying the edited artifact
- Network calls

## Requirements

- Hook must be non-blocking (best-effort)
- Hook must include session ID in event
- Hook must match only governance artifacts

## Acceptance Criteria

- [ ] Hook fires on Edit/Write to `docs/adr/**`
- [ ] Hook fires on Edit/Write to `docs/briefs/**`
- [ ] `artifact_edited` event appended to ledger
- [ ] Hook includes session ID
- [ ] Hook exits 0 even on ledger write failure

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_hooks.py` |

## Evidence

### Implementation Summary

- Completion evidence: Capability is implemented in the current `gz` runtime and validated by repository quality gates.
- Reconciliation date: 2026-02-22
