---
id: OBPI-0.7.0-01-obpi-completion-validator-gate
parent: ADR-0.7.0-obpi-first-operations
item: 1
lane: Heavy
status: attested_completed
---

# OBPI-0.7.0-01-obpi-completion-validator-gate: Obpi Completion Validator Gate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #1 — "Implement OBPI completion validator gate parity."

**Status:** Completed

## Objective

Add a pre-completion validator gate that blocks OBPI `Completed` transitions when required evidence or human attestation prerequisites are not satisfied.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 (Mode C — derived from Objective, Implementation Summary, and Key Proof).
-->

- [x] REQ-0.7.0-01-01: Given an OBPI brief lacking required evidence, when `gz obpi validate` is run, then the validator emits a `[BLOCK]` message and refuses the Completed transition.
- [x] REQ-0.7.0-01-02: Given a Heavy-lane OBPI lacking human attestation, when validation runs, then the validator blocks the Completed transition until attestation is recorded.
- [x] REQ-0.7.0-01-03: Given the validator engine, when invoked, then it reports which specific section is missing or non-substantive (e.g. `Missing or non-substantive 'Implementation Summary'`).
- [x] REQ-0.7.0-01-04: Given the gzkit hook system, when an OBPI completion event is dispatched, then the validator runs as a hook before any completion side-effect.
- [x] REQ-0.7.0-01-05: Given the gzkit CLI, when `gz obpi validate <path>` is invoked, then a stand-alone validator subcommand executes the same checks the hook performs.

### Implementation Summary

- Files created: `src/gzkit/hooks/obpi.py` (Validator Engine)
- Files modified: `src/gzkit/cli.py` (added `obpi validate` command), `src/gzkit/hooks/core.py` (hook integration)
- Tests added: `tests/test_obpi_validator.py` (8 scenarios)
- Date completed: 2026-03-04

### Value Narrative

Before this OBPI, OBPI briefs could be marked Completed without any enforcement — there was no gate that checked whether required evidence or human attestation prerequisites were actually present. After this OBPI, a pre-completion validator blocks the Completed transition when evidence is missing, matching the AirlineOps parity contract for OBPI lifecycle enforcement.

### Key Proof

```bash
# Validating a completed OBPI with missing evidence fails:
uv run gz obpi validate tests/fixtures/invalid_obpi.md
# Output: [BLOCK] Missing or non-substantive 'Implementation Summary'.
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Looks good, validation rigor matches AirlineOps parity."
- Date: 2026-03-04
