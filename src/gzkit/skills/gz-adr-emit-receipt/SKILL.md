---
name: gz-adr-emit-receipt
description: Emit ADR receipt events with scoped evidence payloads. Use when recording a completed, validated or closed ADR receipt event.
category: adr-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-26
metadata:
  skill-version: "1.1.0"
model: haiku
---

# gz adr emit-receipt

## Overview

Record one ADR receipt event (`completed`, `validated` or `closed`) in the
ledger with `uv run gz adr emit-receipt`.

## Workflow

1. Confirm the ADR ID and read its `lane` and `kind` from frontmatter; they
   decide what the evidence must carry.
2. Choose the event and build `--evidence-json` for it:
   - `completed` needs `value_narrative` and `key_proof`. On Heavy lane or
     Foundation kind it also needs `human_attestation` (true),
     `attestation_text` and `attestation_date` (see `--help`).
   - `validated` is a Gate-5 human attestation. `attestation_text` (or
     `scope`) carries the operator's verbatim words and is refused when empty.
     Never author words the operator did not say.
   - `closed` is the ADR closeout. It refuses at exit 3 while any OBPI has an
     unwaived REQ coverage gap.
3. Record the operator as `--attestor g0`, never a real name (`AGENTS.md`
   § Execution Rules, operator PII).
4. Run with `--dry-run` to see the event, then run it for real.
5. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

```bash
uv run gz adr emit-receipt ADR-X.Y.Z \
  --event validated \
  --attestor g0 \
  --evidence-json '{"attestation_text": "<operator verbatim words>. Receipts: arb-ruff-<id>, arb-step-typecheck-<id>, arb-step-unittest-<id>, arb-step-mkdocs-<id>", "attestation_date": "YYYY-MM-DD"}'
```

On **Heavy** lane / **foundation** kind, the attestation text MUST cite the `arb-*`
receipt IDs emitted by the canonical ARB steps (`gz arb ruff`, `gz arb typecheck`,
`gz arb step --name unittest ...`, `gz arb step --name mkdocs ...`). The gate reads the IDs
from the `attestation_text` (or `scope`) prose only; a separate `receipts` list is not read.
A text citing no receipt fails closed at exit 3 before the receipt is recorded (locked by
`CANONICAL_STEP_COMMANDS`; see AGENTS.md § Attestation).

The `$gz-adr-emit-receipt` token in `agents/openai.yaml` names this skill
for Codex; it is not a CLI alias. Every agent runs the literal
`uv run gz adr emit-receipt ...` command shown above.
