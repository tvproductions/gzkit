---
name: gz-adr-promote
persona: main-session
description: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR.
category: adr-lifecycle
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-07
metadata:
  skill-version: "1.6.0"
model: sonnet
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
    *   Promotion is fail-closed unless the pool ADR contains an actionable `## Target Scope` section. When a `## Proposed OBPI Decomposition` table is also present, it is the preferred slug source (see Slug Source Contract below) — but it **supplements, not replaces**, `## Target Scope`. The Target Scope section is always required: it is preserved verbatim into the promoted ADR as the narrative scope.

### Slug Source Contract (GHI #241)

The promoter resolves OBPI slugs from the pool ADR in this order — author the
pool to hit the first path that fits:

1.  **`## Proposed OBPI Decomposition` table (preferred).** A markdown table
    with `Slug` and `Description` columns (a leading `#` column is fine; extra
    columns like `Lane` are ignored). The `Slug` column drives the OBPI name;
    the `Description` column becomes the Feature Checklist text.

    ```markdown
    ## Proposed OBPI Decomposition

    | # | Slug | Description | Lane |
    |---|------|-------------|------|
    | 01 | check-pipeline | Implement ordered check pipeline | Lite |
    | 02 | auto-repair-tier | Deterministic auto-repair executor | Lite |
    ```

2.  **`- **slug** — narrative` bullets in `## Target Scope`.** When every
    top-level bullet uses the bold-prefix convention, the bold text becomes
    the OBPI slug and the em-dash narrative becomes the checklist text.

    ```markdown
    ## Target Scope

    - **check-pipeline** — Implement ordered check pipeline with Pydantic models
    - **auto-repair-tier** — Deterministic auto-repair executor
    ```

3.  **Legacy narrative-only bullets (deprecated).** Still accepted for
    backward compatibility but emits a deprecation warning on promote. The
    full bullet text becomes both slug source and checklist text, which
    produces long, narrative-leaking OBPI slugs. Migrate to path 1 or 2.

Bullets nested under `### H3` subsections within `## Target Scope` are
**ignored** by paths 2 and 3 — only direct top-level bullets count as scope.
This means a pool ADR can safely decompose under a clean table (path 1) while
keeping rich prose in a `### Detailed specification` subsection below.
4.  **Run the promotion**:
    *   Preview with `--dry-run` if unsure of the layout.
    *   Execute: `uv run gz adr promote <POOL-ADR> --semver <X.Y.Z>`
5.  **Register the promoted ADR in the ledger (Mandatory):** `gz adr promote` emits `artifact_renamed` but does not emit `adr_registered`. Run `uv run gz register-adrs <NEW-ADR-ID>` immediately after promotion so `gz adr report` and downstream gates recognize the ADR. Skipping this step is the failure that produces "ADR exists on disk but is not registered in ledger" warnings.
6.  **Verify the transition**:
    *   Confirm the new ADR file exists in the correct SemVer bucket (`foundation/`, `pre-release/`, or `<major>.0/`).
    *   Confirm matching OBPI briefs were created under the promoted ADR `obpis/` directory.
    *   Confirm the original pool file is updated with `status: Superseded`.
    *   Confirm the ledger records an `adr_registered` event (from step 5) and `obpi_created` events for the generated briefs.

## Options

- `--semver`: (Required) The target version (e.g., `X.Y.Z`).
- `--slug`: Optional override for the target slug (defaults to slug derived from pool ID).
- `--lane`: Optional override for the lane (`lite` or `heavy`).
- `--kind`: Optional — specify the ADR kind (`foundation` or `feature`). When promoting, confirm whether the pool ADR becomes a foundation or feature ADR. Foundation = app/system invariant; Feature = release-carrying capability. Use the invariance test to resolve edge cases: *"Foundation = without it, we wouldn't be doing the project."* The hexagonal-ports lens clarifies: **ports point to invariance; adapters are features**. See `docs/user/concepts/foundation-feature-invariance-test.md` for worked examples and anti-patterns.

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

## Demote (inverse lifecycle)

`gz adr demote` reverses a promotion — moves an active pre-release ADR back to
the pool tier when the design intent needs re-scoping or the version slot must
be freed. Use when a promote was premature or the ADR needs fundamental rework.

```bash
# Demote a feature ADR back to pool (requires --ghi to anchor the reason)
uv run gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520

# Dry-run first to preview the demotion plan
uv run gz adr demote ADR-0.27.0-arb-receipt-system-absorption --ghi 520 --dry-run
```

## Example

Use $gz-adr-promote to promote a pool ADR into a canonical pre-release package.
