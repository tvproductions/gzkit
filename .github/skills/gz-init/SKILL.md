---
name: gz-init
description: Initialize gzkit governance scaffolding for a repository. Use when bootstrapping or reinitializing project governance surfaces.
---

# gz init

## Overview

Operate the gz init command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz init with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-init to initialize a repository in the requested mode..
