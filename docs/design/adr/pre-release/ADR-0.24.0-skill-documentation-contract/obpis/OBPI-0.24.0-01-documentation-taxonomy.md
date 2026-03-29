---
id: OBPI-0.24.0-01-documentation-taxonomy
parent: ADR-0.24.0-skill-documentation-contract
item: 1
status: Completed
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

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run mkdocs build --strict` passes with taxonomy document
- [x] Code Quality: `uv run gz lint` passes

## VERIFICATION COMMANDS

- `uv run mkdocs build --strict`
- `rg -n "Manpages|Runbook entries|Docstrings|Linkage model" docs/governance/documentation-taxonomy.md`
- `rg -n "documentation-taxonomy\\.md" docs/design/adr/pre-release/ADR-0.24.0-skill-documentation-contract/ADR-0.24.0-skill-documentation-contract.md`

## Closing Argument

### Implementation Summary

- Created: `docs/governance/documentation-taxonomy.md` — three-layer taxonomy defining manpage, runbook, and docstring requirements per artifact type
- Added: mkdocs.yml navigation entry under Governance (Canonical) section
- Documented: linkage model (docstrings -> manpages -> runbooks) with code and markdown examples
- Documented: SKILL.md vs manpage audience split (agent vs operator)
- Documented: enforcement gap with GHI tvproductions/gzkit#40 tracking automated skill audit

### Key Proof

```bash
$ rg -n "Manpages|Runbook entries|Docstrings|Linkage model" docs/governance/documentation-taxonomy.md
27:### Manpages
55:### Runbook entries
82:### Docstrings
158:Docstrings ──reference──► Manpages ──reference──► Runbooks
```

```bash
$ uv run mkdocs build --strict
INFO - Documentation built in 0.93 seconds
```

All six FAIL-CLOSED requirements verified by independent spec reviewer (PASS, 6/6 MET).
