---
name: gz-plan
description: Create ADR artifacts for planned change. Use when recording architecture intent and lane-specific scope.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz plan

## Overview

Operate the gz plan command surface as a reusable governance workflow.

## Workflow

1. **Spec Developer Phase:** Before planning or generating an ADR, act as a Spec Developer. Review the target context and aggressively spin up `Explore` subagents to search and read relevant code.
2. Ask the user up to 20 non-obvious, clarifying questions to discover edge cases, dependencies, and potential regressions regarding the planned change. Do not generate the ADR until these questions are answered.
3. Once the scope and edge cases are clearly defined, confirm target context, IDs, and lane assumptions.
4. Run `uv run gz plan` with the required options.
5. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-plan to plan a new ADR with semver and lane options..
