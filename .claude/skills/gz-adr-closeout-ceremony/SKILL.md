---
name: gz-adr-closeout-ceremony
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "7.0.0"
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

## Procedure

### Step 1: Initialize the ceremony

Run the CLI command to start the ceremony. Show the output to the human, then STOP.

```bash
uv run gz closeout ADR-X.Y.Z --ceremony
```

### Step 2: Advance one step at a time

After the human acknowledges, run:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --next
```

Show the output. STOP. Wait for human acknowledgment. Repeat.

**Do NOT call `--next` twice in the same message.** The hook will block it.

### Step 3: Record attestation

When the CLI presents the attestation prompt (Step 6), wait for the human's decision,
then record it:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --attest "Completed"
```

Valid attestations: `"Completed"`, `"Completed - Partial: [reason]"`, `"Dropped - [reason]"`

### Step 4: Continue post-attestation steps

After attestation, continue with `--next` for remaining steps (closeout pipeline,
GitHub issues, release notes, GitHub release). Each step tells you what to do.

For foundation (0.0.x) ADRs, release notes and GitHub release steps are automatically
skipped.

### Step 5: Check ceremony status (optional)

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --ceremony-status
```

---

## MUST Rules

1. **MUST** use `gz closeout --ceremony` commands — never render step content yourself
2. **MUST** show CLI output to the human verbatim
3. **MUST** wait for human acknowledgment between each `--next` call
4. **MUST** run exactly one `--next` per conversation turn
5. **MUST** use `--attest` only when the CLI presents the attestation step
6. **MUST** run `uv run gz closeout ADR-X.Y.Z` when instructed by Step 7

## MUST NOT Rules

1. **MUST NOT** compose step content yourself — the CLI controls what is presented
2. **MUST NOT** call `--next` twice in the same message
3. **MUST NOT** infer attestation from silence or implicit approval
4. **MUST NOT** skip steps or batch multiple steps together
