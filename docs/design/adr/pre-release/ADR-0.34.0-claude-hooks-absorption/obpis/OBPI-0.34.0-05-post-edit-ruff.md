---
id: OBPI-0.34.0-05-post-edit-ruff
parent: ADR-0.34.0-claude-hooks-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.34.0-05: post-edit-ruff

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/ADR-0.34.0-claude-hooks-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.34.0-05 -- "Compare post-edit-ruff.py -- runs ruff after file edits"`

## OBJECTIVE

Compare airlineops's `post-edit-ruff.py` hook against gzkit's equivalent hook behavior. This hook automatically runs ruff (linting and formatting) after the agent edits Python files, ensuring code quality is maintained in real-time during agent work. Determine whether gzkit's existing post-edit hook covers the same behavior or whether airlineops's implementation handles more cases.

## SOURCE MATERIAL

- **airlineops:** `.claude/hooks/post-edit-ruff.py`
- **gzkit equivalent:** `src/gzkit/hooks/` -- post-edit ruff behavior in existing modules

## ASSUMPTIONS

- gzkit likely has a post-edit ruff hook (this is a fundamental quality hook)
- airlineops's version may handle edge cases: non-Python files, ruff failures, partial edits
- The comparison should focus on robustness and error handling

## NON-GOALS

- Changing ruff configuration
- Adding post-edit hooks for non-Python tools

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: file detection, ruff invocation, error handling, performance
1. Record decision: gzkit sufficient, or absorb airlineops improvements
1. If absorbing: integrate into gzkit hook module architecture and write tests
1. If confirming: document why gzkit's post-edit ruff is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.34.0-05-01: Read both implementations completely
- [x] REQ-0.34.0-05-02: Document comparison: file detection, ruff invocation, error handling, performance
- [x] REQ-0.34.0-05-03: Record decision: gzkit sufficient, or absorb airlineops improvements
- [x] REQ-0.34.0-05-04: If absorbing: integrate into gzkit hook module architecture and write tests
- [x] REQ-0.34.0-05-05: If confirming: document why gzkit's post-edit ruff is sufficient


## ALLOWED PATHS

- `src/gzkit/hooks/` -- target for absorbed hook behavior
- `tests/` -- tests for absorbed hook behavior
- `docs/design/adr/pre-release/ADR-0.34.0-claude-hooks-absorption/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
