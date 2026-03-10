---
name: gz-adr-status
description: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.3.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 - Evidence Gathering"
gz_command: status
invocation: uv run gz status --table | uv run gz adr status ADR-0.3.0
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-10
model: haiku
---

# gz-adr-status

Show ADR status using the current `gz` command surface.

## When to Use

- Inspect all ADRs for pending gates and lifecycle at a glance
- Provide repeatable operator summaries in a consistent table format
- Inspect one ADR's lifecycle, QC posture, and OBPI breakdown without reprinting the global table

## Invocation

```text
/gz-adr-status --summary
/gz-adr-status ADR-0.3.0
```

CLI equivalents:

```bash
# Summary view
uv run gz status --table

# Focused ADR drilldown
uv run gz adr status ADR-0.3.0
uv run gz adr status ADR-0.3.0 --json
```

## Notes

- Use `uv run gz status --table` for summary requests without an ADR identifier.
- If an ADR ID is provided, show only the focused ADR details unless the user explicitly asks for both summary and detail.
- `gz adr status` requires an ADR identifier.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
