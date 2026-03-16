---
name: gz-adr-status
description: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.
category: adr-lifecycle
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "2.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 - Evidence Gathering"
gz_command: status
invocation: uv run gz status --table | uv run gz adr report ADR-0.3.0
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-15
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

# Focused ADR report (deterministic table output)
uv run gz adr report ADR-0.3.0
```

## Notes

- Use `uv run gz status --table` for summary requests without an ADR identifier.
- For summary requests, present the command's table output directly in a fenced code block. Do not paraphrase, condense, or replace the table with a prose summary unless the user explicitly asks for analysis.
- If an ADR ID is provided, show only the focused ADR details unless the user explicitly asks for both summary and detail.
- `gz adr status` requires an ADR identifier.

## Output Contract

### Summary Mode

- The response MUST include the raw `uv run gz status --table` output as the primary payload.
- Render that payload in a fenced `text` code block so the table structure is preserved.
- Do not precede the table with a prose recap. Optional commentary belongs after the table and only when the user asks for interpretation.

Required summary-mode shape:

```text
<exact output of `uv run gz status --table`>
```

### Focused Mode

**Run `uv run gz adr report <ADR-ID>` and paste its output verbatim inside a fenced `text` block.** The command produces deterministic ASCII tables — do not reformat, rearrange, or reinterpret the output.

- Do not hand-build tables from JSON. The `gz adr report` command handles all formatting.
- Do not add prose before or between the tables. Commentary, if any, goes after the fenced block and only when the user asks.
- Do not echo raw JSON from `gz adr status --json` into the response.

Required focused-mode shape:

```text
<exact output of `uv run gz adr report <ADR-ID>`>
```

## References

- Command implementation: `src/gzkit/commands/status.py` (`adr_report_cmd`, `_render_adr_report`)
- CLI registration: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
