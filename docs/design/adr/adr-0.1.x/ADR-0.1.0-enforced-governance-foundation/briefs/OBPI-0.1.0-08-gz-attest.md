---
id: OBPI-0.1.0-08
parent: ADR-0.1.0
item: 8
lane: Heavy
status: Pending
---

# OBPI-0.1.0-08: Implement gz attest

## Objective

Implement `gz attest` command that records human attestation with ledger event.

## Parent ADR

- **ADR**: [ADR-0.1.0-enforced-governance-foundation](../ADR-0.1.0-enforced-governance-foundation.md)
- **Checklist Item**: #8 (AC-008: Attestation Command)

## Lane

**Heavy** — External CLI contract

## Allowed Paths

- Prompt for attestation term (Completed / Partial / Dropped)
- Validate required gates are passing (per lane)
- Record attestation with timestamp and identity in ADR
- Append `attested` event to ledger
- Support `--reason` for Partial/Dropped rationale
- Support `--force` to override gate failures with warning

## Denied Paths

- Auto-attesting without human confirmation
- Attesting without gate validation (unless `--force`)

## Requirements

- Attestation terms must be canonical (Completed / Partial / Dropped)
- Ledger event must include term, identity, and timestamp
- Gate failures must block attestation by default

## Acceptance Criteria

- [ ] `gz attest` prompts for term
- [ ] Attestation records timestamp and identity
- [ ] `attested` event appended to ledger
- [ ] `gz attest` fails if gates not passing (without `--force`)
- [ ] `gz attest --force` overrides with warning
- [ ] `gz attest --reason` records rationale for Partial/Dropped

## Gate Evidence

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 2 (TDD) | Tests pass | `uv run -m unittest tests/test_cli.py` |
