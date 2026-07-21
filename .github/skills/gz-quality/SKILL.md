---
name: gz-quality
description: Namespace router → quality and complexity skills. Use to pick the quality-check intent before invoking the matched concrete skill directly.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-24
metadata:
  skill-version: "0.3.0"
model: haiku
---

# gz-quality

| Intent | Skill |
|---|---|
| check / lint / test / typecheck | `gz-check` |
| complexity preview | `gz-complexity-advisor` |
| complexity authoring | `gz-complexity-guide` |
| complexity distill | `gz-complexity-distill` |
| tech debt | `gz-tech-debt-review` |
| arb receipts | `gz-arb` |
| obpi simplify | `gz-obpi-simplify` |

Invoke the matched skill directly. See `gz-skill-router` for the full catalog.
