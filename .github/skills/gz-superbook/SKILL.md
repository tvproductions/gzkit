---
name: gz-superbook
description: Bridge superpowers specs/plans to GovZero ADR/OBPI governance artifacts. Supports retroactive booking of completed work and forward booking before implementation.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-15
---

# gz superbook

Bridge superpowers artifacts to GovZero governance.

## Trigger

- After completing superpowers plan execution (retroactive booking)
- After superpowers plan is approved, before implementation (forward booking)
- User asks to "book", "superbook", or "create ADR from plan"

## Usage

### Retroactive (book completed work)

```bash
uv run gz superbook retroactive \
  --spec docs/superpowers/specs/<spec>.md \
  --plan docs/superpowers/plans/<plan>.md \
  --apply
```

### Forward (book before implementation)

```bash
uv run gz superbook forward \
  --spec docs/superpowers/specs/<spec>.md \
  --plan docs/superpowers/plans/<plan>.md \
  --apply
```

## Behavior

1. Parses superpowers spec and plan markdown
2. Auto-classifies governance lane (lite/heavy) from file scope
3. Maps plan chunks to OBPI briefs with REQ IDs
4. Presents draft for human review
5. On --apply: writes ADR, OBPIs, and ledger events

## Constraints

- Always run dry-run first (default without --apply)
- Human must review and approve before booking
- Retroactive mode sets status to Pending-Attestation (human must still run gz attest)
- Forward mode sets status to Draft
