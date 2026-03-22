---
id: OBPI-0.24.0-04-runbook-skill-entries
parent_adr: ADR-0.24.0-skill-documentation-contract
status: Pending
lane: lite
date: 2026-03-21
---

# OBPI-0.24.0-04: Runbook Skill Invocation Entries

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.24.0-04 — "Add skill invocation entries to operator and governance runbooks"`

## OBJECTIVE

Add skill invocation entries to `docs/user/runbook.md` and `docs/governance/governance_runbook.md` at the natural workflow insertion points where operators should reach for skills.

## ASSUMPTIONS

- Skills participate in identifiable workflows (ADR lifecycle, quality checks, governance ceremonies, etc.)
- The runbook already has workflow sections where skills naturally fit
- Not every skill needs a runbook entry — only those that participate in documented workflows

## NON-GOALS

- Rewriting runbook structure or workflow sequences
- Documenting skills that are purely agent-internal (no operator invocation point)
- Creating new workflow sections in runbooks (only adding to existing sections)

## REQUIREMENTS (FAIL-CLOSED)

1. Identify workflow insertion points in `docs/user/runbook.md` where operator-invocable skills should be referenced
1. Identify workflow insertion points in `docs/governance/governance_runbook.md` for governance skills
1. Add skill references with brief context: what the skill does and why it's invoked at this point in the workflow
1. Link each runbook skill reference to the corresponding manpage in `docs/user/skills/`
1. Do not disrupt existing runbook flow — skill entries are additive

## ALLOWED PATHS

- `docs/user/runbook.md`
- `docs/governance/governance_runbook.md`
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Code Quality: `uv run gz lint` passes
