# Plan: OBPI-0.25.0-01 Attestation Pattern Comparison

## Context

ADR-0.25.0 evaluates 17 airlineops core/common modules for upstream absorption into gzkit. OBPI-0.25.0-01 is the first: compare `airlineops/core/attestation.py` (511 lines) against gzkit's attestation surface and record a decision (Absorb/Confirm/Exclude).

After thorough exploration of both codebases, the recommended decision is **Confirm** — gzkit's attestation infrastructure is categorically more sophisticated across every dimension.

## Decision Rationale

| Dimension | airlineops (511 lines, 1 file) | gzkit (~2000+ lines, 10+ files) | Winner |
|-----------|-------------------------------|--------------------------------|--------|
| Architecture | Standalone module, cycle-based | Distributed multi-module with unified ledger | gzkit |
| Attestation model | 3 responses (approved/rejected/deferred) | Multi-level: ADR + OBPI attestation, canonical terms, force bypass with validation | gzkit |
| Evidence model | SHA256 hashes (world_state, contract, transcript) | Structured REQ-proof inputs, value narrative, key proof, scope audit | gzkit |
| Ceremony | CeremonyRecord model with transcript hash | 11-step closeout pipeline with state machine | gzkit |
| State derivation | Simple summary queries | Composite state machine: 7 runtime states, 4 proof states, drift detection | gzkit |
| Error handling | Single AttestationError, silent skip of malformed records | GzCliError, PolicyBreachError, transactional rollback, input validation | gzkit |
| Domain specificity | AIRAC cycle organization (airline-specific) | ADR/OBPI organization (governance-generic) | N/A |

The only generic patterns in airlineops (JSONL append-only ledger, CommandExecution tracking, hash-based evidence) are already subsumed by gzkit's Ledger class, ARB receipts, and structured proof system.

## Implementation Steps

### Step 1: Update the OBPI brief with comparison and decision

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-01-attestation-pattern.md`

Changes:
1. Update frontmatter `status: Pending` → `status: Completed`
2. Add `## Decision` section after REQUIREMENTS: **Confirm** with rationale
3. Add `## Comparison Analysis` section with six-dimension comparison table
4. Add `## Gate 4 BDD: N/A Rationale` — Confirm decision produces no code or behavior changes
5. Populate Evidence sections: Gate 1, Gate 2 (existing tests pass), Code Quality, Value Narrative, Key Proof, Implementation Summary
6. Check acceptance criteria checkboxes (REQ-01 through REQ-05)
7. Check completion checklist gates (1-4, leave Gate 5 for pipeline)
8. Author Closing Argument
9. Add Brief Status/Date Completed footer

### Step 2: Run verification commands

```bash
test -f ../airlineops/src/airlineops/core/attestation.py   # EXISTS
test -f src/gzkit/commands/attest.py                        # EXISTS
rg -n 'Confirm' docs/design/adr/.../obpis/OBPI-0.25.0-01-attestation-pattern.md  # Found
uv run gz test                                              # Green
uv run gz lint                                              # Clean
uv run gz typecheck                                         # Clean
```

No code changes are needed for a Confirm decision — only the brief update.

## Critical Files

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-01-attestation-pattern.md` — the only file to edit
- `../airlineops/src/airlineops/core/attestation.py` — source under comparison (read-only)
- `src/gzkit/commands/attest.py` — gzkit attestation command (read-only, for evidence)
- `src/gzkit/ledger_semantics.py` — gzkit state derivation (read-only, strongest evidence)

## Verification

After brief update:
- `uv run gz test` passes (no code changes)
- `uv run gz lint` clean
- `uv run gz typecheck` clean
- Brief contains "Confirm" decision with comparison rationale
