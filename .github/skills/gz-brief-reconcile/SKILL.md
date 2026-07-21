---
name: gz-brief-reconcile
description: Reconcile an OBPI brief against current project state and optionally write operator-attested amendments. Use when a brief's allowlist, discovery checklist, verification verbs, REQ count, or citation tuples may have drifted from reality.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-21
metadata:
  skill-version: "0.3.0"
model: haiku
gz_command: gz brief reconcile
---

# gz brief reconcile

## Overview

Operate the `gz brief reconcile` command surface as a reusable governance
workflow. It wraps the OBPI-0.0.37-05 reconciliation engine to detect drift
between an OBPI brief and the project tree across five dimensions — allowlist,
discovery checklist, verification verbs, REQ count, and citation tuples — and
records the result to the ledger (invariant CIC-2, brief↔reality coherence).

## When to Use

- Before Stage 2 implementation, to confirm a brief still matches project shape.
- Before OBPI completion, to confirm zero residual drift.
- Whenever a brief's allowlist or REQ set looks stale relative to the code.

## Workflow

1. Confirm the target OBPI id and that its brief file exists. **Check its
   `status:` first** — a terminal brief (`Completed`, `attested_completed`,
   `Validated`, `Superseded`, `archived`, `Promoted`, `Abandoned`, `Withdrawn`) reports deltas but never
   gates: `has_drift` is always false and the run exits 0. Its deltas read as
   *"what moved since this shipped"*, never as a repair worklist. Do not run
   `--apply` on one — the amendment would rewrite a sealed record under an
   attestation no operator can honestly give (GHI #707).
2. Run `uv run gz brief reconcile <OBPI-ID>` to report per-dimension deltas.
   Exit 0 means clean; exit 3 means drift. On a live (non-terminal) brief only.
3. If drift is real and the amendments are correct, preview with
   `uv run gz brief reconcile <OBPI-ID> --apply --attestor "<name>" --dry-run`.
4. Apply with `uv run gz brief reconcile <OBPI-ID> --apply --attestor "<name>"`.
   Unresolved verbs are recorded as tracked defects, never silently rewritten.
   `--apply` re-measures the brief after writing and reports that second
   measurement, so the exit contract in step 2 binds here too: exit 3 means
   drift survived the amendment (`--apply` repairs the allowlist dimension
   only), not that the write failed.

## Validation

- The exit code already reflects the post-amendment brief — a re-run is a
  confirmation, not the measurement. Confirm the expected dimensions now
  report zero (or the residual is intentional and tracked).
- Confirm the `brief_reconciled` ledger event was emitted (and
  `brief_reconcile_drift_detected` when drift was present).

## Example

Use $gz-brief-reconcile to reconcile an OBPI brief against project state before
completion.
