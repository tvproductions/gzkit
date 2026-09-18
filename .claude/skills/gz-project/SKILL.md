---
name: gz-project
description: Namespace router → project lifecycle skills (init, requirements, constitution, status). Use to pick the project-level intent before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-09-18
metadata:
  skill-version: "0.4.0"
model: haiku
---

# gz-project

| Intent | Skill |
|---|---|
| init | `gz-init` |
| prd | `gz-prd` |
| constitution | `gz-constitute` |
| status | `gz-status` |
| competitor radar | `gz-competitor-radar` |
| flight test | `gz-flighttest` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
