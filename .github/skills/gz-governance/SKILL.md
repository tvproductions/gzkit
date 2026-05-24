---
name: gz-governance
description: Namespace router → ADR/OBPI/ledger governance skills. Use to pick the governance intent before invoking the matched skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-24
skill-version: 0.2.0
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
| obpi lock | `gz-obpi-lock` |
| plan audit | `gz-plan-audit` |
| gates | `gz-gates` |
| justify | `gz-justify` |
| foundation triage | `gz-foundation-triage` |
| competitor discovery | `gz-competitor-radar` |
| ledger receipt | `gz-adr-emit-receipt` |
| validate | `gz-validate` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
