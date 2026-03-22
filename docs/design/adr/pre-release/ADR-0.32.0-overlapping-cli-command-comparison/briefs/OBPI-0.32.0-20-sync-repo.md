---
id: OBPI-0.32.0-20-sync-repo
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-20: sync-repo

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-20 -- "Compare sync-repo -- opsdev sync_repo.py 81 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `sync-repo` command (sync_repo.py, 81 lines) against gzkit's equivalent in cli.py. The sync-repo command synchronizes repository state -- configuration, control surfaces, and governance artifacts. Determine whether opsdev's 81-line implementation handles synchronization steps that gzkit lacks.

## SOURCE MATERIAL

- **opsdev:** `sync_repo.py` (81 lines)
- **gzkit equivalent:** `cli.py` (sync-repo section)

## ASSUMPTIONS

- Both synchronize governance artifacts across the repository
- 81 lines is moderate; implementations may be comparable
- Synchronization order and idempotency matter

## NON-GOALS

- Changing synchronization targets
- Adding new sync steps without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: sync steps, ordering, idempotency, error handling
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
