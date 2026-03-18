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
- **With an ADR ID** (e.g., `ADR-0.3.0`): run `uv run gz adr report ADR-0.3.0` for the summary row, then `uv run gz adr status ADR-0.3.0 --json` for OBPI detail. Render both as tables.

## Invocation

```text
/gz-adr-status              ← summary (all ADRs)
/gz-adr-status --summary    ← summary (explicit)
/gz-adr-status ADR-0.3.0    ← focused drilldown
```

## Commands

```bash
# Summary view
uv run gz adr report

# Focused ADR drilldown
uv run gz adr report ADR-0.3.0
uv run gz adr status ADR-0.3.0 --json
```

## Output Contract

### Summary mode

- Run `uv run gz adr report`. The command output is already visible to the user from tool execution — do NOT re-print it.
- Do not paraphrase, condense, or replace the table with prose unless the user explicitly asks for analysis.
- Optional commentary belongs after the command runs and only when the user asks for interpretation.

### Focused mode

- Render a compact ADR overview table and an OBPI status table derived from `uv run gz adr status <ADR-ID> --json`.
- Do not return the plain-text CLI narrative when a tabular rendering can be produced from JSON.
- Do not use Markdown pipe tables. Use fixed-width ASCII tables inside a fenced `text` block.
- Keep focused mode compact: use a short overview table, a narrow OBPI table, and a separate issues/blockers section.
- Show full OBPI IDs by default. Wrap the ID across lines inside the same row when needed; do not abbreviate unless the user asks for compact output.

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
