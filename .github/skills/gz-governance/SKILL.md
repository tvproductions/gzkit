---
name: gz-governance
description: Namespace router → ADR/OBPI/ledger governance skills. Use to pick the governance intent before invoking the matched skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-26
metadata:
  skill-version: "0.7.0"
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
| obpi sync | `gz-obpi-sync` |
| obpi brief-drift | `gz-obpi-brief-drift` |
| obpi lock | `gz-obpi-lock` |
| semver migrate | `gz-migrate-semver` |
| ledger receipt | `gz-adr-emit-receipt` |
| validate | `gz-validate` |
| ontology | `gz-ontology` |
| health audit | `gz-health-audit` |
| intent trace | `gz-intent-trace` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
