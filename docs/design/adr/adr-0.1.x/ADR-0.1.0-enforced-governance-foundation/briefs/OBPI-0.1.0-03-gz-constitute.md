---
id: OBPI-0.1.0-03
parent: ADR-0.1.0
item: 3
lane: Heavy
status: Pending
---

# OBPI-0.1.0-03: Implement gz constitute

## Objective

Implement `gz constitute` command that creates/validates constitution artifacts.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #3 (AC-003: Constitution Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Create constitution from template if not exists
- Validate constitution structure if exists
- Append `constitution_created` event to ledger
- Support `--template` flag for custom templates

## Denied Paths

- Overwriting existing constitution without explicit flag
- Creating invalid constitution structure

## Requirements

- Constitution must contain required sections per GovZero doctrine
- Validation must report errors with file:line references

## Acceptance Criteria

- [ ] `gz constitute` creates constitution from template
- [ ] `gz constitute --validate` reports errors for malformed constitution
- [ ] Constitution contains required sections
- [ ] `constitution_created` event appended to ledger

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |
