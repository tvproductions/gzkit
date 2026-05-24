---
name: gz-context
description: Namespace router → context preservation and orientation skills. Use to pick the context/handoff intent before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-23
model: haiku
---

# gz-context

| Intent | Skill |
|---|---|
| handoff | `gz-session-handoff` |
| state | `gz-state` |
| map | `gz-adr-map` |
| parity | `airlineops-parity-scan` |
| orientation | `gz-skill-router` |
| context diet | `gz-context-diet` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
