---
name: gz-state
description: Query artifact relationships and readiness state. Use when reporting lineage or artifact graph status.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "0.2.0"
model: haiku
---

# gz state

## Overview

Read the artifact graph the ledger derives: every PRD, ADR and OBPI with its
type, parent and attestation. `gz state` is a Layer 3 view of the ledger, so
cite it for an artifact's relationships, and read completion from the ledger
through `gz obpi status` or `gz adr status`.

- With no flag it prints the `Artifact State` table (ID, Type, Parent,
  Attested). `--full` folds long IDs instead of truncating them.
- `--json` prints the whole graph, including ADR lifecycle fields
  (`lifecycle_status`, `closeout_phase`, `attestation_term`) and, for an OBPI
  with TASKs, a `task_summary` with counts by status.
- `--blocked` keeps only unattested artifacts. That is every pool ADR and
  pending OBPI, not only work that is blocked.
- `--ready` keeps only unattested ADRs whose lane-required gates are satisfied,
  that is, ADRs ready for attestation.
- Withdrawn OBPIs are hidden, and removed from their parent's children;
  `--include-withdrawn` shows them.

`--repair` is the one mode that writes. It ignores the query flags and sets
each OBPI brief's frontmatter `status` from the ledger: `Completed` when the
ledger records completion, `Abandoned` when it records withdrawal, unchanged
otherwise. A terminal brief is never overwritten. It has no dry run.

## Workflow

1. Query: `uv run gz state`, or `--json`, `--blocked`, `--ready`,
   `--include-withdrawn` as the question needs. Add `--full` when IDs are
   quoted as evidence.
2. Before `--repair`, tell the operator that it edits brief files. Run it, then
   report its `State Repair Results` table, or `All frontmatter is aligned with
   ledger state. No changes.`, and include the changed files in the commit.

## Example

```bash
uv run gz state --ready
uv run gz state --json
uv run gz state --repair
```
