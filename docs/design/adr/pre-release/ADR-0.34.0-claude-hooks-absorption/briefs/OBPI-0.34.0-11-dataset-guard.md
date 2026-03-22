---
id: OBPI-0.34.0-11-dataset-guard
parent_adr: ADR-0.34.0-claude-hooks-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-11: dataset-guard

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-11 -- "Evaluate dataset-guard.py -- guards dataset operations (domain-specific?)"`

## OBJECTIVE

Evaluate airlineops's `dataset-guard.py` hook to determine whether it is domain-specific (airline data protection) or governance-generic (general data file protection). This hook guards dataset operations -- preventing unauthorized modifications to data files that are under governance control. The "Evaluate" action indicates this hook may be domain-specific and needs careful assessment before any absorption decision.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/dataset-guard.py`
- **gzkit equivalent:** None

## ASSUMPTIONS

- This hook may protect airline-specific datasets (domain-specific)
- Alternatively, it may protect any governance-controlled data files (generic)
- The evaluation must determine which -- read the implementation before deciding
- If generic, the pattern of "guard data files from unauthorized modification" is valuable

## NON-GOALS

- Absorbing domain-specific data protection without generalization
- Guarding non-governance data files

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops implementation completely
1. Evaluate: Is the guard pattern domain-specific or governance-generic?
1. If domain-specific: document Exclude with rationale
1. If governance-generic: document Absorb, adapt to gzkit conventions, implement, and write tests
1. If partially generic: document which aspects to absorb and which to exclude

## ALLOWED PATHS

- `src/gzkit/hooks/` -- target if absorbing
- `tests/` -- tests if absorbing
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes (if absorbing)
- [ ] Gate 3 (Docs): Evaluation rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
