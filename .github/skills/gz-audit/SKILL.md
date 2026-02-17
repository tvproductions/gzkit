---
name: gz-audit
description: Run strict post-attestation reconciliation audits. Use after attestation to produce and verify audit artifacts.
---

# gz audit

## Overview

Operate the gz audit command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz audit with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-audit to run audit for the target ADR..
