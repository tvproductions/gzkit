---
name: gz-workflow
description: Namespace router → end-to-end workflow skills (design through release). Use to pick the next workflow stage before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-15
metadata:
  skill-version: "0.3.0"
model: haiku
---

# gz-workflow

| Intent | Skill |
|---|---|
| R&D run — "consider this for gzkit" (operator-invoked) | `gz-rnd` |
| design | `gz-design` |
| plan | `gz-plan` |
| implement | `gz-obpi-pipeline` |
| verify | `gz-implement` |
| justify | `gz-justify` |
| plan audit | `gz-plan-audit` |
| release | `gz-patch-release` (also routed by `gz-manage`) |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
