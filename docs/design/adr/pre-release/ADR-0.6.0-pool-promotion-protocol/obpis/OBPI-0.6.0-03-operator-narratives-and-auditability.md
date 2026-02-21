---
id: OBPI-0.6.0-03-operator-narratives-and-auditability
parent: ADR-0.6.0-pool-promotion-protocol
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.6.0-03-operator-narratives-and-auditability

**Brief Status:** Completed

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md`
- **Checklist Item:** #3 -- "Publish operator-facing evidence and value narrative for promotion flow."

## Objective

Ensure promotion workflow outputs are operator-readable, evidence-based, and aligned with OBPI acceptance narratives rather than opaque state changes.

## Lane

**Heavy**

## Allowed Paths

- `docs/governance/GovZero/adr-lifecycle.md`
- `docs/user/commands/adr-promote.md`
- `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Operator docs MUST include the canonical promotion command and expected outcomes.
2. ADR/OBPI artifacts MUST contain evidence and value narrative sections.
3. Promotion state MUST be discoverable through status and ledger surfaces.

## Quality Gates

### Gate 1: ADR

- [x] Scope linked to parent ADR item.

### Gate 2: TDD

- [x] Status/audit behavior validated through command runs and ledger inspection.

### Gate 3: Docs

- [x] Command and governance docs include promotion protocol and outputs.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI acceptance recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] Promotion manpage documents protocol and examples.
- [x] Governance lifecycle doc defines lineage outputs (`promoted_to`, `artifact_renamed`).
- [x] ADR and OBPI records include explicit evidence/value narrative sections.

## Evidence

### Implementation Summary

- Files modified: `src/gzkit/cli.py`, `src/gzkit/ledger.py`, `src/gzkit/schemas/ledger.json`, `tests/test_cli.py`, `tests/test_ledger.py`, `docs/user/commands/obpi-emit-receipt.md`, `docs/user/commands/index.md`, `docs/user/runbook.md`, `docs/user/concepts/obpis.md`, `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md`, `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/obpis/*.md`
- Operational evidence captured:
  - `uv run gz adr promote ADR-pool.pool-promotion-protocol --semver 0.6.0 --dry-run`
  - `uv run gz adr promote ADR-pool.pool-promotion-protocol --semver 0.6.0`
  - `uv run gz obpi emit-receipt OBPI-0.6.0-02-promotion-command-lineage --event validated --attestor "human:Jeff" --dry-run`
  - `uv run gz adr status ADR-0.6.0-pool-promotion-protocol --show-gates`
- Date completed: 2026-02-21

## OBPI Acceptance Ceremony

### Value Narrative

Before this OBPI, promotion outcomes were not consistently surfaced as operator evidence and value framing. After this OBPI, promotion behavior is documented, auditable, and narrated through ADR/OBPI artifacts that explain why the change matters.

### Key Proof

- Command contract proof: `docs/user/commands/adr-promote.md` documents usage, options, and enforced protocol.
- OBPI receipt proof: `docs/user/commands/obpi-emit-receipt.md` documents first-class OBPI receipt emission and ledger contract.
- Governance proof: `docs/governance/GovZero/adr-lifecycle.md` documents promotion lineage effects.
- Runtime proof: `uv run gz adr status ADR-0.6.0-pool-promotion-protocol --show-gates` exposes OBPI completion and gate posture.
