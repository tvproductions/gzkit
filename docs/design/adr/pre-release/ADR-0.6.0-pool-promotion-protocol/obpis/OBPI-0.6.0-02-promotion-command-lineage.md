---
id: OBPI-0.6.0-02-promotion-command-lineage
parent: ADR-0.6.0-pool-promotion-protocol
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.6.0-02-promotion-command-lineage

**Brief Status:** Completed

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md`
- **Checklist Item:** #2 -- "Implement deterministic promotion command behavior and ledger lineage."

## Objective

Deliver a canonical command surface that promotes pool ADRs into canonical package structure and records promotion lineage as first-class ledger evidence.

## Lane

**Heavy**

## Allowed Paths

- `src/gzkit/cli.py`
- `tests/test_cli.py`
- `docs/user/commands/adr-promote.md`
- `docs/user/commands/index.md`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Promotion MUST reject non-pool source ADRs.
2. Promotion MUST route targets by semver bucket (`foundation`, `pre-release`, `<major>.0`).
3. Promotion MUST append an `artifact_renamed` event with reason `pool_promotion`.

## Quality Gates

### Gate 1: ADR

- [x] Scope linked to parent ADR item.

### Gate 2: TDD

- [x] `TestAdrPromoteCommand` added and passing in `tests/test_cli.py`.

### Gate 3: Docs

- [x] Command manpage and index entries updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI acceptance recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] `gz adr promote` exists with `--dry-run` and deterministic target path output.
- [x] Promoted ADR includes `promoted_from`, source pool file records `promoted_to`.
- [x] Ledger lineage event is written during non-dry-run promotion.

## Evidence

### Implementation Summary

- Files modified: `src/gzkit/cli.py`, `tests/test_cli.py`, `docs/user/commands/adr-promote.md`, `docs/user/commands/index.md`
- Tests added: `TestAdrPromoteCommand` validates dry-run planning, file writes, and non-pool rejection.
- Validation commands run:
  - `uv run -m unittest tests.test_cli.TestAdrPromoteCommand tests.test_cli.TestNewCommandParsers`
  - `uv run gz lint`
  - `uv run gz typecheck`
  - `uv run gz cli audit`
  - `uv run gz check`
- Date completed: 2026-02-21

## OBPI Acceptance Ceremony

### Value Narrative

Before this OBPI, pool-to-ADR promotion relied on manual file choreography and implicit lineage. After this OBPI, promotion is a single deterministic command with auditable ledger output.

### Key Proof

- Dry-run proof: `uv run gz adr promote ADR-pool.gz-chores-system --semver 0.6.0 --dry-run` prints planned target path and rename evidence.
- Write-path proof: command creates canonical ADR package and updates pool source metadata.
- Ledger proof: `artifact_renamed` is emitted with reason `pool_promotion`.
