---
name: gz-obpi-brief-drift
description: Reconcile an OBPI brief against current project state and optionally write operator-attested amendments. Use when a brief's allowlist, discovery checklist, verification verbs, REQ count, or citation tuples may have drifted from reality.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.6.0"
model: haiku
gz_command: gz obpi brief-drift
---

# gz obpi brief-drift

## Overview

`gz obpi brief-drift` runs the OBPI-0.0.37-05 reconciliation engine to measure
drift between an OBPI brief and the project tree across five dimensions —
allowlist, discovery checklist, verification verbs, REQ count, and citation
tuples (invariant CIC-2, brief↔reality coherence). Every run, `--dry-run`
included, appends a `brief_reconciled` ledger event, plus
`brief_reconcile_drift_detected` when the result gates.

What gates depends on the brief's `status:`:

- **Terminal** (list in step 1): deltas are reported, nothing gates.
- **`Draft`**: allowlisted paths missing on disk and unresolved `gz` verbs are
  reported but do not gate, because they name what the OBPI will create. A
  Discovery Checklist path still gates unless a sibling OBPI's Allowed Paths
  create it; stale citations still gate.
- **Live** (`Active`, `in_progress`): allowlist, discovery, verification and
  citation drift all gate.

The REQ count delta never gates; it is reported for information.

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
   attestation no operator can honestly give (GHI #707). The CLI does not
   refuse it; this step is the only guard.
2. Run `uv run gz obpi brief-drift <OBPI-ID>` to report per-dimension deltas.
   Exit 0 means clean; exit 3 means drift. On a live (non-terminal) brief only.
3. If drift is real, preview with
   `uv run gz obpi brief-drift <OBPI-ID> --apply --dry-run`. The preview
   writes nothing to the brief and prints the same delta counts; it does not
   list the amendment text.
4. Apply with `uv run gz obpi brief-drift <OBPI-ID> --apply`. `--attestor`
   takes a handle, never a real name, and defaults to
   `authorship.attestor_handle` in `.gzkit.json`; `--apply` refuses without
   one. The write adds each `src/` module that the brief's REQ-covering tests
   import, that sits beside an allowlisted `src/` path, and that the brief
   neither allows nor denies — to frontmatter `allowlist:` on a structured
   brief, under `## Allowed Paths` on a legacy one — and records unresolved verbs and REQ identity drift under
   `## Tracked Defects`, never rewriting them. Allowlisted paths missing on
   disk, discovery and citation drift are not repaired.
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

Use $gz-obpi-brief-drift to reconcile an OBPI brief against project state before
completion.
