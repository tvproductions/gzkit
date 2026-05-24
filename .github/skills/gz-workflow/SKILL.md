---
name: gz-workflow
description: Namespace router → end-to-end workflow skills (design through release). Use to pick the next workflow stage before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-23
model: haiku
---

# gz-workflow

| Intent | Skill |
|---|---|
| design | `gz-design` |
| plan | `gz-plan` |
| implement | `gz-obpi-pipeline` |
| verify | `gz-implement` |
| attest | `gz-adr-closeout-ceremony` |
| release | `gz-patch-release` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
