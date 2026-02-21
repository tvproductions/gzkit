---
name: gz-attest
description: Record human attestation with prerequisite enforcement. Use when formally attesting ADR completion state.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz attest

## Overview

Operate the gz attest command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz attest with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-attest to record attestation for an ADR..
