# OBPI Runtime Contract

**Status:** Active
**Last reviewed:** 2026-03-10
**Parent ADR:** `ADR-0.10.0-obpi-runtime-surface`

---

## Overview

The OBPI runtime contract defines the machine-readable state model used by
ledger-derived OBPI status, reconciliation, and later lifecycle/proof surfaces.

Execution boundaries, allowlist scope law, changed-files auditing, spine-touch
serialization, and parallel-safe blocker rules are defined separately in the
[OBPI Transaction Contract](obpi-transaction-contract.md).

The contract is ledger-first:

- runtime state is derived from `.gzkit/ledger.jsonl`
- brief evidence refines or blocks completion semantics
- no alternate planner or store is authoritative

The canonical implementation boundary is `derive_obpi_semantics()` in
`src/gzkit/ledger.py`.

---

## Canonical Runtime Fields

Derived OBPI payloads expose these stable fields:

- `runtime_state`
- `proof_state`
- `attestation_requirement`
- `attestation_state`
- `req_proof_state`
- `req_proof_inputs`
- `req_proof_summary`
- `completed`
- `ledger_completed`
- `evidence_ok`
- `anchor_state`
- `anchor_commit`
- `current_head`
- `anchor_issues`
- `anchor_drift_files`
- `issues`

---

## Runtime States

| State | Meaning |
|------|---------|
| `pending` | No completed proof has been recorded yet. |
| `in_progress` | Some proof or brief evidence exists, but completion requirements are not satisfied. |
| `completed` | Lite-compatible completion proof is present. |
| `attested_completed` | Heavy/Foundation-compatible completion proof is present with attestation evidence. |
| `validated` | A validated receipt exists on top of completed proof. |
| `drift` | Ledger/brief evidence disagree, or anchor-aware reconciliation found explicit blockers on completed proof. |

Completion accounting is separate from drift signaling. A row may still report
`completed: true` when proof is intact but `runtime_state: drift` because
anchor-aware reconciliation found closeout blockers.

---

## Proof and Attestation Contract

### `proof_state`

`proof_state` is one of:

- `missing`
- `partial`
- `recorded`
- `validated`

`validated` is reserved for validated runtime state. Otherwise `proof_state`
tracks the summarized REQ-proof input state.

### `attestation_requirement`

`attestation_requirement` is one of:

- `optional`
- `required`

Heavy/Foundation completion semantics require attestation proof before an OBPI
can be treated as `attested_completed`.

### `attestation_state`

`attestation_state` is one of:

- `not_required`
- `missing`
- `recorded`

---

## REQ Proof Inputs

`req_proof_inputs` is a normalized list of proof items. Each item must include:

- `name`
- `kind`
- `source`
- `status`

Optional fields:

- `scope`
- `gap_reason`

Allowed `kind` values:

- `command`
- `artifact`
- `brief_section`
- `attestation`
- `legacy_key_proof`

Allowed `status` values:

- `present`
- `missing`

When explicit proof inputs are absent, normalization may backfill them from:

- substantive `Key Proof` brief content
- recorded human-attestation evidence

This preserves compatibility for older receipts while keeping later consumers on
one stable machine-readable shape.

---

## Completed Receipt Context

Completed `obpi_receipt_emitted` events may also carry the recorder context that
later reconciliation consumes directly from ledger evidence:

- `scope_audit`
  - `allowlist`
  - `changed_files`
  - `out_of_scope_files`
- `git_sync_state`
  - `branch`
  - `remote`
  - `head`
  - `remote_head`
  - `dirty`
  - `ahead`
  - `behind`
  - `diverged`
  - `actions`
  - `warnings`
  - `blockers`
- `recorder_source`
- `recorder_warnings`

Anchor-aware reconciliation consumes these fields directly:

- if `HEAD` moved but no recorded-scope files changed, `anchor_state` remains
  non-blocking (`scope_clean`)
- if recorded-scope files changed since the completion anchor,
  `anchor_state = stale` and reconciliation fails closed
- if the completed receipt is missing anchor data or recorded degraded
  `git_sync_state`, reconciliation emits explicit blockers

The canonical derived anchor states are:

- `not_applicable`
- `not_tracked`
- `current`
- `scope_clean`
- `stale`
- `missing`
- `degraded`

---

## Compatibility Boundaries

- OBPI-scoped receipts with `adr_completion: not_completed` do not promote ADR
  lifecycle to `Validated`.
- Runtime consumers must not weaken the fail-closed transaction rules defined in
  the [OBPI Transaction Contract](obpi-transaction-contract.md).
- Legacy receipts without explicit `req_proof_inputs` remain consumable through
  fallback normalization.
- Human attestation remains the authority boundary for Heavy/Foundation
  completion.
- Status and reconciliation surfaces may render this contract differently, but
  they must consume the same derived semantics.
