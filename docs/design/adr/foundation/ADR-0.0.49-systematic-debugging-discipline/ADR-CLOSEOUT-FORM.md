# ADR Closeout Form: ADR-0.0.49-systematic-debugging-discipline

**Status**: Phase 1 — Pending Implementation

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.49-systematic-debugging-discipline` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.49-01-author-systematic-debug-skill](obpis/OBPI-0.0.49-01-author-systematic-debug-skill.md) | Author `gz-systematic-debug` skill at `.gzkit/skills/gz-systematic-debug/SKILL.md` | Draft |
| [OBPI-0.0.49-02-author-investigator-persona](obpis/OBPI-0.0.49-02-author-investigator-persona.md) | Author `investigator` persona at `.gzkit/personas/investigator.md` | Draft |
| [OBPI-0.0.49-03-agents-md-integration](obpis/OBPI-0.0.49-03-agents-md-integration.md) | AGENTS.md integration (DO IT RIGHT #10/#11, PRIME DIRECTIVE cross-ref, Behavior Rule Always #14, Personas table, Skills catalog) | Draft |
| [OBPI-0.0.49-04-ghi-skills-cross-link](obpis/OBPI-0.0.49-04-ghi-skills-cross-link.md) | Cross-link GHI skills (`ghi-author`, `ghi-close`) to systematic debugging at three coupling points | Draft |
| [OBPI-0.0.49-05-systematic-debugging-rule-file](obpis/OBPI-0.0.49-05-systematic-debugging-rule-file.md) | Author `.gzkit/rules/systematic-debugging.md` + scorecard entry | Draft |

## Defense Brief

### Closing Arguments

*To be populated during closeout ceremony.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.49-01-author-systematic-debug-skill | governance_artifact | PENDING |
| OBPI-0.0.49-02-author-investigator-persona | governance_artifact | PENDING |
| OBPI-0.0.49-03-agents-md-integration | governance_artifact | PENDING |
| OBPI-0.0.49-04-ghi-skills-cross-link | governance_artifact | PENDING |
| OBPI-0.0.49-05-systematic-debugging-rule-file | governance_artifact | PENDING |

### Reviewer Assessment

*To be populated during closeout ceremony.*


## Human Attestation

### Verbatim Attestation

*To be recorded at closeout per ADR-0.0.36 universal OBPI attestation.*

**Attested by**: _g0_
**Timestamp (UTC)**: _Pending_
