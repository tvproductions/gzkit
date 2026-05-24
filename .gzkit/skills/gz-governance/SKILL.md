---
name: gz-governance
description: Namespace router → ADR/OBPI/ledger governance skills. Use to pick the governance intent before invoking the matched skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-23
model: haiku
---

# gz-governance

| Intent | Skill |
|---|---|
| adr create | `gz-adr-create` |
| adr promote | `gz-adr-promote` |
| adr audit | `gz-adr-audit` |
| adr status | `gz-adr-status` |
| adr sync | `gz-adr-sync` |
| obpi specify | `gz-obpi-specify` |
| obpi reconcile | `gz-obpi-reconcile` |
| ledger receipt | `gz-adr-emit-receipt` |
| validate | `gz-validate` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
