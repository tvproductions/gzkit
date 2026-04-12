---
name: gz-adr-promote
description: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.1.0"
---

# gz adr promote

## Overview

Operate the gz adr promote command surface to transition pool (backlog) ADRs into versioned, executable ADR packages with preserved ledger lineage.

## Workflow

1.  **Identify the pool ADR**: Confirm the source ADR ID (e.g., `ADR-pool.ai-runtime-foundations`).
2.  **Determine the target version**: Confirm the target semantic version (e.g., `X.Y.Z`).
3.  **Decomposition Protocol (Two-Step)**:
    *   **Step 1: Baseline Structural Template (Rule of Three)**: Scaffold into three baseline layers (Registry, Core Execution, and Lifecycle/Operations).
    *   **Step 2: Refining Overlay (Matrix of Four)**: Apply the four core principles (Single-Narrative, Testability Ceiling, State Anchor, Surface Boundary) to each baseline unit. If a unit violates a principle, it MUST be further decomposed.
    *   **1:1 Synchronization**: The resulting Feature Checklist in the promoted ADR MUST remain in 1:1 synchronization with the generated OBPI brief files. No drift is permitted.
    *   Promotion is fail-closed unless the pool ADR already contains actionable `## Target Scope` bullets.
4.  **Run the promotion**:
    *   Preview with `--dry-run` if unsure of the layout.
    *   Execute: `uv run gz adr promote <POOL-ADR> --semver <X.Y.Z>`
5.  **Verify the transition**:
    *   Confirm the new ADR file exists in the correct SemVer bucket (`foundation/`, `pre-release/`, or `<major>.0/`).
    *   Confirm matching OBPI briefs were created under the promoted ADR `obpis/` directory.
    *   Confirm the original pool file is updated with `status: Superseded`.
    *   Confirm the ledger records an `artifact_renamed` event and `obpi_created` events for the generated briefs.

## Options

- `--semver`: (Required) The target version (e.g., `X.Y.Z`).
- `--slug`: Optional override for the target slug (defaults to slug derived from pool ID).
- `--lane`: Optional override for the lane (`lite` or `heavy`).

## Validation

- Run `uv run gz status` to see the new ADR in its versioned state.
- Run `uv run gz validate` to ensure referential integrity.

## Common Rationalizations

These thoughts mean STOP — you are about to violate the architectural boundary:

| Thought | Reality |
|---------|---------|
| "This pool ADR is post-1.0 but the work is interesting — promote it anyway" | The architectural memo (CLAUDE.md item 1) is fail-closed: post-1.0 pool ADRs do not get promoted while the spine, proof architecture, and pipeline lifecycle are unstable. "Interesting" is not the criterion. |
| "The pool ADR doesn't have actionable Target Scope bullets, but I know what it means" | Promotion is fail-closed without actionable scope. Your interpretation is not a substitute. Refine the pool ADR first. |
| "The Rule of Three feels like overengineering for this small ADR" | The decomposition protocol exists because ADRs that skip it produce briefs that drift during implementation. Small now, sprawling later. |
| "I'll create the OBPI briefs after the promote runs" | The 1:1 sync rule is mandatory: Feature Checklist must match generated briefs at promote time. Backfilling guarantees drift. |
| "The pool file's status is fine — I'll update it later" | The pool file MUST be marked Superseded as part of the promotion. Forgetting it means the ledger has two live ADRs for the same intent. |
| "I can skip `--dry-run`, I know the layout" | `--dry-run` costs nothing. The cost of a wrong-version promotion is recovering from a botched ledger rename. |
| "The original pool ADR was written years ago — it doesn't need re-evaluation" | Pool ADRs are intent. If the intent is years old, the foundation it assumed may not exist. Re-read CLAUDE.md item 1 before promoting. |

## Red Flags

- Promoting a pool ADR not on the active runtime track
- Promoting without confirming the target version against the architectural memo
- Resulting Feature Checklist count differs from generated OBPI brief count
- Original pool file not marked Superseded
- No `artifact_renamed` ledger event recorded
- Promote run without `--dry-run` first when target version is uncertain
- Decomposition Protocol skipped or applied superficially

## Example

Use $gz-adr-promote to promote a pool ADR into a canonical pre-release package.
