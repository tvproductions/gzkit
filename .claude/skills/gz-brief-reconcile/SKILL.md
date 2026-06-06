---
name: gz-brief-reconcile
description: Reconcile an OBPI brief against current project state and optionally write operator-attested amendments. Use when a brief's allowlist, discovery checklist, verification verbs, REQ count, or citation tuples may have drifted from reality.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-06
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

1. Confirm the target OBPI id and that its brief file exists.
2. Run `uv run gz brief reconcile <OBPI-ID>` to report per-dimension deltas.
   Exit 0 means clean; exit 3 means drift.
3. If drift is real and the amendments are correct, preview with
   `uv run gz brief reconcile <OBPI-ID> --apply --attestor "<name>" --dry-run`.
4. Apply with `uv run gz brief reconcile <OBPI-ID> --apply --attestor "<name>"`.
   Unresolved verbs are recorded as tracked defects, never silently rewritten.

## Validation

- Re-run `uv run gz brief reconcile <OBPI-ID>` after `--apply`; confirm the
  expected dimensions now report zero (or the residual is intentional).
- Confirm the `brief_reconciled` ledger event was emitted (and
  `brief_reconcile_drift_detected` when drift was present).

## Example

Use $gz-brief-reconcile to reconcile an OBPI brief against project state before
completion.
