---
name: gz-governance
description: Namespace router → ADR/OBPI/ledger governance skills. Use to pick the governance intent before invoking the matched skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-06
skill-version: 0.3.1
model: haiku
---

# gz-governance

| Intent | Skill |
|---|---|
| adr create | `gz-adr-create` |
| adr promote | `gz-adr-promote` |
| adr audit | `gz-adr-audit` |
| adr evaluate | `gz-adr-evaluate` |
| adr status | `gz-adr-status` |
| adr sync | `gz-adr-sync` |
| adr closeout | `gz-adr-closeout-ceremony` |
| obpi specify | `gz-obpi-specify` |
| obpi reconcile | `gz-obpi-reconcile` |
| brief reconcile | `gz-brief-reconcile` |
| obpi lock | `gz-obpi-lock` |
| semver migrate | `gz-migrate-semver` |
| gates | `gz-gates` |
| ledger receipt | `gz-adr-emit-receipt` |
| validate | `gz-validate` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
