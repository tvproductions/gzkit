---
id: OBPI-0.7.0-01-obpi-completion-validator-gate
parent: ADR-0.7.0-obpi-first-operations
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.7.0-01-obpi-completion-validator-gate: Obpi Completion Validator Gate

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #1 — "Implement OBPI completion validator gate parity."

**Status:** Completed

## Objective

Add a pre-completion validator gate that blocks OBPI `Completed` transitions when required evidence or human attestation prerequisites are not satisfied.

### Implementation Summary

- Files created: `src/gzkit/hooks/obpi.py` (Validator Engine)
- Files modified: `src/gzkit/cli.py` (added `obpi validate` command), `src/gzkit/hooks/core.py` (hook integration)
- Tests added: `tests/test_obpi_validator.py` (8 scenarios)
- Date completed: 2026-03-04

## Key Proof

```bash
# Validating a completed OBPI with missing evidence fails:
uv run gz obpi validate tests/fixtures/invalid_obpi.md
# Output: [BLOCK] Missing or non-substantive 'Implementation Summary'.
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Looks good, validation rigor matches AirlineOps parity."
- Date: 2026-03-04
