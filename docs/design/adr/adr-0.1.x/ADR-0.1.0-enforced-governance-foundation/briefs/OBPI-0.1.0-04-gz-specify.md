---
id: OBPI-0.1.0-04
parent: ADR-0.1.0
item: 4
lane: Heavy
status: Pending
---

# OBPI-0.1.0-04: Implement gz specify

## Objective

Implement `gz specify` command that creates briefs linked to PRD/constitution.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #4 (AC-004: Brief Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Create brief from template in configured briefs directory
- Insert constitution reference automatically
- Generate unique brief ID
- Append `brief_created` event to ledger with `parent` reference

## Denied Paths

- Creating brief without constitution existing
- Creating brief without parent reference

## Requirements

- Brief must link to constitution
- Brief must have unique ID
- Ledger event must include `parent` field

## Acceptance Criteria

- [ ] `gz specify my-feature` creates brief in configured directory
- [ ] Brief contains constitution reference
- [ ] Brief has unique ID
- [ ] `brief_created` event appended to ledger with `parent`
- [ ] Command fails if constitution does not exist

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |
