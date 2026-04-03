---
name: gz-adr-check
description: "ARCHIVED: Consolidated into gz-adr-audit. Use /gz-adr-audit for ADR evidence checks."
lifecycle_state: retired
archived_into: gz-adr-audit
deprecation_replaced_by: gz-adr-audit
deprecation_migration: "Use /gz-adr-audit directly."
deprecation_communication: "Consolidated during skill consolidation 2026-04-03."
deprecation_announced_on: "2026-04-03"
retired_on: "2026-04-03"
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-adr-check (ARCHIVED)

This skill has been consolidated into **gz-adr-audit**.

Use `/gz-adr-audit` for all ADR evidence verification, including:

- `uv run gz adr audit-check <adr-id>` (blocking evidence gate)
- `uv run gz adr audit-check <adr-id> --json` (machine-readable output)

See `gz-adr-audit` § Validation Commands for the full reference.
