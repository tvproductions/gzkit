---
name: gz-obpi-audit
description: "ARCHIVED: Consolidated into gz-obpi-reconcile. Use /gz-obpi-reconcile for OBPI evidence verification."
lifecycle_state: retired
archived_into: gz-obpi-reconcile
deprecation_replaced_by: gz-obpi-reconcile
deprecation_migration: "Use /gz-obpi-reconcile directly."
deprecation_communication: "Reconcile Phase 1 IS the audit; no independent caller existed. Consolidated 2026-04-03."
deprecation_announced_on: "2026-04-03"
retired_on: "2026-04-03"
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-obpi-audit (ARCHIVED)

This skill has been consolidated into **gz-obpi-reconcile**.

Reconcile Phase 1 performs the same evidence gathering (tests, coverage, @covers tags)
and writes the same JSONL ledger entries. Use `/gz-obpi-reconcile` for all OBPI
verification — it audits, fixes stale briefs, syncs the ADR table, and reports.

```bash
# Single brief
/gz-obpi-reconcile ADR-0.0.19 --brief OBPI-0.0.19-03

# Full ADR
/gz-obpi-reconcile ADR-0.0.19
```
