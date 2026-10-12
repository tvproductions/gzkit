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

During active OBPI pipeline execution, gzkit also persists a lightweight
machine-readable stage-state payload in:

- `.claude/plans/.pipeline-active-{OBPI-ID}.json`
- `.claude/plans/.pipeline-active.json`

That marker payload is compatibility state for active execution, not the
authority for completion semantics. Completion and lifecycle truth remain
ledger-first.

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

## Active Pipeline Marker Fields

While an OBPI pipeline is active, the marker payload exposes these stable
fields:

- `obpi_id`
- `parent_adr`
- `lane`
- `entry`
- `execution_mode`
- `current_stage`
- `position`
- `started_at`
- `updated_at`
- `receipt_state`
- `nonce`
- `blockers`
- `required_human_action`
- `next_command`
- `resume_point`

`entry` is how the run was launched and does not change as the run advances.
It is one of:

- `full`
- `verify`
- `ceremony`
- `sync`

`current_stage` is the stage the run has reached, which a full launch leaves
behind as it advances. It is one of the four canonical stages
(`CANONICAL_STAGES` in `src/gzkit/pipeline_stage_fence.py`):

- `implement`
- `verify`
- `ceremony`
- `sync`

`position` is where the run is inside `current_stage`: the last recorded
boundary it crossed. It is absent until a boundary is recorded after the
launch, and is never written as a `current_stage` value. It is an object with
exactly these fields, each a non-empty string:

- `kind` — `task` at `implement`, `phase` at `verify`, `round` at `ceremony`,
  `step` at `sync`
- `label` — the task the boundary marked, otherwise the boundary's name
- `boundary` — the command that marked the crossing

Each recorded boundary appends one `pipeline_stage_transition` event to the
ledger and then writes the same payload to both marker files, so every
position a marker carries has a Layer 2 source. A command that begins a
stage's work moves `current_stage`; a check or a bookkeeping event records its
position inside the stage already reached. The set of boundaries is
`RULED_BOUNDARIES` in `src/gzkit/pipeline_position.py`, and
[`gz obpi pipeline`](../../user/manpages/obpi-pipeline.md#where-the-run-is-stage-and-position)
lists it for operators. `uv run gz state --repair` restores a missing marker
file from its twin, or rebuilds both from those events
([`gz state`](../../user/manpages/state.md#repair-mode)).

`started_at` is the time of the launch. `updated_at` is the time of the last
recorded boundary, or of the launch when nothing follows it; reading a marker
never moves it.

`receipt_state` mirrors the Stage 1 plan-audit receipt classification used by
the runtime (`missing`, `pass`, `fail`, `invalid`, `other_obpi`, `unknown`).

`nonce` pairs the marker with its `pipeline_launched` ledger event.

`blockers` is a plain list of blocker strings for the active stage: what the
last failed verification found.

`required_human_action` is either `null` or the current stage's explicit human
action summary. It is populated while the run is at `ceremony`, in every lane:
human attestation is required for every OBPI completion (ADR-0.0.36).

`next_command` is either `null` or the next canonical operator command.

`resume_point` is either `null` or the stage label the operator should resume
from after clearing blockers or finishing the current stage.

A marker may also carry `dispatch_state` and `single_driver_declaration`,
caches of ledger records that no gate reads; a rebuild from the ledger does not
restore them.

Consumers must remain backward-compatible with older marker payloads that only
carry `obpi_id` and timestamp fields, and must ignore unknown future keys.

---

## Runtime States

| State | Meaning |
|------|---------|
| `pending` | No completed proof has been recorded yet. |
| `in_progress` | Some proof or brief evidence exists, but completion requirements are not satisfied. |
| `completed` | Lite-compatible completion proof is present. |
| `attested_completed` | Heavy-lane (any kind) or foundation-kind (any lane) completion proof is present with attestation evidence. |
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

Heavy-lane completion semantics (any kind) and foundation-kind completion
semantics (any lane) require attestation proof before an OBPI can be treated
as `attested_completed`. `kind` and `lane` are orthogonal axes; attestation
rigor keys on lane, with foundation-kind work additionally inheriting
ADR-0.0.18 walkthrough discipline regardless of lane.

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

`out_of_scope_files` lists changed files that are neither allowlisted nor one of
gzkit's own records (the transaction contract's Scope Isolation section names
them). Receipts written before 2026-10-10 list record files such as the ledger
there.

All three producers write this context: `gz obpi complete`, `gz obpi emit-receipt`
and the recorder hook. Dated record, 2026-10-09: receipts `gz obpi complete` wrote
from its introduction on 2026-04-05 until the repair under GHI #1181 do not carry
it, so a consumer must still treat each field as optional.

The intended pipeline ordering in gzkit is:

1. verify
2. ceremony / human attestation when required
3. guarded `git sync`
4. final completed receipt emission
5. downstream brief/ADR sync

That ordering makes the completed receipt the anchor for the synced
implementation state rather than for a clearly unsynced repository snapshot.

Anchor-aware reconciliation consumes these fields directly:

- if `HEAD` moved but no recorded-scope files changed, `anchor_state` remains
  non-blocking (`scope_clean`)
- if recorded-scope files changed since the completion anchor,
  `anchor_state = superseded`. Later work on the same files is expected and does
  not invalidate the anchor
- if the completed receipt is missing anchor data, `anchor_state = missing`; if
  the changes since the anchor cannot be inspected, `anchor_state = degraded`.
  Each carries an anchor issue
- `git_sync_state` recorded at receipt time is reported as an anchor note

Anchor issues and notes are informational at the OBPI level: they are listed
with the OBPI's reflection issues and do not change its runtime state. This has
been the behaviour of `src/gzkit/ledger_semantics.py` since commit `5b68226a1`
(2026-03-19), which replaced `stale` with `superseded`; this section said
otherwise until 2026-10-10 (GHI #1181).

The canonical derived anchor states are:

- `not_applicable`
- `not_tracked`
- `current`
- `scope_clean`
- `superseded`
- `missing`
- `degraded`
- `none` (a withdrawn or repudiated OBPI)

---

## Compatibility Boundaries

- OBPI-scoped receipts with `adr_completion: not_completed` do not promote ADR
  lifecycle to `Validated`.
- Runtime consumers must not weaken the fail-closed transaction rules defined in
  the [OBPI Transaction Contract](obpi-transaction-contract.md).
- Legacy receipts without explicit `req_proof_inputs` remain consumable through
  fallback normalization.
- Human attestation remains the authority boundary for heavy-lane
  completion (any kind) and foundation-kind completion (any lane).
- Status and reconciliation surfaces may render this contract differently, but
  they must consume the same derived semantics.
