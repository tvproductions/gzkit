---
id: OBPI-0.4.0-03-sync-determinism-and-recovery
parent: ADR-0.4.0-skill-capability-mirroring
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.4.0-03-sync-determinism-and-recovery

**Brief Status:** Completed

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

- [x] Determinism and recovery tests added and passing.

### Gate 3: Docs

- [x] Sync/recovery operator docs updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI acceptance recorded (ADR-level Gate 5 attestation still pending at ADR closeout).

## Acceptance Criteria

- [x] Deterministic sync behavior is test-covered.
- [x] Recovery behavior is explicit and validated.
- [x] Invalid canonical state cannot silently propagate to mirrors.

## Evidence

### Implementation Summary

- Files created/modified: `src/gzkit/sync.py`, `src/gzkit/cli.py`, `tests/test_sync.py`, `tests/test_cli.py`, `docs/user/commands/agent-sync-control-surfaces.md`, `docs/user/commands/index.md`, `.gzkit/skills/gz-agent-sync/SKILL.md`, `.agents/skills/gz-agent-sync/SKILL.md`, `.claude/skills/gz-agent-sync/SKILL.md`, `.github/skills/gz-agent-sync/SKILL.md`
- Determinism/recovery contract: sync preflight now fail-closes on canonical skill corruption; sync output path list is deterministic; stale mirror-only paths are explicitly reported with non-destructive recovery steps
- Validation commands run: `uv run -m unittest tests.test_sync tests.test_cli.TestSyncCommand`, `uv run gz agent sync control-surfaces`, `uv run gz lint`, `uv run -m unittest`, `uv run gz check`
- Date completed: 2026-02-21

## OBPI Acceptance Ceremony

### Value Narrative

Before this OBPI, `gz agent sync control-surfaces` could propagate from an invalid canonical skill state and recovery behavior for stale mirror-only paths was implicit. After this OBPI, sync is deterministic for unchanged inputs, canonical corruption fails closed before mirror propagation, and stale mirror drift is surfaced with an explicit non-destructive recovery protocol.

### Key Proof

- Canonical corruption proof: `tests/test_cli.py` `test_agent_sync_fails_closed_on_canonical_skill_corruption` verifies sync exits non-zero before propagation.
- Recovery proof: `tests/test_cli.py` `test_agent_sync_reports_stale_mirror_recovery_non_destructively` verifies stale mirror-only paths are reported and preserved for manual cleanup.
- Determinism proof: `tests/test_sync.py` `test_sync_outputs_deterministic_updated_paths_for_unchanged_inputs` verifies stable updated-path output across repeated runs.

### Human Attestation

- Attested by: Jeff (human operator)
- Attestation: Accepted
- Method: explicit acceptance in session (`option 1`)
- Date: 2026-02-21
