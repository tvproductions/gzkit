---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "7.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-30
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony via CLI-driven step sequencing.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## Architecture

The CLI is the step driver. The agent is a relay. Each `--next` call returns exactly one
step's content. The agent cannot skip steps because it never sees future steps.

A PreToolUse hook (`ceremony-step-gate.py`) blocks the agent from calling `--next` more
than once per conversation turn, enforcing human acknowledgment between steps.

State is persisted in `.gzkit/ceremonies/ADR-X.Y.Z.ceremony.json`.

---

## Invocation

The skill receives an ADR semver as its argument (e.g. `0.0.8`). Normalize to
`ADR-X.Y.Z` format and begin immediately. Do not ask clarifying questions.

---

## Agent Loop

On skill invocation, the agent enters a **relay loop**. The loop is simple:

1. **First turn (skill invoked):** Run `uv run gz closeout ADR-X.Y.Z --ceremony`. Stop.
2. **Every subsequent human message:** That message IS the acknowledgment. Run
   `uv run gz closeout ADR-X.Y.Z --ceremony --next`. If the CLI output lists commands
   to run (walkthrough commands, closeout pipeline, gh issue commands), run them
   immediately in the same turn, then stop.
3. **Attestation step:** When the CLI output contains "I await your attestation",
   stop and wait. The human's next message is their attestation decision. Run
   `uv run gz closeout ADR-X.Y.Z --ceremony --attest "<their decision>"`.
4. **Ceremony complete:** When the CLI output contains "COMPLETE", the ceremony is done.

**The agent is a relay that executes what the CLI tells it to. One `--next` per turn,
but run any commands the step requires in the same turn.**

---

## MUST Rules

1. **MUST** run the CLI command immediately on invocation — no preamble, no questions
2. **MUST** treat every human message as acknowledgment and run `--next`
3. **MUST** run exactly one ceremony CLI call per turn
4. **MUST** use `--attest` only when CLI output says "I await your attestation"
5. **MUST** execute action-step commands (closeout, gh issue, gh release) when instructed
6. **MUST** stop after showing CLI output — no "ready when you are", no offers, no asks

## MUST NOT Rules

1. **MUST NOT** compose step content yourself — the CLI controls what is presented
2. **MUST NOT** call `--next` twice in the same message
3. **MUST NOT** add commentary, interpretation, or offers around CLI output
4. **MUST NOT** ask permission to proceed — the human's message is the permission
5. **MUST NOT** skip steps or batch multiple steps together
