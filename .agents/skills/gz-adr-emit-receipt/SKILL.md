---
name: gz-adr-emit-receipt
description: Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events.
category: adr-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-18
metadata:
  skill-version: "1.0.2"
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
  --evidence-json '{"scope": "ADR-X.Y.Z", "date": "YYYY-MM-DD", "receipts": ["arb-ruff-<id>", "arb-step-typecheck-<id>", "arb-step-unittest-<id>", "arb-step-mkdocs-<id>"]}'
```

On **Heavy** lane / **foundation** kind, the `--evidence-json` payload MUST carry the
`arb-*` receipt IDs emitted by the canonical ARB steps (`gz arb ruff`, `gz arb typecheck`,
`gz arb step --name unittest ...`, `gz arb step --name mkdocs ...`). A zero-receipt payload
fail-closes at exit 3 before the receipt is recorded (locked by `CANONICAL_STEP_COMMANDS`;
see AGENTS.md § Attestation).

The `$gz-adr-emit-receipt` token used in some agent integrations
(e.g. `agents/openai.yaml`) is a slash-command alias that resolves to
the literal `uv run gz adr emit-receipt ...` invocation above; agents
without slash-command resolution must invoke the literal CLI directly.
