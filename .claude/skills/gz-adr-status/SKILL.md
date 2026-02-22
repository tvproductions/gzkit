---
name: gz-adr-status
description: Always show a table of ADRs and lifecycle/QC status; optionally follow with focused ADR detail.
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.2.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: status --table
invocation: uv run gz status --table
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-22
---

# gz-adr-status

Show ADR status using the current `gz` command surface.

## When to Use

- Inspect all ADRs for pending gates and lifecycle at a glance
- Provide repeatable operator summaries in a consistent table format
- Optionally drill into one ADR after presenting the table

## Invocation

```text
/gz-adr-status --summary
/gz-adr-status ADR-0.3.0
```

CLI equivalents:

```bash
# Required table summary (always)
uv run gz status --table

# Optional focused ADR drilldown after table
uv run gz adr status ADR-0.3.0
uv run gz adr status ADR-0.3.0 --json
```

## Notes

- This skill must always show `uv run gz status --table` output.
- If an ADR ID is provided, show the table first, then focused ADR details.
- `gz adr status` requires an ADR identifier.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
