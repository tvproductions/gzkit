---
id: OBPI-0.1.0-05
parent: ADR-0.1.0
item: 5
lane: Heavy
status: Pending
---

# OBPI-0.1.0-05: Implement gz plan

## Objective

Implement `gz plan` command that creates ADRs via mandatory Q&A interview.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #5 (AC-005: ADR Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Run mandatory Q&A interview to shape ADR content
- Create ADR folder structure with obpis/ subdirectory
- Create ADR document from template populated with interview answers
- Create ADR-CLOSEOUT-FORM.md template
- Save Q&A transcript to `.gzkit/transcripts/`
- Append `adr_created` event to ledger

## Denied Paths

- Creating ADR without completing interview
- Creating ADR without brief reference
- Skipping folder structure creation

## Requirements

- Interview must be completed before ADR is created
- ADR must link to specified brief(s)
- ADR folder structure must include obpis/ subdirectory
- Transcript must be preserved as artifact

## Acceptance Criteria

- [ ] `gz plan ADR-0.1.0 --brief my-feature` runs mandatory Q&A interview
- [ ] Interview answers populate ADR template
- [ ] ADR folder structure created with obpis/ subdirectory
- [ ] ADR-CLOSEOUT-FORM.md created
- [ ] ADR contains brief linkage
- [ ] `adr_created` event appended to ledger with `parent`
- [ ] Command fails if referenced brief does not exist
- [ ] Command fails if interview not completed

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_interview.py` |
