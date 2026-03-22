---
id: OBPI-0.24.0-01-documentation-taxonomy
parent_adr: ADR-0.24.0-skill-documentation-contract
status: Pending
lane: lite
date: 2026-03-21
---

# OBPI-0.24.0-01: Documentation Taxonomy

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.24.0-01 — "Define documentation taxonomy — rationale for when manpages, runbook entries, and docstrings are required"`

## OBJECTIVE

Define and document the three-layer documentation taxonomy for gzkit: what artifact types require manpages, what requires runbook entries, and what requires docstrings — with explicit rationale for each requirement.

## ASSUMPTIONS

- The taxonomy applies to all operator-facing artifacts, not just skills
- The existing command manpage convention is correct and should be formalized, not redesigned
- The taxonomy is a governance artifact, not a code artifact

## NON-GOALS

- Writing actual manpages or runbook entries (covered by OBPIs 02-05)
- Changing the existing command manpage structure
- Automating documentation coverage checks (future chore)

## REQUIREMENTS (FAIL-CLOSED)

1. Define which artifact types require manpages (CLI commands, skills, others) — manpages provide exacting, extensive detail so operators and agents know exactly what a tool does and how to use it
1. Define which artifact types require runbook entries (workflow participants) — runbooks capture end-to-end overarching workflows: where to start, what to run, how workflows connect
1. Define which artifact types require docstrings (code-backed artifacts) — docstrings link back to manpages and runbooks, reinforcing intent and pointing to the broader workflow context
1. State the rationale for each: what question does each layer answer, for whom, at what time. The goal: neither operators nor agents should have to guess at the intent of anything in gzkit
1. Document the linkage model: docstrings reference manpages, manpages reference runbook workflow positions, runbooks orchestrate the end-to-end narrative
1. Locate the taxonomy in governance docs so it's discoverable and enforceable

## ALLOWED PATHS

- `docs/governance/` — taxonomy governance artifact
- `docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/` — this ADR and briefs

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes with taxonomy document
- [ ] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `rg -n "Manpages|Runbook entries|Docstrings|Linkage model" docs/governance/documentation-taxonomy.md`
- `rg -n "documentation-taxonomy\\.md" docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`
