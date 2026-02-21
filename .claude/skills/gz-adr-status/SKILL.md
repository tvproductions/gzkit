---
name: gz-adr-status
description: Show focused status for one ADR, or global status across ADRs.
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: adr status
invocation: uv run gz adr status <ADR-ID>
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-status

Show ADR status using the current `gz` command surface.

## When to Use

- Check one ADR before implementation or closeout
- Inspect all ADRs for pending gates
- Confirm lane and lifecycle state

## Invocation

```text
/gz-adr-status ADR-0.3.0
/gz-adr-status --summary
```

CLI equivalents:

```bash
# Focused ADR status
uv run gz adr status ADR-0.3.0
uv run gz adr status ADR-0.3.0 --json

# Multi-ADR summary
uv run gz status
uv run gz status --json
```

## Notes

- `gz adr status` requires an ADR identifier.
- Use `gz status` for repository-wide lifecycle and gate summary.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
