---
name: gz-adr-status
description: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.
category: adr-lifecycle
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.9.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 - Evidence Gathering"
gz_command: status
invocation: uv run gz adr report | uv run gz adr report ADR-0.3.0
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-11
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
/gz-adr-status
/gz-adr-status ADR-0.3.0
```

CLI equivalent:

```bash
# Summary table (all ADRs)
uv run gz adr report

# Focused ADR detail
uv run gz adr report ADR-0.3.0
```

## Notes

- `gz adr report` is the single deterministic table surface for ADR status.
- Without an argument it renders the summary table (same as `gz status --table`).
- With an ADR ID it renders overview + OBPI + issues tables for that ADR.
- The CLI renders all tables. The agent does NOT hand-render tables from JSON.
- NEVER use `gz adr status --json` in the main conversation. The raw JSON output is noisy and the user does not want to see it.

## Output Contract

- Run `uv run gz adr report` or `uv run gz adr report <ADR-ID>`.
- Present the command output verbatim in a fenced `text` code block.
- Do not precede the table with a prose recap. Optional commentary belongs after the table and only when the user asks for interpretation.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
