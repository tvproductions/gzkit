---
name: gz-cli-audit
description: Audit CLI documentation coverage and headings. Use when verifying command manpage and index parity.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz cli audit

## Overview

Operate the gz cli audit command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz cli audit with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-cli-audit to audit command docs and coverage..
