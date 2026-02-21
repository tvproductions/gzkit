---
name: gz-adr-recon
description: Reconcile ADR/OBPI evidence state from ledger-driven gz outputs.
compatibility: GovZero v6 framework with OBPI briefs
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  skill-type: "reconciler"
  govzero_layer: "Layer 2 — Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-recon

Use ledger-first `gz` commands to reconcile ADR and OBPI status.

## Procedure

```bash
# 1) ADR-focused reconciliation view
uv run gz adr status ADR-0.3.0 --json

# 2) Blocking evidence check for linked briefs
uv run gz adr audit-check ADR-0.3.0 --json

# 3) Global lifecycle and gate context
uv run gz status --json
```

## Notes

- This repo does not expose `gz adr recon`; use the workflow above.
- Apply any required markdown table updates manually, then run `uv run gz lint`.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/adr-audit-check.md`
