---
name: gz-plan
description: Create ADR artifacts for planned change. Use when recording architecture intent and lane-specific scope.
category: adr-lifecycle
metadata:
  skill-version: "1.1.0"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-20
---

# gz plan

## Overview

Operate the gz plan command surface as a reusable governance workflow.

## Workflow

1. **Spec Developer Phase:** Before planning or generating an ADR, act as a Spec Developer. Review the target context and aggressively spin up `Explore` subagents to search and read relevant code.

    **Pre-flight — defect-fix routing.** If this is an in-flight defect fix per `.gzkit/rules/defect-fix-routing.md` thresholds (≤10 source lines, ≤2 source files, in-flight trigger, ≥3 recent `fix(...)` precedents in the 60-day window, unit-test coverage viable), route to a direct `fix(<scope>): … (GHI #N)` commit instead of scaffolding an ADR. Default-to-ceremony for small in-flight defects is the exact over-application pattern GHI #195 authored the routing rule to prevent.
2. **Decomposition Protocol (Two-Step):**
    *   **Step 1: Baseline Structural Template (Rule of Three)**: For complex ADRs, scaffold into three baseline layers (Registry, Core Execution, and Lifecycle/Operations).
    *   **Step 2: Refining Overlay (Matrix of Four)**: Apply the four core principles (Single-Narrative, Testability Ceiling, State Anchor, Surface Boundary) to each baseline unit. If a unit violates a principle, it MUST be further decomposed.
    *   **1:1 Synchronization**: The resulting Feature Checklist in the ADR MUST remain in 1:1 synchronization with the generated OBPI brief files. No drift is permitted.
3. Present the assessment results and the resulting OBPI checklist to the user for approval.
4. Ask the user up to 20 non-obvious, clarifying questions to discover edge cases, dependencies, and potential regressions regarding the planned change. Do not generate the ADR until these questions are answered.
5. Once the scope and edge cases are clearly defined, confirm target context, IDs, and lane assumptions.
6. **Ask the operator for `--kind` explicitly.** `gz plan create` has no default kind — the operator must choose. Present the concise heuristic verbatim and wait for an answer; do not guess, do not propose a default.

    > **What kind of ADR is this?** `foundation` (app/system invariant, always 0.0.x) / `feature` (release-carrying capability) / `pool` (noted, not committed).
    >
    > Heuristic: Does this decision shape what the app IS (identity/invariant)? → `foundation`. Does this decision ship a named capability to users? → `feature`. Is this decision noted but not committed? → `pool`. For deeper context see `docs/user/concepts/adr-taxonomy.md`.

7. Run `uv run gz plan` with the required options, passing the operator's chosen `--kind` through verbatim.
8. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-plan to plan a new ADR with semver and lane options..
