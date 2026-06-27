---
name: gz-manage
description: Namespace router → repo and release management skills (git-sync, issues, releases, tidy, mx hangar). Use to pick the management intent before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-27
skill-version: 0.4.0
model: haiku
---

# gz-manage

| Intent | Skill |
|---|---|
| git sync | `git-sync` |
| issue author | `ghi-author` |
| issue close | `ghi-close` |
| issue triage | `ghi-triage` |
| issue file | `gz-issue-file` |
| patch release | `gz-patch-release` |
| agent sync | `gz-agent-sync` |
| mx hangar | `gz-mx` |
| tidy | `gz-tidy` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
