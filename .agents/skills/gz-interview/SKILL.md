---
name: gz-interview
description: "ARCHIVED: Consolidated into gz-adr-create as mandatory Step 0. Interview is now a non-negotiable prerequisite for ADR authoring."
lifecycle_state: retired
archived_into: gz-adr-create
deprecation_replaced_by: gz-adr-create
deprecation_migration: "Use /gz-adr-create directly."
deprecation_communication: "Consolidated during skill consolidation 2026-04-03."
deprecation_announced_on: "2026-04-03"
retired_on: "2026-04-03"
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-interview (ARCHIVED)

This skill has been consolidated into **gz-adr-create** as mandatory Step 0.

The `gz interview adr` command is now a non-negotiable prerequisite for ADR authoring.
No ADR may be created without first completing the structured interview.

Run `uv run gz interview adr` — this is enforced as the first step in `/gz-adr-create`.

For OBPI and PRD interviews, use the CLI directly:

```bash
uv run gz interview obpi
uv run gz interview prd
```
