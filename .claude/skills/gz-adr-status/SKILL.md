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
gz_command: adr report
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

## Behavior

When this skill is invoked, **immediately run the appropriate command** — do not ask clarifying questions.

- **No arguments** or `--summary`: run `uv run gz adr report` and present the output.
- **With an ADR ID** (e.g., `ADR-0.3.0`): run `uv run gz adr report ADR-0.3.0`. This single command produces the full focused view (overview table, OBPI table, and issues). Do NOT also run `--json` — the report command output is sufficient and already visible.
- **With a type name** (`foundation`, `feature`, `pool`): run `uv run gz adr report <type>` to filter the summary to one ADR category.

## Invocation

```text
/gz-adr-status              ← summary (all ADRs)
/gz-adr-status --summary    ← summary (explicit)
/gz-adr-status ADR-0.3.0    ← focused drilldown
/gz-adr-status pool          ← pool ADRs only
/gz-adr-status feature       ← feature ADRs only
/gz-adr-status foundation    ← foundation ADRs only
```

## Commands

```bash
# Summary view
uv run gz adr report

# Focused ADR drilldown
uv run gz adr report ADR-0.3.0

# Filter by type
uv run gz adr report pool
uv run gz adr report feature
uv run gz adr report foundation
```

## Output Contract

### Both modes

- The command output is already visible to the user from tool execution — do NOT re-print it.
- Do NOT run `uv run gz adr status <ADR-ID> --json` — it produces raw JSON which must never be shown to the user.
- Do not paraphrase, condense, or replace the table with prose unless the user explicitly asks for analysis.
- Optional commentary belongs after the command runs and only when the user asks for interpretation.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
