---
name: gz-adr-promote
description: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-04
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

## Example

Use $gz-adr-promote to promote a pool ADR into a canonical pre-release package.
