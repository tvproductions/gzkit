---
id: OBPI-0.1.0-10
parent: ADR-0.1.0
item: 10
lane: Heavy
status: Pending
---

# OBPI-0.1.0-10: Create templates

## Objective

Create minimal templates for PRD, constitution, brief, and ADR artifacts.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #10 (Templates)

## Lane

**Heavy** — External artifact contract

## Allowed Paths

- Create templates at `src/gzkit/templates/`
- Include required sections per GovZero doctrine
- Support variable substitution for scaffolding
- Keep templates minimal (harden based on usage)

## Denied Paths

- Over-engineering templates
- Adding optional sections that inflate ceremony

## Requirements

- PRD template must include: invariants, gate mapping, Q&A, attestation block
- Constitution template must include: purpose, principles, authority
- Brief template must include: objective, parent reference, acceptance criteria
- ADR template must include: intent, decision, consequences, checklist, attestation block

## Acceptance Criteria

- [ ] `src/gzkit/templates/prd.md` exists with required sections
- [ ] `src/gzkit/templates/constitution.md` exists with required sections
- [ ] `src/gzkit/templates/brief.md` exists with required sections
- [ ] `src/gzkit/templates/adr.md` exists with required sections
- [ ] Templates render correctly with variable substitution

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_templates.py` |
