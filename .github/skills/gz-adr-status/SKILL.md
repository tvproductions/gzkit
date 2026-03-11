---
name: gz-adr-status
description: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.
compatibility: GovZero v6 framework; uses gz CLI status surfaces
metadata:
  skill-version: "1.9.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 - Evidence Gathering"
gz_command: status
invocation: uv run gz status --table | uv run gz adr status ADR-0.3.0
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
- For summary requests, present the command's table output directly in a fenced code block. Do not paraphrase, condense, or replace the table with a prose summary unless the user explicitly asks for analysis.
- If an ADR ID is provided, show only the focused ADR details unless the user explicitly asks for both summary and detail.
- For focused ADR requests, prefer `uv run gz adr status <ADR-ID> --json` and render the response as tables instead of prose bullets whenever the needed fields are available.
- `gz adr status` requires an ADR identifier.

## Output Contract

- Summary mode is table-first. The response must include the raw `uv run gz status --table` output as the primary payload.
- Render that payload in a fenced `text` code block so the table structure is preserved.
- Do not precede the table with a prose recap. Optional commentary belongs after the table and only when the user asks for interpretation.
- Focused mode is table-first as well. The response should render a compact ADR overview table and an OBPI status table derived from `uv run gz adr status <ADR-ID> --json`.
- In focused mode, do not return the plain-text CLI narrative when a tabular rendering can be produced from JSON.
- In focused mode, do not use Markdown pipe tables. Long identifiers wrap badly in chat and make the result unreadable.
- Focused mode tables must be fixed-width ASCII tables inside a fenced `text` block.
- If Markdown syntax must be shown, present it inside a fenced `md` code block so the Markdown source is visible instead of rendered.
- Keep focused mode compact: use a short overview table, a narrow OBPI table with abbreviated labels or ordinal IDs, and a separate issues/blockers section instead of wide issue columns.
- In focused mode, show full OBPI IDs by default in the OBPI table. Wrap the ID across lines inside the same row when needed; do not replace the ID with an abbreviation unless the user explicitly asks for compact output.

Required summary-mode shape:

```text
<exact output of `uv run gz status --table`>
```

Required focused-mode shape:

```text
ADR Overview
+----------+---------+--------------+------+----------+---------+
| ADR      | Life    | Phase        | OBPI | Closeout | QC      |
+----------+---------+--------------+------+----------+---------+
| ADR-...  | Pending | pre_closeout | 0/6  | BLOCKED  | PENDING |
+----------+---------+--------------+------+----------+---------+

OBPIs
+----+--------------------------------------+-------------+-------+------+
| #  | OBPI ID                              | State       | Brief | Done |
+----+--------------------------------------+-------------+-------+------+
| 01 | OBPI-0.11.0-01-obpi-transaction-     | in_progress | draft | no   |
|    | contract-and-scope-isolation         |             |       |      |
| 02 | OBPI-0.11.0-02-obpi-completion-      | in_progress | draft | no   |
|    | validator-and-git-sync-gate          |             |       |      |
+----+--------------------------------------+-------------+-------+------+

Issues
01 ledger proof of completion is missing
01 brief file status is not Completed
02 ledger proof of completion is missing
```

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`
