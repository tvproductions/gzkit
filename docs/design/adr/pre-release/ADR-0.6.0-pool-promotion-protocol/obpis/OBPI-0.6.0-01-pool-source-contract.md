---
id: OBPI-0.6.0-01-pool-source-contract
parent: ADR-0.6.0-pool-promotion-protocol
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.6.0-01-pool-source-contract

**Brief Status:** Completed

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md`
- **Checklist Item:** #1 -- "Define pool source and archive contract for promotion."

## Objective

Define pool entry lifecycle semantics so active pool ADRs use `Pool`, while promoted entries are archived as `Superseded` with explicit forward linkage.

## Lane

**Heavy**

## Allowed Paths

- `docs/design/adr/pool/**`
- `docs/governance/GovZero/adr-lifecycle.md`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Active pool entries MUST use `status: Pool`.
2. Promoted pool entries MUST be retained as historical context with `status: Superseded`.
3. Promoted pool entries MUST include `promoted_to: ADR-X.Y.Z-slug`.

## Quality Gates

### Gate 1: ADR

- [x] Scope linked to parent ADR item.

### Gate 2: TDD

- [x] Promotion behavior covered by CLI tests.

### Gate 3: Docs

- [x] Pool and lifecycle protocol docs updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI acceptance recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] Pool status doctrine is explicit and consistent.
- [x] Promotion archival semantics are documented and enforced.
- [x] Pool index reflects active vs promoted lineage.

## Evidence

### Implementation Summary

- Files modified: `docs/design/adr/pool/README.md`, `docs/design/adr/pool/ADR-pool.pool-promotion-protocol.md`, `docs/governance/GovZero/adr-lifecycle.md`
- Contract delivered: Active pool entries now standardize on `Pool`; promoted entries are archived with `Superseded` and `promoted_to` metadata.
- Date completed: 2026-02-21

## OBPI Acceptance Ceremony

### Value Narrative

Before this OBPI, pool lifecycle semantics and promotion archival behavior were inconsistent. After this OBPI, the lifecycle contract is explicit, auditable, and consistent across protocol docs and pool artifacts.

### Key Proof

- `docs/design/adr/pool/README.md` now defines active pool status and canonical promotion command.
- `docs/governance/GovZero/adr-lifecycle.md` now documents promotion outputs and lineage requirements.
- `docs/design/adr/pool/ADR-pool.pool-promotion-protocol.md` shows archival promotion metadata (`status: Superseded`, `promoted_to`).
