---
id: OBPI-0.34.0-02-obpi-completion-recorder
parent: ADR-0.34.0-claude-hooks-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-02: obpi-completion-recorder

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-02 -- "Absorb obpi-completion-recorder.py -- records OBPI completions to ledger"`

## OBJECTIVE

Absorb airlineops's `obpi-completion-recorder.py` hook into gzkit. This hook records OBPI completion events to the governance ledger -- creating an audit trail of when OBPIs were completed, by which agent, and with what evidence. gzkit does not currently have this hook behavior. Evaluate the implementation and absorb it into gzkit's hook module architecture.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/obpi-completion-recorder.py`
- **gzkit equivalent:** None -- this is a new behavior for gzkit

## ASSUMPTIONS

- OBPI completion recording is governance-generic -- all governed projects need audit trails
- The recorder likely writes to the ledger (`.gzkit/ledger.jsonl`)
- This hook complements the completion validator (OBPI-01) -- validate then record
- Must integrate with gzkit's ledger infrastructure

## NON-GOALS

- Changing ledger format
- Recording non-OBPI events in this hook

## REQUIREMENTS (FAIL-CLOSED)

1. Read the airlineops implementation completely
1. Evaluate governance generality (expected: governance-generic)
1. Adapt to gzkit hook module architecture
1. Implement and write tests
1. Document the absorption rationale

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.34.0-02-01: Read the airlineops implementation completely
- [x] REQ-0.34.0-02-02: Evaluate governance generality (expected: governance-generic)
- [x] REQ-0.34.0-02-03: Adapt to gzkit hook module architecture
- [x] REQ-0.34.0-02-04: Implement and write tests
- [x] REQ-0.34.0-02-05: Document the absorption rationale


## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for new hook behavior
- `tests/` -- tests for new hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Absorption rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
