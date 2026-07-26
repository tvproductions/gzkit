---
name: gz-constitute
description: Create constitution artifacts. Use when governance constitutions must be created or refreshed.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-25
metadata:
  skill-version: "0.1.1"
model: opus
---

# gz constitute

## Overview


> **Self-Escalation (opus-tier).** Spawn an `Agent` with `model="opus"` to execute this skill. Pass the operator's request verbatim, any relevant context (ADR IDs, OBPI IDs, design topic, prior decisions), and instruct the subagent to read `.gzkit/skills/gz-constitute/SKILL.md` for the full workflow. Relay the subagent's output to the operator.

Operate the gz constitute command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz constitute with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-constitute to create a constitution document for this project..
