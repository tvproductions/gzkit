---
name: gz-obpi-sync
description: "ARCHIVED: Consolidated into gz-obpi-reconcile. Use /gz-obpi-reconcile for OBPI status sync."
lifecycle_state: retired
archived_into: gz-obpi-reconcile
deprecation_replaced_by: gz-obpi-reconcile
deprecation_migration: "Use /gz-obpi-reconcile directly."
deprecation_communication: "Sync was only used as pre/post helper inside audit; standalone unverified sync is risky. Consolidated 2026-04-03."
deprecation_announced_on: "2026-04-03"
retired_on: "2026-04-03"
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-obpi-sync (ARCHIVED)

This skill has been consolidated into **gz-obpi-reconcile** (Phase 3: Sync ADR Table).

Standalone unverified sync (reading Status: fields without checking evidence) was
risky — it could propagate incorrect status. Reconcile verifies evidence first,
then syncs. Use `/gz-obpi-reconcile` for all OBPI status operations.
