---
name: gz-adr-sync
description: Reconcile ADR files with ledger registration and status views.
compatibility: GovZero v6 framework; uses register-adrs + status commands
metadata:
  skill-version: "6.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 3 — File Sync"
gz_command: register-adrs
invocation: uv run gz register-adrs
---

# gz-adr-sync

Sync ADR governance state using current `gz` capabilities.

## Semantics

In gzkit, ADR sync is ledger registration plus status refresh.

## Procedure

```bash
# Preview ADR registration drift
uv run gz register-adrs --dry-run

# Register ADR files missing from ledger state
uv run gz register-adrs

# Confirm reconciled status
uv run gz status
```

## Notes

- `gzkit` does not expose a standalone `adr-docs` command.
- Use this workflow after adding/moving ADR files or importing pool ADRs.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/register-adrs.md`, `docs/user/commands/status.md`
