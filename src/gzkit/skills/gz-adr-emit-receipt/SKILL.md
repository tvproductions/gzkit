---
name: gz-adr-emit-receipt
description: Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events.
category: adr-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-18
metadata:
  skill-version: "1.0.1"
model: haiku
---

# gz adr emit-receipt

## Overview

Operate the gz adr emit-receipt command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz adr emit-receipt with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

```bash
uv run gz adr emit-receipt ADR-X.Y.Z \
  --event validated \
  --attestor "human:Jane Doe" \
  --evidence-json '{"gate": 5, "tests_passed": true, "coverage_pct": 48.5}'
```

The `$gz-adr-emit-receipt` token used in some agent integrations
(e.g. `agents/openai.yaml`) is a slash-command alias that resolves to
the literal `uv run gz adr emit-receipt ...` invocation above; agents
without slash-command resolution must invoke the literal CLI directly.
