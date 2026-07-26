---
name: gz-chores
description: Namespace router → maintenance and code-quality chore skills. Use to pick the chore intent before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-07-25
metadata:
  skill-version: "0.1.1"
model: haiku
---

# gz-chores

| Intent | Skill |
|---|---|
| chore runner | `gz-chore-runner` |
| deps upgrade | `gz-deps-upgrade` |
| foundation triage | `gz-foundation-triage` |
| pythonic detect | `gz-pythonic-pattern-detect` |
| pythonic apply | `gz-pythonic-pattern-apply` |
| config check | `gz-check-config-paths` |
| cli audit | `gz-cli-audit` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
