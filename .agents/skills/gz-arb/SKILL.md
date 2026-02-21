---
name: gz-arb
description: Quality evidence workflow using native gz lint/typecheck/test/check commands.
compatibility: GovZero v6 framework; uses gz CLI quality surfaces
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
  status: ACTIVE
  effective-date: "2026-02-18"
gz_command: check
invocation: uv run gz check
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-arb

Run deterministic quality checks using built-in `gz` command surfaces.

## Procedure

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz check
```

## When to Use

- Before `gz git-sync --apply --lint --test`
- Before Gate 2 / Gate 3 verification
- Before closeout and attestation workflows

## Notes

- This repository does not expose `gz arb` subcommands.
- Use the commands above as the canonical quality evidence workflow.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/index.md`
