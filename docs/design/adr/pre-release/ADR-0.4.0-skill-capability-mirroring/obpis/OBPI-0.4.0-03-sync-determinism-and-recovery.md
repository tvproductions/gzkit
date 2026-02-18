---
id: OBPI-0.4.0-03-sync-determinism-and-recovery
parent: ADR-0.4.0-skill-capability-mirroring
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.4.0-03-sync-determinism-and-recovery

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md`
- **Checklist Item:** #3 -- "Make sync deterministic and add recovery behavior."

## Objective

Harden `gz agent sync control-surfaces` so repeated runs are deterministic and drift/recovery behavior is explicit when canonical or mirrors diverge.

## Lane

**Heavy**

## Allowed Paths

- `src/gzkit/sync.py`
- `src/gzkit/cli.py`
- `.gzkit/skills/**`
- `.agents/skills/**`
- `.claude/skills/**`
- `.github/skills/**`
- `tests/test_sync.py`
- `tests/test_cli.py`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Sync outputs MUST be deterministic for unchanged inputs.
2. Recovery path MUST be documented when mirrors are stale or partially missing.
3. Sync MUST fail closed on canonical corruption rather than propagating invalid state.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Determinism and recovery tests added and passing.

### Gate 3: Docs

- [ ] Sync/recovery operator docs updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Deterministic sync behavior is test-covered.
- [ ] Recovery behavior is explicit and validated.
- [ ] Invalid canonical state cannot silently propagate to mirrors.
