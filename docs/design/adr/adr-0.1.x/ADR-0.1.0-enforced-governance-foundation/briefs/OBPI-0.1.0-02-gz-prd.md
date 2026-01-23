---
id: OBPI-0.1.0-02
parent: ADR-0.1.0
item: 2
lane: Heavy
status: Pending
---

# OBPI-0.1.0-02: Implement gz prd

## Objective

Implement `gz prd` command that creates PRDs via mandatory Q&A interview.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #2 (AC-002: PRD Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Run mandatory Q&A interview to shape PRD content
- Create PRD from hardened template populated with interview answers
- Save Q&A transcript to `.gzkit/transcripts/`
- Append `prd_created` event to ledger

## Denied Paths

- Creating PRD without completing interview
- Skipping required sections in template
- `--skip-interview` flag

## Requirements

- Interview must be completed before PRD is created
- PRD must contain hardened sections (invariants, gate mapping, Q&A, attestation)
- Transcript must be preserved as artifact

## Acceptance Criteria

- [ ] `gz prd PRD-FOO-1.0.0` runs mandatory Q&A interview
- [ ] Interview answers populate PRD template
- [ ] PRD contains hardened sections
- [ ] `prd_created` event appended to ledger
- [ ] Q&A transcript saved to `.gzkit/transcripts/`

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_interview.py` |
