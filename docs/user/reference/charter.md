# The gzkit Charter

Status: Active
Version: 1.2
Authority: Canon (sole authority for covenant definitions)

This document defines the **Development Covenant** between human and agent.

Canonical GovZero source: [`docs/governance/GovZero/charter.md`](../../governance/GovZero/charter.md).
This page is a gzkit user overlay.

---

## Runtime Overlay Notes

The runtime preserves canonical authority while exposing additive operational semantics:

- Attestation tokens remain `completed|partial|dropped` for CLI stability.
- Outputs map to canonical terms: `Completed`, `Completed — Partial`, `Dropped`.
- Lifecycle/status surfaces are ledger-first (`attested`, `closeout_initiated`, `audit_receipt_emitted`).
- `gz audit` is strict post-attestation.
- `gz attest` enforces prerequisite gates by default; accountable override requires rationale.

---

## Canonical Principles

1. The human is index zero.
2. Agents present evidence; humans decide.
3. Ceremony must earn its place.
4. Silence is not attestation.

---

## Gate Summary

| Gate | Name | Scope |
|------|------|-------|
| 1 | ADR | All lanes |
| 2 | TDD | All lanes |
| 3 | Docs | Heavy lane |
| 4 | BDD | Heavy lane |
| 5 | Human | Heavy lane |

---

## Canonical Attestation Terms

- `Completed`
- `Completed — Partial: [reason]`
- `Dropped — [reason]`

---

## Operator Sequence

1. Orientation
2. Tool use and verification
3. Closeout presentation
4. Human attestation
5. Post-attestation audit
6. Receipt/accounting

---

For doctrine details, use the canonical GovZero docs under `docs/governance/GovZero/`.
